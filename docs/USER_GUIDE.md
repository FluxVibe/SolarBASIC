---
title: "SolarBASIC User Guide"
version: "1.0.0"
author: "FluxVibe"
---

# SolarBASIC User Guide

Language: English (default) | [한국어 문서](USER_GUIDE.ko.md)

> Where 1980s home-computer BASIC vibes meet GitHub-friendly docs. This guide helps **end users** get productive with SolarBASIC v1.0.0.

## Install & Run
- **Requirements:** Python 3.10+
- **REPL:** `python main.py`
- **Run a script:** `python main.py examples/demo.bas`
- **Debug mode:** `python main.py --debug examples/demo.bas`
- **Version:** `python main.py --version`

## Quick Concepts
- **Line numbers** store program text; run with `RUN`.
- **No line number** → direct mode (executes immediately). GOSUB/WHILE blocks are meant for program mode.
- **Scope rules:**
  - `X = expr` → updates existing name in the current scope or creates a new local inside functions; global otherwise.
  - `LET X = expr` → always writes to the global table.
  - Lookup order: local → global; otherwise `RUNTIME ERROR: Undefined variable <name>`.

## Core Commands & Examples
### Output and expressions
```basic
PRINT "HELLO"
PRINT 1 + 2 * 3
PRINT SGN(-5)
```

### Assignments
```basic
LET N = 3       ' force global
X = 10          ' stored in current scope
X = X + 5
PRINT X
```

### Conditions / loops
```basic
IF X > 5 THEN PRINT "BIG"
10 WHILE X < 5
20 X = X + 1
30 WEND
```

### Functions and calls
```basic
10 FUNC ADD(A,B)
20 RETURN A + B
30 ENDFUNC
40 PRINT ADD(2,3)
```

### Line-based subroutines (GOSUB/RETURN)
```basic
10 GOSUB 100
20 PRINT "MAIN"
30 EXIT
100 PRINT "SUB"
110 RETURN
```

### LED simulation
```basic
LED 0 0 ON
LED 2 2 OFF
```
LED coordinates are expected in 0–4; invalid coordinates produce a friendly error.

### Built-in numeric functions
- `RND(N)` : integer in [0, N), returns 0 if N <= 0
- `ABS(X)` : absolute value
- `SGN(X)` : sign (-1/0/1)

## Tips to avoid mistakes
- Check `LIST` before `RUN` to confirm stored lines.
- GOSUB/RETURN is valid in program mode only.
- Inside functions, GOSUB and line-based RETURN are disallowed.
- Printing an undefined variable raises a runtime error.

## FAQ
| Question | Answer |
| --- | --- |
| Can I exit with EOF (CTRL+D)? | Yes, you’ll see the goodbye message. |
| What if a loop hangs? | Use `--step-limit N` or rely on the default 10,000-step guard. |
| How is RND seeded? | Uses Python defaults; you can seed via `import random` before running. |

## Error message samples
- `RUNTIME ERROR: Undefined variable X`
- `RUNTIME ERROR: RETURN without GOSUB`
- `ERROR: Step limit exceeded (possible infinite loop)`

## Recommended patterns
- Keep functions short and return-focused.
- Pair LED commands with TRACE/debug mode to visualize control flow.
- Use `NEW` before loading fresh programs to clear previous state.

## Further learning
- Quickstart: `docs/QUICKSTART.md`
- Developer internals: `docs/DEVELOPER_SPEC.md`

