# Project 07: The Parking Sensor -- SOLUTION
# Version: V01
#
# Teacher copy. Two timer checks in one loop, plus tank drive, and not a
# single time.sleep() anywhere in the file. That absence is the project.
#
# The two checks are deliberately different shapes:
#   WORK 1  "has the second number changed?"   -- int() of a division
#   WORK 2  "has enough time gone by?"         -- ticks_diff against a mark
# A student who only ever sees the second shape thinks timers are one
# recipe. Seeing both is what makes the idea portable.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

MAX_RPM = 70
MS_PER_SECOND = 1000

BLINK_MS_PER_CM = 20
BLINK_MS_FASTEST = 60
BLINK_MS_SLOWEST = 1200

TOO_CLOSE_CM = 5.0

# WORK 3 adds this line. Building the gamepad blocks until a controller
# connects, which is why it is not at the top of the student scaffold --
# WORK 1 and WORK 2 must run with nothing but a USB cable.
gamepad = RobotGamepad(alvik)

# The remembering variables. All of them live above the loop.
start_time = time.ticks_ms()    # WORK 1: what "zero seconds" means
last_seconds = -1               # WORK 1: forces a write the first time
led_is_on = False               # WORK 2
last_toggle_time = time.ticks_ms()   # WORK 2

try:
    while not sb.held('cancel'):

        # --- WORK 1: THE CLOCK ---
        # ticks_diff() handles the wrap when ticks_ms() runs off the end
        # of its counter. Plain subtraction would go hugely negative
        # there, and the clock would stop for the rest of the run.
        now = time.ticks_ms()
        elapsed_ms = time.ticks_diff(now, start_time)
        seconds = int(elapsed_ms / MS_PER_SECOND)

        # The screen is written only when the number changes -- roughly
        # once a second instead of several hundred times. Nothing here is
        # throttling for the sake of it; the same number redrawn is just
        # work nobody sees.
        if seconds != last_seconds:
            last_seconds = seconds
            sb.update_display("Seconds: ", str(seconds))

        # --- WORK 2: THE BLINK ---
        distance = sb.get_closest_distance()
        blink_delay = distance * BLINK_MS_PER_CM

        # The two limits do more than tidy the ends. With nothing in
        # front of it get_closest_distance() reports NO_READING_CM (999),
        # which would ask for a 20-second wait; the slow limit turns that
        # into a calm heartbeat instead of a light that looks broken.
        if blink_delay > BLINK_MS_SLOWEST:
            blink_delay = BLINK_MS_SLOWEST
        if blink_delay < BLINK_MS_FASTEST:
            blink_delay = BLINK_MS_FASTEST

        if time.ticks_diff(now, last_toggle_time) > blink_delay:
            last_toggle_time = now
            led_is_on = not led_is_on
            if led_is_on:
                sb.light_both_leds(1, 0, 0)
            else:
                sb.light_both_leds(0, 0, 0)

        # --- WORK 3: TANK DRIVE, COPIED OUT OF THEIR OWN P03 ---
        gamepad.update()
        left_speed = gamepad.left_y * MAX_RPM
        right_speed = gamepad.right_y * MAX_RPM

        # --- FLEX: REFUSE TO DRIVE INTO IT ---
        # Forward is blocked inside TOO_CLOSE_CM, reverse is always
        # allowed, so the robot is never stuck. Purely additive: it edits
        # the two speeds between the sticks and the wheels, and takes
        # nothing away from WORK 3.
        if distance < TOO_CLOSE_CM:
            if left_speed > 0:
                left_speed = 0
            if right_speed > 0:
                right_speed = 0

        alvik.set_wheels_speed(left_speed, right_speed)

        # A tiny yield to the OS, not a throttle. Nothing in this project
        # is timed by a sleep -- WORK 1 and WORK 2 each check the clock
        # themselves, and this line could be deleted without changing
        # what either one does.
        time.sleep_ms(10)
finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()
