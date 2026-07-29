"""Dict ↔ protobuf DslEnvelope / DslResult."""

from __future__ import annotations

import json
from typing import Any

from dsl2wup.grammar import parse_line, to_text
from dsl2wup.result import DslResult
from dsl2wup.v1 import command_pb2, result_pb2

_BODY_MAP = {
    "QUERY": "query",
    "VALIDATE": "validate",
    "RESOLVE": "resolve",
    "HEALTH": "health",
    "STATUS": "status",
    "PATCH": "patch",
    "UPDATE": "patch",
    "REPLACE": "patch",
    "MAP": "map",
    "INIT": "init",
    "GENERATE": "generate",
    "SYNC": "sync",
    "ADOPT": "adopt",
    "ENDPOINTS": "endpoints",
    "INIT_CLI": "init_cli",
}


_BODY_DEFAULTS = {
    "QUERY": {"format": "json"}, "STATUS": {"project": ".", "deps_file": "deps.json"},
    "MAP": {"project": ".", "out": "deps.json", "framework": "auto"},
    "INIT": {"project": ".", "out": "wup.yaml"}, "SYNC": {"project": "."},
    "ADOPT": {"root": "."}, "ENDPOINTS": {"out": "testql-deps.json", "testql_bin": "testql"},
    "INIT_CLI": {"project": ".", "out": "wup.yaml", "scenarios": "testql-scenarios"},
}
_BODY_FIELDS = {
    "QUERY": ("target", "file", "format", "project"), "VALIDATE": ("path", "project"),
    "RESOLVE": ("text", "file", "project"), "HEALTH": ("service", "project"),
    "STATUS": ("project", "deps_file", "file", "delta_seconds", "failed_only"),
    "PATCH": ("target", "with_path", "file", "project"), "MAP": ("project", "out", "framework"),
    "INIT": ("project", "out"), "GENERATE": ("text", "out", "project", "template"),
    "SYNC": ("project", "file", "merge_endpoints"), "ADOPT": ("root", "out"),
    "ENDPOINTS": ("scenarios_dir", "out", "testql_bin"),
    "INIT_CLI": ("project", "out", "scenarios", "merge", "infer_args"),
}
_BOOL_FIELDS = {"failed_only", "merge_endpoints", "merge"}
_INT_FIELDS = {"delta_seconds"}


def _canonical_verb(verb: str) -> str:
    return "PATCH" if verb in {"UPDATE", "REPLACE"} else verb


def _set_body(envelope: command_pb2.DslEnvelope, cmd: dict[str, Any]) -> None:
    verb = _canonical_verb(str(cmd.get("verb", "")).upper())
    field = _BODY_MAP.get(verb)
    if not field:
        return
    msg = getattr(envelope, field)
    defaults = _BODY_DEFAULTS.get(verb, {})
    for name in _BODY_FIELDS[verb]:
        value = cmd.get(name, defaults.get(name, ""))
        if name == "infer_args":
            value = value is not False
        elif name in _BOOL_FIELDS:
            value = bool(value)
        elif name in _INT_FIELDS:
            value = int(value or 0)
        else:
            value = str(value)
        setattr(msg, name, value)


def _body_to_dict(verb: str, msg: Any) -> dict[str, Any]:
    cmd: dict[str, Any] = {}
    defaults = _BODY_DEFAULTS.get(verb, {})
    for name in _BODY_FIELDS[verb]:
        value = getattr(msg, name)
        if name == "infer_args":
            if not value:
                cmd[name] = False
        elif name in _BOOL_FIELDS:
            if value:
                cmd[name] = True
        elif name in _INT_FIELDS:
            if value:
                cmd[name] = int(value)
        elif value:
            cmd[name] = value
        elif name in defaults:
            cmd[name] = defaults[name]
    return cmd


def envelope_to_dict(envelope: command_pb2.DslEnvelope) -> dict[str, Any]:
    verb = envelope.verb.upper()
    cmd: dict[str, Any] = {"verb": verb}
    field = _BODY_MAP.get(verb)
    if not field or envelope.WhichOneof("body") != field:
        return cmd
    cmd.update(_body_to_dict(_canonical_verb(verb), getattr(envelope, field)))
    return cmd


def encode_protobuf(cmd: dict[str, Any], *, default_file: str = "", correlation_id: str = "") -> bytes:
    envelope = command_pb2.DslEnvelope()
    envelope.verb = str(cmd.get("verb", "")).upper()
    _set_body(envelope, cmd)
    envelope.default_file = default_file
    envelope.correlation_id = correlation_id
    return envelope.SerializeToString()


def decode_protobuf(data: bytes) -> dict[str, Any]:
    envelope = command_pb2.DslEnvelope()
    envelope.ParseFromString(data)
    return envelope_to_dict(envelope)


def encode_text_to_protobuf(line: str, *, default_file: str = "", correlation_id: str = "") -> bytes:
    cmd = parse_line(line)
    if cmd is None:
        raise ValueError("empty command")
    return encode_protobuf(cmd, default_file=default_file, correlation_id=correlation_id)


def decode_protobuf_to_text(data: bytes) -> str:
    return to_text(decode_protobuf(data))


def result_to_pb(result: DslResult) -> result_pb2.DslResult:
    pb = result_pb2.DslResult()
    pb.ok = result.ok
    pb.verb = (result.action or "").upper()
    pb.output = result.output
    pb.data_json = json.dumps(result.data, ensure_ascii=False).encode("utf-8")
    pb.error = result.error or ""
    pb.event_id = result.event_id or ""
    pb.command = result.command
    pb.action = result.action
    return pb


def encode_result_protobuf(result: DslResult) -> bytes:
    return result_to_pb(result).SerializeToString()
