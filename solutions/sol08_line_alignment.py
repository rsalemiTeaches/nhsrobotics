# Project 08: Line Alignment -- SOLUTION
# Version: V01
#
# Teacher copy. Ray's state machine, written out. Six states, one elif
# tree keyed on current_state.
#
#   INITIALIZE            wait for the sensors to wake up and for OK
#   START_MOTOR           give the order to roll forward
#   SEEK                  watch for an outer sensor to reach the tape,
#                         then stop and start the sweep
#   FIND_ANGLE_AND_ALIGN  watch for a sensor to reach the tape again,
#                         then turn back half of the sweep
#   DRIVE                 give the order to roll forward again
#   FIND_LINE             watch for all three sensors to be on the tape
#
# The rhythm is one order, then one watcher. START_MOTOR gives an order
# and leaves; SEEK does nothing but watch. DRIVE and FIND_LINE are the
# same pair again.
#
# Why halving works. The two outer sensors are mirrored about the
# robot's centreline, so they ride one circle around the wheel axle, and
# the edge of the tape cuts that circle twice. The first touch is one
# crossing. The sweep carries the robot through square and onto the
# mirror crossing, so half of the sweep comes back to square. Nothing in
# that arithmetic needs the sensor spacing or how far ahead of the axle
# they sit -- only the symmetry. And because the answer is half of a
# measured angle, any scale error in theta divides out.
#
# LINE_TOUCH is 150 on purpose. Paper reads about 50 and tape reads 300
# and up, so 150 trips while the sensor is still at the edge of the
# tape rather than on it. That is what lets a small turn pull the
# sensor back under the threshold, which is what makes the next state's
# test work.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# Wheel speeds, in RPM, the unit set_wheels_speed() uses by default.
SEEK_SPEED = 20
TURN_SPEED = 10

# The sensor reads about 50 on white paper and 300 or more on tape.
LINE_TOUCH = 150      # the edge of the tape
LINE_ON = 200         # squarely over the tape
PAPER_MAX = 75       # anything under this is bare paper

# brake() does not stop the robot the instant it is called. Wait this
# long before reading or zeroing the pose, so the number describes a
# robot that has finished moving.
SETTLE_MS = 1000

# Long enough for the turn to actually start, so the sensor that
# tripped SEEK has moved off the edge before anything looks at it.
TURN_START_MS = 50




current_state = 'INITIALIZE'
last_state = ''

try:
    while not sb.held('cancel'):
        time.sleep_ms(10)  # tiny yield to the OS, not a throttle
        # The screen names the state, and is written only when the state
        # changes -- the P07 pattern. On a robot turning this slowly it
        # is the difference between debugging and guessing.
        if current_state != last_state:
            last_state = current_state
            sb.update_display("State:", current_state)

        left_sensor, center_sensor, right_sensor = alvik.get_line_sensors()

        if current_state == 'INITIALIZE':
            # Two things have to be true before the machine starts: the
            # sensors are awake, and the robot is on bare paper. A robot
            # parked on the tape would trip SEEK on its first pass and
            # measure nothing.
            if (left_sensor > PAPER_MAX
                or center_sensor > PAPER_MAX
                or right_sensor > PAPER_MAX):
                sb.update_display("Move me off", "the tape")
            else:
                sb.update_display("Press OK", "to start")
                if sb.pressed('ok'):
                    current_state = 'START_MOTOR'

        elif current_state == 'START_MOTOR':
            # One order, given once. Re-issuing it every pass floods the
            # link to the base, and a speed that is already set does not
            # need setting again.
            alvik.set_wheels_speed(SEEK_SPEED, SEEK_SPEED)
            current_state = 'SEEK'

        elif current_state == 'SEEK':
            # Roll forward until either outer sensor reaches the edge of
            # the tape.
            if left_sensor > LINE_TOUCH or right_sensor > LINE_TOUCH:
                alvik.brake()
                time.sleep_ms(SETTLE_MS)

                # Zero the trip meter here, once the robot has actually
                # stopped, so what the next state measures is the sweep
                # and nothing else.
                alvik.reset_pose(0, 0, 0)

                # Turn toward the side that touched. That drags the
                # sensor which touched back off the tape and carries the
                # other one forward onto the far crossing. Right wheel
                # backwards is clockwise.
                if right_sensor > LINE_TOUCH:
                    alvik.set_wheels_speed(TURN_SPEED, -TURN_SPEED)
                else:
                    alvik.set_wheels_speed(-TURN_SPEED, TURN_SPEED)

                time.sleep_ms(TURN_START_MS)
                current_state = 'FIND_ANGLE_AND_ALIGN'

        elif current_state == 'FIND_ANGLE_AND_ALIGN':
            # Turn until a sensor is on the edge of the tape again. By
            # now the one that tripped SEEK has been pulled back under
            # LINE_TOUCH, so whichever sensor answers here is the far
            # crossing.
            if left_sensor > LINE_TOUCH or right_sensor > LINE_TOUCH:
                alvik.brake()
                time.sleep_ms(SETTLE_MS)

                # theta is the whole sweep, which is twice the angle the
                # robot was off by, and in the wrong direction.
                _x, _y, theta = alvik.get_pose()
                fix_turn = -1 * theta / 2

                # Nothing to watch during this turn -- the angle is
                # already known -- so it is the one place in the machine
                # that is allowed to block.
                alvik.rotate(fix_turn, blocking=True)
                current_state = 'DRIVE'

        elif current_state == 'DRIVE':
            alvik.set_wheels_speed(SEEK_SPEED, SEEK_SPEED)
            current_state = 'FIND_LINE'

        elif current_state == 'FIND_LINE':
            # Square, but not yet on the tape. Roll forward until all
            # three sensors are over it at once. All three, not any one:
            # a single sensor is satisfied the moment the machine gets
            # here, and the robot would stop without moving.
            if (left_sensor > LINE_ON
                    and center_sensor > LINE_ON
                    and right_sensor > LINE_ON):
                alvik.brake()
                sb.update_display("Aligned", "")
                current_state = 'INITIALIZE'
                last_state = ''

finally:
    alvik.brake()
    sb.light_both_leds(0, 0, 0)
    alvik.stop()
