# Project 04: Drive to the Wall and Back
# Version: V04
#
# GOAL: Your robot runs on its own. Power it up, press OK, and it drives
# to the wall, turns around, comes back to where it started, and turns
# to face the wall again -- ready to go as many times as you like. No
# Thonny, no cable, no gamepad.
#
# You type the code yourself, from the guide. Thonny does the indenting.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p04.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# The name matters this time. main.py looks for p04.py by name, so
# /workspace/p04.py is the only spelling that works.
#
# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# GIVEN: the robot and the suit. No gamepad in this project, so no WiFi
# and no browser.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# GIVEN: how close to the wall you stop, and how fast you get there.
WALL_THRESHOLD_CM = 5.0
DRIVE_SPEED_CMS = 10.0

try:
    # --- WORK 1: WAIT FOR THE GO SIGNAL ---
    # The robot starts itself now, so it must not drive off the second
    # it powers up. The guide gives you a loop that flashes both lights
    # and watches two pads: Cancel to quit, OK to go. Copy it in where
    # the "pass" line is, then delete the "pass" line.
    #
    # Stop after this and test it. At this point the program flashes
    # until you hold Cancel, and OK does nothing yet.
    pass

    # --- WORK 2: DRIVE TO THE WALL ---
    # Goes inside the "if" that WORK 1 gave you. Zero the pose, start
    # driving, and keep asking the distance sensor how much room is
    # left. Stop when the wall is closer than WALL_THRESHOLD_CM, then
    # give the robot a moment to actually finish stopping. The guide
    # explains why that last bit matters.

    # --- WORK 3: TURN AROUND AND COME BACK ---
    # Read how far you actually traveled, turn the robot around, drive
    # that same distance, and turn once more so it ends up facing the
    # wall again. The guide shows you where the robot keeps track of
    # where it has been.

finally:
    # GIVEN. A crash partway through a drive must never leave the wheels
    # running.
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
