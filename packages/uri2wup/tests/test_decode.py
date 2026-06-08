"""Tests for uri2wup decode."""

from __future__ import annotations

from uri2wup.decode import decode_uri
from uri2wup.uri import uri_for_block, uri_for_cmd


def test_decode_cmd_query() -> None:
    uri = uri_for_cmd(
        "QUERY",
        target=uri_for_block("project"),
        file="wup.yaml",
        project=".",
    )
    line = decode_uri(uri)
    assert line.startswith("QUERY")
    assert "wup://block/project" in line
    assert "FILE wup.yaml" in line


def test_decode_block_defaults_to_query() -> None:
    uri = uri_for_block("watch", file="wup.yaml", project="/tmp/proj")
    line = decode_uri(uri)
    assert line.startswith("QUERY")
    assert uri in line
