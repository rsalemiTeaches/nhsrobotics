# Project 08: Line Alignment -- SOLUTION
# Version: V01
#
# Teacher copy. Four states, four waits, one elif tree.
#
#   DRIVE     roll forward until EITHER outer sensor sees the line
#   SEARCH    turn toward the side that has NOT seen it, until the other
#             sensor lands on the far crossing
#   ALIGN     turn back half of what SEARCH swept
#   APPROACH  roll forward until BOTH outer sensors see the line at once
#
# Why these four and not seven. A state is something the robot is doing
# while it waits. A "STOP" state and a "CALCULATE" state would exit on the
# same pass they were entered, so they are not states -- they are the two
# or three lines that run at a transition. And SEARCH CW / SEARCH CCW are
# one state: the direction and the sensor being waited on are data, not
# control flow. Splitting them duplicates every future edit.
#
# Why a state variable is needed at all. DRIVE and APPROACH perform the
# same physical action -- roll forward, watch the outer sensors -- and end
# on different tests. In DRIVE, one sensor going high means stop and
# branch. In SEARCH, the same sensor going high means nothing at all. In
# APPROACH it means nothing unless its partner is high too. Identical
# readings, three correct answers, and nothing in the reading says which.
# Only the state does.
#
# Why halving works, and why it is immune to the odometry error. Both
# outer sensors ride the same circle around the wheel axle, and the line
# cuts that circle twice. Turning toward the side that has NOT seen the
# line puts the second sensor on the FAR crossing. Stopping halfway back
# leaves the sensor pair symmetric between the two crossings, which is
# the same as saying the pair is parallel to the line -- square. Because
# the answer is half of a measured angle, theta's 8-13% over-report
# divides out. Do NOT "improve" this by reaching for yaw: yaw wraps at
# 360 and would need unwrapping to buy nothing.
#
# No alvik.rotate() anywhere. Every turn in this project is watching
# something, so every turn is drive().

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

DRIVE_SPEED_CMS = 8.0
TURN_RATE_DEG_S = 45.0

# On the white field the tape reads ABOVE this. The sumo ring is the
# opposite polarity -- that is P09's problem, not this one.
LINE_THRESHOLD = 500


# How long to wait at startup for the sensors to start reporting.
SELF_CHECK_TIMEOUT_MS = 3000


def sensors_reporting():
    """True once all three sensors return a real number.

    A sensor reads None until its first packet arrives. None is not a
    reading of zero and it is not 'no line' -- it is no answer at all.
    Those are different facts and the state machine below must never have
    to tell them apart.
    """
    left, center, right = alvik.get_line_sensors()
    return left is not None and center is not None and right is not None


def wait_for_sensors():
    """Block here, before the machine starts, until the sensors are alive.

    This is the only place in the file that knows None exists. It returns
    False if they never come up, and the caller stops with a message on
    the screen -- because a robot that drives forward forever, certain
    there is no line, looks exactly like a robot with no line in front of
    it. Silence is the worst possible report.
    """
    started = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), started) < SELF_CHECK_TIMEOUT_MS:
        if sensors_reporting():
            return True
        time.sleep_ms(20)
    return False


def outer_sensors():
    """(left, right), True when that sensor is over the line.

    Safe to compare without a guard: nothing calls this until
    wait_for_sensors() has said the numbers are real.
    """
    left, _center, right = alvik.get_line_sensors()
    return left > LINE_THRESHOLD, right > LINE_THRESHOLD


def heading():
    """Rotation so far, in degrees, from the wheel odometry.

    Deliberately theta and not yaw. Yaw is the IMU and is the better
    number in general, but this project only ever uses HALF OF A MEASURED
    ANGLE, so any consistent scale error divides out -- theta's 8-13%
    over-report is invisible here. Yaw would cost an unwrap, because it
    runs 0-360 and rolls over mid-sweep, and would buy nothing.

    The one thing that would break this is wheel slip, which is not
    proportional and would not divide out. Turning slowly in place on a
    flat field is the least slip-prone thing the robot does.
    """
    _x, _y, theta = alvik.get_pose()
    return theta


state = 'DRIVE'
last_state = ''

# Set at the DRIVE -> SEARCH transition. The sweep direction and the
# sensor that ends the sweep are both discovered at runtime, because the
# approach angle is arbitrary -- that is the whole premise of the project.
search_rate = 0.0
waiting_for_left = False
swept = 0.0
align_target = 0.0

try:
    # GIVEN: the self-check. It runs once, before the machine starts, so
    # that every sensor read inside the loop is a real number and the
    # states never have to ask whether the data exists.
    if not wait_for_sensors():
        sb.update_display("No line", "sensors")
        sb.light_both_leds(1, 0, 0)
        time.sleep(3.0)
        state = 'FAILED'

    while not sb.held('cancel') and state not in ('DONE', 'FAILED'):

        # The screen names the state, written only when it changes --
        # the P07 pattern. On a robot that is turning slowly this is the
        # difference between debugging and guessing.
        if state != last_state:
            last_state = state
            sb.update_display("State: ", state)

        left_on, right_on = outer_sensors()

        if state == 'DRIVE':
            # Roll forward and wait for EITHER outer sensor.
            alvik.drive(DRIVE_SPEED_CMS, 0)

            if left_on or right_on:
                # Turn toward the side that has NOT seen the line, so the
                # second sensor lands on the far crossing. Negative turns
                # right, positive turns left.
                if left_on:
                    search_rate = -TURN_RATE_DEG_S
                    waiting_for_left = False
                else:
                    search_rate = TURN_RATE_DEG_S
                    waiting_for_left = True

                # Zero the trip meter here, so what SEARCH measures is the
                # sweep and nothing else. No brake first: P05 already
                # showed that drive() needs no stop between legs, and
                # calling it again just changes what the robot is doing.
                alvik.reset_pose(0, 0, 0)
                state = 'SEARCH'

        elif state == 'SEARCH':
            # Turn, and wait for the OTHER sensor. The one that got us
            # here is still sitting on the line and is ignored.
            alvik.drive(0, search_rate)

            found = left_on if waiting_for_left else right_on
            if found:
                swept = heading()
                align_target = swept / 2.0
                state = 'ALIGN'

        elif state == 'ALIGN':
            # Turn back the other way until the pose says we are halfway.
            # Both numbers come from the same over-reading odometry, so
            # the error cancels.
            alvik.drive(0, -search_rate)

            if swept > 0:
                arrived = heading() <= align_target
            else:
                arrived = heading() >= align_target
            if arrived:
                state = 'APPROACH'

        elif state == 'APPROACH':
            # Square now, but not necessarily ON the line. Roll forward
            # until BOTH outer sensors are on it at once, which is what
            # square-on-the-line means. Note this is the same action as
            # DRIVE with a different exit test -- and it is why "drive
            # until you see the line" is not enough: written with OR, this
            # finishes on the pass it starts, without moving, and looks
            # right doing it.
            alvik.drive(DRIVE_SPEED_CMS, 0)

            if left_on and right_on:
                state = 'DONE'

        # A tiny yield to the OS, not a throttle. Every wait above is a
        # test on this loop, so nothing here is timed by a sleep.
        time.sleep_ms(10)

    alvik.brake()
    if state == 'DONE':
        sb.update_display("Square", "")
        sb.light_both_leds(0, 1, 0)
        time.sleep(2.0)

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()
