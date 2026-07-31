# Project 07: Sumo Skills
# GOAL: Make your driving robot SURVIVE. A sumo bot that drives off the
# ring edge or keeps rolling when the WiFi drops loses instantly.
#
# You are combining three things you already know:
#   P03 tank driving  +  P06 sensor override  +  a new sensor (line sensors)

from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
gamepad = RobotGamepad(alvik)

MAX_RPM = 45

# The ring floor is dark; the boundary is a white edge. The three line
# sensors read LOW numbers over the white edge.
# WORK 3 (Goal 2): tune this on the real ring until edge detection is
# reliable but doesn't trigger in the middle.
EDGE_THRESHOLD = 500

try:
    # CANCEL on the robot or OPTIONS on the gamepad ends the run.
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        # --- 1. SENSE ---
        gamepad.update()
        left_line, center_line, right_line = alvik.get_line_sensors()

        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM

        # --- 2. THINK ---
        # WORK 1: LINK-LOSS GUARD. If the gamepad link is gone, the
        # robot must not keep driving on old stick values.
        # The check is:   gamepad.controller.is_connected()
        # If it returns False: force both speeds to 0.

        # WORK 2: EDGE GUARD. Build a True/False variable using the
        # 2-of-3 rule (the MIDDLE reading below the threshold means at
        # least two sensors see white):
        #   sorted_sensors = sorted((left_line, center_line, right_line))
        #   edge_detected = sorted_sensors[1] < EDGE_THRESHOLD
        # When the edge is detected: block FORWARD driving (positive
        # speeds only, like P06) and turn the LEDs red. Reverse must
        # stay allowed — backing away from the edge is how you survive!

        # --- 3. ACT ---
        alvik.set_wheels_speed(left_speed, right_speed)
        time.sleep(0.02)

finally:
    alvik.set_wheels_speed(0, 0)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
