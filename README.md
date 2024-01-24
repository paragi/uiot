# Edge Node Platform - one

ENP-1 is a platform for solutions based on ESP32 (a cheep and versetile microcontroler devices) 
It provides basic functionality and easy adaption of modules intendet for specific hardware
Modules are writen in python, using micropython firmware.

ENP-1 is mainly intented for smarthome devices. 

Main features:
    * WiFi client og access point mode
    * Webserver with dashboard, configuration at tools.
    * MQTT
    * Command interface
    * Timer
    * Relay control module
    * support for some one-wire and i2c peripherals

ENP-1 was originally made as a teaching tool for kids, to play with microcontrolers.

Current state: Alpha


## Installation
TODO:  

### GitHub

### flash ESP32 med micropython

    pip install esptool

Slet hukommelsen og installer micropython:

Linux:

    esptool.py --port /dev/ttyUSB0 erase_flash
    esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-20220618-v1.19.1.bin

Window

    esptool.py --port COM4 erase_flash
    esptool.py --chip esp32 --port COM4 write_flash -z 0x1000 esp32-20220618-v1.19.1.bin

Hold boot microswitchen (til højre for USB kablet) til den starter

flash alle filer under "src" til ESP-32 i roden.


### connect to WiFi
TODO

