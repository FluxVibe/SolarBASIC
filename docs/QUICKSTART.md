---
title: "SolarBASIC Quickstart"
version: "1.0.0"
author: "FluxVibe"
---

# SolarBASIC Quickstart

Language: English (default) | [한국어 문서](QUICKSTART.ko.md)

> Learn SolarBASIC in under a minute. Every snippet runs in the REPL or via `python main.py <file>`.

## Get started
```bash
python main.py            # REPL
python main.py demo.bas   # script
```

## Example set (7+)

### 1) Hello + variables
```basic
PRINT "HELLO"
LET X = 5
PRINT X
```

### 2) Loops and conditions
```basic
10 X = 0
20 WHILE X < 3
30 PRINT X
40 X = X + 1
50 WEND
```

### 3) Functions and SGN
```basic
10 FUNC SIGN3(N)
20 RETURN SGN(N)
30 ENDFUNC
40 PRINT SIGN3(-7)
```

### 4) GOSUB and return
```basic
10 GOSUB 100
20 PRINT "BACK"
30 EXIT
100 PRINT "SUB"
110 RETURN
```

### 5) LED and random
```basic
LED 0 0 ON
PRINT RND(5)
```

### 6) Sum function
```basic
10 FUNC ADD2(A,B)
20 RETURN A + B
30 ENDFUNC
40 PRINT ADD2(4,6)
```

### 7) Loop exit detection
```basic
10 X = 5
20 IF X = 0 THEN PRINT "DONE"
30 X = X - 1
40 IF X > 0 THEN GOTO 20
50 PRINT "END"
```

## Next steps
- More examples: `examples/`
- Developer details: `docs/DEVELOPER_SPEC.md`
- Full guide: `docs/USER_GUIDE.md`

