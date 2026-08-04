# Is get_pose()'s theta odometry, or the IMU?
# Version: V02
#
# Runs on the robot with no cable. Put one line in the robot's main.py:
#     import workspace.pose_source_test
# Power up and read the screen. Hold Cancel to quit.
#
# Test 1 -- pick the robot up and turn it 90 degrees by hand.
#     th moves   -> the IMU is feeding the pose
#     th frozen  -> encoders only, pure dead reckoning
#
# Test 2 -- hold it in the air, wheels free, and hold OK. It commands a
# 4 second spin the wheels cannot deliver. Lights go white while it runs.
#     th climbs  -> odometry, believing wheels that touch nothing
#     th frozen  -> something other than the wheels is being used
#
# th is get_pose(). yaw is get_orientation(), which arrives in a different
# packet from the motor board. yaw is the control: it should move in
# test 1 whatever else happens.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

SPIN_DEG_S = 45
SPIN_MS = 4000
REFRESH_S = 0.2


def num(v):
    """The pose fields read None until the first packet lands."""
    return '  ----' if v is None else '%6.1f' % v


def screen():
    """Three lines on the OLED.

    log_info() takes one string and splits it at 16 and 32 characters, so
    each field is padded to exactly 16 to make the lines land square.
    MicroPython has no str.ljust(), hence the %-16s.
    """
    x, y, theta = alvik.get_pose()
    _, _, yaw = alvik.get_orientation()
    sb.log_info('%-16s%-16s%-16s' % ('th  ' + num(theta),
                                     'yaw ' + num(yaw),
                                     'x' + num(x) + ' y' + num(y)))


try:
    time.sleep(1.0)                 # let the first packets arrive
    alvik.reset_pose(0, 0, 0)

    while not sb.held('cancel'):
        screen()

        if sb.held('ok'):
            sb.light_both_leds(1, 1, 1)
            alvik.drive(0, SPIN_DEG_S)
            start = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), start) < SPIN_MS:
                screen()
                time.sleep(REFRESH_S)
            alvik.brake()
            sb.light_both_leds(0, 0, 0)
            time.sleep(0.5)

        time.sleep(REFRESH_S)

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()
