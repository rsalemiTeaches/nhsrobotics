# Project 10 SOLUTION: Robot Timers
from arduino_alvik import ArduinoAlvik
from nhs_robotics import NanoLED
import time

alvik = ArduinoAlvik()
alvik.begin()
nano = NanoLED()

blink_delay = 500
led_is_on = False
last_toggle_time = time.ticks_ms()

try:
    while not alvik.get_touch_cancel():
        now = time.ticks_ms()

        # GOAL 1 (WORK 1)
        if time.ticks_diff(now, last_toggle_time) > blink_delay:
            led_is_on = not led_is_on
            if led_is_on:
                nano.set_rgb(255, 0, 0)
            else:
                nano.off()
            last_toggle_time = now

        # GOAL 2 (WORK 2-4)
        if alvik.get_touch_up():
            blink_delay = max(100, blink_delay - 100)
            print("blink_delay =", blink_delay)
            time.sleep(0.25)   # crude de-bounce: one press = one step
        if alvik.get_touch_down():
            blink_delay = min(2000, blink_delay + 100)
            print("blink_delay =", blink_delay)
            time.sleep(0.25)

        # FLEX: color follows speed — map blink_delay (100..2000) to a
        # red/blue mix so fast = red, slow = blue:
        # red = int(255 * (2000 - blink_delay) / 1900)
        # blue = 255 - red
        # ...use (red, 0, blue) instead of (255, 0, 0).

        time.sleep(0.01)
finally:
    nano.off()
    alvik.stop()
