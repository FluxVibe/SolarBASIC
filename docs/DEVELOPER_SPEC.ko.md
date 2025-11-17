---
title: "SolarBASIC 개발자 사양서"
version: "1.0.0"
author: "FluxVibe"
---

# SolarBASIC 개발자 사양서

언어: 한국어 | [English](DEVELOPER_SPEC.md)

> 공식 언어 노트와 내부 구조를 정리한 문서입니다. 레트로 BASIC 감성과 현대 OSS 문서 스타일을 함께 담았습니다.

## 1. 언어 철학
- 8비트 BASIC 단순함 + 현대 OSS 워크플로
- 가벼운 토크나이저/파서, 명확한 오류, 포팅 용이성
- 미래 확장 대비: VM/백엔드/변형 가능 (하드웨어 배포는 별도 리포지토리)

## 2. 구성 요소
- **Tokenizer**: 입력을 토큰으로 분리
- **Parser**: Statement/Expression AST 생성
- **Executor & ProgramRunner**: 실행 상태, 환경, 제어 흐름 관리
- **FunctionTable**: 사용자 함수 등록, 내장 함수 우선 처리

![Runtime Flow](assets/runtime_flow.puml)

## 3. 문법 스냅샷 (BNF 유사)
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

## 4. 스코프 정책
- **기본 대입(`X = expr`)**: 현재 스코프에 존재하면 갱신; 함수 내부에서는 없으면 새 지역 변수 생성. 전역에서는 전역 갱신.
- **전역 강제(`LET X = expr`)**: 항상 전역 테이블에 기록.
- **조회 순서**: 지역 → 전역 → 없으면 `RUNTIME ERROR: Undefined variable <name>`.

## 5. 제어 흐름 제약
- **GOTO/GOSUB/RETURN(라인)**: 프로그램 모드 전용, 함수 내부 금지.
- **WHILE/WEND**: 파서가 짝을 확인하고 ProgramRunner가 조건을 재평가.
- **FUNC/RETURN(expr)**: 독립 스택 프레임과 지역 환경. 함수 안에서는 EXIT/GOTO/GOSUB 금지.

## 6. 실행 모델
- **ProgramRunner**: 정렬된 라인 목록, 프로그램 카운터, GOSUB 스택, 스텝 제한, TRACE 로깅.
- **CommandExecutor**: 명령 실행, LED 시뮬레이터, 내장 함수(RND/ABS/SGN).
- **ExpressionEvaluator**: 재귀 하강, 비교 연산, 단항 음수, 함수 호출, 식별자 조회.

### ASCII 흐름
```
User -> REPL -> Tokenizer -> Parser -> AST -> ProgramRunner
                                   |                |
                                   v                v
                              FunctionTable      Executor
```

## 7. 오류 모델
- 문법 오류: 토큰 위치와 함께 보고
- 런타임 오류: 정의되지 않은 변수, RETURN without GOSUB, LED 좌표 초과 등
- 가드: 기본 10,000 스텝 제한, TRACE 디버그 로깅

## 8. 확장 노트
- 후보: 추가 내장 함수, 배열, 문자열, 파일 I/O 등
- 포팅/VM은 코어를 플랫폼 중립적으로 유지하면서 별도 리포지토리에서 탐구 가능

## 9. 기여 팁
- 테스트: `python -m unittest discover -s tests`
- 문서: YAML 프런트매터 포함 Markdown, 다이어그램은 `docs/assets`에 배치
- 스타일: 간결한 함수, 친절한 오류, import를 try/except로 감싸지 않기
