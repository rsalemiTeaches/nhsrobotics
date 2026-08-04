# Project 06 SOLUTION: The Magic Circle
# Version: V01
#
# Runs from main.py on the robot, or from Thonny with the cable in. The
# gamepad needs the laptop either way.
#
# Why these three numbers work together, for whenever they get retuned.
#
# The tempting rule is MAX_DIST_CM * sin(TOLERANCE_DEG) < RING_DIAMETER_CM/2
# -- aim once, drive straight, and the leftover aiming error must stay
# inside the ring. At 100 cm, 6 degrees and a 10 cm radius that fails:
# 10.45 cm of drift into 10 cm.
#
# It does not matter, because that rule describes a student who aims once
# from maximum range and then ignores the lights the whole way in. The
# tolerance is divided by the distance, so the aimed-at window is a fixed
# number of DEGREES and therefore a shrinking number of CENTIMETERS as the
# robot closes: about 10 cm of slack at a meter out, about 2 cm at twenty.
# A side light comes back on and sends them back to aiming. The loop
# tightens on itself, so the real requirement is that the final approach
# converges, and it always does.
#
# What WOULD break the game is making the tolerance so tight that a
# student cannot hold the robot inside it with tank-drive sticks. 6 degrees
# is a 12 degree window; much less than that and aiming stops being fun.
#
# Nothing here depends on the robot driving an accurate distance or an
# accurate angle. The ring exists only in the robot's own pose frame, so
# there is no physical ring for a drifting pose to disagree with, and the
# student is the control loop. That is deliberate -- see the
# alvik-drive-measured-behavior notes.
#
# UNVERIFIED, and the whole project rests on it: that the STM32 keeps
# integrating the pose when the wheels are driven by set_wheels_speed()
# rather than by drive(). Check this first.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import math
import random
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)
gamepad = RobotGamepad(alvik)

MAX_RPM = 70                    # GIVEN, the motor ceiling
MAX_DIST_CM = 100               # GIVEN
RING_DIAMETER_CM = 20           # GIVEN, about two robot widths


class Circle:
    """A ring on the floor that only the robot can see. GIVEN in full."""

    TOLERANCE_DEG = 6
    MIN_DIST_CM = 40

    def __init__(self, max_dist, diameter):
        self.radius = diameter / 2
        away = random.uniform(self.MIN_DIST_CM, max_dist)
        bearing = math.radians(random.uniform(0, 360))
        self.x = away * math.cos(bearing)
        self.y = away * math.sin(bearing)

    def get_bearings(self):
        x, y, theta = alvik.get_pose()
        dx = self.x - x
        dy = self.y - y

        t = math.radians(theta)
        forward = dx * math.cos(t) + dy * math.sin(t)
        sideways = -dx * math.sin(t) + dy * math.cos(t)

        away = math.sqrt(dx * dx + dy * dy)
        limit = math.sin(math.radians(self.TOLERANCE_DEG))

        # sideways/away instead of sideways keeps the aimed window a fixed
        # number of degrees at any range. The forward test is not optional:
        # with the ring dead astern sideways is also ~0, and without it the
        # robot reports "aimed" while pointing exactly the wrong way.
        if away > 0.1 and forward > 0 and abs(sideways / away) < limit:
            return 0, dx, dy
        if sideways > 0:
            return 1, dx, dy
        return -1, dx, dy


alvik.reset_pose(0, 0, 0)
circle = Circle(MAX_DIST_CM, RING_DIAMETER_CM)

try:
    while not (sb.held('cancel') or gamepad.held('options')):
        gamepad.update()

        left_speed = gamepad.left_y * MAX_RPM       # GIVEN, from P03
        right_speed = gamepad.right_y * MAX_RPM
        alvik.set_wheels_speed(left_speed, right_speed)

        dir, dx, dy = circle.get_bearings()         # GIVEN

        # WORK 1: the Pythagorean theorem, and the number on the screen.
        distance = math.sqrt(dx * dx + dy * dy)
        sb.update_display("Distance", str(round(distance)))

        # WORK 2: the side the ring is on, or neither when aimed at it.
        if dir == 1:
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 0, 0)
        elif dir == -1:
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 1, 0)
        else:
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)

        # WORK 3: distance as a color. set_rgb() clamps to 0-255 itself,
        # so driving further out than MAX_DIST_CM just pins it at blue
        # instead of crashing, and no student has to write a clamp.
        red = 255 * (1 - distance / MAX_DIST_CM)
        blue = 255 * (distance / MAX_DIST_CM)
        sb.nano_led.set_rgb(red, 0, blue)

        # GIVEN: the ending, the dance, and the next ring.
        if distance < RING_DIAMETER_CM / 2:
            alvik.brake()
            sb.light_both_leds(1, 1, 1)
            alvik.drive(0, 120)
            time.sleep(3.0)
            alvik.brake()
            sb.light_both_leds(0, 0, 0)
            time.sleep(1.0)
            alvik.reset_pose(0, 0, 0)
            circle = Circle(MAX_DIST_CM, RING_DIAMETER_CM)

        # FLEX: an autopilot on a held button. R1 down and the robot hunts
        # the ring itself; R1 up and the student is driving again.
        #
        # if gamepad.held('R1'):
        #     if dir != 0:
        #         alvik.set_wheels_speed(-20 * dir, 20 * dir)
        #     else:
        #         alvik.set_wheels_speed(30, 30)
        #
        # ADDITIVE, which the earlier version of this flex was not. That one
        # had students replace the tank drive, which broke the rule that
        # nothing may replace WORK behaviour. This one only adds: the tank
        # drive above has already issued its order, and set_wheels_speed()
        # is an order rather than a setting, so the last call in a loop pass
        # wins. With R1 up the block never fires and the sticks still rule.
        #
        # Signs: dir 1 means the ring is left, and left wheel back with
        # right wheel forward turns left, so (-20 * dir, 20 * dir) always
        # turns toward the ring. It never needs an accurate turn -- only to
        # know which way is wrong.
        #
        # Also the on-ramp to P07: a robot that hunts on its own while a
        # human stays ready to take the controls is most of a sumo robot.

        time.sleep(0.05)

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    sb.nano_led.off()
    alvik.stop()  # GIVEN, never a WORK item.
