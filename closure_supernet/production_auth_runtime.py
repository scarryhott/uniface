from __future__ import annotations

import os
from typing import Any

from .production import Authenticator, Principal


_PATCHED = False


def install_owner_auth_bootstrap() -> None:
    """Allow one Railway-managed owner key without duplicating it in JSON.

    `CLOSURE_AUTH_API_KEYS_JSON` remains the general multi-principal registry.
    `CLOSURE_OWNER_API_KEY` is a focused production bootstrap: when present it
    contributes exactly one operator principal. The key value is never returned
    by runtime status or public API responses.
    """

    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    original_init = Authenticator.__init__

    def init(self: Authenticator, config: Any) -> None:
        original_init(self, config)
        owner_api_key = os.getenv("CLOSURE_OWNER_API_KEY", "").strip()
        if owner_api_key:
            self.api_keys.setdefault(
                owner_api_key,
                Principal(
                    subject="harry",
                    role="operator",
                    participant_id="harry",
                    scopes=("supernet:operator",),
                    source="owner_api_key",
                    authenticated=True,
                ),
            )

    Authenticator.__init__ = init  # type: ignore[method-assign]


install_owner_auth_bootstrap()
