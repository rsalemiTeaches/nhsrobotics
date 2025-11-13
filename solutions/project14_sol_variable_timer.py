# Project 14: The Variable Blinker
#
# This project combines two major concepts:
# 1. The Button Class (from Project 13) to get clean button presses.
# 2. A Non-Blocking Timer (using ticks_ms) to do two things at once.
#
# GOAL:
# Make the NanoLED blink. Pressing UP speeds up the blink,
# and pressing DOWN slows it down.
#
# A+ FLEX GOAL:
# Change the LED color from Red (slow) to Blue (fast) and
# print the new interval.

from arduino_alvik import ArduinoAlvik
import time

# NEW: Import the NanoLED controller from our helper library
from nhs_robotics import NanoLED

# ---------------------------------------------------------------------
# PART 1: THE BUTTON CLASS (Copied from Project 13)
# ---------------------------------------------------------------------

class Button:
    """
    A class to manage a button's state and detect a single "press" 
    (a "rising edge") to prevent rapid repeats from holding it down.
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
        self.get_touch_function = get_touch_function
        self.current_state = self.STATE_UP

    def get_touch(self):
        """
        Checks the button state. This MUST be called in every loop.
        
        It updates the internal state machine and returns True ONLY 
        on the "rising edge" — the single moment the button was 
        first pressed.
        """
        return_value = False
        is_pressed = self.get_touch_function()

        # --- State Machine logic ---
        if self.current_state == self.STATE_UP:
            if is_pressed:
                return_value = True
                self.current_state = self.STATE_PRESSED
        
        elif self.current_state == self.STATE_PRESSED:
            if not is_pressed:
                self.current_state = self.STATE_UP
                
        return return_value


# ---------------------------------------------------------------------
# PART 2: THE VARIABLE BLINKER PROGRAM
# ---------------------------------------------------------------------

if __name__ == "__main__":

    print("Starting Project 14: Variable Blinker (A+ Flex)...")
    print("Press UP to speed up, DOWN to slow down.")
    print("Press X to exit.")

    alvik = ArduinoAlvik()
    alvik.begin()
    
    # --- Setup ---
    # 1. Create Button objects
    up_button = Button(alvik.get_touch_up)
    down_button = Button(alvik.get_touch_down)
    cancel_button = Button(alvik.get_touch_cancel)
    
    # 2. Create NanoLED object
    nano_led = NanoLED()
    nano_led.set_brightness(50) # Use 50% brightness
    led_is_on = False # Track the LED's state
    
    # 3. Create Timer variables
    blink_interval = 1000  # Start at 1000ms (1 second)
    
    # This is the key: get the "start time"
    last_blink_time = time.ticks_ms()
    
    # --- NEW FOR FLEX: Color Mapping Ranges ---
    FASTEST_INTERVAL = 100   # 100ms will be pure BLUE
    SLOWEST_INTERVAL = 2000  # 2000ms will be pure RED
  
    def turn_on_LED():
      global FASTEST_INTERVAL, SLOWEST_INTERVAL, blink_interval, nano_led
      # Map Red from 0 (fast) to 255 (slow)
      red_val = int(blink_interval / SLOWEST_INTERVAL * 255)
      # Map Blue from 255 (fast) to 0 (slow)
      blue_val = int((SLOWEST_INTERVAL-blink_interval)/SLOWEST_INTERVAL*255)  
      nano_led.set_rgb(red_val, 0, blue_val)      
      
    try:
        while not cancel_button.get_touch():
            
            # --- TASK 1: CHECK FOR BUTTONS (Runs every loop) ---
            # We can check for input *without* stopping our timer!
            
            if up_button.get_touch():
                # Speed up by 30%
                blink_interval = blink_interval * 0.7

                if blink_interval < FASTEST_INTERVAL:                  
                  blink_interval = FASTEST_INTERVAL
                  
                # FLEX: Print the new interval
                print(f"New interval: {blink_interval} ms")
                turn_on_LED()
            if down_button.get_touch():
                # Slow down by 30%
                blink_interval = blink_interval * 1.3
              
                if blink_interval > SLOWEST_INTERVAL:
                  blink_interval = SLOWEST_INTERVAL

                # FLEX: Print the new interval
                print(f"New interval: {blink_interval} ms")
                turn_on_LED()
              

            # --- TASK 2: CHECK THE TIMER (Runs every loop) ---
            # Get the current "odometer" reading
            now = time.ticks_ms()
            
            # Check the "trip meter": has enough time passed?
            if time.ticks_diff(now, last_blink_time) >= blink_interval:
                
                # --- An Event! Time to toggle the LED ---
                
                if led_is_on:
                    # Turn it off
                    # Use set_rgb(0,0,0) as per the new function
                    nano_led.off()
                    led_is_on = False
                else:
                    # Turn it on (Dynamic Color)
                    # Use set_rgb() as requested
                    turn_on_LED()
                    led_is_on = True
                    
                # Reset the "lap" timer for the *next* blink
                last_blink_time = now
            
            
            # --- Yield ---
            # We must *always* sleep for a tiny bit to let
            # background tasks run.
            time.sleep(0.01) # Sleep for 10ms

    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Cleanup code
        print("Stopping program.")
        nano_led.off()
        alvik.stop()