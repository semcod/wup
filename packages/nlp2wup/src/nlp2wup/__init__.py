"""Natural language control for WUP."""

from nlp2wup.apply import apply_nl, to_dsl
from nlp2wup.generate import generate_from_nl
from nlp2wup.validate import validate_wup_config

__all__ = ["apply_nl", "to_dsl", "validate_wup_config", "generate_from_nl"]
