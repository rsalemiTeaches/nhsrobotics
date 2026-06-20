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
# We name it 'sb' as per the SuperBot naming convention.
sb = SuperBot(alvik) 

# 2. Configuration: Set the distance thresholds (in cm)
THRESHOLD_RED = 3      # Very close
THRESHOLD_PURPLE = 10   # Medium range
THRESHOLD_BLUE = 15    # Nearby

try:
    alvik.begin()
    print("Project 03 Started using SuperBot.")

    # 3. Main loop: Run until the Cancel (X) button is pressed
    while not alvik.get_touch_cancel():

        
        # IMPORTANT: Sleep for 10 ms so that the robot 
        # has time to process the button presses.
        sleep_ms(10)

        # 4. Get the single closest distance directly from the SuperBot
        # The SuperBot handles reading the sensors and finding the minimum value
        closest_distance = sb.get_closest_distance()

        # --- FLEX: OLED DISPLAY ---
        # Show the real-time distance on the OLED screen
        sb.update_display("Dist:", closest_distance)

        # 5. if/elif/else chain for color warning logic 
        # We control the LEDs directly through the alvik object
        
        # Very Close
        if closest_distance < THRESHOLD_RED:
            alvik.left_led.set_color(1, 0, 0) # Red
            alvik.right_led.set_color(1, 0, 0)
        
        # Close
        elif closest_distance < THRESHOLD_PURPLE:
            alvik.left_led.set_color(1, 0, 1) # Purple
            alvik.right_led.set_color(1, 0, 1)
            
        # Nearby
        elif closest_distance < THRESHOLD_BLUE:
            alvik.left_led.set_color(0, 0, 1) # Blue
            alvik.right_led.set_color(0, 0, 1)
            
        # All Clear
        else:
            alvik.left_led.set_color(0, 1, 0) # Green
            alvik.right_led.set_color(0, 1, 0)

finally:
    # 6. Cleanup logic: Leave the robot in a safe state
    # We turn off LEDs and clear the display
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    sb.update_display("Program", "Stopped")
    print("Project 03 Stopped.")
    