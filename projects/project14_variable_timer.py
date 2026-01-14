# Project 14: The Variable Blinker
#
# GOAL:
# Make the NanoLED blink without stopping the code (Non-blocking).
# Pressing UP speeds up the blink, and pressing DOWN slows it down.

from arduino_alvik import ArduinoAlvik
import time


from nhs_robotics import NanoLED
# ---------------------------------------------------------------------
# PART 1: THE BUTTON CLASS (Provided for you from Project 13)
# ---------------------------------------------------------------------

class Button:
    """
    A class to manage a button's state and detect a single "press" 
    (a "rising edge") to prevent rapid repeats from holding it down.
    """
    STATE_UP = 1
    STATE_PRESSED = 2
    
    def __init__(self, get_touch_function):
        self.get_touch_function = get_touch_function
        self.current_state = self.STATE_UP

    def get_touch(self):
        return_value = False
        is_pressed = self.get_touch_function()

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



print("Starting Project 14: Variable Blinker...")

alvik = ArduinoAlvik()
alvik.begin()

# --- Setup ---

# 1. Create Button objects
# WORK: Initialize the UP and DOWN buttons using alvik.get_touch_up and alvik.get_touch_down
# Hint: pass the function name inside the parenthesis like with cancel_button
up_button = Button(# WORK)
down_button = Button(# WORK)
cancel_button = Button(alvik.get_touch_cancel)

# 2. Create NanoLED object
# WORK: Initialize the NanoLED()
nano_led = NanoLED()
nano_led.set_brightness(50) 
led_is_on = False 

# 3. Create Timer variables
# WORK: Set the starting interval to 1000 milliseconds (1 second)
blink_interval = # WORK

# WORK: Initialize the timer by getting the current time in ms
# Hint: Use time.ticks_ms
last_blink_time = time.# WORK()

# --- A+ FLEX GOAL SETTINGS ---
FASTEST_INTERVAL = 100   
SLOWEST_INTERVAL = 2000  

def turn_on_LED_dynamic():
    """
    Calculates the color based on speed.
    Fast = Blue, Slow = Red.
    """
    global blink_interval, nano_led
    
    # Math to mix the colors based on speed (Provided for you)
    red_val = int(blink_interval / SLOWEST_INTERVAL * 255)
    blue_val = int((SLOWEST_INTERVAL-blink_interval)/SLOWEST_INTERVAL*255)  
    
    # WORK: Set the NanoLED color using red_val for red, 0 for green, and blue_val for blue
    # Hint: set_rgb(r, g, b)
    nano_led.set_rgb(# WORK, 0, # WORK)      
    
try:
    # Loop until the Cancel (X) button is pressed
    while not cancel_button.get_touch():
        
        # --- TASK 1: CHECK FOR BUTTONS ---
        
        if up_button.get_touch():
            print("Speeding up!")
            # WORK: Multiply blink_interval by 0.7 to make it faster
            blink_interval = blink_interval * # WORK

            # Keep it from going too fast (clamping)
            if blink_interval < FASTEST_INTERVAL:                  
                blink_interval = FASTEST_INTERVAL
            
            # Turn on the LED immediately so we see the new color
            turn_on_LED_dynamic()

        if down_button.get_touch():
            print("Slowing down...")
            # WORK: Multiply blink_interval by 1.3 to make it slower
            blink_interval = blink_interval * # WORK
            
            # Keep it from going too slow
            if blink_interval > SLOWEST_INTERVAL:
                blink_interval = SLOWEST_INTERVAL

            turn_on_LED_dynamic()
            

        # --- TASK 2: CHECK THE TIMER ---
        
        # WORK: Get the current time in ms
        # Hint: Use ticks_ms
        now = time.# WORK()
        
        # Check if enough time has passed
        # WORK: Check if time.ticks_diff(now, last_blink_time) is greater than or equal to blink_interval
        if time.ticks_diff(now, last_blink_time) >= # WORK:
            
            # Toggle the LED
            if led_is_on:
                # WORK: Turn the nano_led off
                nano_led.# WORK()
                led_is_on = False
            else:
                # WORK: Turn the nano_led on using our dynamic function
                turn_on_LED_dynamic()
                led_is_on = True
                
            # WORK: Reset the timer by setting last_blink_time equal to now
            last_blink_time = # WORK
        
        
        # --- Yield ---
        time.sleep(0.01) 

except Exception as e:
    print(f"An error occurred: {e}")
    
finally:
    print("Stopping program.")
    nano_led.off()
    alvik.stop()
