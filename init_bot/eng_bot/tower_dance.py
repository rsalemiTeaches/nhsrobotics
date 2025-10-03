# Alvik Tower Dance Code - Stress Test Version (Distance-Based)
# This program makes the Alvik robot perform a series of random
# forward, backward, and turning motions for a fixed duration to test
# the stability of the student-built tower. This version uses the
# official distance and rotation functions from the library.

# Import necessary libraries
from arduino_alvik import ArduinoAlvik
import time
import random

# --- Constants ---
# The total duration of the test dance in seconds.
TEST_DURATION = 30

# --- Main Program ---
try:
    # Initialize the Alvik robot.
    alvik = ArduinoAlvik()
    # ** Wake up the robot's hardware. **
    alvik.begin()

    # --- Wait for Start Signal ---
    print("Ready to dance... Press OK (checkmark) to start.")
    # Loop indefinitely, blinking the LEDs, until the OK button is pressed.
    while not alvik.get_touch_ok():
        alvik.left_led.set_color(0, 1, 0)  # Green
        alvik.right_led.set_color(0, 1, 0) # Green
        time.sleep(0.25)
        alvik.left_led.set_color(0, 0, 0)  # Off
        alvik.right_led.set_color(0, 0, 0) # Off
        time.sleep(0.25)

        # Allow user to cancel the program while waiting
        if alvik.get_touch_cancel():
            raise KeyboardInterrupt("Program cancelled by user before dance started.")

    # --- Start the Timed Dance ---
    # Get the start time of the test.
    start_time = time.time()

    print(f"Starting {TEST_DURATION} second tower dance...")

    # The main loop. It runs as long as the elapsed time is less than the total test duration
    # AND the user has not pressed the 'X' (cancel) button.
    while (time.time() - start_time) < TEST_DURATION and not alvik.get_touch_cancel():

        # Set LEDs to blue to indicate the test is running.
        alvik.left_led.set_color(0, 0, 1)  # Blue
        alvik.right_led.set_color(0, 0, 1) # Blue

        # --- 1. Forward/Backward Movement ---

        # Choose a random distance between 3 and 9 centimeters.
        move_distance_cm = random.uniform(3, 9)
        
        # Choose a random direction (1 for forward, -1 for backward).
        move_direction = random.choice([1, -1])

        # Move the specified distance. The function defaults to 'cm'.
        alvik.move(move_distance_cm * move_direction)
        time.sleep(0.2) # A brief pause

        # --- 2. Return to Start ---

        # Move in the opposite direction for the SAME distance to return to the center.
        alvik.move(-move_distance_cm * move_direction)
        time.sleep(0.2) # A brief pause

        # --- 3. Turning Movement ---
        
        # Choose a random angle to turn in degrees.
        turn_angle = random.randint(45, 120)

        # Choose a random turn direction (1 for right, -1 for left).
        turn_direction = random.choice([1, -1])

        # Execute the turn for the specified angle. 
        # The speed argument is removed as it caused the error.
        alvik.rotate(turn_angle * turn_direction)
        time.sleep(0.2) # A brief pause before the next cycle

    # After the loop, check why it ended.
    if alvik.get_touch_cancel():
        print("Emergency stop button pressed.")
    else:
        print("Dance complete.")

finally:
    # This 'finally' block is MANDATORY for all Alvik programs.
    # It ensures that no matter what happens, the motors will be safely turned off.
    alvik.stop()
    # Turn off the LEDs.
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    print("Program stopped safely.")

