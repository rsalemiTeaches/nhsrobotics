# Project 01: Gamepad Lights
# Version: V01
#
# GOAL: Build a robot whose headlights change color when you press
# buttons on a PS5 controller.
#
# You do NOT need to understand every line yet. Find the # WORK comments.
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
from nhs_robotics import RobotGamepad
import time

# --- SETUP ---
alvik = ArduinoAlvik()
alvik.begin()

# RobotGamepad creates the WiFi network and WAITS here (blinking yellow)
# until the browser connects. Then the LEDs turn green.
gamepad = RobotGamepad(alvik)

try:
    # --- MAIN LOOP ---
    # CANCEL on the robot or OPTIONS on the gamepad ends the run.
    while not (alvik.get_touch_cancel() or gamepad.buttons['options']):
        # Ask the gamepad for fresh data. This must happen EVERY loop.
        gamepad.update()

        # WORK 1: When the CROSS (X) button is held, make BOTH LEDs blue.
        # The buttons dictionary works like this:
        #     gamepad.buttons['cross']  -> True while held, False otherwise
        # An LED is set like this:
        #     alvik.left_led.set_color(red, green, blue)   # each 0 or 1
        if gamepad.buttons['cross']:
            pass  # <-- replace with two set_color lines (left and right)

        # WORK 2: Add two elif branches right here, between the if above
        # and the else below.
        #   Hold CIRCLE   -> both LEDs red
        #   Hold TRIANGLE -> both LEDs green
        # Do WORK 1 first. Without the else below, the LEDs stay stuck on
        # after your first press and you cannot tell what is happening.

        # WORK 1 (continued): When NO button is held, turn both LEDs
        # WHITE (1, 1, 1), not off. White means "running, waiting for a
        # button", so you can tell a waiting robot from a frozen one.
        else:
            pass  # <-- replace with two set_color(1, 1, 1) lines

        time.sleep(0.02)  # small pause keeps the loop stable

finally:
    # This block ALWAYS runs when the program stops, even on a crash.
    #
    # WORK 3: clean up, in this order.
    #   1. Turn both LEDs red.
    #   2. time.sleep(0.5)
    #   3. Turn both LEDs off.
    #
    # The red flash proves the shutdown ran. A silent stop looks exactly
    # like a crash, and you want to tell them apart.
    alvik.stop() # You must always call this function 
                 # to stop the robot software
                 # and free the WiFi network.
