# V03
# This code written with the help of Gemini Pro
from arduino_alvik import ArduinoAlvik
from time import sleep_ms, ticks_ms, ticks_diff
import math

# --- CONFIGURATION ---
# Adjust this value! 
# 1.0 is normal gravity. 
# 2.7 means the robot experienced 2.7x gravity.
EGG_BREAK_THRESHOLD = 2.7 

# Threshold to detect that a drop has finished/impact occurred
IMPACT_TRIGGER = 2.0

class EggDropBot:
    def __init__(self):
        self.alvik = ArduinoAlvik()
        self.alvik.begin()
        # Wait a moment for sensors to stabilize
        sleep_ms(1000)
        print("Egg Drop Bot Ready.")

    def get_g_force(self):
        """Reads accelerometer and calculates total G-force magnitude."""
        # get_accelerations returns (x, y, z) usually in Gs or mg.
        # If values are large (e.g. 1000), divide by 1000 to get Gs.
        ax, ay, az = self.alvik.get_accelerations()
        
        # Calculate magnitude using Pythagorean theorem
        magnitude = math.sqrt(ax**2 + ay**2 + az**2)
        return magnitude

    def set_color(self, r, g, b):
        """Helper to set both LEDs using 0 or 1."""
        self.alvik.left_led.set_color(r, g, b)
        self.alvik.right_led.set_color(r, g, b)

    def wait_for_drop(self):
        """State 1: Blinking Blue, waiting for impact."""
        print("Ready for drop...")
        last_blink = 0
        led_on = False
        
        while True:
            # 1. Non-blocking Blink Logic
            now = ticks_ms()
            if ticks_diff(now, last_blink) > 500: # Blink every 500ms
                if led_on:
                    self.set_color(0, 0, 0) # Off
                else:
                    self.set_color(0, 0, 1) # Blue
                led_on = not led_on
                last_blink = now

            # 2. Monitor G-Force
            current_g = self.get_g_force()
            
            # If we detect a spike greater than our trigger, impact has started
            if current_g > IMPACT_TRIGGER:
                return self.measure_impact()
            
            # Small delay to prevent CPU hogging, but fast enough to catch drops
            sleep_ms(10)

    def measure_impact(self):
        """State 2: Impact Detected. Measuring peak force."""
        print("Impact detected! Measuring...")
        self.set_color(1, 0, 1) # Purple during calculation
        
        max_g_seen = 0.0
        start_time = ticks_ms()
        
        # Monitor for 500ms to capture the full crash peak
        while ticks_diff(ticks_ms(), start_time) < 500:
            current_g = self.get_g_force()
            if current_g > max_g_seen:
                max_g_seen = current_g
            sleep_ms(5)
            
        return max_g_seen

    def show_result(self, peak_g):
        """State 3 & 4: Display Red/Green and wait for reset."""
        print(f"Impact Result: {peak_g:.2f} G")
        
        survived = peak_g < EGG_BREAK_THRESHOLD
        
        while True:
            # Blink Result
            if survived:
                self.set_color(0, 1, 0) # Green
            else:
                self.set_color(1, 0, 0) # Red
            
            sleep_ms(300)
            self.set_color(0, 0, 0)
            sleep_ms(300)

            # Check for Reset Button (Button OK/A)
            # Use get_touch_ok() or similar depending on library version
            if self.alvik.get_touch_ok(): 
                print("Resetting...")
                # Debounce: wait for button release
                while self.alvik.get_touch_ok():
                    sleep_ms(50)
                break

    def run(self):
        while True:
            peak_force = self.wait_for_drop()
            self.show_result(peak_force)

# Main Execution
bot = None
try:
    bot = EggDropBot()
    bot.run()
except KeyboardInterrupt:
    print("Program stopped by user.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Ensure LEDs are off and motors stopped if program exits
    if bot is not None:
        bot.alvik.left_led.set_color(0, 0, 0)
        bot.alvik.right_led.set_color(0, 0, 0)
        bot.alvik.stop()
    print("Cleaned up.")
    