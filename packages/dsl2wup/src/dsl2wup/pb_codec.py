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


def _set_body(envelope: command_pb2.DslEnvelope, cmd: dict[str, Any]) -> None:
    verb = str(cmd.get("verb", "")).upper()
    field = _BODY_MAP.get(verb)
    if not field:
        return
    msg = getattr(envelope, field)
    if verb == "QUERY":
        msg.target = str(cmd.get("target", ""))
        msg.file = str(cmd.get("file", ""))
        msg.format = str(cmd.get("format", "json"))
        msg.project = str(cmd.get("project", ""))
    elif verb == "VALIDATE":
        msg.path = str(cmd.get("path", ""))
        msg.project = str(cmd.get("project", ""))
    elif verb == "RESOLVE":
        msg.text = str(cmd.get("text", ""))
        msg.file = str(cmd.get("file", ""))
        msg.project = str(cmd.get("project", ""))
    elif verb == "HEALTH":
        msg.service = str(cmd.get("service", ""))
        msg.project = str(cmd.get("project", ""))
    elif verb == "STATUS":
        msg.project = str(cmd.get("project", "."))
        msg.deps_file = str(cmd.get("deps_file", "deps.json"))
        msg.file = str(cmd.get("file", ""))
        msg.delta_seconds = int(cmd.get("delta_seconds") or 0)
        msg.failed_only = bool(cmd.get("failed_only"))
    elif verb in {"PATCH", "UPDATE", "REPLACE"}:
        msg.target = str(cmd.get("target", ""))
        msg.with_path = str(cmd.get("with_path", ""))
        msg.file = str(cmd.get("file", ""))
        msg.project = str(cmd.get("project", ""))
    elif verb == "MAP":
        msg.project = str(cmd.get("project", "."))
        msg.out = str(cmd.get("out", "deps.json"))
        msg.framework = str(cmd.get("framework", "auto"))
    elif verb == "INIT":
        msg.project = str(cmd.get("project", "."))
        msg.out = str(cmd.get("out", "wup.yaml"))
    elif verb == "GENERATE":
        msg.text = str(cmd.get("text", ""))
        msg.out = str(cmd.get("out", ""))
        msg.project = str(cmd.get("project", ""))
        msg.template = str(cmd.get("template", ""))
    elif verb == "SYNC":
        msg.project = str(cmd.get("project", "."))
        msg.file = str(cmd.get("file", ""))
        msg.merge_endpoints = bool(cmd.get("merge_endpoints"))
    elif verb == "ADOPT":
        msg.root = str(cmd.get("root", "."))
        msg.out = str(cmd.get("out", ""))
    elif verb == "ENDPOINTS":
        msg.scenarios_dir = str(cmd.get("scenarios_dir", ""))
        msg.out = str(cmd.get("out", "testql-deps.json"))
        msg.testql_bin = str(cmd.get("testql_bin", "testql"))
    elif verb == "INIT_CLI":
        msg.project = str(cmd.get("project", "."))
        msg.out = str(cmd.get("out", "wup.yaml"))
        msg.scenarios = str(cmd.get("scenarios", "testql-scenarios"))
        msg.merge = bool(cmd.get("merge"))
        msg.infer_args = cmd.get("infer_args", True) is not False


def envelope_to_dict(envelope: command_pb2.DslEnvelope) -> dict[str, Any]:
    verb = envelope.verb.upper()
    cmd: dict[str, Any] = {"verb": verb}
    field = _BODY_MAP.get(verb)
    if not field or envelope.WhichOneof("body") != field:
        return cmd
    msg = getattr(envelope, field)
    if verb == "QUERY":
        if msg.target:
            cmd["target"] = msg.target
        if msg.file:
            cmd["file"] = msg.file
        if msg.format:
            cmd["format"] = msg.format
        if msg.project:
            cmd["project"] = msg.project
    elif verb == "VALIDATE":
        if msg.path:
            cmd["path"] = msg.path
        if msg.project:
            cmd["project"] = msg.project
    elif verb == "RESOLVE":
        if msg.text:
            cmd["text"] = msg.text
        if msg.file:
            cmd["file"] = msg.file
        if msg.project:
            cmd["project"] = msg.project
    elif verb == "HEALTH":
        if msg.service:
            cmd["service"] = msg.service
        if msg.project:
            cmd["project"] = msg.project
    elif verb == "STATUS":
        cmd["project"] = msg.project or "."
        if msg.deps_file:
            cmd["deps_file"] = msg.deps_file
        if msg.file:
            cmd["file"] = msg.file
        if msg.delta_seconds:
            cmd["delta_seconds"] = int(msg.delta_seconds)
        if msg.failed_only:
            cmd["failed_only"] = True
    elif verb in {"PATCH", "UPDATE", "REPLACE"}:
        if msg.target:
            cmd["target"] = msg.target
        if msg.with_path:
            cmd["with_path"] = msg.with_path
        if msg.file:
            cmd["file"] = msg.file
        if msg.project:
            cmd["project"] = msg.project
    elif verb == "MAP":
        cmd["project"] = msg.project or "."
        if msg.out:
            cmd["out"] = msg.out
        if msg.framework:
            cmd["framework"] = msg.framework
    elif verb == "INIT":
        cmd["project"] = msg.project or "."
        if msg.out:
            cmd["out"] = msg.out
    elif verb == "GENERATE":
        if msg.text:
            cmd["text"] = msg.text
        if msg.out:
            cmd["out"] = msg.out
        if msg.project:
            cmd["project"] = msg.project
        if msg.template:
            cmd["template"] = msg.template
    elif verb == "SYNC":
        cmd["project"] = msg.project or "."
        if msg.file:
            cmd["file"] = msg.file
        if msg.merge_endpoints:
            cmd["merge_endpoints"] = True
    elif verb == "ADOPT":
        cmd["root"] = msg.root or "."
        if msg.out:
            cmd["out"] = msg.out
    elif verb == "ENDPOINTS":
        if msg.scenarios_dir:
            cmd["scenarios_dir"] = msg.scenarios_dir
        if msg.out:
            cmd["out"] = msg.out
        if msg.testql_bin:
            cmd["testql_bin"] = msg.testql_bin
    elif verb == "INIT_CLI":
        cmd["project"] = msg.project or "."
        if msg.out:
            cmd["out"] = msg.out
        if msg.scenarios:
            cmd["scenarios"] = msg.scenarios
        if msg.merge:
            cmd["merge"] = True
        if not msg.infer_args:
            cmd["infer_args"] = False
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
