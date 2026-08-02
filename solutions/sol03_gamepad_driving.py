# Project 03 SOLUTION: Gamepad Driving (Tank Drive)
# Version: V03
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

MAX_RPM = 70                            # GIVEN, the motor ceiling

try:
    while not (sb.held('cancel') or gamepad.held('options')):
        gamepad.update()

        # WORK 1: one reading per press, not one per loop.
        if gamepad.pressed('cross'):
            sb.log_info(gamepad.left_y, gamepad.right_y)

        # WORK 2: stick value times the speed limit, straight to the wheels.
        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM
        alvik.set_wheels_speed(left_speed, right_speed)

        # FLEX: each LED reports its own wheel. Green forward, red back,
        # white stopped. The stick properties zero a resting stick, so the
        # else branch is exact and needs no threshold. Right side is the
        # same three branches against right_speed.
        #
        # if left_speed > 0:
        #     alvik.left_led.set_color(0, 1, 0)
        # elif left_speed < 0:
        #     alvik.left_led.set_color(1, 0, 0)
        # else:
        #     alvik.left_led.set_color(1, 1, 1)

        time.sleep(0.02)

finally:
    alvik.brake()                       # WORK 3
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN, never a WORK item.
