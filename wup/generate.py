"""Generate wup.yaml — domain logic using assistant auto-detection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from wup.assistant import WupAssistant
from wup.config import save_config
from wup.models.config import ServiceConfig


def _detect_template(hint: str, explicit: str | None) -> str:
    if explicit:
        return explicit.lower()
    text = hint.lower()
    for fw in ("fastapi", "flask", "django", "express"):
        if fw in text:
            return fw
    return ""


def generate_wup_config(
    project_root: str | Path,
    *,
    hint: str = "",
    template: str | None = None,
    out: str = "wup.yaml",
) -> dict[str, Any]:
    """Generate wup.yaml with assistant-style auto-detection (non-interactive)."""
    root = Path(project_root).expanduser().resolve()
    if not root.exists():
        return {"ok": False, "error": f"project not found: {root}"}

    assistant = WupAssistant(str(root))
    framework = _detect_template(hint, template) or assistant._detect_framework() or "fastapi"

    assistant.config.project.name = root.name
    assistant.config.project.description = f"{framework.capitalize()} project monitored by WUP"

    services = assistant._auto_detect_services(framework)
    assistant.config.services = services if services else [ServiceConfig(name="main", type="auto")]
    assistant.config.watch.paths = ["app/**", "src/**", "wup/**"]
    assistant.config.watch.file_types = [".py", ".yaml", ".yml"]
    assistant.config.web.enabled = True
    assistant.config.web.endpoint = "http://localhost:8000"

    output_path = Path(out)
    if not output_path.is_absolute():
        output_path = root / output_path

    if output_path.exists() and "overwrite" not in hint.lower():
        return {"ok": False, "error": f"config already exists: {output_path}", "output": str(output_path)}

    save_config(assistant.config, output_path)
    return {
        "ok": True,
        "output": str(output_path),
        "framework": framework,
        "services": len(assistant.config.services),
        "project": str(root),
    }
