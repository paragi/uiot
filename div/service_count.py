try:
    import uasyncio as asyncio
except Exception as e:
    import asyncio
from common import *

async def start():
    debug("Starting count service")
    c = 1
    while True:
        debug(c)
        c += 1
        await asyncio.sleep(5)