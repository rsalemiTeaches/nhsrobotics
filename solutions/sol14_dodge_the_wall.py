# Project 14 SOLUTION: Dodge the Wall  (requires nhs_robotics V03)
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

STATE_FOLLOWING = 0
STATE_AVOIDING = 1
STATE_SEARCHING = 2

DRIVE_SPEED = 30
OBSTACLE_CM = 12
LINE_THRESHOLD = 500
SEARCH_SPEED = 20

current_state = STATE_FOLLOWING

print("Robot on the line, obstacle down-course. Press OK.")
while not alvik.get_touch_ok():
    time.sleep(0.05)

try:
    while not alvik.get_touch_cancel():
        time.sleep(0.015)

        if current_state == STATE_FOLLOWING:
            left_speed, right_speed = sb.follow_line(DRIVE_SPEED)  # WORK 1
            if sb.line_lost:
                alvik.brake()
            else:
                alvik.left_led.set_color(0, 1, 0)
                alvik.right_led.set_color(0, 1, 0)
                alvik.set_wheels_speed(left_speed, right_speed)

            if sb.get_closest_distance() < OBSTACLE_CM:            # WORK 1 (continued)
                alvik.brake()
                alvik.left_led.set_color(1, 0, 0)
                alvik.right_led.set_color(1, 0, 0)
                print("Obstacle! Avoiding.")
                current_state = STATE_AVOIDING

        elif current_state == STATE_AVOIDING:                      # WORK 2
            sb.nav.rotate_precise(-90)
            sb.nav.drive_distance(20)
            sb.nav.rotate_precise(90)
            sb.nav.drive_distance(35)
            sb.nav.rotate_precise(90)
            print("Maneuver done. Searching for the line.")
            current_state = STATE_SEARCHING

        elif current_state == STATE_SEARCHING:                     # WORK 3
            alvik.set_wheels_speed(SEARCH_SPEED, SEARCH_SPEED)
            left, center, right = alvik.get_line_sensors()
            if max(left, center, right) > LINE_THRESHOLD:
                alvik.brake()
                sb.nav.rotate_precise(-90)
                sb.reset_line()
                print("Line reacquired. Following.")
                current_state = STATE_FOLLOWING

        # FLEX (smart dodge): before committing left, compare the five
        # distance readings — dodge toward the side with more room:
        # d = alvik.get_distance(); left side = d[0]+d[1], right = d[3]+d[4].
finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
