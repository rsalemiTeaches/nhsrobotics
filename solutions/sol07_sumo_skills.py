# Project 07 SOLUTION: Sumo Skills
from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
gamepad = RobotGamepad(alvik)

MAX_RPM = 45
EDGE_THRESHOLD = 500   # WORK 3: tuned on the classroom ring

try:
    while True:
        # 1. SENSE
        gamepad.update()
        left_line, center_line, right_line = alvik.get_line_sensors()

        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM

        # 2. THINK
        if not gamepad.controller.is_connected():      # WORK 1
            left_speed = 0
            right_speed = 0

        edge_detected = max(left_line, center_line, right_line) < EDGE_THRESHOLD
        if edge_detected:                              # WORK 2
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            if left_speed > 0:
                left_speed = 0
            if right_speed > 0:
                right_speed = 0
        else:
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)

        # FLEX (auto-recover): instead of just blocking forward at the
        # edge, automatically back away:
        # if edge_detected:
        #     alvik.set_wheels_speed(-40, -40)
        #     time.sleep(0.3)
        #     continue

        # 3. ACT
        alvik.set_wheels_speed(left_speed, right_speed)
        time.sleep(0.02)
finally:
    alvik.set_wheels_speed(0, 0)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
