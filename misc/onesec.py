from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
sb = SuperBot(alvik)

try:
    led_on = True
    start_time = time.ticks_ms()
    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, start_time) > 1000:
            led_on = not led_on
            start_time = now
            
        if led_on:
            sb.nano_led.set_color(0,1,0)
        else:
            sb.nano_led.set_color(0,0,0)
finally:
    sb.nano_led.set_color(0,0,0)
    
