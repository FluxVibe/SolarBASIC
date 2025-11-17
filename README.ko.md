---
title: "SolarBASIC 레포지토리 개요"
version: "1.0.0"
author: "FluxVibe"
---

# SolarBASIC v1.0.0

언어: 한국어 | [English](README.md)

SolarBASIC는 8비트 홈 컴퓨터 BASIC 감성을 현대적으로 재구성한 **작고 배우기 쉬운 언어**입니다. READY> REPL, 가벼운 파서, 친절한 오류 메시지로 교육·실험·레트로 취미에 적합합니다.

## SolarBASIC이란?
간단한 BASIC 스타일 문법, 번호 있는 프로그램 라인, 즉시 실행 모드, 함수/제어 흐름/내장 함수, 5×5 LED 시뮬레이터를 갖춘 소형 언어입니다.

## 핵심 특징
- READY> REPL과 스크립트 실행(`python main.py <file>`)
- PRINT, 대입(일반/LET), IF/THEN, WHILE/WEND, GOTO, GOSUB/RETURN
- FUNC/RETURN 함수, 내장 수치 함수(RND/ABS/SGN), 5×5 LED 시뮬레이터
- 스텝 제한, TRACE 디버그 모드, 명확한 런타임 오류 메시지
- 버전 플래그(`--version`), 도움말(`HELP`/`ABOUT`), 함수 목록(`LISTF`)

## 빠른 시작
```bash
python main.py                     # REPL
python main.py examples/demo.bas   # 스크립트 실행
python main.py --debug --step-limit 5000 examples/demo.bas
python main.py --version
```
- 번호 없는 입력은 바로 실행되며, 번호가 있으면 프로그램으로 저장됩니다.
- 저장된 프로그램은 `RUN`으로 실행하고, `LIST`로 내용을 확인할 수 있습니다.

## 문서 모음
- 사용자 가이드(한국어): [docs/USER_GUIDE.ko.md](docs/USER_GUIDE.ko.md) | [English](docs/USER_GUIDE.md)
- 개발자 사양서(한국어): [docs/DEVELOPER_SPEC.ko.md](docs/DEVELOPER_SPEC.ko.md) | [English](docs/DEVELOPER_SPEC.md)
- 1분 퀵스타트(한국어): [docs/QUICKSTART.ko.md](docs/QUICKSTART.ko.md) | [English](docs/QUICKSTART.md)
- 변경 내역: [CHANGELOG.md](CHANGELOG.md)

## 예제
`examples/` 폴더에 바로 실행 가능한 10개 이상의 프로그램이 있습니다. REPL에서 `LISTF`로 함수 목록을 확인하거나 `HELP`로 명령 도움말을 볼 수 있습니다.

## 확장성
토크나이저/파서/실행 모델이 단순해 다른 VM이나 백엔드로의 포팅이 용이합니다. 하드웨어 배포는 본 리포지토리 범위 밖이지만, 미래 확장 가능성은 열려 있습니다.
