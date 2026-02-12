# Project 05: The Variable Blinker (Refactored for SuperBot)
# Version: V04
#
# Changes:
# 1. Imported ArduinoAlvik and instantiated it explicitly.
# 2. Passed alvik instance to SuperBot constructor.
# 3. Removed main() and running at top level.
# 4. turn_on_led accepts explicit interval argument.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# --- CONSTANTS ---
FASTEST_INTERVAL = 100
SLOWEST_INTERVAL = 2000
INTERVAL_STEP = 100

def map_value(x, in_min, in_max, out_min, out_max):
    """
    Standard map function to convert a range (0-100) to another (0-255).
    """
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# --- INITIALIZATION ---
# Create the hardware interface first
alvik = ArduinoAlvik()
alvik.begin()

# Wrap it in our SuperBot class
sb = SuperBot(alvik)

# --- STATE VARIABLES ---
blink_interval = 1000  # Start at 1 second
last_blink_time = time.ticks_ms()
led_is_on = False

print("Program Started. Use UP/DOWN to change speed. Press OK to exit.")

# --- HELPER FUNCTIONS ---
def turn_on_led(interval):
    """
    Sets the LED color based on the provided interval.
    Fast (100ms) = Blue
    Slow (2000ms) = Red
    """
    # Map interval to color values
    red_val = map_value(interval, FASTEST_INTERVAL, SLOWEST_INTERVAL, 0, 255)
    blue_val = map_value(interval, FASTEST_INTERVAL, SLOWEST_INTERVAL, 255, 0)
    
    # Ensure values stay within 0-255 byte range
    red_val = max(0, min(255, red_val))
    blue_val = max(0, min(255, blue_val))
    
    sb.nano_led.set_rgb(red_val, 0, blue_val)

# --- MAIN LOOP ---
try:
    # We access the raw 'ok' button from the underlying alvik object for the kill switch
    while not sb.alvik.get_touch_cancel():
        
        # --- TASK 1: CHECK INPUTS (Debounced by SuperBot) ---
        
        if sb.get_pressed_up():
            # Make it faster (decrease interval)
            blink_interval -= INTERVAL_STEP
            if blink_interval < FASTEST_INTERVAL:
                blink_interval = FASTEST_INTERVAL
            
            print(f"Faster! Interval: {blink_interval} ms")
            
            # A+ Flex: Update immediately for visual feedback
            turn_on_led(blink_interval)
            led_is_on = True
            last_blink_time = time.ticks_ms() # Reset timer to prevent double-blink

        if sb.get_pressed_down():
            # Make it slower (increase interval)
            blink_interval += INTERVAL_STEP
            if blink_interval > SLOWEST_INTERVAL:
                blink_interval = SLOWEST_INTERVAL
            
            print(f"Slower... Interval: {blink_interval} ms")
            
            # A+ Flex: Update immediately
            turn_on_led(blink_interval)
            led_is_on = True
            last_blink_time = time.ticks_ms()

        # --- TASK 2: CHECK THE TIMER (Non-blocking) ---
        
        now = time.ticks_ms()
        
        # Check if the "lap time" matches our target interval
        if time.ticks_diff(now, last_blink_time) >= blink_interval:
            if led_is_on:
                sb.nano_led.off()
                led_is_on = False
            else:
                turn_on_led(blink_interval)
                led_is_on = True
            
            # Reset the "lap" timer
            last_blink_time = now

        # Yield to system
        time.sleep(0.01)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    print("Stopping program.")
    sb.nano_led.off()
    alvik.stop() # Stops threads and resets