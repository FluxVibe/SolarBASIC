"""SolarBASIC REPL and script-file runner."""
from __future__ import annotations

from .ast_nodes import (
    ExecutionSignal,
    LineStorage,
    RunStatement,
    StoreAction,
    StoreResult,
    split_line_number,
)
from .executor import CommandExecutor, DEFAULT_STEP_LIMIT
from .parser import CommandParser
from .ast_nodes import ParseError
from .tokenizer import TokenizerError
from .version import TAGLINE, VERSION_LABEL as SOLARBASIC_VERSION


class SolarBasicRepl:
    """Provide SolarBASIC REPL behavior for the v1.0.0 release."""

    PROMPT = "READY> "

    def __init__(self, *, debug: bool = False, step_limit: int = DEFAULT_STEP_LIMIT) -> None:
        self._running = True
        self._debug = debug
        self._step_limit = step_limit if step_limit > 0 else DEFAULT_STEP_LIMIT
        self._line_storage = LineStorage()
        self._parser = CommandParser()
        self._executor = CommandExecutor(
            self._line_storage,
            self._parser,
            debug=self._debug,
            step_limit=self._step_limit,
        )

    def start(self) -> None:
        """Show the READY> prompt repeatedly and process early-stage input."""

        self._print_banner()
        while self._running:
            try:
                user_input = input(self.PROMPT)
            except EOFError:
                print()
                self._say_goodbye()
                break
            except KeyboardInterrupt:
                print()
                self._say_goodbye()
                break

            normalized = user_input.strip()
            if not normalized:
                continue

            if self._try_store_program_line(user_input):
                continue
            if self._handle_direct_mode(normalized):
                break

    def _print_banner(self) -> None:
        stage = f"SolarBASIC {SOLARBASIC_VERSION} — {TAGLINE}"
        if self._debug:
            stage += " [debug trace]"
        print(stage)
        print("Type HELP for a quick command summary.")

    def _say_goodbye(self) -> None:
        print("Bye. :)")

    def _try_store_program_line(self, raw_input: str) -> bool:
        """Return True when the input begins with a line number and got stored."""

        parsed = split_line_number(raw_input)
        if not parsed:
            return False

        line_number, content = parsed
        result = self._line_storage.set_line(line_number, content)
        self._report_line_storage(result, content)
        return True

    def _report_line_storage(self, result: StoreResult, content: str) -> None:
        """Give lightweight feedback about how the line buffer changed."""

        if result.action is StoreAction.ADDED:
            print(f"Stored line {result.line_number}: {content or '(blank)'}")
        elif result.action is StoreAction.UPDATED:
            print(f"Updated line {result.line_number}: {content or '(blank)'}")
        elif result.action is StoreAction.DELETED:
            print(f"Deleted line {result.line_number}.")
        else:
            print(f"No change for line {result.line_number} (it was already empty).")

    def _handle_direct_mode(self, normalized_input: str) -> bool:
        """Parse and execute direct-mode commands.

        Returns True when the caller should exit the REPL.
        """

        try:
            statement = self._parser.parse(normalized_input)
        except (ParseError, TokenizerError) as exc:
            print(f"Parse error: {exc}")
            return False

        result = self._executor.execute(statement)
        if result.goto_target is not None:
            print("GOTO is only available when RUN executes stored program lines.")
            return False

        if result.gosub_target is not None:
            print("GOSUB is only available when RUN executes stored program lines.")
            return False

        if result.gosub_return:
            print("RETURN without GOSUB has no effect in direct mode.")
            return False

        if result.signal is ExecutionSignal.EXIT:
            self._say_goodbye()
            return True

        return False


def run_script_file(
    path: str,
    *,
    debug: bool = False,
    step_limit: int = DEFAULT_STEP_LIMIT,
) -> int:
    """Execute a SolarBASIC source file without launching the REPL."""

    parser = CommandParser()
    storage = LineStorage()
    executor = CommandExecutor(
        storage,
        parser,
        debug=debug,
        step_limit=step_limit if step_limit > 0 else DEFAULT_STEP_LIMIT,
    )

    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError as exc:
        print(f"Unable to read script '{path}': {exc}")
        return 1

    used_numbers = set()
    next_auto_line = 10
    for raw_line in lines:
        stripped_line = raw_line.rstrip("\n")
        normalized = stripped_line.strip()
        if not normalized:
            continue

        parsed = split_line_number(stripped_line)
        if parsed:
            line_number, content = parsed
            used_numbers.add(line_number)
            next_auto_line = max(next_auto_line, line_number + 10)
        else:
            line_number = next_auto_line
            while line_number in used_numbers:
                line_number += 10
            next_auto_line = line_number + 10
            content = normalized
            used_numbers.add(line_number)

        storage.set_line(line_number, content)

    executor.execute(RunStatement())
    return 0
