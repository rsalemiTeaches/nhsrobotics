from arduino_alvik import ArduinoAlvik
# Import the tools we need from our library
from nhs_robotics import Controller, Button 
import machine
import ubinascii
import time

# --- SETUP ---
# 1. Generate Unique Name for Wi-Fi
id_hex = ubinascii.hexlify(machine.unique_id()).decode()
MY_NAME = f"Alvik-{id_hex[-4:].upper()}"

# 2. Initialize Robot
alvik = ArduinoAlvik()
alvik.begin()
alvik.left_led.set_color(1, 1, 0) # Yellow = Waiting for Wi-Fi

# 3. Start Controller Server
print("--------------------------------")
print(f" WIFI CREATED:  {MY_NAME}")
print(" PASSWORD:      password")
print(" GO TO BROWSER: http://192.168.4.1")
print("--------------------------------")

ctl = Controller(ssid=MY_NAME)

# --- WAITING FOR CONNECTION ---
# Blink Yellow until the web page is open and sending data
print("Waiting for controller connection...")
while not ctl.is_connected():
    ctl.update() # Check for new data
    alvik.left_led.set_color(1, 1, 0) # Yellow
    time.sleep(0.1)
    alvik.left_led.set_color(0, 0, 0) # Off
    time.sleep(0.1)

# Connected! Turn Green.
print("Connected!")
alvik.left_led.set_color(0, 1, 0)
alvik.right_led.set_color(0, 1, 0)

# --- MAIN LOOP ---
while True:
    # 1. VITAL: Update the controller listener
    ctl.update()
    
    # 2. Check the 'cross' button directly
    if ctl.buttons['cross']:
        # If held, turn Green
        alvik.left_led.set_color(0, 1, 0)
        alvik.right_led.set_color(0, 1, 0)
    else:
        # If released, turn Blue (Idle)
        alvik.left_led.set_color(0, 0, 1)
        alvik.right_led.set_color(0, 0, 1)
        
    # Small delay to keep things running smoothly
    time.sleep(0.01)
