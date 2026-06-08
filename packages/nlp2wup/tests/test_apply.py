"""Tests for nlp2wup."""

from __future__ import annotations

from nlp2wup.apply import to_dsl


def test_to_dsl_validate() -> None:
    line = to_dsl("validate wup.yaml")
    assert line.startswith("VALIDATE")


def test_to_dsl_map() -> None:
    line = to_dsl("map deps for project")
    assert line.startswith("MAP")
