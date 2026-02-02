#########################
#       Project 04      #
#     Obstacle Stop     #
#########################

# In this project, we will combine movement and sensors
# to make the Alvik more intelligent. The robot will
# drive forward on its own until it detects an object
# in its path, at which point it will stop.

# We will also use the LEDs as status indicators:
# - GREEN means the robot is driving.
# - RED means the robot has stopped for an obstacle.

# As always, we import the resources we need.
from arduino_alvik import ArduinoAlvik
from time import sleep_ms

# We'll use the same helper function from the last project
# to easily find the closest object.
from nhs_robotics import get_closest_distance

# Create our Alvik robot controller.
alvik = ArduinoAlvik()

# --- Configuration ---
# It's good practice to store settings in variables at the top.
# This makes them easy to change later without hunting through the code.
DRIVE_SPEED = 30     # The speed in RPM when the robot is moving.
STOP_DISTANCE = 10   # The distance (in cm) at which the robot should stop.

try:
    alvik.begin()  # Initialize the robot

    print("Project 04: Obstacle Stop Started.")
    print(f"I will drive forward and stop within {STOP_DISTANCE} cm of an object.")
    print("Press the Cancel (X) button to stop the program.")

    # This is the main loop that will run continuously.
    while True:
        # Always check for the cancel button first.
        if alvik.get_touch_cancel():
            print("Cancel button pressed. Stopping.")
            break

        # Get the distance reading from the front sensor.
        raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r = alvik.get_distance()
        
        # WORK: Use the get_closest_distance() function to find the single
        # WORK: closest distance. Store the result in a variable called `closest_distance`.
        closest_distance = 0 # Replace 0 with your function call

        # WORK: Write an if/else statement that checks if `closest_distance`
        # WORK: is less than `STOP_DISTANCE`.
        if False: # WORK: Replace `False` with your condition.
            # --- Stop the robot ---
            # WORK: Set wheel speeds to 0 to stop the robot.
            
            # WORK: Set both LEDs to RED to indicate it is stopped.

            pass # You can remove this 'pass' line when you add your code.
        else:
            # --- Drive the robot ---
            # WORK: Set both wheel speeds to DRIVE_SPEED to move forward.

            # WORK: Set both LEDs to GREEN to indicate it is driving.

            pass # You can remove this 'pass' line when you add your code.


        # A small delay in the loop is important for stability.
        sleep_ms(50)

finally:
    # This code always runs when the program ends.
    # WORK: It's our safety net. Make sure the robot stops
    # WORK: by calling the correct function.
    print("Program finished. Stopping robot.")
    

