# test_approach.py
# Version: V03
# Purpose: Validates the calculate_approach_vector() math in SuperBot.
# Updates: Fixed case sensitivity for 'id' attribute (was ID, now id).

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time
import sys

# --- SETUP ---
print("Loading test_approach.py V03")
print("Initializing...")
alvik = ArduinoAlvik()
alvik.begin()

sb = SuperBot(alvik) 
sb.enable_info_logging()

# --- MOCK OBJECTS ---
class MockBlock:
    def __init__(self, xCenter, width):
        # Updated to use xCenter to match the real HuskyLens library found on robot
        self.xCenter = xCenter 
        self.width = width
        self.height = width # Assuming square tag
        self.id = 1 # Lowercase 'id' to match library

# --- TESTS ---

def test_1_math_verification():
    """
    Test 1: Static Math Check.
    We create fake blocks representing specific scenarios and check the math.
    """
    sb.update_display("Test 1: Math", "Checking Trig...")
    print("\n--- TEST 1: MATH VERIFICATION ---")
    
    # Scenario A: Tag is Perfectly Centered (x=160), 100cm away
    # K_CONSTANT = 1624. Width = 16.24
    
    mock_center = MockBlock(xCenter=160, width=16.24)
    vector_a = sb.calculate_approach_vector(mock_center, target_dist_cm=20)
    
    print(f"Scenario A (Center): Angle={vector_a.angle:.1f} (Exp: 0), Dist={vector_a.distance:.1f} (Exp: 80)")
    
    # Scenario B: Tag is Far Left (x=0).
    # Lateral Offset (x) = 100 * sin(30) = 50cm
    # Forward Dist (y) = 100 * cos(30) = 86.6cm
    # Target (20cm short) -> y_approach = 66.6cm, x_approach = 50cm
    
    mock_left = MockBlock(xCenter=0, width=16.24)
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
            
            # Accessing xCenter safely for display since we know it exists now
            # Changed tag.ID to tag.id to match library
            line1 = f"T:{tag.id} X:{tag.xCenter} W:{tag.width}"
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