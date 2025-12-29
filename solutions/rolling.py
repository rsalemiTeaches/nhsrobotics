# Project 18: Capstone Step 1 - The Blind Approach
# Version: V16 (Step-and-Scan / Zeno's Approach)
#
# OBJECTIVE:
# 1. State Machine: WAITING -> PREPARE -> SCAN -> STEP -> SCAN... -> BLIND -> SUCCESS.
# 2. Strategy: Read distance, drive 50% of the way, stop, repeat.
# 3. Tag Loss: If tag lost, use tracked position to finish the drive.
# 4. Latency Fix: Camera is only queried when robot is stopped.
#
# Created with the help of Gemini Pro

from arduino_alvik import ArduinoAlvik
from qwiic_huskylens import QwiicHuskylens
from qwiic_i2c.micropython_i2c import MicroPythonI2C
from nhs_robotics import oLED
from machine import I2C, Pin
import time
import sys

# --- CONSTANTS ---
K_CONSTANT = 1624.0
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
alvik = ArduinoAlvik()
alvik.begin()

print("Initializing Shared I2C Bus...")
shared_i2c = I2C(1, scl=Pin(12), sda=Pin(11), freq=400000)

screen = None
try:
    screen = oLED(i2cDriver=shared_i2c)
    screen.show_lines("Booting...", "V16 Init")
except Exception as e:
    print(f"OLED Error: {e}")

try:
    alvik_i2c = MicroPythonI2C(esp32_i2c=shared_i2c)
    huskylens = QwiicHuskylens(i2c_driver=alvik_i2c)
    huskylens.begin()
    print("HuskyLens Initialized")
except:
    if screen: screen.show_lines("Cam Error!", "Exit")
    sys.exit()

# --- HELPER FUNCTIONS ---

def set_fork_position(angle):
    pos = alvik.get_servo_positions()
    alvik.set_servo_positions(angle, pos[1])
    time.sleep(0.5)

def get_distance_to_tag():
    """Request new data from camera. blocking call."""
    huskylens.request()
    if len(huskylens.blocks) > 0:
        width = huskylens.blocks[0].width
        if width == 0: return None
        return K_CONSTANT / width
    return None

def update_display(l1, l2=""):
    if screen:
        try:
            screen.show_lines(str(l1), str(l2))
        except: pass

# --- STATE VARIABLES ---
current_state = STATE_WAITING
previous_state = -1

estimated_dist = 100.0   # Where we think we are
step_size_cm = 0.0       # How far to move in the current step

blink_timer = 0
blink_on = False

# --- MAIN LOOP ---
try:
    print("--- CAPSTONE V16 START ---")
    
    while True:
        # --- GLOBAL CANCEL CHECK ---
        if alvik.get_touch_cancel():
            if current_state != STATE_WAITING:
                print(">>> CANCEL DETECTED: Resetting to WAITING")
                alvik.brake()
                alvik.left_led.set_color(1, 0, 0)
                alvik.right_led.set_color(1, 0, 0)
                update_display("Canceled", "Resetting...")
                time.sleep(1.0)
                
                current_state = STATE_WAITING
                previous_state = -1
                set_fork_position(0)
            
        # --- STATE MACHINE ---
        
        # 1. STATE_WAITING
        if current_state == STATE_WAITING:
            if previous_state != STATE_WAITING:
                print("State: WAITING")
                update_display("Waiting", "Press Center")
                alvik.set_wheels_speed(0, 0)
                set_fork_position(0)
                blink_timer = time.ticks_ms()
                previous_state = STATE_WAITING

            if time.ticks_diff(time.ticks_ms(), blink_timer) >= 500:
                blink_on = not blink_on
                if blink_on:
                    alvik.left_led.set_color(0, 0, 1)
                    alvik.right_led.set_color(0, 0, 1)
                else:
                    alvik.left_led.set_color(0, 0, 0)
                    alvik.right_led.set_color(0, 0, 0)
                blink_timer = time.ticks_ms()
            
            if alvik.get_touch_center():
                current_state = STATE_PREPARE
            
            time.sleep(0.05)

        # 2. STATE_PREPARE
        elif current_state == STATE_PREPARE:
            print("State: PREPARE")
            update_display("Preparing", "Fork Down")
            alvik.left_led.set_color(1, 1, 0)
            alvik.right_led.set_color(1, 1, 0)
            
            set_fork_position(180) 
            current_state = STATE_SCAN
            previous_state = STATE_PREPARE

        # 3. STATE_SCAN (The "Scan" Phase)
        elif current_state == STATE_SCAN:
            print("State: SCAN")
            update_display("Scanning...", "")
            alvik.set_wheels_speed(0, 0)
            time.sleep(0.5) # Let robot settle before reading
            
            dist = get_distance_to_tag()
            
            if dist is not None:
                print(f"Tag Seen: {dist:.1f} cm")
                estimated_dist = dist # Update our truth
                
                # Logic: Drive half the distance
                step_size_cm = estimated_dist / 2.0
                
                # Check: If step takes us closer than target (overshoot) or very close
                # Just finish the job now.
                remaining_after_step = estimated_dist - step_size_cm
                
                if remaining_after_step <= TARGET_DIST_CM:
                    # The step is practically the final drive
                    print("Close enough -> Final Drive")
                    current_state = STATE_BLIND_CALC
                else:
                    print(f"Step: {step_size_cm:.1f} cm")
                    current_state = STATE_DRIVE_STEP
            else:
                print("Tag Lost -> Blind Calculation")
                current_state = STATE_BLIND_CALC
                
            previous_state = STATE_SCAN

        # 4. STATE_DRIVE_STEP (The "Step" Phase)
        elif current_state == STATE_DRIVE_STEP:
            update_display("Stepping", f"{step_size_cm:.1f} cm")
            alvik.move(step_size_cm, blocking=False)
            
            # Update our estimate IMMEDIATELY so if we lose tag next scan, we know where we are
            estimated_dist -= step_size_cm
            
            current_state = STATE_WAIT_STEP
            previous_state = STATE_DRIVE_STEP

        # 5. STATE_WAIT_STEP
        elif current_state == STATE_WAIT_STEP:
            # Wait for the partial move to finish
            if alvik.is_target_reached():
                current_state = STATE_SCAN # Go back and verify
            
            previous_state = STATE_WAIT_STEP
            time.sleep(0.1)

        # 6. STATE_BLIND_CALC
        elif current_state == STATE_BLIND_CALC:
            print("State: BLIND CALC")
            
            final_push = estimated_dist - TARGET_DIST_CM
            
            if final_push > 0:
                print(f"Final Push: {final_push:.1f} cm")
                update_display("Final Push", f"{final_push:.1f} cm")
                alvik.move(final_push, blocking=False)
                current_state = STATE_BLIND_EXECUTE
            else:
                print("Already at Target")
                current_state = STATE_SUCCESS
            
            previous_state = STATE_BLIND_CALC

        # 7. STATE_BLIND_EXECUTE
        elif current_state == STATE_BLIND_EXECUTE:
            if alvik.is_target_reached():
                current_state = STATE_SUCCESS
            previous_state = STATE_BLIND_EXECUTE
            time.sleep(0.1)

        # 8. STATE_SUCCESS
        elif current_state == STATE_SUCCESS:
            if previous_state != STATE_SUCCESS:
                print("State: SUCCESS")
                update_display("Target Reached", "Done")
                alvik.stop()
                alvik.left_led.set_color(0, 1, 0)
                alvik.right_led.set_color(0, 1, 0)
                previous_state = STATE_SUCCESS
            
            time.sleep(0.1)

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    if screen: screen.show_lines("Error", str(e)[:16])
    for _ in range(5):
        alvik.left_led.set_color(1,0,0)
        time.sleep(0.2)
        alvik.left_led.set_color(0,0,0)
        time.sleep(0.2)

finally:
    print("Program End.")
    alvik.stop()
    alvik.left_led.set_color(0,0,0)
    alvik.right_led.set_color(0,0,0)