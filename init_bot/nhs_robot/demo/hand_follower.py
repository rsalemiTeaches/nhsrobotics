from arduino_alvik import ArduinoAlvik
from time import sleep_ms

# Developed with the assistance of Google Gemini V01

def run_hand_follower(alvik):
    """
    Runs the hand follower logic loop.
    Blocks until the 'Cancel' (X) button is touched.
    """
    reference = 10.0 # Target distance in cm
    
    print("Hand Follower Started. Press 'X' to stop.")
    
    # Set initial LED state
    alvik.left_led.set_color(0, 1, 0)
    alvik.right_led.set_color(0, 1, 0)

    # Main execution loop for this specific demo
    while not alvik.get_touch_cancel():
        # Get distances: Left, Center-Left, Center, Center-Right, Right
        # We only use Center (C) for this simple follower
        L, CL, C, CR, R = alvik.get_distance()
        
        # Calculate error (Distance - Target)
        error = C - reference
        
        # Simple Proportional control
        # If error is positive (too far), move forward
        # If error is negative (too close), move backward
        speed = error * 10
        
        # Limit speed to avoid crazy behavior (optional but good practice)
        if speed > 50: speed = 50
        if speed < -50: speed = -50
        
        alvik.set_wheels_speed(speed, speed)
        
        sleep_ms(100)

    # Cleanup before returning
    alvik.stop()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    print("Hand Follower Stopped.")

if __name__ == "__main__":
    # Allow running this file standalone for testing
    alvik = ArduinoAlvik()
    alvik.begin()
    
    # Wait for a touch to start (as per original logic logic)
    while alvik.get_touch_ok():
        sleep_ms(50)
        
    run_hand_follower(alvik)