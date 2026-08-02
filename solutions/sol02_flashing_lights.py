# Project 02 SOLUTION: Flashing Lights
# Version: V06
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)


def blink(blinks, on_time, off_time, red, green, blue):
    """Blink both lights. Given to students. Bails out on Cancel."""
    for _ in range(blinks):
        if sb.held('cancel'):
            return
        sb.light_both_leds(red, green, blue)
        time.sleep(on_time)
        sb.light_both_leds(0, 0, 0)
        time.sleep(off_time)


try:
    while not sb.held('cancel'):

        # WORK 1: the blink written out by hand, red, half a second each way.
        for _ in range(3):
            sb.light_both_leds(1, 0, 0)
            time.sleep(0.5)
            sb.light_both_leds(0, 0, 0)
            time.sleep(0.5)

        # WORK 2: the same idea, driven by named values, one line to run it.
        on_time = 0.4
        off_time = 0.4
        red = 0
        green = 1
        blue = 0
        blink(3, on_time, off_time, red, green, blue)

        # WORK 3: same call, new values. Fast cyan instead of slow green.
        on_time = 0.1
        off_time = 0.1
        red = 0
        green = 1
        blue = 1
        blink(3, on_time, off_time, red, green, blue)

    # FLEX: heartbeat. Start on_time at 0.6 and subtract 0.02 each lap,
    # resetting to 0.6 once it drops below 0.1. The blink speeds up,
    # then starts over.

finally:
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN, never a WORK item.
