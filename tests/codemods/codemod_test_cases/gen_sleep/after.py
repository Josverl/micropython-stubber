"""
A coroutine that calls gen.sleep.
"""
from tornado import gen
import asyncio


async def ping():
    await asyncio.sleep(10)
    return "pong"
