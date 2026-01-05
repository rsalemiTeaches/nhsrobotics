# Project 13: Building a Button Class (Student Version)
#
# OBJECTIVE:
# In Project 12, you USED a class (Pet).
# In Project 13, you will BUILD a class (Button).
#
# This class solves a specific robot problem: "Bouncing."
# We want to detect a single "click" even if the button is held down.
#
# Created with the help of Gemini Pro - V02

from arduino_alvik import ArduinoAlvik
import time
from nhs_robotics import NanoLED 

# ---------------------------------------------------------------------
# PART 1: THE BUTTON CLASS (THE BLUEPRINT)
# ---------------------------------------------------------------------

class Button:
    """
    A class to manage a button's state and detect a single "press" 
    (a "rising edge").
    """
    # 1. CLASS CONSTANTS
    # We use these names instead of numbers (1 or 2) to make code readable.
    STATE_UP = 1
    STATE_PRESSED = 2
    
    def __init__(self, get_touch_function):
        """
        The Constructor: Sets up the button when we create it.
        
        Arguments:
        get_touch_function -- The Alvik function (like alvik.get_touch_ok) 
                              that this button will use to check hardware.
        """
        # --- TODO: WORK SECTION 1 ---
        # We need to save the 'get_touch_function' into a "self" variable
        # so we can use it later in other methods.
        self.get_hardware_state = get_touch_function
        
        # Set the initial state of the button to STATE_UP (not pressed)
        # HINT: Look at the constants above!
        self.current_state = None # <--- REPLACE 'None' WITH YOUR CODE

    def get_touch(self):
        """
        Checks the button state. 
        Returns True ONLY the very first moment the button is pressed.
        """
        return_value = False
        
        # --- TODO: WORK SECTION 2 ---
        # 1. Ask the hardware if it is currently being touched.
        # Call the function we saved in __init__ (self.get_hardware_state)
        # Store the result in a variable called 'is_pressed'
        
        # <--- WRITE CODE HERE
        

        # --- TODO: WORK SECTION 3 (The Logic) ---
        # We need to check our "State Machine".
        # Translate these English sentences into Python 'if' statements.
        
        # SCENARIO A: The button was UP, but now it is pressed.
        # IF self.current_state is equal to self.STATE_UP:
            # IF is_pressed is True:
                # We found a new press!
                # 1. Set return_value to True
                # 2. Change self.current_state to self.STATE_PRESSED
        
        
        
        # SCENARIO B: The button was PRESSED, but now let go.
        # ELIF self.current_state is equal to self.STATE_PRESSED:
            # IF is_pressed is False:
                # The button was released.
                # 1. Change self.current_state back to self.STATE_UP
                
        
        
        
        # Return the result (True only on the exact frame of the press)
        return return_value


# ---------------------------------------------------------------------
# PART 2: THE MAIN PROGRAM (The LED Swapper)
# ---------------------------------------------------------------------

print("Starting Project 13: Button Class...")

# 1. Setup Robot
alvik = ArduinoAlvik()
alvik.begin()

# --- TODO: WORK SECTION 4 (Create Objects) ---
# Create two Button objects. 
# NOTE: Pass the function NAME (e.g., alvik.get_touch_ok), 
# do NOT put () after it! We are passing the tool, not the result.

center_button = Button(alvik.get_touch_ok) 
# Create the cancel_button below using 'alvik.get_touch_cancel'
cancel_button = None # <--- REPLACE 'None' WITH YOUR CODE

# 2. Setup Variables
left_led_is_red = True
alvik.left_led.set_color(1, 0, 0)  # Start Red
alvik.right_led.set_color(0, 1, 0) # Start Green

try:
    # Loop until the Cancel button is pressed
    # Notice how we use our new object method: .get_touch()
    while not cancel_button.get_touch():
        
        # --- TODO: WORK SECTION 5 (Use Objects) ---
        # Check if the center_button has been touched.
        # IF center_button.get_touch() is True:
        #    Toggle the 'left_led_is_red' variable ( use: var = not var )
        #    Print "Swap!" to the console
        
        # <--- WRITE CODE HERE
        
        
        # --- Update LEDs based on the variable (Done for you) ---
        if left_led_is_red:
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(0, 1, 0)
        else:
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(1, 0, 0)

        # Tiny sleep to let the robot think
        time.sleep(0.01)

except Exception as e:
    print(f"Error: {e}")
    
finally:
    alvik.left_led.off()
    alvik.right_led.off()
    alvik.stop()
    