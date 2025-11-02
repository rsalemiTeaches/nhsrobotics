# Project 03: Proximity Color Indicator
# This program finds the single closest object to the robot and changes
# the color of BOTH LEDs based on how near it is. This is a great way to
# visualize distance.

from arduino_alvik import ArduinoAlvik  # Import Alvik controller definition
from time import sleep_ms

# Import an NHS helper function from nhs robotics
from nhs_robotics import get_closest_distance

# Create an object for our robot.
alvik = ArduinoAlvik()

# --- Configuration ---
# We will define different distance thresholds for each color.
# Students can change these values to tune the robot's response.
THRESHOLD_RED = 3      # For very close objects
THRESHOLD_PURPLE = 10   # For medium-range objects
THRESHOLD_BLUE = 15    # For far-away objects


try:

    alvik.begin() # Start the robot

    print("Proximity Color Indicator Project Started.")
    print("LEDs will change color based on the closest object.")
    print("Press the Cancel (X) button to stop.")

    # --- Main Loop ---
    while True:
        # Check if the user wants to stop the program.
        if alvik.get_touch_cancel():
            print("Cancel button pressed. Exiting.")
            break

        # 1. Read the raw distance sensor zones.
        raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r = alvik.get_distance()

        # 2. Use the get_closet_distance function to find the single closest distance.
        closest_distance = get_closest_distance(raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r)

        # 3. Work: SET THE LED COLOR 
        # This series of if/elif/else checks from closest to farthest.
        # We now call set_color with the three numbers for (Red, Green, Blue).
        #
        # Set the LEDs to RED if the closest distance
        # is less than THRESHOLD_RED
        if closest_distance < THRESHOLD_RED:
            alvik.left_led.set_color(1, 0, 0)  # Red
            alvik.right_led.set_color(1, 0, 0) # Red
        
        # WORK: Set the LEDs to PURPLE if the closest distance
        # WORK is less than THRESHOLD_PURPLE

        # WORK: Set the LEDs to BLUE if the closest distance
        # WORK: is less than THRESHOLD_BLUE

        ## WORK: Set LEDs to GREEN if the closest distance is 
        ## WORK: Further than all thresholds

        # A small delay is important in a loop to keep
        # the sensor working properly.
        sleep_ms(50)

finally:
    # WORK When the programs ends either due to the user pressing
    # WORK the X button or some other interrupt, turn off all the
    # WORK LEDs and stop the robot.
    pass  # replace this line with your code.
