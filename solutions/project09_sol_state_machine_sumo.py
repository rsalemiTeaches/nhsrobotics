# Project 09: The State Machine Sumo Bot
#
# This project refactors the priority-based logic from Project 07
# into a formal state machine. This solution includes the "Flex"
# challenge and a formal "WAITING_FOR_START" state.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms

# NOTE: We are assuming that a 'get_closest_distance' function exists
# in the 'nhs_robotics.py' library file.
from nhs_robotics import get_closest_distance

# --- Configuration Constants ---
# SENSOR THRESHOLDS
WHITE_THRESHOLD = 500  # Value that indicates the white line is detected
ATTACK_DISTANCE = 200  # Distance in mm to trigger a potential attack

# MOTOR SPEEDS
SEARCH_SPEED = 20
ATTACK_SPEED = 50

# --- State Definitions ---
# Using constants makes the code much more readable and less error-prone.
STATE_SEARCHING = 0
STATE_ATTACKING = 1
STATE_EVADING = 2
STATE_CONFIRMING_TARGET = 3 # The new state for the "Flex" challenge
STATE_WAITING_FOR_START = 4 # The new state for the initial wait period

alvik = ArduinoAlvik()

try:
    alvik.begin()

    # The robot now starts in the WAITING_FOR_START state.
    current_state = STATE_WAITING_FOR_START
    print("Ready for Sumo! Press OK to begin.")

    while not alvik.get_touch_cancel():
        
        # --- SENSE ---
        # Get sensor readings once at the beginning of each loop.
        # Note: We only need to do this if we are not in the waiting state.
        if current_state != STATE_WAITING_FOR_START:
            l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()
            all_distances = alvik.get_distance()
            # CORRECTED: Use the '*' to unpack the tuple into 5 arguments.
            closest_distance = get_closest_distance(*all_distances)

        # --- THINK & ACT (The State Machine) ---
        
        # --- WAITING_FOR_START STATE ---
        if current_state == STATE_WAITING_FOR_START:
            # ACT: Blink yellow LEDs to show it's ready.
            alvik.left_led.set_color(1, 1, 0)
            alvik.right_led.set_color(1, 1, 0)
            sleep_ms(100)
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)
            sleep_ms(100)
            
            # THINK: Check for the transition condition (OK button press).
            if alvik.get_touch_ok():
                print("Match Start!")
                print("Transition: WAITING -> SEARCHING")
                current_state = STATE_SEARCHING

        # --- SEARCHING STATE ---
        elif current_state == STATE_SEARCHING:
            # ACT: Drive forward slowly, LEDs green.
            alvik.set_wheels_speed(SEARCH_SPEED, SEARCH_SPEED)
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
            
            # THINK: Check for transitions to other states.
            if l_sensor > WHITE_THRESHOLD or r_sensor > WHITE_THRESHOLD:
                print("Transition: SEARCHING -> EVADING (Edge detected)")
                current_state = STATE_EVADING
            elif closest_distance < ATTACK_DISTANCE:
                print("Transition: SEARCHING -> CONFIRMING_TARGET (Potential target found)")
                current_state = STATE_CONFIRMING_TARGET

        # --- CONFIRMING_TARGET STATE (Flex Challenge) ---
        elif current_state == STATE_CONFIRMING_TARGET:
            # ACT: Briefly stop and set LEDs to purple.
            alvik.brake()
            alvik.left_led.set_color(1, 0, 1)
            alvik.right_led.set_color(1, 0, 1)
            
            # THINK: Immediately check the center sensor to resolve ambiguity.
            center_distance = all_distances[2]
            
            if center_distance < ATTACK_DISTANCE:
                print("Transition: CONFIRMING -> ATTACKING (Target confirmed)")
                current_state = STATE_ATTACKING
            else:
                print("Transition: CONFIRMING -> EVADING (Target was false alarm)")
                current_state = STATE_EVADING

        # --- ATTACKING STATE ---
        elif current_state == STATE_ATTACKING:
            # ACT: Drive forward fast, LEDs red.
            alvik.set_wheels_speed(ATTACK_SPEED, ATTACK_SPEED)
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            
            # THINK: Check for transitions to other states.
            if l_sensor > WHITE_THRESHOLD or r_sensor > WHITE_THRESHOLD:
                print("Transition: ATTACKING -> EVADING (Edge detected during attack)")
                current_state = STATE_EVADING
            elif closest_distance >= ATTACK_DISTANCE:
                print("Transition: ATTACKING -> SEARCHING (Opponent lost)")
                current_state = STATE_SEARCHING

        # --- EVADING STATE ---
        elif current_state == STATE_EVADING:
            # ACT: Perform the full evasive maneuver. LEDs blue.
            print("Executing Evasive Maneuver...")
            alvik.left_led.set_color(0, 0, 1)
            alvik.right_led.set_color(0, 0, 1)
            
            alvik.brake()
            alvik.move(-5, 'cm')
            alvik.rotate(180, 'deg')
            
            # THINK: After evading, always go back to searching.
            print("Transition: EVADING -> SEARCHING (Maneuver complete)")
            current_state = STATE_SEARCHING

finally:
    print("Match finished. Stopping robot.")
    alvik.stop()

