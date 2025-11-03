# Project 11: Building a Button Class
#
# This file contains the complete lesson for Project 11.
# Part 1: The Button Class to build.
# Part 2: A full example program (LED Swapper)
#         to test the class.

from arduino_alvik import ArduinoAlvik
import time
# We removed NanoLED, as this demo uses the main Alvik LEDs.
# from nhs_robotics import NanoLED 

# ---------------------------------------------------------------------
# PART 1: THE BUTTON CLASS
# ---------------------------------------------------------------------

class Button:
    """
    A class to manage a button's state and detect a single "press" 
    (a "rising edge") to prevent rapid repeats from holding it down.

    This class works like a simple state machine with two states:
    - STATE_UP: The button is not being pressed.
    - STATE_PRESSED: The button is being held down.
    
    It only reports a "press" on the single frame when the button
    goes from STATE_UP to STATE_PRESSED.
    """
    # Class-level constants for our states
    STATE_UP = 1
    STATE_PRESSED = 2
    
    def __init__(self, get_touch_function):
        """
        Initializes the button's internal state.
        
        get_touch_function: A function (like alvik.get_touch_up) that
                            will be called to get the hardware state.
        """
        # Save the function that was passed in, so we can call it later
        self.get_hardware_state = get_touch_function
        
        # Initialize the internal state
        self.current_state = self.STATE_UP

    def get_touch(self):
        """
        Checks the button state. This MUST be called in every loop.
        
        It updates the internal state machine and returns True ONLY 
        on the "rising edge" — the single moment the button was 
        first pressed.
        """
        return_value = False
        
        # Call the hardware function we saved during __init__
        is_pressed = self.get_hardware_state()

        # --- This is the State Machine logic ---
        
        # Check if the current state is UP
        if self.current_state == self.STATE_UP:
            if is_pressed:
                # This is the "rising edge"!
                return_value = True
                # Transition to the PRESSED state
                self.current_state = self.STATE_PRESSED
        
        # Check if the current state is PRESSED
        elif self.current_state == self.STATE_PRESSED:
            if not is_pressed:
                # The button was released.
                # Transition back to the UP state.
                self.current_state = self.STATE_UP
                
        # Return True only if this was the frame it was pressed
        return return_value


# ---------------------------------------------------------------------
# PART 2: EXAMPLE USAGE (The LED Swapper)
# ---------------------------------------------------------------------

# The 'if __name__ == "__main__":' block means this code will
# only run when you press "Run" on this file directly.
# It won't run if another script imports this file.
if __name__ == "__main__":

    print("Starting Project 11: Button Class Demo...")
    print("Press the CENTER button (OK) to swap LED colors.")
    print("Press X to exit.")

    alvik = ArduinoAlvik()
    alvik.begin()
    
    # --- Button Setup ---
    # Create an object for each button we want to track.
    # We pass the *function* itself (not the result) into the
    # constructor.
    center_button = Button(alvik.get_touch_ok)
    cancel_button = Button(alvik.get_touch_cancel)

    # --- LED State Setup ---
    # This variable will track our state.
    # True = Left is Red, Right is Green
    # False = Left is Green, Right is Red
    left_led_is_red = True
    
    # Set the initial LED state
    alvik.left_led.set_color(1, 0, 0)  # Left Red
    alvik.right_led.set_color(0, 1, 0) # Right Green
    
    try:
        # This is the main non-blocking loop
        # We use our new Button object to control the loop!
        while not cancel_button.get_touch():
            
            # --- SENSE / THINK ---
            
            # 1. Check the center button
            # Calling .get_touch() both updates the button's
            # internal state AND returns True if it was pressed.
            if center_button.get_touch():
                print("Swap!")
                # Toggle the state variable
                left_led_is_red = not left_led_is_red

                # --- ACT (Set LEDs) ---
                if left_led_is_red:
                    alvik.left_led.set_color(1, 0, 0)  # Left Red
                    alvik.right_led.set_color(0, 1, 0) # Right Green
                else:
                    alvik.left_led.set_color(0, 1, 0) # Left Green
                    alvik.right_led.set_color(1, 0, 0)  # Right Red

            
            # --- IMPORTANT ---
            # We must yield control to the Alvik's background tasks
            # This tiny sleep is what allows the interrupt system
            # (and other background logic) to run.
            # We use time.sleep(float) NOT sleep_ms(int).
            time.sleep(0.01) # Sleep for 10ms

    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Cleanup code
        print("Stopping program.")
        # Turn off the main Alvik LEDs
        alvik.left_led.off()
        alvik.right_led.off()
        alvik.stop()

