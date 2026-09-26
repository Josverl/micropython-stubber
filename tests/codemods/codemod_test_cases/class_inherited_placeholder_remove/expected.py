from _typeshed import Incomplete


class Parent:
    def read(self, nbytes: int, /) -> bytes: ...


class Child(Parent):
    TOKEN: int = 1

    def status(self, verbose: bool = False) -> str: ...
    def __init__(self, pin: int, /) -> None: ...
