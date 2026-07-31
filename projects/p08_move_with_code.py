# Project 08: Move With Code
# GOAL: Welcome to AUTOMATION. No gamepad this time. The robot
# moves because your CODE says exactly where to go.
#
# SuperBot gives you two precision commands:
#   sb.nav.drive_distance(30)     # drive forward 30 cm, then stop
#   sb.nav.rotate_precise(90)     # turn 90 degrees in place
# Each command FINISHES before the next line runs (it "blocks").
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p08.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

print("Place the robot at the start mark. Press OK to go.")
while not alvik.get_touch_ok():
    time.sleep(0.05)

try:
    # --- WORK 1-2: DRIVE A SQUARE ---
    # WORK 1: drive one side of a square: forward 30 cm, then turn 90.

    # WORK 2: a square is that same pair of moves FOUR times.
    # Don't copy-paste four times — use a loop:
    #     for _ in range(4):
    # (Put your WORK 1 lines inside it, indented.)

    # --- WORK 3: DRIVE THE TAPED COURSE ---
    # WORK 3: the classroom floor has a taped course with measured
    # sides and marked angles. Write the sequence of drive_distance
    # and rotate_precise calls that takes the robot from START to
    # FINISH. Measure twice, code once!

    print("Route complete.")

finally:
    alvik.brake()
    alvik.stop()
