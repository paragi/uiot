# -*- coding: utf-8 -*-
import os

micro_controler = (os.uname().machine == 'ESP module with ESP8266')
if micro_controler:
    from machine import Pin, I2C
    import ssd1306

class Dispplay_conf:
    size_x = 128
    size_y = 64

class Display_stub:
    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y

    def text(self, str, x, y, c = 1):
        print(str)

    def pixel(self, x, y, c):
        pass

    def show(self):
        pass
    def invert(self, state):
        pass

def bar_chart_function(data, x, y, width, height):
    elements = len(data)
    bar_width = int(x / elements)
    y_scale = height / max(data)
    for i in range(0, elements - 1):
        x_start = i * bar_width
        if micro_controler:
            display.fill_rect(x_start, y, bar_width, int(y_scale * data[i]),1)
        else:
            print(x, Dispplay_conf.size_y - 1, x + bar_width, int(y_scale * data[i]))

#ssd1306_gfx.SSD1306_I2C_SETUP.bar_chart = bar_chart_function

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if micro_controler:
        # Set LED on
        led = Pin(2, Pin.OUT)
        led.value(0)

        # Setup ssd1306 OLED display
        display = ssd1306.SSD1306_I2C(Dispplay_conf.size_x, Dispplay_conf.size_y, I2C(sda=Pin(4), scl=Pin(5)))
        #display = ssd1306_gfx.SSD1306_I2C_SETUP(Pin(4), Pin(5), Dispplay_conf.size_x, Dispplay_conf.size_y)
    else:
        display = Display_stub(Dispplay_conf.size_y, Dispplay_conf.size_x)
        
    display.bar_chart = bar_chart_function    
    #display.fill(1)
    display.invert(True)

    print(os.uname().machine)
    #display.text(os.uname().machine, 0, 0, 1)
    display.text('Nu pris: 5,45 Kr.', 0, 0, 1)
    display.text('3t slot: kl 14', 0, 10, 1)
    display.text('6t slot: kl 12', 0, 20, 1)
    display.pixel(63, 47, 1)
    display.show()

    print("Done")
    if micro_controler:
        led.value(1)
    display.invert(False)

    spot_price = [1.23,2.3,3.8,5.9,6.2,3.7,2.1,0.3,0.3,0.3,0.3,0.3,0.3,0.3,1.23,2.3,3.8,5.9]
    display.bar_chart(spot_price, 0, Dispplay_conf.size_y-1, Dispplay_conf.size_x, Dispplay_conf.size_y-24)
    display.show()