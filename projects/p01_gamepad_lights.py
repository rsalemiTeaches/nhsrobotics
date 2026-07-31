# Project 01: Gamepad Lights
# GOAL: Connect a PS5 gamepad to your robot and use buttons to control LEDs.
# You do NOT need to understand every line yet. Find the # WORK comments.
#
# SETUP ORDER (see the Pairing Checklist poster):
#   0. In Thonny, File > Save As -> the Alvik (MicroPython device) -> save
#      this file as /workspace/p01.py. Do every step below, and all your
#      work, on that copy -- files outside /workspace get overwritten
#      whenever the projects are updated.
#   1. Run this program. Watch Thonny print your robot's WiFi name.
#   2. Connect the Mac to that WiFi network (password: password).
#   3. Open http://192.168.4.1 in Chrome, and KEEP THAT CHROME WINDOW OPEN
#      AND IN FRONT for the rest of the project. The browser blocks gamepad
#      input to any tab that isn't visible and focused, so switching to
#      another window (even Thonny) will make your buttons stop working.
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

        # WORK 3: Add two elif branches HERE, above the else below: when
        # CIRCLE is held, make both LEDs red; when TRIANGLE is held, make
        # both LEDs green.

        # WORK 2: When NO button is held, turn both LEDs WHITE (1, 1, 1),
        # not off -- that way you can SEE the program is running and just
        # waiting for a button, instead of wondering if it froze.
        # HINT: do this right after WORK 1, before WORK 3 -- otherwise the
        # LEDs will get stuck on once you press a button, since there's no
        # "idle" case yet.
        else:
            pass  # <-- replace with two set_color(1, 1, 1) lines

        time.sleep(0.02)  # small pause keeps the loop stable

finally:
    # This block ALWAYS runs when the program stops. Leave the robot clean.
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
