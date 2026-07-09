# Project 15: Race Prep
# GOAL: Turn your P14 dodge-bot into a RACE robot for Capstone 2.
#
# Three upgrades:
#   1. A MANUAL state: drive to the start line with the gamepad, then
#      press TRIANGLE to launch the autonomous run. (Term 2 stays
#      blended: human for setup, robot for the race.)
#   2. A FINISH detector: the finish line is a bar of tape ACROSS the
#      course. Following the line, only the CENTER sensor reads high —
#      but on a perpendicular bar, ALL THREE read high at once.
#   3. A race timer: qualifying is about the clock.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

# --- STATES ---
STATE_MANUAL = 0
STATE_FOLLOWING = 1
STATE_AVOIDING = 2
STATE_SEARCHING = 3
STATE_FINISHED = 4

# --- TUNED VALUES (WORK 1: copy your best P13/P14 numbers) ---
DRIVE_SPEED = 30
OBSTACLE_CM = 12
LINE_THRESHOLD = 500
SEARCH_SPEED = 20
MAX_RPM = 45           # manual-mode speed limit

current_state = STATE_MANUAL
run_start_time = 0

try:
    # CANCEL on the robot or OPTIONS on the gamepad ends the run.
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        time.sleep(0.015)
        gamepad.update()

        if current_state == STATE_MANUAL:
            # WORK 2: tank drive (your P03 code) so you can place the
            # robot on the start line. Include the link-loss guard.

            # WORK 3: when TRIANGLE is pressed: record the start time
            #   run_start_time = time.ticks_ms()
            # call sb.reset_line(), and launch:
            #   current_state = STATE_FOLLOWING
            pass

        elif current_state == STATE_FOLLOWING:
            # WORK 4: your P14 FOLLOWING state (follow_line + line_lost
            # safety + obstacle check -> STATE_AVOIDING).

            # WORK 5: FINISH DETECTION — read the line sensors; if ALL
            # THREE are above LINE_THRESHOLD at once, that's the finish
            # bar: brake, print the elapsed time in seconds
            #   time.ticks_diff(time.ticks_ms(), run_start_time) / 1000
            # and go to STATE_FINISHED.
            pass

        elif current_state == STATE_AVOIDING:
            # WORK 6: your P14 box-around maneuver -> STATE_SEARCHING.
            # RACE RULE: everyone must dodge to the LEFT, so two robots
            # meeting head-on pass each other safely.
            pass

        elif current_state == STATE_SEARCHING:
            # WORK 7: your P14 search -> reset_line() -> STATE_FOLLOWING
            pass

        elif current_state == STATE_FINISHED:
            # Victory lights! Alternate the LEDs green (non-blocking,
            # P10 style). The run is over; only CANCEL exits.
            pass

finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
