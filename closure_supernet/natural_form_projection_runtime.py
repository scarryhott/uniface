from __future__ import annotations

"""Published projection runtime with natural-form visual translation.

The mutation/equality runtime is unchanged. Only the HTML projection surface is
replaced with a renderer that derives all retained natural-form family layers
from the already verified atlas/local-freedom contract.
"""

from . import minimal_projection_runtime as _base
from .natural_form_visual_interface import NATURAL_FORM_SUPERNET_HTML

# The base FastAPI route reads this module global at request time. Rebinding the
# imported base module therefore changes presentation only; the return relation,
# closure derivation, stores, validation, versioned runtime contract, and
# source-preserving mutation path are exactly the existing runtime.
_base.CLOSURE_ONLY_SUPERNET_HTML = NATURAL_FORM_SUPERNET_HTML

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
