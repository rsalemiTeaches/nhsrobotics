# Project 15 SOLUTION: Race Prep  (requires nhs_robotics V03)
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

STATE_MANUAL = 0
STATE_FOLLOWING = 1
STATE_AVOIDING = 2
STATE_SEARCHING = 3
STATE_FINISHED = 4

DRIVE_SPEED = 40       # WORK 1: race-tuned from P13
OBSTACLE_CM = 12
LINE_THRESHOLD = 500
SEARCH_SPEED = 20
MAX_RPM = 45

current_state = STATE_MANUAL
run_start_time = 0

try:
    while not alvik.get_touch_cancel():
        time.sleep(0.015)
        gamepad.update()

        if current_state == STATE_MANUAL:
            left_speed = gamepad.left_y * MAX_RPM        # WORK 2
            right_speed = gamepad.right_y * MAX_RPM
            if not gamepad.controller.is_connected():
                left_speed = 0
                right_speed = 0
            alvik.set_wheels_speed(left_speed, right_speed)
            alvik.left_led.set_color(0, 0, 1)            # blue = manual
            alvik.right_led.set_color(0, 0, 1)

            if gamepad.buttons['triangle']:              # WORK 3
                alvik.brake()
                run_start_time = time.ticks_ms()
                sb.reset_line()
                print("LAUNCH!")
                current_state = STATE_FOLLOWING

        elif current_state == STATE_FOLLOWING:
            left, center, right = alvik.get_line_sensors()
            if max(left, center, right) < LINE_THRESHOLD:      # WORK 5
                alvik.brake()
                elapsed = time.ticks_diff(time.ticks_ms(), run_start_time) / 1000
                print("FINISH! Time:", elapsed, "seconds")
                current_state = STATE_FINISHED
                continue

            left_speed, right_speed = sb.follow_line(DRIVE_SPEED)  # WORK 4
            if sb.line_lost:
                alvik.brake()
            else:
                alvik.left_led.set_color(0, 1, 0)
                alvik.right_led.set_color(0, 1, 0)
                alvik.set_wheels_speed(left_speed, right_speed)

            if sb.get_closest_distance() < OBSTACLE_CM:
                alvik.brake()
                alvik.left_led.set_color(1, 0, 0)
                alvik.right_led.set_color(1, 0, 0)
                current_state = STATE_AVOIDING

        elif current_state == STATE_AVOIDING:                    # WORK 6
            sb.nav.rotate_precise(-90)   # LEFT dodge — race rule!
            sb.nav.drive_distance(20)
            sb.nav.rotate_precise(90)
            sb.nav.drive_distance(35)
            sb.nav.rotate_precise(90)
            current_state = STATE_SEARCHING

        elif current_state == STATE_SEARCHING:                   # WORK 7
            alvik.set_wheels_speed(SEARCH_SPEED, SEARCH_SPEED)
            left, center, right = alvik.get_line_sensors()
            if min(left, center, right) < LINE_THRESHOLD:
                alvik.brake()
                sb.nav.rotate_precise(-90)
                sb.reset_line()
                current_state = STATE_FOLLOWING

        elif current_state == STATE_FINISHED:
            # non-blocking green victory alternation
            phase = (time.ticks_ms() // 250) % 2
            if phase == 0:
                alvik.left_led.set_color(0, 1, 0)
                alvik.right_led.set_color(0, 0, 0)
            else:
                alvik.left_led.set_color(0, 0, 0)
                alvik.right_led.set_color(0, 1, 0)

        # FLEX (gamepad override): in any autonomous state, pressing
        # SQUARE bails out to STATE_MANUAL (brake first). From MANUAL,
        # TRIANGLE re-launches — reset_line() makes re-entry clean.
        # (In the race, an override counts as a rescue.)

finally:
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
