# run_diagnostics.py
# Version: V01
#
# The main execution script for NHS Robotics Diagnostics.
# It initializes the hardware and runs tests defined in external modules.

import time
import sys
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot

# Import test modules
import tests_core
import tests_extras

class DiagnosticRunner:
    def __init__(self):
        print("\n" + "="*40)
        print("NHS ROBOTICS DIAGNOSTIC SUITE V01")
        print("="*40)
        
        # 1. Init Hardware
        print("Initializing Hardware...")
        self.alvik = ArduinoAlvik()
        self.alvik.begin()
        self.alvik.stop() 
        
        # 2. Init SuperBot
        self.sb = SuperBot(self.alvik)
        
        # 3. Stats
        self.passes = 0
        self.fails = 0
        self.skips = 0

    def set_status_led(self, status):
        """
        Sets the NanoLED color based on status.
        status: 'ready', 'pass', 'fail', 'skip'
        """
        try:
            if status == 'ready':
                self.sb.set_nano_rgb(0, 0, 100) # Blue
            elif status == 'pass':
                self.sb.set_nano_rgb(0, 100, 0) # Green
            elif status == 'fail':
                self.sb.set_nano_rgb(100, 0, 0) # Red
            elif status == 'skip':
                self.sb.set_nano_rgb(50, 50, 0) # Yellow
            elif status == 'off':
                self.sb.nano_off()
        except:
            pass

    def log_result(self, test_name, result):
        """
        result tuple: (status_code, message)
        0=FAIL, 1=PASS, 2=SKIP
        """
        code, msg = result
        
        if code == 1:
            print(f"[PASS] {test_name}")
            self.passes += 1
            self.set_status_led('pass')
        elif code == 2:
            print(f"[SKIP] {test_name} ({msg})")
            self.skips += 1
            self.set_status_led('skip')
        else:
            print(f"[FAIL] {test_name} -> {msg}")
            self.fails += 1
            self.set_status_led('fail')
            
        time.sleep(0.15) # Visual delay for LED

    def run(self):
        self.set_status_led('ready')
        time.sleep(0.5)

        # --- DEFINE TEST SUITE ---
        # You can add or remove tests here easily
        test_suite = [
            ("API Integrity", tests_core.test_api_integrity),
            ("IMU Sensor",    tests_core.test_imu),
            ("ToF Sensors",   tests_core.test_tof),
            ("Line Sensors",  tests_core.test_line_sensors),
            ("Nano LED",      tests_extras.test_nano_led),
            ("OLED Display",  tests_extras.test_oled),
            ("Qwiic Buzzer",  tests_extras.test_buzzer),
            ("HuskyLens",     tests_extras.test_huskylens),
        ]

        # --- EXECUTE SUITE ---
        for name, func in test_suite:
            try:
                # Run the test function, passing the SuperBot instance
                result = func(self.sb)
                self.log_result(name, result)
            except Exception as e:
                self.log_result(name, (0, f"CRASH: {e}"))

        # --- REPORT ---
        print("\n" + "="*40)
        print(f"RESULTS: {self.passes} PASS | {self.fails} FAIL | {self.skips} SKIP")
        
        if self.sb.screen:
            self.sb.screen.show_lines("Tests Complete", f"Fail: {self.fails}", f"Pass: {self.passes}")

        if self.fails == 0:
            print("STATUS: SYSTEM HEALTHY")
            self.blink_sequence((0, 100, 0), 3) # Blink Green
        else:
            print("STATUS: SYSTEM FAILURE")
            while True:
                self.blink_sequence((100, 0, 0), 1) # Blink Red forever

    def blink_sequence(self, color, times):
        for _ in range(times):
            self.sb.set_nano_rgb(*color)
            time.sleep(0.3)
            self.sb.nano_off()
            time.sleep(0.3)

if __name__ == "__main__":
    runner = DiagnosticRunner()
    runner.run()
    