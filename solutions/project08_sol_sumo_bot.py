# Sumo Bot V10
# Solution for Project 08: The State Machine Sumo Bot (Survival Mode)
# Updated to use numeric constants for states.

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
        ok_pressed = sb.get_pressed_ok()
        cancel_touched = alvik.get_touch_cancel()
        
        # Check line sensors (Returns Left, Center, Right)
        left_line, center_line, right_line = alvik.get_line_sensors()
        
        # Assume higher numbers mean white edge. 
        edge_detected = max(left_line, center_line, right_line) > EDGE_THRESHOLD
        
        # Check distance using SuperBot helper
        distance_cm = sb.get_closest_distance()

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
            # ACT
            alvik.left_led.set_color(0, 1, 0) # Green
            alvik.right_led.set_color(0, 1, 0)
            alvik.set_wheels_speed(SEARCH_SPEED, SEARCH_SPEED)
            
            # THINK
            if edge_detected:
                current_state = STATE_TURNING
                sb.log_info("State:", "TURNING", "Edge detected!")
            elif distance_cm < ATTACK_DISTANCE:
                current_state = STATE_PUSHING
                sb.log_info("State:", "PUSHING", "Target:", distance_cm, "cm")
                
        elif current_state == STATE_PUSHING:
            # ACT
            alvik.left_led.set_color(1, 0, 1) # Purple
            alvik.right_led.set_color(1, 0, 1)
            alvik.set_wheels_speed(PUSH_SPEED, PUSH_SPEED)
            
            # THINK
            if edge_detected:
                current_state = STATE_TURNING
                sb.log_info("State:", "TURNING", "Edge detected!")
            elif distance_cm >= ATTACK_DISTANCE:
                current_state = STATE_SEARCHING
                sb.log_info("State:", "SEARCHING", "Target lost.")
                
        elif current_state == STATE_TURNING:
            # ACT
            alvik.left_led.set_color(1, 0, 0) # Red
            alvik.right_led.set_color(1, 0, 0)
            alvik.brake()
            
            # Backup and rotate
            sb.log_info("Executing", "evade maneuver...")
            alvik.move(-5, 'cm', blocking=True)
            alvik.rotate(120, 'deg', blocking=True)
            
            # THINK
            # Force transition back to searching after maneuver is done
            current_state = STATE_SEARCHING
            sb.log_info("State:", "SEARCHING", "Maneuver complete.")

        # Small delay to keep the SENSE loop stable
        sleep_ms(10)

finally:
    # Cleanup code runs when the loop exits or crashes
    sb.log_info("Program stopped.", "Running cleanup...")
    alvik.brake() # Stop motors
    alvik.stop()  # Stop the background threads