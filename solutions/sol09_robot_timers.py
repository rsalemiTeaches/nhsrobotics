# Project 09 SOLUTION: Robot Timers
from arduino_alvik import ArduinoAlvik
from nhs_robotics import NanoLED, Button
import time

alvik = ArduinoAlvik()
alvik.begin()
nano = NanoLED()

# Button() reports a press only on the tick the touch STARTS (a "rising
# edge"), so one press is one step -- and it never sleeps.
btn_up = Button(alvik.get_touch_up)
btn_down = Button(alvik.get_touch_down)

blink_delay = 500
led_is_on = False
last_toggle_time = time.ticks_ms()

try:
    while not alvik.get_touch_cancel():
        now = time.ticks_ms()

        # WORK 1
        if time.ticks_diff(now, last_toggle_time) > blink_delay:
            led_is_on = not led_is_on
            if led_is_on:
                nano.set_rgb(255, 0, 0)
            else:
                nano.off()
            last_toggle_time = now

        # WORK 2-3
        if btn_up.is_pressed():                         # WORK 2
            blink_delay = max(100, blink_delay - 100)
            print("blink_delay =", blink_delay)         # WORK 2 (continued)
        if btn_down.is_pressed():                       # WORK 3
            blink_delay = min(2000, blink_delay + 100)
            print("blink_delay =", blink_delay)         # WORK 3 (continued)

        # FLEX: color follows speed — map blink_delay (100..2000) to a
        # red/blue mix so fast = red, slow = blue:
        # red = int(255 * (2000 - blink_delay) / 1900)
        # blue = 255 - red
        # ...use (red, 0, blue) instead of (255, 0, 0).

        time.sleep(0.01)
finally:
    nano.off()
    alvik.stop()
