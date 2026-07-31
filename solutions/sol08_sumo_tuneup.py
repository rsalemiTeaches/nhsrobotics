# Project 08 SOLUTION: Sumo Tune-Up (tournament-ready reference)
from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
gamepad = RobotGamepad(alvik)

MAX_RPM = 55            # WORK 1: competitive but controllable
EDGE_THRESHOLD = 500

SPIN_SPEED = 60


def spin_attack():      # FLEX
    """Quarter-second spin to shake off an attacker."""
    alvik.set_wheels_speed(SPIN_SPEED, -SPIN_SPEED)
    time.sleep(0.25)
    alvik.set_wheels_speed(0, 0)


print("SELF-CHECK: line sensors =", alvik.get_line_sensors())
for _ in range(3):
    alvik.left_led.set_color(0, 1, 0)
    alvik.right_led.set_color(0, 1, 0)
    time.sleep(0.15)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    time.sleep(0.15)
print("SELF-CHECK complete. Waiting for gamepad.")

try:
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        # 1. SENSE
        gamepad.update()
        left_line, center_line, right_line = alvik.get_line_sensors()

        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM

        # 2. THINK
        if not gamepad.controller.is_connected():   # WORK 2
            left_speed = 0
            right_speed = 0

        # 2-of-3 rule: the MIDDLE (median) reading below the threshold
        # means at least two sensors see the white boundary.
        sorted_sensors = sorted((left_line, center_line, right_line))
        edge_detected = sorted_sensors[1] < EDGE_THRESHOLD
        if edge_detected:                            # WORK 3
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            if left_speed > 0:
                left_speed = 0
            if right_speed > 0:
                right_speed = 0
        else:
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)

        if gamepad.buttons['R1']:                    # FLEX
            spin_attack()

        # 3. ACT
        alvik.set_wheels_speed(left_speed, right_speed)
        time.sleep(0.02)
finally:
    alvik.set_wheels_speed(0, 0)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
