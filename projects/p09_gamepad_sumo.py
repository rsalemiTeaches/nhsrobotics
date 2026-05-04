# Project 09: Gamepad Sumo (Student Scaffold)
# Target: Bare-Bones Tank Drive
from arduino_alvik import ArduinoAlvik
from wifi_controller import Controller
import ubinascii
import machine
import time

# --- SETUP ---

# 1. Initialize Robot
alvik = ArduinoAlvik()
alvik.begin()

# 2. Generate Unique Name for Wi-Fi (Based on hardware ID)
id_hex = ubinascii.hexlify(machine.unique_id()).decode()
MY_NAME = f"Alvik-{id_hex[-4:].upper()}"

# 3. Initialize Wi-Fi Controller
print(f"Starting Wi-Fi: {MY_NAME}")
ctl = Controller(ssid=MY_NAME, password="password")

# --- THE SILENT ERROR ---
# Troubleshooting: Is 1 RPM enough for a Sumo bot?
MAX_RPM = 1 

# --- WAITING FOR CONNECTION ---
print(f"Waiting for controller... Connect to {MY_NAME} and go to http://192.168.4.1")
while not ctl.is_connected():
    # Blink Yellow while waiting
    alvik.left_led.set_color(1, 1, 0)
    alvik.right_led.set_color(1, 1, 0)
    time.sleep(0.1)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    time.sleep(0.1)
    ctl.update()

print("Connected!")
alvik.left_led.set_color(0, 1, 0)
alvik.right_led.set_color(0, 1, 0)

# --- MAIN CONTROL LOOP ---
try:
    while True:
        # Update data from the web server
        ctl.update()

        # Safety Check: Stop motors if link is lost
        if not ctl.is_connected():
            alvik.set_wheels_speed(0, 0)
            while not ctl.is_connected():
                alvik.left_led.set_color(1, 0, 0) # Red Blink = Link Lost
                time.sleep(0.2)
                alvik.left_led.set_color(0, 0, 0)
                time.sleep(0.2)
                ctl.update()
            alvik.left_led.set_color(0, 1, 0) # Back to Green

        # --- WORK: TANK DRIVE LOGIC ---
        # 1. Calculate speeds by multiplying the stick (ctl.left_y) by MAX_RPM
        # Note: You may need to multiply by -1 if the robot drives backwards!
        
        left_speed = 0  # WORK: Insert your math here
        right_speed = 0 # WORK: Insert your math here

        # 2. Send the speeds to the motors
        # WORK: Use alvik.set_wheels_speed() to move your robot
        

except Exception as e:
    print(f"Error: {e}")

finally:
    # --- WORK: SAFETY SHUTDOWN ---
    # This ensures the robot stops even if your code crashes.
    alvik.brake()
    alvik.stop()
    print("Emergency Stop engaged.")
    # WORK: Call the appropriate Alvik methods to stop all movement
    