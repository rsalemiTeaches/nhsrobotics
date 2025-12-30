# test_drive.py
# Version: V01
# Purpose: Validates the drive_distance() and move_complete() methods in SuperBot (nhs_robotics V18)

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# --- SETUP ---
print("Initializing Robot...")
alvik = ArduinoAlvik()
alvik.begin()

bot = SuperBot(alvik)
bot.enable_info_logging()

# --- HELPER ---
def countdown(seconds, message):
    for i in range(seconds, 0, -1):
        bot.update_display(message, f"Starting in {i}...")
        print(f"{message} in {i}...")
        time.sleep(1)
    bot.update_display(message, "GO!")

# --- TESTS ---

def test_1_blocking_precision():
    """
    Test 1: Drive forward 30cm, wait, drive back 30cm.
    User should verify the robot returns to the exact starting line.
    """
    DIST = 30
    
    countdown(3, "Test 1: Precision")
    
    # Forward
    bot.log_info(f"Forward {DIST}cm")
    bot.drive_distance(DIST, speed_cm_s=25, blocking=True)
    
    time.sleep(0.5)
    
    # Backward
    bot.log_info(f"Reverse {DIST}cm")
    bot.drive_distance(-DIST, speed_cm_s=25, blocking=True)
    
    bot.log_info("Test 1 Complete")
    time.sleep(2)

def test_2_non_blocking_multitask():
    """
    Test 2: Start a drive, then flash LEDs while moving.
    Proves the code does not hang the processor.
    """
    DIST = 30
    
    countdown(3, "Test 2: Multitask")
    
    bot.log_info("Driving Async...")
    
    # Start moving (blocking=False)
    bot.drive_distance(DIST, speed_cm_s=15, blocking=False)
    
    # Do other things while moving
    toggle = False
    while not bot.move_complete():
        # This loop runs WHILE the robot is driving
        if toggle:
            bot.bot.left_led.set_color(1, 0, 0) # Red
            bot.bot.right_led.set_color(0, 0, 1) # Blue
        else:
            bot.bot.left_led.set_color(0, 0, 1) # Blue
            bot.bot.right_led.set_color(1, 0, 0) # Red
        toggle = not toggle
        
        # Update screen with encoder values to show we are live
        l, r = bot.bot.get_wheels_position()
        bot.update_display("Moving Async", f"L:{int(l)} R:{int(r)}")
        time.sleep(0.1)
        
    # Reset LEDs
    bot.bot.left_led.set_color(0, 0, 0)
    bot.bot.right_led.set_color(0, 0, 0)
    bot.log_info("Test 2 Complete")
    time.sleep(2)

def test_3_safety_timeout():
    """
    Test 3: Command a move that is impossible to finish in the time given.
    Example: Drive 100cm but timeout after 2 seconds.
    The robot should STOP after 2 seconds.
    """
    countdown(3, "Test 3: Timeout")
    
    bot.log_info("Force Timeout...")
    
    # Drive 100cm (takes ~5s) but timeout set to 2s
    bot.drive_distance(100, speed_cm_s=20, blocking=True, timeout=2.0)
    
    bot.log_info("Test 3 Complete")
    bot.update_display("Done", "Check Log for", "Timeout Warn")

# --- MAIN EXECUTION ---

try:
    bot.update_display("Test Suite", "Place on Floor")
    time.sleep(2)
    
    test_1_blocking_precision()
    test_2_non_blocking_multitask()
    test_3_safety_timeout()
    
    bot.update_display("All Tests", "Finished")

except KeyboardInterrupt:
    bot.bot.brake()
    print("Test Aborted")

# Developed with the assistance of Google Gemini