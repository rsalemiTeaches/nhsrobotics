# Sumo Bot V11 (Student Scaffold)
# Solution for Project 08: The State Machine Sumo Bot (Survival Mode)
# Instructions: Look for the word 'WORK' to see where you need to add code!

from time import sleep_ms, ticks_ms, ticks_diff
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot

# 1. Initialize Alvik first to start I2C threads
alvik = ArduinoAlvik()
alvik.begin()

# 2. Wrap it with our SuperBot library
sb = SuperBot(alvik)

# --- CONSTANTS ---
# States defined as numbers to prevent confusion with strings
STATE_WAITING = 0
STATE_SEARCHING = 1
STATE_PUSHING = 2
STATE_TURNING = 3

SEARCH_SPEED = 20     # Slow patrol speed
PUSH_SPEED = 80       # Attack speed
ATTACK_DISTANCE = 3   # Distance in cm to trigger pushing
EDGE_THRESHOLD = 500  # Threshold for white line detection (Tune as needed for your ring)

# Starting State
current_state = STATE_WAITING

# Blink Timer Variables
last_blink_time = ticks_ms()
leds_on = False

# Setup UI

sb.log_info("Sumo Bot initialized.", "State:", "WAITING")
sb.log_info("Sumo Bot", "Press OK to run")
cancel_touched = False

try:
    while not cancel_touched:
        # ==========================================
        # 1. SENSE (Gather Data)
        # ==========================================
        
        # Check buttons
        # WORK: Read the OK button from the SuperBot (sb)
        # ok_pressed = sb.get_pressed_ok()
        ok_pressed = False # Dummy value so code runs before you edit it
        
        # WORK: set cancel_touched to the value from alvik.get_touch_canceled()
        
        # Check line sensors (Returns Left, Center, Right)
        # WORK: Get the line sensor values from the Alvik
        left_line, center_line, right_line = 0, 0, 0 # REPLACE these 0's
        
        # Assume higher numbers mean white edge. 
        edge_detected = max(left_line, center_line, right_line) > EDGE_THRESHOLD
        
        # Check distance using SuperBot helper
        # WORK: Get the closest distance in cm from the SuperBot
        distance_cm = 999 # REPLACE this dummy value with sb.get_closest_distance
        
        # ==========================================
        # 2 & 3. THINK & ACT (Unified State Logic)
        # ==========================================
        
        if current_state == STATE_WAITING:
            # ACT
            alvik.brake()
            
            # Non-blocking blink logic (toggles every 500ms)
            if ticks_diff(ticks_ms(), last_blink_time) > 500:
                leds_on = not leds_on
                last_blink_time = ticks_ms()
                
            if leds_on:
                alvik.left_led.set_color(0, 0, 1) # Blue
                alvik.right_led.set_color(0, 0, 1)
            else:
                alvik.left_led.set_color(0, 0, 0) # Off
                alvik.right_led.set_color(0, 0, 0)
            
            # THINK
            if ok_pressed:
                current_state = STATE_SEARCHING
                sb.log_info("State:", "SEARCHING")
                sb.log_info("Transition:", "WAITING", "->", "SEARCHING")
                
        elif current_state == STATE_SEARCHING:
            sb.log_info("State:", "PUSHING", "Target:", distance_cm, "cm")
            pass
                
        elif current_state == STATE_PUSHING:
            # ACT
            # WORK: Turn both LEDs Purple (1, 0, 1) and set wheels to PUSH_SPEED
            pass
            
            # THINK
            # WORK: Check if an edge is detected (switch to STATE_TURNING).
            #       Otherwise, if the target is lost (distance >= ATTACK_DISTANCE), switch to STATE_SEARCHING.

            pass
                
        elif current_state == STATE_TURNING:
            # ACT
            # WORK: Turn both LEDs Red (1, 0, 0) and stop the motors (brake).
            # WORK: Print an evade message, back up 5 cm, and rotate 120 degrees (both blocking)
            # sb.log_info("Executing", "evade maneuver...")
            # use alvik.move()
            # use alvik.rotate()
            pass
            
            # THINK
            # WORK: Force the state back to STATE_SEARCHING now that the turn is complete.
            sb.log_info("State:", "SEARCHING", "Maneuver complete.")
            pass

        # Small delay to keep the SENSE loop stable
        sleep_ms(10)

finally:
    # Cleanup code runs when the loop exits or crashes
    sb.log_info("Program stopped.", "Running cleanup...")
    alvik.brake() # Stop motors
    alvik.stop()  # Stop the background threa