# Project 10: Robot Timers
# GOAL: Blink WITHOUT time.sleep().
#
# Remember P04? While a move ran its sleep(), the robot ignored you.
# sleep() FREEZES the whole program. Real robots can't freeze — they
# must blink AND watch buttons AND read sensors, all at once.
#
# The trick: instead of stopping, keep a clock and ask every loop:
#   "has enough time passed yet?"
#     time.ticks_ms()          -> the clock, in milliseconds
#     time.ticks_diff(now, before) -> milliseconds between two readings
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p10.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import NanoLED
import time

alvik = ArduinoAlvik()
alvik.begin()
nano = NanoLED()

blink_delay = 500          # milliseconds between toggles
led_is_on = False
last_toggle_time = time.ticks_ms()

try:
    while not alvik.get_touch_cancel():
        now = time.ticks_ms()

        # --- GOAL 1: THE NON-BLOCKING BLINK ---
        # WORK 1: if ticks_diff(now, last_toggle_time) > blink_delay:
        #   - flip led_is_on  (HINT:  led_is_on = not led_is_on)
        #   - if led_is_on, set the LED red; otherwise nano.off()
        #   - record now as the new last_toggle_time

        # --- GOAL 2 (next class): LIVE SPEED CONTROL ---
        # Because the loop never sleeps, buttons work DURING the blink!
        # WORK 2: UP arrow  (alvik.get_touch_up())   -> blink faster:
        #             subtract 100 from blink_delay (minimum 100),
        #             then print the new blink_delay.
        # WORK 3: DOWN arrow (alvik.get_touch_down()) -> blink slower:
        #             add 100 to blink_delay (maximum 2000),
        #             then print the new blink_delay.

        time.sleep(0.01)   # tiny pause; NOT the blink timing!

finally:
    nano.off()
    alvik.stop()
