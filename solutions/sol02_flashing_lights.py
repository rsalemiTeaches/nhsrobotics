# Project 02 SOLUTION: Flashing Lights
from arduino_alvik import ArduinoAlvik
from nhs_robotics import NanoLED
import time

alvik = ArduinoAlvik()
alvik.begin()
nano = NanoLED()

blink_time = 0.5
red = 255
green = 0
blue = 0

try:
    # GOAL 1 solution: basic blink
    # while not alvik.get_touch_cancel():
    #     nano.set_rgb(red, green, blue)   # WORK 1
    #     time.sleep(blink_time)           # WORK 1
    #     nano.off()                       # WORK 2
    #     time.sleep(blink_time)           # WORK 2

    # GOAL 2 solution: two fast red blinks, one slow blue blink  (WORK 3)
    fast = 0.1
    slow = 0.6
    while not alvik.get_touch_cancel():
        for _ in range(2):               # two fast red blinks
            nano.set_rgb(255, 0, 0)
            time.sleep(fast)
            nano.off()
            time.sleep(fast)
        nano.set_rgb(0, 0, 255)          # one slow blue blink
        time.sleep(slow)
        nano.off()
        time.sleep(slow)

    # FLEX solution sketch (heartbeat that speeds up):
    # start blink_time at 0.6; subtract 0.02 each cycle; reset at 0.1.
finally:
    nano.off()
    alvik.stop()
