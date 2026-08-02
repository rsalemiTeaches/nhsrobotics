# Project 04: Button Moves
# Version: V01
#
# GOAL: Write your own functions. Each one is a move, and each move gets
# a button on the gamepad.
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
from nhs_robotics import SuperBot, RobotGamepad
import time

# GIVEN: the robot, the suit and the gamepad. You typed these yourself in
# P01. From here on they come with the file.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)
gamepad = RobotGamepad(alvik)


# --- WORK 1: YOUR FIRST FUNCTION ---
# The guide prints a speed variable and a function named spin_move().
# Copy both of them here. Function definitions live above the loop --
# writing one does not run it.
#
# No move in this project stops the wheels. The else down in the loop
# does that, and it is the only thing that does.


# --- WORK 2: A MOVE YOU WRITE YOURSELF ---
# The guide describes wiggle_move() but does not print it. Write it here,
# with its own speed variable, under spin_move(). Then put it on a
# button down in the loop.


# --- WORK 3: A MOVE THAT TAKES AN ARGUMENT ---
# Your own move, and this one takes a value from whoever calls it. The
# guide shows you how a def line takes an argument. Write it here.


try:
    # Cancel on the robot or Options on the gamepad ends the run.
    while not (sb.held('cancel') or gamepad.held('options')):
        gamepad.update()

        # --- WORK 1 (continued): PUT IT ON A BUTTON ---
        # The guide gives you an "if" that calls spin_move() while you
        # hold X, and an "else" that brakes when you are not holding
        # anything. Copy both here.

        # --- WORK 2 (continued) ---
        # Add wiggle_move() to the chain with an elif, on CIRCLE. It goes
        # ABOVE the else -- the else stays on the bottom.

        # --- WORK 3 (continued) ---
        # Add your own move with one more elif, on SQUARE, above the else.
        # Hand it a real number when you call it.

        time.sleep(0.02)

finally:
    # GIVEN. You wrote this cleanup yourself in P03. brake() stops the
    # wheels, and the lights are still green from when the gamepad
    # connected.
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
