---
title: "SolarBASIC Quickstart"
version: "1.0.0"
author: "FluxVibe"
---

SolarBASIC — Quickstart

# SolarBASIC Quickstart

> 1분 안에 SolarBASIC을 맛보는 초보자용 빠른 안내. 모든 예제는 REPL 또는 `python main.py <file>`로 바로 실행할 수 있습니다.

## 시작하기
```bash
python main.py            # REPL
python main.py demo.bas   # 스크립트
```

## 예제 모음 (5개 이상)

### 1) Hello + 변수
```basic
PRINT "HELLO"
LET X = 5
PRINT X
```

### 2) 반복과 조건
```basic
10 X = 0
20 WHILE X < 3
30 PRINT X
40 X = X + 1
50 WEND
```

### 3) 함수와 SGN
```basic
10 FUNC SIGN3(N)
20 RETURN SGN(N)
30 ENDFUNC
40 PRINT SIGN3(-7)
```

### 4) GOSUB와 복귀
```basic
10 GOSUB 100
20 PRINT "BACK"
30 EXIT
100 PRINT "SUB"
110 RETURN
```

### 5) LED와 난수
```basic
LED 0 0 ON
PRINT RND(5)
```

### 6) 합계 계산
```basic
10 FUNC ADD2(A,B)
20 RETURN A + B
30 ENDFUNC
40 PRINT ADD2(4,6)
```

### 7) 루프 종료 감지
```basic
10 X = 5
20 IF X = 0 THEN PRINT "DONE"
30 X = X - 1
40 IF X > 0 THEN GOTO 20
50 PRINT "END"
```

## 다음 단계
- 더 많은 예제는 `examples/` 폴더를 확인하세요.
- 세부 사양: `docs/DEVELOPER_SPEC.md`
- 사용자 설명서: `docs/USER_GUIDE.md`

