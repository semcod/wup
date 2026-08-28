"""Smoke and safety tests for mcp2wup."""

import pytest

from mcp2wup.server import _require_mutation, create_server


def test_create_server() -> None:
    try:
        server = create_server()
        assert server.name == "wup"
    except RuntimeError:
        pass  # mcp optional


def test_mcp_mutations_require_operator_capability(monkeypatch) -> None:
    monkeypatch.delenv("WUP_MCP_ALLOW_MUTATION", raising=False)
    with pytest.raises(PermissionError, match="WUP_MCP_ALLOW_MUTATION"):
        _require_mutation("wup_patch")

    monkeypatch.setenv("WUP_MCP_ALLOW_MUTATION", "yes")
    _require_mutation("wup_patch")
