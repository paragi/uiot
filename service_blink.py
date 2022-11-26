# ESP32 blink developer board LED (pin 2)

async def start():
    print("Starting blink service")
    try:
        import machine
        led = machine.Pin(2, machine.Pin.OUT)
        while True:
            led.value(not led.value())
            await asyncio.sleep(0.5)
            # print(".", end='')

    except Exception as e:
        print("LED Blink service failed")
