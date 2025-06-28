# Project 03: Proximity Color Indicator
# This program finds the single closest object to the robot and changes
# the color of BOTH LEDs based on how near it is. This is a great way to
# visualize distance.

from arduino_alvik import ArduinoAlvik
import time

# Create an object for our robot.
alvik = ArduinoAlvik()

# --- Configuration ---
# We will define different distance thresholds for each color.
# Students can change these values to tune the robot's response.
THRESHOLD_RED = 3      # For very close objects
THRESHOLD_YELLOW = 10   # For medium-range objects
THRESHOLD_BLUE = 15    # For far-away objects


# --- Helper Function (Provided to Students) ---
# This function takes the 5 raw sensor readings, finds the single
# closest valid reading (ignoring zeros), and returns it.
def get_closest_distance(d_l, d_cl, d_c, d_cr, d_r):
    # Put all readings into a list.
    all_readings = [d_l, d_cl, d_c, d_cr, d_r]
    
    # Use a list comprehension to create a new list containing only valid readings (> 0).
    # This is a more concise and efficient way to write the filter.
    valid_readings = [d for d in all_readings if d > 0]

    # If there are no valid readings, return a large number.
    if not valid_readings:
        return 999
    
    # If there are valid readings, return the smallest one.
    return min(valid_readings)


try:
    # Initialize the robot's hardware.
    alvik.begin()
    
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

        # 2. Use the helper function to find the single closest distance.
        # STUDENTS: You don't need to worry about HOW this function works,
        # just that it gives you the number you need!
        closest_distance = get_closest_distance(raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r)

        # 3. SET THE LED COLOR (This is the student's main task)
        # This series of if/elif/else checks from closest to farthest.
        # We now call set_color with the three numbers for (Red, Green, Blue).
        if closest_distance < THRESHOLD_RED:
            alvik.left_led.set_color(1, 0, 0)  # Red
            alvik.right_led.set_color(1, 0, 0) # Red
        elif closest_distance < THRESHOLD_YELLOW:
            alvik.left_led.set_color(1, 0, 1)  # Purple
            alvik.right_led.set_color(1, 0, 1)  # Purple
        elif closest_distance < THRESHOLD_BLUE:
            alvik.left_led.set_color(0, 0, 1)  # Blue
            alvik.right_led.set_color(0, 0, 1)  # Blue
        else:
            # If no valid object is close enough, turn the LEDs Green.
            alvik.left_led.set_color(0, 1, 0)   # Green
            alvik.right_led.set_color(0, 1, 0)   # Green

        # A small delay is important in a loop.
        time.sleep_ms(50)

finally:
    # This code runs when the program is stopped.
    print("\nProgram stopped. Turning off LEDs.")
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()

