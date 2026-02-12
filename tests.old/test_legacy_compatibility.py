# test_legacy_compatibility.py
# Version: V01
#
# PURPOSE:
# This script represents "Old Student Code".
# It must run EXACTLY the same on the new library as it did on the old one.
# It does NOT use the new NHSAlvik class.

from nhs_robotics import oLED, Buzzer, get_closest_distance
import time

print("--- STARTING LEGACY COMPATIBILITY TEST ---")

# 1. Test Helper Function
# Expected: Ignore 0, ignore negative (if any), return lowest positive.
print("1. Testing get_closest_distance...")
d = get_closest_distance(0, 100, 50, 0, 12)
if d == 12:
    print(f"   [PASS] Distance Logic Correct: {d}")
else:
    print(f"   [FAIL] Distance Logic Incorrect: {d}")


# 2. Test OLED (Legacy Mode)
# Student Expectation: oLED() creates its own connection and works immediately.
print("\n2. Testing OLED (Default Init)...")
try:
    screen = oLED()
    screen.show_lines("Legacy Test", "Running...", "Look at screen")
    print("   [PASS] OLED Command Sent")
except Exception as e:
    print(f"   [FAIL] OLED Crash: {e}")


# 3. Test Buzzer (Legacy Mode)
# Student Expectation: Buzzer() creates its own connection.
print("\n3. Testing Buzzer (Default Init)...")
try:
    # Explicitly using the old signature (no i2c_driver passed)
    my_buzzer = Buzzer()
    
    # Check if the buzzer actually connected (internal attribute check)
    if my_buzzer._buzzer is not None:
        print("   [PASS] Buzzer Connected")
        print("   Playing 'Yes' effect...")
        my_buzzer.play_effect(my_buzzer.EFFECT_YES)
    else:
        print("   [WARN] Buzzer object created, but hardware not detected.")
        print("          (This is normal if no buzzer is plugged in)")

except Exception as e:
    print(f"   [FAIL] Buzzer Crash: {e}")

print("\n--- TEST COMPLETE ---")
