# Project 04 SOLUTION: Move With Code
# Version: V01
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)


# WORK 2. Printed in the guide, character for character.
# Out, about-face, back, about-face. Ends where it started.
def patrol():
    alvik.move(40)
    alvik.rotate(180)
    alvik.move(40)
    alvik.rotate(180)


# WORK 3. NOT printed. The guide teaches the argument on patrol(distance)
# and the for loop on a bare square, and the student assembles the two.
def square(side):
    for _ in range(4):
        alvik.move(side)
        alvik.rotate(90)


# FLEX: the taped course, as one more function on the DOWN pad. Every
# class will tape a different one; this is the shape of the answer.
#
# def course():
#     alvik.move(50)
#     alvik.rotate(-45)
#     alvik.move(70)
#     alvik.rotate(90)
#     alvik.move(40)


try:
    while not sb.held('cancel'):

        # pressed(), not held(): each move finishes on its own, so one
        # touch should mean one move.
        if sb.pressed('up'):            # WORK 1
            alvik.move(30)
            alvik.rotate(90)
        elif sb.pressed('left'):        # WORK 2
            patrol()
        elif sb.pressed('right'):       # WORK 3
            square(30)

        # FLEX: elif sb.pressed('down'):
        #           course()

        time.sleep(0.02)

finally:
    alvik.brake()
    alvik.stop()  # GIVEN, never a WORK item.
