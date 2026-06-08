"""CLI for mcp2wup."""

from __future__ import annotations

import argparse
import sys

from mcp2wup.server import run_server


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mcp2wup", description="WUP MCP server (stdio)")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("serve", help="Start MCP server")
    args = parser.parse_args(argv or sys.argv[1:])
    if args.cmd == "serve" or args.cmd is None:
        run_server()
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
