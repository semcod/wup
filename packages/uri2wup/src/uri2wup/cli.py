"""CLI for uri2wup."""

from __future__ import annotations

import argparse
import json
import sys

from uri2wup.decode import decode_uri
from uri2wup.nlp2uri import nlp2uri
from uri2wup.query import query_uri


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uri2wup", description="wup:// URI tools")
    sub = parser.add_subparsers(dest="cmd")

    resolve = sub.add_parser("resolve", help="NL → wup:// URI hits")
    resolve.add_argument("prompt")
    resolve.add_argument("--file", default="")
    resolve.add_argument("--project", default=".")

    decode = sub.add_parser("decode", help="wup:// URI → DSL line")
    decode.add_argument("--uri", required=True)

    run = sub.add_parser("run", help="decode URI → dispatch")
    run.add_argument("--uri", required=True)
    run.add_argument("--file", default="")

    query = sub.add_parser("query", help="Query wup://block URI (read-only)")
    query.add_argument("uri")
    query.add_argument("--file", default="")
    query.add_argument("--format", default="json")
    query.add_argument("--project", default=".")

    args = parser.parse_args(argv or sys.argv[1:])
    if args.cmd == "resolve":
        hits = nlp2uri(args.prompt, file=args.file or None, project=args.project)
        print(json.dumps([h.to_dict() for h in hits], ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "decode":
        print(decode_uri(args.uri))
        return 0
    if args.cmd == "query":
        result = query_uri(args.uri, file=args.file or None, fmt=args.format, project=args.project)
        print(result.rendered or json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1
    if args.cmd == "run":
        from dsl2wup import dispatch

        line = decode_uri(args.uri)
        result = dispatch(line, default_file=args.file or None)
        print(result.output or json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        if result.error:
            print(f"error: {result.error}", file=sys.stderr)
        return 0 if result.ok else 1
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
