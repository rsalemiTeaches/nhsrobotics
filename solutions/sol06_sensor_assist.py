# Project 06 SOLUTION: Sensor Assist
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
bot = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

MAX_RPM = 45
STOP_DISTANCE = 15

try:
    while True:
        # 1. SENSE
        gamepad.update()
        distance_cm = bot.get_closest_distance()

        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM

        # 2. THINK
        # GOAL 1 version (WORK 1) — simple but traps you at the wall:
        # if distance_cm < STOP_DISTANCE:
        #     left_speed = 0
        #     right_speed = 0
        #     alvik.left_led.set_color(1, 0, 0)
        #     alvik.right_led.set_color(1, 0, 0)
        # else:
        #     alvik.left_led.set_color(0, 1, 0)
        #     alvik.right_led.set_color(0, 1, 0)

        # GOAL 2 version (WORK 2) — block forward only, allow escape:
        if distance_cm < STOP_DISTANCE:
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            if left_speed > 0:
                left_speed = 0
            if right_speed > 0:
                right_speed = 0
        else:
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)

        # 3. ACT
        alvik.set_wheels_speed(left_speed, right_speed)
        time.sleep(0.02)
finally:
    alvik.set_wheels_speed(0, 0)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
