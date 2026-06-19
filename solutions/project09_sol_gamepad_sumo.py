from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

# 1. Initialize Robot
alvik = ArduinoAlvik()
alvik.begin()

# 2. Initialize Wi-Fi Controller
gamepad = RobotGamepad(alvik)
MAX_SPEED = 100.0 # 100% speed multiplier

try:
    # --- MAIN LOOP ---
    while True:
        # Update Data from Wi-Fi
        gamepad.update()

        # Drive Logic (Tank Drive)
        left_speed = gamepad.left_y * MAX_SPEED
        right_speed = gamepad.right_y * MAX_SPEED
        alvik.set_wheels_speed(left_speed, right_speed)

        # 4. BUTTON LED MAPPING
        # Default: Green (Connected)
        l_r, l_g, l_b = 0, 1, 0
        r_r, r_g, r_b = 0, 1, 0

        # Change colors based on face buttons
        if gamepad.buttons['cross']: # X Button (Blue)
            l_r, l_g, l_b = 0, 0, 1
            r_r, r_g, r_b = 0, 0, 1
        elif gamepad.buttons['circle']: # Circle Button (Red)
            l_r, l_g, l_b = 1, 0, 0
            r_r, r_g, r_b = 1, 0, 0
        elif gamepad.buttons['triangle']: # Triangle Button (Green)
            l_r, l_g, l_b = 0, 1, 0
            r_r, r_g, r_b = 0, 1, 0
        elif gamepad.buttons['square']: # Square Button (Pink/Purple)
            l_r, l_g, l_b = 1, 0, 1
            r_r, r_g, r_b = 1, 0, 1

        alvik.left_led.set_color(l_r, l_g, l_b)
        alvik.right_led.set_color(r_r, r_g, r_b)

        # Tiny delay to keep loop stable
        time.sleep(0.02) 

finally:
    print("Program Ended. Motors Stopped, LEDs Off.")
    alvik.set_wheels_speed(0, 0)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()