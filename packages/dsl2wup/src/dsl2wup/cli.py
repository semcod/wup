"""CLI for WUP control DSL — dual-mode legacy + subcommands."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dsl2wup.bus import execute_dsl, execute_dsl_line
from dsl2wup.codec import decode_protobuf, encode_protobuf, roundtrip_text
from dsl2wup.events import default_event_store
from dsl2wup.schema_registry import validate_schema_registry

_SUBCOMMANDS = frozenset({"validate-schema", "encode", "decode", "replay"})


def _main_legacy(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="dsl2wup",
        description="Control WUP via DSL commands (QUERY, VALIDATE, MAP, PATCH, ...)",
    )
    parser.add_argument("script", nargs="?", help="Optional .dsl script file")
    parser.add_argument("-c", "--command", help="Execute single DSL command")
    parser.add_argument("--file", help="Default wup.yaml / app.doql.less path")
    parser.add_argument("--json", action="store_true", help="Print JSON results")
    args = parser.parse_args(argv)

    if args.command:
        results = [execute_dsl_line(args.command, default_file=args.file)]
    elif args.script:
        text = Path(args.script).read_text(encoding="utf-8")
        results = execute_dsl(text, default_file=args.file)
    else:
        text = sys.stdin.read()
        if not text.strip():
            parser.print_help()
            return 1
        results = execute_dsl(text, default_file=args.file)

    exit_code = 0
    for result in results:
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            if result.error:
                print(f"error: {result.error}", file=sys.stderr)
            if result.output:
                print(result.output.rstrip())
        if not result.ok:
            exit_code = 1
    return exit_code


def _main_subcommand(argv: list[str]) -> int:
    cmd = argv[0]
    rest = argv[1:]

    if cmd == "validate-schema":
        errors = validate_schema_registry()
        if errors:
            for err in errors:
                print(f"error: {err}", file=sys.stderr)
            return 1
        print("schema registry OK")
        return 0

    if cmd == "encode":
        parser = argparse.ArgumentParser(prog="dsl2wup encode")
        parser.add_argument("command", help="DSL command line")
        parser.add_argument("--format", choices=["protobuf", "text"], default="protobuf")
        parser.add_argument("--file", default="")
        args = parser.parse_args(rest)
        if args.format == "protobuf":
            sys.stdout.buffer.write(encode_protobuf(args.command, default_file=args.file))
            return 0
        print(roundtrip_text(args.command))
        return 0

    if cmd == "decode":
        parser = argparse.ArgumentParser(prog="dsl2wup decode")
        parser.add_argument("--input", required=True)
        parser.add_argument("--format", choices=["protobuf"], default="protobuf")
        args = parser.parse_args(rest)
        data = Path(args.input).read_bytes()
        print(decode_protobuf(data))
        return 0

    if cmd == "replay":
        parser = argparse.ArgumentParser(prog="dsl2wup replay")
        parser.add_argument("--file", default="app.doql.less")
        args = parser.parse_args(rest)
        for event in default_event_store(args.file).replay():
            print(json.dumps(event.to_dict(), ensure_ascii=False))
        return 0

    return 1


def main(argv: list[str] | None = None) -> int:
    args = argv or sys.argv[1:]
    if args and args[0] in _SUBCOMMANDS:
        return _main_subcommand(args)
    return _main_legacy(args)


if __name__ == "__main__":
    raise SystemExit(main())
