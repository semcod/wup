"""CLI for nlp2wup."""

from __future__ import annotations

import argparse
import json
import sys

from nlp2wup.apply import apply_nl, to_dsl


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="nlp2wup", description="Natural language → WUP DSL")
    sub = parser.add_subparsers(dest="cmd")

    to_dsl_cmd = sub.add_parser("to-dsl", help="NL → DSL line (no execution)")
    to_dsl_cmd.add_argument("prompt")
    to_dsl_cmd.add_argument("--file", default="")
    to_dsl_cmd.add_argument("--project", default=".")

    apply_cmd = sub.add_parser("apply", help="NL → DSL → dispatch")
    apply_cmd.add_argument("prompt")
    apply_cmd.add_argument("--file", default="")
    apply_cmd.add_argument("--project", default=".")
    apply_cmd.add_argument("--json", action="store_true")

    args = parser.parse_args(argv or sys.argv[1:])
    if args.cmd == "to-dsl":
        print(to_dsl(args.prompt, file=args.file or None, project=args.project))
        return 0
    if args.cmd == "apply":
        result = apply_nl(args.prompt, file=args.file or None, project=args.project)
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(result.output or json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
