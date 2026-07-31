# Project 04: Button Moves
# GOAL: Learn FUNCTIONS by turning gamepad buttons into pre-programmed moves.
#
# A function is a named block of code you write ONCE and run whenever
# you want, just by calling its name.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p04.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
gamepad = RobotGamepad(alvik)

SPIN_SPEED = 45


# --- FUNCTION DEFINITIONS ---
# Definitions go BEFORE the main loop. Defining a function does not
# run it. It runs when you CALL it, like:  spin_move()

def spin_move():
    """Spin in place to the right for half a second."""
    alvik.set_wheels_speed(SPIN_SPEED, -SPIN_SPEED)
    time.sleep(0.5)
    alvik.set_wheels_speed(0, 0)


# WORK 2: Write a function called  wiggle_move()  that:
#   - drives left wheel only for 0.2 s, then right wheel only for 0.2 s,
#   - repeats that once more (four moves total), then stops the wheels.


# WORK 3: Invent your own third move. Name the function yourself.
# Ideas: reverse escape, victory shimmy, slow creep forward.


try:
    # CANCEL on the robot or OPTIONS on the gamepad ends the run.
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        gamepad.update()

        # WORK 1: When CROSS is pressed, CALL spin_move().
        # Calling a function is its name with parentheses:  spin_move()

        # WORK 2 (continued): map CIRCLE to wiggle_move() with elif.
        # WORK 3 (continued): map SQUARE to your invented move with
        # elif — elif means only one move runs at a time.

        time.sleep(0.02)

finally:
    alvik.brake()
    alvik.stop()
