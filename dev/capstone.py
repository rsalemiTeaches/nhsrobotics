# capstone.py
# Version: V10
# Purpose: Flat State Machine implementation using ForkLiftBot.
# Updates:
#   - Removed STATE_PICKUP_ENGAGE.
#   - Logic assumes that reaching PICKUP_TARGET_DIST (5cm) puts the forks
#     under the box automatically because the forks are in front of the robot.
#   - Transitions: Approach (Visual or Blind) -> Lift -> Success.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import Button
from forklift_bot import ForkLiftBot
import time
import sys

# --- CONFIGURATION ---
ALIGN_TARGET_DIST = 25.0    # Stop 25cm away after alignment
PICKUP_TARGET_DIST = 5.0    # Final goal distance (Forks should be under box here)
APPROACH_SPEED = 20         # Speed for approach steps

# --- STATE CONSTANTS ---
STATE_IDLE           = 0    # Waiting for start
STATE_ALIGN_SCAN     = 1    # Looking for the tag
STATE_ALIGN_MANEUVER = 2    # Turning and driving to center
STATE_APPROACH_CHECK = 3    # Measuring distance
STATE_APPROACH_MOVE  = 4    # Driving the calculated step
STATE_APPROACH_BLIND = 5    # Final push if tag is lost close to target
STATE_PICKUP_LIFT    = 9    # Lift the box
STATE_MISSION_SUCCESS= 6    # Green lights
STATE_MISSION_FAIL   = 7    # Red lights
STATE_EXIT           = 99   # End program

# --- HARDWARE SETUP ---
alvik = ArduinoAlvik()
alvik.begin()

# Instantiate our ForkLiftBot
robot = ForkLiftBot(alvik)
robot.enable_info_logging()

robot.log_info("Initializing Capstone V10...")

# Input Buttons
btn_start = Button(robot.bot.get_touch_center)
btn_cancel = Button(robot.bot.get_touch_cancel)

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
        # ------------------------------------------------------------------
        if current_state == STATE_IDLE:
            robot.update_display("Capstone", "Center: GO", "Cancel: EXIT")
            
            # Blink Blue
            if (time.ticks_ms() // 500) % 2 == 0:
                robot.bot.left_led.set_color(0, 0, 1) # Blue
                robot.bot.right_led.set_color(0, 0, 1)
            else:
                robot.bot.left_led.set_color(0, 0, 0) # Off
                robot.bot.right_led.set_color(0, 0, 0)
            
            # Check Inputs
            if btn_cancel.get_touch():
                robot.log_info("Exit requested.")
                current_state = STATE_EXIT
                
            if btn_start.get_touch():
                robot.log_info("Mission Start: Scanning...")
                robot.bot.left_led.set_color(0, 0, 0)
                robot.bot.right_led.set_color(0, 0, 0)
                last_known_dist = 0.0
                found_tag = None
                
                # Ensure fork is down before starting
                robot.lower_fork()
                
                current_state = STATE_ALIGN_SCAN

        # ------------------------------------------------------------------
        # STATE: ALIGN SCAN
        # ------------------------------------------------------------------
        elif current_state == STATE_ALIGN_SCAN:
            found = False
            for _ in range(20):
                robot.husky.request()
                if len(robot.husky.blocks) > 0:
                    found_tag = robot.husky.blocks[0]
                    found = True
                    break
                time.sleep(0.1)
                
            if found:
                robot.log_info(f"Tag ID {found_tag.id} found.")
                current_state = STATE_ALIGN_MANEUVER
            else:
                robot.log_error("Scan failed: No tag.")
                current_state = STATE_MISSION_FAIL

        # ------------------------------------------------------------------
        # STATE: ALIGN MANEUVER
        # ------------------------------------------------------------------
        elif current_state == STATE_ALIGN_MANEUVER:
            vector = robot.calculate_approach_vector(
                found_tag, 
                target_dist_cm=ALIGN_TARGET_DIST
            )
            
            robot.log_info(f"Aligning: Turn {vector.angle:.1f}, Drive {vector.distance:.1f}")
            
            robot.bot.rotate(vector.angle)
            robot.drive_distance(vector.distance)
            robot.bot.rotate(-vector.angle)
            
            time.sleep(0.5)
            current_state = STATE_APPROACH_CHECK

        # ------------------------------------------------------------------
        # STATE: APPROACH CHECK
        # ------------------------------------------------------------------
        elif current_state == STATE_APPROACH_CHECK:
            time.sleep(0.2)
            cam_dist = robot.get_camera_distance()
            
            if cam_dist:
                last_known_dist = cam_dist
                
                if cam_dist <= (PICKUP_TARGET_DIST + 1.0):
                    robot.log_info(f"Target Reached ({cam_dist:.1f}cm)")
                    # Forks should be under the box now
                    current_state = STATE_PICKUP_LIFT
                else:
                    gap = cam_dist - PICKUP_TARGET_DIST
                    dist_to_drive = gap * 0.5
                    
                    if dist_to_drive < 1.0: 
                        dist_to_drive = gap 
                    
                    robot.log_info(f"Gap: {gap:.1f}cm -> Drive {dist_to_drive:.1f}cm")
                    current_state = STATE_APPROACH_MOVE
            else:
                robot.log_info("Tag Lost during approach.")
                if last_known_dist > 0:
                    current_state = STATE_APPROACH_BLIND
                else:
                    current_state = STATE_MISSION_FAIL

        # ------------------------------------------------------------------
        # STATE: APPROACH MOVE
        # ------------------------------------------------------------------
        elif current_state == STATE_APPROACH_MOVE:
            robot.drive_distance(
                dist_to_drive, 
                speed_cm_s=APPROACH_SPEED, 
                blocking=True
            )
            last_known_dist -= dist_to_drive
            current_state = STATE_APPROACH_CHECK

        # ------------------------------------------------------------------
        # STATE: APPROACH BLIND
        # ------------------------------------------------------------------
        elif current_state == STATE_APPROACH_BLIND:
            final_push = last_known_dist - PICKUP_TARGET_DIST
            if final_push > 0:
                robot.log_info(f"Blind Drive: {final_push:.1f}cm")
                robot.drive_distance(final_push, speed_cm_s=10, blocking=True)
            
            # After blind approach, we are at the target
            current_state = STATE_PICKUP_LIFT

        # ------------------------------------------------------------------
        # STATE: PICKUP LIFT
        # Behavior: Raise the fork
        # ------------------------------------------------------------------
        elif current_state == STATE_PICKUP_LIFT:
            robot.log_info("Lifting Box...")
            
            # Raise fork to max level (10)
            robot.raise_fork(10)
            
            time.sleep(0.5)
            current_state = STATE_MISSION_SUCCESS

        # ------------------------------------------------------------------
        # STATE: SUCCESS
        # ------------------------------------------------------------------
        elif current_state == STATE_MISSION_SUCCESS:
            robot.log_info("MISSION COMPLETE")
            robot.bot.left_led.set_color(0, 1, 0)
            robot.bot.right_led.set_color(0, 1, 0)
            
            time.sleep(3)
            current_state = STATE_IDLE

        # ------------------------------------------------------------------
        # STATE: FAIL
        # ------------------------------------------------------------------
        elif current_state == STATE_MISSION_FAIL:
            robot.log_error("MISSION FAILED")
            robot.bot.left_led.set_color(1, 0, 0)
            robot.bot.right_led.set_color(1, 0, 0)
            
            time.sleep(3)
            current_state = STATE_IDLE
        
        time.sleep(0.01)

except KeyboardInterrupt:
    robot.log_info("Aborted via KeyboardInterrupt.")
except Exception as e:
    robot.log_error(f"Critical Error: {e}")
finally:
    robot.bot.stop()
    robot.bot.left_led.set_color(0, 0, 0)
    robot.bot.right_led.set_color(0, 0, 0)
    robot.log_info("Program terminated.")
