#############################
#         Project 11        #
#     Advanced Line Racer   #
#############################

# This project uses a more advanced, fine-grained state machine
# to navigate the line and avoid an obstacle. Each step of the
# avoidance maneuver is its own state. It also adds sound
# effects using the Qwiic Buzzer for better feedback.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
from nhs_robotics import get_closest_distance

# --- State Machine Definitions ---
# We have more states now to handle each part of the maneuver.
LINE_FOLLOWING = 1
SEE_OBSTACLE = 2
DRIVE_FROM_LINE = 3
DRIVE_AROUND = 4
LOOK_FOR_THE_LINE = 5
FOUND_THE_LINE = 6

# --- Configuration ---
BASE_SPEED = 40
OBSTACLE_DISTANCE = 7  # How close to get before avoiding.
KP = 75.0
LINE_FOUND_THRESHOLD = 300 # If the max sensor value is over this, we see the line.
SEARCH_SPEED = 20

# Maneuver Configuration - Tuned for a quicker race
AVOID_TURN_1 = 90  # First turn away from the line
AVOID_STRAIGHT_1 = 10
AVOID_TURN_2 = -90 # Turn back to be parallel
AVOID_STRAIGHT_2 = 20
AVOID_TURN_3 = -90 # Turn back towards the line
ALIGN_TURN = 75   # A negative value correctly turns the robot LEFT

# --- Helper Functions ---
def get_turn_adjustment(left_val, center_val, right_val):
    # We now check if the MAX sensor value is below a threshold.
    # This is less sensitive than checking the sum.
    if max(left_val, center_val, right_val) < LINE_FOUND_THRESHOLD:
        return 0

    sum_values = (left_val * 1) + (center_val * 2) + (right_val * 3)
    sum_weight = left_val + center_val + right_val
    # Add a check to prevent division by zero if sum_weight is 0
    if sum_weight == 0:
        return 0
    centroid = sum_values / sum_weight
    error = centroid - 2
    return error

# --- Main Program ---
alvik = ArduinoAlvik()


# Start in the default state
current_state = LINE_FOLLOWING

try:
    alvik.begin()
    print("Project 11: Advanced Line Racer")
    print("Press OK to start the race!")

    while True:
        if alvik.get_touch_ok():
            break
        # Blinking startup lights...
        alvik.left_led.set_color(0, 0, 1)
        alvik.right_led.set_color(0, 0, 1)
        sleep_ms(100)
        alvik.left_led.set_color(0, 0, 0)
        alvik.right_led.set_color(0, 0, 0)
        sleep_ms(100)

    print("Go!")

    # --- Main Loop ---
    while True:
        if alvik.get_touch_cancel():
            break

        # SENSE: Always get fresh sensor data
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()
        raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r = alvik.get_distance()
        closest_distance = get_closest_distance(raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r)

        # --- THINK & ACT: The Fine-Grained State Machine ---

        if current_state == LINE_FOLLOWING:
            alvik.left_led.set_color(0, 1, 0) # Green
            if closest_distance < OBSTACLE_DISTANCE:
                current_state = SEE_OBSTACLE
            else:
                adjustment = get_turn_adjustment(l_sensor, c_sensor, r_sensor)
                control_signal = adjustment * KP
                alvik.set_wheels_speed(BASE_SPEED + control_signal, BASE_SPEED - control_signal)

        elif current_state == SEE_OBSTACLE:
            alvik.set_wheels_speed(0, 0)
            print("State: SEE_OBSTACLE -> DRIVE_FROM_LINE")
            current_state = DRIVE_FROM_LINE
            sleep_ms(500) # Pause to make the state change clear

        elif current_state == DRIVE_FROM_LINE:
            alvik.left_led.set_color(1, 1, 0) # Yellow
            alvik.right_led.set_color(1, 1, 0)
            alvik.rotate(AVOID_TURN_1)
            alvik.move(AVOID_STRAIGHT_1)
            print("State: DRIVE_FROM_LINE -> DRIVE_AROUND")
            current_state = DRIVE_AROUND

        elif current_state == DRIVE_AROUND:
            alvik.left_led.set_color(1, 1, 0) # Yellow
            alvik.right_led.set_color(1, 1, 0)
            alvik.rotate(AVOID_TURN_2)
            alvik.move(AVOID_STRAIGHT_2)
            alvik.rotate(AVOID_TURN_3) # Perform final turn before searching
            print("State: DRIVE_AROUND -> LOOK_FOR_THE_LINE")
            current_state = LOOK_FOR_THE_LINE

        elif current_state == LOOK_FOR_THE_LINE:
            alvik.left_led.set_color(0, 0, 1) # Blue
            alvik.right_led.set_color(0, 0, 1)
            alvik.set_wheels_speed(SEARCH_SPEED, SEARCH_SPEED)

            # Transition check: Have we found the line?
            # Use the new, more robust check.
            if max(l_sensor, c_sensor, r_sensor) > LINE_FOUND_THRESHOLD:
                current_state = FOUND_THE_LINE

        elif current_state == FOUND_THE_LINE:
            alvik.set_wheels_speed(0, 0)
            print("State: Aligning with line...")
            alvik.rotate(ALIGN_TURN) # Line up
            print("State: -> LINE_FOLLOWING")
            current_state = LINE_FOLLOWING
            sleep_ms(250)

        sleep_ms(20)

finally:
    alvik.stop()
    print("Race finished.")
