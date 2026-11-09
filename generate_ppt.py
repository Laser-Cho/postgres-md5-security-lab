#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_ppt.py
Creates a detailed, text-rich 16:9 PowerPoint presentation explaining:
- Why MD5 collision attack is misunderstood
- Why Pass-the-Hash is the real critical vulnerability in PostgreSQL MD5
- A step-by-step flowchart of the penetration process
- Technical, cryptographic, and architectural breakdowns
"""

import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # Blank slide

    # Colors
    NAVY = RGBColor(26, 43, 76)
    DARK_GRAY = RGBColor(45, 52, 54)
    MID_GRAY = RGBColor(99, 110, 114)
    LIGHT_BG = RGBColor(248, 249, 250)
    BORDER_COLOR = RGBColor(220, 224, 230)
    RED_ACCENT = RGBColor(192, 57, 43)
    BLUE_ACCENT = RGBColor(41, 128, 185)
    GREEN_ACCENT = RGBColor(39, 174, 96)
    WHITE = RGBColor(255, 255, 255)
    BOX_BG = RGBColor(241, 243, 246)

    def add_header(slide, title_text, category_text="PostgreSQL MD5 보안 분석 및 침투 실증"):
        # Category Banner
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = BLUE_ACCENT
        p_cat.font.name = "Malgun Gothic"

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.7))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY
        p_title.font.name = "Malgun Gothic"

        # Divider line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.02))
        line.fill.solid()
        line.fill.fore_color.rgb = BORDER_COLOR
        line.line.color.rgb = BORDER_COLOR

    def add_card(slide, left, top, width, height, title, body_paragraphs, header_color=NAVY, bg_color=BOX_BG):
        # Card background shape
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        shape.line.color.rgb = BORDER_COLOR
        shape.line.width = Pt(1)

        # Text Frame
        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.2)
        tf.margin_bottom = Inches(0.2)

        # Card Title
        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(14)
        p_title.font.bold = True
        p_title.font.color.rgb = header_color
        p_title.font.name = "Malgun Gothic"
        p_title.space_after = Pt(8)

        # Card Body Paragraphs
        for item in body_paragraphs:
            p = tf.add_paragraph()
            p.text = item
            p.font.size = Pt(10.5)
            p.font.color.rgb = DARK_GRAY
            p.font.name = "Malgun Gothic"
            p.space_after = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 1: 표지
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()

    tbox1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(4.5))
    tf1 = tbox1.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "보안 아키텍처 및 취약점 실증 보고서"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(180, 205, 237)
    p0.font.name = "Malgun Gothic"
    p0.space_after = Pt(14)

    p1 = tf1.add_paragraph()
    p1.text = "PostgreSQL MD5 다운그레이드의 위험성과\nPass-the-Hash 침투 메커니즘 분석"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.font.name = "Malgun Gothic"
    p1.space_after = Pt(20)

    p2 = tf1.add_paragraph()
    p2.text = "■ 쟁점: 구형 DB 접근 제어 솔루션 연동을 위한 SCRAM-SHA-256 → MD5 강제 변경 요구\n" \
              "■ 의문: 'MD5는 충돌 공격(Collision)으로 한 방에 뚫리는 알고리즘 아닌가?'에 대한 암호학적 검증\n" \
              "■ 진실: 충돌 공격의 오해를 바로잡고, 실제 DB를 완전히 장악하는 'Pass-the-Hash'와 '초고속 크래킹' 실증"
    p2.font.size = Pt(13)
    p2.font.color.rgb = RGBColor(220, 225, 235)
    p2.font.name = "Malgun Gothic"
    p2.space_after = Pt(30)

    p3 = tf1.add_paragraph()
    p3.text = "대상 독자: 비전공자, 인프라 엔지니어, DB 관리자, 보안 담당자 모두를 위한 상세 해설"
    p3.font.size = Pt(11)
    p3.font.color.rgb = RGBColor(160, 175, 200)
    p3.font.name = "Malgun Gothic"

    # -------------------------------------------------------------
    # SLIDE 2: 배경 및 문제 상황
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "[문제 배경] 구형 솔루션과 보안팀의 MD5 다운그레이드 요구", "1. 현상 분석 및 도입 배경")

    add_card(slide2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "1. 사내 DB 접근 제어 솔루션의 현실적 한계",
             [
                 "• 기업 컴플라이언스(접근 기록 보관 의무)를 준수하기 위해 사내 네트워크에 'DB 접근 제어 소프트웨어'를 도입하여 사용 중입니다.",
                 "• 그러나 도입된 솔루션이 노후화된 구형 버전이어서 최신 PostgreSQL의 표준 인증 규격인 'SCRAM-SHA-256' 프로토콜을 해석하지 못하는 기술적 한계가 발생했습니다.",
                 "• 솔루션이 DB 패킷을 복호화/해석하지 못하자 개발 및 운영 쿼리가 전부 차단되는 업무 장애가 발생하였고, 이를 해결해야 하는 상황에 직면했습니다."
             ])

    add_card(slide2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1),
             "2. 보안팀의 조치 권고와 발생하는 모순",
             [
                 "• 보안팀은 장애 해소를 위해 PostgreSQL의 설정을 과거 20년 전 표준인 MD5 방식으로 변경할 것을 요청했습니다.",
                 "   - pg_hba.conf : 인증 방식을 scram-sha-256 에서 md5 로 수정",
                 "   - postgresql.conf : password_encryption 설정을 md5 로 수정",
                 "• 하지만 이는 '보안 통제를 위해 도입한 솔루션' 때문에 역설적으로 '핵심 DB 엔진의 암호 체계를 취약하게 퇴보'시키는 심각한 주객전도의 모순을 낳습니다.",
                 "• 실무 담당자 관점에서 'MD5는 이미 해킹에 뚫려 폐기된 알고리즘인데 이를 적용해도 안전한가?'라는 중대한 의구심이 제기됩니다."
             ], header_color=RED_ACCENT)

    # -------------------------------------------------------------
    # SLIDE 3: 암호학 기초 개념
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "[암호학 기초] 해시 함수와 패스워드 인증의 작동 원리", "2. 사전 필수 개념 정리")

    add_card(slide3, Inches(0.8), Inches(1.8), Inches(3.7), Inches(5.1),
             "1. 단방향 해시 함수 (Hash)",
             [
                 "• 임의의 긴 데이터를 넣어도 고정된 길이(예: MD5는 128비트, 32자리 16진수)의 고유 지문으로 변환하는 수학적 함수입니다.",
                 "• '단방향성(One-way)': 과일을 믹서기에 갈아 주스를 만들 수는 있지만, 주스를 다시 과일로 되돌릴 수는 없는 것과 같습니다.",
                 "• DB는 사용자의 평문 비밀번호를 그대로 저장하지 않고 해시값만 저장하여 관리자조차 비밀번호를 알 수 없도록 보호합니다."
             ])

    add_card(slide3, Inches(4.8), Inches(1.8), Inches(3.7), Inches(5.1),
             "2. 솔트(Salt)와 무차별 대입 방어",
             [
                 "• 'password123'처럼 흔한 단어는 해시값이 널리 알려져 있어 사전표(레인보우 테이블)로 즉시 털릴 수 있습니다.",
                 "• 이를 방지하기 위해 비밀번호 뒤에 무작위 문자열('솔트, Salt')을 소금 치듯이 덧붙여 해싱합니다.",
                 "• PostgreSQL MD5는 유저명을 솔트로 사용하여 'md5(password + username)' 형태로 DB에 저장합니다.",
                 "• 하지만 고정 솔트(유저명)는 현대 GPU의 초고속 무차별 대입 공격 앞에서는 방어력이 턱없이 부족합니다."
             ])

    add_card(slide3, Inches(8.8), Inches(1.8), Inches(3.7), Inches(5.1),
             "3. 현대 표준: SCRAM-SHA-256",
             [
                 "• 단순 해싱이 아닌 암호학적 키 유도 함수(PBKDF2)를 도입하여 4,096번 이상의 반복 해싱(Key Stretching)을 수행합니다.",
                 "• 클라이언트와 서버가 서로의 평문 비밀번호를 교환하지 않고도 서로가 비밀번호를 알고 있음을 수학적으로 증명하는 상호 증명 프로토콜입니다.",
                 "• DB 내의 인증 데이터가 통째로 유출되어도 해시값 자체로는 로그인이 불가능하도록 완벽히 설계되었습니다."
             ], header_color=GREEN_ACCENT)

    # -------------------------------------------------------------
    # SLIDE 4: 오해 바로잡기 (충돌 vs 역상)
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "[오해와 진실] 'MD5는 충돌 공격으로 한 방에 뚫린다'의 실체", "3. 암호학적 공격 유형 분석")

    add_card(slide4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "1. 충돌 공격(Collision Attack)의 본질 (MD5 취약)",
             [
                 "• 개념: 공격자가 완전히 자유롭게 조작할 수 있는 '임의의 서로 다른 두 데이터 M1과 M2'를 만들어 H(M1) == H(M2)가 되게 만드는 공격입니다.",
                 "• 역사: 2004년 샤오윈 왕 교수에 의해 MD5의 충돌 저항성이 깨졌으며, 현재는 일반 PC에서도 1초 만에 충돌 쌍을 생성할 수 있습니다.",
                 "• 피해 대상: 두 계약서의 내용이 다른데 서명 해시가 같아지는 '전자 계약서 위조', 가짜 SSL 인증서를 진짜처럼 속이는 '인증서 위조'에 치명적입니다.",
                 "• 핵심: 공격자가 두 입력값(M1, M2)을 모두 자기가 원하는 쓰레기 값으로 채워서 맞추는 기법입니다."
             ])

    add_card(slide4, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1),
             "2. 왜 충돌 공격으로 DB 인증을 뚫을 수 없는가?",
             [
                 "• DB 인증은 '역상 공격(Pre-image Attack)'의 영역입니다:",
                 "   - DB 서버에는 이미 피해자(admin, app_user)의 비밀번호 해시가 H_target으로 고정되어 저장되어 있습니다.",
                 "   - 공격자가 로그인하려면 임의의 두 값을 만드는 게 아니라, '이미 정해진 H_target과 똑같은 값을 내는 비밀번호'를 찾아야 합니다.",
                 "   - MD5의 역상 저항성은 여전히 이론적으로 2^128에 달하여 전 세계 슈퍼컴퓨터를 동원해도 수학적 역산이 불가능합니다.",
                 "• 동적 난수 솔트(Dynamic Salt)의 방어:",
                 "   - 로그인 시마다 서버가 4바이트 랜덤 솔트를 발급하므로 사전에 계산해 둔 충돌 데이터를 주입하는 것이 원천 불가능합니다.",
                 "• 결론: 충돌 공격으로 DB 로그인을 뚫는다는 것은 공격 유형을 오해한 것입니다."
             ], header_color=RED_ACCENT)

    # -------------------------------------------------------------
    # SLIDE 5: 진짜 취약점 (Pass-the-Hash)
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "[실제 침투 취약점] MD5 프로토콜의 치명적 결함: Pass-the-Hash", "4. 프로토콜 결함 분석")

    add_card(slide5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "1. PostgreSQL MD5 프로토콜의 설계 미스",
             [
                 "• PostgreSQL에서 MD5 인증 시 클라이언트와 서버가 주고받는 공식은 다음과 같습니다:",
                 "   [DB 저장값] H_stored = md5( Password + Username )",
                 "   [서버 챌린지] 4바이트 무작위 Salt 전송",
                 "   [클라이언트 응답] Client_Token = md5( H_stored + Salt )",
                 "• 치명적인 결함:",
                 "   - 클라이언트가 서버로 전송할 인증 토큰(Client_Token)을 계산할 때 '평문 비밀번호'가 전혀 쓰이지 않습니다!",
                 "   - 오직 DB에 저장된 해시 문자열(H_stored)만 있으면 완벽한 유효 토큰을 계산해낼 수 있습니다.",
                 "   - 즉, 해시값 자체가 또 다른 형태의 비밀번호(Plaintext Equivalent) 역할을 해버리는 구조적 결함입니다."
             ], header_color=RED_ACCENT)

    add_card(slide5, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1),
             "2. 침투 시나리오: 해시만 있으면 DB가 완전히 털린다",
             [
                 "• 침투 전제 조건:",
                 "   - 웹 애플리케이션의 SQL Injection 취약점",
                 "   - 과거 DB 백업 덤프 파일(.sql)의 외부 유출",
                 "   - 소스코드 저장소나 개발자 PC 설정 파일에 남은 DB 계정 해시",
                 "• 결과: 공격자는 해시를 복호화하거나 비밀번호를 알아내려고 애쓸 필요가 전혀 없습니다.",
                 "• 유출된 해시 문자열을 그대로 공격 도구에 집어넣고 DB 접속 패킷을 조립하여 전송하면 서버는 즉시 관리자 권한을 부여하고 세션을 열어줍니다.",
                 "• SCRAM-SHA-256에서는 서버에 StoredKey만 보관되어 클라이언트가 ClientKey를 유도해낼 수 없으므로 이 공격이 100% 차단됩니다."
             ], header_color=NAVY)

    # -------------------------------------------------------------
    # SLIDE 6: [핵심 순서도] 침투 절차 순서도
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "[★ 핵심 순서도] PostgreSQL MD5 Pass-the-Hash 침투 5단계", "5. 침투 프로세스 순서도")

    # Flowchart step boxes
    steps_data = [
        ("STEP 1: 해시 탈취", "SQLi, 백업 파일, DB 설정 파일 등에서\npg_authid 해시값(H_stored) 획득\n(평문 비밀번호는 여전히 모름)", RED_ACCENT),
        ("STEP 2: TCP 연결 수립", "공격자 도구가 DB 포트(5432)에 접속\nPostgreSQL Frontend 프로토콜 규격의\n'StartupMessage' (User, DB) 전송", NAVY),
        ("STEP 3: 솔트 수신", "DB 서버가 AuthenticationMD5Password(5)\n코드와 함께 세션 전용 4바이트 난수\n솔트(Salt, 예: 0xb87c2fe0) 반환", BLUE_ACCENT),
        ("STEP 4: 토큰 패킷 조립", "탈취한 해시와 수신된 솔트로 계산:\nmd5(H_stored + Salt) = Token\n암호 복호화 없이 PasswordMessage 전송", RED_ACCENT),
        ("STEP 5: 인증 통과 & 탈취", "서버가 AuthenticationOk(0) 응답 반환\nSQL 쿼리(Query 'Q')를 직접 주입하여\n사내 1급 기밀 및 임직원 급여 탈취 완료", GREEN_ACCENT)
    ]

    box_width = Inches(2.18)
    box_height = Inches(4.8)
    spacing = Inches(0.2)
    start_left = Inches(0.8)
    top_pos = Inches(1.8)

    for i, (stitle, sdesc, scolor) in enumerate(steps_data):
        cur_left = start_left + i * (box_width + spacing)
        # Main Step Box
        shape = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_pos, box_width, box_height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = LIGHT_BG
        shape.line.color.rgb = scolor
        shape.line.width = Pt(2)

        tf = shape.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.15)
        tf.margin_top = Inches(0.2)

        # Step badge / title
        p_badge = tf.paragraphs[0]
        p_badge.text = f"[단계 {i+1}]"
        p_badge.font.size = Pt(11)
        p_badge.font.bold = True
        p_badge.font.color.rgb = scolor
        p_badge.font.name = "Malgun Gothic"

        p_title = tf.add_paragraph()
        p_title.text = stitle.split(": ")[1]
        p_title.font.size = Pt(13)
        p_title.font.bold = True
        p_title.font.color.rgb = NAVY
        p_title.font.name = "Malgun Gothic"
        p_title.space_after = Pt(14)

        # Separator line
        p_sep = tf.add_paragraph()
        p_sep.text = "------------------------"
        p_sep.font.size = Pt(8)
        p_sep.font.color.rgb = BORDER_COLOR
        p_sep.space_after = Pt(12)

        # Step description
        p_desc = tf.add_paragraph()
        p_desc.text = sdesc
        p_desc.font.size = Pt(10)
        p_desc.font.color.rgb = DARK_GRAY
        p_desc.font.name = "Malgun Gothic"

        # Arrow to next step (except last)
        if i < 4:
            arrow_left = cur_left + box_width + Inches(0.04)
            arrow = slide6.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, arrow_left, Inches(3.9), Inches(0.14), Inches(0.3))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = MID_GRAY
            arrow.line.fill.background()

    # -------------------------------------------------------------
    # SLIDE 7: 순서도 단계별 심층 해설
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "[순서도 심층 분석] 왜 일반 클라이언트(psql)가 아닌 전용 도구를 쓰는가?", "5. 침투 프로세스 상세 해설")

    add_card(slide7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "1. 일반 psql 클라이언트와 공격 도구의 차이점",
             [
                 "• 일반 psql 접속기:",
                 "   - 사용자가 키보드로 '평문 비밀번호'를 입력할 것을 전제로 만들어져 있습니다.",
                 "   - 사용자가 비밀번호를 입력하면 psql 내부 라이브러리가 해시를 만들고 솔트를 섞어 전송합니다.",
                 "   - 따라서 평문 비밀번호를 모르는 일반인은 해시값을 알아도 psql 비밀번호 입력창에 넣을 수가 없습니다.",
                 "• 공격자가 사용하는 Pass-the-Hash 도구 (2_exploit_pass_the_hash.py):",
                 "   - 키보드 입력을 거치지 않고 직접 저수준 TCP 소켓을 통해 PostgreSQL Frontend 와이어 프로토콜(Wire Protocol)을 구동합니다.",
                 "   - 평문 비밀번호 입력 단계를 생략하고, 훔쳐온 해시값과 서버가 준 난수 솔트를 직접 바이트 단위로 결합하여 인증 토큰을 만들어 쏩니다."
             ])

    add_card(slide7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1),
             "2. 서버 측의 착각: '정상 사용자'로 오인",
             [
                 "• DB 서버는 클라이언트가 평문 비밀번호를 알고 있는지 여부를 확인할 방법이 없습니다.",
                 "• 서버는 오직 자신이 보낸 솔트와 DB에 저장된 해시의 조합 결과인 '토큰 문자열'이 일치하는지만 검증합니다.",
                 "• 공격 도구가 올바른 토큰을 반환했으므로, 서버는 침입자를 합법적인 정식 관리자/애플리케이션으로 승인하고 'AuthenticationOk' 패킷을 내려줍니다.",
                 "• 인증이 완료되는 순간 세션이 수립되어 임의의 SQL 쿼리를 자유자재로 실행하고 DB 내 모든 테이블을 탈취할 수 있게 됩니다.",
                 "• 결론: MD5 해시값은 '암호화된 문자열'이 아니라 '그 자체로 패스워드 프리패스 티켓'입니다."
             ], header_color=RED_ACCENT)

    # -------------------------------------------------------------
    # SLIDE 8: 또 다른 위협 (오프라인 고속 크래킹)
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "[추가 위협] Key Stretching 부재와 초고속 오프라인 크래킹", "6. 부가적 보안 위험성")

    add_card(slide8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "1. 연산 비용의 치명적 차이: 1회 vs 4,096회",
             [
                 "• MD5 알고리즘의 본질:",
                 "   - 1991년 파일 체크섬용으로 설계되어 극도로 빠르고 가벼운 연산이 특징입니다.",
                 "   - 패스워드 방어에 필수적인 키 스트레칭(반복 해싱)이 전혀 없어 단 1회의 연산만으로 결과가 나옵니다.",
                 "• SCRAM-SHA-256의 방어력:",
                 "   - 기본 4,096회의 PBKDF2 해싱을 거치므로 1번 검증할 때마다 MD5 대비 수천 배의 CPU/GPU 자원이 소모됩니다.",
                 "• 공격 속도 격차:",
                 "   - 최신 GPU 1대로 MD5는 초당 1,000억 회(100 GH/s) 이상의 대입이 가능합니다.",
                 "   - 일반적인 8~12자리 복합 패스워드도 사전 대입을 통해 수 분~수십 분 내에 무력화됩니다."
             ], header_color=RED_ACCENT)

    add_card(slide8, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1),
             "2. 네트워크 도청(Sniffing) 시 패킷 크래킹",
             [
                 "• 내부망 침투 공격자가 와이어샤크(Wireshark)나 스위치 미러링으로 DB 접속 트래픽을 가로채면:",
                 "   - 서버가 보낸 4바이트 난수 솔트(Salt)",
                 "   - 클라이언트가 응답한 토큰(md5(md5(pw+user)+salt))",
                 "• 위 2개의 데이터가 암호화되지 않은 채 평문으로 고스란히 노출됩니다.",
                 "• 오픈소스 해킹 도구인 Hashcat(모드 11100: PostgreSQL Challenge-Response)에 이 두 값을 넣고 실행하면:",
                 "   - 오프라인 상태에서 네트워크 패킷 데이터로부터 원래의 평문 비밀번호를 즉시 복구해 냅니다.",
                 "• 3_exploit_md5_crack.py 스크립트 시연 결과 0.00001초 만에 실제 패스워드가 복구되었습니다."
             ])

    # -------------------------------------------------------------
    # SLIDE 9: 실습 환경 침투 실증 결과
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "[실증 결과] 구축된 Docker 컨테이너 실제 공격 및 탈취 검증", "7. 모의 침투 실증 결과")

    add_card(slide9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "1. Docker 랩 구성 및 공식 Deprecated 경고",
             [
                 "• 환경: postgres:latest 공식 이미지 + MD5 설정 강제 적용",
                 "   - postgresql.conf : password_encryption = md5",
                 "   - pg_hba.conf : host/local all all md5",
                 "• 초기화 및 기동 시 PostgreSQL 공식 엔진의 로그 출력:",
                 "   - [WARNING] setting an MD5-encrypted password",
                 "   - [DETAIL] MD5 password support is deprecated and will be removed in a future release of PostgreSQL.",
                 "   - [HINT] Refer to PostgreSQL documentation for migrating to another password type.",
                 "• 공식 엔진 차원에서도 MD5는 완전히 폐기 수순을 밟고 있는 위험 기술임을 자인하고 있습니다."
             ])

    add_card(slide9, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1),
             "2. Pass-the-Hash 익스플로잇 실행 결과 (데이터 탈취)",
             [
                 "• 타겟 계정: app_user (평문 비밀번호: 절대 입력하지 않음)",
                 "• 탈취된 해시 주입: md56a4473637a18da137b70dddbc1d39a4b",
                 "• 실행 결과: 즉시 AuthenticationOk(0) 승인 및 세션 탈취 성공",
                 "• [탈취된 사내 기밀 데이터 실측]:",
                 "   - R&D | PROJ-QUANTUM-9921 | TOP SECRET (차세대 AI 트레이딩 엔진)",
                 "   - Finance | CORP-BANK-ACCOUNTS | CONFIDENTIAL (해외 에스크로 계좌)",
                 "   - HR | EXEC-SALARY-TABLE-2026 | SECRET (임원진 보수 및 배수표)",
                 "   - Security | VPN-GATEWAY-MASTER-KEY | TOP SECRET (글로벌 VPN 키)",
                 "   - 홍길동, 김철수 등 사내 임직원 전원의 연봉 및 개인정보 전량 유출"
             ], header_color=RED_ACCENT)

    # -------------------------------------------------------------
    # SLIDE 10: 컴플라이언스 및 법적 위험성
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "[감사 및 규정] MD5 다운그레이드 시 발생하는 법적/규제 위험", "8. 컴플라이언스 영향도")

    add_card(slide10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1),
             "1. 국내외 보안 인증 및 법률 가이드라인 위반",
             [
                 "• ISMS-P 인증 기준 (2.7.1 암호정책 정의 및 운영):",
                 "   - 비밀번호 등 주요 인증 정보 저장 시 안전성이 입증된 일방향 암호화 알고리즘(SHA-256 이상) 적용을 의무화합니다.",
                 "   - MD5, SHA-1과 같이 안전하지 않은 취약 알고리즘의 사용은 중대 결함(인증 취소/보완 요구 사유)에 해당합니다.",
                 "• 개인정보보호위원회 고시 (개인정보의 안전성 확보조치 기준):",
                 "   - 비밀번호는 일방향 암호화하여 저장하되 안전한 해시 함수를 사용하도록 강제하고 있습니다.",
                 "• 금융보안원 금융분야 암호기술 안내서:",
                 "   - 패스워드 해싱 시 솔트 적용 및 PBKDF2/Argon2 등의 키 스트레칭 적용을 명시하여 MD5를 전면 금지합니다."
             ], header_color=RED_ACCENT)

    add_card(slide10, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1),
             "2. 침해 사고 발생 시 책임 소재와 기술 부채",
             [
                 "• 감사 지적 및 법적 과징금 리스크:",
                 "   - 만에 하나 DB 유출 사고가 발생했을 때, 보안팀의 요청으로 안전한 SCRAM-SHA-256을 취약한 MD5로 고의 다운그레이드한 사실이 드러나면 중과실 판정을 피할 수 없습니다.",
                 "• 차기 버전 업그레이드 불가 (기술적 고립):",
                 "   - PostgreSQL 14부터 SCRAM이 기본값이며, 조만간 릴리즈될 버전에서는 MD5 지원 코드가 엔진에서 완전히 삭제됩니다.",
                 "   - 구형 솔루션 때문에 DB 전체의 버전 업그레이드가 영구히 가로막히는 막대한 기술 부채가 발생합니다."
             ])

    # -------------------------------------------------------------
    # SLIDE 11: 최종 대응 전략 및 해결책
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "[최종 권고] 보안팀 설득 논리 및 기술적 대체 해결 방안", "9. 실무 실행 가이드")

    add_card(slide11, Inches(0.8), Inches(1.8), Inches(3.7), Inches(5.1),
             "대안 1 (최선책)\n솔루션 벤더 패치 요청",
             [
                 "• 원인 제공처인 DB 접근 제어 소프트웨어 제조사에 공식 패치를 강력히 요청합니다.",
                 "• PostgreSQL 10 버전(SCRAM 도입)이 출시된 지 8년이 넘었으므로 최신 libpq 클라이언트 라이브러리를 연동한 패치 버전을 제공받는 것이 정석입니다.",
                 "• 유지보수 계약을 맺고 있는 솔루션이라면 보안 컴플라이언스 미충족을 근거로 무상 기술지원을 요구해야 합니다."
             ], header_color=GREEN_ACCENT)

    add_card(slide11, Inches(4.8), Inches(1.8), Inches(3.7), Inches(5.1),
             "대안 2 (차선책)\n로깅 아키텍처 현대화",
             [
                 "• 인증 패킷을 가로채서 해석하는 구형 인라인 프록시 방식 대신 호스트/엔진 레벨 로깅으로 전환합니다.",
                 "• PostgreSQL 공식 감사 확장 모듈인 'pgaudit'을 활성화하여 완벽한 SQL 접근 및 쿼리 실행 로그를 남깁니다.",
                 "• 또는 eBPF 기반 최신 경량 에이전트를 도입하여 DB 인증 프로토콜을 건드리지 않고 완벽한 접근 기록을 남길 수 있습니다."
             ], header_color=BLUE_ACCENT)

    add_card(slide11, Inches(8.8), Inches(1.8), Inches(3.7), Inches(5.1),
             "대안 3 (과도기 임시 조치)\n극단적 네트워크 통제",
             [
                 "• 패치가 완료될 때까지 부득이하게 MD5를 유지해야 한다면 다음 보완 조치를 강제해야 합니다:",
                 "  1) 포트 접근 통제: DB 포트(5432)는 오직 접근 제어 솔루션의 고정 IP만 화이트리스팅",
                 "  2) 외부 차단: 개발자/운영자 PC 대역에서 DB로의 직접 TCP 연결을 방화벽에서 전면 차단",
                 "  3) TLS/mTLS 강제: 네트워크 스니핑을 원천 방어하기 위해 SSL/TLS 상호 인증 필수 적용"
             ], header_color=NAVY)

    # -------------------------------------------------------------
    # SLIDE 12: 요약 및 맺음말
    # -------------------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    bg12 = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg12.fill.solid()
    bg12.fill.fore_color.rgb = NAVY
    bg12.line.fill.background()

    tbox12 = slide12.shapes.add_textbox(Inches(1.2), Inches(1.5), Inches(11.0), Inches(5.0))
    tf12 = tbox12.text_frame
    tf12.word_wrap = True

    p0 = tf12.paragraphs[0]
    p0.text = "SUMMARY & CONCLUSION"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(180, 205, 237)
    p0.font.name = "Malgun Gothic"
    p0.space_after = Pt(12)

    p1 = tf12.add_paragraph()
    p1.text = "보안팀 설득을 위한 한 줄 요약 보고"
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.font.name = "Malgun Gothic"
    p1.space_after = Pt(24)

    summary_points = [
        "1. 암호학적 규명: MD5는 '충돌 공격'으로 뚫리는 것이 아닙니다. DB 로그인은 '역상 공격' 대상이며 이는 여전히 불가능합니다.",
        "2. 실질적 침투 위협: 하지만 'Pass-the-Hash'와 '초고속 크래킹'이라는 치명적인 프로토콜 결함 때문에 DB가 완벽히 장악됩니다.",
        "3. 실증 완료: 평문 패스워드를 모르는 상태에서 유출된 해시 문자열만으로 DB에 침투하여 사내 1급 기밀 전량을 성공적으로 탈취했습니다.",
        "4. 최종 결론: 구형 솔루션 연동을 위한 MD5 다운그레이드는 보안을 심각하게 훼손하고 규정을 위반하므로 솔루션 패치 및 로깅 체계 전환을 강력히 권고합니다."
    ]

    for sp in summary_points:
        p = tf12.add_paragraph()
        p.text = sp
        p.font.size = Pt(13.5)
        p.font.color.rgb = RGBColor(230, 238, 248)
        p.font.name = "Malgun Gothic"
        p.space_after = Pt(14)

    output_filename = "PostgreSQL_MD5_다운그레이드_보안분석_및_침투실증.pptx"
    prs.save(output_filename)
    print(f"[SUCCESS] Presentation generated successfully: {output_filename}")

if __name__ == "__main__":
    create_presentation()
