# Common elements to the CP-IOT project
# By Simon Rigét 2022
# Released under MIT license
# Import generic modules
print('+-----------------------------------------------------------+')
print('|                  Edge Node Platform 1                     |')
print('+-----------------------------------------------------------+')

import gc

# import core modules
print('Initializing core modules...')
from common import *

# importing libraries
import os

'''
import psutil


# inner psutil function
def process_memory():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss


# decorator function
def profile(func):
    def wrapper(*args, **kwargs):
        mem_before = process_memory()
        result = func(*args, **kwargs)
        mem_after = process_memory()
        print("{}:consumed memory: {:,}".format(
            func.__name__,
            mem_before, mem_after, mem_after - mem_before))

        return result

    return wrapper

'''

async def cmd_start():
  try:
    end = False
    while not end:
      command = input(cfg['general']['devicename'].values + '>')
      if command in ('end', 'exit', 'quit', 'bye', 'x'):
        end = True
        print('Bye')
        break;
      else:
        reply = app.cmd(command)
        for line in reply:
          print(line)
  except Exception as e:
    print("Command line service failed")

# ------------------------------------ Main ------------------------------------
async def start_services():
  print('Loading and initializing modules...')

  if 'module' not in config:
    config['module'] = {}

  modules = sorted([i for i in os.listdir() if i.startswith('0')])
  for fileName in modules:
    name = fileName.split('.',2)[0]
    if name not in config['module']:
      config.add('module', name, ('on', 'off'), 'on')

    if config['module'][name].value == 'on':
      print('Loading module', name)
      __import__(name)
      gc.collect()

  # Read configuration from file
  app.configure.retrieve()

  # app.wifi.scan()
  gc.collect()

  # Keep alive
  while True:
    await asyncio.sleep(1000)


app.debugLevel = DEBUG
# app.debugLevel = WARNING

# Add default device name
config.add('general','devicename', 'text','ENP-1 unit')

# Config can't register interactions because of circular initialiazion
# So it has to be done here instead of in cfg.py
registerContext('cfg', app.configure.handle_cmd, ['save','store'])
registerContext('config', app.configure.handle_cmd, ['save','store'])
registerContext('configuration', app.configure.handle_cmd, ['save','store'])

# Start all services as background jobs
asyncio.run(start_services())

# take input from usb interface
def not_avtive():
  end = False
  while not end:
    command = input(cfg['general']['devicename'].values + '>')
    if command in ('end', 'exit', 'quit', 'bye', 'x'):
      end = True
      print('Bye')
      break;
    else:
      reply = app.cmd(command)
      for line in reply:
        print(line)