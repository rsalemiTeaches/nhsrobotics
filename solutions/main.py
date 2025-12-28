# Project 18: Capstone Step 1 - The Blind Approach
# Version: V10
#
# OBJECTIVE:
# 1. Start in IDLE (Fork Up).
# 2. On Button Press -> Drop Fork -> Search.
# 3. Drive to the target using the Camera.
# 4. Handle the "Blind Spot" DYNAMICALLY.
# 5. SAFETY: Allow 'X' button to cancel at any time.
# 6. SHUTDOWN: Ensure motors and LEDs turn off on exit.
# 7. DISPLAY: Show distance on oLED using show_lines().
#
# Created with the help of Gemini Pro

from arduino_alvik import ArduinoAlvik
from qwiic_huskylens import QwiicHuskylens
from qwiic_i2c.micropython_i2c import MicroPythonI2C
from nhs_robotics import oLED
import time
import sys

# --- CONSTANTS ---
K_CONSTANT = 1624.0      # Calculated from your calibration
BLIND_SPOT_THRESHOLD = 20.0 # If we lose tag closer than this, assume it's the Blind Spot
TARGET_DIST_CM = 5.0     # Final goal distance from box
SPEED_APPROACH = 20      # Slow speed for safety

# --- HARDWARE SETUP ---
alvik = ArduinoAlvik()
alvik.begin()

# Setup OLED - Global Variable
screen = None
try:
    screen = oLED()
    # Simplified initialization using show_lines
    screen.show_lines("Booting...", "Please Wait")
    print("OLED Initialized")
except Exception as e:
    print(f"OLED Error: {e}")

# Camera
try:
    alvik_i2c = MicroPythonI2C(scl=12, sda=11)
    huskylens = QwiicHuskylens(i2c_driver=alvik_i2c)
    huskylens.begin()
except:
    print("Camera Error!")
    if screen:
        screen.show_lines("Cam Error!", "Check Wiring")
    sys.exit()

# --- HELPER FUNCTIONS ---

def set_fork_position(angle):
    """
    Moves Servo A (Fork) while keeping Servo B safely where it is.
    0 = UP (Carry)
    180 = DOWN (Pickup)
    """
    # 1. Get current positions so we don't disturb Servo B
    current_positions = alvik.get_servo_positions()
    current_b = current_positions[1]
    
    # 2. Update ONLY Servo A, keep B exactly the same
    alvik.set_servo_positions(angle, current_b)
    
    time.sleep(0.5) # Wait for physical movement

def get_distance_to_tag():
    """Returns distance in CM or None if no tag seen."""
    huskylens.request()
    if len(huskylens.blocks) > 0:
        width = huskylens.blocks[0].width
        return K_CONSTANT / width
    return None

def check_cancel():
    """Checks if the X button is pressed. If so, raises exception to stop."""
    if alvik.get_touch_cancel():
        raise SystemExit("User pressed 'X'")

def update_display(line1, line2=""):
    """Helper to write to OLED using the built-in library function"""
    global screen
    if screen:
        try:
            # show_lines handles clearing and refreshing internally
            screen.show_lines(str(line1), str(line2))
        except Exception as e:
            print(f"Display Error: {e}")

# --- MAIN PROGRAM ---
try:
    print("--- CAPSTONE STEP 1 (V10) ---")
    update_display("Capstone V10", "Waiting...")
    print("Waiting for Button to start...")
    alvik.left_led.set_color(0, 1, 0) # Green (Ready)

    # 1. STATE_IDLE
    # Wait for user input
    set_fork_position(0) # Ensure fork is UP

    while not alvik.get_touch_center():
        check_cancel() # Allow exit even while waiting
        time.sleep(0.01)

    print("Starting Approach...")
    update_display("Approach", "Starting...")
    alvik.left_led.set_color(1, 1, 0) # Yellow (Working)

    # 2. PREPARE
    # Lower the fork before we get too close
    set_fork_position(180) # Down

    # 3. STATE_APPROACH (Visual Phase)
    tag_limit_reached = False
    last_known_dist = 100.0 # Start with a large number

    while True:
        # A. Safety Check
        check_cancel()
        
        # B. Sensor Data
        dist = get_distance_to_tag()
        
        if dist is not None:
            # --- CASE 1: TAG VISIBLE ---
            print(f"Visual Distance: {dist:.1f} cm")
            update_display("Visual Mode", f"Dist: {dist:.1f} cm")
            last_known_dist = dist # Remember this!
            
            # Drive forward
            alvik.set_wheels_speed(SPEED_APPROACH, SPEED_APPROACH)
            alvik.right_led.set_color(0,1,0)
            alvik.left_led.set_color(0,1,0)
            
        else:
            # --- CASE 2: TAG LOST ---
            # Did we lose it because we got too close (Blind Spot)?
            # Or did we lose it because it's gone?
            
            if last_known_dist < BLIND_SPOT_THRESHOLD:
                print(f"Tag lost at {last_known_dist:.1f}cm. Assuming Blind Spot.")
                update_display("Tag Lost", "Blind Spot!")
                tag_limit_reached = True
                break # Exit loop to do final blind push
                
            else:
                # Safety: Stop if we lose the tag unexpectedly far away
                print("Tag lost! Stopping.")
                update_display("Tag Lost", "Stopping")
                alvik.set_wheels_speed(0, 0)
                alvik.right_led.set_color(1,0,0)
                alvik.left_led.set_color(1,0,0)
            
        time.sleep(0.05)

    # 4. STATE_APPROACH (Blind Phase)
    if tag_limit_reached:
        # Final check before the blind move
        check_cancel()
        
        # Calculate remaining distance based on the LAST KNOWN distance
        final_push_cm = last_known_dist - TARGET_DIST_CM
        
        if final_push_cm > 0:
            print(f"Blind Drive: Moving {final_push_cm:.1f} cm...")
            update_display("Blind Drive", f"Go {final_push_cm:.1f} cm")
            
            # NOTE: .move() is blocking. We cannot cancel *during* this specific move
            # without more complex code, but it is short (~10cm).
            alvik.move(final_push_cm) 
        else:
            print("Already at target distance!")
            update_display("Blind Drive", "At Target")

    # 5. STOP
    print("Target Reached!")
    update_display("Target Reached!", "Done")

except SystemExit:
    # Graceful exit for cancel button
    pass
except Exception as e:
    print(f"An error occurred: {e}")
    if screen:
        try:
            # Simplified error display
            screen.show_lines("Error:", str(e)[:16])
        except:
            pass

finally:
    # --- CLEANUP (Runs on Exit, Error, or Cancel) ---
    print("Program Finished. Cleaning up...")
    alvik.set_wheels_speed(0, 0)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
    