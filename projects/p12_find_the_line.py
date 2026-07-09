# Project 12: Find the Line
# GOAL: Before a robot can FOLLOW a line, it has to FIND one.
#
# The three line sensors read reflectance. Over the bare floor the
# numbers are LOW; over the tape they rise HIGH (same trick as your
# sumo edge guard, P07).
#
#   sb.nav.drive_to_line(speed)   # drive straight until a line is seen

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

LINE_THRESHOLD = 500   # tune on the real course tape
SEARCH_SPEED = 30      # RPM while hunting
LEG_TIME_MS = 2000     # how long to drive one search leg before turning

print("Place the robot anywhere. Press OK to start.")
while not alvik.get_touch_ok():
    time.sleep(0.05)

try:
    # --- GOAL 1: STOP ON THE LINE ---
    # WORK 1: point the robot at the line and call drive_to_line.
    # Then set both LEDs green so we can SEE that the robot knows
    # it arrived.

    # --- GOAL 2 (next class): FIND IT FROM ANYWHERE ---
    # drive_to_line only works if the line happens to be ahead.
    # A real search DRIVES A LEG, CHECKS, TURNS, and tries again —
    # and it must watch the sensors WHILE moving (your P10 timer
    # skill, because drive_distance would block right past the line).
    #
    # WORK 2: build the search loop:
    #   found = False
    #   while not found:
    #       leg_start = time.ticks_ms()
    #       drive forward with alvik.set_wheels_speed(SEARCH_SPEED, SEARCH_SPEED)
    #       inner loop: while ticks_diff(now, leg_start) < LEG_TIME_MS:
    #           read the sensors; if max(...) > LINE_THRESHOLD:
    #               found = True, brake, break
    #       if not found: brake, then sb.nav.rotate_precise(45)
    #
    # WORK 3: when found, stop and celebrate (green LEDs).
    # Test from THREE different starting spots and headings.

    pass  # delete once your code is in

finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
