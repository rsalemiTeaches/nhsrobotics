# Project 17: The Ultimate Remote Control
#
# GOAL: Use the WebGamepad library to drive the robot.
# 
# CONTROLS:
# Left Stick:  Drive (Speed)
# Right Stick: Turn (Steering)
# Button A:    Honk Horn
# Button B:    Turbo Boost!

from arduino_alvik import ArduinoAlvik
from web_gamepad import WebGamepad
import time

# --- Setup ---
alvik = ArduinoAlvik()
alvik.begin()

# Create the Gamepad Connection
# This will print the IP address to the console
gamepad = WebGamepad()

print("Ready to Race!")
alvik.left_led.set_color(0, 0, 1) # Blue light means ready

try:
    while not alvik.get_touch_cancel():
        
        # 1. IMPORTANT: Process network data
        gamepad.update()
        
        # 2. Read Inputs
        # Axis 1 is Left Stick Up/Down (Inverted)
        throttle = gamepad.get_axis(1) * -1 
        
        # Axis 2 is Right Stick Left/Right
        steering = gamepad.get_axis(2)
        
        # 3. Handle Buttons
        if gamepad.is_pressed(gamepad.BTN_A):
            print("Honk!")
            # Add buzzer code here if you have one!
            alvik.left_led.set_color(1, 0, 0)
        else:
            alvik.left_led.set_color(0, 1, 0) # Green is normal

        # Turbo Boost on Button B?
        speed_multiplier = 0.5 # Normal speed 50%
        if gamepad.is_pressed(gamepad.BTN_B):
            speed_multiplier = 1.0 # Turbo 100%

        # 4. Arcade Drive Logic
        # Mix Throttle and Steering to get Left/Right motor speeds
        left_motor = (throttle + steering) * speed_multiplier
        right_motor = (throttle - steering) * speed_multiplier
        
        # 5. Drive the Robot
        alvik.set_wheels_speed(left_motor, right_motor)
        
        # Small sleep to keep loop running smoothly
        # (Too fast and the WiFi handling gets choppy)
        time.sleep(0.01)

except Exception as e:
    print(f"Error: {e}")

finally:
    alvik.stop()
    alvik.set_wheels_speed(0, 0)