# -----------------------------------------------------------------------------
# FRAMEWORK: Gamepad Robot Control
# -----------------------------------------------------------------------------
#
# GAMEPAD INPUT LIST:
#
# Analog Sticks (Floats from -1.0 to 1.0)
#   ctl.left_stick_x    ctl.right_stick_x
#   ctl.left_stick_y    ctl.right_stick_y
#
# Analog Triggers (Floats from 0.0 to 1.0)
#   ctl.L2              ctl.R2
#
# Buttons (Booleans: True or False)
#   ctl.buttons['cross']       ctl.buttons['triangle']
#   ctl.buttons['square']      ctl.buttons['circle']
#   ctl.buttons['up']          ctl.buttons['down']
#   ctl.buttons['left']        ctl.buttons['right']
#   ctl.buttons['L1']          ctl.buttons['R1']
#   ctl.buttons['L3']          ctl.buttons['R3'] (Stick clicks)
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


    # --- 2. CONNECTION LOOP (Requirement 1) ---
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
        # A. UPDATE (Requirement 2)
        # Must be called at the start of every loop to get new Wi-Fi data
        ctl.update()

        # B. CALCULATE SPEEDS (Requirement 3)
        # Initialize speeds to 0
        left_speed = 0
        right_speed = 0
        
        # --- STUDENT WORK SECTION ---
        # TODO: Calculate the speed based on the controller inputs.
        # Example: left_speed = ctl.left_stick_y * 50
        
        
        
        # ----------------------------

        # C. APPLY MOTOR SPEEDS
        # This runs every loop, even if speeds are 0 (which stops the bot)
        alvik.set_wheels_speed(left_speed, right_speed)

        # D. SLEEP
        # Short delay to keep the loop stable
        time.sleep_ms(10)
finally:
    alvik.set_wheels_speed(0,0)
    alvik.stop()
    