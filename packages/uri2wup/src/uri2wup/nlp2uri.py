"""Map natural language hints to wup:// URIs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from uri2wup.uri import uri_for_block


@dataclass
class UriHit:
    uri: str
    score: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {"uri": self.uri, "score": self.score, "reason": self.reason}


_KEYWORDS = {
    "config": (["config"], 0.9, "config"),
    "services": (["services"], 0.9, "services"),
    "watch": (["watch"], 0.85, "watch paths"),
    "testql": (["testql"], 0.85, "testql settings"),
    "status": (["status"], 0.8, "project status"),
    "health": (["health"], 0.8, "service health"),
    "deps": (["deps"], 0.75, "dependency map"),
    "validate": (["config"], 0.7, "validate config"),
    "map": (["deps"], 0.65, "dependency map"),
}


def nlp2uri(prompt: str, *, file: str | None = None, project: str = ".") -> list[UriHit]:
    text = prompt.lower()
    hits: list[UriHit] = []
    for keyword, (parts, score, reason) in _KEYWORDS.items():
        if keyword in text:
            full = uri_for_block(*parts, file=file, project=project)
            hits.append(UriHit(uri=full, score=score, reason=reason))
    if not hits:
        hits.append(UriHit(uri=uri_for_block("config", file=file, project=project), score=0.5, reason="default config"))
    return sorted(hits, key=lambda h: h.score, reverse=True)


def best_uri(prompt: str, *, file: str | None = None, project: str = ".") -> UriHit | None:
    hits = nlp2uri(prompt, file=file, project=project)
    return hits[0] if hits else None
