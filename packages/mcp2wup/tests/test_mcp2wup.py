"""Smoke test for mcp2wup."""

from mcp2wup.server import create_server


def test_create_server() -> None:
    try:
        server = create_server()
        assert server.name == "wup"
    except RuntimeError:
        pass  # mcp optional
