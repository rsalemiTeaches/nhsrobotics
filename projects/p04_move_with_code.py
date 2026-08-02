# Project 04: Move With Code
# Version: V01
#
# GOAL: The robot drives a measured distance and turns a measured angle
# because your code said exactly how far. Then you pack a whole route
# under one name.
#
# You type the code yourself, from the guide. Thonny does the indenting.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p04.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# GIVEN: the robot and the suit. No gamepad in this project, so no WiFi
# and no browser. Just the USB cable and the pads on the robot.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)


# --- YOUR FUNCTIONS GO HERE ---
# Both of them, above the loop. WORK 1 has no function -- it lives down
# in the loop with the others.


# --- WORK 2: YOUR FIRST FUNCTION ---
# The guide prints a function named patrol(). Copy it here. Writing a
# function does not run it.


# --- WORK 3: A FUNCTION THAT TAKES AN ARGUMENT ---
# A square, driven by a for loop, in a function that takes the length of
# a side. The guide does not print this one -- it shows you the pieces
# and you put them together. Write it here.


try:
    # The Cancel pad on the robot ends the run.
    while not sb.held('cancel'):

        # --- WORK 1: DRIVE ONE LEG ---
        # The guide gives you an "if" that fires when you touch UP, and
        # two lines under it that drive forward and turn a corner. Copy
        # them here, then get a ruler and find out what the robot really
        # did.

        # --- WORK 2 (continued) ---
        # Add patrol() to the chain with an elif, on the LEFT pad.

        # --- WORK 3 (continued) ---
        # Add your square with one more elif, on the RIGHT pad. Hand it a
        # real number when you call it.

        time.sleep(0.02)

finally:
    # GIVEN. The same emergency cleanup you wrote yourself in P03. Your
    # moves stop their own wheels, but a crash partway through one does
    # not, and that is what brake() is here for.
    alvik.brake()
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
