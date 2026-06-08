"""Smoke test for cli2wup imports."""

from cli2wup.cli import main


def test_cli_help() -> None:
    assert main(["exec", "HEALTH", "--json"]) in (0, 1)
