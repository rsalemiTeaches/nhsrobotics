# test_nhs_features.py
# Version: V01
# Purpose: Verify all features of nhs_robotics.py V09

from nhs_robotics import NHSAlvik, get_closest_distance
import time
import os

print("--- TESTING NHS ROBOTICS V09 ---")

# 1. Initialize Robot
print("\n1. Initializing NHSAlvik...")
robot = NHSAlvik()
robot.begin() # Start base Alvik
print("   [PASS] Robot Initialized")

# 2. Test Distance Logic Bridge
print("\n2. Testing Distance Logic Bridge...")
# Test Standalone (Legacy)
d_legacy = get_closest_distance(0, 100, 50, 0, 12)
# Test New Static Method via Instance
d_new = robot._get_closest_distance(0, 100, 50, 0, 12)

if d_legacy == 12 and d_new == 12:
    print(f"   [PASS] Logic Consistent (Legacy: {d_legacy}, New: {d_new})")
else:
    print(f"   [FAIL] Logic Mismatch (Legacy: {d_legacy}, New: {d_new})")

# 3. Test Logging System
print("\n3. Testing Logging & OLED Wrapping...")

# Enable Logging
robot.enable_logging()

# Test Short Message
robot.log_message("Short Msg Test")
time.sleep(1)

# Test Long Message (Should Wrap)
long_msg = "This is a very long message that should wrap nicely on the OLED screen."
print(f"   Sending: '{long_msg[:20]}...'")
robot.log_message(long_msg)
time.sleep(2)

# Test Error Logging (Should verify file write)
robot.log_error("Test Critical Error")

# Verify File Creation
print("   Verifying Log Files...")
try:
    if 'logs' in os.listdir('/'):
        logs = os.listdir('/logs')
        if 'messages.log' in logs and 'errors.log' in logs:
            print(f"   [PASS] Log files found: {logs}")
        else:
            print(f"   [WARN] Log directory exists, but files missing? {logs}")
    else:
        print("   [FAIL] /logs directory missing")
except Exception as e:
    print(f"   [FAIL] File Check Error: {e}")

# Disable Logging
robot.disable_logging()

# 4. Test Hardware Access
print("\n4. Testing Hardware Access (Graceful Fail)...")
dist = robot.get_camera_distance()
if dist is None:
    print("   [INFO] Camera Distance: None (Normal if no tag)")
else:
    print(f"   [PASS] Camera Distance: {dist:.1f} cm")

print("\n--- TEST COMPLETE ---")