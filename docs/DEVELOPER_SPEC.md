---
title: "SolarBASIC Developer Specification"
version: "1.0.0"
author: "FluxVibe"
---

# SolarBASIC Developer Specification

Language: English (default) | [한국어 문서](DEVELOPER_SPEC.ko.md)

> Formal language notes, internals, and a touch of retro BASIC warmth. This reference is for contributors and language explorers.

## 1. Language philosophy
- 8-bit home-computer BASIC simplicity + modern OSS workflows
- Lightweight tokenizer/parser, clear errors, easy to port
- Future-friendly: open to VM/backends/variants (hardware deployment lives in other repos)

## 2. Components
- **Tokenizer**: splits input into tokens.
- **Parser**: builds Statement/Expression AST nodes.
- **Executor & ProgramRunner**: manage execution state, environments, and control flow.
- **FunctionTable**: registers user functions; built-ins take precedence.

![Runtime Flow](assets/runtime_flow.puml)

## 3. Grammar snapshot (BNF-ish)
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

## 4. Scope policy
- **Default assignment (`X = expr`)**: updates existing name in current scope; inside functions creates new locals when missing. Global scope updates globals.
- **Force global (`LET X = expr`)**: always writes to the global table.
- **Lookup order**: local → global; otherwise `RUNTIME ERROR: Undefined variable <name>`.

## 5. Control-flow constraints
- **GOTO/GOSUB/RETURN(line)**: program mode only; forbidden inside functions.
- **WHILE/WEND**: parser validates pairing; ProgramRunner re-evaluates conditions.
- **FUNC/RETURN(expr)**: isolated stack frame, local env; EXIT/GOTO/GOSUB forbidden inside functions.

## 6. Execution model
- **ProgramRunner**: sorted line list, program counter, GOSUB stack, step limit, TRACE logging.
- **CommandExecutor**: per-statement execution, LED simulator, built-ins RND/ABS/SGN.
- **ExpressionEvaluator**: recursive descent, comparisons, unary minus, function calls, identifier lookup.

### ASCII flow
```
User -> REPL -> Tokenizer -> Parser -> AST -> ProgramRunner
                                   |                |
                                   v                v
                              FunctionTable      Executor
```

## 7. Error model
- Syntax errors: reported with token position.
- Runtime errors: undefined variables, RETURN without GOSUB, out-of-range LED coordinates, etc.
- Guards: default 10,000-step limit, TRACE debug logging.

## 8. Extension notes
- Potential: extra built-ins, arrays, strings, file I/O.
- Ports/VMs can be explored separately while keeping the core platform-neutral.

## 9. Contribution quick notes
- Tests: `python -m unittest discover -s tests`
- Docs: Markdown with YAML front matter; diagrams live in `docs/assets`.
- Style: concise functions, user-friendly errors, never wrap imports in try/except.

