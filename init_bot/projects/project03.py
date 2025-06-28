# Project 03: Proximity Color Indicator
# This program finds the single closest object to the robot and changes
# the color of BOTH LEDs based on how near it is. This is a great way to
# visualize distance.

# WORK  Import the ArduinoAvlik class and the sleep_ms() function

# Create a robot object and store it in 
# a variable named alvik


# --- Configuration ---
# We will define different distance thresholds for each color.
# Students can change these values to tune the robot's response.
THRESHOLD_RED = 3      # For very close objects
THRESHOLD_PURPLE = 10   # For medium-range objects
THRESHOLD_BLUE = 15    # For far-away objects


# STUDENTS CAN IGNORE THIS FUNCTION
# I wrote it to help with the problem, but you don't
# have to know how it works unless you want to.
#
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
    # WORK Initialize the robot's hardware.
    
    print("Proximity Color Indicator Project Started.")
    print("LEDs will change color based on the closest object.")
    print("Press the Cancel (X) button to stop.")

    # --- Main Loop ---
    while True:
        # WORK Check if the user wants to stop the program.
        # and break out of the loop.


        # 1. Read the raw distance sensor zones.
        raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r = alvik.get_distance()

        # 2. Use the helper function to find the single closest distance.
        # STUDENTS: You don't need to worry about HOW this function works,
        # just that it gives you the number you need!
        closest_distance = get_closest_distance(raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r)

        # 3. SET THE LED COLOR (This is the student's main task)
        # This series of if/elif/else checks from closest to farthest.
        # We now call set_color with the three numbers for (Red, Green, Blue).
        #
        # WORK : Lots of work here
        #
        # IF Closest Distance is < THRESHHOLD_RED set the LEDs to RED
        # ELSE IF the closest distance is < THRESHOLD_PURPLE set LEDS to PURPLE
        # ELSE IF the close distance is < THRESHOLD_BLUE set the LEDS to BLUE
        # ELSE set the LEDS to GREEN



        # A small delay is important in a loop.
        sleep_ms(50)

finally:
    # This code runs when the program is stopped.
    print("\nProgram stopped. Turning off LEDs.")
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()

