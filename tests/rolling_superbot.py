# Project 18: Capstone Step 1 - The Blind Approach
# Version: V01 (Refactored to use SuperBot)
#
# OBJECTIVE:
# 1. State Machine: WAITING -> PREPARE -> SCAN -> STEP -> SCAN... -> BLIND -> SUCCESS.
# 2. Strategy: Read distance, drive 50% of the way, stop, repeat.
# 3. Tag Loss: If tag lost, use tracked position to finish the drive.
# 4. Latency Fix: Camera is only queried when robot is stopped.
#
# REFACTOR NOTE: Now uses nhs_robotics.SuperBot for hardware management.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time
import sys

# --- CONSTANTS ---
TARGET_DIST_CM = 5.0     # Goal: Stop 5cm away from the tag/box
SPEED_APPROACH = 20

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
bot = SuperBot(alvik)
bot.enable_info_logging() # Optional: Log steps to file
bot.log_info("SuperBot Ready")

# --- HELPER FUNCTIONS ---

def set_fork_position(angle):
    # Access raw robot via bot.bot
    pos = bot.bot.get_servo_positions()
    bot.bot.set_servo_positions(angle, pos[1])
    time.sleep(0.5)

# --- STATE VARIABLES ---
current_state = STATE_WAITING
previous_state = -1

estimated_dist = 100.0   # Where we think we are
step_size_cm = 0.0       # How far to move in the current step

blink_timer = 0
blink_on = False

# --- MAIN LOOP ---
try:
    bot.log_info("--- CAPSTONE SUPERBOT START ---")
    
    while True:
        # --- GLOBAL CANCEL CHECK ---
        # Access raw robot inputs via bot.bot
        if bot.bot.get_touch_cancel():
            if current_state != STATE_WAITING:
                bot.log_info(">>> CANCEL DETECTED: Resetting")
                bot.bot.brake()
                bot.bot.left_led.set_color(1, 0, 0)
                bot.bot.right_led.set_color(1, 0, 0)
                bot.update_display("Canceled", "Resetting...")
                time.sleep(1.0)
                
                current_state = STATE_WAITING
                previous_state = -1
                set_fork_position(0)
            
        # --- STATE MACHINE ---
        
        # 1. STATE_WAITING
        if current_state == STATE_WAITING:
            if previous_state != STATE_WAITING:
                bot.log_info("State: WAITING")
                bot.update_display("Waiting", "Press Center")
                bot.bot.set_wheels_speed(0, 0)
                set_fork_position(0)
                blink_timer = time.ticks_ms()
                previous_state = STATE_WAITING

            if time.ticks_diff(time.ticks_ms(), blink_timer) >= 500:
                blink_on = not blink_on
                if blink_on:
                    bot.bot.left_led.set_color(0, 0, 1)
                    bot.bot.right_led.set_color(0, 0, 1)
                else:
                    bot.bot.left_led.set_color(0, 0, 0)
                    bot.bot.right_led.set_color(0, 0, 0)
                blink_timer = time.ticks_ms()
            
            if bot.bot.get_touch_center():
                current_state = STATE_PREPARE
            
            time.sleep(0.05)

        # 2. STATE_PREPARE
        elif current_state == STATE_PREPARE:
            bot.log_info("State: PREPARE")
            bot.update_display("Preparing", "Fork Down")
            bot.bot.left_led.set_color(1, 1, 0)
            bot.bot.right_led.set_color(1, 1, 0)
            
            set_fork_position(180) 
            current_state = STATE_SCAN
            previous_state = STATE_PREPARE

        # 3. STATE_SCAN (The "Scan" Phase)
        elif current_state == STATE_SCAN:
            bot.log_info("State: SCAN")
            bot.update_display("Scanning...", "")
            bot.bot.set_wheels_speed(0, 0)
            time.sleep(0.5) # Let robot settle before reading
            
            # Use SuperBot's camera wrapper
            dist = bot.get_camera_distance()
            
            if dist is not None:
                bot.log_info(f"Tag Seen: {dist:.1f} cm")
                estimated_dist = dist # Update our truth
                
                # Logic: Drive half the distance
                step_size_cm = estimated_dist / 2.0
                
                # Check: If step takes us closer than target (overshoot) or very close
                remaining_after_step = estimated_dist - step_size_cm
                
                if remaining_after_step <= TARGET_DIST_CM:
                    # The step is practically the final drive
                    bot.log_info("Close enough -> Final Drive")
                    current_state = STATE_BLIND_CALC
                else:
                    bot.log_info(f"Step: {step_size_cm:.1f} cm")
                    current_state = STATE_DRIVE_STEP
            else:
                bot.log_info("Tag Lost -> Blind Calculation")
                current_state = STATE_BLIND_CALC
                
            previous_state = STATE_SCAN

        # 4. STATE_DRIVE_STEP (The "Step" Phase)
        elif current_state == STATE_DRIVE_STEP:
            bot.update_display("Stepping", f"{step_size_cm:.1f} cm")
            # Using raw move for now (non-blocking)
            bot.bot.move(step_size_cm, blocking=False)
            
            # Update our estimate IMMEDIATELY
            estimated_dist -= step_size_cm
            
            current_state = STATE_WAIT_STEP
            previous_state = STATE_DRIVE_STEP

        # 5. STATE_WAIT_STEP
        elif current_state == STATE_WAIT_STEP:
            # Wait for the partial move to finish
            if bot.bot.is_target_reached():
                current_state = STATE_SCAN # Go back and verify
            
            previous_state = STATE_WAIT_STEP
            time.sleep(0.1)

        # 6. STATE_BLIND_CALC
        elif current_state == STATE_BLIND_CALC:
            bot.log_info("State: BLIND CALC")
            
            final_push = estimated_dist - TARGET_DIST_CM
            
            if final_push > 0:
                bot.log_info(f"Final Push: {final_push:.1f} cm")
                bot.update_display("Final Push", f"{final_push:.1f} cm")
                bot.bot.move(final_push, blocking=False)
                current_state = STATE_BLIND_EXECUTE
            else:
                bot.log_info("Already at Target")
                current_state = STATE_SUCCESS
            
            previous_state = STATE_BLIND_CALC

        # 7. STATE_BLIND_EXECUTE
        elif current_state == STATE_BLIND_EXECUTE:
            if bot.bot.is_target_reached():
                current_state = STATE_SUCCESS
            previous_state = STATE_BLIND_EXECUTE
            time.sleep(0.1)

        # 8. STATE_SUCCESS
        elif current_state == STATE_SUCCESS:
            if previous_state != STATE_SUCCESS:
                bot.log_info("State: SUCCESS")
                bot.update_display("Target Reached", "Done")
                bot.bot.brake()
                bot.bot.left_led.set_color(0, 1, 0)
                bot.bot.right_led.set_color(0, 1, 0)
                time.sleep(5)
                current_state = STATE_WAITING
            
            time.sleep(0.1)

except Exception as e:
    # Use SuperBot error logging
    try:
        bot.log_error(f"CRASH: {e}")
    except:
        print(f"CRITICAL: {e}")
        
    for _ in range(5):
        bot.bot.left_led.set_color(1,0,0)
        time.sleep(0.2)
        bot.bot.left_led.set_color(0,0,0)
        time.sleep(0.2)

finally:
    print("Program End.")
    bot.bot.stop()
    bot.bot.left_led.set_color(0,0,0)
    bot.bot.right_led.set_color(0,0,0)