# Curve pose test -- does get_pose() tell the truth through a curve?
# Version: V01
#
# Not a student project. This answers the questions P06 rests on, and one
# that P05 rests on, in a single run with one tape measure.
#
#   1. Is y honest? NOTHING has ever measured y. Every pose number we
#      trust came from a straight line (x) or a spin in place (theta).
#   2. Is theta honest while the robot is also translating? Measured in
#      place, never during a curve.
#   3. How far past the target angle does the robot keep turning after the
#      poll fires? P06 ends the curve with drive(SPEED, 0), not brake(),
#      so the overshoot is whatever the 0.21 s command lag costs.
#   4. Does polling get_pose() at 30 Hz keep up? (Prints the worst gap.)
#   5. P05's prediction: the arc radius is right even though the traverse
#      is 7.4% slow, because radius = forward / turn and the error
#      cancels. Radius is half the sideways offset, so the tape measure
#      that answers question 1 answers this one too.
#
# Phase D also measures alvik.rotate(), which has never been tested. P06
# does not use it. P04's WORK 3 does.
#
# Run it:
#   Put this file in the robot's workspace folder, and put one line in the
#   robot's main.py:
#       import workspace.curve_pose_test
#   Place the robot in the start box of the P05 board, nose pointing along
#   the board the way P05 drives. Mark the floor at the front edge and
#   along the centre line. Power up, hold OK.
#
# It drives leg 1, curves 180 deg right, runs one more second straight to
# catch the overshoot, stops, then spins four quarter turns in place.
#
# Logs 10 Hz to /curve_pose_data.csv and prints the numbers that matter to
# the shell, so with the cable in you can skip the CSV unless something
# looks wrong.
#
# MEASURE BY HAND after it stops, before Phase D spins it:
#   - forward:  start line to the robot's centre, along the board
#   - sideways: board centre line to the robot's centre, across the board
#   - heading:  against your floor mark, by eye is fine
# Compare those three against the printed pose. That is the whole test.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import math
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

SPEED_CMS = 6.0             # sol05's worked example
TURN_RATE_DEG_S = -30.0     # negative turns right, measured 2026-08-03
X_TARGET_CM = 20.0          # leg 1: about where sol05's 3.6 s lands
THETA_TARGET_DEG = -180.0   # half a circle
COAST_WATCH_S = 1.0         # keep logging after the turn command ends
SETTLE_S = 0.5              # brake() takes about this long
LEG_LIMIT_S = 30.0          # bail out rather than drive off the board

POLL_S = 0.03               # 30 Hz, the rate P04 already polls at
LOG_S = 0.10                # 10 Hz to the CSV
LOG_PATH = '/curve_pose_data.csv'

log = None
t0 = time.ticks_ms()
worst_gap_ms = 0


def now_s():
    return time.ticks_diff(time.ticks_ms(), t0) / 1000.0


def note(leg, x, y, theta):
    log.write('%.2f,%s,%.2f,%.2f,%.2f\n' % (now_s(), leg, x, y, theta))


def run_until(leg, done, limit_s=LEG_LIMIT_S):
    """Poll at 30 Hz, log at 10 Hz, until done(x, y, theta) is true.

    Returns (x, y, theta, timed_out).
    """
    global worst_gap_ms
    start = now_s()
    last_log = -1.0
    last_poll = time.ticks_ms()
    while True:
        x, y, theta = alvik.get_pose()

        gap = time.ticks_diff(time.ticks_ms(), last_poll)
        last_poll = time.ticks_ms()
        if gap > worst_gap_ms:
            worst_gap_ms = gap

        t = now_s()
        if t - last_log >= LOG_S:
            note(leg, x, y, theta)
            last_log = t

        if done(x, y, theta):
            return x, y, theta, False
        if t - start > limit_s:
            return x, y, theta, True

        time.sleep(POLL_S)


def show(label, x, y, theta):
    print('%-22s x=%7.2f  y=%7.2f  theta=%8.2f' % (label, x, y, theta))


try:
    print()
    print('Curve pose test V01.  Hold OK to run, Cancel to quit.')
    print('Speed %.1f cm/s, turn %.1f deg/s, leg 1 to x=%.1f cm.'
          % (SPEED_CMS, TURN_RATE_DEG_S, X_TARGET_CM))

    while not sb.held('cancel'):
        sb.light_both_leds(1, 1, 1)
        time.sleep(0.25)
        sb.light_both_leds(0, 0, 0)
        time.sleep(0.25)

        if not sb.held('ok'):
            continue

        log = open(LOG_PATH, 'w')
        log.write('t,leg,x,y,theta\n')
        t0 = time.ticks_ms()
        worst_gap_ms = 0

        # ---- Phase A: leg 1, straight out, stop by watching x ----------
        alvik.reset_pose(0, 0, 0)
        time.sleep(0.2)
        alvik.drive(SPEED_CMS, 0)
        ax, ay, atheta, a_late = run_until(
            'A_straight', lambda x, y, th: x >= X_TARGET_CM)

        # ---- Phase B: the curve, stop the turn by watching theta -------
        # No brake between legs. This is exactly what P06 asks students
        # to write, and what P05 does with a tuned sleep instead.
        alvik.drive(SPEED_CMS, TURN_RATE_DEG_S)
        bx, by, btheta, b_late = run_until(
            'B_curve', lambda x, y, th: th <= THETA_TARGET_DEG)

        # ---- Phase C: switch out of the turn, keep watching ------------
        # The turn does not stop when the command changes. Whatever theta
        # does over the next second is the overshoot P06 has to live with.
        alvik.drive(SPEED_CMS, 0)
        c_start = now_s()
        cx, cy, ctheta, _ = run_until(
            'C_coast', lambda x, y, th: now_s() - c_start >= COAST_WATCH_S)

        alvik.brake()
        time.sleep(SETTLE_S)
        fx, fy, ftheta = alvik.get_pose()
        note('F_final', fx, fy, ftheta)
        log.flush()

        radius_pred = SPEED_CMS / math.radians(abs(TURN_RATE_DEG_S))

        print()
        print('---- pose at each transition ----')
        show('end of leg 1', ax, ay, atheta)
        show('theta poll fired', bx, by, btheta)
        show('1 s later', cx, cy, ctheta)
        show('after brake + settle', fx, fy, ftheta)
        print()
        print('theta overshoot after the command changed: %.2f deg'
              % (ftheta - btheta))
        print('worst gap between get_pose() calls: %d ms' % worst_gap_ms)
        print()
        print('---- what the arc should have been ----')
        print('predicted radius  %.2f cm   (forward / turn, in radians)'
              % radius_pred)
        print('predicted sideways offset  %.2f cm   (twice the radius)'
              % (-2 * radius_pred))
        print('pose says sideways         %.2f cm' % fy)
        if a_late or b_late:
            print('*** a leg hit its time limit -- numbers are junk ***')
        print()
        print('MEASURE NOW, before it spins:')
        print('  forward  from the start line to the robot centre')
        print('  sideways from the board centre line to the robot centre')
        print('  heading  against your floor mark')
        print()
        print('Hold OK again for the rotate() check, Cancel to stop here.')

        while True:
            if sb.held('cancel'):
                raise KeyboardInterrupt
            if sb.held('ok'):
                break
            sb.light_both_leds(0, 0, 1)
            time.sleep(0.25)
            sb.light_both_leds(0, 0, 0)
            time.sleep(0.25)

        # ---- Phase D: rotate(), for P04. Not used by P06. -------------
        # Four quarter turns should come back to the same heading and add
        # 360 to theta. Also checks that theta does not wrap.
        print()
        print('---- rotate() check: four rotate(90) turns ----')
        d_start_theta = ftheta
        for i in range(4):
            alvik.rotate(90)
            time.sleep(SETTLE_S)
            dx, dy, dtheta = alvik.get_pose()
            note('D_rotate_%d' % (i + 1), dx, dy, dtheta)
            print('after turn %d: theta=%8.2f   change from start=%8.2f'
                  % (i + 1, dtheta, dtheta - d_start_theta))
        print()
        print('Pose should read 360.00 deg of change, and the physical')
        print('heading should be back on your floor mark. Both matter, and')
        print('they can disagree. Write down the change from start.')

        log.close()
        log = None
        print()
        print('Done. CSV at %s' % LOG_PATH)
        break

except KeyboardInterrupt:
    print('stopped')

finally:
    alvik.brake()
    if log is not None:
        log.close()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()
