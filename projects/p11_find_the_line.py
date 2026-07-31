# Project 11: Find the Line
# GOAL: Before a robot can FOLLOW a line, it has to FIND one.
#
# The three line sensors read reflectance. This field is the OPPOSITE
# of the sumo ring. On the sumo ring you watched for the WHITE rim,
# where the numbers drop LOW, and you needed 2 of 3 sensors to agree.
# Here the field is white and the line is BLACK tape, so the numbers
# rise HIGH -- and ANY ONE sensor finding the line is enough.
#
#   sb.nav.drive_to_line(speed)   # drive straight until a line is seen
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p11.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

# FLEX (the A+): there is one. The guide tells you what it is.

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
    # --- WORK 1: STOP ON THE LINE ---
    # WORK 1: point the robot at the line and call drive_to_line.
    # Then set both LEDs green so we can SEE that the robot knows
    # it arrived.

    # --- HANDOFF ---
    # WORK 1 leaves the robot sitting ON the line, which would make
    # WORK 2's search succeed instantly and prove nothing. So we stop
    # and let YOU move the robot somewhere new first. That way one run
    # of this file demos ALL of your work -- you never erase WORK 1.
    print("Line found. Move the robot anywhere, then press OK.")
    while not alvik.get_touch_ok():
        time.sleep(0.05)

    # --- WORK 2-3: FIND IT FROM ANYWHERE ---
    # drive_to_line only works if the line happens to be ahead.
    # A real search DRIVES A LEG, CHECKS, TURNS, and tries again —
    # and it must watch the sensors WHILE moving (your P09 timer
    # skill, because drive_distance would block right past the line).
    #
    # WORK 2: build the search loop:
    #   found = False
    #   while not found and not alvik.get_touch_cancel():
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
