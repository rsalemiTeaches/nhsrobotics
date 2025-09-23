# Project 08: Traffic Light State Machine
# Your task is to complete the code in the sections marked with "WORK:".

from arduino_alvik import ArduinoAlvik
from time import sleep_ms

# --- State Definitions ---
STATE_NS_GREEN = 0
STATE_NS_YELLOW = 1
STATE_EW_GREEN = 2
STATE_EW_YELLOW = 3
STATE_ALL_RED = 4
STATE_WALK = 5
# WORK (Flex): Add the new state for the flashing warning signal
STATE_FLASHING_WARN = 6

# --- Direction Constants ---
DIRECTION_NS = 0
DIRECTION_EW = 1

# --- Timing Constants (in milliseconds) ---
GREEN_DELAY_MS = 5000
YELLOW_DELAY_MS = 2000
ALL_RED_DELAY_MS = 1000
WALK_DELAY_MS = 4000
FLASH_DELAY_MS = 250 # For the flex

alvik = ArduinoAlvik()

try:
    alvik.begin()

    current_state = STATE_NS_GREEN
    last_green_direction = DIRECTION_NS
    walk_request_pending = False

    while not alvik.get_touch_cancel():

        # --- EVENT HANDLING ---
        # WORK: Check if the center button is pressed. If it is,
        # set the walk_request_pending flag to True.
        if alvik.get_touch_center():
            print("Walk button pressed! Request is now pending.")
            walk_request_pending = True

        # --- STATE HANDLING ---
        
        if current_state == STATE_NS_GREEN:
            print("State: NS Green")
            # WORK: Set Left LED to Green, Right LED to Red
            # WORK: Set the last_green_direction
            # WORK: sleep for GREEN_DELAY_MS
            # WORK: Transition to the next state (NS_YELLOW)
            
        elif current_state == STATE_NS_YELLOW:
            print("State: NS Yellow")
            # WORK: Set Left LED to Yellow, Right LED to Red
            # WORK: sleep for YELLOW_DELAY_MS
            # WORK: Transition to the next state (ALL_RED)
            
        elif current_state == STATE_EW_GREEN:
            print("State: EW Green")
            # WORK: Set Left LED to Red, Right LED to Green
            # WORK: Set the last_green_direction
            # WORK: sleep for GREEN_DELAY_MS
            # WORK: Transition to the next state (EW_YELLOW)
        
        elif current_state == STATE_EW_YELLOW:
            print("State: EW Yellow")
            # WORK: Set Left LED to Red, Right LED to Yellow
            # WORK: sleep for YELLOW_DELAY_MS
            # WORK: Transition to the next state (ALL_RED)

        elif current_state == STATE_ALL_RED:
            print("State: All Red")
            # WORK: Set both LEDs to Red
            # WORK: sleep for ALL_RED_DELAY_MS

            # This is the "thinking" part of the state machine.
            # WORK: Write an if/elif/else block to decide the next state.
            # - If walk_request_pending is True, go to STATE_WALK.
            # - Else if the last green was NS, go to STATE_EW_GREEN.
            # - Otherwise, go to STATE_NS_GREEN.
                
        elif current_state == STATE_WALK:
            print("State: WALK")
            # WORK: The first thing to do here is to reset the
            # walk_request_pending flag to False.
            
            # WORK: Set both LEDs to Blue
            # WORK: sleep for WALK_DELAY_MS
            
            # WORK: Transition to the next state.
            # For the main project, this goes to ALL_RED.
            # For the flex, this goes to FLASHING_WARN.
        
        # WORK (Flex): Add an elif block here for STATE_FLASHING_WARN
        # Inside, use a for loop to blink the lights blue a few times.
        # After the loop, transition to STATE_ALL_RED.

            
finally:
    print("Program finished. Stopping robot.")
    alvik.stop()

