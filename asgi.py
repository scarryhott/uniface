"""Vercel ASGI entry: the same natural-interface app as `closure-supernet serve`."""

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

from closure_supernet.api_inversion import app  # noqa: E402
from closure_supernet.api_completion import attach_completion_routes  # noqa: E402
from closure_supernet.api_handed import attach_handed_life_routes  # noqa: E402
from closure_supernet.api_turing_being import attach_turing_being_routes  # noqa: E402
from closure_supernet.api_continuation import attach_continuation_routes  # noqa: E402
from closure_supernet.api_proof_completion import (  # noqa: E402
    attach_proof_completion_routes,
)
from closure_supernet.api_natural_interface import (  # noqa: E402
    attach_natural_interface_routes,
)

app = attach_natural_interface_routes(
    attach_proof_completion_routes(
        attach_continuation_routes(
            attach_turing_being_routes(
                attach_handed_life_routes(attach_completion_routes(app))
            )
        )
    )
)

__all__ = ["app"]
