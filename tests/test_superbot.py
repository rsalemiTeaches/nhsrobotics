# test_superbot.py
# Version: V01
# 
# A comprehensive diagnostic tool for NHS Robotics.
# Checks for:
# 1. API Completeness (did an update delete methods?)
# 2. Core Alvik Hardware (IMU, ToF, Line Sensors)
# 3. Optional Peripherals (HuskyLens, OLED, Buzzer) - Skips if missing.

import time
import sys
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot

class Diagnostics:
    def __init__(self):
        print("\n" + "="*40)
        print("NHS ROBOTICS DIAGNOSTIC SUITE V01")
        print("="*40)
        
        # Init Hardware
        self.alvik = ArduinoAlvik()
        self.alvik.begin()
        self.alvik.stop() # Ensure motors are off
        
        # Init SuperBot
        print("Initializing SuperBot...")
        self.sb = SuperBot(self.alvik)
        
        self.fails = 0
        self.passes = 0
        self.skips = 0

    def set_leds(self, color):
        """Helper to set top LED color. color = (r, g, b)"""
        # Alvik specific LED control (assuming using left/right or system LED)
        try:
            self.alvik.left_led.set_color(color[0], color[1], color[2])
            self.alvik.right_led.set_color(color[0], color[1], color[2])
        except:
            pass

    def report(self, test_name, status, message=""):
        """
        Status: 
        0 = FAIL (Red)
        1 = PASS (Green)
        2 = SKIP (Yellow)
        """
        if status == 1:
            print(f"[PASS] {test_name}")
            self.passes += 1
            self.set_leds((0, 100, 0)) # Green
        elif status == 2:
            print(f"[SKIP] {test_name} ({message})")
            self.skips += 1
            self.set_leds((50, 50, 0)) # Yellow
        else:
            print(f"[FAIL] {test_name} -> {message}")
            self.fails += 1
            self.set_leds((100, 0, 0)) # Red
            
        time.sleep(0.1) # Small delay to see the LED flash

    def run_tests(self):
        self.set_leds((0, 0, 100)) # Blue start
        time.sleep(1)

        # --- GROUP 1: API INTEGRITY (The "Did I break it?" check) ---
        print("\n--- API CHECK ---")
        required_methods = [
            "drive_distance", 
            "approach_tag", 
            "turn_to_heading",
            "get_closest_distance",
            "get_pressed_ok",  # Check for new buttons
            "center_on_tag"
        ]
        
        for method in required_methods:
            if hasattr(self.sb, method):
                self.report(f"Method: {method}()", 1)
            else:
                self.report(f"Method: {method}()", 0, "MISSING from SuperBot class")

        # --- GROUP 2: CORE SENSORS ---
        print("\n--- CORE SENSORS ---")
        
        # IMU Check
        try:
            yaw = self.sb.get_yaw()
            # Yaw should be a float/int, not None
            if isinstance(yaw, (int, float)):
                self.report("IMU (Yaw)", 1)
            else:
                self.report("IMU (Yaw)", 0, f"Invalid value: {yaw}")
        except Exception as e:
            self.report("IMU (Yaw)", 0, str(e))

        # ToF Check
        try:
            dist = self.sb.get_closest_distance()
            if isinstance(dist, (int, float)) and dist >= 0:
                self.report("ToF Sensors", 1)
            else:
                self.report("ToF Sensors", 0, "Invalid reading")
        except Exception as e:
            self.report("ToF Sensors", 0, str(e))

        # Line Sensor Check
        try:
            # Direct alvik access just to be sure hardware responds
            l, c, r = self.alvik.get_line_sensors()
            if isinstance(l, int):
                self.report("Line Sensors", 1)
            else:
                self.report("Line Sensors", 0, "Invalid Data")
        except Exception as e:
            self.report("Line Sensors", 0, str(e))

        # --- GROUP 3: OPTIONAL PERIPHERALS ---
        print("\n--- PERIPHERALS ---")

        # OLED Test
        if self.sb.screen:
            try:
                self.sb.screen.show_lines("Diagnostic Mode", "Running Tests...", "Please Wait")
                self.report("OLED Display", 1)
            except Exception as e:
                self.report("OLED Display", 0, str(e))
        else:
            self.report("OLED Display", 2, "Not Detected")

        # Buzzer Test
        # Note: We check the internal _buzzer object or the class wrapper
        if hasattr(self.sb, 'buzzer') and self.sb.buzzer and self.sb.buzzer.connected:
            try:
                self.sb.buzzer.on()
                time.sleep(0.1)
                self.sb.buzzer.off()
                self.report("Qwiic Buzzer", 1)
            except Exception as e:
                self.report("Qwiic Buzzer", 0, str(e))
        else:
            self.report("Qwiic Buzzer", 2, "Not Detected")

        # HuskyLens Test
        if self.sb.husky:
            try:
                # Just pinging it to see if it crashes
                self.sb.husky.request()
                self.report("HuskyLens", 1)
            except Exception as e:
                # If request fails, it might be a wiring issue or protocol error
                self.report("HuskyLens", 0, str(e))
        else:
            self.report("HuskyLens", 2, "Not Detected")

        # --- CONCLUSION ---
        print("\n" + "="*40)
        print(f"RESULTS: {self.passes} PASS | {self.fails} FAIL | {self.skips} SKIP")
        
        if self.sb.screen:
            self.sb.screen.show_lines("Tests Complete", f"Failures: {self.fails}", f"Passes: {self.passes}")

        if self.fails == 0:
            print("STATUS: SYSTEM HEALTHY")
            # Pulse Green 3 times
            for _ in range(3):
                self.set_leds((0, 100, 0))
                time.sleep(0.3)
                self.set_leds((0, 0, 0))
                time.sleep(0.3)
            # Stay Green
            self.set_leds((0, 50, 0))
        else:
            print("STATUS: SYSTEM FAILURE")
            # Blink Red forever
            while True:
                self.set_leds((100, 0, 0))
                time.sleep(0.2)
                self.set_leds((0, 0, 0))
                time.sleep(0.2)

if __name__ == "__main__":
    diag = Diagnostics()
    diag.run_tests()
    