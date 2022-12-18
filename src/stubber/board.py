import importlib.util
from pathlib import Path

__all__ = ["create_stubs"]

_origin = Path(importlib.util.find_spec("stubber").origin)  # type: ignore

create_stubs = _origin.parent.parent / "board" / "createstubs.py"

_editable_root = _origin.parent.parent.parent
_editable_create = _editable_root / "board" / "createstubs.py"
if _editable_create.exists():
    create_stubs = _editable_create
