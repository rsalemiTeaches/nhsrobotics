from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
import time

# 1. Initialize Robot
alvik = ArduinoAlvik()
alvik.begin()

alvik.set_servo_positions(180,180)

# 2. Initialize Wi-Fi Controller
gamepad = RobotGamepad(alvik)
MAX_SPEED = 100.0 # 100% speed multiplier

kick_start_time = 0
is_kicking = False

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
            if not is_kicking:
                alvik.set_servo_positions(0,0)
                kick_start_time = time.ticks_ms()
                is_kicking = True
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

        # Check kick timeout (1000ms) to return to rest position
        if is_kicking and time.ticks_diff(time.ticks_ms(), kick_start_time) > 1000:
            alvik.set_servo_positions(180, 180)
            is_kicking = False

        alvik.left_led.set_color(l_r, l_g, l_b)
        alvik.right_led.set_color(r_r, r_g, r_b)

        # Tiny delay to keep loop stable
        time.sleep(0.02) 

except KeyboardInterrupt:
    print("Program stopped by user.")
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    print("Program Ended. Motors Stopped, LEDs Off.")
    alvik.set_wheels_speed(0, 0)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)