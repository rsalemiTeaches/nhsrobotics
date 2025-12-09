# -----------------------------------------------------------------------------
# PROJECT 17 SOLUTION: Gamepad Forklift (Tank Drive + Lift + Safety Fence)
# -----------------------------------------------------------------------------
#
# CONTROLS:
#   Left Stick Y   -> Left Motor (Tank)
#   Right Stick Y  -> Right Motor (Tank)
#   D-Pad Up       -> Raise Lift
#   D-Pad Down     -> Lower Lift
#   Options        -> Exit Program
#
# SAFETY:
#   The robot will refuse to drive FORWARD if it detects a black line.
#   It will allows drive BACKWARD to escape the edge.
# -----------------------------------------------------------------------------

from arduino_alvik import ArduinoAlvik
from nhs_robotics import Controller
import machine
import ubinascii
import time

# --- 1. SETUP & CONFIGURATION ---

# Speed Limit (0 to 100)
MAX_SPEED = 50
# Servo Smoothness (Degrees to move per loop)
SERVO_STEP = 4
# Line Sensor Threshold (Higher = Darker)
# > 300 usually indicates a black line on white paper
LINE_THRESHOLD = 300

# Generate Unique Name
id_hex = ubinascii.hexlify(machine.unique_id()).decode()
MY_NAME = f"Alvik-{id_hex[-4:].upper()}"

# Initialize Robot
alvik = ArduinoAlvik()
alvik.begin()

# Initialize Servo State
current_servo_angle = 0
target_servo_angle = 0
alvik.set_servo_positions(current_servo_angle, 0)

try:
    # Initialize Controller
    print(f"Creating Wi-Fi: {MY_NAME}")
    ctl = Controller(ssid=MY_NAME)

    # --- 2. CONNECTION LOOP ---
    print("Waiting for controller connection...")
    while not ctl.is_connected():
        ctl.update()
        # Blink Yellow
        alvik.left_led.set_color(1, 1, 0)
        alvik.right_led.set_color(1, 1, 0)
        time.sleep(0.1)
        alvik.left_led.set_color(0, 0, 0)
        alvik.right_led.set_color(0, 0, 0)
        time.sleep(0.1)

    print("Controller Connected!")
    alvik.left_led.set_color(0, 1, 0)
    alvik.right_led.set_color(0, 1, 0)


    # --- 3. MAIN LOOP ---
    while True:
        # A. UPDATE
        ctl.update()
        
        # B. CHECK EXIT
        if ctl.buttons['options']:
            print("Options pressed. Exiting...")
            break

        # C. CALCULATE DRIVETRAIN (Tank Control)
        # Negative stick = Reverse, Positive stick = Forward
        left_speed = ctl.left_stick_y * MAX_SPEED
        right_speed = ctl.right_stick_y * MAX_SPEED

        # --- D. SAFETY FENCE LOGIC ---
        # Read the 3 line sensors (Left, Center, Right)
        l_sens, c_sens, r_sens = alvik.get_line_sensors()
        
        # Check if ANY sensor sees the black line
        if l_sens > LINE_THRESHOLD or c_sens > LINE_THRESHOLD or r_sens > LINE_THRESHOLD:
            # SAFETY TRIGGERED: The robot is on the edge.
            
            # Logic: If the user is trying to drive FORWARD (speed > 0), stop them.
            # If they are trying to drive BACKWARD (speed < 0), let them go.
            
            if left_speed > 0:
                left_speed = 0
            
            if right_speed > 0:
                right_speed = 0
                
            # Optional: Flash Red to warn the driver
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
        else:
            # Clear warning lights (Return to Green)
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)

        # E. CALCULATE FORKLIFT (Target Selection)
        if ctl.buttons['up']:
            target_servo_angle = 0
        elif ctl.buttons['down']:
            target_servo_angle = 180
            
        # F. SMOOTH SERVO MOVEMENT
        if current_servo_angle < target_servo_angle:
            current_servo_angle += SERVO_STEP
            if current_servo_angle > target_servo_angle:
                current_servo_angle = target_servo_angle
                
        elif current_servo_angle > target_servo_angle:
            current_servo_angle -= SERVO_STEP
            if current_servo_angle < target_servo_angle:
                current_servo_angle = target_servo_angle

        # G. APPLY OUTPUTS
        alvik.set_wheels_speed(left_speed, right_speed)
        alvik.set_servo_positions(current_servo_angle, 0)
        
        time.sleep_ms(10)

finally:
    print("Stopping Robot...")
    alvik.set_wheels_speed(0,0)
    # Lower lift for safety
    alvik.set_servo_positions(180,0)
    alvik.stop()
