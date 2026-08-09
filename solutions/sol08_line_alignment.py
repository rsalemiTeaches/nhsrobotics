# Project 08: Line Alignment -- SOLUTION
# Version: V05
#
# Teacher copy.
#
#   START_DRIVE     -> roll forward, once
#   WATCH_DRIVE        wait for EITHER outer sensor
#   START_STOP      -> brake, once
#   WATCH_STOP         wait until the pose stops changing -- the robot is
#                      really stopped, not just told to stop
#   START_SEARCH    -> zero the pose, start turning, once
#   WATCH_SEARCH       wait for the other sensor to leave the line, THEN
#                      come back onto it. Record the sweep.
#   START_ALIGN     -> start turning back the other way, once
#   WATCH_ALIGN        turn back until BOTH outer sensors are on the line.
#                      Half the sweep is the backstop, not the goal.
#   START_APPROACH  -> roll forward, once
#   WATCH_APPROACH     wait for BOTH outer sensors
#
# WHAT V04 GOT WRONG, from its own trace:
#
#   START_SEARCH  (50, 52, 263)   theta -0.50
#   WATCH_SEARCH  (649, 652, 634) theta  0.03
#
# One pass -- ten milliseconds -- and all three sensors went from white to
# black. The robot never stopped. drive(0, rate) was sent, but the base
# takes about 0.2 s to act on it, and in the meantime the robot rolled
# right onto the band. So the sensor SEARCH was waiting for was already
# on, the sweep measured 0.03 degrees, half of nothing is nothing, and
# ALIGN finished on the pass it started. The machine ran to completion in
# about forty milliseconds without ever turning.
#
# Two fixes, and both are about sensing instead of assuming:
#
#   1. STOP is a real state now. Brake, then WATCH the pose until it stops
#      changing. Never assume a command has taken effect.
#   2. Nothing is believed unless a sensor says so. SEARCH will not accept
#      a sensor that was already on -- it has to go off and come back.
#      ALIGN finishes when the sensors say square, not when arithmetic on
#      the pose says it should be.
#
# No alvik.rotate() anywhere: every turn here is watching something.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

DRIVE_SPEED_CMS = 3.0
TURN_RATE_DEG_S = 30.0

# Measured 2026-08-09 with dev/line_sensor_probe.py, marker on white
# paper: white reads about 50, a sensor on the line reads 300-650.
LINE_THRESHOLD = 200

# The robot counts as stopped when the pose moves less than this between
# two looks. Sensed, not timed.
STILL_DEG = 0.05
STILL_CM = 0.05

# A sweep smaller than this did not happen. Better to say so than to halve
# a number that means nothing.
MIN_SWEEP_DEG = 3.0

# ALIGN gives up on the sensors past this much of the sweep and settles
# for the arithmetic. Half is the answer; this is the backstop.
ALIGN_OVERSHOOT = 1.2

SELF_CHECK_TIMEOUT_MS = 3000


def sensors_reporting():
    """True once all three sensors return a real number.

    A sensor reads None until its first packet arrives. None is not zero
    and it is not 'no line' -- it is no answer at all. The state machine
    below must never have to tell those apart.
    """
    left, centre, right = alvik.get_line_sensors()
    return left is not None and centre is not None and right is not None


def wait_for_sensors():
    """The only place in the file that knows None exists."""
    started = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), started) < SELF_CHECK_TIMEOUT_MS:
        if sensors_reporting():
            return True
        time.sleep_ms(20)
    return False


def outer_sensors():
    """(left, right), True when that sensor is over the line."""
    left, _centre, right = alvik.get_line_sensors()
    return left > LINE_THRESHOLD, right > LINE_THRESHOLD


def one_sensor(want_left):
    """Just the sensor being waited for. While the robot turns, the other
    two sweep over the line and read high; looking at them can only end
    the sweep early."""
    left, _centre, right = alvik.get_line_sensors()
    return (left if want_left else right) > LINE_THRESHOLD


def pose():
    x, y, theta = alvik.get_pose()
    return x, y, theta


def heading():
    """Rotation so far, from the wheel odometry.

    theta and not yaw on purpose. This project uses HALF OF A MEASURED
    ANGLE, so a consistent scale error divides out and theta's 8-13%
    over-report is invisible. Yaw runs 0-360 and rolls over mid-sweep,
    which would cost an unwrap and buy nothing.
    """
    return pose()[2]


state = 'START_DRIVE'
last_state = ''

search_rate = 0.0
waiting_for_left = False
target_left_the_line = False     # SEARCH will not accept a sensor that
                                 # was already on when the turn began
swept = 0.0
align_target = 0.0
align_limit = 0.0
last_pose = None

try:
    if not wait_for_sensors():
        sb.update_display("No line", "sensors")
        sb.light_both_leds(1, 0, 0)
        time.sleep(3.0)
        state = 'FAILED'

    while not sb.held('cancel') and state not in ('DONE', 'FAILED'):

        if state != last_state:
            last_state = state
            sb.update_display("State: ", state)
            print(state, alvik.get_line_sensors(), "theta", heading())

        # ---- orders: each runs once, then hands over to its watcher ----

        if state == 'START_DRIVE':
            alvik.drive(DRIVE_SPEED_CMS, 0)
            state = 'WATCH_DRIVE'

        elif state == 'START_STOP':
            alvik.brake()
            last_pose = None
            state = 'WATCH_STOP'

        elif state == 'START_SEARCH':
            alvik.reset_pose(0, 0, 0)
            alvik.drive(0, search_rate)
            # The sensor we are waiting for may still be sitting on the
            # band. It does not count until it has left and come back.
            target_left_the_line = not one_sensor(waiting_for_left)
            state = 'WATCH_SEARCH'

        elif state == 'START_ALIGN':
            alvik.drive(0, -search_rate)
            state = 'WATCH_ALIGN'

        elif state == 'START_APPROACH':
            alvik.drive(DRIVE_SPEED_CMS, 0)
            state = 'WATCH_APPROACH'

        # ---- watchers: these give no orders, they only look ----

        elif state == 'WATCH_DRIVE':
            left_on, right_on = outer_sensors()
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
                state = 'START_STOP'

        elif state == 'WATCH_STOP':
            # Watch the pose instead of counting off half a second. The
            # robot is stopped when it stops moving, and only the pose
            # can say that.
            now_pose = pose()
            if last_pose is not None:
                moved = (abs(now_pose[0] - last_pose[0]) > STILL_CM or
                         abs(now_pose[1] - last_pose[1]) > STILL_CM or
                         abs(now_pose[2] - last_pose[2]) > STILL_DEG)
                if not moved:
                    state = 'START_SEARCH'
            last_pose = now_pose

        elif state == 'WATCH_SEARCH':
            on_line = one_sensor(waiting_for_left)
            if not on_line:
                target_left_the_line = True
            elif target_left_the_line:
                swept = heading()
                if abs(swept) < MIN_SWEEP_DEG:
                    # The turn never happened. Say so rather than halving
                    # a number that means nothing.
                    print("SWEEP TOO SMALL:", swept)
                    sb.update_display("Sweep too", "small")
                    sb.light_both_leds(1, 0, 0)
                    time.sleep(3.0)
                    state = 'FAILED'
                else:
                    align_target = swept / 2.0
                    align_limit = swept * (1.0 - ALIGN_OVERSHOOT)
                    state = 'START_ALIGN'

        elif state == 'WATCH_ALIGN':
            # The sensors decide. Square means both outer sensors on the
            # line at the same time, and that is something the robot can
            # see. The halved angle is only there to stop it turning for
            # ever if it never sees it.
            left_on, right_on = outer_sensors()
            if left_on and right_on:
                state = 'START_STOP_DONE'
            elif swept > 0:
                if heading() <= align_limit:
                    state = 'START_APPROACH'
            else:
                if heading() >= align_limit:
                    state = 'START_APPROACH'

        elif state == 'START_STOP_DONE':
            alvik.brake()
            state = 'DONE'

        elif state == 'WATCH_APPROACH':
            # Square but not on the line: roll forward until both outer
            # sensors are on it at once.
            left_on, right_on = outer_sensors()
            if left_on and right_on:
                state = 'START_STOP_DONE'

        time.sleep_ms(10)

    if state == 'DONE':
        alvik.brake()
        sb.update_display("Square", "")
        sb.light_both_leds(0, 1, 0)
        time.sleep(2.0)

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()
