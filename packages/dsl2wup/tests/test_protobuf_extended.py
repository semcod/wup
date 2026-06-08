"""Protobuf round-trip for extended verbs."""

from __future__ import annotations

from dsl2wup.codec import decode_protobuf, encode_protobuf, roundtrip_text


def test_status_roundtrip() -> None:
    line = "STATUS PROJECT . DEPS deps.json DELTA 30"
    assert decode_protobuf(encode_protobuf(line)) == roundtrip_text(line)


def test_init_cli_roundtrip() -> None:
    line = "INIT_CLI . OUT wup.yaml SCENARIOS testql-scenarios MERGE"
    assert decode_protobuf(encode_protobuf(line)) == roundtrip_text(line)


def test_endpoints_roundtrip() -> None:
    line = "ENDPOINTS scenarios/tests OUT out.json TESTQL_BIN testql"
    assert decode_protobuf(encode_protobuf(line)) == line
