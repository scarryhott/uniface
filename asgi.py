"""ASGI entry: the completed Supernet plus its tool-only MCP agent bridge."""

from __future__ import annotations

import os

# Vercel Functions are writable only under /tmp. Dashboard env still wins.
os.environ.setdefault("CLOSURE_DB_PATH", "/tmp/closure_supernet.db")
os.environ.setdefault("CLOSURE_INBOX_DIR", "/tmp/inbox")
os.environ.setdefault("CLOSURE_BACKUP_DIR", "/tmp/backups")
os.environ.setdefault("CLOSURE_AUTONOMY_ENABLED", "false")
os.environ.setdefault("CLOSURE_SERVICE_ROLE", "web")
os.environ.setdefault(
    "CLOSURE_TRUSTED_HOSTS",
    "localhost,127.0.0.1,*.vercel.app",
)

# Keep the historical base import explicit: the agent surface extends the same
# application lineage rather than replacing the pre-existing Supernet app.
from closure_supernet.api_inversion import app as _inversion_app  # noqa: E402,F401
from closure_supernet.api_agent import app  # noqa: E402

__all__ = ["app"]
