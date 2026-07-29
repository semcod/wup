"""Interactive CLI shell for WUP control DSL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dsl2wup.engine import execute_dsl, execute_dsl_line


def run_shell(*, default_file: str | None = None, json_out: bool = False) -> int:
    print("cli2wup shell — WUP control DSL (exit/quit to leave)")
    exit_code = 0
    while True:
        try:
            line = input("wup> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.lower() in {"exit", "quit", ":q"}:
            break
        result = execute_dsl_line(line, default_file=default_file)
        if json_out:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            if result.error:
                print(f"error: {result.error}", file=sys.stderr)
            if result.output:
                print(result.output.rstrip())
        if not result.ok:
            exit_code = 1
    return exit_code


def _print_result(result: object, *, json_out: bool) -> None:
    if json_out:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return
    if result.error:
        print(f"error: {result.error}", file=sys.stderr)
    if result.output:
        print(result.output.rstrip())


def _run_script(args: argparse.Namespace) -> int:
    results = execute_dsl(Path(args.script).read_text(encoding="utf-8"), default_file=args.file)
    exit_code = 0
    for result in results:
        _print_result(result, json_out=args.json)
        if not result.ok:
            exit_code = 1
    return exit_code


def _run_command(args: argparse.Namespace) -> int:
    result = execute_dsl_line(args.command, default_file=args.file)
    _print_result(result, json_out=args.json)
    return 0 if result.ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cli2wup",
        description="Interactive shell for WUP control DSL (via dsl2wup)",
    )
    sub = parser.add_subparsers(dest="cmd")

    shell = sub.add_parser("shell", help="Interactive REPL")
    shell.add_argument("--file", help="Default wup.yaml path")
    shell.add_argument("--json", action="store_true")

    run = sub.add_parser("run", help="Run a .dsl script file")
    run.add_argument("script", help="DSL script path")
    run.add_argument("--file", help="Default wup.yaml path")
    run.add_argument("--json", action="store_true")

    one = sub.add_parser("exec", help="Execute one DSL command")
    one.add_argument("command", help='DSL command, e.g. QUERY wup://block/config')
    one.add_argument("--file", help="Default wup.yaml path")
    one.add_argument("--json", action="store_true")

    args = parser.parse_args(argv or sys.argv[1:])
    cmd = args.cmd or "shell"
    parsed = argparse.Namespace(**vars(args))
    parsed.cmd = cmd

    handlers = {"shell": lambda: run_shell(default_file=parsed.file, json_out=parsed.json), "run": lambda: _run_script(parsed), "exec": lambda: _run_command(parsed)}
    if handler := handlers.get(parsed.cmd):
        return handler()

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
