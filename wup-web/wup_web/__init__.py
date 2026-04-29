"""WUP Web Dashboard — FastAPI backend for WUP regression watcher."""

__version__ = "0.2.16"

from .main import create_app, app

__all__ = ["create_app", "app", "__version__"]
