# goto_box.py
# Version: V06
# Purpose: Combines alignment geometry and incremental approach to position robot for pickup.
# Updates: 
#   - V04: Replaced standard print() with sb.log_info() and sb.log_error().
#   - V05: Updated imports. Button class is now imported from nhs_robotics.
#   - V06: Moved cleanup code to a 'finally' block to guarantee execution.
# Developed with the assistance of Google Gemini.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, Button
import time
import sys

# --- CONFIGURATION ---
ALIGN_TARGET_DIST = 25.0   # Stop 25cm away during the alignment phase
PICKUP_TARGET_DIST = 5.0   # Final goal for the approach phase
APPROACH_SPEED = 20        # Speed for approach steps

# --- SETUP ---
alvik = ArduinoAlvik()
alvik.begin()

sb = SuperBot(alvik)
sb.enable_info_logging()

sb.log_info("Loading goto_box.py V06")

# Initialize Buttons
btn_start = Button(sb.bot.get_touch_center)
btn_cancel = Button(sb.bot.get_touch_cancel)

# --- FUNCTIONS ---

def perform_alignment():
    """
    Phase 1: Geometry
    Scans for a tag, calculates the geometric path to the center-line,
    and executes Turn->Drive->Align.
    Returns: True if successful, False if no tag found.
    """
    sb.update_display("Phase 1: Align", "Scanning...")
    sb.log_info("--- PHASE 1: ALIGNMENT ---")
    
    # 1. Find the Tag
    found_tag = None
    max_retries = 20
    
    for i in range(max_retries):
        if not sb.husky:
            sb.log_error("HuskyLens error.")
            return False

        sb.husky.request()
        if len(sb.husky.blocks) > 0:
            found_tag = sb.husky.blocks[0]
            sb.log_info(f"Tag Found: ID {found_tag.id} at x={found_tag.xCenter}")
            break
        time.sleep(0.1)
    
    if not found_tag:
        sb.update_display("Align Failed", "No Tag Found")
        sb.log_error("Alignment Failed: No tag found.")
        return False

    # 2. Calculate Vector (Targeting ALIGN_TARGET_DIST out)
    vector = sb.calculate_approach_vector(found_tag, target_dist_cm=ALIGN_TARGET_DIST)
    
    sb.log_info(f"Plan: Turn {vector.angle:.1f}, Drive {vector.distance:.1f}, Align {-vector.angle:.1f}")

    # 3. Execute Maneuver
    sb.update_display("Aligning", f"T:{vector.angle:.0f} D:{vector.distance:.0f}")
    
    # A: Face Target
    sb.bot.rotate(vector.angle)
    
    # B: Drive to Setup Point
    sb.drive_distance(vector.distance)
    
    # C: Square Up (Rotate back)
    sb.bot.rotate(-vector.angle)
    
    sb.log_info("Alignment Phase Complete.")
    return True


def perform_approach():
    """
    Phase 2: Zeno's Approach
    Uses the logic from rolling.py to incrementally close the gap 
    from the current position to PICKUP_TARGET_DIST (5cm).
    """
    sb.update_display("Phase 2: Appr", "Starting...")
    sb.log_info("--- PHASE 2: APPROACH ---")
    
    # State constants
    STATE_SCAN = 0
    STATE_DRIVE = 1
    STATE_BLIND_CALC = 2
    STATE_BLIND_EXECUTE = 3
    STATE_DONE = 4
    
    current_state = STATE_SCAN
    estimated_dist = 999
    last_known_dist = 0
    dist_to_drive = 0
    
    while current_state != STATE_DONE:
        
        # --- SCAN STATE ---
        if current_state == STATE_SCAN:
            time.sleep(0.5) # Stability pause
            cam_dist = sb.get_camera_distance()
            
            if cam_dist:
                sb.log_info(f"Dist: {cam_dist:.1f}cm")
                estimated_dist = cam_dist
                last_known_dist = cam_dist
                
                # Check if we are there (Tolerance 1cm)
                if estimated_dist <= (PICKUP_TARGET_DIST + 1.0):
                    sb.log_info("Target Reached (Visual).")
                    current_state = STATE_DONE
                else:
                    # Calculate "Zeno" Step: 50% of the gap
                    gap = estimated_dist - PICKUP_TARGET_DIST
                    dist_to_drive = gap * 0.5
                    if dist_to_drive < 1.0: dist_to_drive = gap 
                    current_state = STATE_DRIVE
            else:
                sb.log_info("Tag Lost.")
                if last_known_dist > 0:
                    sb.log_info("Switching to Blind Logic.")
                    current_state = STATE_BLIND_CALC
                else:
                    sb.log_error("Lost and confused. Aborting.")
                    return False

        # --- DRIVE STATE ---
        elif current_state == STATE_DRIVE:
            sb.drive_distance(dist_to_drive, speed_cm_s=APPROACH_SPEED, blocking=True)
            estimated_dist -= dist_to_drive
            current_state = STATE_SCAN

        # --- BLIND CALC STATE ---
        elif current_state == STATE_BLIND_CALC:
            final_push = estimated_dist - PICKUP_TARGET_DIST
            if final_push > 0:
                sb.log_info(f"Blind Push: {final_push:.1f}cm")
                dist_to_drive = final_push
                current_state = STATE_BLIND_EXECUTE
            else:
                current_state = STATE_DONE

        # --- BLIND EXECUTE STATE ---
        elif current_state == STATE_BLIND_EXECUTE:
             sb.drive_distance(dist_to_drive, speed_cm_s=10, blocking=True)
             current_state = STATE_DONE

    sb.update_display("Approach", "Complete")
    sb.log_info("Approach Phase Complete.")
    return True

# --- MAIN EXECUTION ---

try:
    running_app = True
    
    while running_app:
        # 1. Waiting State
        sb.update_display("GoTo Box", "Center: GO", "Cancel: EXIT")
        sb.log_info("Waiting for Center Button... (Cancel to Exit)")
        
        waiting_for_input = True
        toggle = True
        last_toggle = time.ticks_ms()
        
        # Reset LEDs logic variables
        sb.bot.left_led.set_color(0, 0, 0)
        sb.bot.right_led.set_color(0, 0, 0)

        while waiting_for_input:
            # Check Exit
            if btn_cancel.get_touch():
                running_app = False
                waiting_for_input = False
                sb.log_info("Cancel pressed. Exiting.")
            
            # Check Start
            if btn_start.get_touch():
                waiting_for_input = False
                sb.log_info("Starting run...")
            
            # Blink Logic (Blue)
            if time.ticks_diff(time.ticks_ms(), last_toggle) > 500:
                if toggle:
                    sb.bot.left_led.set_color(0, 0, 1) # Blue
                    sb.bot.right_led.set_color(0, 0, 1)
                else:
                    sb.bot.left_led.set_color(0, 0, 0) # Off
                    sb.bot.right_led.set_color(0, 0, 0)
                toggle = not toggle
                last_toggle = time.ticks_ms()
            
            time.sleep(0.01) # Yield to background tasks
        
        if not running_app:
            break
        
        # 2. Reset LEDs for the run
        sb.bot.left_led.set_color(0, 0, 0)
        sb.bot.right_led.set_color(0, 0, 0)
        
        # 3. Execute Phases
        success = False
        
        if perform_alignment():
            time.sleep(0.5) 
            if perform_approach():
                success = True
        
        # 4. Feedback (Green vs Red)
        if success:
            sb.update_display("Success!", "Returning...")
            sb.bot.left_led.set_color(0, 1, 0)
            sb.bot.right_led.set_color(0, 1, 0)
        else:
            # sb.update_display was likely set by the failing function, but we ensure LEDs are red
            sb.bot.left_led.set_color(1, 0, 0)
            sb.bot.right_led.set_color(1, 0, 0)
            
        time.sleep(3) # Hold the result for 3 seconds
        
        # Loop restarts -> goes back to waiting

except KeyboardInterrupt:
    sb.log_info("Aborted via KeyboardInterrupt.")

except Exception as e:
    sb.log_error(str(e))

finally:
    # Cleanup on Exit (Guaranteed to run)
    sb.bot.stop()
    sb.update_display("Program", "Ended")
    sb.bot.left_led.set_color(0, 0, 0)
    sb.bot.right_led.set_color(0, 0, 0)
