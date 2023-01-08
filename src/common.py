# Common elements to the CP-IOT project
# By Simon Rigét 2022
# Released under MIT license

try:
    import uasyncio as asyncio
except:
    import asyncio

# Degug level
SILENT = 0
ERROR = 1
WARNING = 2
INFO = 3
DEBUG = 4
debug_level = INFO

class App(dict):
    def __init__(self):
        import command # Import locally to avoid circular references
        import config
        # Setup basic structure
        self.command = command.Command()
        self.context = self.command.context
        self.cmd = self.command.cmd
        self.register_context = self.command.register_context
        self.register_interaction = self.command.register_interaction
        self.configure = config.Configure()
        self.config = self.configure.setting
        self.task = {}
        self.loop = None

def debug( msg=None, msg_level=None, level=None):
    global debug_level
    level_str = ('', 'Error', 'Warning', 'Info', 'Debug')
    if level and isinstance(level, int) and SILENT < level <= DEBUG:
        debug_level = level
    if not msg_level or type(msg_level) != 'int':
        msg_level = INFO
    if msg and msg_level <= debug_level and debug_level > SILENT:
        print(level_str[msg_level] + ':', msg)


# System globals:
app = App()
cmd = app.cmd
register_context = app.register_context
register_interaction = app.register_interaction
config = app.config
task = app.task

# Config can't register interactions because of circulær initialiazion
# So it has to be done here instead of in config.py (Don't we just LOVE OO hiraki :)
register_interaction('config', 'factory_reset', app.configure.handle_cmd)
register_interaction('config', 'save', app.configure.handle_cmd)
register_interaction('config', 'store', app.configure.handle_cmd)
register_interaction('config', 'all', app.configure.handle_cmd)
for group in config:
    for field in config[group]:
        register_interaction('config', f"{group}/{field}", app.configure.handle_cmd)
