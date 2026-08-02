# Project 03: Gamepad Driving (Tank Drive)
# Version: V02
#
# GOAL: Drive your robot with the two sticks. Left stick = left wheel,
# right stick = right wheel.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p03.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad, Button
import time

alvik = ArduinoAlvik()
alvik.begin()

# GIVEN: SuperBot wraps the robot and adds tools. This project uses one
# of them, sb.log_info(). In later projects you make it yourself.
sb = SuperBot(alvik)

gamepad = RobotGamepad(alvik)


def x_is_down():
    """GIVEN: True the whole time X is held down."""
    return gamepad.buttons['cross']


# GIVEN: btn_x.is_pressed() is True only at the INSTANT X goes down, so
# one press gives you one reading instead of a hundred.
btn_x = Button(x_is_down)

# GIVEN: 70 is the fastest the motors go.
MAX_RPM = 70

try:
    # CANCEL on the robot or OPTIONS on the gamepad ends the run.
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        gamepad.update()

        # --- WORK 1: LOOK AT THE STICKS ---
        # Press X to take one reading of both sticks:
        #
        #   if btn_x.is_pressed():
        #       sb.log_info(gamepad.left_y, gamepad.right_y)
        #
        # Push a stick all the way and press X. Push it halfway and press
        # X. Let go and press X. Write down all three numbers.

        # --- WORK 2: DRIVE ---
        # Turn each stick value into a wheel speed, then send both to the
        # wheels:
        #
        #   left_speed = gamepad.left_y * MAX_RPM
        #   right_speed = gamepad.right_y * MAX_RPM
        #   alvik.set_wheels_speed(left_speed, right_speed)

        time.sleep(0.02)

finally:
    # WORK 3: a crashed program must NEVER leave motors running.
    # Write your cleanup ABOVE the alvik.stop() line below:
    #   1. alvik.brake()                  stop the wheels
    #   2. turn both LEDs off             set_color(0, 0, 0) on each
    # Every project that moves motors ends this way.

    alvik.stop()  # Always call this. It stops the robot software and
                  # frees the WiFi network. Without it the robot can
                  # hang and need a restart.
