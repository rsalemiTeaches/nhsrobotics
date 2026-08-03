# Project 05 SOLUTION: Around the Cone
# Version: V01
#
# Runs from main.py on the robot. main.py holds one line:
#     import workspace.p05
#
# The four tuned numbers below are for MY_SPEED_CMS = 6.0 on a board with
# the two boxes 24 cm apart, centre to centre, which makes the arc a 12 cm
# radius. Every student's numbers are different because every student's
# speed is different. These are a worked example, not an answer key.
#
# Speeds come from the student number: multiply by 5, subtract 41 until
# it is under 41, divide by 10, add 4. That gives 24 distinct values from
# 4.3 to 8.0, with no two neighbouring numbers closer than 0.5. Student 4
# gets the 6.0 used below. Every value in the range keeps a 12 cm arc
# inside the motor budget -- the worst case, 8.0, needs 10.9 of 12.5.
#
# Why they land where they do, for reference when a student is stuck:
#   drive() delivers about 92.6% of the speed you ask for (measured on
#   three robots, 2026-08-03), so 6.0 cm/s is really about 5.5 cm/s and
#   -30 deg/s is really about -27.7 deg/s. Students never see this. They
#   tune until it works, and the tuning absorbs it. Do NOT put a
#   correction factor in the guide or in nhs_lib.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

MY_SPEED_CMS = 6.0          # GIVEN, different for every student

STRAIGHT_1_SECONDS = 3.6    # tuned: out of the box, level with the cone
TURN_RATE_DEG_S = -30.0     # tuned: negative because the course turns right
ARC_SECONDS = 6.5           # tuned: half a circle, pointing at the box
STRAIGHT_2_SECONDS = 3.6    # tuned: into the parking space

try:
    # GIVEN in the scaffold this time. Students typed this loop in P04.
    while not sb.held('cancel'):
        sb.light_both_leds(1, 1, 1)
        time.sleep(0.25)
        sb.light_both_leds(0, 0, 0)
        time.sleep(0.25)

        if sb.held('ok'):

            # FLEX: the A+ adds this line, so the robot is counting from
            # zero before the first leg starts.
            #
            # alvik.reset_pose(0, 0, 0)

            # WORK 1: out of the start box. Straight, so a zero in the
            # second spot -- the same call they wrote in P04, and the
            # first time anyone has told them what that zero was for.
            alvik.drive(MY_SPEED_CMS, 0)
            time.sleep(STRAIGHT_1_SECONDS)

            # FLEX: the A+ reads the distance here, at the end of the
            # straight leg and before the curve moves things around.
            # The parking box is level with the start box, so leg 3 is
            # the same length as leg 1.
            #
            # distance_out, _, _ = alvik.get_pose()

            # WORK 2: the curve. Both arguments at once, which is the
            # whole point of the project. No brake first -- calling
            # drive() again just changes what the wheels are doing.
            alvik.drive(MY_SPEED_CMS, TURN_RATE_DEG_S)
            time.sleep(ARC_SECONDS)

            # WORK 3: into the box. Straight again.
            alvik.drive(MY_SPEED_CMS, 0)
            time.sleep(STRAIGHT_2_SECONDS)

            # FLEX: the A+ replaces those two lines with one call that
            # measures itself instead of being tuned. move() blocks, so
            # there is no sleep and no brake needed after it.
            #
            # alvik.move(distance_out)

            alvik.brake()   # GIVEN

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN, never a WORK item.
