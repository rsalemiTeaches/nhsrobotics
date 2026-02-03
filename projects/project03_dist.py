# ==========================================================
#              Project 03: Proximity Indicator
#       In this project, you'll use the SuperBot to monitor
#       distances and change the LED colors as a warning.
# ==========================================================
# Version: V01

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms

# 1. Initialize the base Alvik 
alvik = ArduinoAlvik()

# WORK: Initialize the SuperBot object and name it sb
# Remove the hashtag from the line below to create the SuperBot
# sb = SuperBot(alvik) 

# 2. Configuration: Set the distance thresholds (in cm)
THRESHOLD_RED = 3      # Very close
THRESHOLD_PURPLE = 10   # Medium range
THRESHOLD_BLUE = 15    # Nearby

try:
    alvik.begin()
    print("Project 03 Started using SuperBot.")

    # 3. Main loop: Run until the Cancel (X) button is pressed
    while not alvik.get_touch_cancel():

        # 4. Get the single closest distance directly from the SuperBot
        # The SuperBot handles reading the sensors and finding the minimum value
        closest_distance = sb.get_closest_distance()

        # 5. if/elif/else chain for color warning logic 
        # We control the LEDs directly through the alvik object
        
        # Very Close
        if closest_distance < THRESHOLD_RED:
            alvik.left_led.set_color(1, 0, 0) # Red
            alvik.right_led.set_color(1, 0, 0)
        
        # Close
        # WORK: Uncomment the elif line below to enable the Purple check
        # elif closest_distance < THRESHOLD_PURPLE:
            alvik.left_led.set_color(1, 0, 1) # Purple
            alvik.right_led.set_color(1, 0, 1)
            
        # Nearby
        # WORK: Write the elif statement for THRESHOLD_BLUE. 
        # We added 'pass' so the code runs, but you need to add the LED code.
        elif closest_distance < THRESHOLD_BLUE:
            # WORK: Set LEDs to Blue (0, 0, 1)
            pass
            
        # All Clear
        # WORK: Write the else statement
        else:
            # WORK: Set LEDs to Green (0, 1, 0)
            pass

        # Small delay for sensor stability
        sleep_ms(50)

finally:
    # 6. Cleanup logic: Leave the robot in a safe state
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()  # Shut down background threads

# Developed with the assistance of Google Gemini
