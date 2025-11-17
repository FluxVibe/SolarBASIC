---
title: "SolarBASIC Repository Overview"
version: "1.0.0"
author: "FluxVibe"
---

# SolarBASIC v1.0.0

Language: English (default) | [한국어 문서 보기](README.ko.md)

SolarBASIC is a **tiny, learner-friendly language** that reimagines 8-bit home computer BASIC for modern OSS workflows.

## What is SolarBASIC?
A compact BASIC-like language with a READY> REPL, lightweight parser, and friendly errors—designed for quick experiments, teaching, and retro-inspired fun.

## Key Features
- READY> REPL and script execution (`python main.py <file>`)
- PRINT, assignments (implicit/LET), IF/THEN, WHILE/WEND, GOTO, GOSUB/RETURN
- FUNC/RETURN functions, built-ins (RND/ABS/SGN), 5×5 LED simulator
- Step limit, TRACE debug mode, and helpful runtime errors
- Version flag (`--version`), help/metadata (`HELP`/`ABOUT`), function listing (`LISTF`)

## Quick Start
```bash
python main.py                     # REPL
python main.py examples/demo.bas   # run a script
python main.py --debug --step-limit 5000 examples/demo.bas
python main.py --version
```
- Direct mode executes single commands immediately.
- Numbered input is stored as a program and run via `RUN`.

## Documentation Set
- User Guide: [docs/USER_GUIDE.md](docs/USER_GUIDE.md) | [한국어](docs/USER_GUIDE.ko.md)
- Developer Specification: [docs/DEVELOPER_SPEC.md](docs/DEVELOPER_SPEC.md) | [한국어](docs/DEVELOPER_SPEC.ko.md)
- 1-minute Quickstart: [docs/QUICKSTART.md](docs/QUICKSTART.md) | [한국어](docs/QUICKSTART.ko.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)

## Examples
`examples/` contains 10+ runnable snippets. In the REPL, use `LIST` to view stored programs and `LISTF` to list function headers.

## Extensibility
The interpreter uses a small tokenizer/parser, clear AST, and execution model, making it amenable to future ports or VM backends. Hardware deployment is intentionally out of scope for this repository.

Looking for Korean? Read [README.ko.md](README.ko.md) for the full Korean walkthrough and language links.

## Credits & Acknowledgements

SolarBASIC is an independently designed programming language project
created with the goal of blending the warm simplicity of retro BASIC
with the clarity and structure expected in modern scripting languages.

This project was envisioned, directed, documented, tested, and refined
by **FluxVibe**, with the development process intentionally built on
an **AI-assisted, specification-driven workflow** to explore the future
of programming collaboration between human creativity and intelligent tools.

### Development Model
- Idea, language rules, execution model, feature roadmap, test logic,  
  and final quality approval were manually designed and reviewed.
- Implementation and rapid iteration were accelerated using  
  **OpenAI Codex** under human supervision and structural guidance.
- Architectural discussions, language philosophy alignment, and  
  debugging insight were supported by **ChatGPT** sessions.

### Creative Intent
SolarBASIC is not only a working interpreter, but also a small
experiment about *how people and AI will co-create software in the future*.
It is a reminder that **writing code is important, but designing meaning
is even more important**.

### Special Thanks
To everyone who loves retro computing, tiny languages,
and glowing READY> prompts — this project is dedicated to you.

And to everyone who may contribute to SolarBASIC in the future — thank you in advance.
This project is not something that can be completed by one person alone.
All forms of contribution are equally valuable, whether it’s proposing ideas,
submitting code, reporting bugs, improving documentation, or participating in discussions.

Let’s grow, learn, and build a better small language together.

READY>
