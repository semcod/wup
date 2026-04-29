"""WUP Browser Dashboard — FastAPI backend for WUP regression watcher."""

__version__ = "0.2.19"

from .main import create_app, app

__all__ = ["create_app", "app", "__version__"]
