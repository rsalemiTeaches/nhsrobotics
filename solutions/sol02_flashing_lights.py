# Project 02 SOLUTION: Flashing Lights
# Version: V03
from arduino_alvik import ArduinoAlvik
import time

alvik = ArduinoAlvik()
alvik.begin()


def both_leds(r, g, b):
    """Set both lights to the same color. Given to students."""
    alvik.left_led.set_color(r, g, b)
    alvik.right_led.set_color(r, g, b)


def blink(blinks, on_time, off_time, r, g, b):
    """Blink both lights. Given to students. Bails out on Cancel."""
    for _ in range(blinks):
        if alvik.get_touch_cancel():
            return
        both_leds(r, g, b)
        time.sleep(on_time)
        both_leds(0, 0, 0)
        time.sleep(off_time)


try:
    while not alvik.get_touch_cancel():

        # WORK 1: the blink written out by hand, red, half a second each way.
        for _ in range(3):
            both_leds(1, 0, 0)
            time.sleep(0.5)
            both_leds(0, 0, 0)
            time.sleep(0.5)

        # WORK 2: the same idea, driven by named values, one line to run it.
        on_time = 0.4
        off_time = 0.4
        r = 0
        g = 1
        b = 0
        blink(3, on_time, off_time, r, g, b)

        # WORK 3: same call, new values. Fast cyan instead of slow green.
        on_time = 0.1
        off_time = 0.1
        r = 0
        g = 1
        b = 1
        blink(3, on_time, off_time, r, g, b)

    # FLEX: heartbeat. Start on_time at 0.6 and subtract 0.02 each lap,
    # resetting to 0.6 once it drops below 0.1. The blink speeds up,
    # then starts over.

finally:
    both_leds(0, 0, 0)
    alvik.stop()  # GIVEN, never a WORK item.
