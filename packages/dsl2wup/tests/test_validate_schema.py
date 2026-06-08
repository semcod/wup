"""Phase 5: full validate-schema audit."""

from __future__ import annotations

from dsl2wup.schema_registry import PUBLIC_VERBS, validate_schema_registry


def test_validate_schema_registry_passes() -> None:
    errors = validate_schema_registry()
    assert errors == [], "\n".join(errors)


def test_all_public_verbs_have_schemas() -> None:
    from dsl2wup.schema_registry import _schema_verb_for, schema_for_verb

    missing = [verb for verb in PUBLIC_VERBS if schema_for_verb(_schema_verb_for(verb)) is None]
    assert missing == []
