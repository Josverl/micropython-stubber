# .. module:: uselect
# origin: micropython\docs\library\uselect.rst
# v1.16
"""
   :synopsis: wait for events on a set of streams

|see_cpython_module| :mod:`python:select`.

This module provides functions to efficiently wait for events on multiple
`streams <stream>` (select streams which are ready for operations).
"""

from typing import Any, Optional, Union, Tuple

# .. module:: uselect
# .. function:: poll()
def poll() -> Any:
    """
    Create an instance of the Poll class.
    """
    ...


# .. _class: Poll
# .. method:: poll.register(obj[, eventmask])
class poll:
    """ """

    def register(self, obj, eventmask: Optional[Any]) -> Any:
        """
        Register `stream` *obj* for polling. *eventmask* is logical OR of:

        * ``uselect.POLLIN``  - data available for reading
        * ``uselect.POLLOUT`` - more data can be written

        Note that flags like ``uselect.POLLHUP`` and ``uselect.POLLERR`` are
        *not* valid as input eventmask (these are unsolicited events which
        will be returned from `poll()` regardless of whether they are asked
        for). This semantics is per POSIX.

        *eventmask* defaults to ``uselect.POLLIN | uselect.POLLOUT``.

        It is OK to call this function multiple times for the same *obj*.
        Successive calls will update *obj*'s eventmask to the value of
        *eventmask* (i.e. will behave as `modify()`).
        """
        ...

    # .. method:: poll.modify(obj, eventmask)
    def modify(self, obj, eventmask) -> Any:
        """
        Modify the *eventmask* for *obj*. If *obj* is not registered, `OSError`
        is raised with error of ENOENT.
        """
        ...

    # .. method:: poll.ipoll(timeout=-1, flags=0, /)
    def ipoll(self, timeout=-1, flags=0, /) -> Any:
        """
        Like :meth:`poll.poll`, but instead returns an iterator which yields a
        `callee-owned tuple`. This function provides an efficient, allocation-free
        way to poll on streams.

        If *flags* is 1, one-shot behaviour for events is employed: streams for
        which events happened will have their event masks automatically reset
        (equivalent to ``poll.modify(obj, 0)``), so new events for such a stream
        won't be processed until new mask is set with `poll.modify()`. This
        behaviour is useful for asynchronous I/O schedulers.

        .. admonition:: Difference to CPython
           :class: attention

           This function is a MicroPython extension.
        """
        ...
