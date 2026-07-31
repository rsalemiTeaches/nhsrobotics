# Project 08 SOLUTION: Move With Code
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
    # WORK 1 + WORK 2: the square
    print("The square.")
    for _ in range(4):
        sb.nav.drive_distance(30)
        sb.nav.rotate_precise(90)

    # The square ends where it started, facing its original heading, so
    # WORK 3 can simply run next. Everything demos in one run -- nothing
    # gets commented out or erased for the checkoff.
    print("Square complete. Reposition on the course START mark,")
    print("then press OK to drive the taped course.")
    while not alvik.get_touch_ok():
        time.sleep(0.05)

    # WORK 3: the taped course — these numbers are an EXAMPLE.
    # Measure the real tape and replace them.
    print("The taped course.")
    sb.nav.drive_distance(50)
    sb.nav.rotate_precise(-45)      # negative turns the other way
    sb.nav.drive_distance(70)
    sb.nav.rotate_precise(90)
    sb.nav.drive_distance(40)

    # FLEX: drive your initials. Example, the letter "L":
    # sb.nav.drive_distance(40)       # down stroke
    # sb.nav.rotate_precise(-90)
    # sb.nav.drive_distance(20)       # foot

    print("Route complete.")
finally:
    alvik.brake()
    alvik.stop()
