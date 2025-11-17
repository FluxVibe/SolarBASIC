"""Entry point for the SolarBASIC tools (REPL or script runner)."""

from __future__ import annotations

import argparse
from typing import Sequence

from solarbasic.interpreter import DEFAULT_STEP_LIMIT, SolarBasicRepl, run_script_file
from solarbasic.version import TAGLINE, VERSION, VERSION_LABEL


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"SolarBASIC {VERSION_LABEL} — {TAGLINE}")
    parser.add_argument("script", nargs="?", help="Path to a .bas file to execute once")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Trace each RUN line before it executes.",
    )
    parser.add_argument(
        "--step-limit",
        type=int,
        default=DEFAULT_STEP_LIMIT,
        help="Maximum RUN steps before aborting (default: 10000).",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the SolarBASIC version and exit.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"SolarBASIC {VERSION_LABEL}")
        raise SystemExit(0)

    if args.script:
        status = run_script_file(args.script, debug=args.debug, step_limit=args.step_limit)
        raise SystemExit(status)

    repl = SolarBasicRepl(debug=args.debug, step_limit=args.step_limit)
    repl.start()


if __name__ == "__main__":
    main()
