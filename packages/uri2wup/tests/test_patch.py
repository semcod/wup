"""Tests for nested wup:// config patches."""

from __future__ import annotations

from pathlib import Path

import yaml
from uri2wup.patch import patch_uri


def test_patch_nested_value_preserves_sibling_keys(tmp_path: Path) -> None:
    config = tmp_path / "wup.yaml"
    config.write_text(
        "project:\n  name: demo\nwatch:\n  paths:\n  - old/**\n  file_types:\n  - .py\n",
        encoding="utf-8",
    )

    result = patch_uri(
        "wup://block/watch/paths",
        content="- src/**\n- lib/**\n",
        file=str(config),
        project=str(tmp_path),
    )

    assert result.ok, result.error
    raw = yaml.safe_load(config.read_text(encoding="utf-8"))
    assert raw["watch"]["paths"] == ["src/**", "lib/**"]
    assert raw["watch"]["file_types"] == [".py"]
