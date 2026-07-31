# Project 12 SOLUTION: Follow the Line  (requires nhs_robotics V03)
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

DRIVE_SPEED = 40   # WORK 3: tuned; 25 = safe, ~40-45 = race pace

print("Place the robot ON the line. Press OK to start.")
while not alvik.get_touch_ok():
    time.sleep(0.05)

try:
    while not alvik.get_touch_cancel():
        time.sleep(0.015)

        left_speed, right_speed = sb.follow_line(DRIVE_SPEED)   # WORK 1

        if sb.line_lost:                                         # WORK 2
            alvik.brake()
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            continue

        alvik.left_led.set_color(0, 1, 0)
        alvik.right_led.set_color(0, 1, 0)
        alvik.set_wheels_speed(left_speed, right_speed)

        # FLEX (speed zones): read the center sensor's recent history —
        # if the correction has been small for a while (straightaway),
        # temporarily raise the base speed; drop it when corrections
        # grow (curve ahead). Simplest version: track
        # abs(left_speed - right_speed) and pick fast/slow base speed.
finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
