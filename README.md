# Coding Pirate Elpris projekt

Udestående problemer:
* moderne browsere accepterer ikke at vise sider fra ESP i access point mode. (Der er masser af trafik, men siden vises ikke)
* Optimer caching
* Optimer memory forbrug



## Installation
TODO: find bedre metode 

### GitHub
I terminalen:

    git config --global user.email "you@example.com"
    git config --global user.name "Your Name"
    (... opret token via PyCharm)

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




### connect to WiFi
In REPL and type:

    import network
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect('<ssid>', '<password>')
 
test:

    print(station.ifconfig())


