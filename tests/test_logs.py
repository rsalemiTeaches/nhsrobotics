# test_logging.py
# Version: V01
# Description: Tests the enhanced multi-argument log_info and log_error functions.
# Developed with the assistance of Google Gemini.

import time
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot

# 1. Initialize the base ArduinoAlvik object
alvik = ArduinoAlvik()

# 2. MUST call begin() before initializing SuperBot to enable I2C
alvik.begin()

# 3. Initialize the SuperBot wrapper (MUST be named sb)
sb = SuperBot(alvik)

print("\n--- Starting Logging Feature Test ---\n")

# Enable info logging so messages are written to /workspace/logs/messages.log
sb.enable_info_logging()
time.sleep(1)

# Test 1: Standard single-string logging (Backwards compatibility)
sb.log_info("Test 1: Standard single string.")
time.sleep(1)

# Test 2: Multiple arguments of mixed types (String, Float, Integer)
simulated_distance = 12.4
simulated_tag = 2
sb.log_info("Test 2: Distance to tag", simulated_tag, "is", simulated_distance, "cm.")
time.sleep(1)

# Test 3: Multiple arguments with a custom separator
x_coord = 150
y_coord = 200
sb.log_info("Test 3: Target Coordinates", x_coord, y_coord, sep=" | ")
time.sleep(1)

# Test 4: Single-string error logging
sb.log_error("Test 4: Single string simulated error.")
time.sleep(1)

# Test 5: Multiple arguments error logging
error_code = 503
sensor_name = "HuskyLens"
sb.log_error("Test 5: Connection to", sensor_name, "timed out. Code:", error_code)

print("\n--- Logging Test Complete ---")
print("Please check the OLED screen to see if the last error is displayed.")
print("Then, check /workspace/logs/messages.log and /workspace/logs/errors.log on the Alvik.")

# Turn off logging before exiting
sb.disable_info_logging()
