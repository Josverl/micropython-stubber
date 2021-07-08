# .. module:: uasyncio
# origin: micropython\docs\library\uasyncio.rst
# v1.16
"""
   :synopsis: asynchronous I/O scheduler for writing concurrent code

|see_cpython_module|
`asyncio <https://docs.python.org/3.8/library/asyncio.html>`_

Example::

    import uasyncio

    async def blink(led, period_ms):
        while True:
            led.on()
            await uasyncio.sleep_ms(5)
            led.off()
            await uasyncio.sleep_ms(period_ms)

    async def main(led1, led2):
        uasyncio.create_task(blink(led1, 700))
        uasyncio.create_task(blink(led2, 400))
        await uasyncio.sleep_ms(10_000)

    # Running on a pyboard
    from pyb import LED
    uasyncio.run(main(LED(1), LED(2)))

    # Running on a generic board
    from machine import Pin
    uasyncio.run(main(Pin(1), Pin(2)))
"""

from typing import Any, Optional, Union, Tuple

# .. module:: uasyncio
# .. function:: create_task(coro)
def create_task(coro) -> Any:
    """
    Create a new task from the given coroutine and schedule it to run.

    Returns the corresponding `Task` object.
    """
    ...


# .. function:: run(coro)
def run(coro) -> Any:
    """
    Create a new task from the given coroutine and run it until it completes.

    Returns the value returned by *coro*.
    """
    ...


# .. function:: sleep_ms(t)
def sleep_ms(t) -> Any:
    """
    Sleep for *t* milliseconds.

    This is a coroutine, and a MicroPython extension.
    """
    ...


# .. function:: wait_for(awaitable, timeout)
def wait_for(awaitable, timeout) -> Any:
    """
    Wait for the *awaitable* to complete, but cancel it if it takes longer
    that *timeout* seconds.  If *awaitable* is not a task then a task will be
    created from it.

    If a timeout occurs, it cancels the task and raises ``asyncio.TimeoutError``:
    this should be trapped by the caller.

    Returns the return value of *awaitable*.

    This is a coroutine.
    """
    ...


# .. function:: gather(*awaitables, return_exceptions=False)
def gather(*awaitables, return_exceptions=False) -> Any:
    """
    Run all *awaitables* concurrently.  Any *awaitables* that are not tasks are
    promoted to tasks.

    Returns a list of return values of all *awaitables*.

    This is a coroutine.
    """
    ...


# .. class:: Task()
# .. class:: Task()

# class:: Task
class Task:
    """
    This object wraps a coroutine into a running task.  Tasks can be waited on
    using ``await task``, which will wait for the task to complete and return
    the return value of the task.

    Tasks should not be created directly, rather use `create_task` to create them.
    """

    def __init__(
        self,
    ) -> None:
        ...

    # .. class:: Event()
    # .. class:: Event()

    # class:: Event
    class Event:
        """
        Create a new event which can be used to synchronise tasks.  Events start
        in the cleared state.
        """

        def __init__(
            self,
        ) -> None:
            ...

        # .. method:: Event.set()
        def set(
            self,
        ) -> Any:
            """
            Set the event.  Any tasks waiting on the event will be scheduled to run.

            Note: This must be called from within a task. It is not safe to call this
            from an IRQ, scheduler callback, or other thread. See `ThreadSafeFlag`.
            """
            ...

        # .. method:: Event.wait()
        def wait(
            self,
        ) -> Any:
            """
            Wait for the event to be set.  If the event is already set then it returns
            immediately.

            This is a coroutine.
            """
            ...

        # .. class:: ThreadSafeFlag()
        # .. class:: ThreadSafeFlag()

        # class:: ThreadSafeFlag
        class ThreadSafeFlag:
            """
            Create a new flag which can be used to synchronise a task with code running
            outside the asyncio loop, such as other threads, IRQs, or scheduler
            callbacks.  Flags start in the cleared state.
            """

            def __init__(
                self,
            ) -> None:
                ...

            # .. method:: ThreadSafeFlag.wait()
            def wait(
                self,
            ) -> Any:
                """
                Wait for the flag to be set.  If the flag is already set then it returns
                immediately.

                A flag may only be waited on by a single task at a time.

                This is a coroutine.
                """
                ...

            # .. class:: Lock()
            # .. class:: Lock()

            # class:: Lock
            class Lock:
                """
                Create a new lock which can be used to coordinate tasks.  Locks start in
                the unlocked state.

                In addition to the methods below, locks can be used in an ``async with`` statement.
                """

                def __init__(
                    self,
                ) -> None:
                    ...

                # .. method:: Lock.acquire()
                def acquire(
                    self,
                ) -> Any:
                    """
                    Wait for the lock to be in the unlocked state and then lock it in an atomic
                    way.  Only one task can acquire the lock at any one time.

                    This is a coroutine.
                    """
                    ...

                # .. function:: open_connection(host, port)
                def open_connection(host, port) -> Any:
                    """
                    Open a TCP connection to the given *host* and *port*.  The *host* address will be
                    resolved using `socket.getaddrinfo`, which is currently a blocking call.

                    Returns a pair of streams: a reader and a writer stream.
                    Will raise a socket-specific ``OSError`` if the host could not be resolved or if
                    the connection could not be made.

                    This is a coroutine.
                    """
                    ...

                # .. class:: Stream()
                # .. class:: Stream()

                # class:: Stream
                class Stream:
                    """
                    This represents a TCP stream connection.  To minimise code this class implements
                    both a reader and a writer, and both ``StreamReader`` and ``StreamWriter`` alias to
                    this class.
                    """

                    def __init__(
                        self,
                    ) -> None:
                        ...

                    # .. method:: Stream.close()
                    def close(
                        self,
                    ) -> Any:
                        """
                        Close the stream.
                        """
                        ...

                    # .. method:: Stream.read(n)
                    def read(self, n) -> Any:
                        """
                        Read up to *n* bytes and return them.

                        This is a coroutine.
                        """
                        ...

                    # .. method:: Stream.readline()
                    def readline(
                        self,
                    ) -> Any:
                        """
                        Read a line and return it.

                        This is a coroutine.
                        """
                        ...

                    # .. method:: Stream.drain()
                    def drain(
                        self,
                    ) -> Any:
                        """
                        Drain (write) all buffered output data out to the stream.

                        This is a coroutine.
                        """
                        ...

                    # .. method:: Server.close()
                    class Server:
                        """ """

                        def close(
                            self,
                        ) -> Any:
                            """
                            Close the server.
                            """
                            ...

                        # .. function:: get_event_loop()
                        def get_event_loop() -> Any:
                            """
                            Return the event loop used to schedule and run tasks.  See `Loop`.
                            """
                            ...

                        # .. class:: Loop()
                        # .. class:: Loop()

                        # class:: Loop
                        class Loop:
                            """
                            This represents the object which schedules and runs tasks.  It cannot be
                            created, use `get_event_loop` instead.
                            """

                            def __init__(
                                self,
                            ) -> None:
                                ...

                            # .. method:: Loop.run_forever()
                            def run_forever(
                                self,
                            ) -> Any:
                                """
                                Run the event loop until `stop()` is called.
                                """
                                ...

                            # .. method:: Loop.stop()
                            def stop(
                                self,
                            ) -> Any:
                                """
                                Stop the event loop.
                                """
                                ...

                            # .. method:: Loop.set_exception_handler(handler)
                            def set_exception_handler(self, handler) -> Any:
                                """
                                Set the exception handler to call when a Task raises an exception that is not
                                caught.  The *handler* should accept two arguments: ``(loop, context)``.
                                """
                                ...

                            # .. method:: Loop.default_exception_handler(context)
                            def default_exception_handler(self, context) -> Any:
                                """
                                The default exception handler that is called.
                                """
                                ...
