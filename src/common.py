# Common elements to this project

import json
import os

# Degug level
SILENT = 0
ERROR = 1
WARNING = 2
INFO = 3    # Default level
DEBUG = 4
debug_level = SILENT


def debug(msg=None, msg_level=None, level=None):
    global debug_level
    level_str = ('','Error','Warning','Info','Debug')
    if level and isinstance(level, int) and SILENT < level <= DEBUG:
        debug_level = level
    if not msg_level or type(msg_level) != 'int':
        msg_level = INFO
    if msg and msg_level <= debug_level and debug_level > SILENT:
        print(level_str[msg_level] + ':', msg)

class Services:
    pass

service = Services()

def _cmd(cmd):
    print(f"Command recieved: {cmd}")
    return 'ok'


cmd = _cmd

if __name__ == '__main__':
  pass