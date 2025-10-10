# Alvik Tower Dance Code - Stress Test Version (Distance-Based)
# This program makes the Alvik robot perform a series of random
# forward, backward, and turning motions for a fixed duration to test
# the stability of the student-built tower.
# This version includes a visual timer using the onboard Nano RGB LED.

# Import necessary libraries
from arduino_alvik import ArduinoAlvik
from nanolib import NanoLED  # Import the NanoLED library
import time
import random

# --- Constants ---
# The total duration of the test dance in seconds.
TEST_DURATION = 30
# How many seconds at the end should the LED blink.
BLINK_DURATION = 5

# --- Main Program ---
try:
    # Initialize the Alvik robot and the Nano LED.
    alvik = ArduinoAlvik()
    nano_led = NanoLED()
    
    # ** Wake up the robot's hardware. **
    alvik.begin()
    # Set a default brightness for the Nano LED.
    nano_led.set_brightness(60)

    # --- Wait for Start Signal ---
    print("Ready to dance... Press OK (checkmark) to start.")
    # Loop indefinitely, blinking the Alvik LEDs, until the OK button is pressed.
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
        
        # --- Visual Timer Logic ---
        elapsed_time = time.time() - start_time
        
        # Check if we are in the final countdown phase.
        if elapsed_time > (TEST_DURATION - BLINK_DURATION):
            # For the final 5 seconds, set the Alvik LEDs to solid blue.
            alvik.left_led.set_color(0, 0, 1)
            alvik.right_led.set_color(0, 0, 1)
        else:
            # Normal color fade logic for the main part of the timer.
            # This will now only apply to the first 25 seconds.
            progress = elapsed_time / (TEST_DURATION - BLINK_DURATION)
            
            r, g, b = 0, 0, 0
            
            # First half of the countdown (Red to Green)
            if progress < 0.5:
                half_progress = progress * 2
                r = 255 * (1 - half_progress)
                g = 255 * half_progress
                b = 0
            # Second half of the countdown (Green to Blue)
            else:
                half_progress = (progress - 0.5) * 2
                r = 0
                g = 255 * (1 - half_progress)
                b = 255 * half_progress
                
            # Update the Nano LED color
            nano_led.set_rgb(r, g, b)

        # --- 1. Forward/Backward Movement ---
        move_distance_cm = random.uniform(3, 6)
        move_direction = random.choice([1, -1])
        alvik.move(move_distance_cm * move_direction)
        time.sleep(0.2)

        # --- 2. Return to Start ---
        alvik.move(-move_distance_cm * move_direction)
        time.sleep(0.2)

        # --- 3. Turning Movement ---
        turn_angle = random.randint(45, 120)
        turn_direction = random.choice([1, -1])
        alvik.rotate(turn_angle * turn_direction)
        time.sleep(0.2)

    # After the loop, check why it ended.
    if alvik.get_touch_cancel():
        print("Emergency stop button pressed.")
    else:
        print("Dance complete.")

finally:
    # This 'finally' block ensures all hardware is safely shut down.
    alvik.stop()
    nano_led.off()  # Turn off the Nano LED
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    print("Program stopped safely.")

