# fmt: off
"""
Overloaded methods
"""
from typing import overload

class Parrot:
    @overload
    @classmethod
    def speak(cls, number: int):
        """
        Speak a number
        First overload
        """
        ...

    @overload
    @classmethod
    def speak(cls, words: str):
        """
        Speak a word
        Second overload
        """
        ...
