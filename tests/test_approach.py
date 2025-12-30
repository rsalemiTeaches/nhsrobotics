# test_approach.py
# Version: V01
# Purpose: Validates the calculate_approach_vector() math in SuperBot V19.
#
# Tests included:
# 1. Math Verification (Mock Data): Feeds fake tag data to verify the trig logic.
# 2. Live Sensor Test: Continuously prints the calculated vector for a real tag.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time
import sys

# --- SETUP ---
print("Initializing...")
alvik = ArduinoAlvik()
alvik.begin()

sb = SuperBot(alvik) # Using 'sb' convention
sb.enable_info_logging()

# --- MOCK OBJECTS ---
class MockBlock:
    def __init__(self, x, width):
        self.x = x
        self.width = width
        self.height = width # Assuming square tag
        self.ID = 1

# --- TESTS ---

def test_1_math_verification():
    """
    Test 1: Static Math Check.
    We create fake blocks representing specific scenarios and check the math.
    """
    sb.update_display("Test 1: Math", "Checking Trig...")
    print("\n--- TEST 1: MATH VERIFICATION ---")
    
    # Scenario A: Tag is Perfectly Centered (x=160), 100cm away
    # Expected: Angle = 0, Distance = 100 - 20 = 80cm
    # Note: K_CONSTANT = 1624. So width = 1624 / 100 = 16.24
    
    mock_center = MockBlock(x=160, width=16.24)
    vector_a = sb.calculate_approach_vector(mock_center, target_dist_cm=20)
    
    print(f"Scenario A (Center): Angle={vector_a.angle:.1f} (Exp: 0), Dist={vector_a.distance:.1f} (Exp: 80)")
    
    # Scenario B: Tag is Far Left (x=0).
    # Pixel Offset = 160. Degrees = 160 / (320/60) = 30 degrees Left.
    # We are 100cm away (hypotenuse).
    # Lateral Offset (x) = 100 * sin(30) = 50cm
    # Forward Dist (y) = 100 * cos(30) = 86.6cm
    # Target (20cm short) -> y_approach = 66.6cm, x_approach = 50cm
    # Resulting Vector: Dist = sqrt(50^2 + 66.6^2), Angle = atan(50/66.6)
    
    mock_left = MockBlock(x=0, width=16.24)
    vector_b = sb.calculate_approach_vector(mock_left, target_dist_cm=20)
    
    print(f"Scenario B (Left): Angle={vector_b.angle:.1f} (Exp: ~37), Dist={vector_b.distance:.1f} (Exp: ~83)")
    
    sb.log_info("Math Check Done")
    time.sleep(3)

def test_2_live_readout():
    """
    Test 2: Live Feedback.
    Reads the real HuskyLens.
    Calculates the approach vector.
    Displays it on the screen so user can walk a tag around the robot.
    """
    sb.update_display("Test 2: Live", "Show Tag Now")
    print("\n--- TEST 2: LIVE SENSOR ---")
    print("Press Ctrl+C to stop.")
    
    while True:
        # Get REAL data
        if not sb.husky:
            print("HuskyLens not connected!")
            break
            
        sb.husky.request()
        
        if len(sb.husky.blocks) > 0:
            tag = sb.husky.blocks[0]
            
            # Calculate the "Arrow"
            vector = sb.calculate_approach_vector(tag, target_dist_cm=20)
            
            # Display
            # Line 1: Raw Tag Data
            # Line 2: Calculated Turn Angle
            # Line 3: Calculated Drive Distance
            
            line1 = f"T:{tag.ID} X:{tag.x} W:{tag.width}"
            line2 = f"Turn: {vector.angle:.1f} deg"
            line3 = f"Drive: {vector.distance:.1f} cm"
            
            sb.update_display(line1, line2, line3)
            print(f"LIVE: {line2}, {line3}")
            
        else:
            sb.update_display("No Tag Seen", "Searching...")
        
        time.sleep(0.2)

# --- MAIN ---

try:
    test_1_math_verification()
    test_2_live_readout()
    
except KeyboardInterrupt:
    print("\nTest Aborted")
    sb.bot.stop() # Safety Stop

# Developed with the assistance of Google Gemini