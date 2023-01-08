# Common elements to the CP-IOT project
# By Simon Rigét 2022
# Released under MIT license
import time
import gc

PC = 1
ESP = 2
try:
  import uasyncio as asyncio
  platform = ESP
except:
  import asyncio
  platform = PC

from common import *


async def blink_start():
  print("Starting blink service")
  try:
    import machine
    led = machine.Pin(2, machine.Pin.OUT)
    while True:
      led.value(not led.value())
      await asyncio.sleep(0.5)
      # print(".", end='')

  except Exception as e:
    print("LED Blink service failed")


# ------------------------------------ Main ------------------------------------
async def start_services():
  # Core services
  import wifi
  import web

  import relay


  gc.collect()

  # start other services here
  task['blink'] = asyncio.create_task(blink_start())

  app.wifi.scan()
  gc.collect()

  print("All tasks started")

  while True:
    await asyncio.sleep(100)
    gc.collect()

asyncio.run(start_services())
