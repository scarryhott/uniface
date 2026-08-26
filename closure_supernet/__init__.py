"""Closure Supernet complete continuous living interface.

Every offered or returned relative form enters one append-only integrator. The
primary public surface is a zoomable topology over that field: point/line/loop,
truth diagonal, metavector, ball/hair, reciprocal poles, light cone, ellipse,
shared architecture, selector and anatomy-tree readings are lenses rather than
parallel runtimes. Natural-form determination requires a rigidity receipt and
never emits TRUE merely because the relation became rigid.
"""

from . import living_store_runtime as _living_store_runtime
from . import reopening_store_runtime as _reopening_store_runtime
from .config import RuntimeConfig
from .runtime import ClosureSupernetRuntime
from . import resource_runtime as _resource_runtime
from . import equality_runtime as _equality_runtime
from . import hardware_runtime as _hardware_runtime
from . import supernet_runtime as _supernet_runtime
from . import topology_runtime as _topology_runtime

__all__ = ["RuntimeConfig", "ClosureSupernetRuntime"]
__version__ = "2.0.0"
