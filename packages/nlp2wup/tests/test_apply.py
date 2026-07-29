"""Tests for nlp2wup."""

from __future__ import annotations

import yaml
from nlp2wup.apply import apply_nl, to_dsl


def test_to_dsl_validate() -> None:
    line = to_dsl("validate wup.yaml")
    assert line.startswith("VALIDATE")


def test_to_dsl_map() -> None:
    line = to_dsl("map deps for project")
    assert line.startswith("MAP")


def test_to_dsl_init_cli_is_not_misclassified_as_generate() -> None:
    assert to_dsl("init-cli for this project").startswith("INIT_CLI")


def test_to_dsl_patch_is_not_misclassified_as_query() -> None:
    assert to_dsl("patch watch in wup.yaml").startswith("PATCH")


def test_apply_patch_uses_supplied_content_without_fragment_file(tmp_path) -> None:
    config = tmp_path / "wup.yaml"
    config.write_text(
        "project:\n  name: demo\nwatch:\n  paths:\n  - old/**\n",
        encoding="utf-8",
    )

    result = apply_nl(
        "patch watch in wup.yaml",
        file=str(config),
        project=str(tmp_path),
        content="paths:\n- src/**\n",
    )

    assert result.ok, result.error
    assert yaml.safe_load(config.read_text(encoding="utf-8"))["watch"]["paths"] == [
        "src/**"
    ]
