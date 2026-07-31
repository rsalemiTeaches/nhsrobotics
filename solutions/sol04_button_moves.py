# Project 04 SOLUTION: Button Moves
from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
gamepad = RobotGamepad(alvik)

SPIN_SPEED = 45


def spin_move():
    """Spin in place to the right for half a second."""
    alvik.set_wheels_speed(SPIN_SPEED, -SPIN_SPEED)
    time.sleep(0.5)
    alvik.set_wheels_speed(0, 0)


def wiggle_move():                       # WORK 2
    """Rock side to side."""
    for _ in range(2):
        alvik.set_wheels_speed(SPIN_SPEED, 0)
        time.sleep(0.2)
        alvik.set_wheels_speed(0, SPIN_SPEED)
        time.sleep(0.2)
    alvik.set_wheels_speed(0, 0)


def escape_move():                       # WORK 3 (example invented move)
    """Back up fast, then spin to face a new direction."""
    alvik.set_wheels_speed(-60, -60)
    time.sleep(0.4)
    alvik.set_wheels_speed(SPIN_SPEED, -SPIN_SPEED)
    time.sleep(0.3)
    alvik.set_wheels_speed(0, 0)


try:
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        gamepad.update()

        if gamepad.buttons['cross']:         # WORK 1
            spin_move()
        elif gamepad.buttons['circle']:      # WORK 2 (continued)
            wiggle_move()
        elif gamepad.buttons['square']:      # WORK 3 (continued)
            escape_move()

        # FLEX: combo move — a new function that CALLS the other
        # functions in sequence and flashes the LEDs between them:
        # def combo_move():
        #     alvik.left_led.set_color(1, 0, 1)
        #     spin_move()
        #     alvik.right_led.set_color(0, 1, 1)
        #     wiggle_move()
        #     alvik.left_led.set_color(0, 0, 0)
        #     alvik.right_led.set_color(0, 0, 0)
        # ...mapped to triangle.

        time.sleep(0.02)
finally:
    alvik.set_wheels_speed(0, 0)
    alvik.stop()
