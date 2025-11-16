"""Quick smoke test for the SolarBASIC Stage 10 feature set."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from solarbasic.interpreter import (
    CommandExecutor,
    CommandParser,
    LineStorage,
    ProgramRunner,
    run_script_file,
)


def main() -> None:
    parser = CommandParser()
    storage = LineStorage()
    executor = CommandExecutor(storage, parser)

    storage.set_line(10, "PRINT 1+2*3")
    storage.set_line(20, "LED 2 2 ON")
    storage.set_line(30, "WHILE 0")
    storage.set_line(40, "PRINT 99")
    storage.set_line(50, "WEND")
    storage.set_line(60, "FUNC ADD(A,B)")
    storage.set_line(70, "RETURN A+B")
    storage.set_line(80, "ENDFUNC")
    storage.set_line(90, "PRINT ADD(3,4)")

    runner = ProgramRunner(parser, executor)
    runner.run(storage.snapshot())

    print("\nDirect-mode checks:")
    executor.execute(parser.parse("PRINT ADD(5,6)"))
    executor.execute(parser.parse("LED 0 0 ON"))

    demo_script = PROJECT_ROOT / "examples" / "demo.bas"
    if demo_script.exists():
        print("\nScript runner check:")
        run_script_file(str(demo_script))


if __name__ == "__main__":
    main()
