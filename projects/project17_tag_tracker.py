# Project 15: Tag Tracker


from arduino_alvik import ArduinoAlvik
from qwiic_huskylens import QwiicHuskylens
from qwiic_i2c.micropython_i2c import MicroPythonI2C
import time
import sys

# --- CONFIGURATION ---
CENTER_X = 160
DEADZONE = 40 
LEFT_THRESHOLD = CENTER_X - DEADZONE  # 120
RIGHT_THRESHOLD = CENTER_X + DEADZONE # 200

# --- SETUP HARDWARE ---
# 1. Initialize the Robot
alvik = ArduinoAlvik()
alvik.begin()

# 2. Initialize the Camera (I2C)
print("Checking Camera...")
try:
    i2c = MicroPythonI2C(scl=12, sda=11)
    lens = QwiicHuskylens(i2c)
    lens.begin()
    print("HuskyLens Connected!")
except:
    print("Camera Error! Check wires.")
    sys.exit()

# 3. Set Algorithm
print("Switching to Tag Recognition...")
lens.set_algorithm(lens.ALGORITHM_TAG_RECOGNITION)

# --- MAIN LOOP ---
print("Scanning for AprilTags...")

while True:
    # Ask the camera for new data
    if lens.request():
        
        # Check if we saw any tags
        if len(lens.blocks) > 0:
            tag = lens.blocks[0]
            x = tag.xCenter
            
            # --- STUDENT WORK SECTION ---
            # TODO: Write your Logic Below!
            
            # 1. If tag is in the CENTER (between 120 and 200)
            if x > LEFT_THRESHOLD and x < RIGHT_THRESHOLD:
                # Turn BOTH LEDs Green
                pass # Delete 'pass' and write your code
            
            # 2. If tag is to the LEFT
            elif x <= LEFT_THRESHOLD:
                # Turn LEFT LED Green, RIGHT LED Off
                pass 
                
            # 3. If tag is to the RIGHT
            elif x >= RIGHT_THRESHOLD:
                # Turn LEFT LED Off, RIGHT LED Green
                pass
                
        else:
            # 4. If NO tag is seen (The list is empty)
            # Turn BOTH LEDs Off
            pass
            
    # Small delay to prevent crashing
    time.sleep(0.05)
# --- END OF FILE ---
