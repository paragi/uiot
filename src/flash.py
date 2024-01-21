# Flash LED
# An LED is usually attach to GPIO pin 2 on a developer board.
# This module starts a job, that flashed this LED
# This will only work on an ESP32 developer board, but must not trigger exception when run on other platforms.

# Import common functionality of the application
from common import *

# Import the platform specific module to utilize the GPIO
if platform == ESP:
    import machine


class Flash():
  def __init__(self):
    if platform == ESP:
      # Initialize GPIO pin 2 to output
      self.led = machine.Pin(2, machine.Pin.OUT)
      self.enable: bool = config['flash']['frequency'].value == 'on'
    else:
      self.enable = False

  # this i an asynchronous function that runs in the background and flashes an LED
  async def start(self):
    if platform == ESP:
      try:
        # Continue to toggle the output forever
        while True:
          if self.enable:
            self.led.value(not self.led.value())
          frequency = float(config['flash']['frequency'])
          # Keep waiting time sane
          if frequency < 0.01 or frequency > 100: frequency = 1
          await asyncio.sleep(1/frequency)
          # print(".", end='')

      except Exception as e:
        debug(e)
    else:
      print("LED flash service not running on this platform")

  def handleCmd(self, interaction, action):
    if interaction == 'led':
      if len(action) and action in ('on', 'off', 'toggle'):
        if action == 'toggle':
          self.enable = not self.enable
        else:
          self.enable = True if action == 'on' else False
      return f"ok\nFlash led is {'on' if self.enable else 'off'}"
    elif interaction in ('frequency', 'freq'):
      if len(action):
        config['flash']['frequency'] = str2int(action)
        return 'ok'
    else:
      return f"failed\nInteraction {interaction} not recognised"

  def handlePresentation(self):
    presentation = {}
    presentation['Flash LED enable'] = PresentationData(self.enable, 'slider', f'flash led')
    presentation['Flash frequency Hz'] = PresentationData(config['flash']['frequency'].value, 'float')
    return presentation


# ------------  Module registration ------------
# Register factory configuration
# Usages: config.add( group or module name, name, type ('text'), alias, cfguratioon hint, advanced view only)
# Example config.add('relay', '1-name', 'text', 'Relæ-1', 'Name used to reference this interaction', True)
config.add('flash', 'led', 'bool', 'on', 'Enable LED to flash', False)
config.add('flash', 'frequency', 'float', '2', 'Number of flashed pr. second. ', False)

# All modules must register itself and attach to the application
app.flash = Flash()
startJob('flash', app.flash.start)

# What to show on the dashboard
# dashboard['Flash'] = app.flash.handlePresentation
# registerDashboardPresentationHandler('Flash LED', app.flash.handlePresentation)

# Register the context of this module, and a handler for commands to same
# Commands has the format: <context> [<interaction> [<action>]]
#   Context is usually the module name
#   Interaction is the name of the thing, unique within the context
#   Action is what to do with it
# The command handler is a function that handles commands sent to this module.
registerContext('flash', app.flash.handleCmd)

# Run this code, if run alone (for test purposes). Else ignore
if __name__ == '__main__':
    pass
