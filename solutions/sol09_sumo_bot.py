# Project 09: The Sumo Bot -- SOLUTION
# Version: V01
#
# Teacher copy. Three states, one elif tree, and one test that lives
# outside the tree.
#
#   PATROLLING  green, patrol speed, hunting
#   TURNING     blue, back off the rim and turn away
#   ATTACKING   red, full speed into whatever is in front
#
# WHAT IS NEW HERE, AND IT IS ONLY ONE THING.
#
# Every transition the class has ever written lived inside a branch, and
# so took effect on the NEXT pass of the loop. The edge test cannot wait
# for the next pass and cannot be repeated in all three branches, so it
# sits above the tree and writes current_state before the tree runs.
# That makes it take effect on THIS pass: the tree sees the new state
# and the TURNING branch executes immediately.
#
# It reads as a contradiction of P08 and it is not. P08's rule was about
# transitions inside a branch. A guard above the tree is a different
# animal, and the whole reason to put it there is the thing P08 said
# transitions do not do.
#
# WHY THE GUARD HAS TO OUTRANK THE CHARGE, in numbers. The rim is about
# 3 inches, 7.6 cm. At 50 RPM that is roughly nine tenths of a second
# from first white to falling out, and the loop runs twenty times a
# second, so the margin is enormous. At 70 RPM it shrinks by a third --
# and 70 RPM is exactly when the robot is least interested in looking
# down. The faster the robot, the more the check has to come first.
#
# It also means a robot cannot win itself out of the ring. Shove an
# opponent over the rim and the winner is standing on the rim, so the
# guard fires before the attack branch runs. Nobody writes that case.
#
# WHY THE RETREAT MAY BLOCK. Backing up and turning both move away from
# the edge, and nothing an opponent does during that second changes the
# right answer. Same argument P08 made, and it needs making again
# because a sumo ring makes blocking look reckless.
#
# WHAT IS NOT SOLVED, ON PURPOSE. Two robots nose to nose both see
# something inside ATTACK_CM, both charge, and neither moves. Nothing in
# these three states breaks that. It is the most likely thing to happen
# in a real match, and it is where a fourth state -- and the podium --
# is won.

import random
import time

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

PATROLLING = "PATROLLING"
TURNING = "TURNING"
ATTACKING = "ATTACKING"

PATROL_RPM = 50
ATTACK_RPM = 70

# The ring floor false-positives the distance sensor from about 5 cm
# out, so the charge threshold sits underneath the lies.
ATTACK_CM = 3.0

# Must be further than the nose has already crept over the white, or the
# robot turns with a sensor still on the rim and guards again forever.
BACKUP_CM = 10.0

# Black floor reads high, white rim reads low, so the rim is a reading
# that DROPS. Measure on the real ring.
EDGE_THRESHOLD = 200

# One answer of many. A quarter turn tends to run the robot along the
# rim and trip the guard again; anything near a half turn sends it back
# through the middle, where the opponents are. Random so that two
# robots meeting the rim together do not leave together.
TURN_MIN_DEG = 120
TURN_MAX_DEG = 240


def edge_detected():
    """True when any line sensor has reached the white rim.

    Given to students. The line sensors appear nowhere else in the
    project, so this is the only place that knows they return None until
    their first packet arrives, and the only place that knows the rim is
    low rather than high.

    Any one sensor is enough. Waiting for all three means waiting until
    the robot is most of the way off the ring.
    """
    left, center, right = alvik.get_line_sensors()
    if left is None or center is None or right is None:
        return False
    return (left < EDGE_THRESHOLD
            or center < EDGE_THRESHOLD
            or right < EDGE_THRESHOLD)


def waiting_for_gamepad(gamepad):
    """Hold the robot still until its driver presses CROSS.

    RobotGamepad's constructor already blinks yellow while the
    controller connects and leaves the lights solid green, so this
    only has to cover the second half: blinking green while the robot
    waits for the start of the match.

    The blink is not timed by a sleep, because the button has to stay
    responsive -- pressed() only sees a push if update() is called
    often enough to catch it.
    """
    lights_on = False
    last_blink = time.ticks_ms()
    while not gamepad.pressed('cross'):
        gamepad.update()
        if time.ticks_diff(time.ticks_ms(), last_blink) > 300:
            last_blink = time.ticks_ms()
            lights_on = not lights_on
            if lights_on:
                sb.light_both_leds(0, 1, 0)
            else:
                sb.light_both_leds(0, 0, 0)
        time.sleep_ms(20)
    sb.light_both_leds(0, 0, 0)


current_state = PATROLLING
last_state = ""

gamepad = RobotGamepad(alvik)

try:
    waiting_for_gamepad(gamepad)

    while not sb.held('cancel'):

        distance = sb.get_closest_distance()

        # --- WORK 2: THE EDGE GUARD ---
        # Above the tree, so it beats every branch in it.
        if edge_detected():
            current_state = TURNING

        # The screen is written AFTER the guard, and that is not a
        # detail. TURNING is set by the guard and cleared by its own
        # branch on the same pass, so a screen written above the guard
        # never sees it -- the robot would spend a second and a half
        # backing up and turning while the display still said
        # PATROLLING. Put the guard first and the screen second and the
        # display tells the truth again.
        if current_state != last_state:
            last_state = current_state
            sb.update_display("Sumo:", current_state)

        # --- WORK 1: PATROLLING ---
        if current_state == PATROLLING:
            sb.light_both_leds(0, 1, 0)
            alvik.set_wheels_speed(PATROL_RPM, PATROL_RPM)

            if distance < ATTACK_CM:
                current_state = ATTACKING

        # --- WORK 2: TURNING ---
        # Both moves block, and the robot is leaving, so there is
        # nothing it needs to watch while they run.
        elif current_state == TURNING:
            sb.light_both_leds(0, 0, 1)
            alvik.move(-BACKUP_CM)
            alvik.rotate(random.randint(TURN_MIN_DEG, TURN_MAX_DEG))
            current_state = PATROLLING

        # --- WORK 3: ATTACKING ---
        elif current_state == ATTACKING:
            sb.light_both_leds(1, 0, 0)
            alvik.set_wheels_speed(ATTACK_RPM, ATTACK_RPM)

            # The opponent got away, or was pushed out. Either way there
            # is nothing to charge, so go back to hunting. During a real
            # shove the opponent stays inside ATTACK_CM and this never
            # fires -- the guard ends the attack instead, at the rim.
            if distance > ATTACK_CM:
                current_state = PATROLLING

        # --- The catch-all ---
        else:
            sb.light_both_leds(1, 0, 0)
            sb.log_info("Bad:", current_state)
            time.sleep_ms(3000)
            break

        time.sleep_ms(50)

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()
