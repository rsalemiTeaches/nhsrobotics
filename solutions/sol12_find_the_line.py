# Project 12 SOLUTION: Find the Line
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

LINE_THRESHOLD = 500
SEARCH_SPEED = 30
LEG_TIME_MS = 2000

print("Place the robot anywhere. Press OK to start.")
while not alvik.get_touch_ok():
    time.sleep(0.05)

try:
    # GOAL 1 (WORK 1) — line straight ahead:
    # sb.nav.drive_to_line(15)
    # alvik.left_led.set_color(0, 1, 0)
    # alvik.right_led.set_color(0, 1, 0)

    # GOAL 2 (WORK 2-3) — search from anywhere:
    found = False
    while not found and not alvik.get_touch_cancel():
        leg_start = time.ticks_ms()
        alvik.set_wheels_speed(SEARCH_SPEED, SEARCH_SPEED)
        while time.ticks_diff(time.ticks_ms(), leg_start) < LEG_TIME_MS:
            left, center, right = alvik.get_line_sensors()
            if max(left, center, right) > LINE_THRESHOLD:
                found = True
                alvik.brake()
                break
            time.sleep(0.01)
        if not found:
            alvik.brake()
            sb.nav.rotate_precise(45)   # new heading, try again

    if found:                            # WORK 3
        alvik.left_led.set_color(0, 1, 0)
        alvik.right_led.set_color(0, 1, 0)
        print("Line found!")

    # FLEX (spiral search): make LEG_TIME_MS grow a little every leg
    # (e.g. LEG_TIME_MS += 300) so the robot sweeps outward instead of
    # circling one spot.
finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
