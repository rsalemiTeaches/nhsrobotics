# project06_solution.py
# Version: V05
# Project 06: The Alvi-Pet Survival Challenge (Solution)
#
# This program implements a State Machine to simulate a virtual pet.
# It uses non-blocking timers (ticks_ms) for all logic.
#
# States:
# - HAPPY:   Green LEDs. Transitions to HUNGRY after 10s.
# - HUNGRY:  Orange LEDs. Transitions to DEAD after 8s if not fed.
# - EATING:  Flashing Green. Lasts 3s then returns to HAPPY.
# - DEAD:    Red LEDs. Terminal state. Resets with Checkmark.

import time
import sys
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot

# --- Constants ---
# Use integers for state values (efficient and standard practice)
STATE_HAPPY = 0
STATE_HUNGRY = 1
STATE_EATING = 2
STATE_DEAD = 3

HUNGRY_TIME = 5000 # Reduced to 5s for faster testing
EATING_TIME = 3000

# --- Setup ---
alvik = ArduinoAlvik()
alvik.begin()        # CRITICAL: Initialize I2C before SuperBot
sb = SuperBot(alvik) # Scans for sensors


# Enable logging
sb.enable_info_logging() # <--- REQUIRED to write to messages.log
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
        # Get the current time for this loop iteration
        now = time.ticks_ms()
        if alvik.get_touch_cancel():
            break

        # =========================================
        # STATE: HAPPY
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
            # Behavior: Solid Orange (Red + Blue mixed for Purple/Orange look)
            alvik.left_led.set_color(1, 0, 1) 
            alvik.right_led.set_color(1, 0, 1)

            # Transition 1: Feed Button -> EATING (Saved!)
            if alvik.get_touch_up():
                current_state = STATE_EATING
                last_state_change = now
                sb.log_info("STATE: EATING")

            # Transition 2: Time -> DEAD (8 seconds of neglect)
            elif time.ticks_diff(now, last_state_change) > 8000:
                death_count += 1
                current_state = STATE_DEAD
                last_state_change = now
                # Log the death count (Flex Challenge)
                sb.log_info(f"STATE: DEAD (x{death_count})")

        # =========================================
        # STATE: EATING
        # =========================================
        elif current_state == STATE_EATING:
            # Behavior: Fast Flash Green (Non-blocking!)
            if time.ticks_diff(now, blink_timer) > 100:
                blink_timer = now
                blink_on = not blink_on
                if blink_on:
                    alvik.left_led.set_color(0, 1, 0)
                    alvik.right_led.set_color(0, 1, 0)
                else:
                    alvik.left_led.set_color(0, 0, 0)
                    alvik.right_led.set_color(0, 0, 0)
            
            # Transition: Time -> HAPPY (3 seconds)
            if time.ticks_diff(now, last_state_change) > EATING_TIME:
                current_state = STATE_HAPPY
                last_state_change = now
                sb.log_info("STATE: HAPPY")

        # =========================================
        # STATE: DEAD
        # =========================================
        elif current_state == STATE_DEAD:
            # Behavior: Solid Red
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)

            # Transition: Checkmark -> HAPPY (Resurrection)
            if alvik.get_touch_ok():
                current_state = STATE_HAPPY
                last_state_change = now
                sb.log_info("Resurrecting...")
                time.sleep(1) # Small pause for effect
                sb.log_info("STATE: HAPPY")

finally:    # Cleanup
    print("Program Stopped")
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    sb.update_display("", "", "")
    alvik.stop()