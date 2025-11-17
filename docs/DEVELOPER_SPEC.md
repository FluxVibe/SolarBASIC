---
title: "SolarBASIC Developer Specification"
version: "1.0.0"
author: "FluxVibe"
---

SolarBASIC — Developer Specification

# SolarBASIC Developer Specification

> 정식 언어 사양, 내부 구조 해설, 그리고 레트로 BASIC 매뉴얼의 따뜻한 감성을 담았습니다. 본 문서는 개발자와 기여자를 위한 참고서입니다.

## 1. 언어 철학과 목표
- 8비트 홈 컴퓨터 BASIC의 단순함 + 현대 OSS 워크플로
- 가벼운 파서/토크나이저, 명확한 오류 메시지, 포팅 용이성
- 미래 확장성: VM, 다른 CPU, 교육용 변종 등에 열려 있음 (하드웨어 배포는 별도 저장소에서 다룸)

## 2. 구성 요소 개요
- **Tokenizer**: 입력을 토큰 스트림으로 분해.
- **Parser**: Statement/Expression AST 생성.
- **Executor & ProgramRunner**: 실행 상태, 변수 환경, 제어 흐름 관리.
- **FunctionTable**: 사용자 정의 함수 등록/호출, 내장 함수 우선 처리.

![Runtime Flow](assets/runtime_flow.puml)

## 3. 문법 개요 (요약 BNF)
```
program      ::= { line }
line         ::= NUMBER statement
statement    ::= print | led | list | new | run | goto | gosub | return | while | wend
               | ifthen | func | endfunc | assignment | about | help | listfuncs | exit
assignment   ::= ["LET"] IDENT "=" expr
print        ::= "PRINT" expr_list
expr_list    ::= expr { "," expr }
ifthen       ::= "IF" expr relop expr "THEN" statement
while        ::= "WHILE" expr
wend         ::= "WEND"
func         ::= "FUNC" IDENT "(" [args] ")"
args         ::= IDENT {"," IDENT}
expr         ::= term {("+"|"-") term}
term         ::= factor {("*"|"/") factor}
factor       ::= NUMBER | STRING | IDENT | call | "(" expr ")" | "-" factor
call         ::= IDENT "(" [expr_list] ")"
```

## 4. 변수 스코프 정책
- **기본 대입 (`X = expr`)**: 현재 스코프에 존재하면 갱신, 없으면 새 로컬 생성(함수 내부). 전역에서는 전역 갱신.
- **강제 전역 (`LET X = expr`)**: 항상 전역 테이블에 기록.
- **조회 순서**: 로컬 → 전역. 존재하지 않으면 `RUNTIME ERROR: Undefined variable <name>`.

## 5. 제어 흐름 제약
- **GOTO/GOSUB/RETURN(line)**: 프로그램 모드 전용. 함수 내부에서는 오류를 발생시킴.
- **WHILE/WEND**: 파서에서 짝 확인 후 ProgramRunner가 조건 재평가.
- **FUNC/RETURN(expr)**: 독립 스택 프레임, 로컬 환경, RETURN으로 종료. 함수 내부에서 EXIT/GOTO/GOSUB 금지.

## 6. 실행 모델
- **ProgramRunner**: 정렬된 라인 목록, 프로그램 카운터, GOSUB 스택, 스텝 제한, TRACE 로깅.
- **CommandExecutor**: Statement 타입별 실행, LED 시뮬레이터, 내장 함수(RND/ABS/SGN) 처리.
- **ExpressionEvaluator**: 중위 표기 재귀 파싱, 비교 연산, 단항 -, 함수 호출, 식별자 조회.

### 간단한 실행 흐름 다이어그램 (ASCII)
```
User -> REPL -> Tokenizer -> Parser -> AST -> ProgramRunner
                                   |                |
                                   v                v
                              FunctionTable      Executor
```

## 7. 오류 모델
- 구문 오류: 토큰 위치와 함께 메시지 출력.
- 런타임 오류: 정의되지 않은 변수, RETURN without GOSUB, 범위 밖 LED 좌표 등.
- 안전장치: 기본 10,000 스텝 제한, debug TRACE 로그.

## 8. 확장 방안
- 추가 내장 함수, 파일 I/O, 배열, 문자열 확장 등 소프트웨어적 확장.
- 다른 VM/플랫폼 포팅은 별도 저장소에서 다루되, 코어 설계는 플랫폼 독립적으로 유지.

## 9. 기여 가이드 요약
- 테스트: `python -m unittest discover -s tests`
- 문서: Markdown + YAML front-matter, PlantUML 다이어그램 `docs/assets`에 배치.
- 코딩 스타일: 간결한 함수, 예외 시 사용자 친화 메시지, try/catch로 import 감싸지 않기.

