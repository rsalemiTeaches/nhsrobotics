# capstone.py
# Version: V05
# Purpose: Flat State Machine implementation (No Classes).
#          Combines alignment (Phase 1) and Zeno's approach (Phase 2).
# Updates:
#   - Removed redundant update_display() calls.
#   - Relies on log_info() for user feedback during operation.
#   - Only uses update_display() for the start menu instructions.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, Button
import time
import sys

# --- CONFIGURATION ---
ALIGN_TARGET_DIST = 25.0    # Stop 25cm away after alignment
PICKUP_TARGET_DIST = 5.0    # Final goal distance
APPROACH_SPEED = 20         # Speed for approach steps

# --- STATE CONSTANTS ---
STATE_IDLE           = 0    # Waiting for start
STATE_ALIGN_SCAN     = 1    # Looking for the tag
STATE_ALIGN_MANEUVER = 2    # Turning and driving to center
STATE_APPROACH_CHECK = 3    # Measuring distance
STATE_APPROACH_MOVE  = 4    # Driving the calculated step
STATE_APPROACH_BLIND = 5    # Final push if tag is lost close to target
STATE_MISSION_SUCCESS= 6    # Green lights
STATE_MISSION_FAIL   = 7    # Red lights
STATE_EXIT           = 99   # End program

# --- HARDWARE SETUP ---
alvik = ArduinoAlvik()
alvik.begin()

sb = SuperBot(alvik)
sb.enable_info_logging()

sb.log_info("Initializing Capstone V05...")

# Input Buttons
btn_start = Button(sb.bot.get_touch_center)
btn_cancel = Button(sb.bot.get_touch_cancel)

# --- GLOBAL VARIABLES ---
current_state = STATE_IDLE
found_tag = None
last_known_dist = 0.0
dist_to_drive = 0.0

# --- MAIN LOOP ---
try:
    while current_state != STATE_EXIT:
        
        # ------------------------------------------------------------------
        # STATE: IDLE
        # Behavior: Blink Blue, Wait for User Input
        # Note: This is the ONLY place we use update_display explicitly
        # ------------------------------------------------------------------
        if current_state == STATE_IDLE:
            sb.update_display("Capstone", "Center: GO", "Cancel: EXIT")
            
            # Blink Blue
            if (time.ticks_ms() // 500) % 2 == 0:
                sb.bot.left_led.set_color(0, 0, 1) # Blue
                sb.bot.right_led.set_color(0, 0, 1)
            else:
                sb.bot.left_led.set_color(0, 0, 0) # Off
                sb.bot.right_led.set_color(0, 0, 0)
            
            # Check Inputs
            if btn_cancel.get_touch():
                sb.log_info("Exit requested.")
                current_state = STATE_EXIT
                
            if btn_start.get_touch():
                sb.log_info("Mission Start: Scanning...")
                # Reset LEDs and Variables
                sb.bot.left_led.set_color(0, 0, 0)
                sb.bot.right_led.set_color(0, 0, 0)
                last_known_dist = 0.0
                found_tag = None
                current_state = STATE_ALIGN_SCAN

        # ------------------------------------------------------------------
        # STATE: ALIGN SCAN
        # Behavior: Look for the tag using HuskyLens
        # ------------------------------------------------------------------
        elif current_state == STATE_ALIGN_SCAN:
            # No update_display here; log_info drives the screen
            found = False
            # Try for 2 seconds (20 * 0.1s)
            for _ in range(20):
                sb.husky.request()
                if len(sb.husky.blocks) > 0:
                    found_tag = sb.husky.blocks[0]
                    found = True
                    break
                time.sleep(0.1)
                
            if found:
                sb.log_info(f"Tag ID {found_tag.id} found.")
                current_state = STATE_ALIGN_MANEUVER
            else:
                sb.log_error("Scan failed: No tag.")
                current_state = STATE_MISSION_FAIL

        # ------------------------------------------------------------------
        # STATE: ALIGN MANEUVER
        # Behavior: Calculate geometry and move to center line (25cm out)
        # ------------------------------------------------------------------
        elif current_state == STATE_ALIGN_MANEUVER:
            # 1. Calculate the path
            vector = sb.calculate_approach_vector(
                found_tag, 
                target_dist_cm=ALIGN_TARGET_DIST
            )
            
            sb.log_info(f"Aligning: Turn {vector.angle:.1f}, Drive {vector.distance:.1f}")
            
            # 2. Execute the path
            sb.bot.rotate(vector.angle)
            sb.drive_distance(vector.distance)
            sb.bot.rotate(-vector.angle) # Square up
            
            time.sleep(0.5) # Stability pause
            current_state = STATE_APPROACH_CHECK

        # ------------------------------------------------------------------
        # STATE: APPROACH CHECK
        # Behavior: Measure distance, decide whether to move or finish
        # ------------------------------------------------------------------
        elif current_state == STATE_APPROACH_CHECK:
            time.sleep(0.2)
            cam_dist = sb.get_camera_distance()
            
            if cam_dist:
                last_known_dist = cam_dist
                
                # Are we there yet? (Target + 1cm tolerance)
                if cam_dist <= (PICKUP_TARGET_DIST + 1.0):
                    sb.log_info(f"Target Reached ({cam_dist:.1f}cm)")
                    current_state = STATE_MISSION_SUCCESS
                else:
                    # Zeno's Paradox: Drive 50% of the remaining gap
                    gap = cam_dist - PICKUP_TARGET_DIST
                    dist_to_drive = gap * 0.5
                    
                    # Minimum movement clamp (don't move less than 1cm unless very close)
                    if dist_to_drive < 1.0: 
                        dist_to_drive = gap 
                    
                    sb.log_info(f"Gap: {gap:.1f}cm -> Drive {dist_to_drive:.1f}cm")
                    current_state = STATE_APPROACH_MOVE
            else:
                sb.log_info("Tag Lost during approach.")
                if last_known_dist > 0:
                    current_state = STATE_APPROACH_BLIND
                else:
                    current_state = STATE_MISSION_FAIL

        # ------------------------------------------------------------------
        # STATE: APPROACH MOVE
        # Behavior: Execute the partial drive step calculated in CHECK
        # ------------------------------------------------------------------
        elif current_state == STATE_APPROACH_MOVE:
            sb.drive_distance(
                dist_to_drive, 
                speed_cm_s=APPROACH_SPEED, 
                blocking=True
            )
            # Loop back to check
            current_state = STATE_APPROACH_CHECK

        # ------------------------------------------------------------------
        # STATE: APPROACH BLIND
        # Behavior: If tag lost near end, trust last math and finish
        # ------------------------------------------------------------------
        elif current_state == STATE_APPROACH_BLIND:
            final_push = last_known_dist - PICKUP_TARGET_DIST
            
            if final_push > 0:
                sb.log_info(f"Blind Drive: {final_push:.1f}cm")
                sb.drive_distance(final_push, speed_cm_s=10, blocking=True)
                
            current_state = STATE_MISSION_SUCCESS

        # ------------------------------------------------------------------
        # STATE: SUCCESS
        # Behavior: Green LEDs, Celebrate
        # ------------------------------------------------------------------
        elif current_state == STATE_MISSION_SUCCESS:
            sb.log_info("MISSION COMPLETE")
            # Green LEDs
            sb.bot.left_led.set_color(0, 1, 0)
            sb.bot.right_led.set_color(0, 1, 0)
            
            time.sleep(3)
            current_state = STATE_IDLE

        # ------------------------------------------------------------------
        # STATE: FAIL
        # Behavior: Red LEDs, error state
        # ------------------------------------------------------------------
        elif current_state == STATE_MISSION_FAIL:
            sb.log_error("MISSION FAILED")
            # Red LEDs
            sb.bot.left_led.set_color(1, 0, 0)
            sb.bot.right_led.set_color(1, 0, 0)
            
            time.sleep(3)
            current_state = STATE_IDLE
        
        # Small sleep to prevent CPU hogging
        time.sleep(0.01)

except KeyboardInterrupt:
    sb.log_info("Aborted via KeyboardInterrupt.")
except Exception as e:
    sb.log_error(f"Critical Error: {e}")
finally:
    # Cleanup
    sb.bot.stop()
    sb.bot.left_led.set_color(0, 0, 0)
    sb.bot.right_led.set_color(0, 0, 0)
    sb.log_info("Program terminated.")