# project06.py
# Version: V01
# Project 06: The Alvi-Pet Survival Challenge
#
# Your Mission: Implement the logic for the Hungry, Eating, and Dead states.
# Use the HAPPY state as a model for how to write the code.

import time
import sys
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot

# --- Constants ---
STATE_HAPPY = 0
STATE_HUNGRY = 1
STATE_EATING = 2
STATE_DEAD = 3

HUNGRY_TIME = 5000 
EATING_TIME = 3000

# --- Setup ---
alvik = ArduinoAlvik()
alvik.begin()        # CRITICAL: Initialize I2C before SuperBot
sb = SuperBot(alvik) # Scans for sensors

# Enable logging
sb.enable_info_logging() 
sb.log_info("Starting Alvi-Pet...")
time.sleep(1)

# Initial State
current_state = STATE_HAPPY
last_state_change = time.ticks_ms()
sb.log_info("STATE: HAPPY")

# Variables for blinking effects (Eating State)
blink_timer = 0
blink_on = False

# Variable for Flex Challenge
death_count = 0

try:
    while True:
        time.sleep_ms(10)        
        now = time.ticks_ms()
        if alvik.get_touch_cancel():
            break

        # =========================================
        # STATE: HAPPY (MODEL)
        # Use this code as an example for the other states!
        # =========================================
        if current_state == STATE_HAPPY:
            # Behavior: Solid Green
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)

            # Transition 1: Time -> HUNGRY (10 seconds)
            if time.ticks_diff(now, last_state_change) > HUNGRY_TIME:
                current_state = STATE_HUNGRY
                last_state_change = now
                sb.log_info("STATE: HUNGRY")
            
            # Transition 2: Feed Button -> EATING (Overfeeding is allowed)
            elif alvik.get_touch_up():
                current_state = STATE_EATING
                last_state_change = now
                sb.log_info("STATE: EATING")

        # =========================================
        # STATE: HUNGRY
        # =========================================
        elif current_state == STATE_HUNGRY:
            # WORK: Set the LEDs to Orange (or Purple) to indicate hunger.
            # Hint: Use alvik.left_led.set_color(...)
            pass 

            # WORK: Implement Transition 1 (Feed Button)
            # If the UP button is pressed (alvik.get_touch_up()):
            #   1. Change current_state to STATE_EATING
            #   2. Update last_state_change to 'now'
            #   3. Log the new state using sb.log_info()

            # Transition 2: Time -> DEAD (8 seconds of neglect)
            # (We have provided this one for you)
            if time.ticks_diff(now, last_state_change) > 8000:
                death_count += 1
                current_state = STATE_DEAD
                last_state_change = now
                sb.log_info(f"STATE: DEAD (x{death_count})")

        # =========================================
        # STATE: EATING
        # =========================================
        elif current_state == STATE_EATING:
            # WORK: Implement the Eating Behavior
            # 1. Use a non-blocking timer to blink the Green LEDs.
            #    (Hint: Use 'blink_timer' and 'blink_on' variables with ticks_diff)
            pass

            # WORK: Implement Transition (Time -> HAPPY)
            # If 3 seconds (EATING_TIME) have passed:
            #   1. Change state back to STATE_HAPPY
            #   2. Reset last_state_change
            #   3. Log the new state

        # =========================================
        # STATE: DEAD
        # =========================================
        elif current_state == STATE_DEAD:
            # WORK: Implement the Dead State
            # 1. Set LEDs to Red
            # 2. Check for the Checkmark button (alvik.get_touch_ok())
            #    If pressed:
            #      - Resurrect! Change state to STATE_HAPPY
            #      - Reset last_state_change
            #      - Log "Resurrecting..." and then "STATE: HAPPY"
            pass

finally:    # Cleanup
    print("Program Stopped")
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    sb.update_display("", "", "")
    alvik.stop()
