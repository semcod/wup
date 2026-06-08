"""CLI for rest2wup."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rest2wup", description="REST API for WUP control DSL")
    sub = parser.add_subparsers(dest="cmd")
    serve = sub.add_parser("serve", help="Start FastAPI server")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8216)
    args = parser.parse_args(argv or sys.argv[1:])
    if args.cmd == "serve" or args.cmd is None:
        import uvicorn

        from rest2wup.app import create_app

        uvicorn.run(create_app(), host=args.host, port=args.port)
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
