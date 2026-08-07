# Project 03: Gamepad Driving (Tank Drive)
# Version: V04
#
# GOAL: Drive your robot with the two sticks. Left stick = left wheel,
# right stick = right wheel.
#
# You type the code yourself, from the guide. Thonny does the indenting.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p03.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

# GIVEN: the robot, the suit and the gamepad. You typed these yourself in
# P01. From here on they come with the file.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

# GIVEN: 70 is as fast as these motors go.
MAX_RPM = 70

try:
    # GIVEN: the main loop. Cancel on the robot or Options on the gamepad
    # ends the run.
    while not (sb.held('cancel') or gamepad.held('options')):

        # GIVEN: fresh data from the controller. Ask every time through
        # the loop -- skip it and the sticks never change.
        gamepad.update()

        # --- WORK 1: LOOK AT THE STICKS ---
        # Before you drive anything, find out what the sticks actually
        # report. The guide gives you an "if" that fires once each time
        # you press X, and a line under it that prints both stick values.
        # Copy them here. Run it and write the numbers down.

        # --- WORK 2: DRIVE ---
        # The sticks report -1.0 to +1.0. The motors want RPM. Copy the
        # two lines from the guide that do that conversion, and the line
        # under them that sends both speeds to the wheels.

        # GIVEN: a small pause, so the loop does not run away with the
        # processor.
        time.sleep(0.02)

finally:
    # --- WORK 3: CLEAN UP ---
    # A crashed program must NEVER leave the motors running, and the
    # gamepad left both lights green when it connected. Copy the two
    # lines from the guide that stop the wheels and clear the lights.
    # They go ABOVE the alvik.stop() line.

    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
