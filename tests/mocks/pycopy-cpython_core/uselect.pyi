from typing import Any, Dict, Optional, Sequence, Tuple, Union

Node = Any

class poll:
    def __init__(self) -> None: ...
    def register(self, stream: Any, events: Any, userdata: Any) -> None: ...
    def ipoll(self, timeout: Any) -> None: ...
