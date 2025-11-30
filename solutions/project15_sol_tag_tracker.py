# Project 15: Hello HuskyLens (Tag Edition)
#
# MISSION:
# 1. Initialize the HuskyLens.
# 2. Switch to AprilTag Recognition mode.
# 3. Read the position of the tag (X-coordinate).
# 4. Turn on LEDs to match the tag's position.

from arduino_alvik import ArduinoAlvik
from qwiic_huskylens import QwiicHuskylens
from qwiic_i2c.micropython_i2c import MicroPythonI2C
import time
import sys

# --- CONFIGURATION ---
# The HuskyLens screen is 320 pixels wide.
# 0 is Left, 320 is Right, 160 is Center.
CENTER_X = 160
DEADZONE = 40  # How wide is the "Center" zone? (160 +/- 40)

# Calculate thresholds
LEFT_THRESHOLD = CENTER_X - DEADZONE  # 120
RIGHT_THRESHOLD = CENTER_X + DEADZONE # 200

# --- SETUP HARDWARE ---
alvik = ArduinoAlvik()
alvik.begin()

print("Checking Camera...")
try:
    # We use the Alvik's built-in I2C ports (SCL=12, SDA=11)
    i2c = MicroPythonI2C(scl=12, sda=11)
    lens = QwiicHuskylens(i2c)
    lens.begin()
    print("HuskyLens Connected!")
except:
    print("Camera Error! Check your wires.")
    sys.exit()

# --- SETUP ALGORITHM ---
# Switch to TAG Recognition instead of Color
print("Switching to Tag Recognition...")
lens.set_algorithm(lens.ALGORITHM_TAG_RECOGNITION)

# --- MAIN LOOP ---
print("Scanning for AprilTags...")

while True:
    # 1. Ask the camera for new data
    # .request() returns True if it successfully talked to the camera
    if lens.request():
        
        # 2. Check if we saw any blocks (tags)
        if len(lens.blocks) > 0:
            # We only care about the first tag we see
            tag = lens.blocks[0]
            x = tag.xCenter
            
            # --- LOGIC: Where is the tag? ---
            
            # CASE A: Tag is in the CENTER
            if x > LEFT_THRESHOLD and x < RIGHT_THRESHOLD:
                print(f"CENTER (x={x})")
                alvik.left_led.set_color(0, 1, 0)  # Green
                alvik.right_led.set_color(0, 1, 0) # Green
            
            # CASE B: Tag is on the LEFT
            elif x <= LEFT_THRESHOLD:
                print(f"LEFT (x={x})")
                alvik.left_led.set_color(0, 1, 0)  # Green
                alvik.right_led.set_color(0, 0, 0) # Off
                
            # CASE C: Tag is on the RIGHT
            elif x >= RIGHT_THRESHOLD:
                print(f"RIGHT (x={x})")
                alvik.left_led.set_color(0, 0, 0)  # Off
                alvik.right_led.set_color(0, 1, 0) # Green
                
        else:
            # CASE D: No Tag Seen
            print("No Tag")
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)
            
    else:
        # Camera communication failed momentarily
        pass

    # Small delay to keep the loop running smoothly
    time.sleep(0.05)
    