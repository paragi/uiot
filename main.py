import network
import gc
try:
    import uasyncio as asyncio
except Exception as e:
    import asyncio
from common import *

# import service_blink
import service_count
import service_webserver

debug(level=DEBUG)
get_config()


def connect():

    if config['access point']['enable'] == 'on':
        debug("Setting up access point", DEBUG)
        ap = network.WLAN(network.AP_IF)
        ap.connect(config['wifi']['ssid'].value, config['wifi']['key'].value)
        ap.config(reconnects = 5)
        ap.active(False)
        ap.active(True)
        while not ap.isconnected():
            pass
        debug("Access point running")
        debug("SSID: {} key: '{}'".format(config['wifi']['ssid'].value, config['wifi']['key'].value))
        nc = ap.ifconfig()
        debug(f'Network interface settings: {nc[0]}</br>{nc[1]}</br>{nc[2]}</br>{nc[3]}')

    elif config['wifi']['enable'] == 'on':
        debug("Connecting to WiFI", DEBUG)

        station = network.WLAN(network.STA_IF)

        if station.isconnected() == True:
            print("Already connected")
            print(station.ifconfig())
            return

        station.active(True)
        station.connect(config['wifi']['ssid'].value, config['wifi']['key'].value)

        while not station.isconnected():
            pass

        print("Connection successful")
        print(station.ifconfig())
    debug("Not using network", DEBUG)


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
