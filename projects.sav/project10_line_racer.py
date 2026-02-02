# Project 10: The Line Racer (Starter Code)
#
# GOAL:
# Combine proportional line-following with obstacle avoidance
# to create a multi-step state machine.
#
# This file provides the skeleton. Your job is to fill in the
# # WORK: sections to complete the logic.

from arduino_alvik import ArduinoAlvik
import time
from nhs_robotics import get_closest_distance

# ---------------------------------------------------------------------
# PART 1: CONFIGURATION & STATES
# ---------------------------------------------------------------------

# --- State Constants ---
STATE_WAITING = 1
STATE_RACING = 2
# This is a 4-step maneuver
STATE_AVOID_1_TURN_LEFT_45 = 3 # Turn 45 degrees LEFT
STATE_AVOID_2_DRIVE = 4        # Drive forward
STATE_AVOID_3_TURN_RIGHT_90 = 5 # Turn 90 degrees RIGHT
STATE_AVOID_4_FIND_LINE = 6    # Drive forward until center sensor finds line

# --- Sensor Thresholds ---
OBSTACLE_DISTANCE = 15  # How close to get before avoiding (in cm)
LINE_BLACK_THRESHOLD = 700 # Value to be "on the line"

# --- Motor Speeds ---
RACE_SPEED = 60      # Base speed for line following
FIND_LINE_SPEED = 30 # Speed for re-acquiring the line

# --- Maneuver Constants ---
# WORK: Tune these values!
AVOID_TURN_1 = 45   # Step 1: Turn 45 degrees LEFT
AVOID_DRIVE_CM = 25   # Step 2: Drive 25 cm
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
    KP = 25
    
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
            # --- ACT (This state is complete) ---
            alvik.left_led.set_color(0, 0, 1) # Blue
            alvik.right_led.set_color(0, 0, 1) # Blue
            time.sleep(0.2)
            alvik.left_led.set_color(0, 0, 0) # Off
            alvik.right_led.set_color(0, 0, 0) # Off
            time.sleep(0.2)
            
            # --- THINK (Transitions) ---
            if alvik.get_touch_ok():
                print("Button pressed! Starting race...")
                current_state = STATE_RACING

        
        elif current_state == STATE_RACING:
            # --- ACT (Non-blocking) ---
            alvik.left_led.set_color(0, 1, 0) # Green
            alvik.right_led.set_color(0, 1, 0)
            
            # WORK: Call the 'get_turn_adjustment' function
            # adjustment = ???
            
            # WORK: Calculate 'left_speed' and 'right_speed'
            # left_speed = ???
            # right_speed = ???
            
            # WORK: Set the wheels speed
            # alvik.set_wheels_speed(???, ???)
            
            pass # Remove this 'pass' when you add code
            
            # --- THINK (Transitions) ---
            # WORK: If 'sees_obstacle' is True,
            # stop the robot and change state.
            # if ???:
            #    print("Obstacle detected! Starting avoidance...")
            #    alvik.stop()
            #    current_state = ???
            
            pass # Remove this 'pass' when you add code


        elif current_state == STATE_AVOID_1_TURN_LEFT_45:
            # --- ACT (Blocking) ---
            print(f"AVOID: 1. Turning LEFT {AVOID_TURN_1} degrees")
            alvik.left_led.set_color(1, 1, 0) # Yellow
            alvik.right_led.set_color(1, 1, 0)
            
            # WORK: Use the blocking 'rotate' command
            # alvik.rotate(???)

            # --- THINK (Transitions) ---
            # WORK: This state is done, transition to the next state
            # current_state = ???
            
            pass # Remove this 'pass' when you add code


        elif current_state == STATE_AVOID_2_DRIVE:
            # --- ACT (Blocking) ---
            print(f"AVOID: 2. Driving {AVOID_DRIVE_CM} cm")
            alvik.left_led.set_color(1, 1, 0) # Yellow
            alvik.right_led.set_color(1, 1, 0)
            
            # WORK: Use the blocking 'move' command
            # alvik.move(???)
            
            # --- THINK (Transitions) ---
            # WORK: This state is done, transition to the next state
            # current_state = ???
            
            pass # Remove this 'pass' when you add code


        elif current_state == STATE_AVOID_3_TURN_RIGHT_90:
            # --- ACT (Blocking) ---
            print(f"AVOID: 3. Turning RIGHT {AVOID_TURN_2} degrees")
            alvik.left_led.set_color(1, 1, 0) # Yellow
            alvik.right_led.set_color(1, 1, 0)
            
            # WORK: Use the blocking 'rotate' command
            # alvik.rotate(???)

            # --- THINK (Transitions) ---
            # WORK: This state is done, transition to the next state
            # current_state = ???
            
            pass # Remove this 'pass' when you add code

        
        elif current_state == STATE_AVOID_4_FIND_LINE:
            # --- ACT (Non-blocking) ---
            print("AVOID: 4. Driving forward to FIND line...")
            alvik.left_led.set_color(1, 0, 1) # Purple
            alvik.right_led.set_color(1, 0, 1)
            
            # WORK: Set the wheels to drive forward slowly
            # alvik.set_wheels_speed(???, ???)

            # --- THINK (Transitions) ---
            # WORK: Check if the CENTER line sensor is
            # back on the black line.
            
            # if c_sensor > LINE_BLACK_THRESHOLD:
            #    print("Line found (center sensor)! Resuming race...")
            #    alvik.stop()
            #    current_state = ???
            
            pass # Remove this 'pass' when you
        

        else:
            # Unknown state? Safety default.
            print(f"Error: Unknown state! ({current_state})")
            current_state = STATE_RACING

        
        # --- Yield ---
        time.sleep(0.01)

finally:
    # Cleanup code
    print("Stopping program.")
    alvik.stop()
    