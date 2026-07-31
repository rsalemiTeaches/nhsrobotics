# Project 02: Flashing Lights
# Version: V03
#
# GOAL: Make the robot's two lights blink, then take control of the blink
# with variables you write yourself.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p02.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
import time

alvik = ArduinoAlvik()
alvik.begin()


def both_leds(r, g, b):
    """Set the left and right lights to the same color.

    Given to you. One call instead of two.
    """
    alvik.left_led.set_color(r, g, b)
    alvik.right_led.set_color(r, g, b)


def blink(blinks, on_time, off_time, r, g, b):
    """Blink both lights a set number of times.

    Given to you. This is the whole four-step blink, wrapped up so you can
    run it with one line. It stops early if you touch Cancel.
    """
    for _ in range(blinks):
        if alvik.get_touch_cancel():
            return
        both_leds(r, g, b)
        time.sleep(on_time)
        both_leds(0, 0, 0)
        time.sleep(off_time)


try:
    # The whole light show repeats until you touch the X (cancel) button.
    while not alvik.get_touch_cancel():

        # --- WORK 1: BLINK IT BY HAND ---
        # Inside this loop, write the four steps of a blink. Use red, and
        # half a second for each wait:
        #   1. both_leds(1, 0, 0)   turn them red
        #   2. time.sleep(0.5)      wait
        #   3. both_leds(0, 0, 0)   turn them off
        #   4. time.sleep(0.5)      wait again, the SAME amount
        for _ in range(3):
            pass  # delete this line once your four lines are in

        # --- WORK 2: YOUR OWN VARIABLES ---
        # A variable is a name for a value. Make five of them right here.
        # Pick your own numbers:
        #
        #   on_time  = 0.5     how long the lights stay on
        #   off_time = 0.5     how long they stay off
        #   r = 1              red   part, 0 or 1
        #   g = 0              green part, 0 or 1
        #   b = 0              blue  part, 0 or 1
        #
        # Then blink three times using the NAMES, not numbers:
        #
        #   blink(3, on_time, off_time, r, g, b)

        # --- WORK 3: CHANGE ONLY THE VARIABLES ---
        # Give those same five variables new values. Pick a different
        # color and a faster or slower blink.
        #
        # Then call blink again with EXACTLY the same line as WORK 2:
        #
        #   blink(3, on_time, off_time, r, g, b)
        #
        # Same call, different result, because the variables changed.
        # That is the whole point of a variable.

finally:
    both_leds(0, 0, 0)
    alvik.stop()  # Always call this. It stops the robot software and
                  # frees the WiFi network. Without it the robot can
                  # hang and need a restart.
