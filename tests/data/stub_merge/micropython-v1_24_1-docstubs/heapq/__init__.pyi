"""
Heap queue algorithm.

MicroPython module: https://docs.micropython.org/en/v1.24.0/library/heapq.html

CPython module: :mod:`python:heapq` https://docs.python.org/3/library/heapq.html .

This module implements the
`min heap queue algorithm <https://en.wikipedia.org/wiki/Heap_%28data_structure%29>`_.

A heap queue is essentially a list that has its elements stored in such a way
that the first item of the list is always the smallest.
"""

# source version: v1.24.1
# origin module:: repos/micropython/docs/library/heapq.rst
from __future__ import annotations

from typing import Any

from typing_extensions import TypeVar

_T = TypeVar("_T")

def heappush(heap: list[_T], item: _T, /) -> None:
    """
    Push the ``item`` onto the ``heap``.
    """
    ...

def heappop(heap: list[_T], /) -> _T:
    """
    Pop the first item from the ``heap``, and return it.  Raise ``IndexError`` if
    ``heap`` is empty.

    The returned item will be the smallest item in the ``heap``.
    """
    ...

def heapify(x: list[Any], /) -> None:
    """
    Convert the list ``x`` into a heap.  This is an in-place operation.
    """
    ...
