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
# The Handler function is called, when a command the registered context and interaction name.
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

class Command:
    def __init__(self):
        self.context = {}
        self.register_interaction('command','help', self.cmd_handler)
        self.register_interaction('command','all', self.cmd_handler)

    def register_context(self, context, handler):
        self.register_interaction(self, context.replace(' ', '_'), '*', handler)

    def register_interaction(self, context, interaction, handler):
        if not context \
                or not isinstance(context, str) \
                or not interaction \
                or not isinstance(interaction, str) \
                or not handler:
            debug(f"Can't register interaction '{context}' '{interaction}' {(handler)}")
            return False
        if context not in self.context:
            self.context[context] = {}
        self.context[context.replace(' ', '_')][interaction.replace(' ', '_')] = handler

    def cmd(self, cmd_str):
        while True:  # Run once
            reply = 'failed'
            debug(f"CMD> {cmd_str}", DEBUG)
            if not cmd_str or not len(cmd_str) or not isinstance(cmd_str, str): break
            assert cmd_str, "empty command"
            cont, sep, rest = cmd_str.partition(' ')
            interaction, sep, action = rest.partition(' ')
            if not len(interaction): interaction = 'all'
            debug(f"Interpretation: context={cont} interaction={interaction} action={action}")
            if cont in self.context:
                if not interaction: interaction = 'all'
                if interaction in self.context[cont]:
                    if callable(self.context[cont][interaction]):
                        reply = self.context[cont][interaction](interaction, action)
            break
        debug(f"Reply: {reply}", DEBUG)
        return reply

    def cmd_handler(self, interaction, action):
        reply = ['failed']
        if interaction == 'all' or interaction == 'help':
            reply = ['ok']
            for grp in self.context:
                for intact in self.context[grp]:
                    reply.append(f"{grp} {intact} <action>")
        return reply