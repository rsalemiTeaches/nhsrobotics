# Project 01 SOLUTION: Gamepad Lights
# Version: V01
from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
gamepad = RobotGamepad(alvik)

try:
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        gamepad.update()

        if gamepad.buttons['cross']:              # WORK 1
            alvik.left_led.set_color(0, 0, 1)
            alvik.right_led.set_color(0, 0, 1)
        elif gamepad.buttons['circle']:           # WORK 2
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
        elif gamepad.buttons['triangle']:         # WORK 2 (continued)
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
        elif gamepad.buttons['square']:           # FLEX
            alvik.left_led.set_color(1, 0, 1)     # magenta
            alvik.right_led.set_color(0, 1, 1)    # cyan
        else:                                     # WORK 1 (continued)
            alvik.left_led.set_color(1, 1, 1)     # white = alive, waiting
            alvik.right_led.set_color(1, 1, 1)

        time.sleep(0.02)

finally:
    # WORK 3: the red flash proves the shutdown ran, then go dark.
    alvik.left_led.set_color(1, 0, 0)
    alvik.right_led.set_color(1, 0, 0)
    time.sleep(0.5)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()  # GIVEN, never a WORK item. Always call this to stop the
                  # robot software and free the WiFi network. Without it
                  # the robot can hang and need a restart.
