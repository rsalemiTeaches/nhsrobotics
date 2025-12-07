# -----------------------------------------------------------------------------
# SOLUTION: Gamepad Robot Control (Tank Drive + Digital Lift)
# -----------------------------------------------------------------------------
#
# GAMEPAD INPUT LIST:
#
# Analog Sticks (Floats from -1.0 to 1.0)
#   ctl.left_stick_y   -> Left Motor Speed
#   ctl.right_stick_y  -> Right Motor Speed
#
# D-Pad Buttons (Booleans)
#   ctl.buttons['up']    -> Raise Lift (Servo 0)
#   ctl.buttons['down']  -> Lower Lift (Servo 180)
#
# System Buttons
#   ctl.buttons['options'] -> Exit Program
#
# -----------------------------------------------------------------------------

from arduino_alvik import ArduinoAlvik
from nhs_robotics import Controller
import machine
import ubinascii
import time

# --- 1. SETUP & CONFIGURATION ---

# Speed Limit (0 to 100)
MAX_SPEED = 50

# Generate Unique Name for Wi-Fi based on the board's ID
id_hex = ubinascii.hexlify(machine.unique_id()).decode()
MY_NAME = f"Alvik-{id_hex[-4:].upper()}"

# Initialize Robot
alvik = ArduinoAlvik()
alvik.begin()

# Initialize Servo State (Start Raised/0)
current_servo_angle = 0
# Set initial position immediately
alvik.set_servo_positions(current_servo_angle, 0)

try:
    # Initialize Controller
    print(f"Creating Wi-Fi: {MY_NAME}")
    ctl = Controller(ssid=MY_NAME)

    # --- 2. CONNECTION LOOP ---
    # Loop and blink Yellow until the Gamepad connects
    print("Waiting for controller connection...")

    while not ctl.is_connected():
        # Vital: Check for network activity
        ctl.update()
        
        # Blink routine
        alvik.left_led.set_color(1, 1, 0) # Yellow
        alvik.right_led.set_color(1, 1, 0)
        time.sleep(0.1)
        
        alvik.left_led.set_color(0, 0, 0) # Off
        alvik.right_led.set_color(0, 0, 0)
        time.sleep(0.1)

    # Connection Established - Turn Green
    print("Controller Connected!")
    alvik.left_led.set_color(0, 1, 0)
    alvik.right_led.set_color(0, 1, 0)


    # --- 3. MAIN LOOP ---
    while True:
        # A. UPDATE (Requirement: Always Call First)
        ctl.update()
        
        # B. CHECK EXIT CONDITION
        if ctl.buttons['options']:
            print("Options pressed. Exiting...")
            break

        # C. CALCULATE DRIVETRAIN (Tank Control)
        # Left Stick controls Left Wheel, Right Stick controls Right Wheel
        left_speed = ctl.left_stick_y * MAX_SPEED
        right_speed = ctl.right_stick_y * MAX_SPEED

        # D. CALCULATE FORKLIFT (Digital Control)
        # We check the buttons to update the state variable.
        # The variable 'current_servo_angle' remembers the position.
        
        if ctl.buttons['up']:
            current_servo_angle = 0
        elif ctl.buttons['down']:
            current_servo_angle = 180
            
        # E. APPLY OUTPUTS
        
        # Drive Motors
        alvik.set_wheels_speed(left_speed, right_speed)
        
        # Move Servos
        # We constantly send the current angle (0 or 180) to Servo 1.
        # Servo 2 is kept at 0.
        alvik.set_servo_positions(current_servo_angle, 0)
        
        # F. SLEEP
        time.sleep_ms(10)

finally:
    # Safety Shutdown
    print("Stopping Robot...")
    alvik.set_wheels_speed(0,0)
    alvik.set_servo_positions(180,0)
    alvik.stop()