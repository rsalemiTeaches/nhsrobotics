# Project 05 SOLUTION: Distance Sensor
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
bot = SuperBot(alvik)

CLOSE = 10    # WORK 3: tuned values; anything sensible is fine
MEDIUM = 25

try:
    while not alvik.get_touch_cancel():

        distance_cm = bot.get_closest_distance()   # WORK 1
        print(distance_cm)                          # WORK 1 (continued)

        if distance_cm < CLOSE:                     # WORK 2
            alvik.left_led.set_color(1, 0, 0)       # red
            alvik.right_led.set_color(1, 0, 0)
        elif distance_cm < MEDIUM:
            alvik.left_led.set_color(1, 1, 0)       # yellow
            alvik.right_led.set_color(1, 1, 0)
        else:
            alvik.left_led.set_color(0, 1, 0)       # green
            alvik.right_led.set_color(0, 1, 0)

        # ORDER MATTERS: the CLOSE test must come first. If the
        # MEDIUM test ran first, a 5 cm reading would match
        # "< MEDIUM" and show yellow — the red case could never win.

        # FLEX (parking assistant): blink rate speeds up as the wall
        # nears — sleep for distance_cm / 100 seconds between LED
        # toggles, so 50 cm blinks every 0.5 s and 5 cm every 0.05 s.

        time.sleep(0.1)
finally:
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
