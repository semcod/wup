"""NL-driven wup.yaml generation via wup core."""

from __future__ import annotations

import re
from typing import Any

from wup.generate import generate_wup_config


def _extract_template(prompt: str) -> str | None:
    text = prompt.lower()
    for fw in ("fastapi", "flask", "django", "express"):
        if fw in text:
            return fw
    return None


def generate_from_nl(
    prompt: str,
    *,
    project: str = ".",
    out: str = "wup.yaml",
) -> dict[str, Any]:
    return generate_wup_config(project, hint=prompt, template=_extract_template(prompt), out=out)
