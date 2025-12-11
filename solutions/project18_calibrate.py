# Project 18: Capstone Menu System
# Version: V05
# Created with the help of Gemini Pro
#
# LOGIC FLOW:
# 1. Startup -> Check for 'robot_config.txt'.
# 2. If Missing -> Force CALIBRATION MODE.
# 3. If Found   -> Go to MENU MODE.
#
# USES: nhs_robotics.get_closest_distance for sensor reading.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
from qwiic_huskylens import QwiicHuskylens
from qwiic_i2c.micropython_i2c import MicroPythonI2C
from nhs_robotics import get_closest_distance
import os

# --- CONSTANTS ---
FILE_NAME = "robot_config.txt"
CALIBRATION_DIST_CM = 7.0  # Max distance to accept a calibration reading

# Colors (R, G, B)
COLOR_MENU = (0, 1, 0)         # Green
COLOR_CALIB = (1, 0, 1)        # Purple
COLOR_TEST = (1, 1, 0)         # Yellow
COLOR_RUN = (1, 1, 1)          # White
COLOR_ERROR = (1, 0, 0)        # Red

# States
STATE_MENU = 0
STATE_CALIBRATION = 1
STATE_TEST = 2
STATE_OPERATION = 3

# --- HARDWARE SETUP ---
alvik = ArduinoAlvik()
alvik.begin()

# Camera Setup
try:
    alvik_i2c = MicroPythonI2C(scl=12, sda=11)
    huskylens = QwiicHuskylens(i2c_driver=alvik_i2c)
    if not huskylens.begin():
        print("HuskyLens not connected!")
        alvik.left_led.set_color(*COLOR_ERROR)
        alvik.right_led.set_color(*COLOR_ERROR)
        while True: pass
except Exception as e:
    print(f"Hardware Error: {e}")

# --- HELPER FUNCTIONS ---

def save_k_constant(k_val):
    """Writes the K float value to the text file."""
    try:
        with open(FILE_NAME, "w") as f:
            f.write(str(k_val))
        print(f"SAVED: K = {k_val}")
        return True
    except OSError:
        print("Error saving file.")
        return False

def load_k_constant():
    """Reads K from file. Returns float or None."""
    try:
        with open(FILE_NAME, "r") as f:
            data = f.read()
            return float(data)
    except (OSError, ValueError):
        return None

# --- INITIALIZATION ---

# Check memory on startup
k_constant = load_k_constant()

if k_constant is None:
    print("Config missing. Forcing Calibration.")
    current_state = STATE_CALIBRATION
else:
    print(f"Loaded K: {k_constant}. Ready.")
    current_state = STATE_MENU

# --- MAIN STATE MACHINE ---

while True:
    
    # =========================================================================
    # STATE: MENU (Green)
    # =========================================================================
    if current_state == STATE_MENU:
        alvik.left_led.set_color(*COLOR_MENU)
        alvik.right_led.set_color(*COLOR_MENU)
        
        # Check Buttons
        if alvik.get_touch_up():
            current_state = STATE_CALIBRATION
            print("Mode: CALIBRATION")
            sleep_ms(500) # Debounce
            
        elif alvik.get_touch_down():
            # Only allow test if K exists
            if k_constant is not None:
                current_state = STATE_TEST
                print("Mode: TEST")
            else:
                # Flash Red if they try to test without K
                alvik.left_led.set_color(*COLOR_ERROR)
                alvik.right_led.set_color(*COLOR_ERROR)
                sleep_ms(200)
            sleep_ms(500)
            
        elif alvik.get_touch_center(): # OK Button
            if k_constant is not None:
                current_state = STATE_OPERATION
                print("Mode: OPERATION")
            else:
                alvik.left_led.set_color(*COLOR_ERROR)
                sleep_ms(200)
            sleep_ms(500)

    # =========================================================================
    # STATE: CALIBRATION (Purple)
    # =========================================================================
    elif current_state == STATE_CALIBRATION:
        alvik.left_led.set_color(*COLOR_CALIB)
        alvik.right_led.set_color(*COLOR_CALIB)
        
        # 1. Read ToF Sensor using student library
        # alvik.get_distance() returns a tuple of 5 sensors.
        # We unpack (*) them into get_closest_distance(d1, d2, d3, d4, d5)
        measurements = alvik.get_distance()
        tof_dist = get_closest_distance(*measurements)
        
        # 2. Read Camera
        huskylens.request()
        blocks = huskylens.blocks # No parentheses!
        
        # 3. Validation Logic
        if len(blocks) > 0:
            tag = blocks[0]
            
            # Only calibrate if tag is very close (reliable)
            if 0 < tof_dist < CALIBRATION_DIST_CM:
                # FORMULA: K = Width (pixels) * Distance (cm)
                new_k = tag.width * tof_dist
                
                # Save
                save_k_constant(new_k)
                k_constant = new_k # Update memory variable
                
                # Feedback: Flash White then return to Menu
                alvik.left_led.set_color(*COLOR_RUN)
                alvik.right_led.set_color(*COLOR_RUN)
                sleep_ms(1000)
                current_state = STATE_MENU
        
        # Escape Hatch: Press X to cancel
        if alvik.get_touch_cancel():
            current_state = STATE_MENU
            sleep_ms(500)
            
        sleep_ms(50)

    # =========================================================================
    # STATE: TEST MODE (Yellow)
    # =========================================================================
    elif current_state == STATE_TEST:
        alvik.left_led.set_color(*COLOR_TEST)
        alvik.right_led.set_color(*COLOR_TEST)
        
        huskylens.request()
        blocks = huskylens.blocks
        
        if len(blocks) > 0:
            tag = blocks[0]
            # FORMULA: Distance = K / Width
            calculated_dist = k_constant / tag.width
            print(f"Tag Width: {tag.width}px  |  Calc Dist: {calculated_dist:.2f} cm")
        else:
            print("No Tag Seen")
            
        # Exit Condition (OK or X)
        if alvik.get_touch_cancel() or alvik.get_touch_center():
            current_state = STATE_MENU
            sleep_ms(500)
            
        sleep_ms(100)

    # =========================================================================
    # STATE: OPERATION (White)
    # =========================================================================
    elif current_state == STATE_OPERATION:
        alvik.left_led.set_color(*COLOR_RUN)
        alvik.right_led.set_color(*COLOR_RUN)
        
        # NO-OP: Placeholder for mission code
        
        # Exit for testing purposes
        if alvik.get_touch_cancel():
            current_state = STATE_MENU
            sleep_ms(500)
            
        sleep_ms(100)

