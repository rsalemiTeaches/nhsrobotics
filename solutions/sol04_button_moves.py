# Project 04 SOLUTION: Button Moves
# Version: V01
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

# WORK 1: the student picks this number. 45 is what the guide prints.
spin_speed = 45

# WORK 2: their own name and their own number.
wiggle_speed = 40


def spin_move():                        # WORK 1, printed in the guide
    """Spin in place, then stop."""
    alvik.set_wheels_speed(spin_speed, -spin_speed)
    time.sleep(0.5)



def wiggle_move():                      # WORK 2, described but not printed
    """Rock side to side twice."""
    for _ in range(2):
        alvik.set_wheels_speed(wiggle_speed, 0)
        time.sleep(0.2)
        alvik.set_wheels_speed(0, wiggle_speed)
        time.sleep(0.2)



def back_up_move(speed):                # WORK 3, one example. Takes an argument.
    """Drive straight back at whatever speed the caller asks for."""
    alvik.set_wheels_speed(-speed, -speed)
    time.sleep(0.4)



# FLEX: one move built entirely out of the other three -- no
# set_wheels_speed of its own -- and it calls the WORK 3 move twice with
# different numbers. Like every other def, it belongs up here.
#
# def combo_move():
#     spin_move()
#     wiggle_move()
#     back_up_move(30)
#     back_up_move(70)


try:
    while not (sb.held('cancel') or gamepad.held('options')):
        gamepad.update()

        # held(), not pressed(): holding the button repeats the move.
        if gamepad.held('cross'):           # WORK 1
            spin_move()
        elif gamepad.held('circle'):        # WORK 2
            wiggle_move()
        elif gamepad.held('square'):        # WORK 3
            back_up_move(60)
        else:
            alvik.brake()

        # FLEX: combo_move() is defined above the try. It hangs off one
        # more elif here.
        #
        # elif gamepad.held('triangle'):
        #     combo_move()

        time.sleep(0.02)

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN, never a WORK item.
