# fmt: off
"""
Overloaded methods
"""
from typing import overload

class Parrot:
    def talk(): ...

    @overload
    def speak(number: int):
        """
        Speak a number
        First overload
        """
        ...

    @overload
    def speak(words: str):
        """
        Speak a word
        Second overload
        """
        ...


class Dog:
    def speak(): ...
