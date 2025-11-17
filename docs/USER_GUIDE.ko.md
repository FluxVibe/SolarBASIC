---
title: "SolarBASIC 사용자 가이드"
version: "1.0.0"
author: "FluxVibe"
---

# SolarBASIC 사용자 가이드

언어: 한국어 | [English](USER_GUIDE.md)

> 1980년대 홈 컴퓨터 BASIC 감성과 현대 OSS 문서 톤을 합쳤습니다. 이 가이드는 **최종 사용자**가 SolarBASIC v1.0.0을 바로 활용하도록 돕습니다.

## 설치 및 실행
- **필수:** Python 3.10+
- **REPL:** `python main.py`
- **스크립트 실행:** `python main.py examples/demo.bas`
- **디버그 모드:** `python main.py --debug examples/demo.bas`
- **버전 보기:** `python main.py --version`

## 핵심 개념
- **라인 번호**가 있으면 프로그램으로 저장하며 `RUN`으로 실행합니다.
- **라인 번호 없음** → direct mode(즉시 실행). GOSUB/WHILE 같은 블록 명령은 프로그램 모드에서 사용하세요.
- **스코프 규칙:**
  - `X = expr` → 현재 스코프 이름을 갱신하거나, 함수 안에서는 새 지역 변수를 만듭니다. 전역에서는 전역 갱신.
  - `LET X = expr` → 항상 전역 테이블에 기록합니다.
  - 조회 순서: 지역 → 전역. 없으면 `RUNTIME ERROR: Undefined variable <name>`.

## 핵심 명령과 예제
### 출력과 표현식
```basic
PRINT "HELLO"
PRINT 1 + 2 * 3
PRINT SGN(-5)
```

### 대입
```basic
LET N = 3       ' 전역 강제
X = 10          ' 현재 스코프
X = X + 5
PRINT X
```

### 조건/반복
```basic
IF X > 5 THEN PRINT "BIG"
10 WHILE X < 5
20 X = X + 1
30 WEND
```

### 함수와 호출
```basic
10 FUNC ADD(A,B)
20 RETURN A + B
30 ENDFUNC
40 PRINT ADD(2,3)
```

### 라인 기반 서브루틴 (GOSUB/RETURN)
```basic
10 GOSUB 100
20 PRINT "MAIN"
30 EXIT
100 PRINT "SUB"
110 RETURN
```

### LED 시뮬레이터
```basic
LED 0 0 ON
LED 2 2 OFF
```
좌표는 0–4 범위를 사용하며, 벗어나면 친절한 오류를 표시합니다.

### 내장 수치 함수
- `RND(N)` : [0, N) 범위 정수, N <= 0이면 0
- `ABS(X)` : 절대값
- `SGN(X)` : 부호(-1/0/1)

## 실수 예방 팁
- `RUN` 전 `LIST`로 저장된 코드를 확인하세요.
- GOSUB/RETURN은 프로그램 모드 전용입니다.
- 함수 내부에서는 GOSUB, 라인 RETURN을 사용할 수 없습니다.
- 정의되지 않은 변수를 출력하면 런타임 오류가 발생합니다.

## FAQ
| 질문 | 답변 |
| --- | --- |
| EOF(CTRL+D)로 종료할 수 있나요? | 네, 인사 메시지와 함께 종료됩니다. |
| 루프가 멈추지 않으면? | `--step-limit N`을 사용하거나 기본 10,000 스텝 가드를 활용하세요. |
| RND 시드는 어떻게 되나요? | Python 기본 시드를 따르며, 필요하면 실행 전 `import random; random.seed(...)`를 호출하세요. |

## 오류 메시지 예시
- `RUNTIME ERROR: Undefined variable X`
- `RUNTIME ERROR: RETURN without GOSUB`
- `ERROR: Step limit exceeded (possible infinite loop)`

## 권장 패턴
- 함수는 짧고 명확하게 작성하세요.
- LED 명령과 TRACE 모드를 함께 사용하면 흐름을 시각적으로 따라가기 쉽습니다.
- 새 프로그램을 로드하기 전 `NEW`로 상태를 초기화하세요.

## 추가 학습
- 퀵스타트: `docs/QUICKSTART.ko.md`
- 개발자 내부 구조: `docs/DEVELOPER_SPEC.ko.md`
