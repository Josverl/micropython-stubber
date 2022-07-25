"""
A coroutine that calls gen.sleep.
"""
from tornado import gen


@gen.coroutine
def ping():
    yield gen.sleep(10)
    raise gen.Return("pong")
