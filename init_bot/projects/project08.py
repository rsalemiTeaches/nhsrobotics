# Project 08: Traffic Light State Machine
# In this project, you will formally learn about State Machines by
# programming the Alvik's LEDs to simulate a traffic light.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
from nhs_robotics import NanoLED  # Import our new helper library

# --- State Definitions ---
STATE_NS_GREEN = 0
STATE_NS_YELLOW = 1
STATE_EW_GREEN = 2
STATE_EW_YELLOW = 3
STATE_ALL_RED = 4
STATE_WALK = 5
STATE_FLASHING_WARN = 6 # Flex State

# --- Direction Constants ---
DIRECTION_NS = 0
DIRECTION_EW = 1

# --- Timing Constants (in milliseconds) ---
GREEN_DELAY_MS = 3000
YELLOW_DELAY_MS = 1000
ALL_RED_DELAY_MS = 1000
WALK_DELAY_MS = 4000
FLASH_DELAY_MS = 250 # Flex timing

alvik = ArduinoAlvik()
# Create a controller for the Nano's onboard LED
nano_led = NanoLED()

try:
    alvik.begin()

    current_state = STATE_ALL_RED # Start at a safe state
    last_green_direction = DIRECTION_EW
    walk_request_pending = False

    while not alvik.get_touch_cancel():

        # --- EVENT HANDLING ---
        # WORK: Check if the center button is pressed using alvik.get_touch_center().
        # If it is, set the walk_request_pending flag to True.
        # As part of the user feedback, turn the Nano's onboard LED white.
        # Remember to set its brightness to 100%.
        pass # Remove this line when you add your code
                
        # --- STATE HANDLING ---
        
        if current_state == STATE_NS_GREEN:
            print("State: NS Green")
            # WORK: Set the Alvik's main LEDs for this state.
            # WORK: Remember which direction was green last.
            # WORK: Wait for the correct delay.
            # WORK: Transition to the next state.
            pass # Remove this line
            
        elif current_state == STATE_NS_YELLOW:
            print("State: NS Yellow")
            # WORK: Set the Alvik's main LEDs for this state.
            # WORK: Wait for the correct delay.
            # WORK: Transition to the next state.
            pass # Remove this line
            
        elif current_state == STATE_EW_GREEN:
            print("State: EW Green")
            # WORK: Set the Alvik's main LEDs for this state.
            # WORK: Remember which direction was green last.
            # WORK: Wait for the correct delay.
            # WORK: Transition to the next state.
            pass # Remove this line
        
        elif current_state == STATE_EW_YELLOW:
            print("State: EW Yellow")
            # WORK: Set the Alvik's main LEDs for this state.
            # WORK: Wait for the correct delay.
            # WORK: Transition to the next state.
            pass # Remove this line

        elif current_state == STATE_ALL_RED:
            print("State: All Red")
            # WORK: Set the Alvik's main LEDs for this state.
            # WORK: Wait for the correct delay.
            # WORK: This is the "brain". Write an if/elif/else block to decide
            # what the next state should be. Check for a walk request first!
            pass # Remove this line
                
        elif current_state == STATE_WALK:
            print("State: WALK")
            # WORK: The walk request has been handled, so reset the flag to False.
            # WORK: Turn the Nano LED off.
            # WORK: Set the Alvik's main LEDs to blue for the walk signal.
            # WORK: Wait for the correct delay.
            # WORK: Transition to the flashing warning state.
            pass # Remove this line

        elif current_state == STATE_FLASHING_WARN:
            # FLEX: This is the challenge state.
            print("State: Flashing Warning")
            # WORK: Use a for loop to make the main LEDs blink blue 4 times.
            # WORK: After the loop, transition to the all-red safety state.
            pass # Remove this line

finally:
    print("Program finished. Stopping robot.")
    # WORK: Make sure ALL LEDs (Alvik's and Nano's) are turned off.
    # WORK: Stop the robot.
    pass # Remove this line

