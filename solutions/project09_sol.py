#############################
#         Project 08        #
#        Line Racer         #
#############################

# This project combines everything: smart line following,
# obstacle detection, and pre-programmed maneuvers.
# The robot will use a "state machine" to decide what
# it should be doing at any given moment.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
from nhs_robotics import get_closest_distance

# --- State Machine Definitions ---
# We define our robot's possible states as constants.
# Using names instead of numbers makes the code easier to read.
FOLLOWING_LINE = 1
AVOIDING_OBSTACLE = 2
SEARCHING_FOR_LINE = 3

# --- Configuration ---
# General
BASE_SPEED = 40
OBSTACLE_DISTANCE = 7 # How close to get before avoiding.
FIND_LINE_ANGLE = 60
# Line Following (from Project 06)
KP = 25.0
LINE_LOST_THRESHOLD = 200

# Obstacle Avoidance Maneuver
AVOID_TURN_DEGREES = 90
AVOID_STRAIGHT_CM_1 = 10
AVOID_STRAIGHT_CM_2 = 25

# Line Searching
SEARCH_SPEED = 20

# --- Helper Functions ---

# This is the same "smart" function from Project 06.
def get_turn_adjustment(left_val, center_val, right_val):
    if (left_val + center_val + right_val) < LINE_LOST_THRESHOLD:
        return 0
    
    sum_values = (left_val * 1) + (center_val * 2) + (right_val * 3)
    sum_weight = left_val + center_val + right_val
    centroid = sum_values / sum_weight
    error = centroid - 2
    return error

# --- Main Program ---
alvik = ArduinoAlvik()

# Start in the default state
current_state = FOLLOWING_LINE

try:
    alvik.begin()
    print("Project 08: Line Racer")
    print(f"Current State: FOLLOWING_LINE")
    print("Press OK to start the race!")

    while True:
        if alvik.get_touch_ok():
            break
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

        # SENSE: Get all sensor data at the start of the loop
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()
        raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r = alvik.get_distance()
        closest_distance = get_closest_distance(raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r)

        # THINK & ACT: The State Machine
        
        # --- STATE 1: FOLLOWING THE LINE ---
        if current_state == FOLLOWING_LINE:
            alvik.left_led.set_color(0, 1, 0) # Green lights for following
            alvik.right_led.set_color(0, 1, 0)

            # Check for a transition: Is there an obstacle?
            if closest_distance < OBSTACLE_DISTANCE:
                print("Obstacle detected! Changing state to AVOIDING_OBSTACLE")
                current_state = AVOIDING_OBSTACLE
                alvik.set_wheels_speed(0, 0) # Stop the motors before starting the maneuver
                sleep_ms(250)
            else:
                # Stay in this state and follow the line
                adjustment = get_turn_adjustment(l_sensor, c_sensor, r_sensor)
                control_signal = adjustment * KP
                alvik.set_wheels_speed(BASE_SPEED + control_signal, BASE_SPEED - control_signal)

        # --- STATE 2: AVOIDING THE OBSTACLE ---
        elif current_state == AVOIDING_OBSTACLE:
            alvik.left_led.set_color(1, 1, 0) # Yellow lights for avoiding
            alvik.right_led.set_color(1, 1, 0)
            
            # Execute the pre-programmed maneuver.
            # These are "blocking" calls, so the program will wait
            # for each movement to finish before starting the next.
            alvik.rotate(AVOID_TURN_DEGREES)       # Turn right
            alvik.move(AVOID_STRAIGHT_CM_1)        # Go straight
            alvik.rotate(-AVOID_TURN_DEGREES)      # Turn left
            alvik.move(AVOID_STRAIGHT_CM_2)        # Go straight to pass obstacle
            alvik.rotate(-AVOID_TURN_DEGREES)      # Turn left to face the line
            
            # Transition: Maneuver is done, now find the line.
            print("Avoidance maneuver complete. Changing state to SEARCHING_FOR_LINE")
            current_state = SEARCHING_FOR_LINE
            
        # --- STATE 3: SEARCHING FOR THE LINE ---
        elif current_state == SEARCHING_FOR_LINE:
            alvik.left_led.set_color(0, 0, 1) # Blue lights for searching
            alvik.right_led.set_color(0, 0, 1)

            # Check for a transition: Have we found the line?
            # We check if ANY of the sensors sees black.
            if (l_sensor + c_sensor + r_sensor) > LINE_LOST_THRESHOLD:
                print("Line found! Changing state to FOLLOWING_LINE")
                # Stop briefly before the next action
                alvik.set_wheels_speed(0, 0)
                # Do a small corrective turn to get fully back on the line
                alvik.rotate(FIND_LINE_ANGLE)
                current_state = FOLLOWING_LINE
            else:
                # Stay in this state and drive forward slowly.
                alvik.set_wheels_speed(SEARCH_SPEED, SEARCH_SPEED)

        sleep_ms(20)

finally:
    alvik.stop()
    print("Race finished.")
