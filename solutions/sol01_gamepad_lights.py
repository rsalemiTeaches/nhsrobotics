# Project 01 SOLUTION: Gamepad Lights
from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
gamepad = RobotGamepad(alvik)

try:
    while True:
        gamepad.update()

        if gamepad.buttons['cross']:            # WORK 1
            alvik.left_led.set_color(0, 0, 1)
            alvik.right_led.set_color(0, 0, 1)
        elif gamepad.buttons['circle']:          # WORK 2
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
        elif gamepad.buttons['triangle']:        # WORK 3
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
        else:                                    # WORK 4
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)

        # FLEX: SQUARE makes a two-color light show (left magenta, right cyan,
        # or an alternating pattern using time.ticks_ms()).
        time.sleep(0.02)
finally:
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
