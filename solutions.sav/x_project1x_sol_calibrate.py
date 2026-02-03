# Project 16: The Optical Rangefinder (Calibration Tool)
#
# GOAL:
# Turn the Alvik into a precision measurement tool using Computer Vision.
# 1. CALIBRATE: Use the ToF sensor to auto-calculate the camera's K constant.
# 2. SAVE: Write that calibration data to the robot's permanent memory.
# 3. MEASURE: Use the camera to estimate distance instantly.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
from qwiic_huskylens import QwiicHuskylens
from qwiic_i2c.micropython_i2c import MicroPythonI2C
import os # Needed to check if files exist

print("Starting Project 16: Optical Rangefinder")

# ---------------------------------------------------------
# SETUP: CRITICAL ORDER OF OPERATIONS
# ---------------------------------------------------------
# 1. Start the Robot FIRST
alvik = ArduinoAlvik()
alvik.begin()

# 2. Connect the Camera
try:
    alvik_i2c = MicroPythonI2C(scl=12, sda=11)
    huskylens = QwiicHuskylens(i2c_driver=alvik_i2c)
    
    # 3. Start the Camera
    if not huskylens.begin():
        print("CRITICAL ERROR: HuskyLens not found!")
        while True: # Flash Red forever
            alvik.left_led.set_color(1, 0, 0)
            sleep_ms(200)
            alvik.left_led.set_color(0, 0, 0)
            sleep_ms(200)
    else:
        print("HuskyLens connected successfully!")

except Exception as e:
    print(f"Setup Error: {e}")

# --- State Constants ---
STATE_CALIBRATE = 0
STATE_MEASURING = 1

# --- Global Variables ---
current_state = STATE_CALIBRATE
calibrated_k = None # Pythonic initialization

# ---------------------------------------------------------
# HELPER FUNCTIONS: The Robot's "Long Term Memory"
# ---------------------------------------------------------

def save_calibration(k_value):
    """Writes the K value to a text file so we don't lose it."""
    print(f"Saving K={k_value} to permanent memory...")
    try:
        f = open('config.txt', 'w')
        f.write(str(k_value)) 
        f.close()
        print("Saved successfully!")
    except Exception as e:
        print(f"Error saving file: {e}")

def load_calibration():
    """Reads the K value from the text file."""
    print("Looking for saved calibration...")
    try:
        f = open('config.txt', 'r')
        data = f.read()
        f.close()
        k = float(data)
        print(f"Found saved data! K = {k}")
        return k
    except OSError:
        print("No calibration file found. Starting fresh.")
        # Pythonic change: Return None to indicate absence of value
        return None

# ---------------------------------------------------------
# MAIN PROGRAM
# ---------------------------------------------------------

# 1. Try to load previous settings
calibrated_k = load_calibration()

# Pythonic check for validity
if calibrated_k is not None:
    print("Calibration loaded. Ready to measure.")
    current_state = STATE_MEASURING
else:
    print("Robot is uncalibrated.")
    current_state = STATE_CALIBRATE

# === SAFETY BLOCK START ===
try:
    while not alvik.get_touch_cancel():
        
        # --- SENSE (Gather Data) ---
        
        # 1. Get ToF Distance (The "Truth" for calibration)
        d1, d2, d3, d4, d5 = alvik.get_distance()
        
        # We use the Center Sensor (d3) as our ground truth.
        tof_cm = d3
        
        # Sanity check: If sensor returns -1 (infinity), treat as 0/Invalid
        if tof_cm < 0:
            tof_cm = 0
        
        # 2. Get Vision Data
        tag_width_px = 0
        tag_id = 0
        
        try:
            if huskylens.request():
                if len(huskylens.blocks) > 0:
                    target = huskylens.blocks[0]
                    tag_width_px = target.width
                    tag_id = target.id
        except Exception as e:
            print(f"Camera Error: {e}")

        # --- THINK & ACT (State Machine) ---
        
        if current_state == STATE_CALIBRATE:
            # --- MODE: TEACHING THE ROBOT ---
            alvik.left_led.set_color(1, 0, 1) # Purple
            alvik.right_led.set_color(1, 0, 1)

            # We need BOTH a valid visual target AND a valid ToF reading
            # to perform cross-sensor calibration.
            valid_target = (tag_width_px > 0) and (tof_cm > 0)

            if valid_target:
                # Calculate what K WOULD be right now
                current_k = tof_cm * tag_width_px
                
                print(f"ToF: {tof_cm}cm | Width: {tag_width_px}px | K: {current_k:.0f}")
                
                # Visual Helper: Is the tag roughly square?
                ratio = target.width / target.height
                if ratio > 0.9 and ratio < 1.1:
                     print("  [ALIGNED - PRESS OK]  ")
                else:
                     print("  [Angled - Straighten Tag] ")
            else:
                print(f"ToF: {tof_cm}cm | [NO TAG SEEN]")

            # ACTION: User locks in the calibration
            if alvik.get_touch_ok():
                if valid_target:
                    # === CROSS-SENSOR CALIBRATION ===
                    # K = Real_Distance * Pixel_Width
                    calibrated_k = tof_cm * tag_width_px
                    
                    print("---------------------------------")
                    print(f"CALIBRATION LOCKED! K = {calibrated_k}")
                    print("---------------------------------")
                    
                    save_calibration(calibrated_k)
                    sleep_ms(1000) 
                    current_state = STATE_MEASURING
                else:
                    print("ERROR: Need both Tag and Distance to calibrate!")
                    alvik.left_led.set_color(1, 0, 0) # Red flash
                    sleep_ms(500)
                    
        elif current_state == STATE_MEASURING:
            # --- MODE: USING THE ROBOT ---
            alvik.left_led.set_color(0, 1, 0) # Green
            alvik.right_led.set_color(0, 1, 0)

            if tag_width_px > 0:
                # === THE MAGIC FORMULA ===
                # Distance = K / Width
                vision_dist_cm = calibrated_k / tag_width_px
                
                print(f"Vision: {vision_dist_cm:.1f} cm  |  ToF: {tof_cm:.1f} cm")
                
                # Accuracy Check: Blue if match
                diff = abs(vision_dist_cm - tof_cm)
                if diff < 1.0 and tof_cm > 0:
                    alvik.left_led.set_color(0, 0, 1) # Blue
                    alvik.right_led.set_color(0, 0, 1)
            else:
                print("Searching for tag...")
                alvik.left_led.set_color(0, 0.1, 0)

            # Recalibration trigger
            if alvik.get_touch_center():
                print("Switching back to Calibration Mode...")
                current_state = STATE_CALIBRATE
                sleep_ms(1000)

        sleep_ms(100)

except Exception as e:
    print(f"CRASH ERROR: {e}")
    alvik.left_led.set_color(1, 0, 0)
    alvik.right_led.set_color(1, 0, 0)

finally:
    print("Program Finished. Safely stopping robot.")
    alvik.set_wheels_speed(0, 0) 
    alvik.left_led.set_color(0, 0, 0) 
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()