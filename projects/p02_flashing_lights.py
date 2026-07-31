# Project 02: Flashing Lights
# GOAL: Learn variables and loops by blinking the NanoLED (the small color
# LED on the top board).
#
# Daily Goal 1 (today): make the LED blink using a loop.
# Daily Goal 2 (next class): use VARIABLES to control speed and color.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p02.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import NanoLED
import time

alvik = ArduinoAlvik()
alvik.begin()
nano = NanoLED()

# --- VARIABLES ---
# A variable is a named value you can change in ONE place.
blink_time = 0.5     # seconds the LED stays on (and off)
red = 255            # color parts, each 0-255
green = 0
blue = 0

try:
    # --- GOAL 1: THE BLINK LOOP ---
    # Runs a FIXED number of times, then moves on to GOAL 2 below on its
    # own -- that way Goal 1's blink and Goal 2's pattern BOTH run every
    # time you press play, and you never have to erase Goal 1 to build
    # Goal 2.
    for _ in range(6):

        # WORK 1: Turn the LED on using the color variables, then wait
        # blink_time seconds. The commands are:
        #     nano.set_rgb(red, green, blue)
        #     time.sleep(blink_time)

        # WORK 2: Turn the LED off, then wait again so the off-time
        # matches the on-time. The commands are:
        #     nano.off()
        #     time.sleep(blink_time)
        pass  # delete this line once you've added your code

    # --- GOAL 2 (next class): PATTERNS WITH VARIABLES ---
    # Change blink_time to 0.1 above and rerun -- what happens to GOAL 1?
    # Change the color variables to make purple (red + blue) and rerun.
    # WORK 3: Make a pattern: two fast red blinks, then one slow blue
    # blink, repeating -- until the X (cancel) button is touched. HINT:
    # you will need more sleep and set_rgb lines inside the loop, or a
    # second set of color variables.
    while not alvik.get_touch_cancel():
        pass  # delete this line once your pattern code is in

finally:
    nano.off()
    alvik.stop()
