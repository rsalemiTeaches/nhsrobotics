# Project 08: Traffic Light State Machine
# In this project, we will formally learn about State Machines by
# programming the Alvik's LEDs to simulate a traffic light.
# This solution includes the "Flex" for the flashing warning light.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms

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
GREEN_DELAY_MS = 5000
YELLOW_DELAY_MS = 2000
ALL_RED_DELAY_MS = 1000
WALK_DELAY_MS = 4000
FLASH_DELAY_MS = 250 # Flex timing

alvik = ArduinoAlvik()

try:
    alvik.begin()

    current_state = STATE_NS_GREEN
    last_green_direction = DIRECTION_NS
    walk_request_pending = False

    while not alvik.get_touch_cancel():

        # --- EVENT HANDLING ---
        if alvik.get_touch_center():
            print("Walk button pressed! Request is now pending.")
            walk_request_pending = True
                
        # --- STATE HANDLING ---
        
        if current_state == STATE_NS_GREEN:
            print("State: NS Green")
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(1, 0, 0)
            last_green_direction = DIRECTION_NS
            sleep_ms(GREEN_DELAY_MS)
            current_state = STATE_NS_YELLOW
            
        elif current_state == STATE_NS_YELLOW:
            print("State: NS Yellow")
            alvik.left_led.set_color(1, 1, 0)
            alvik.right_led.set_color(1, 0, 0)
            sleep_ms(YELLOW_DELAY_MS)
            current_state = STATE_ALL_RED
            
        elif current_state == STATE_EW_GREEN:
            print("State: EW Green")
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(0, 1, 0)
            last_green_direction = DIRECTION_EW
            sleep_ms(GREEN_DELAY_MS)
            current_state = STATE_EW_YELLOW
        
        elif current_state == STATE_EW_YELLOW:
            print("State: EW Yellow")
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 1, 0)
            sleep_ms(YELLOW_DELAY_MS)
            current_state = STATE_ALL_RED

        elif current_state == STATE_ALL_RED:
            print("State: All Red")
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            sleep_ms(ALL_RED_DELAY_MS)

            if walk_request_pending:
                current_state = STATE_WALK
            elif last_green_direction == DIRECTION_NS:
                current_state = STATE_EW_GREEN
            else:
                current_state = STATE_NS_GREEN
                
        elif current_state == STATE_WALK:
            print("State: WALK")
            walk_request_pending = False
            
            alvik.left_led.set_color(0, 0, 1)
            alvik.right_led.set_color(0, 0, 1)
            sleep_ms(WALK_DELAY_MS)
            
            # Transition to the new flashing state
            current_state = STATE_FLASHING_WARN

        elif current_state == STATE_FLASHING_WARN:
            print("State: Flashing Warning")
            # Use a for loop to blink the lights 4 times
            for _ in range(4):
                alvik.left_led.set_color(0, 0, 1) # Blue
                alvik.right_led.set_color(0, 0, 1)
                sleep_ms(FLASH_DELAY_MS)
                alvik.left_led.set_color(0, 0, 0) # Off
                alvik.right_led.set_color(0, 0, 0)
                sleep_ms(FLASH_DELAY_MS)
            
            # After flashing, transition back to the all-red safety state
            current_state = STATE_ALL_RED

finally:
    print("Program finished. Stopping robot.")
    alvik.stop()

