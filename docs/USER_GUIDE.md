---
title: "SolarBASIC User Guide"
version: "1.0.0"
author: "FluxVibe"
---

SolarBASIC — User Guide

# SolarBASIC User Guide

> 1980s 홈 컴퓨터 BASIC 감성과 GitHub 스타일 문서가 만나는 곳. 이 안내서는 **최종 사용자**가 SolarBASIC v1.0.0을 바로 써볼 수 있도록 구성했습니다.

## 설치와 실행
- **요구 사항:** Python 3.10+
- **REPL:** `python main.py`
- **스크립트 실행:** `python main.py examples/demo.bas`
- **디버그 모드:** `python main.py --debug examples/demo.bas`
- **버전 확인:** `python main.py --version`

## 빠른 개념 요약
- **라인 번호가 있으면** 프로그램 메모리에 저장, `RUN`으로 실행.
- **라인 번호가 없으면** 즉시 실행(direct mode). GOSUB/WHILE 블록은 프로그램 모드에서 사용.
- **스코프 규칙:**
  - `X = expr` → 함수 내부에서는 로컬 우선, 없으면 새 로컬 생성. 전역에서는 전역.
  - `LET X = expr` → 항상 전역 변수에 기록.
  - 식별자 조회는 로컬 → 전역 순.

## 주요 명령/구문과 예제
### 출력과 수식
```basic
PRINT "HELLO"
PRINT 1 + 2 * 3
PRINT SGN(-5)
```

### 변수 대입
```basic
LET N = 3       ' 전역 강제
X = 10          ' 현재 스코프에 저장
X = X + 5
PRINT X
```

### 조건 / 반복
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

### LED 시뮬레이션
```basic
LED 0 0 ON
LED 2 2 OFF
```
LED 좌표는 0~4 범위를 권장합니다. 유효하지 않은 좌표는 친절한 오류로 안내됩니다.

### 내장 숫자 함수
- `RND(N)` : 0 이상 N 미만 정수(비양수면 0)
- `ABS(X)` : 절대값
- `SGN(X)` : 부호

## 실수 예방 팁
- `RUN` 전에는 `LIST`로 저장된 라인을 확인하세요.
- GOSUB/RETURN은 프로그램 모드에서만 유효합니다.
- 함수 내부에서는 GOSUB/라인 RETURN 사용 금지.
- 정의되지 않은 변수를 PRINT하면 런타임 오류가 납니다.

## FAQ
| 질문 | 답변 |
| --- | --- |
| READY> 프롬프트에서 EOF(CTRL+D)로 종료되나요? | 네, 종료 메시지와 함께 종료됩니다. |
| 무한 루프가 걸리면? | `RUN --step-limit N`으로 제한하거나 기본 10,000 스텝 제한이 오류를 발생시킵니다. |
| 난수 초기값은? | Python 기본 시드에 따르며, 필요하면 `import random`으로 시드를 설정한 후 실행할 수 있습니다. |

## 오류 메시지 예시
- `RUNTIME ERROR: Undefined variable X`
- `RUNTIME ERROR: RETURN without GOSUB`
- `ERROR: Step limit exceeded (possible infinite loop)`

## 권장 패턴
- 함수는 짧고 명확하게, 반환값 중심으로 작성합니다.
- LED 명령은 디버그 모드에서 TRACE와 함께 사용하면 흐름을 파악하기 쉽습니다.
- 프로그램을 저장하기 전 `NEW`로 초기화해 이전 상태를 지울 수 있습니다.

## 추가 학습
- `docs/QUICKSTART.md`에서 1분 만에 배우기
- `docs/DEVELOPER_SPEC.md`에서 내부 동작과 확장 정책 확인

