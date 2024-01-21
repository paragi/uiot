# Command interpretation module
# By Simon Rigét 2022
# Released under MIT license
#
# command format: <context> <interaction>|all [<action>]
# context dictionary:
#   dict of contexts containing
#       dict of interactions containing
#           handler functions(context, interaction, Action)
#
# The Handler function is called, on a command with the registered context and interaction name.
# parameters:
#   context:        string. letters numbers and '/' no spaces
#                   '7' is used to identify sub context: foo/bar
#   interaction:    Interaction to manipulate. string. letters numbers and symbols. no spaces
#   action          string.
#
# Return:
#   string: ok | failed | one or more values. List element separated by nl
#
# If <action> is omitted, retrieving a value is assumed
# If <interaction> is omitted, it's set to 'all'. This makes i posible to have a <context> all handler.
#
from common import *

if platform == ESP:
    import uasyncio as asyncio
else:
    import asyncio
import os


help = {}
help['no context'] = '''
failed
{action} is not a registered context.
Use: list to see options.'''
help['generic'] = ''''ok
Commands has the format: <context> [<interaction> [<action>]]
- Context is usually the module name
- Interaction is the name of the thing, unique within the context
- Action is what to do with it. 

example: relay light on

Generic commands are:
- help [context]:   Show this text or if specified, interactions og context
- restart:          Restart device
- shutdown :        Turn off this device. (Require manual restart)
- exit, quit, bye:  same as shutdown
- factory reset:    Reset configuration to factory default settings
- say [...]:        Say something back
- list:             List available contexts
'''


class Command:
    class Handler:
        def __init__(self, handler, interactions):
            self.handler = handler
            self.interactions = interactions

    def __init__(self):
        self.context = {}

    # If no interactions are needen, a moduile can just register a context ands a command handler.
    def registerContext(self, context, handler, interactions = []):
        context = context.replace(' ', '_')
        if not context or not isinstance(context, str):
            debug(f"Can't register context. Not a string'")
            return False

        if not handler or not callable(handler):
            debug(f"Can't register context. {context}. Handler not a function'")
            return False

        debug(f"adding cmd context:  {context}", DEBUG)
        self.context[context] = self.Handler(handler, interactions)

    def bool2OnOff(self,str):
        action, sep, rest = str.partition(' ')

        if action in ['on','1','true','checked']:
            return 'on'
        elif action in ['off','0','false','unchecked']:
            return 'off'
        else:
            return False

    def cmd(self, cmd_str):
        while True:  # Run once
            try:
                reply = 'failed (2)\nCommand was empty'

                cmd_str = str(cmd_str).strip().lower()
                debug(f"CMD> {cmd_str}", DEBUG)
                if not cmd_str or not len(cmd_str) : break

                assert cmd_str, "empty command"
                cont, sep, rest1 = cmd_str.lower().partition(' ')
                interaction, sep, rest2 = rest1.partition(' ')
                action, sep, rest = rest2.partition(' ')

                if cont in self.context and callable(self.context[cont].handler):
                    if not len(interaction): interaction = 'all'

                    if len(action) > 0 and len(rest) == 0:
                        onOff = self.bool2OnOff(action)
                        if onOff: action = onOff

                    debug(f"Interpretation: context={cont} interaction={interaction} action={action}")

                    reply = self.context[cont].handler(interaction, action)

                else:
                    reply = self.cmd_handler(cont, rest1)

            except Exception as e:
                debug(e)
                reply = f"failed (5)\nInternal error"
            break

        if isinstance(reply, (list,tuple)):
            reply  = "\n".join(reply)

        debug(f"Reply : {reply}", DEBUG)
        return reply

    # Execute a drastic command with a small delay, to allow a return message
    async def deferred_cmd(self,command):
        try:
            if platform == ESP:
                import machine
            import os
            import sys

            await asyncio.sleep(0.5)

            if command == 'shutdown':
                print("The device will power down now...")
                if platform == ESP:
                    machine.deepsleep()
                else:
                    sys.exit(0)

            elif command == 'restart':
                print("The device will restart now...")
                if platform == ESP:
                    machine.reset()
                else:
                    os.execl(sys.executable, sys.executable, *sys.argv)

        except Exception as e:
            debug(e)

    # Simple system commands
    def cmd_handler(self, key, action):
        debug(f"system command: {key} {action}")

        if key == 'help':
            if len(action):
                if action not in app.context:
                    return help['no context']
                reply = "ok"
                for name, r in app.context[action]:
                    reply += f"\n{name} default value: {r.default}: {r.hint}"
                return reply
            return help['generic']

        elif key in ('restart', 'reset'):
            asyncio.ensure_future(self.deferred_cmd('restart'))
            return "ok\nRestarting device..."

        elif key in ('shutdown','exit','quit','bye'):
            asyncio.ensure_future(self.deferred_cmd('shutdown'))
            return "ok\nShutting down device..."

        elif key == 'factory' and action == 'reset' or key == 'factory_reset':
            try:
                debug("Deleting stored configuration")
                os.remove('config.json')
            except Exception as e:
                debug(e)
            asyncio.ensure_future(self.deferred_cmd('restart'))
            return "ok\nRestarting device..."

        elif key == 'say':
            return "ok\n" + action

        elif key == 'list':
            reply = "ok"
            for cont in self.context:
                reply += " \n" + cont
            return reply

        elif key == 'debug':
            try:
                interaction, sep, level = action.partition(' ')
                if interaction != 'level':
                    return f"failed\nunknow or missing interaction of debug '{interaction}'"
                levels = [item.lower() for item in app.debugLevelStr]
                if not len(level) or level not in levels:
                    return f"ok\nDebug level is '{app.debugLevelStr[app.debugLevel]}'"
                app.debugLevel = levels.index(level)
                return f"ok\nDebug level set to {app.debugLevelStr[app.debugLevel]}"
            except Exception as e:
                debug(e)
        else:
            return "failed\nSorry, don't know how to do that"