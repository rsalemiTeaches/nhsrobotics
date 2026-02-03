# Project 11: The Button Problem
#
# GOAL:
# Write a program that swaps the colors of the left and
# right LEDs every time you press the CENTER button.
#
# CHALLENGE:
# Run this code and try to press the center button.
# Can you make the LEDs swap just ONCE?
#
# You will see them flicker uncontrollably!
#
# WHY?
# The 'while' loop runs thousands of times per second.
# Your finger holds the button for (maybe) half a second.
#
# This means the code inside the 'if' statement:
#   if alvik.get_touch_center():
#
# ...runs hundreds or thousands of times, causing the
# LEDs to swap back and forth in a "strobe" effect.
#
# We don't want to detect the button *being held*.
# We want to detect the *single moment* it is *first pressed*.
#
# How can we solve this?

from arduino_alvik import ArduinoAlvik, sleep_ms


print("Starting Project 11: The Button Problem...")
print("Press the CENTER button to swap LED colors.")
print("...or try to, anyway!")
print("Press X to exit.")

alvik = ArduinoAlvik()
alvik.begin()

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
    while not alvik.get_touch_cancel():
        
        if alvik.get_touch_center():
            print("Swap!") # This will print hundreds of times!
            
            # Toggle the state variable
            left_led_is_red = not left_led_is_red

            if left_led_is_red:
                alvik.left_led.set_color(1, 0, 0)  # Left Red
                alvik.right_led.set_color(0, 1, 0) # Right Green
            else:
                alvik.left_led.set_color(0, 1, 0) # Left Green
                alvik.right_led.set_color(1, 0, 0)  # Right Red

        sleep_ms(10) # Sleep for 10ms to avoid busy-waiting

except Exception as e:
    print(f"An error occurred: {e}")
    
finally:
    # Cleanup code
    print("Stopping program.")
    # Turn off the main Alvik LEDs
    alvik.left_led.set_color(0,0,0)
    alvik.right_led.set_color(0,0,0)
    alvik.stop()
