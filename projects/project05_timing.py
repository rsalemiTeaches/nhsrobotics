# Project 05: The Variable Blinker (Student Version)
# Version: V09
#
# OBJECTIVE:
# Run a timer to blink an LED *while* listening for button presses.
#
# CONCEPTS (See Project 05 Document):
# 1. Non-Blocking Timer: Using time.ticks_ms() and time.ticks_diff() 
#    instead of time.sleep().
# 2. Functions: Defining code blocks we can reuse.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# --- CONSTANTS ---
FASTEST_INTERVAL = 100   # 100ms
SLOWEST_INTERVAL = 2000  # 2 seconds
INTERVAL_STEP = 100      # Change amount per press

# --- HELPER FUNCTION: Map Value ---
# We provide this helper to make the math easier.
# It converts a value from one range to another.
def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# --- INITIALIZATION ---
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

# Note: sb.nano_led is automatically created for you by SuperBot!

# --- STATE VARIABLES ---
blink_interval = 1000       # Start at 1 second
led_is_on = False           # Track if LED is on or off

# --- TIMER SETUP ---
# As discussed in the "New Tools" section of the Project 05 document,
# we need a variable to store the "start time" of the current cycle.
last_blink_time = time.ticks_ms()

print("Program Started. Use UP/DOWN to change speed. Press X to exit.")

# --- DEFINING FUNCTIONS ---
# We define functions so we can "call" them later.
# This prevents us from writing the same color-math code in two different places.
#
# The variable 'interval' inside the parentheses is an ARGUMENT.
# When we call this function later, we must pass it a number.
def turn_on_led(interval):
    """
    Calculates the color based on speed and turns on the LED.
    """
    # WORK 1: Calculate the Red and Blue values
    # Use the map_value() function to convert 'interval' to a 0-255 range.
    # See the "Flex for the A+" section in the document.
    #
    # red_val = map_value(interval, FASTEST_INTERVAL, SLOWEST_INTERVAL, 0, 255)
    # blue_val = ... (You calculate this one: Fast = Blue!)
    
    # WORK 2: Turn on the LED
    # Use sb.nano_led.set_rgb() with your calculated values.
    # Reminder: set_rgb() takes (red, green, blue).
    pass # Remove this 'pass' when you add your code

# --- MAIN LOOP ---
try:
    while not sb.alvik.get_touch_ok():
        
        # ==========================================================
        # TASK 1: CHECK INPUTS
        # ==========================================================
        # Use sb.get_pressed_up() and sb.get_pressed_down() to change
        # the 'blink_interval' variable.
        
        # WORK 3: Handle the UP Button (Faster)
        # if sb.get_pressed_up():
        #     1. Subtract INTERVAL_STEP from blink_interval
        #     2. Use an 'if' statement to make sure it doesn't go below FASTEST_INTERVAL
        #     3. Print the new interval
        #     4. Call turn_on_led(blink_interval) to update the color immediately
        
        # WORK 4: Handle the DOWN Button (Slower)
        # (Write the code for the Down button here. It should ADD to the interval.)

        # ==========================================================
        # TASK 2: THE NON-BLOCKING TIMER
        # ==========================================================
        # This corresponds to the "Blink Without Delay" pattern in the document.
        
        # 1. Get current time
        now = time.ticks_ms()
        
        # WORK 5: Check if enough time has passed
        # usage: time.ticks_diff(time_a, time_b)
        #
        # Here is the logic structure you need to write:
        #
        # if time.ticks_diff(now, last_blink_time) >= blink_interval:
        #
        #     if led_is_on:
        #         # If the LED is currently ON, turn it OFF.
        #         # 1. Turn hardware off: sb.nano_led.off()
        #         # 2. Update state variable: led_is_on = False
        #     else:
        #         # If the LED is currently OFF, turn it ON.
        #         # 1. Turn hardware on: turn_on_led(blink_interval)
        #         # 2. Update state variable: led_is_on = True
        #
        #     # IMPORTANT: Reset the timer for the next lap!
        #     last_blink_time = now

        # ==========================================================
        # YIELD
        # ==========================================================
        # Short sleep to let the robot breathe. 
        # Since it's only 10ms, it won't block the buttons noticeably.
        time.sleep(0.01)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    print("Stopping program.")
    sb.nano_led.off()
    sb.alvik.stop()