# main.py - Test script for the final nhs_robotics library

import nhs_robotics
import time

print("--- Starting Class-based OLED Test ---")

# A student's code is now this simple:
screen = nhs_robotics.oLED()

# Check if the screen initialized correctly before using it
if screen.display:
    print("Screen object created. Displaying text...")
    
    screen.show_lines(
        "Hello Alvik!",
        "The class works!",
        "Final version."
    )
    
    time.sleep(5)
    
    print("Clearing the screen.")
    screen.clear()
else:
    print("Skipping display test because screen failed to initialize.")

print("--- Test Complete ---")