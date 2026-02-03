# Project 18: Capstone Step 1 - The Blind Approach
# Version: V03 (Added blinking LEDs in WAITING state)
#
# OBJECTIVE:
# 1. State Machine: WAITING -> PREPARE -> SCAN -> STEP -> SCAN... -> BLIND -> SUCCESS.
# 2. Strategy: Read distance, drive 50% of the way, stop, repeat.
# 3. Tag Loss: If tag lost, use tracked position to finish the drive.
# 4. Latency Fix: Camera is only queried when robot is stopped.
#
# REFACTOR NOTE: Now uses nhs_robotics.SuperBot for hardware management.
# V02 UPDATE: Replaces native alvik.move() with SuperBot.drive_distance() for precision.
# V03 UPDATE: Added blinking LED logic to STATE_WAITING.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time
import sys

# --- CONSTANTS ---
TARGET_DIST_CM = 5.0     # Goal: Stop 5cm away from the tag/box
SPEED_APPROACH = 20      # Speed for the approach steps
SLOW_APPROACH = 5

# --- STATES ---
STATE_WAITING = 0
STATE_PREPARE = 1
STATE_SCAN = 2           # Stop and read camera
STATE_DRIVE_STEP = 3     # Drive half the distance
STATE_WAIT_STEP = 4      # Wait for partial move to finish
STATE_BLIND_CALC = 5     # Calculate final push
STATE_BLIND_EXECUTE = 6  # Final drive
STATE_SUCCESS = 7

# --- HARDWARE SETUP ---
print("Initializing Alvik...")
alvik = ArduinoAlvik()
alvik.begin()

print("Suiting up SuperBot...")
sb = SuperBot(alvik) # Renamed to 'sb' per user request
sb.enable_info_logging() # Optional: Log steps to file

# --- VARIABLES ---
current_state = STATE_WAITING
previous_state = -1

distance_to_drive = 0    # How far to move in the current step
estimated_dist = 0       # Internal map of where the tag *should* be
last_known_dist = 0      # The last reliable reading from the camera

# Blink Helpers
last_blink_time = 0
blink_state = False

# --- MAIN LOOP ---
try:
    while True:
        # 1. STATE_WAITING
        if current_state == STATE_WAITING:
            if previous_state != STATE_WAITING:
                sb.log_info("State: WAITING")
                sb.update_display("Blind Approach", "Press Center")
                # Initialize blink
                blink_state = True
                sb.bot.left_led.set_color(0, 0, 1) # Blue
                sb.bot.right_led.set_color(0, 0, 1)
                last_blink_time = time.ticks_ms()
            
            # Blink Logic (Non-blocking)
            if time.ticks_diff(time.ticks_ms(), last_blink_time) > 500: # 500ms toggle
                last_blink_time = time.ticks_ms()
                blink_state = not blink_state
                if blink_state:
                    sb.bot.left_led.set_color(0, 0, 1) # Blue
                    sb.bot.right_led.set_color(0, 0, 1)
                else:
                    sb.bot.left_led.set_color(0, 0, 0) # Off
                    sb.bot.right_led.set_color(0, 0, 0)

            # Use SuperBot's wrapped controller if available, or direct check
            if sb.bot.get_touch_center(): # Simple touch check
                 # Debounce
                while sb.bot.get_touch_center():
                    time.sleep(0.05)
                current_state = STATE_PREPARE
            
            previous_state = STATE_WAITING
            time.sleep(0.05) # Reduced sleep to make blink responsive

        # 2. STATE_PREPARE
        elif current_state == STATE_PREPARE:
            sb.log_info("State: PREPARE")
            sb.bot.left_led.set_color(1, 1, 0) # Yellow
            sb.bot.right_led.set_color(1, 1, 0)
            
            # Reset trackers
            estimated_dist = 999 
            last_known_dist = 0
            
            current_state = STATE_SCAN
            previous_state = STATE_PREPARE

        # 3. STATE_SCAN
        elif current_state == STATE_SCAN:
            if previous_state != STATE_SCAN:
                sb.log_info("State: SCANNING")
                sb.update_display("Scanning...", "Looking for Tag")
                # Stop briefly to ensure clean camera reading
                time.sleep(0.5)

            # Get Camera Reading
            cam_dist = sb.get_camera_distance()
            
            if cam_dist:
                sb.log_info(f"Tag Found: {cam_dist:.1f}cm")
                
                # Update our internal map
                estimated_dist = cam_dist
                last_known_dist = cam_dist
                
                # Logic: Are we close enough to finish?
                if estimated_dist <= (TARGET_DIST_CM + 2.0):
                    # We are basically there (within 2cm tolerance)
                    current_state = STATE_SUCCESS
                else:
                    # We are far away. Drive 50% of the remaining gap.
                    gap = estimated_dist - TARGET_DIST_CM
                    distance_to_drive = gap * 0.5
                    
                    # Minimum step size check (don't move if < 1cm)
                    if distance_to_drive < 1.0:
                        distance_to_drive = gap # Just finish it
                        
                    current_state = STATE_DRIVE_STEP

            else:
                # Tag NOT seen
                sb.log_info("Tag Lost / Not Found")
                
                if last_known_dist > 0:
                    # We saw it recently, assume we got too close and it dropped below view
                    # Go to Blind Phase to finish the job based on memory
                    sb.log_info("Switching to BLIND")
                    current_state = STATE_BLIND_CALC
                else:
                    # We never saw it. Just wait.
                    sb.update_display("No Tag Seen", "Adjust & Retry")
                    time.sleep(1)
                    # Stay in SCAN
            
            previous_state = STATE_SCAN

        # 4. STATE_DRIVE_STEP
        elif current_state == STATE_DRIVE_STEP:
            sb.log_info(f"Step: {distance_to_drive:.1f}cm")
            
            # V02 UPDATE: Use drive_distance instead of move()
            # Non-blocking so we can manage state in the next loop
            sb.drive_distance(distance_to_drive, speed_cm_s=SPEED_APPROACH, blocking=False)
            
            # Update internal estimation (we are moving closer)
            estimated_dist -= distance_to_drive
            
            current_state = STATE_WAIT_STEP
            previous_state = STATE_DRIVE_STEP

        # 5. STATE_WAIT_STEP
        elif current_state == STATE_WAIT_STEP:
            # Wait for the motor move to finish
            if sb.move_complete():
                # Move done. Go back to Scan to verify position.
                current_state = STATE_SCAN
            
            previous_state = STATE_WAIT_STEP
            time.sleep(0.01)

        # 6. STATE_BLIND_CALC
        elif current_state == STATE_BLIND_CALC:
            sb.log_info("State: BLIND CALC")
            
            # We are here because we lost the tag but know where it WAS.
            # estimated_dist holds our theoretical distance to the object.
            
            final_push = estimated_dist - TARGET_DIST_CM
            
            if final_push > 0:
                sb.log_info(f"Blind Push: {final_push:.1f}cm")
                sb.update_display("Final Push", f"{final_push:.1f} cm")
                
                # V02 UPDATE: Use drive_distance
                sb.drive_distance(final_push, speed_cm_s=SLOW_APPROACH, blocking=False)
                current_state = STATE_BLIND_EXECUTE
            else:
                sb.log_info("Already at Target")
                current_state = STATE_SUCCESS
            
            previous_state = STATE_BLIND_CALC

        # 7. STATE_BLIND_EXECUTE
        elif current_state == STATE_BLIND_EXECUTE:
            # Wait for final blind move to finish
            if sb.move_complete():
                current_state = STATE_SUCCESS
            
            previous_state = STATE_BLIND_EXECUTE
            time.sleep(0.01)

        # 8. STATE_SUCCESS
        elif current_state == STATE_SUCCESS:
            if previous_state != STATE_SUCCESS:
                sb.log_info("State: SUCCESS")
                sb.update_display("Target Reached", "Done")
                sb.bot.brake()
                sb.bot.left_led.set_color(0, 1, 0)
                sb.bot.right_led.set_color(0, 1, 0)
                time.sleep(5)
                
                # Reset
                sb.bot.left_led.set_color(0, 0, 0)
                sb.bot.right_led.set_color(0, 0, 0)
                current_state = STATE_WAITING
            
            time.sleep(0.1)

except KeyboardInterrupt:
    sb.bot.stop() # Explicit stop on exit
    print("\nProgram Terminated")

except Exception as e:
    # Use SuperBot error logging
    try:
        sb.log_error(f"CRASH: {e}")
    except:
        print(f"CRITICAL: {e}")
        
    for _ in range(5):
        sb.bot.left_led.set_color(1,0,0)
        sb.bot.right_led.set_color(1,0,0)
        time.sleep(0.2)
        sb.bot.left_led.set_color(0,0,0)
        sb.bot.right_led.set_color(0,0,0)
        time.sleep(0.2)
    sb.bot.stop()

# Developed with the assistance of Google Gemini