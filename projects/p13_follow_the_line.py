# Project 13: Follow the Line
# GOAL: Follow the taped course using SuperBot's PID line follower.
#
# REQUIRES nhs_robotics V03 on the robot (ask your teacher if you see
# an AttributeError on follow_line).
#
# You call it every loop tick with a base speed; it hands back the two
# wheel speeds that keep you on the line:
#     left_speed, right_speed = sb.follow_line(DRIVE_SPEED)
# You do NOT write the PID math — your job is everything around it.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p13.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# WORK 3 (Goal 2): raise this until laps get unreliable, then back off.
# Keep it 50 or below — the motors max out at 70 RPM, and the PID
# needs headroom to speed up the outside wheel in curves.
DRIVE_SPEED = 25

print("Place the robot ON the line. Press OK to start.")
while not alvik.get_touch_ok():
    time.sleep(0.05)

try:
    while not alvik.get_touch_cancel():
        time.sleep(0.015)

        # WORK 1: get the two wheel speeds from sb.follow_line and
        # send them to the wheels.

        # WORK 2: SAFETY — if sb.line_lost is True, brake and turn the
        # LEDs red, then `continue` (skip driving this tick). When the
        # line is back, LEDs green.

finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
