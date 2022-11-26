import network
import gc
try:
    import uasyncio as asyncio
except Exception as e:
    import asyncio
from config import *

# import service_blink
import service_count
import service_webserver


get_config()

def connect():
    station = network.WLAN(network.STA_IF)

    if station.isconnected() == True:
        print("Already connected")
        print(station.ifconfig())
        return

    station.active(True)
    station.connect(config['wifi']['ssid'].value, config['wifi']['key'].value)
    station.connect(config['wifi']['ssid'].value, config['wifi']['key'].value)

    while station.isconnected() == False:
        pass

    print("Connection successful")
    print(station.ifconfig())


async def start_services():
    gc.collect()
    tasks = [
        asyncio.create_task(service_count.start()),
        # asyncio.create_task(service_blink.start()),
        asyncio.create_task(service_webserver.start()),
    ]
    await asyncio.gather(*tasks)
    print("All tasks have completed now.")


connect()
asyncio.run(start_services())
