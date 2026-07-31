# Project 03: Gamepad Driving (Tank Drive)
# GOAL: Drive your robot with the two sticks. Left stick = left wheel,
# right stick = right wheel.
#
# THE MATH: each stick reports -1.0 (full back) to +1.0 (full forward).
# The motors want RPM. So:   target_rpm = stick_value * MAX_RPM
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p03.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
gamepad = RobotGamepad(alvik)

# WORK 2 (Goal 2): this speed limit is deliberately silly-slow.
# Find a value that is fast but still controllable.
MAX_RPM = 1

try:
    # CANCEL on the robot or OPTIONS on the gamepad ends the run.
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        gamepad.update()

        # WORK 1: Calculate each wheel's speed, then send the speeds
        # to the wheels. The stick values are gamepad.left_y and
        # gamepad.right_y; the drive command is:
        #     alvik.set_wheels_speed(left_speed, right_speed)
        left_speed = 0    # <-- replace 0 with the math
        right_speed = 0   # <-- replace 0 with the math

        time.sleep(0.02)

finally:
    # WORK 3 (Goal 2): a crashed program must NEVER leave motors running.
    # Stop the wheels, turn LEDs off, and call alvik.stop() here.
    pass
