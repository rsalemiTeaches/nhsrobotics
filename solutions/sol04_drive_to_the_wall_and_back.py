# Project 04 SOLUTION: Drive to the Wall and Back
# Version: V06
#
# Runs from main.py on the robot. main.py holds one line:
#     import workspace.p04
# The student's file must be saved as exactly /workspace/p04.py or that
# import fails.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

WALL_THRESHOLD_CM = 15.0    # GIVEN, stop this far from the wall
DRIVE_SPEED_CMS = 10.0      # GIVEN, forward speed

try:
    # WORK 1: one flash per pass. The loop is the wait AND the repeat,
    # so Cancel gets read every half second while it sits there.
    while not sb.held('cancel'):
        sb.light_both_leds(1, 1, 1)
        time.sleep(0.25)
        sb.light_both_leds(0, 0, 0)
        time.sleep(0.25)

        if sb.held('ok'):

            # WORK 2: zero the pose, drive, stop when the wall is close.
            alvik.reset_pose(0, 0, 0)
            alvik.drive(DRIVE_SPEED_CMS, 0)

            while sb.get_closest_distance() > WALL_THRESHOLD_CM:
                time.sleep(0.03)

            # brake() only ASKS the robot to stop. Without this settle
            # sleep the pose gets read while the wheels are still
            # turning, distance_out comes back short by the coast, and
            # the robot lands about 1 cm shy of home on every lap.
            # Measured 2026-08-02 at 10 cm/s: 5 laps drifted ~6 cm without
            # it; 0.5 s settles it to near zero. 0.3 s was not enough.
            alvik.brake()
            time.sleep(0.5)

            # WORK 3: how far did we come, turn, drive it back, turn
            # again. The second rotate is what leaves the robot facing
            # the wall, ready for the next lap.
            distance_out, _, _ = alvik.get_pose()
            sb.log_info(distance_out)

            alvik.rotate(180)
            alvik.move(distance_out)
            alvik.rotate(180)

            # FLEX: the number with a label and its units, on the
            # screen. log_info() already puts the bare number there; the
            # work is making it readable. update_display() takes three
            # lines of ~16 characters.
            #
            # sb.update_display("Distance out",
            #                   "{:.1f} cm".format(distance_out))

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()  # GIVEN, never a WORK item.
