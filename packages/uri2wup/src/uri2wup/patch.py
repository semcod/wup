"""Patch wup.yaml blocks via wup:// URIs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from uri2wup.uri import parse_wup_uri


@dataclass
class PatchResult:
    ok: bool
    uri: str
    file: str
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"ok": self.ok, "uri": self.uri, "file": self.file, "error": self.error}


def _resolve_config_path(project: str, file_param: str | None) -> Path:
    project_path = Path(project).expanduser().resolve()
    if file_param:
        path = Path(file_param).expanduser()
        return path if path.is_absolute() else project_path / path
    from wup.config import find_config_file

    found = find_config_file(project_path)
    return found or (project_path / "wup.yaml")


def patch_uri(
    uri: str,
    *,
    content: str,
    file: str | None = None,
    project: str = ".",
) -> PatchResult:
    try:
        parsed = parse_wup_uri(uri)
        parts = list(parsed["parts"])  # type: ignore[arg-type]
        project_path = str(parsed.get("project") or project)
        config_path = _resolve_config_path(project_path, file or str(parsed.get("file") or ""))
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        fragment = yaml.safe_load(content) or {}

        if not parts:
            raise ValueError("PATCH target must specify block, e.g. wup://block/services")
        block = parts[0]
        if block == "services" and isinstance(fragment, list):
            raw["services"] = fragment
        elif block == "watch" and isinstance(fragment, dict):
            raw["watch"] = fragment
        elif block == "testql" and isinstance(fragment, dict):
            raw["testql"] = fragment
        elif block == "project" and isinstance(fragment, dict):
            raw["project"] = fragment
        else:
            raw[block] = fragment

        config_path.write_text(yaml.safe_dump(raw, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return PatchResult(ok=True, uri=uri, file=str(config_path))
    except Exception as exc:
        return PatchResult(ok=False, uri=uri, file=file or "", error=str(exc))
