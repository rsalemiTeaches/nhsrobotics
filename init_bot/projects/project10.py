#############################
#         Project 10        #
#          Line Racer       #
#############################

# This project uses a fine-grained state machine
# to navigate the line and avoid an obstacle. Each step of the
# avoidance maneuver is its own state. It also adds sound
# effects using the Qwiic Buzzer for better feedback.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
from nhs_robotics import get_closest_distance, Buzzer

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
KP = 25.0
LINE_FOUND_THRESHOLD = 400 # If the max sensor value is over this, we see the line.
SEARCH_SPEED = 20

# Maneuver Configuration - Tuned for a quicker race
# NOTE: Negative values turn the robot RIGHT, Positive values turn LEFT.
AVOID_TURN_1 = -90 # First turn RIGHT, away from the line
AVOID_STRAIGHT_1 = 15
AVOID_TURN_2 = 90  # Turn LEFT to be parallel
AVOID_STRAIGHT_2 = 25
AVOID_TURN_3 = 90  # Turn LEFT again to head back towards the line
ALIGN_TURN = -70   # Final turn RIGHT to align with the line

# --- Helper Functions ---
def get_turn_adjustment(left_val, center_val, right_val):
    if max(left_val, center_val, right_val) < LINE_FOUND_THRESHOLD:
        return 0
    sum_values = (left_val * 1) + (center_val * 2) + (right_val * 3)
    sum_weight = left_val + center_val + right_val
    if sum_weight == 0:
        return 0
    centroid = sum_values / sum_weight
    error = centroid - 2
    return error

# --- Main Program ---
alvik = ArduinoAlvik()
my_buzzer = Buzzer()

current_state = LINE_FOLLOWING

try:
    alvik.begin()
    print("Project 10: Advanced Line Racer")
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

        # SENSE: Always get fresh sensor data
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()
        raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r = alvik.get_distance()
        closest_distance = get_closest_distance(raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r)

        # --- THINK & ACT: The Fine-Grained State Machine ---
        
        # This state is complete for you as an example.
        if current_state == LINE_FOLLOWING:
            alvik.left_led.set_color(0, 1, 0) # Green
            if closest_distance < OBSTACLE_DISTANCE:
                current_state = SEE_OBSTACLE
            else:
                adjustment = get_turn_adjustment(l_sensor, c_sensor, r_sensor)
                control_signal = adjustment * KP
                alvik.set_wheels_speed(BASE_SPEED + control_signal, BASE_SPEED - control_signal)

        # This state is also complete for you.
        elif current_state == SEE_OBSTACLE:
            alvik.set_wheels_speed(0, 0)
            my_buzzer.play_effect(my_buzzer.EFFECT_NO) # Warning sound
            print("State: SEE_OBSTACLE -> DRIVE_FROM_LINE")
            current_state = DRIVE_FROM_LINE
            sleep_ms(500)

        elif current_state == DRIVE_FROM_LINE:
            alvik.left_led.set_color(1, 1, 0) # Yellow
            alvik.right_led.set_color(1, 1, 0)
            # WORK: Call alvik.rotate() and alvik.move() to perform the
            # WORK: first part of the avoidance maneuver. Use the constants
            # WORK: AVOID_TURN_1 and AVOID_STRAIGHT_1.
            
            print("State: DRIVE_FROM_LINE -> DRIVE_AROUND")
            current_state = DRIVE_AROUND

        elif current_state == DRIVE_AROUND:
            alvik.left_led.set_color(1, 1, 0) # Yellow
            alvik.right_led.set_color(1, 1, 0)
            # WORK: Call alvik.rotate() and alvik.move() twice to complete
            # WORK: the maneuver around the obstacle. Use the constants
            # WORK: AVOID_TURN_2, AVOID_STRAIGHT_2, and AVOID_TURN_3.
            
            # WORK: After the maneuver is done, set the current_state
            # WORK: to LOOK_FOR_THE_LINE.
            
            print("State: DRIVE_AROUND -> LOOK_FOR_THE_LINE")
            
        elif current_state == LOOK_FOR_THE_LINE:
            alvik.left_led.set_color(0, 0, 1) # Blue
            alvik.right_led.set_color(0, 0, 1)
            my_buzzer.set_frequency(1500)
            my_buzzer.set_duration(100)
            my_buzzer.on()
            
            # WORK: Set the wheel speed to SEARCH_SPEED to drive forward.
            
            # WORK: Write an if statement to check if the robot has found the
            # WORK: line again. Use max() and LINE_FOUND_THRESHOLD.
            # WORK: If it has found the line, change the current_state to FOUND_THE_LINE.
            
        
        # WORK: Write the entire final state, `FOUND_THE_LINE`, from scratch.
        # WORK: It should be an `elif` block that checks if the
        # WORK: current_state is equal to FOUND_THE_LINE.
        # WORK: Inside, it should:
        # WORK: 1. Stop the robot.
        # WORK: 2. Play the "Yes" sound effect.
        # WORK: 3. Perform the final alignment turn using ALIGN_TURN.
        # WORK: 4. Change the current_state back to LINE_FOLLOWING.
        
        sleep_ms(20)

finally:
    my_buzzer.off()
    alvik.stop()
    print("Race finished.")
