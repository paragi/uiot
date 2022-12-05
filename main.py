import gc
try:
    import uasyncio as asyncio
except Exception as e:
    import asyncio
from common import *
import config as config_moduel
import relay
import wifi
import service_blink
import service_count
import service_webserver

debug(level=DEBUG)


def cmd(command):
    reply = 'failed'
    try:
        (context, interaction, action) = command.split(" ", 2)
        debug(f"Command context: {context} interaction: {interaction} action {action}", DEBUG)
        if context.startswith('relay'):
            action = 0 if action == 'off' or action == "false" else 1
            service.relay.set(int(interaction), action)
            reply = 'ok'
        elif context.startswith('conf'):
            if '/' in context:
                group = context.split("/")[1]
                if group in config and interaction in config[group]:
                    config[group][interaction].value = action
                    reply = 'ok'
            elif interaction == 'data':
                if action == 'save':
                    service.config.store()
                    reply = 'ok'
                elif action == 'reset':
                    service.config.delete()
                    reply = 'ok'
    except Exception as e:
        debug(f"Command error: {e}")
    debug(f"Reply {reply}", DEBUG)
    return reply


config_moduel.retrieve()
config = config_moduel.config
debug(f"Config: {config}")
service.config = config_moduel
service.wifi = wifi.Wifi()
service.cmd = cmd
service.relay = relay.Relay(4)


async def start_services():
    gc.collect()
    tasks = [
        # asyncio.create_task(service_count.start()),
        asyncio.create_task(service_blink.start()),
        asyncio.create_task(service_webserver.start('0.0.0.0', config['webserver']['port'].value, routes)),
    ]
    await asyncio.gather(*tasks)
    print("All tasks have completed now.")


# AP settings
#ssid = config['access point']['ssid'].value  # 0 - 32-byte
#key = config['access point']['key'].value  # 0-63 bytes
# channel = config['access point']['channel']


# if not wifi.ap(ssid=ssid, key=key,channel=channel):
#    debug("Unable to establish network connection")

# Wifi connect
ssid = config['wifi']['ssid'].value  # 0 - 32-byte
key = config['wifi']['key'].value  # 0-63 bytes

if not service.wifi.connect(ssid=ssid, key=key):
    debug("Unable to establish network connection")

#host = config['webserver']['host ip'].value
port = config['webserver']['port'].value

routes = [
    ("/", service_webserver.dashboard_page),
    ("/index.html", service_webserver.dashboard_page),
    ("/dashboard.html", service_webserver.dashboard_page),
    ("/setup.html", service_webserver.setup_page),
    ("/status.html", service_webserver.status_page),
    ("/theme.css", service_webserver.static_file_handler),
    ("/favicon.ico", service_webserver.static_file_handler),
    ("/logo.png", service_webserver.static_file_handler),
    ("/logo.gif", service_webserver.static_file_handler),
    ("/test.pyhtml", service_webserver.static_file_handler),
    ("/test.pyhtml", service_webserver.static_file_handler),
    ("/api", service_webserver.api_handler),
    # (re.compile("^/iam/(.+)"), hello),
]



asyncio.run(start_services())
