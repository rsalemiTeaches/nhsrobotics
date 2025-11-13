# Project 09: The State Machine Sumo Bot (Starter Code)
#
# GOAL:
# Convert your Project 07 Sumo Bot (which used if/elif/else)
# into a formal State Machine, just like the Traffic Light.
#
# This file provides the complete "skeleton" of the state machine.
# Your job is to fill in the # WORK: sections to make it function.

from arduino_alvik import ArduinoAlvik
import time
# Import the helper function to find the closest object
from nhs_robotics import get_closest_distance

# ---------------------------------------------------------------------
# PART 1: CONFIGURATION & STATES
# ---------------------------------------------------------------------

# --- State Constants ---
# We define our states as "constant" variables.
# This makes the code much easier to read.
STATE_WAITING = 1
STATE_SEARCHING = 2
STATE_ATTACKING = 3
STATE_EVADING = 4

# --- Sensor Thresholds ---
# The 'get_line_sensors()' function returns a HIGH value (near 1000)
# for the BLACK line, and a LOW value (near 0) for the WHITE edge.
WHITE_THRESHOLD = 300  # If sensor value is LESS than this, we see white.
ATTACK_DISTANCE = 18   # How close an opponent must be to attack (in cm)

# --- Motor Speeds ---
SEARCH_SPEED = 30
ATTACK_SPEED = 80
EVADE_TURN_SPEED = 50

# ---------------------------------------------------------------------
# PART 2: THE STATE MACHINE
# ---------------------------------------------------------------------


print("Starting Project 09: State Machine Sumo Bot...")

alvik = ArduinoAlvik()
alvik.begin()

# Initialize the starting state
current_state = STATE_WAITING

try:
    while not alvik.get_touch_cancel():

        # --- SENSE (Read sensors ONCE at the top) ---
        # This is more efficient. We read all sensors, then
        # use these variables in the state logic.
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()
        all_distances = alvik.get_distance()
        
        # Use the '*' to unpack the 5 values into the helper function
        closest_dist = get_closest_distance(*all_distances) 
        
        # Check for the white edge
        sees_white_left = l_sensor < WHITE_THRESHOLD
        sees_white_right = r_sensor < WHITE_THRESHOLD
        sees_white_edge = sees_white_left or sees_white_right
        
        # Check for an opponent
        sees_opponent = closest_dist < ATTACK_DISTANCE


        # ---------------------------------------------------------
        # --- THINK / ACT (The State Machine) ---
        # ---------------------------------------------------------

        if current_state == STATE_WAITING:
            # --- ACT ---
            # Blink lights to show we are waiting
            alvik.left_led.set_color(0, 0, 1) # Blue
            alvik.right_led.set_color(0, 0, 1) # Blue
            time.sleep(0.2)
            alvik.left_led.set_color(0, 0, 0) # Off
            alvik.right_led.set_color(0, 0, 0) # Off
            time.sleep(0.2)
            
            # --- THINK (Transitions) ---
            # WORK: If the OK button is pressed,
            # change the current_state to STATE_SEARCHING.
            if alvik.get_touch_ok():
                print("Button pressed! Starting search...")
                # WORK: Set the current_state variable here
                # current_state = ???
                pass # Remove this 'pass'

        
        elif current_state == STATE_SEARCHING:
            # --- ACT ---
            # Set LEDs to GREEN and drive forward slowly
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
            alvik.set_wheels_speed(SEARCH_SPEED, SEARCH_SPEED)

            # --- THINK (Transitions) ---
            # WORK: Check for transitions, IN PRIORITY ORDER.
            
            # Priority 1: Do we see the white edge?
            # if sees_white_edge:
            #    print("Edge detected! Evading...")
            #    current_state = ???

            # Priority 2: Do we see an opponent?
            # elif sees_opponent:
            #    print("Opponent detected! Attacking...")
            #    current_state = ???
            
            # (If neither, we stay in this state)
            pass # Remove this 'pass'


        elif current_state == STATE_ATTACKING:
            # --- ACT ---
            # Set LEDs to RED and charge forward!
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            alvik.set_wheels_speed(ATTACK_SPEED, ATTACK_SPEED)

            # --- THINK (Transitions) ---
            # WORK: Check for transitions, IN PRIORITY ORDER.
            
            # Priority 1: Do we see the white edge?
            # (We MUST check this first, even during attack!)
            # if sees_white_edge:
            #    print("Edge detected! Evading...")
            #    current_state = ???

            # Priority 2: Did we lose the opponent?
            # (Check if 'sees_opponent' is now False)
            # elif not sees_opponent:
            #    print("Opponent lost. Resuming search...")
            #    current_state = ???
            
            # (If neither, we stay in this state)
            pass # Remove this 'pass'


        elif current_state == STATE_EVADING:
            # --- ACT ---
            # This state is special. It performs a sequence of
            # BLOCKING moves and then *automatically* transitions.
            
            print("EVADING: Backing up...")
            alvik.left_led.set_color(1, 1, 0) # Yellow
            alvik.right_led.set_color(1, 1, 0) # Yellow
            
            # We use the new blocking move commands here!
            alvik.move(-10) # Move backwards 10 cm
            
            print("EVADING: Turning...")
            
            # WORK: Decide which way to turn.
            # If the left sensor saw white, we should turn RIGHT.
            # If the right sensor saw white, we should turn LEFT.
            
            if sees_white_left:
                alvik.rotate(-90) # Turn RIGHT 90 degrees
            elif sees_white_right:
                alvik.rotate(90) # Turn LEFT 90 degrees
            else:
                # Both saw white? Just turn left.
                alvik.rotate(90)

            # --- THINK (Transition) ---
            # Since the evasion move is "done", we can
            # immediately go back to searching.
            print("Evasion complete. Resuming search.")
            current_state = STATE_SEARCHING

        
        else:
            # Unknown state? Safety default.
            print(f"Error: Unknown state! ({current_state})")
            current_state = STATE_SEARCHING

        
        # --- Yield ---
        # This sleep is essential for a non-blocking loop
        time.sleep(0.01)

except Exception as e:
    print(f"An error occurred: {e}")
    
finally:
    # Cleanup code
    print("Stopping program.")
    alvik.stop()
