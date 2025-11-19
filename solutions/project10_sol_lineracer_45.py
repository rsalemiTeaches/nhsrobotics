# Project 10: The Line Racer (Starter Code)
#
# GOAL:
# Combine proportional line-following with obstacle avoidance
# to create a multi-step state machine.
#
# This file provides the skeleton. Your job is to fill in the
# # WORK: sections to complete the logic.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
from nhs_robotics import get_closest_distance

# ---------------------------------------------------------------------
# PART 1: CONFIGURATION & STATES
# ---------------------------------------------------------------------

# --- State Constants ---
STATE_WAITING = 1
STATE_RACING = 2
# This is now a 4-step maneuver based on your new logic
STATE_AVOID_1_TURN_LEFT_45 = 3 # Turn 45 degrees LEFT
STATE_AVOID_2_DRIVE = 4        # Drive forward
STATE_AVOID_3_TURN_RIGHT_90 = 5 # Turn 90 degrees RIGHT
STATE_AVOID_4_FIND_LINE = 6    # Drive forward until center sensor finds line
STATE_TURN_TO_LINE = 7
# --- Sensor Thresholds ---
OBSTACLE_DISTANCE = 7  # How close to get before avoiding (in cm)
LINE_BLACK_THRESHOLD = 700 # Value to be "on the line"

# --- Motor Speeds ---
RACE_SPEED = 35      # Base speed for line following
FIND_LINE_SPEED = 30 # Speed for re-acquiring the line

# --- Maneuver Constants ---
# WORK: Tune these values!
AVOID_TURN_1 = 45   # Step 1: Turn 45 degrees LEFT
AVOID_DRIVE_CM = 15   # Step 2: Drive 25 cm
AVOID_TURN_2 = -90  # Step 3: Turn 90 degrees RIGHT

# ---------------------------------------------------------------------
# PART 2: HELPER FUNCTION (From Project 06)
# ---------------------------------------------------------------------

def get_turn_adjustment(l_sensor, c_sensor, r_sensor):
    """
    Calculates the proportional 'error' for line following.
    This is the "brain" of the smart line follower.
    """
    global LINE_BLACK_THRESHOLD
    
    # Check for "line lost" (all sensors see white)
    sum_all = l_sensor + c_sensor + r_sensor
    if sum_all < (LINE_BLACK_THRESHOLD / 2):
        return 0

    # The "centroid" algorithm from Project 06
    weighted_sum = (l_sensor * 1) + (c_sensor * 2) + (r_sensor * 3)
    centroid = weighted_sum / sum_all
    
    # Calculate the error
    error = centroid - 2.0
    
    # KP is the "Proportional Gain"
    KP = 50
    
    adjustment = error * KP
    return adjustment

# ---------------------------------------------------------------------
# PART 3: THE STATE MACHINE
# ---------------------------------------------------------------------

print("Starting Project 10: The Line Racer...")

alvik = ArduinoAlvik()
alvik.begin()

# Initialize the starting state
current_state = STATE_WAITING

try:
    while not alvik.get_touch_cancel():

        # --- SENSE (Read sensors ONCE at the top) ---
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()
        
        dist_left, dist_front_left, dist_center, dist_front_right, dist_right = alvik.get_distance()
        closest_dist = get_closest_distance(dist_left, dist_front_left, dist_center, dist_front_right, dist_right) 
        
        # Check for an obstacle
        sees_obstacle = closest_dist < OBSTACLE_DISTANCE


        # ---------------------------------------------------------
        # --- THINK / ACT (The State Machine) ---
        # ---------------------------------------------------------

        if current_state == STATE_WAITING:
            # --- ACT ---
            alvik.left_led.set_color(0, 0, 1) # Blue
            alvik.right_led.set_color(0, 0, 1) # Blue
            sleep_ms(200)
            alvik.left_led.set_color(0, 0, 0) # Off
            alvik.right_led.set_color(0, 0, 0) # Off
            sleep_ms(200)
            
            # --- THINK (Transitions) ---
            if alvik.get_touch_ok():
                print("Button pressed! Starting race...")
                current_state = STATE_RACING

        
        elif current_state == STATE_RACING:
            # --- ACT (Non-blocking) ---
            alvik.left_led.set_color(0, 1, 0) # Green
            alvik.right_led.set_color(0, 1, 0)
            
            adjustment = get_turn_adjustment(l_sensor, c_sensor, r_sensor)
            left_speed = RACE_SPEED + adjustment
            right_speed = RACE_SPEED - adjustment
            alvik.set_wheels_speed(left_speed, right_speed)
            
            # --- THINK (Transitions) ---
            if sees_obstacle:
               print("Obstacle detected! Starting avoidance...")
               alvik.set_wheels_speed(0,0)
               current_state = STATE_AVOID_1_TURN_LEFT_45 


        elif current_state == STATE_AVOID_1_TURN_LEFT_45:
            # --- ACT (Blocking) ---
            print(f"AVOID: 1. Turning LEFT {AVOID_TURN_1} degrees")
            alvik.left_led.set_color(1, 1, 0) # Yellow
            alvik.right_led.set_color(1, 1, 0)
            
            alvik.rotate(AVOID_TURN_1) # Turn 45 deg LEFT

            # --- THINK (Transitions) ---
            current_state = STATE_AVOID_2_DRIVE


        elif current_state == STATE_AVOID_2_DRIVE:
            # --- ACT (Blocking) ---
            print(f"AVOID: 2. Driving {AVOID_DRIVE_CM} cm")
            alvik.left_led.set_color(1, 1, 0) # Yellow
            alvik.right_led.set_color(1, 1, 0)
            
            alvik.move(AVOID_DRIVE_CM)
            
            # --- THINK (Transitions) ---
            current_state = STATE_AVOID_3_TURN_RIGHT_90


        elif current_state == STATE_AVOID_3_TURN_RIGHT_90:
            # --- ACT (Blocking) ---
            print(f"AVOID: 3. Turning RIGHT {AVOID_TURN_2} degrees")
            alvik.left_led.set_color(1, 1, 0) # Yellow
            alvik.right_led.set_color(1, 1, 0)
            
            alvik.rotate(AVOID_TURN_2) # Turn 90 deg RIGHT

            # --- THINK (Transitions) ---
            current_state = STATE_AVOID_4_FIND_LINE

        
        elif current_state == STATE_AVOID_4_FIND_LINE:
            # --- ACT (Non-blocking) ---
            print("AVOID: 4. Driving forward to FIND line...")
            alvik.left_led.set_color(1, 0, 1) # Purple
            alvik.right_led.set_color(1, 0, 1)
            
            alvik.set_wheels_speed(FIND_LINE_SPEED, FIND_LINE_SPEED)
            
            if c_sensor > LINE_BLACK_THRESHOLD/2:
                print("Line found (center sensor)! Resuming race...")
                alvik.set_wheels_speed(0,0)
                current_state = STATE_TURN_TO_LINE
        elif current_state == STATE_TURN_TO_LINE:
            alvik.rotate(45)
            current_state = STATE_RACING
        else:
            # Unknown state? Safety default.
            print(f"Error: Unknown state! ({current_state})")
            current_state = STATE_RACING

        
        # --- Yield ---
        sleep_ms(10)

finally:
    # Cleanup code
    print("Stopping program.")
    alvik.stop()