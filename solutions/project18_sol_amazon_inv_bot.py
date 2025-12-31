# capstone.py
# Version: V27
# Purpose: Capstone solution consistent with nhs_roalvikics.py V35.
# Logic: Find Tag -> Align -> Approach -> Lift -> Spin -> Return -> Drop.
# Notes: Renamed roalvik -> forklift per instructions.

from arduino_alvik import ArduinoAlvik
from nhs_roalvikics import Button
from forklift_alvik import ForkLiftalvik
import time
import sys

# --- CONFIGURATION ---
ALIGN_TARGET_DIST = 25.0    # Distance to stop for alignment
PICKUP_TARGET_DIST = 8.0    # Final distance for pickup
APPROACH_SPEED = 5          # Slow speed for visual servoing (cm/s)
RETURN_SPEED = 15           # Faster speed for return
BLACK_THRESHOLD = 500       # Line sensor threshold

# --- STATE CONSTANTS ---
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

# Instantiate ForkLiftalvik
forklift = ForkLiftalvik(alvik)
forklift.enable_info_logging()

forklift.log_info("Initializing Capstone V27...")

# Hardware Check
if forklift.husky is None:
    forklift.log_error("CRITICAL: HuskyLens not found.")
    while True:
        forklift.alvik.left_led.set_color(1, 0, 0)
        time.sleep(0.5)
        forklift.alvik.left_led.set_color(0, 0, 0)
        time.sleep(0.5)

# Input Buttons
btn_start = Button(forklift.alvik.get_touch_center)
btn_cancel = Button(forklift.alvik.get_touch_cancel)

# Global Variables
current_state = STATE_IDLE

# --- MAIN LOOP ---
try:
    while current_state != STATE_EXIT:
        
        # ------------------------------------------------------------------
        # STATE: IDLE
        # ------------------------------------------------------------------
        if current_state == STATE_IDLE:
            forklift.update_display("Capstone V27", "Center: START", "Cancel: EXIT")
            
            # Blink Blue
            if (time.ticks_ms() // 500) % 2 == 0:
                forklift.alvik.left_led.set_color(0, 0, 1) 
                forklift.alvik.right_led.set_color(0, 0, 1)
            else:
                forklift.alvik.left_led.set_color(0, 0, 0) 
                forklift.alvik.right_led.set_color(0, 0, 0)
            
            if btn_cancel.get_touch():
                forklift.log_info("Exit requested.")
                current_state = STATE_EXIT
                
            if btn_start.get_touch():
                forklift.log_info("Mission Start...")
                forklift.alvik.left_led.set_color(0, 0, 0)
                forklift.alvik.right_led.set_color(0, 0, 0)
                forklift.lower_fork()
                current_state = STATE_ALIGN

        # ------------------------------------------------------------------
        # STATE: ALIGN
        # ------------------------------------------------------------------
        elif current_state == STATE_ALIGN:
            forklift.log_info("Aligning to Tag...")
            
            success = forklift.align_to_tag(target_id=1, align_dist=ALIGN_TARGET_DIST)
            
            if success:
                forklift.log_info("Aligned.")
                current_state = STATE_APPROACH
            else:
                forklift.log_error("Align Failed: Tag Not Found")
                current_state = STATE_FAIL

        # ------------------------------------------------------------------
        # STATE: APPROACH
        # ------------------------------------------------------------------
        elif current_state == STATE_APPROACH:
            forklift.log_info("Approaching Box...")
            
            success = forklift.approach_tag(
                target_id=1, 
                stop_distance=PICKUP_TARGET_DIST, 
                speed=APPROACH_SPEED,
                blocking=True
            )
            
            if success:
                forklift.log_info("Arrived at Box.")
                current_state = STATE_LIFT
            else:
                forklift.log_error("Approach Failed: Lost Tag")
                current_state = STATE_FAIL

        # ------------------------------------------------------------------
        # STATE: LIFT
        # ------------------------------------------------------------------
        elif current_state == STATE_LIFT:
            forklift.log_info("Lifting Box...")
            forklift.raise_fork(10)
            current_state = STATE_RETURN_SPIN

        # ------------------------------------------------------------------
        # STATE: RETURN SPIN
        # ------------------------------------------------------------------
        elif current_state == STATE_RETURN_SPIN:
            forklift.log_info("Spinning 180...")
            forklift.alvik.rotate(180)
            current_state = STATE_RETURN_DRIVE

        # ------------------------------------------------------------------
        # STATE: RETURN DRIVE
        # ------------------------------------------------------------------
        elif current_state == STATE_RETURN_DRIVE:
            forklift.log_info("Returning to Edge...")
            
            forklift.drive_to_line(speed=RETURN_SPEED, threshold=BLACK_THRESHOLD, blocking=True)
            
            forklift.log_info("Edge Detected.")
            current_state = STATE_DROP

        # ------------------------------------------------------------------
        # STATE: DROP
        # ------------------------------------------------------------------
        elif current_state == STATE_DROP:
            forklift.log_info("Dropping Box...")
            forklift.lower_fork()
            current_state = STATE_SUCCESS

        # ------------------------------------------------------------------
        # STATE: SUCCESS
        # ------------------------------------------------------------------
        elif current_state == STATE_SUCCESS:
            forklift.log_info("MISSION COMPLETE")
            forklift.alvik.left_led.set_color(0, 1, 0)
            forklift.alvik.right_led.set_color(0, 1, 0)
            time.sleep(3)
            current_state = STATE_IDLE

        # ------------------------------------------------------------------
        # STATE: FAIL
        # ------------------------------------------------------------------
        elif current_state == STATE_FAIL:
            forklift.log_error("MISSION FAILED")
            forklift.alvik.left_led.set_color(1, 0, 0)
            forklift.alvik.right_led.set_color(1, 0, 0)
            time.sleep(3)
            current_state = STATE_IDLE
        
        time.sleep(0.01)

except KeyboardInterrupt:
    forklift.log_info("Aborted via KeyboardInterrupt.")
except Exception as e:
    forklift.log_error(f"Critical Error: {e}")
finally:
    forklift.alvik.stop()
    forklift.alvik.left_led.set_color(0, 0, 0)
    forklift.alvik.right_led.set_color(0, 0, 0)
    forklift.log_info("Program terminated.")

# Developed with the assistance of Google Gemini