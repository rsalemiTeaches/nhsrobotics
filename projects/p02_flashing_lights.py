# Project 02: Flashing Lights
# GOAL: Learn variables and loops by blinking the NanoLED (the small color
# LED on the top board).
#
# Daily Goal 1 (today): make the LED blink using a loop.
# Daily Goal 2 (next class): use VARIABLES to control speed and color.

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
    # Press the X (cancel) button on the robot to stop.
    while not alvik.get_touch_cancel():

        # WORK 1: Turn the LED on using the color variables.
        # The command is:  nano.set_rgb(red, green, blue)

        # WORK 2: Wait for blink_time seconds.
        # The command is:  time.sleep(blink_time)

        # WORK 3: Turn the LED off.  The command is:  nano.off()

        # WORK 4: Wait again, so the off-time matches the on-time.
        pass  # delete this line once you've added your code

    # --- GOAL 2 (next class): PATTERNS WITH VARIABLES ---
    # Change blink_time to 0.1  -> what happens?
    # Change the color variables to make purple (red + blue).
    # WORK 5: Make a pattern: two fast red blinks, then one slow blue blink,
    # repeating. HINT: you will need more sleep and set_rgb lines inside
    # the loop, or a second set of color variables.

finally:
    nano.off()
    alvik.stop()
