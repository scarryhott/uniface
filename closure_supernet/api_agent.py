"""Published Supernet entrypoint.

The production app exposes one closure projection and one source-preserving
return relation. The visible surface is now the natural-form translation of the
verified current-closure-relative atlas; rendering remains presentation-only
and cannot author equality or truth.
"""

from .natural_form_projection_runtime import app, create_app


__all__ = ["app", "create_app"]
