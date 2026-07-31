# Project 09: Robot Timers
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
# (MicroPython device), and save this file as /workspace/p09.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import NanoLED, Button
import time

alvik = ArduinoAlvik()
alvik.begin()
nano = NanoLED()

blink_delay = 500          # milliseconds between toggles
led_is_on = False
last_toggle_time = time.ticks_ms()

# A plain alvik.get_touch_up() is True the WHOLE time you hold the
# button, so one press would count dozens of times. Button() reports the
# press only on the tick it STARTS -- one press, one step, no sleeping.
btn_up = Button(alvik.get_touch_up)
btn_down = Button(alvik.get_touch_down)

try:
    while not alvik.get_touch_cancel():
        now = time.ticks_ms()

        # --- WORK 1: THE NON-BLOCKING BLINK ---
        # WORK 1: if ticks_diff(now, last_toggle_time) > blink_delay:
        #   - flip led_is_on  (HINT:  led_is_on = not led_is_on)
        #   - if led_is_on, set the LED red; otherwise nano.off()
        #   - record now as the new last_toggle_time

        # --- WORK 2-3: LIVE SPEED CONTROL ---
        # Because the loop never sleeps, buttons work DURING the blink!
        # WORK 2: if btn_up.is_pressed()   -> blink faster:
        #             subtract 100 from blink_delay (minimum 100),
        #             then print the new blink_delay.
        # WORK 3: if btn_down.is_pressed() -> blink slower:
        #             add 100 to blink_delay (maximum 2000),
        #             then print the new blink_delay.
        # Do NOT use time.sleep() to stop double-counting -- that is the
        # exact freeze this whole project exists to avoid.

        time.sleep(0.01)   # tiny pause; NOT the blink timing!

finally:
    nano.off()
    alvik.stop()
