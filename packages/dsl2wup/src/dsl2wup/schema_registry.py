"""Verb → JSON Schema registry."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from typing import Any

import jsonschema

QUERY_VERBS = frozenset({"QUERY", "RESOLVE", "VALIDATE", "HEALTH", "STATUS"})
COMMAND_VERBS = frozenset({
    "PATCH", "UPDATE", "REPLACE", "MAP", "INIT", "GENERATE", "SYNC", "ADOPT",
    "INIT_CLI", "ENDPOINTS",
})
PUBLIC_VERBS = QUERY_VERBS | COMMAND_VERBS
# Aliases share the PATCH schema / handler.
SCHEMA_VERB_ALIASES = {"UPDATE": "PATCH", "REPLACE": "PATCH"}


@lru_cache(maxsize=1)
def _load_schemas() -> dict[str, dict[str, Any]]:
    schemas: dict[str, dict[str, Any]] = {}
    pkg = resources.files("dsl2wup").joinpath("schema/commands")
    for path in pkg.iterdir():
        if path.name.endswith(".schema.json"):
            verb = path.name.replace(".schema.json", "").upper()
            schemas[verb] = json.loads(path.read_text(encoding="utf-8"))
    return schemas


def schema_for_verb(verb: str) -> dict[str, Any] | None:
    return _load_schemas().get(verb.upper())


def all_schemas() -> dict[str, dict[str, Any]]:
    return dict(_load_schemas())


def validate_command_dict(cmd: dict[str, Any]) -> list[str]:
    verb = str(cmd.get("verb", "")).upper()
    schema = schema_for_verb(verb)
    if schema is None:
        return []
    validator = jsonschema.Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(cmd), key=str)]


def _schema_verb_for(verb: str) -> str:
    return SCHEMA_VERB_ALIASES.get(verb.upper(), verb.upper())


def validate_schema_registry() -> list[str]:
    """Audit registry: handler verbs, schema files, protobuf codec alignment."""
    errors: list[str] = []
    schemas = _load_schemas()

    for verb, schema in schemas.items():
        props = schema.get("properties", {}).get("verb", {})
        const = props.get("const")
        enum_vals = props.get("enum")
        if const and const != verb:
            errors.append(f"{verb}: verb const mismatch (expected {verb}, got {const})")
        if enum_vals and verb not in {v.upper() for v in enum_vals}:
            errors.append(f"{verb}: verb enum mismatch")

    for verb in sorted(PUBLIC_VERBS):
        schema_key = _schema_verb_for(verb)
        if schema_key not in schemas:
            errors.append(f"{verb}: missing schema {schema_key.lower()}.schema.json")

    schema_verbs = set(schemas)
    handled_schema_verbs = {_schema_verb_for(v) for v in PUBLIC_VERBS}
    for verb in sorted(schema_verbs - handled_schema_verbs):
        errors.append(f"{verb}: schema has no handler in PUBLIC_VERBS")

    from dsl2wup.pb_codec import _BODY_MAP  # noqa: PLC0415

    for verb in sorted(PUBLIC_VERBS):
        if verb not in _BODY_MAP:
            errors.append(f"{verb}: missing protobuf body mapping in pb_codec")

    return errors
