# capstone.py
# Version: V15
# Purpose: Continuous Rolling Tracking (Visual Servoing).
# Updates:
#   - Fixed Scope Bug: Removed local K_CONSTANT.
#   - Now uses robot.K_CONSTANT defined in SuperBot.__init__.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import Button
from forklift_bot import ForkLiftBot
import time
import sys

# --- CONFIGURATION ---
ALIGN_TARGET_DIST = 25.0    # Stop 25cm away after alignment
PICKUP_TARGET_DIST = 8.0    # Final goal distance
ROLLING_SPEED = 15          # cm/s
STEERING_GAIN = 0.15        # Proportional gain

# --- STATE CONSTANTS ---
STATE_IDLE              = 0
STATE_ALIGN_SCAN        = 1
STATE_ALIGN_MANEUVER    = 2
STATE_APPROACH_ROLLING  = 3
STATE_PICKUP_LIFT       = 9
STATE_MISSION_SUCCESS   = 6
STATE_MISSION_FAIL      = 7
STATE_EXIT              = 99

# --- HARDWARE SETUP ---
alvik = ArduinoAlvik()
alvik.begin()

# Instantiate our ForkLiftBot
robot = ForkLiftBot(alvik)
robot.enable_info_logging()

robot.log_info("Initializing Capstone V15...")

# Input Buttons
btn_start = Button(robot.bot.get_touch_center)
btn_cancel = Button(robot.bot.get_touch_cancel)

# --- GLOBAL VARIABLES ---
current_state = STATE_IDLE
found_tag = None
start_heading = 0.0

# --- MAIN LOOP ---
try:
    while current_state != STATE_EXIT:
        
        # ------------------------------------------------------------------
        # STATE: IDLE
        # ------------------------------------------------------------------
        if current_state == STATE_IDLE:
            robot.update_display("Capstone V15", "Center: GO", "Cancel: EXIT")
            
            # Blink Blue
            if (time.ticks_ms() // 500) % 2 == 0:
                robot.bot.left_led.set_color(0, 0, 1) 
                robot.bot.right_led.set_color(0, 0, 1)
            else:
                robot.bot.left_led.set_color(0, 0, 0) 
                robot.bot.right_led.set_color(0, 0, 0)
            
            if btn_cancel.get_touch():
                robot.log_info("Exit requested.")
                current_state = STATE_EXIT
                
            if btn_start.get_touch():
                robot.log_info("Mission Start...")
                robot.bot.left_led.set_color(0, 0, 0)
                robot.bot.right_led.set_color(0, 0, 0)
                found_tag = None
                robot.lower_fork()
                current_state = STATE_ALIGN_SCAN

        # ------------------------------------------------------------------
        # STATE: ALIGN SCAN
        # ------------------------------------------------------------------
        elif current_state == STATE_ALIGN_SCAN:
            found = False
            for _ in range(20):
                try:
                    robot.husky.request()
                    if len(robot.husky.blocks) > 0:
                        found_tag = robot.husky.blocks[0]
                        found = True
                        break
                except OSError:
                    pass # Ignore I2C glitches during scan
                time.sleep(0.1)
                
            if found:
                robot.log_info(f"Tag ID {found_tag.id} found.")
                start_heading = robot.get_yaw()
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
            
            robot.log_info(f"Coarse Align: Turn {vector.angle:.1f}")
            robot.bot.rotate(vector.angle)
            robot.drive_distance(vector.distance)
            robot.bot.rotate(-vector.angle)
            
            robot.log_info("Heading Snap...")
            robot.turn_to_heading(start_heading)
            
            robot.center_on_tag(tolerance=3)
            
            time.sleep(0.5)
            current_state = STATE_APPROACH_ROLLING

        # ------------------------------------------------------------------
        # STATE: APPROACH ROLLING (Continuous Visual Servoing)
        # ------------------------------------------------------------------
        elif current_state == STATE_APPROACH_ROLLING:
            robot.log_info("Rolling Approach...")
            
            lost_tag_count = 0
            
            while True:
                # 1. Get Visual Data (Protected)
                try:
                    robot.husky.request()
                except OSError as e:
                    # If I2C times out, just skip this frame and try again
                    # Do NOT stop the robot; momentum handles small gaps
                    continue 

                blocks = [b for b in robot.husky.blocks if b.id == found_tag.id]
                
                if not blocks:
                    lost_tag_count += 1
                    if lost_tag_count > 10: # Increased tolerance for glitches (approx 1 sec)
                        robot.bot.brake()
                        robot.log_error("Lost Tag Moving.")
                        current_state = STATE_MISSION_FAIL
                        break
                    time.sleep(0.05)
                    continue
                else:
                    lost_tag_count = 0
                    target = blocks[0]

                # 2. Check Distance
                if target.width == 0: continue
                # Correctly using the instance variable from SuperBot
                current_dist = robot.K_CONSTANT / target.width
                
                if current_dist <= PICKUP_TARGET_DIST:
                    robot.bot.brake()
                    robot.log_info(f"Arrived: {current_dist:.1f}cm")
                    current_state = STATE_PICKUP_LIFT
                    break
                
                # 3. Calculate Steering
                error_pixels = 160 - target.xCenter
                turn_rate = error_pixels * STEERING_GAIN
                
                # Limit turn rate
                if turn_rate > 30: turn_rate = 30
                if turn_rate < -30: turn_rate = -30
                
                # 4. Update Motors
                robot.bot.drive(ROLLING_SPEED, turn_rate)
                
                time.sleep(0.05)

        # ------------------------------------------------------------------
        # STATE: PICKUP LIFT
        # ------------------------------------------------------------------
        elif current_state == STATE_PICKUP_LIFT:
            robot.log_info("Lifting Box...")
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

# Developed with the assistance of Google Gemini