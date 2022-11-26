try:
    import uasyncio as asyncio
except Exception as e:
    import asyncio


async def start():
    print("Starting count service")
    c = 1
    while True:
        print(c)
        c += 1
        await asyncio.sleep(5)