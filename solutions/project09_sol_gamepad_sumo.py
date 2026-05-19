from arduino_alvik import ArduinoAlvik
from controller import Controller
import time
import ubinascii
import machine

# 1. Initialize Robot
alvik = ArduinoAlvik()
alvik.begin()

# 2. Initialize Wi-Fi Controller
print("Starting Wi-Fi Access Point...")
ssid = "Alvik-"+ubinascii.hexlify(machine.unique_id()).decode('utf-8').upper()[-4:]
ctl = Controller(ssid=ssid, password="password")
MAX_SPEED = 1.0 # 100% speed multiplier

print("Waiting for connection... Connect phone and press a button.")

# --- WAIT FOR HANDSHAKE ---


print("Connected!")

try:
    # --- MAIN LOOP ---
    while True:
        # Update Data from Wi-Fi
        ctl.update()


        # Drive Logic (Tank Drive)
        # Using the correct variable names from our V50 wifi_controller
        left_speed = ctl.left_y * MAX_SPEED
        right_speed = ctl.right_y * MAX_SPEED
        alvik.set_wheels_speed(left_speed, right_speed)

        # 4. BUTTON LED MAPPING
        # Default: Green (Connected)
        l_r, l_g, l_b = 0, 1, 0
        r_r, r_g, r_b = 0, 1, 0

        # Change colors based on face buttons
        if ctl.buttons['cross']: # X Button (Blue)
            l_r, l_g, l_b = 0, 0, 1
            r_r, r_g, r_b = 0, 0, 1
        elif ctl.buttons['circle']: # Circle Button (Red)
            l_r, l_g, l_b = 1, 0, 0
            r_r, r_g, r_b = 1, 0, 0
        elif ctl.buttons['triangle']: # Triangle Button (Green)
            l_r, l_g, l_b = 0, 1, 0
            r_r, r_g, r_b = 0, 1, 0
        elif ctl.buttons['square']: # Square Button (Pink/Purple)
            l_r, l_g, l_b = 1, 0, 1
            r_r, r_g, r_b = 1, 0, 1

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
