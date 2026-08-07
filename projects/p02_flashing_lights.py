# Project 02: Flashing Lights
# Version: V06
#
# GOAL: Make the robot's two lights blink, then take control of the blink
# with variables you write yourself.
#
# You type the code yourself, from the guide. Thonny does the indenting.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p02.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# GIVEN: the robot and the suit. You typed these yourself in P01. From
# here on they come with the file.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)


# GIVEN: the four-step blink, wrapped up so one line runs the whole
# thing. Read it -- there is nothing in here you will not have written by
# hand in WORK 1.
def blink(blinks, on_time, off_time, red, green, blue):
    """Blink both lights a set number of times.

    Stops early if you touch Cancel.
    """
    for _ in range(blinks):
        if sb.held('cancel'):
            return
        sb.light_both_leds(red, green, blue)
        time.sleep(on_time)
        sb.light_both_leds(0, 0, 0)
        time.sleep(off_time)


try:
    # GIVEN: the whole light show repeats until you touch the Cancel pad,
    # so you can watch it as many times as you like.
    while not sb.held('cancel'):

        # --- WORK 1: BLINK IT BY HAND ---
        # Copy the four-step blink from the guide and put it inside this
        # loop, where the "pass" line is. Then delete the "pass" line.
        for _ in range(3):
            pass

        # --- WORK 2: YOUR OWN VARIABLES ---
        # Copy the five variables and the blink call from the guide and
        # put them right here. Then change the numbers to your own.

        # --- WORK 3: CHANGE ONLY THE VARIABLES ---
        # Give those same five variables new values, then call blink again
        # with EXACTLY the same line you used in WORK 2. Do not retype the
        # call any differently -- copying it character for character is the
        # whole point.

finally:
    # GIVEN. A crash must never leave a light on.
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
