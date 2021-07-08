# .. module:: ucollections
# origin: micropython\docs\library\ucollections.rst
# v1.16
"""
   :synopsis: collection and container types

|see_cpython_module| :mod:`python:collections`.

This module implements advanced collection and container types to
hold/accumulate various objects.
"""

from typing import Any, Optional, Union, Tuple

# .. module:: ucollections
# .. function:: deque(iterable, maxlen[, flags])
def deque(iterable, maxlen, flags: Optional[Any]) -> Any:
    """
    Deques (double-ended queues) are a list-like container that support O(1)
    appends and pops from either side of the deque.  New deques are created
    using the following arguments:

        - *iterable* must be the empty tuple, and the new deque is created empty.

        - *maxlen* must be specified and the deque will be bounded to this
          maximum length.  Once the deque is full, any new items added will
          discard items from the opposite end.

        - The optional *flags* can be 1 to check for overflow when adding items.

    As well as supporting `bool` and `len`, deque objects have the following
    methods:

    .. method:: deque.append(x)

        Add *x* to the right side of the deque.
        Raises IndexError if overflow checking is enabled and there is no more room left.

    .. method:: deque.popleft()

        Remove and return an item from the left side of the deque.
        Raises IndexError if no items are present.
    """
    ...


# .. function:: OrderedDict(...)
def OrderedDict(*args) -> Any:
    """
    ``dict`` type subclass which remembers and preserves the order of keys
    added. When ordered dict is iterated over, keys/items are returned in
    the order they were added::

        from ucollections import OrderedDict

        # To make benefit of ordered keys, OrderedDict should be initialized
        # from sequence of (key, value) pairs.
        d = OrderedDict([("z", 1), ("a", 2)])
        # More items can be added as usual
        d["w"] = 5
        d["b"] = 3
        for k, v in d.items():
            print(k, v)

    Output::

        z 1
        a 2
        w 5
        b 3
    """
    ...
