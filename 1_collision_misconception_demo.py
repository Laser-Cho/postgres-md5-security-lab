#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
1_collision_misconception_demo.py
[암호학 분석] MD5 '충돌 공격(Collision)'에 대한 오해와 진실 검증 데모
=============================================================================
질문: "MD5는 충돌 공격으로 한 방에 뚫리는 알고리즘인데, DB 인증도 충돌 공격으로 뚫릴까?"
답변: "충돌 공격은 실제로 존재하지만, DB 인증 우회에는 쓰일 수 없습니다."

이 스크립트는:
1. 실제로 서로 다른 두 바이너리 데이터(M1 != M2)가 동일한 MD5 해시를 갖는
   실제 MD5 충돌 쌍(Xiaoyun Wang Collision Pair)을 생성/검증합니다.
2. 왜 이 충돌 공격이 PostgreSQL DB 패스워드 인증을 우회하는 데에는 
   사용될 수 없는지 암호학적(역상 공격 vs 충돌 공격)으로 증명합니다.
=============================================================================
"""

import hashlib
import time

def demo_md5_collision():
    print("=" * 70)
    print(" 1. 실제 MD5 충돌 공격 (Collision Attack) 시연")
    print("=" * 70)
    print("MD5는 2004년 중국 산둥대 샤오윈 왕(Xiaoyun Wang) 교수 연구진에 의해")
    print("충돌 저항성(Collision Resistance)이 완전히 붕괴되었습니다.\n")

    # 왕 교수 연구진이 발견한 실제 128바이트 충돌 블록 쌍 (Hex 디코딩)
    block1 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c"
        "2fcab58712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e488832571415a"
        "085125e8f7cdc99fd91dbdf280373c5b"
        "d8823e3156348f5bae6dacd436c919c6"
        "dd53e2b487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080a80d1e"
        "c69821bcb6a8839396f9652b6ff72a70"
    )

    block2 = bytes.fromhex(
        "d131dd02c5e6eec4693d9a0698aff95c"
        "2fcab50712467eab4004583eb8fb7f89"
        "55ad340609f4b30283e4888325f1415a"
        "085125e8f7cdc99fd91dbd7280373c5b"
        "d8823e3156348f5bae6dacd436c919c6"
        "dd53e23487da03fd02396306d248cda0"
        "e99f33420f577ee8ce54b67080280d1e"
        "c69821bcb6a8839396f965ab6ff72a70"
    )

    hash1 = hashlib.md5(block1).hexdigest()
    hash2 = hashlib.md5(block2).hexdigest()

    print(f"[*] 블록 1 크기: {len(block1)} bytes")
    print(f"[*] 블록 2 크기: {len(block2)} bytes")
    print(f"[*] 두 블록의 일치 여부 (block1 == block2): {block1 == block2} (완전히 다른 데이터!)")
    print(f"[*] Block 1 MD5 Hash: {hash1}")
    print(f"[*] Block 2 MD5 Hash: {hash2}")
    print(f"[*] 두 해시의 일치 여부: {hash1 == hash2} (해시 충돌 발생!)")
    print("\n -> 결론: 공격자는 동일한 MD5를 갖는 문서 2개(예: 변조된 계약서)를 만들 수 있습니다.")

def explain_preimage_vs_collision():
    print("\n" + "=" * 70)
    print(" 2. 왜 충돌 공격으로 PostgreSQL 인증을 뚫을 수 없을까?")
    print("=" * 70)
    print("""
암호학에서 공격 유형은 명확히 구분됩니다:

[1] 충돌 공격 (Collision Attack) - MD5 취약함!
    - 목표: H(M1) == H(M2) 인 서로 다른 '임의의' 두 값 M1, M2를 공격자가 직접 생성.
    - 피해 대상: 전자 서명, 파일 무결성 검증, TLS 인증서 위조.

[2] 제1 역상 공격 (Pre-image Attack) - MD5 여전히 불가능! (복잡도 2^128)
    - 목표: 서버에 이미 정해진 해시 H_target이 주어졌을 때,
            H(M) == H_target 을 만족하는 M(원래 패스워드)을 역산하는 것.
    - 피해 대상: 패스워드 인증 시스템!

[3] PostgreSQL MD5 인증 프로토콜 구조:
    1. DB에 저장된 해시: H_stored = md5(패스워드 || 유저명)
       -> 대상 유저의 패스워드는 이미 정해져 있음 (타겟 H_target).
       -> 임의의 충돌 쌍 M1, M2를 만든다고 해서 기존 유저의 H_stored와 일치하지 않음!
    
    2. 접속 시 서버 챌린지:
       -> 클라이언트가 접속할 때마다 서버가 4바이트 '랜덤 솔트(Salt)'를 발급.
       -> 최종 응답 = md5(H_stored || Salt)
       -> 접속 시도마다 Salt가 계속 바뀌므로 사전에 계산된 충돌 공격은 원천 차단됨!

따라서:
"MD5는 충돌 공격으로 한 방에 뚫린다"는 말은 '전자서명/인증서'에는 맞지만,
'DB 패스워드 인증 우회'에는 기술적으로 성립하지 않는 대표적인 오해입니다.
""")

def introduce_real_md5_attacks():
    print("=" * 70)
    print(" 3. 그렇다면 MD5는 안전한가? -> 전혀 아닙니다! (실제 위험성)")
    print("=" * 70)
    print("""
충돌 공격 때문이 아니라, MD5 자체의 '구조적 결함' 때문에 뚫립니다:

[위협 1] Pass-the-Hash (해시 전달 공격) -> 2_exploit_pass_the_hash.py 참고
    PostgreSQL의 치명적인 프로토콜 결함:
    클라이언트가 서버로 보낼 응답을 만들 때 '평문 비밀번호'가 필요 없고,
    오직 DB에 저장된 해시값 H_stored만 있으면 계산이 가능합니다!
    따라서 공격자가 DB 백업, SQL 인젝션, 로그 등에서 해시만 훔쳐오면
    비밀번호를 크랙할 필요도 없이 '해시 그대로' 로그인하여 데이터를 전부 털어갈 수 있습니다.
    (SCRAM-SHA-256에서는 암호학적으로 원천 방어됨)

[위협 2] 극도로 빠른 오프라인 사전/브루트포스 공격 -> 3_exploit_md5_crack.py 참고
    MD5는 암호학적 해시함수가 아니라 빠른 체크섬 수준으로 가볍습니다.
    SCRAM-SHA-256은 4,096번의 PBKDF2 해싱을 거치지만,
    MD5는 단 1번만 계산하므로 GPU 1대로 초당 수백억 번의 무차별 대입이 가능합니다.
    통신 패킷을 스니핑하거나 해시를 탈취당했을 때 순식간에 비밀번호가 노출됩니다.
""")

if __name__ == "__main__":
    demo_md5_collision()
    explain_preimage_vs_collision()
    introduce_real_md5_attacks()
