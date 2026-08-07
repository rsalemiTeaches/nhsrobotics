# Project 13: Dodge the Wall
# GOAL: The full Capstone-2 skill — a STATE MACHINE (P10) that follows
# the line (P12), detects an obstacle (P05), drives around it (P08),
# finds the line again (P11), and keeps going.
#
#   FOLLOWING --obstacle close--> AVOIDING --maneuver done--> SEARCHING
#       ^                                                        |
#       +----------------- line found again ---------------------+
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p13.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.

# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# --- STATES ---
STATE_FOLLOWING = 0
STATE_AVOIDING = 1
STATE_SEARCHING = 2

DRIVE_SPEED = 30
OBSTACLE_CM = 12       # WORK 1: tune — far enough to stop cleanly
LINE_THRESHOLD = 500

current_state = STATE_FOLLOWING

print("Robot on the line, obstacle down-course. Press OK.")
while not alvik.get_touch_ok():
    time.sleep(0.05)

try:
    while not alvik.get_touch_cancel():
        time.sleep(0.015)

        if current_state == STATE_FOLLOWING:
            # WORK 1: your P12 code — follow_line, drive,
            # handle line_lost. Then the obstacle check: read
            # sb.get_closest_distance(); when it is closer than
            # OBSTACLE_CM: brake, LEDs red, and change current_state
            # to STATE_AVOIDING.
            pass

        elif current_state == STATE_AVOIDING:
            # WORK 2: the box-around maneuver. Blocking moves
            # are FINE here — nothing else needs attention mid-dodge:
            #   rotate_precise(-90)      # face left, away from the line
            #   drive_distance(20)       # step out of the obstacle's lane
            #   rotate_precise(90)       # face down-course again
            #   drive_distance(35)       # pass the obstacle
            #   rotate_precise(90)       # face back toward the line
            # (If your robot turns the wrong way, flip every sign.)
            # Then change current_state to STATE_SEARCHING.
            pass

        elif current_state == STATE_SEARCHING:
            # WORK 3: drive forward slowly; when
            # max(line sensors) > LINE_THRESHOLD the line is back:
            #   brake
            #   rotate_precise(-90)   # turn down-course along the line
            #   sb.reset_line()       # IMPORTANT: clear old PID memory
            #   current_state = STATE_FOLLOWING
            pass

finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
