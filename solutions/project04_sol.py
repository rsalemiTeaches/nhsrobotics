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
        # This is the same logic as Project 03.
        raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r = alvik.get_distance()
        closest_distance = get_closest_distance(raw_dist_l, raw_dist_cl, raw_dist_c, raw_dist_cr, raw_dist_r)

        # Now, we make a decision based on the distance.
        # Is the closest object nearer than our STOP_DISTANCE?
        if closest_distance < STOP_DISTANCE:
            # --- Stop the robot ---
            # Set wheel speeds to 0.
            alvik.set_wheels_speed(0, 0)
            # Set LEDs to RED to indicate it is stopped.
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
        else:
            # --- Drive the robot ---
            # Set both wheel speeds to drive forward.
            alvik.set_wheels_speed(DRIVE_SPEED, DRIVE_SPEED)
            # Set LEDs to GREEN to indicate it is driving.
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)

        # A small delay in the loop is important for stability.
        sleep_ms(50)

finally:
    # This code always runs when the program ends.
    # It's our safety net to make sure the robot stops.
    print("Program finished. Stopping robot.")
    alvik.stop()

