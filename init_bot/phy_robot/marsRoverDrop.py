# V09
# This code written with the help of Gemini Pro
from arduino_alvik import ArduinoAlvik
from nhs_robotics import oLED
from time import sleep_ms, ticks_ms, ticks_diff
import math

# --- CONFIGURATION ---
# Mass of the Alvik Robot (kg)
ROBOT_MASS = 0.20 

# Earth Gravity (m/s^2) - Used for Force Calc
GRAVITY_EARTH = 9.81

# Mars Gravity (m/s^2) - Used for Mars Eq Calc
GRAVITY_MARS = 3.71

# Structural Limit in Gs (Earth Gs)
STRUCTURAL_INTEGRITY_LIMIT = 2.7 

# Calculate the Safety Limit in Newtons (The Target)
# F = m * a -> 0.20 * (2.7 * 9.81)
SAFE_FORCE_NEWTONS = ROBOT_MASS * (STRUCTURAL_INTEGRITY_LIMIT * GRAVITY_EARTH)

# Threshold to detect that the drop has started/touchdown occurred (in Gs)
TOUCHDOWN_TRIGGER = 2.0

class MarsRover:
    def __init__(self):
        self.alvik = ArduinoAlvik()
        self.alvik.begin()
        
        # Initialize OLED
        try:
            self.oled = oLED()
            self.oled_active = True
        except Exception as e:
            print(f"OLED Error: {e}")
            self.oled_active = False

        # Wait a moment for sensors to stabilize
        sleep_ms(1000)
        print("Mars Rover Landing System Ready.")
        self.update_display("SYSTEM READY", "Awaiting Launch")

    def update_display(self, line1, line2, line3=""):
        """Helper to write 3 lines of text to the OLED."""
        if not self.oled_active:
            return
            
        self.oled.display.fill(0)
        self.oled.display.text(line1, 0, 0)
        self.oled.display.text(line2, 0, 10)
        self.oled.display.text(line3, 0, 20)
        self.oled.display.show()

    def draw_skull(self):
        """Draws a pixel-art skull on the right side of the screen."""
        if not self.oled_active:
            return

        # Position for the skull (Right side)
        start_x = 110
        start_y = 5

        # Draw the main skull shape (White block)
        self.oled.display.fill_rect(start_x + 2, start_y, 10, 8, 1)     # Cranium
        self.oled.display.fill_rect(start_x, start_y + 3, 14, 5, 1)     # Wide part
        self.oled.display.fill_rect(start_x + 3, start_y + 8, 8, 5, 1)  # Jaw

        # Carve out the eyes (Black / Clear pixels)
        self.oled.display.fill_rect(start_x + 2, start_y + 3, 3, 3, 0)
        self.oled.display.fill_rect(start_x + 9, start_y + 3, 3, 3, 0)

        # Carve out the nose (Black inverted V)
        self.oled.display.line(start_x + 7, start_y + 7, start_x + 6, start_y + 9, 0)
        self.oled.display.line(start_x + 7, start_y + 7, start_x + 8, start_y + 9, 0)

        # Carve out the teeth (Black vertical lines)
        self.oled.display.line(start_x + 5, start_y + 10, start_x + 5, start_y + 12, 0)
        self.oled.display.line(start_x + 7, start_y + 10, start_x + 7, start_y + 12, 0)
        self.oled.display.line(start_x + 9, start_y + 10, start_x + 9, start_y + 12, 0)

        self.oled.display.show()

    def get_g_force(self):
        """Reads accelerometer and calculates total G-force magnitude."""
        # get_accelerations returns (x, y, z) in Gs
        ax, ay, az = self.alvik.get_accelerations()
        
        # Calculate magnitude using Pythagorean theorem
        magnitude = math.sqrt(ax**2 + ay**2 + az**2)
        return magnitude

    def set_color(self, r, g, b):
        """Helper to set both LEDs using 0 or 1."""
        self.alvik.left_led.set_color(r, g, b)
        self.alvik.right_led.set_color(r, g, b)

    def wait_for_descent(self):
        """State 1: Blinking Blue, waiting for touchdown."""
        print("Awaiting descent...")
        self.update_display("STATUS: ARMED", "Drop when ready")
        
        last_blink = 0
        led_on = False
        
        while True:
            # 1. Non-blocking Blink Logic (Radar Ping effect)
            now = ticks_ms()
            if ticks_diff(now, last_blink) > 500: # Blink every 500ms
                if led_on:
                    self.set_color(0, 0, 0) # Off
                else:
                    self.set_color(0, 0, 1) # Blue (System Active)
                led_on = not led_on
                last_blink = now

            # 2. Monitor G-Force for Impact
            current_g = self.get_g_force()
            
            # If we detect a spike greater than our trigger, touchdown has started
            if current_g > TOUCHDOWN_TRIGGER:
                return self.measure_impact()
            
            # Small delay to prevent CPU hogging
            sleep_ms(5)

    def measure_impact(self):
        """State 2: Touchdown Detected. Measuring peak force."""
        print("Touchdown detected! Analyzing structural integrity...")
        self.set_color(1, 0, 1) # Purple during calculation
        self.update_display("IMPACT DETECTED", "Analyzing...")
        
        max_g_seen = 0.0
        start_time = ticks_ms()
        
        # Monitor for 500ms to capture the full crash peak
        # Loop runs as fast as possible (no sleep) to catch peaks
        while ticks_diff(ticks_ms(), start_time) < 500:
            current_g = self.get_g_force()
            if current_g > max_g_seen:
                max_g_seen = current_g
            # No sleep here for max sampling rate
            
        return max_g_seen

    def show_mission_status(self, peak_g):
        """State 3 & 4: Display Mission Status and wait for reset."""
        
        # --- PHYSICS CALCULATIONS ---
        # 1. Force in Newtons (Real Impact Force)
        # F = m * a
        # a = peak_g * 9.81 (convert Gs to m/s^2)
        acceleration_ms2 = peak_g * GRAVITY_EARTH
        force_newtons = ROBOT_MASS * acceleration_ms2
        
        # 2. Mars Equivalent Gs
        # How many times the robot's Mars-weight is this force?
        weight_on_mars = ROBOT_MASS * GRAVITY_MARS
        mars_gs = force_newtons / weight_on_mars

        # Print detailed telemetry to Console
        print(f"Impact: {peak_g:.2f} G (Earth)")
        print(f"Force:  {force_newtons:.2f} N")
        print(f"Mars Eq:{mars_gs:.2f} G")
        
        survived = peak_g < STRUCTURAL_INTEGRITY_LIMIT
        
        status_text = "STATUS: SAFE" if survived else "STATUS: FAIL"
        
        # Update OLED - Prioritize the Target Comparison
        # Line 1: Force: 7.2 N
        # Line 2: Limit: 5.3 N
        # Line 3: STATUS: SAFE (or FAIL)
        self.update_display(
            f"Force: {force_newtons:.1f} N",
            f"Limit: {SAFE_FORCE_NEWTONS:.1f} N",
            status_text
        )

        # If mission failed, stamp the skull on the screen
        if not survived:
            self.draw_skull()

        if survived:
            print("Mission Status: SUCCESS. Rover operational.")
        else:
            print("Mission Status: FAILURE. Critical structural damage.")

        while True:
            # Blink Result
            if survived:
                self.set_color(0, 1, 0) # Green
            else:
                self.set_color(1, 0, 0) # Red
            
            sleep_ms(300)
            self.set_color(0, 0, 0)
            sleep_ms(300)

            # Check for Reset Button (Button OK/A) to reboot system
            if self.alvik.get_touch_ok(): 
                print("Rebooting Landing Systems...")
                self.update_display("REBOOTING...", "Please wait")
                # Debounce: wait for button release
                while self.alvik.get_touch_ok():
                    sleep_ms(50)
                break

    def run(self):
        while True:
            peak_force = self.wait_for_descent()
            self.show_mission_status(peak_force)

# Main Execution
rover = None
try:
    rover = MarsRover()
    rover.run()
except KeyboardInterrupt:
    print("Mission Control aborted sequence.")
except Exception as e:
    print(f"System Error: {e}")
    if rover:
        rover.update_display("SYSTEM ERROR", "Check Console")
finally:
    # Ensure LEDs are off and motors stopped if program exits
    if rover is not None:
        rover.alvik.left_led.set_color(0, 0, 0)
        rover.alvik.right_led.set_color(0, 0, 0)
        rover.alvik.stop()
    print("Telemetry closed.")