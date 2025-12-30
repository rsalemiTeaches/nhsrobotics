# test_navigation.py
# Version: V03
# Purpose: Tests the physical execution of the calculated approach vector.
# Logic: Scans for a tag -> Calculates Vector -> Turns -> Drives -> Aligns.
# Developed with the assistance of Google Gemini.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time
import sys

# --- SETUP ---
print("Loading test_navigation.py V03")
print("Initializing Robot...")
alvik = ArduinoAlvik()
alvik.begin()

sb = SuperBot(alvik) 
sb.enable_info_logging()

# --- CONFIGURATION ---
TARGET_DIST_CM = 20  # Stop 20cm away from the tag

sb.update_display("Nav Test", "Searching...")
print("\n--- NAVIGATION TEST ---")
print("Point the robot at a tag.")

found_tag = None

# 1. FIND THE TAG
while True:
    if not sb.husky:
        print("HuskyLens error.")
        sys.exit()

    sb.husky.request()
    
    if len(sb.husky.blocks) > 0:
        found_tag = sb.husky.blocks[0]
        print(f"Tag Found: ID {found_tag.id}")
        break
    
    time.sleep(0.1)

# 2. CALCULATE THE VECTOR
vector = sb.calculate_approach_vector(found_tag, target_dist_cm=TARGET_DIST_CM)

print("-" * 30)
print(f"Current Position: Tag is at {vector.angle:.1f} deg, {vector.distance:.1f} cm away.")
print(f"PLAN: Rotate {vector.angle:.1f} deg -> Drive {vector.distance:.1f} cm -> Align {-vector.angle:.1f} deg")
print("-" * 30)

# 3. EXECUTE "TURN-DRIVE-ALIGN"
time.sleep(2) 

# Step A: Face the destination
sb.update_display("Executing", "Rotating...")
print(f"Rotating {vector.angle:.1f} degrees...")
sb.bot.rotate(vector.angle)

# Step B: Drive to destination
sb.update_display("Executing", "Driving...")
print(f"Driving {vector.distance:.1f} cm...")
sb.drive_distance(vector.distance) 

# Step C: Align (Restore original heading / Square up)
# We rotate back by the negative of the approach angle.
sb.update_display("Executing", "Aligning...")
print(f"Aligning {-vector.angle:.1f} degrees...")
sb.bot.rotate(-vector.angle)

# 5. FINISH
sb.update_display("Arrived", "Target Reached")
print("Maneuver Complete.")

alvik.stop()
