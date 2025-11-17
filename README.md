---
title: "SolarBASIC Repository Overview"
version: "1.0.0"
author: "FluxVibe"
---


# SolarBASIC v1.0.0

SolarBASIC은 8비트 홈 컴퓨터 BASIC 감성을 현대 OSS 워크플로에 맞게 재해석한 **작고 배우기 쉬운 미니 언어**입니다.

## 핵심 특징
- READY> REPL과 스크립트 실행(`python main.py <file>`)
- PRINT, 변수 대입(기본/LET), IF/THEN, WHILE/WEND, GOTO, GOSUB/RETURN
- FUNC/RETURN 함수, 내장 함수(RND/ABS/SGN), 5×5 LED 시뮬레이터
- 스텝 제한, TRACE 디버그 모드, 친절한 오류 메시지
- 버전 플래그(`--version`), 도움말(`HELP`/`ABOUT`), 함수 목록(`LISTF`)

## 빠른 시작
```bash
python main.py             # REPL
python main.py examples/demo.bas  # 스크립트 실행
python main.py --debug --step-limit 5000 examples/demo.bas
python main.py --version
```
- direct mode에서는 단일 명령을 즉시 실행합니다.
- 라인 번호가 있는 입력은 프로그램으로 저장하고 `RUN`으로 실행합니다.

## 문서 모음
- 사용자 가이드: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- 개발자 사양서: [docs/DEVELOPER_SPEC.md](docs/DEVELOPER_SPEC.md)
- 1분 빠른 시작: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- 변경 기록: [CHANGELOG.md](CHANGELOG.md)

## 브랜드 가이드 (요약)
- 로고 이미지는 별도 배포하지 않으며, 텍스트 기반 “SolarBASIC” 워드마크를 사용합니다.
- 명칭: “SolarBASIC”을 단일 단어로 표기합니다.
- 톤: 레트로 BASIC 매뉴얼 감성과 현대적 친절함을 함께 유지합니다.

## 예제
`examples/` 폴더에 최소 10개의 실용 예제가 있습니다. REPL에서는 `LIST`로 저장된 프로그램을 확인하고, `LISTF`로 함수 헤더를 나열할 수 있습니다.

## 확장성
- 코어 인터프리터는 가벼운 파서와 명확한 AST/실행 모델을 갖추고 있으며, VM이나 다른 플랫폼으로의 포팅도 염두에 두고 설계되었습니다. (하드웨어 배포 내용은 본 저장소에서 다루지 않습니다.)

