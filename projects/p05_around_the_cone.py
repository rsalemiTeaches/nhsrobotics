# Project 05: Around the Cone
# Version: V01
#
# GOAL: Drive the course. Out of the start box, around the cone, down the
# other side, and into the parking space -- on its own, in one trip, with
# no cable and nobody touching it.
#
# You type the code yourself, from the guide. Thonny does the indenting.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p05.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# The name matters. main.py looks for p05.py by name, so /workspace/p05.py
# is the only spelling that works.
#
# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# GIVEN: the robot and the suit.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# GIVEN: your own forward speed. Work it out from your student number --
# the guide shows you how -- and type it in here. Nobody else has this
# number, so nobody else has your answers.
MY_SPEED_CMS = 0.0

# Your other numbers go here, one at a time, as the guide asks for them.


try:
    # GIVEN: the wait-for-OK loop, the same one you typed in P04. Both
    # lights flash until somebody holds a pad. Cancel quits, OK runs the
    # course. You already know how this works, so this time it is a gift.
    while not sb.held('cancel'):
        sb.light_both_leds(1, 1, 1)
        time.sleep(0.25)
        sb.light_both_leds(0, 0, 0)
        time.sleep(0.25)

        if sb.held('ok'):

            # --- WORK 1: DRIVE OUT TO THE CONE ---
            # Start the robot moving straight at your own speed, and let
            # it run for a while. Then tune "a while" until the robot
            # stops level with the cone. Copy the lines in from the guide
            # where the "pass" line is, then delete the "pass" line.
            pass

            # --- WORK 2: CURVE AROUND THE CONE ---
            # The new one. Call drive() again, this time with a turning
            # speed in the second spot as well as a forward speed. Two
            # numbers to find here: how hard to turn, and how long to
            # keep turning. The guide says which to get right first.
            #
            # No brake between the legs. The robot rolls out of the
            # straight and into the curve without stopping.

            # --- WORK 3: DRIVE INTO THE PARKING BOX ---
            # Straight again, like WORK 1, until the robot is parked
            # inside the lines.

            # GIVEN: the course is over, so stop the wheels.
            alvik.brake()

finally:
    # GIVEN. A crash partway through a leg must never leave the wheels
    # running.
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
