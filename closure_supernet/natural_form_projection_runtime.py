from __future__ import annotations

"""Published projection runtime with one equal translational closure surface.

The visible natural form is now the interactive relation object itself. There
is no legacy renderer underneath and no pointer-inert natural-form overlay.
The mutation/equality runtime remains the same source-preserving return and
re-closure mechanism.
"""

from . import minimal_projection_runtime as _base
from .equal_translation_interface import EQUAL_TRANSLATION_SUPERNET_HTML

# The base FastAPI route reads this module global at request time. Rebinding the
# surface changes only the browser projection. The canonical stores, returned
# interaction mutation, proof-indexed closure validation, and verified-source
# boundary remain the existing runtime.
_base.CLOSURE_ONLY_SUPERNET_HTML = EQUAL_TRANSLATION_SUPERNET_HTML

TranslationalReturnRequest = _base.TranslationalReturnRequest
MinimalProjectionRuntime = _base.MinimalProjectionRuntime
derive_local_projection_commitment = _base.derive_local_projection_commitment
create_app = _base.create_app

app = create_app()

__all__ = [
    "MinimalProjectionRuntime",
    "TranslationalReturnRequest",
    "app",
    "create_app",
    "derive_local_projection_commitment",
]
