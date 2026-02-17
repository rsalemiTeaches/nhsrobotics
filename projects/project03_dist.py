# ==========================================================
#              Project 03: Proximity Indicator
#       In this project, you'll use the SuperBot to monitor
#       distances and change the LED colors as a warning.
# ==========================================================
# Version: V02

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms

# 1. Initialize the base Alvik 
alvik = ArduinoAlvik()

# WORK: Initialize the SuperBot object and name it sb
# Hint: sb = SuperBot(alvik)
# sb = 

# 2. Configuration: Set the distance thresholds (in cm)
THRESHOLD_RED = 3      # Very close
THRESHOLD_PURPLE = 10   # Medium range
THRESHOLD_BLUE = 15    # Nearby

try:
    alvik.begin()
    print("Project 03 Started using SuperBot.")

    # 3. Main loop: Run until the Cancel (X) button is pressed
    while not alvik.get_touch_cancel():


        # WORK: Sleep for 10 ms so that the robot 
        # has time to process the button presses.
        

        # WORK: Get the single closest distance from the SuperBot and store it 
        # Hint: closest_distance = sb.get_closest_distance()
        closest_distance = 0 # Replace 0 with the correct command

        # --- WORK (FLEX): OLED DISPLAY ---
        # To show the distance on the screen, use the command below:
        # sb.update_display("Dist:", closest_distance)
        

        # 4. WORK: Complete the if/elif/else chain for color warning logic 
        
        # Zone 1: Very Close
        if closest_distance < THRESHOLD_RED:
            alvik.left_led.set_color(1, 0, 0) # Red
            alvik.right_led.set_color(1, 0, 0)
        
        # Zone 2: Close (Purple)
        # elif ...
            
        # Zone 3: Nearby (Blue)
        # elif ...
            
        # Zone 4: All Clear (Green)
        # else:
        

        # Small delay for sensor stability
        sleep_ms(50)

finally:
    # 5. WORK: Cleanup logic
    # Turn off both LEDs so they don't stay lit!
    # Hint: set_color(0, 0, 0)
    
    print("Project 03 Stopped.")