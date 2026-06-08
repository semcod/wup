"""wup:// URI addressing for WUP configuration and state."""

from uri2wup.decode import decode_uri
from uri2wup.patch import patch_uri
from uri2wup.query import query_uri

__all__ = ["decode_uri", "query_uri", "patch_uri"]
