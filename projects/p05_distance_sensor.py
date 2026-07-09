# Project 05: Distance Sensor
# GOAL: Read the robot's Time-of-Flight distance sensors and react.
#
# The Alvik has FIVE distance sensors across its front. This project
# introduces SuperBot, which reads all five and hands you the closest
# valid one:   distance_cm = bot.get_closest_distance()

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
bot = SuperBot(alvik)

# --- THRESHOLDS (in centimeters) ---
# WORK 3: adjust these until the warning feels right.
CLOSE = 10
MEDIUM = 25

try:
    # --- GOAL 1: LIVE READOUT ---
    while not alvik.get_touch_cancel():

        # WORK 1: get the closest distance from SuperBot and store it
        # in a variable named  distance_cm
        distance_cm = 999  # <-- replace 999 with the SuperBot call

        # WORK 2: print it, so you can watch the numbers in Thonny.
        # Move your hand toward the robot and watch what happens.

        # --- GOAL 2: PROXIMITY WARNING ---
        # WORK 4: turn both LEDs
        #     RED    when distance_cm is closer than CLOSE
        #     YELLOW (red + green) when closer than MEDIUM
        #     GREEN  otherwise
        # Think about the ORDER of your if/elif tests. Which test
        # must come first, and why?

        time.sleep(0.1)

finally:
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
