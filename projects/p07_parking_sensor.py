# Project 07: The Parking Sensor
# Version: V01
#
# GOAL: A clock on the screen, a light that blinks faster the closer you
# get, and tank drive -- all running at the same time, and none of them
# ever stopping for the others.
#
# You type the code yourself, from the guide. Thonny does the indenting.
#
# SAVE YOUR COPY FIRST: In Thonny, use File > Save As, pick the Alvik
# (MicroPython device), and save this file as /workspace/p07.py. From
# now on, open and edit THAT copy -- files outside /workspace get
# overwritten whenever the projects are updated.
#
# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

# GIVEN: the robot and the suit. No gamepad yet -- building one makes the
# robot stop and wait for a controller, and WORK 1 and WORK 2 are done
# with the robot in your hand. The gamepad arrives in WORK 3.
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# GIVEN: 70 is as fast as these motors go.
MAX_RPM = 70

# GIVEN: how many milliseconds are in one second.
MS_PER_SECOND = 1000

# GIVEN: how the blink gets its speed. Every centimeter of room buys the
# light 20 more milliseconds of waiting, so far away is slow and close up
# is fast. The two limits stop it going silly at either end.
BLINK_MS_PER_CM = 20
BLINK_MS_FASTEST = 60
BLINK_MS_SLOWEST = 1200

# GIVEN: closer than this and the robot is about to hit something.
TOO_CLOSE_CM = 5.0

# --- YOUR VARIABLES GO HERE ---
# Each WORK step tells you which ones to add. They go here, ABOVE the
# loop, not inside it. A variable made inside the loop is made fresh
# every time through, so it can never remember anything from the time
# before -- and remembering is the whole trick in this project.


try:
    # GIVEN: Cancel on the robot ends the run.
    while not sb.held('cancel'):

        # --- WORK 1: PUT A CLOCK ON THE SCREEN ---
        # Count the seconds since the program started and show the number
        # on the screen -- 0, then 1, then 2, and on up. Write the screen
        # only when the number actually changes, not every time through.
        # The guide has the lines. Copy them in where the "pass" line is,
        # then delete the "pass" line.
        pass

        # --- WORK 2: BLINK FASTER AS YOU GET CLOSER ---
        # Ask the distance sensor how much room is in front of the robot,
        # turn that into a waiting time, and blink both top lights on
        # and off at that speed. Hold the robot in your hand and walk it at a
        # wall. The clock from WORK 1 must keep counting the whole time.

        # --- WORK 3: DRIVE IT ---
        # Go back to your own P03 file and copy your tank drive out of
        # it. Same two sticks, same two wheels. The clock keeps counting
        # and the light keeps blinking while you drive.
        # You also need one new line above the loop to build the gamepad.
        # The guide says which, and where.

        # GIVEN: a tiny yield, so the robot's own background work gets a
        # turn. It is NOT what times anything you are about to write --
        # your clock and your blink each keep their own time.
        time.sleep_ms(10)

finally:
    # GIVEN. A crash must never leave the wheels running or a light on.
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN. Always call this. It stops the robot software
                  # and frees the WiFi network. Without it the robot can
                  # hang and need a restart.
