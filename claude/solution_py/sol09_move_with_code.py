# Project 09 SOLUTION: Move With Code
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

print("Place the robot at the start mark. Press OK to go.")
while not alvik.get_touch_ok():
    time.sleep(0.05)

try:
    # GOAL 1: the square (WORK 1 + WORK 2)
    for _ in range(4):
        sb.nav.drive_distance(30)
        sb.nav.rotate_precise(90)

    # GOAL 2: example taped course (WORK 3) — adjust to the real tape:
    # sb.nav.drive_distance(50)
    # sb.nav.rotate_precise(-45)      # negative turns the other way
    # sb.nav.drive_distance(70)
    # sb.nav.rotate_precise(90)
    # sb.nav.drive_distance(40)

    # FLEX: drive your initials. Example, the letter "L":
    # sb.nav.drive_distance(40)       # down stroke
    # sb.nav.rotate_precise(-90)
    # sb.nav.drive_distance(20)       # foot

    print("Route complete.")
finally:
    alvik.brake()
    alvik.stop()
