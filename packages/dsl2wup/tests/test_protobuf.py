"""Protobuf encode/decode round-trip."""

from __future__ import annotations

from dsl2wup.codec import decode_protobuf, encode_protobuf, roundtrip_text


def test_encode_decode_roundtrip() -> None:
    line = "HEALTH"
    pb = encode_protobuf(line)
    decoded = decode_protobuf(pb)
    assert "HEALTH" in decoded


def test_text_roundtrip() -> None:
    line = 'QUERY wup://block/config FILE wup.yaml FORMAT json'
    assert "QUERY" in roundtrip_text(line)
