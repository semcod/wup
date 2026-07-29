"""Apply natural-language WUP control via nlp2uri + dsl2wup dispatch."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from uri2wup.nlp2uri import best_uri


@dataclass
class ApplyResult:
    ok: bool
    prompt: str
    action: str = ""
    uri: str = ""
    output: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "prompt": self.prompt,
            "action": self.action,
            "uri": self.uri,
            "output": self.output,
            "data": self.data,
            "error": self.error,
        }


_INTENT_KEYWORDS = (
    ("init_cli", ("init-cli", "init cli", "cli setup", "cli scan")),
    ("validate", ("validate", "waliduj", "sprawdź", "sprawdz")),
    ("patch", ("patch", "update", "zmień", "zmien", "edytuj", "edit")),
    ("map", ("map", "deps", "dependency", "map-deps")),
    ("sync", ("sync", "monitoring", "manifest")),
    ("generate", ("generate", "wygeneruj", "init", "stwórz", "stworz", "create")),
    ("endpoints", ("endpoints", "testql-endpoints", "scenarios")),
    ("status", ("status", "stan", "podsumowanie")),
    ("health", ("health", "zdrowie")),
    ("query", ("query", "pokaż", "pokaz", "read", "show", "get", "config")),
)


def _intent(prompt: str) -> str:
    text = prompt.lower()
    for intent, keywords in _INTENT_KEYWORDS:
        if any(word in text for word in keywords):
            return intent
    return "query"


def _simple_command(intent: str, explicit_file: str | None, project: str) -> dict[str, str] | None:
    commands = {
        "validate": {"verb": "VALIDATE", "path": explicit_file or "wup.yaml", "project": project},
        "map": {"verb": "MAP", "project": project, "out": "deps.json"},
        "status": {"verb": "STATUS", "project": project},
        "health": {"verb": "HEALTH", "project": project},
    }
    return commands.get(intent)


def _generated_command(prompt: str, explicit_file: str | None, project: str) -> dict[str, str]:
    from nlp2wup.generate import _extract_template

    cmd = {"verb": "GENERATE", "text": prompt, "out": explicit_file or "wup.yaml", "project": project}
    if template := _extract_template(prompt):
        cmd["template"] = template
    return cmd


def _special_command(intent: str, prompt: str, explicit_file: str | None, file: str | None, project: str) -> dict[str, Any] | None:
    text = prompt.lower()
    if intent == "generate":
        return _generated_command(prompt, explicit_file, project)
    if intent == "sync":
        return {"verb": "SYNC", "project": project, "file": explicit_file or file or "", "merge_endpoints": any(word in text for word in ("merge", "endpoints", "połącz", "polacz"))}
    if intent == "init_cli":
        return {"verb": "INIT_CLI", "project": project, "out": explicit_file or "wup.yaml", "merge": "merge" in text}
    if intent == "endpoints":
        match = re.search(r"([\w./-]+scenarios[\w./-]*)", prompt, re.IGNORECASE)
        return {"verb": "ENDPOINTS", "scenarios_dir": match.group(1) if match else "scenarios/tests", "out": explicit_file or "testql-deps.json"}
    return None


def to_dsl(prompt: str, *, file: str | None = None, project: str = ".") -> str:
    """Convert NL to DSL line without side effects."""
    from dsl2wup.grammar import to_text

    intent = _intent(prompt)
    path_match = re.search(r"([\w./-]+\.(?:ya?ml|json))", prompt, re.IGNORECASE)
    explicit_file = path_match.group(1) if path_match else file

    if cmd := _simple_command(intent, explicit_file, project):
        return to_text(cmd)
    if cmd := _special_command(intent, prompt, explicit_file, file, project):
        return to_text(cmd)
    hit = best_uri(prompt, file=explicit_file, project=project)
    if intent == "patch":
        target = hit.uri if hit else "wup://block/config"
        return to_text(
            {
                "verb": "PATCH",
                "target": target,
                "file": explicit_file or file or "",
                "project": project,
            }
        )
    if hit:
        return to_text(
            {
                "verb": "QUERY",
                "target": hit.uri,
                "file": explicit_file or "",
                "project": project,
            }
        )
    return to_text(
        {
            "verb": "RESOLVE",
            "text": prompt,
            "file": explicit_file or "",
            "project": project,
        }
    )


def apply_nl(
    prompt: str,
    *,
    file: str | None = None,
    project: str = ".",
    content: str | None = None,
) -> ApplyResult:
    line = to_dsl(prompt, file=file, project=project)
    if _intent(prompt) == "patch" and content is not None:
        from uri2wup.patch import patch_uri

        hit = best_uri(prompt, file=file, project=project)
        target = hit.uri if hit else "wup://block/config"
        patched = patch_uri(target, content=content, file=file, project=project)
        payload = patched.to_dict()
        return ApplyResult(
            ok=patched.ok,
            prompt=prompt,
            action="patch",
            uri=target,
            output=json.dumps(payload, ensure_ascii=False, indent=2),
            data=payload,
            error=patched.error,
        )

    from dsl2wup import dispatch

    result = dispatch(line, default_file=file)
    return ApplyResult(
        ok=result.ok,
        prompt=prompt,
        action=result.action,
        output=result.output,
        data=result.to_dict(),
        error=result.error,
    )
