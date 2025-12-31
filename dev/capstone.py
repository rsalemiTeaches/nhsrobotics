# capstone.py
# Version: V23
# Purpose: Capstone solution consistent with nhs_robotics.py V32 architecture.
# Logic: Find Tag -> Align -> Approach -> Lift -> Spin -> Return -> Drop.
# Notes: Uses high-level blocking methods from SuperBot for clean logic.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import Button
from forklift_bot import ForkLiftBot
import time
import sys

# --- CONFIGURATION ---
ALIGN_TARGET_DIST = 25.0    # Distance to stop for alignment
PICKUP_TARGET_DIST = 8.0    # Final distance for pickup
APPROACH_SPEED = 5          # Slow speed for visual servoing
RETURN_SPEED = 15           # Faster speed for return
BLACK_THRESHOLD = 500       # Line sensor threshold

# --- STATE CONSTANTS ---
# Using integers for speed and standard practice
STATE_IDLE              = 0
STATE_ALIGN             = 1
STATE_APPROACH          = 2
STATE_LIFT              = 3
STATE_RETURN_SPIN       = 4
STATE_RETURN_DRIVE      = 5
STATE_DROP              = 6
STATE_SUCCESS           = 7
STATE_FAIL              = 8
STATE_EXIT              = 99

# --- HARDWARE SETUP ---
alvik = ArduinoAlvik()
alvik.begin()

# Instantiate ForkLiftBot
robot = ForkLiftBot(alvik)
robot.enable_info_logging()

robot.log_info("Initializing Capstone V23...")

# Hardware Check
if robot.husky is None:
    robot.log_error("CRITICAL: HuskyLens not found.")
    while True:
        robot.bot.left_led.set_color(1, 0, 0)
        time.sleep(0.5)
        robot.bot.left_led.set_color(0, 0, 0)
        time.sleep(0.5)

# Input Buttons
btn_start = Button(robot.bot.get_touch_center)
btn_cancel = Button(robot.bot.get_touch_cancel)

# Global Variables
current_state = STATE_IDLE

# --- MAIN LOOP ---
try:
    while current_state != STATE_EXIT:
        
        # ------------------------------------------------------------------
        # STATE: IDLE
        # ------------------------------------------------------------------
        if current_state == STATE_IDLE:
            robot.update_display("Capstone V23", "Center: START", "Cancel: EXIT")
            
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
                robot.lower_fork()
                current_state = STATE_ALIGN

        # ------------------------------------------------------------------
        # STATE: ALIGN
        # ------------------------------------------------------------------
        elif current_state == STATE_ALIGN:
            robot.log_info("Aligning to Tag...")
            
            # align_to_tag handles the scan, math, and turns (blocking)
            success = robot.align_to_tag(target_id=1, align_dist=ALIGN_TARGET_DIST)
            
            if success:
                robot.log_info("Aligned.")
                current_state = STATE_APPROACH
            else:
                robot.log_error("Align Failed: Tag Not Found")
                current_state = STATE_FAIL

        # ------------------------------------------------------------------
        # STATE: APPROACH
        # ------------------------------------------------------------------
        elif current_state == STATE_APPROACH:
            robot.log_info("Approaching Box...")
            
            # approach_tag handles visual steering and blind finish (blocking)
            success = robot.approach_tag(
                target_id=1, 
                stop_distance=PICKUP_TARGET_DIST, 
                speed=APPROACH_SPEED,
                blocking=True
            )
            
            if success:
                robot.log_info("Arrived at Box.")
                current_state = STATE_LIFT
            else:
                robot.log_error("Approach Failed: Lost Tag")
                current_state = STATE_FAIL

        # ------------------------------------------------------------------
        # STATE: LIFT
        # ------------------------------------------------------------------
        elif current_state == STATE_LIFT:
            robot.log_info("Lifting Box...")
            robot.raise_fork(10)
            time.sleep(0.5)
            current_state = STATE_RETURN_SPIN

        # ------------------------------------------------------------------
        # STATE: RETURN SPIN
        # ------------------------------------------------------------------
        elif current_state == STATE_RETURN_SPIN:
            robot.log_info("Spinning 180...")
            # Use simple rotate for best reliability
            robot.bot.rotate(180)
            time.sleep(0.5)
            current_state = STATE_RETURN_DRIVE

        # ------------------------------------------------------------------
        # STATE: RETURN DRIVE
        # ------------------------------------------------------------------
        elif current_state == STATE_RETURN_DRIVE:
            robot.log_info("Returning to Edge...")
            
            # drive_to_line blocks until line threshold is met
            robot.drive_to_line(speed=RETURN_SPEED, threshold=BLACK_THRESHOLD, blocking=True)
            
            robot.log_info("Edge Detected.")
            current_state = STATE_DROP

        # ------------------------------------------------------------------
        # STATE: DROP
        # ------------------------------------------------------------------
        elif current_state == STATE_DROP:
            robot.log_info("Dropping Box...")
            robot.lower_fork()
            time.sleep(1.0)
            current_state = STATE_SUCCESS

        # ------------------------------------------------------------------
        # STATE: SUCCESS
        # ------------------------------------------------------------------
        elif current_state == STATE_SUCCESS:
            robot.log_info("MISSION COMPLETE")
            robot.bot.left_led.set_color(0, 1, 0)
            robot.bot.right_led.set_color(0, 1, 0)
            time.sleep(3)
            current_state = STATE_IDLE

        # ------------------------------------------------------------------
        # STATE: FAIL
        # ------------------------------------------------------------------
        elif current_state == STATE_FAIL:
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