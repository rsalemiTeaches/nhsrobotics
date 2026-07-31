# Project 03 SOLUTION: Gamepad Driving (Tank Drive)
from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
gamepad = RobotGamepad(alvik)

MAX_RPM = 45   # WORK 2: 40-60 is competitive and controllable

try:
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        gamepad.update()

        left_speed = gamepad.left_y * MAX_RPM      # WORK 1
        right_speed = gamepad.right_y * MAX_RPM

        alvik.set_wheels_speed(left_speed, right_speed)  # WORK 1 (continued)

        # FLEX (slow-mode toggle): hold R1 to halve the speed:
        # if gamepad.buttons['R1']:      # NOTE: 'R1' is capitalized
        #     left_speed = left_speed * 0.5
        #     right_speed = right_speed * 0.5

        time.sleep(0.02)
finally:
    alvik.brake()                                  # WORK 3
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
