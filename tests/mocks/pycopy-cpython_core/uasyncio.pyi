from typing import Any, Dict, Optional, Sequence, Tuple, Union

Node = Any

class Task(OrgTask):
    def _step(self, value: Any, exc: Any) -> None: ...

class StreamWriter(OrgStreamWriter):
    def awrite(self, data: Any) -> None: ...
    def aclose(self) -> None: ...
