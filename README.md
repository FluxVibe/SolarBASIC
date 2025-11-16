# SolarBASIC Experiments

SolarBASIC is a mini language that aims for the 8-bit home-computer BASIC vibe. We are growing the interpreter over **10 incremental stages**, and the codebase currently implements **Stage 10 (polish)**.

## Current stage (10/10)
- Displays a `READY>` prompt.
- Exits on `EXIT`/`QUIT` (case-insensitive), the EXIT command, EOF (CTRL+D/CTRL+Z), or CTRL+C, and prints `Bye. :)`.
- Inputs that start with a line number are stored inside the program buffer (entering a bare line number deletes it).
- `LIST` prints the stored lines; `LIST FUNCS`/`LISTF` prints any registered `FUNC` headers. `NEW` clears the buffer (including functions and the LED matrix state).
- Direct-mode commands (`PRINT`, `LED`, `RUN`, `EXIT/QUIT`) are parsed via the tokenizer and executed immediately. `PRINT` accepts integer expressions with `+ - * /`, parentheses, unary minus, and comparison operators (`= <> < > <= >=`) in addition to blank lines or single string literals.
- `IF <expression> THEN <command>` is supported in direct mode. Any non-zero expression result is treated as true; comparison operators yield `1` or `0`.
- Stored programs run via `RUN`: lines are parsed, executed sequentially, and may jump with `GOTO <line>`. Attempting `GOTO` outside of `RUN` prints a friendly reminder instead of jumping.
- Stored programs may declare `WHILE <expression>` / `WEND` blocks. The loop condition reuses the expression grammar above; a false (zero) result skips to the matching `WEND`, while a true (non-zero) result keeps executing until `WEND` loops back. Direct mode still guides users to RUN for block structures.
- Stored programs may also define functions with `FUNC NAME(arg1, arg2, ...)` … `ENDFUNC`. Each function can contain statements (including `IF`, `WHILE/WEND`, and nested function calls) and must eventually hit `RETURN <expression>` (defaults to `0` if omitted). After `RUN` parses the program, functions become available to direct-mode expressions via standard call syntax (`PRINT ADD(1, 2)`). `RETURN`, `FUNC`, and `ENDFUNC` are only valid inside stored programs.
- Includes a reusable tokenizer (`solarbasic.tokenizer.Tokenizer`) that recognizes keywords, identifiers, integers, strings, and comparison/arithmetic operators.
- `LED x y ON|OFF` now visualizes a simulated 5×5 grid using `#` and `.` characters so you can see the overall LED layout evolve; `NEW` resets the matrix.
- `HELP` prints a condensed reference card, while `ABOUT` reports `SolarBASIC v0.1`, the author (FluxVibe), and the key feature set.
- `RUN` enforces a 10,000-step ceiling. Going beyond it prints `ERROR: Step limit exceeded (possible infinite loop)` to help catch runaway loops.
- `--debug` (see below) enables `TRACE: line <n>` logging just before each stored line executes.

## Debugging & safety
- `python main.py --debug` enables per-line tracing in addition to the standard output.
- `python main.py --step-limit 5000` customizes the safety ceiling when 10,000 steps is not ideal.
- CTRL+C, EOF, or `EXIT/QUIT` all share the same graceful shutdown path that prints `Bye. :)`.

## Run
```bash
python main.py
```

### Script mode
To run a `.bas` file without entering the REPL, pass it as the first argument:

```bash
python main.py examples/demo.bas
```

Lines without explicit numbers are auto-numbered behind the scenes so they still flow through the regular `RUN` machinery (meaning `GOTO` and loops behave exactly like they do inside the REPL).

For a scripted demonstration of Stage 10 capabilities run:

```bash
python scripts/stage10_smoke.py
```

## Tests

Basic unit tests cover the requested focus areas (expression parsing, IF/THEN, WHILE/WEND handling, and FUNC/RETURN):

```bash
python -m unittest discover -s tests
```

## Roadmap
Stage 10 completes the initial SolarBASIC prototype scope (REPL, arithmetic expressions, IF/THEN, GOTO, WHILE/WEND, functions, and LED simulation). Future experiments will branch out from this baseline.
