---
title: "SolarBASIC 퀵스타트"
version: "1.0.0"
author: "FluxVibe"
---

# SolarBASIC 퀵스타트

언어: 한국어 | [English](QUICKSTART.md)

> 1분 안에 SolarBASIC을 익힙니다. 모든 예제는 REPL이나 `python main.py <file>`로 바로 실행할 수 있습니다.

## 시작하기
```bash
python main.py            # REPL
python main.py demo.bas   # 스크립트 실행
```

## 예제 모음 (7+)
### 1) Hello와 변수
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

### 4) GOSUB/RETURN
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

### 6) 합계 함수
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
- 더 많은 예제: `examples/`
- 개발자 세부사항: `docs/DEVELOPER_SPEC.ko.md`
- 전체 가이드: `docs/USER_GUIDE.ko.md`
