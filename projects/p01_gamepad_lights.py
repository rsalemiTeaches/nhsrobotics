# Project 01: Gamepad Lights
# Version: V04
#
# GOAL: Build a robot whose two colored lights change when you press
# buttons on a PS5 controller.
#
# THIS FILE IS MOSTLY EMPTY ON PURPOSE. You type the code yourself, from
# the guide. Copying it by hand is how you learn the shape of Python.
# Count your spaces -- four per level, never a tab.
#
# SETUP ORDER (see the guide for the full version):
#   0. In Thonny, File > Save As -> the Alvik (MicroPython device) -> save
#      this file as /workspace/p01.py. Do all your work on that copy.
#      Files outside /workspace get overwritten when projects update.
#   1. Run this program. Watch Thonny print your robot's WiFi name.
#   2. Connect the Mac to that WiFi network (password: password).
#   3. Open http://192.168.4.1 in Chrome, and KEEP THAT CHROME WINDOW IN
#      FRONT. Chrome blocks gamepad input to any window that is not
#      focused, so clicking over to Thonny stops your buttons working.
#   4. Pair the PS5 controller to the Mac over Bluetooth.
#
# FLEX (the A+): there is one. The guide tells you what it is.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

# --- WORK 1: SET UP THE ROBOT ---
# Copy the four setup lines from the guide and put them right here.
# They start at the left edge, no spaces in front.
#
# Nothing below this will run until you do. Until then Python stops at
# the "while" line and says sb is not defined, which is correct -- you
# have not made it yet.


try:
    # GIVEN: the main loop. Cancel on the robot or Options on the gamepad
    # ends the run, so you never need Thonny's Stop button.
    while not (sb.held('cancel') or gamepad.held('options')):

        # GIVEN: fresh data from the controller. Ask every time through
        # the loop -- skip it and the buttons never change.
        gamepad.update()

        # --- WORK 2: THE BUTTON CHAIN ---
        # Copy the whole if / elif / elif / else chain from the guide and
        # put it right here. Its first line lines up exactly under the
        # "gamepad.update()" line above.

        # GIVEN: a small pause, so the loop does not run away with the
        # processor.
        time.sleep(0.02)

finally:
    # --- WORK 3: CLEAN UP ---
    # This block ALWAYS runs when the program stops, even on a crash.
    # Copy the five shutdown lines from the guide and put them right
    # here, ABOVE the alvik.stop() line.
    #
    # The red flash proves the shutdown ran. A silent stop looks exactly
    # like a crash, and you want to tell them apart.

    alvik.stop()  # GIVEN. You must always call this function to stop the
                  # robot software and free the WiFi network. Without it
                  # the robot can hang and need a restart.
