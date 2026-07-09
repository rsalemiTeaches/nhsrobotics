# Project 04: Button Moves
# GOAL: Learn FUNCTIONS by turning gamepad buttons into pre-programmed moves.
#
# A function is a named block of code you write ONCE and run whenever
# you want, just by calling its name.

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
    while True:
        gamepad.update()

        # WORK 1: When CROSS is pressed, CALL spin_move().
        # Calling a function is its name with parentheses:  spin_move()

        # WORK 4: Map CIRCLE to wiggle_move() and SQUARE to your
        # invented move. Use elif so only one move runs at a time.

        time.sleep(0.02)

finally:
    alvik.set_wheels_speed(0, 0)
    alvik.stop()
