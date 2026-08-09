# Project 08: The Security Bot -- SOLUTION
# Version: V03
#
# Teacher copy. Four states in one elif tree keyed on current_state,
# plus the FLEX fifth state at the bottom.
#
#   PATROLLING  green, drive forward, watch for anything inside SPOT_CM
#   ADVANCING   red, close in slowly, two ways out
#   TURNING     blue, turn 135 degrees away
#   RUNNING     blue, drive away
#
# WHY THIS ONE NEEDS A STATE VARIABLE.
#
# Follow a single sensor reading of 40 cm through the machine:
#
#   PATROLLING  40 is inside SPOT_CM          -> go and have a look
#   ADVANCING   40 is between the two limits  -> keep closing in
#   TURNING     40 means nothing at all       -> ignored, we are leaving
#   RUNNING     40 means nothing at all       -> ignored, we are leaving
#
# One number, four correct answers, and nothing in the number says
# which. Only current_state says which. That is the argument for the
# whole project, and it is worth making out loud in class.
#
# There is a second argument underneath it, and it is the better one.
# "The clown did not flee" is not a fact about a reading. It is a fact
# about what happened WHILE the robot was doing something. A program
# with no memory of what it was doing cannot say a sentence like that
# at all, however many if statements you give it.
#
# WHICH STATES WATCH, AND WHICH DO NOT.
#
# PATROLLING and ADVANCING are watching states. They set a speed with
# drive(), which returns immediately, and then test the sensor -- so the
# loop keeps running and the robot can change its mind at any moment.
#
# TURNING and RUNNING are not watching anything. The robot has already
# decided to leave, and nothing it could see would change that. So they
# use move() and rotate(), which block: the robot goes deaf, does the
# whole maneuver, and returns when it is finished. That is exactly
# what P07 warned against, and it is the right call here for the
# opposite reason -- there is nothing to watch.
#
# move() and rotate() also choose their own speed. That is why there is
# no run speed or turn rate in the constants below: those numbers only
# exist for drive().

import time

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

PATROLLING = "PATROLLING"
ADVANCING = "ADVANCING"
TURNING = "TURNING"
RUNNING = "RUNNING"
PEEKING = "PEEKING"          # FLEX only

PATROL_SPEED_CMS = 10.0
ADVANCE_SPEED_CMS = 6.0

# 60 cm is the 24 inches in the brief. The other two bracket the advance:
# past FLED_CM it got away, inside STUBBORN_CM it never moved.
SPOT_CM = 60.0
FLED_CM = 90.0
STUBBORN_CM = 15.0

# How far the retreat turns, and how far it runs.
#
# 135 and not 180. Turning right around sends the robot back down the
# line it just came up, so in a corridor or a corner it bounces between
# the same two walls forever and never patrols the rest of the room.
# Less than half a turn breaks that symmetry, and every retreat points
# the robot somewhere it has not just been.
RETREAT_TURN_DEG = 135.0
RUN_CM = 50.0

# FLEX only. The peek looks back down the path the robot just ran, and
# that is half a turn from where it is now -- not another 135. Turning
# RETREAT_TURN_DEG again would leave it looking 90 degrees off.
PEEK_TURN_DEG = 180.0

current_state = PATROLLING
last_state = ""

try:
    while not sb.held('cancel'):

        distance = sb.get_closest_distance()

        if current_state != last_state:
            last_state = current_state
            sb.update_display("Security:", current_state)

        # --- WORK 1: PATROLLING ---
        if current_state == PATROLLING:
            sb.light_both_leds(0, 1, 0)
            alvik.drive(PATROL_SPEED_CMS, 0)

            if distance < SPOT_CM:
                current_state = ADVANCING

        # --- WORK 2: ADVANCING ---
        elif current_state == ADVANCING:
            sb.light_both_leds(1, 0, 0)
            alvik.drive(ADVANCE_SPEED_CMS, 0)

            # Two ways out. The advance is bracketed: the gap either
            # opens up, because the target backed away faster than the
            # robot closed in, or it shuts, because the target never
            # moved. Nothing else can happen while the robot keeps
            # rolling forward, so no third test is needed.
            #
            # A target that runs right out of the room sends
            # get_closest_distance() to 999, which is comfortably past
            # FLED_CM, so the fast escape and the slow one are the same
            # test.
            if distance > FLED_CM:
                current_state = PATROLLING
            elif distance < STUBBORN_CM:
                current_state = TURNING

        # --- WORK 3: TURNING ---
        # rotate() blocks, so the whole turn happens on this one pass
        # and the state is left on the same pass it was entered.
        elif current_state == TURNING:
            sb.light_both_leds(0, 0, 1)
            alvik.rotate(RETREAT_TURN_DEG)
            current_state = RUNNING

        # --- WORK 3: RUNNING ---
        # Same shape. move() blocks, so by the time the next line runs
        # the robot has already covered RUN_CM and stopped itself.
        elif current_state == RUNNING:
            sb.light_both_leds(0, 0, 1)
            alvik.move(RUN_CM)

            # Without the FLEX this line reads
            #     current_state = PATROLLING
            current_state = PEEKING

        # --- FLEX: PEEKING ---
        # The robot ran without ever finding out whether it was chased.
        # This state turns it back around to look, and it is the first
        # one whose arrow can point backwards: seeing something sends it
        # to TURNING, which it has already been through once.
        elif current_state == PEEKING:
            sb.light_both_leds(1, 1, 0)
            alvik.rotate(PEEK_TURN_DEG)

            # rotate() blocked through the whole turn, so the reading
            # taken at the top of this pass is from before the robot
            # turned round. Take a fresh one now that it is facing the
            # way it came.
            if sb.get_closest_distance() < SPOT_CM:
                current_state = TURNING
            else:
                current_state = PATROLLING

        # --- The catch-all ---
        # current_state is a word, and a word can be wrong. A state name
        # misspelled inside quotes is still a perfectly good word, so
        # Python raises nothing and every branch above quietly fails to
        # match. Without this else the robot would carry on at whatever
        # speed it was last given, saying nothing, and the fault would
        # look like a hardware problem.
        #
        # Every new state goes ABOVE this else. It is always last.
        # log_info() does both jobs in one line: it prints to the Shell
        # and writes the screen. The label is short because the screen
        # gives about sixteen characters before it wraps, and "Bad:"
        # leaves room for the longest state name.
        else:
            sb.light_both_leds(1, 0, 0)
            sb.log_info("Bad:", current_state)
            time.sleep_ms(3000)
            break

        # A moment for the robot's own background work. Nothing in this
        # project is timed by it.
        time.sleep_ms(50)

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()
