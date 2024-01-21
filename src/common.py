# Common elements to the CP-IOT project
# By Simon Rigét 2022
# Released under MIT license

# Degug level
SILENT = 0
ERROR = 1
WARNING = 2
INFO = 3
DEBUG = 4

# Platform
PC = 1
ESP = 2

platform = int()
# debugLevel = int()

# Import platform specific modules and determine platform
try:
  import uasyncio as asyncio
  platform = ESP
except Exception as e:
  import asyncio
  platform = PC


def debug( msg=None, msg_level=None):
    if not msg_level or not isinstance(msg_level, int):
        msg_level = INFO
    if isinstance(msg, Exception) and app.debugLevel > SILENT:
        file = __file__.rsplit("/", 1)[1]
        print(f"Error: {type(msg).__name__} at line {msg.__traceback__.tb_lineno} of {file}: {msg}")
    elif msg and msg_level <= app.debugLevel and app.debugLevel > SILENT:
        print(app.debugLevelStr[msg_level] + ':', msg)


# A integer conversion, that return 0 on alle errors
def str2int(string):
    if isinstance(string, (int, float)):
        return int(string)
    try:
        i = int(float(string.strip()))
    except:
        i = 0
    return i


class PresentationData:
    def __init__(self, value=None, type=None, action=None, hint=None, advanced=None):
        self.value = value if value else ""
        self.type = type if type else "text"
        self.advanced = advanced if advanced else False
        self.hint = hint if hint else ""
        self.action = action


class App(dict):
    def __init__(self):
        dict.__init__(self)

        self.debugLevelStr = ('Silent', 'Error', 'Warning', 'Info', 'Debug')
        self.task = {}
        self.dashboard = {}
        self.debugLevel = DEBUG  # default


    def init2(self): # to allow circular references
        import config
        import command

        self.configure = config.Configure()
        self.cfg = self.configure.setting
        self.command = command.Command()
        self.context = self.command.context
        self.cmd = self.command.cmd
        self.registerContext = self.command.registerContext

    def startJob(self, ProcessName, asyncFunction):
        if len(ProcessName) and isinstance(ProcessName, str):
            if ProcessName in app.task:
                debug(f"Canẗ start job. Process already started: {ProcessName}", ERROR)
                return
        if callable(asyncFunction) and asyncio.iscoroutinefunction(asyncFunction):
            app.task[ProcessName] = asyncio.create_task(asyncFunction())
        else:
            debug(f"Canẗ start job. Call is not an asynchronous function: {ProcessName}", ERROR)

    def registerDashboardPresentationHandler(self, name, presentationHandler):
        if callable(presentationHandler):
            self.dashboard[name] = presentationHandler
        else:
            debug(f"Can't register presentation handler function: {name}", ERROR)


# System globals:
# if 'app' not in globals() or not isinstance(app, App):
app = App()
app.init2()

config = app.cfg
cfg = app.cfg
cmd = app.cmd
registerContext = app.registerContext
registerDashboardPresentationHandler = app.registerDashboardPresentationHandler
startJob = app.startJob





