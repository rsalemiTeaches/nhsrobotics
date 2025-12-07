# -----------------------------------------------------------------------------
# SOLUTION: Gamepad Robot Control (Steering + Servo)
# -----------------------------------------------------------------------------
#
# GAMEPAD INPUT LIST:
#
# Analog Sticks (Floats from -1.0 to 1.0)
#   ctl.left_stick_x    ctl.right_stick_x
#   ctl.left_stick_y    ctl.right_stick_y (1.0 = Max Forward)
#
# Analog Triggers (Floats from 0.0 to 1.0)
#   ctl.L2              ctl.R2            (1.0 = Fully Pressed)
#
# Buttons (Booleans: True or False)
#   ctl.buttons['cross']       ctl.buttons['triangle']
#   ctl.buttons['square']      ctl.buttons['circle']
#   ctl.buttons['up']          ctl.buttons['down']
#   ctl.buttons['left']        ctl.buttons['right']
#   ctl.buttons['L1']          ctl.buttons['R1']
#   ctl.buttons['L3']          ctl.buttons['R3']
#   ctl.buttons['share']       ctl.buttons['options']
#   ctl.buttons['ps']
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
        # Break the loop if 'options' is pressed to run the finally block
        if ctl.buttons['options']:
            print("Options pressed. Exiting...")
            break

        # C. CALCULATE DRIVETRAIN (Steering Mix)
        
        # 1. Base Speed from Left Stick Y
        # Prompt: "1 = max forward, -1 = max backward"
        throttle = ctl.left_stick_y * MAX_SPEED
        
        # 2. Turn Percentage from Right Stick X
        # Prompt: "RX controls steering by percentage"
        # -1.0 = Left, 1.0 = Right
        turn_pct = ctl.right_stick_x
        
        # Start with equal speed
        left_speed = throttle
        right_speed = throttle
        
        # Apply Steering Logic:
        # "RX to the left means the left wheel is a 0 and right is drive speed"
        if turn_pct < 0:
            # Turning LEFT: Reduce Left Wheel
            # If turn_pct is -1.0, factor becomes 0.0
            left_speed = throttle * (1 + turn_pct)
            
        elif turn_pct > 0:
            # Turning RIGHT: Reduce Right Wheel
            # If turn_pct is 1.0, factor becomes 0.0
            right_speed = throttle * (1 - turn_pct)

        # D. CALCULATE FORKLIFT (Servo)
        # Prompt: "At R2=1.0 servo is 0. At R2=0 servo is 180."
        # Equation: 180 - (R2 * 180)
        servo_angle = int(180 - (ctl.R2 * 180))
        
        # E. APPLY OUTPUTS
        
        # Drive Motors
        alvik.set_wheels_speed(left_speed, right_speed)
        
        # Move Servos
        # set_servo_positions(servo_1_angle, servo_2_angle)
        # We set Servo 1 to our calculated angle, and Servo 2 to 0 (default)
        alvik.set_servo_positions(servo_angle, 0)
        
        # F. SLEEP
        time.sleep_ms(10)

finally:
    # Safety Shutdown
    print("Stopping Robot...")
    alvik.set_wheels_speed(0,0)
    alvik.stop()