# Project 02: Flashing Lights
# GOAL: Learn variables and loops by blinking the NanoLED (the small color
# LED on the top board).
#
# WORK 1-2: make the LED blink using a loop.
# WORK 3: use VARIABLES to build a pattern.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p02.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

# FLEX (the A+): a heartbeat. The blink starts slow and speeds up each cycle,
# then resets. Hint: subtract a little from blink_time every lap of the loop,
# and reset it when it reaches 0.1. Copy your code into the FLEX box.

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
    # --- WORK 1-2: THE BLINK LOOP ---
    # Runs a FIXED number of times, then moves on to the pattern loop below on its
    # own -- that way the blink and the pattern BOTH run every time you
    # press play, and you never have to erase one to build the other.
    for _ in range(6):

        # WORK 1: Turn the LED on using the color variables, then pause
        # for blink_time seconds so it stays on that long. Check Part 1,
        # section 3 of the guide (The NanoLED) if you forget the command.

        # WORK 2: Turn the LED back off, then pause again -- the SAME
        # length as WORK 1, so on-time and off-time match.
        pass  # delete this line once you've added your code

    # --- WORK 3: PATTERNS WITH VARIABLES ---
    # Change blink_time to 0.1 above and rerun -- what happens to the blink?
    # Change the color variables to make purple (red + blue) and rerun.
    # WORK 3: Make a pattern: two fast red blinks, then one slow blue
    # blink, repeating -- until the X (cancel) button is touched. HINT:
    # you will need more sleep and set_rgb lines inside the loop, or a
    # second set of color variables.
    while not alvik.get_touch_cancel():
        pass  # delete this line once your pattern code is in
        time.sleep(0.01)  # tiny pause every lap -- keeps Cancel responsive

finally:
    nano.off()
    alvik.stop()
