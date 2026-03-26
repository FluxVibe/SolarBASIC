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

## 크레딧 & 감사의 글

SolarBASIC은 복고풍 BASIC의 따뜻한 단순함과,
현대 스크립트 언어에서 기대되는 명확한 구조를
조화롭게 담아내기 위해 독립적으로 설계된
프로그래밍 언어 프로젝트입니다.

이 프로젝트는 **FluxVibe**가 직접 구상하고,
언어 규칙, 실행 모델, 기능 로드맵, 테스트 방향 등을 설계하며
AI 보조 기반의 사양 주도형 개발 방식으로 완성되었습니다.
이는 사람과 AI가 앞으로 어떤 방식으로 함께 개발을 할 수 있는지,
그 가능성과 과정을 탐구하는 실험적 의미도 담고 있습니다.

### 개발 방식
- 아이디어, 언어 철학, 기능 정의, 테스트 기준, 품질 검증은  
  모두 사람에 의해 직접 설계 및 관리되었습니다.
- 구현과 반복 개발은 인간의 지시와 구조 설계를 기반으로  
  **OpenAI Codex**의 도움을 받아 빠르게 진행되었습니다.
- 아키텍처 결정, 설계 검증, 버그 분석 및 철학적 정렬은  
  **ChatGPT와의 논의**를 통해 함께 다듬어졌습니다.

### 제작 의도
SolarBASIC은 단순한 인터프리터 구현을 넘어,  
“**코드를 직접 작성하는 것만이 창조의 전부인가?**”  
라는 질문을 담고 있습니다.  
다음 시대의 개발은 **혼자 만드는 것**이 아니라,  
**함께 설계하는 것**일지 모릅니다.

### Special Thanks
레트로 컴퓨팅과 작은 인터프리터 언어를 사랑하는 사람들,  
그리고 READY> 프롬프트가 주는 묘한 설렘을 아는 모두에게  
이 프로젝트를 바칩니다.

그리고 앞으로 SolarBASIC에 기여해 주실 모든 분들께 미리 감사드립니다.
이 프로젝트는 한 사람의 작업으로만 완성되지 않으며,
아이디어 제안, 코드 기여, 버그 리포트, 문서 보완, 토론 참여 등
모든 형태의 기여는 동등하게 소중합니다.

함께 발전시키고, 함께 배우고, 함께 더 나은 작은 언어를 만들어갑시다. :)

READY>
