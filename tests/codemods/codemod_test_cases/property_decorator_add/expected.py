# fmt: off
"""
Add a decorator to a property method.
"""

class Style:
    """A dict-like interface to an element's `style` attribute."""

    def __init__(self, element: Element) -> None: ...

    @property
    def visible(self) -> bool: ...
    @visible.setter
    def visible(self, value:bool) -> None: ...