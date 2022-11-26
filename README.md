# Elpris


## Installation
TODO: find bedre metode 

### GitHub
I terminalen:

    git config --global user.email "you@example.com"
    git config --global user.name "Your Name"
    (... opret token vis PyCharm)

### flash ESP32 med micropython
### connect to WiFi
In REPL and type:

    import network
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect('<ssid>', '<password>')
 
test:

    print(station.ifconfig())

### Install dependencies
In REPL and type:

    import upip
    upip.install('micropython-uasyncio')
    upip.install('micropython-pkg_resources')
    upip.install('micropython-ulogging')
