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


def _intent(prompt: str) -> str:
    text = prompt.lower()
    if any(w in text for w in ("validate", "waliduj", "sprawdź", "sprawdz")):
        return "validate"
    if any(w in text for w in ("generate", "wygeneruj", "init", "stwórz", "stworz", "create")):
        return "generate"
    if any(w in text for w in ("patch", "update", "zmień", "zmien", "edytuj", "edit")):
        return "patch"
    if any(w in text for w in ("map", "deps", "dependency", "map-deps")):
        return "map"
    if any(w in text for w in ("sync", "monitoring", "manifest")):
        return "sync"
    if any(w in text for w in ("init-cli", "init cli", "cli setup", "cli scan")):
        return "init_cli"
    if any(w in text for w in ("endpoints", "testql-endpoints", "scenarios")):
        return "endpoints"
    if any(w in text for w in ("status", "stan", "podsumowanie")):
        return "status"
    if any(w in text for w in ("health", "zdrowie")):
        return "health"
    if any(w in text for w in ("query", "pokaż", "pokaz", "read", "show", "get", "config")):
        return "query"
    return "query"


def to_dsl(prompt: str, *, file: str | None = None, project: str = ".") -> str:
    """Convert NL to DSL line without side effects."""
    from dsl2wup.grammar import to_text

    intent = _intent(prompt)
    path_match = re.search(r"([\w./-]+\.(?:ya?ml|json))", prompt, re.IGNORECASE)
    explicit_file = path_match.group(1) if path_match else file

    if intent == "validate":
        return to_text({"verb": "VALIDATE", "path": explicit_file or "wup.yaml", "project": project})
    if intent == "generate":
        from nlp2wup.generate import _extract_template

        cmd = {"verb": "GENERATE", "text": prompt, "out": explicit_file or "wup.yaml", "project": project}
        if tpl := _extract_template(prompt):
            cmd["template"] = tpl
        return to_text(cmd)
    if intent == "map":
        return to_text({"verb": "MAP", "project": project, "out": "deps.json"})
    if intent == "sync":
        cmd = {"verb": "SYNC", "project": project, "file": explicit_file or file or ""}
        if any(w in prompt.lower() for w in ("merge", "endpoints", "połącz", "polacz")):
            cmd["merge_endpoints"] = True
        return to_text(cmd)
    if intent == "init_cli":
        cmd = {"verb": "INIT_CLI", "project": project, "out": explicit_file or "wup.yaml"}
        if "merge" in prompt.lower():
            cmd["merge"] = True
        return to_text(cmd)
    if intent == "endpoints":
        scen = "scenarios/tests"
        if m := re.search(r"([\w./-]+scenarios[\w./-]*)", prompt, re.IGNORECASE):
            scen = m.group(1)
        return to_text({"verb": "ENDPOINTS", "scenarios_dir": scen, "out": explicit_file or "testql-deps.json"})
    if intent == "status":
        return to_text({"verb": "STATUS", "project": project})
    if intent == "health":
        return to_text({"verb": "HEALTH", "project": project})
    hit = best_uri(prompt, file=explicit_file, project=project)
    if hit:
        return to_text({"verb": "QUERY", "target": hit.uri, "file": explicit_file or "", "project": project})
    return to_text({"verb": "RESOLVE", "text": prompt, "file": explicit_file or "", "project": project})


def apply_nl(
    prompt: str,
    *,
    file: str | None = None,
    project: str = ".",
    content: str | None = None,
) -> ApplyResult:
    from dsl2wup import dispatch

    line = to_dsl(prompt, file=file, project=project)
    if _intent(prompt) == "patch" and content:
        hit = best_uri(prompt, file=file, project=project)
        if hit:
            line = f'PATCH {hit.uri} WITH patch.fragment.yaml FILE {file or "wup.yaml"} PROJECT {project}'
    result = dispatch(line, default_file=file)
    return ApplyResult(
        ok=result.ok,
        prompt=prompt,
        action=result.action,
        output=result.output,
        data=result.to_dict(),
        error=result.error,
    )
