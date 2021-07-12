from typing import Any, Optional, Union, Tuple

# .. module:: uheapq
# origin: micropython\docs\library\uheapq.rst
# v1.16
"""
   :synopsis: heap queue algorithm

|see_cpython_module| :mod:`python:heapq`.

This module implements the
`min heap queue algorithm <https://en.wikipedia.org/wiki/Heap_%28data_structure%29>`_.

A heap queue is essentially a list that has its elements stored in such a way
that the first item of the list is always the smallest.
"""
# .. function:: heappush(heap, item)
def heappush(heap, item) -> Any:
    """
    Push the ``item`` onto the ``heap``.
    """
    ...


# .. function:: heappop(heap)
def heappop(heap) -> Any:
    """
    Pop the first item from the ``heap``, and return it.  Raise ``IndexError`` if
    ``heap`` is empty.

    The returned item will be the smallest item in the ``heap``.
    """
    ...


# .. function:: heapify(x)
def heapify(x) -> Any:
    """
    Convert the list ``x`` into a heap.  This is an in-place operation.
    """
    ...
