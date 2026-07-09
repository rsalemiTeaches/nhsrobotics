# Project 03: Gamepad Driving (Tank Drive)
# GOAL: Drive your robot with the two sticks. Left stick = left wheel,
# right stick = right wheel.
#
# THE MATH: each stick reports -1.0 (full back) to +1.0 (full forward).
# The motors want RPM. So:   target_rpm = stick_value * MAX_RPM

from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
gamepad = RobotGamepad(alvik)

# WORK 3 (Goal 2): this speed limit is deliberately silly-slow.
# Find a value that is fast but still controllable.
MAX_RPM = 1

try:
    while True:
        gamepad.update()

        # WORK 1: Calculate each wheel's speed.
        # The stick values are:  gamepad.left_y  and  gamepad.right_y
        left_speed = 0    # <-- replace 0 with the math
        right_speed = 0   # <-- replace 0 with the math

        # WORK 2: Send the speeds to the wheels.
        # The command is:  alvik.set_wheels_speed(left_speed, right_speed)

        time.sleep(0.02)

finally:
    # WORK 4 (Goal 2): a crashed program must NEVER leave motors running.
    # Stop the wheels, turn LEDs off, and call alvik.stop() here.
    pass
