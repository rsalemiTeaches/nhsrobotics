# Alvik Tower Dance Code
# This program makes the Alvik robot move randomly on a platform
# without falling off, to test the stability of a student-built tower.

# Import necessary libraries
from arduino_alvik import Alvik
import time
import random

# --- Constants ---
# The distance (in mm) from the ToF sensor that we consider a "cliff" or edge.
# If the sensor reading is GREATER than this, we've found an edge.
CLIFF_THRESHOLD = 150

# The speed for forward and turning movements (0-100).
# A lower speed is safer for this project.
MOVE_SPEED = 30
TURN_SPEED = 40

# --- Main Program ---
try:
    # Initialize the Alvik robot. This is always the first step.
    alvik = Alvik()

    # The main loop. It will continue running until the user presses
    # the 'X' (cancel) button on the Alvik.
    while not alvik.get_touch_cancel():

        # --- Forward Movement Phase ---
        # Set LEDs to green to show we are safely moving forward.
        alvik.left_led.set_color(0, 1, 0)  # Green
        alvik.right_led.set_color(0, 1, 0) # Green

        # Start moving forward.
        alvik.set_motors(MOVE_SPEED, MOVE_SPEED)

        # Keep checking the distance sensor. As long as the distance is LESS
        # than our threshold, it means the robot sees the platform and is safe.
        while alvik.get_distance() < CLIFF_THRESHOLD:
            # A small delay to prevent the loop from running too fast.
            time.sleep(0.01)
            # If the user presses X during this inner loop, break out.
            if alvik.get_touch_cancel():
                break
        
        # If the loop above breaks, it means a cliff has been detected!
        # Now, execute the avoidance maneuver.

        # --- Avoidance Maneuver Phase ---
        # Immediately stop the motors.
        alvik.stop()

        # Set LEDs to red to indicate an edge was detected.
        alvik.left_led.set_color(1, 0, 0)  # Red
        alvik.right_led.set_color(1, 0, 0) # Red
        time.sleep(0.2) # A brief pause

        # Back up for a short, fixed duration to get away from the edge.
        alvik.set_motors(-MOVE_SPEED, -MOVE_SPEED)
        time.sleep(0.5)
        alvik.stop()
        time.sleep(0.2)

        # Choose a random direction to turn (1 for right, -1 for left).
        turn_direction = random.choice([-1, 1])

        # Choose a random duration for the turn to make it unpredictable.
        turn_duration = random.uniform(0.4, 0.8) # Turn for 0.4 to 0.8 seconds

        # Execute the turn.
        alvik.set_motors(TURN_SPEED * turn_direction, -TURN_SPEED * turn_direction)
        time.sleep(turn_duration)
        alvik.stop()
        time.sleep(0.2)

finally:
    # This 'finally' block is MANDATORY for all Alvik programs.
    # It ensures that no matter what happens (even an error or the user
    # pressing 'X'), the motors will be safely turned off.
    alvik.stop()
    # Turn off the LEDs as well.
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    print("Program stopped safely.")

