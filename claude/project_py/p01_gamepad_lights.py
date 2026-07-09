# Project 01: Gamepad Lights
# GOAL: Connect a PS5 gamepad to your robot and use buttons to control LEDs.
# You do NOT need to understand every line yet. Find the # WORK comments.
#
# SETUP ORDER (see the Pairing Checklist poster):
#   1. Run this program. Watch Thonny print your robot's WiFi name.
#   2. Connect the Mac to that WiFi network (password: password).
#   3. Open http://192.168.4.1 in the browser.
#   4. Pair the PS5 controller to the Mac over Bluetooth.

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
    while True:
        # Ask the gamepad for fresh data. This must happen EVERY loop.
        gamepad.update()

        # WORK 1: When the CROSS (X) button is held, make BOTH LEDs blue.
        # The buttons dictionary works like this:
        #     gamepad.buttons['cross']  -> True while held, False otherwise
        # An LED is set like this:
        #     alvik.left_led.set_color(red, green, blue)   # each 0 or 1
        if gamepad.buttons['cross']:
            pass  # <-- replace with two set_color lines (left and right)

        # WORK 2: When CIRCLE is held, make both LEDs red.

        # WORK 3: When TRIANGLE is held, make both LEDs green.

        # WORK 4: When NO button is held, turn both LEDs off.
        # HINT: use else after your if/elif chain.

        time.sleep(0.02)  # small pause keeps the loop stable

finally:
    # This block ALWAYS runs when the program stops. Leave the robot clean.
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
