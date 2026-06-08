"""WUP control DSL — query, patch, validate and adopt manifests."""

from dsl2wup.bus import dispatch, execute_dsl, execute_dsl_line
from dsl2wup.result import DslResult

__all__ = ["DslResult", "dispatch", "execute_dsl", "execute_dsl_line"]
