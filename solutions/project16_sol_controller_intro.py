# Project 16: Remote Control Link
# Version: V01
# Created with the help of Gemini Pro
#
# MISSION:
# 1. Create a WiFi Hotspot with a unique name.
# 2. Wait for a Chromebook to connect (Blinking Yellow).
# 3. When connected (Green), drive the robot using the PS4 controller.
# 4. Use the Gamepad API to control Motors, LEDs, and Brightness.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import NanoLED, Button, Controller
import machine
import ubinascii
import time

# --- CONFIGURATION ---
MAX_SPEED = 50  # RPM

# --- SETUP HARDWARE ---
# 1. Initialize Robot
alvik = ArduinoAlvik()
alvik.begin()

# 2. Initialize NanoLED (the RGB LED on the board)
nano_led = NanoLED()
nano_led.set_color(1, 1, 0) 
nano_led.off() 

# 3. Generate Unique WiFi Name
# This ensures every student has a unique SSID (e.g., "Alvik-A1B2")
id_hex = ubinascii.hexlify(machine.unique_id()).decode()
MY_NAME = f"Alvik-{id_hex[-4:].upper()}"

print("--------------------------------")
print(f" WIFI CREATED:  {MY_NAME}")
print(f" PASSWORD:      password")
print(f" GO TO BROWSER: http://192.168.4.1")
print("--------------------------------")

# 4. Start the Web Controller
# We use the Singleton pattern, so this is safe even if called twice
ctl = Controller(ssid=MY_NAME)
ctl.begin()

# 5. Define Controller Buttons (The "Lambda Bridge")
# We map the text names from the controller to our Button class
cross_btn    = Button(lambda: ctl.buttons['cross'])
triangle_btn = Button(lambda: ctl.buttons['triangle'])
bumper_R1    = Button(lambda: ctl.buttons['R1'])
bumper_L1    = Button(lambda: ctl.buttons['L1'])

# --- PHASE 1: THE WAITING ROOM ---
print("Waiting for Link...")
blink_state = False

# Stay inside this loop until the browser connects
while not ctl.is_connected():
    ctl.update() # Check for incoming data
    
    # Blink Yellow Logic
    if blink_state:
        alvik.left_led.set_color(1, 1, 0)  # Yellow
        alvik.right_led.set_color(1, 1, 0)
    else:
        alvik.left_led.set_color(0, 0, 0)  # Off
        alvik.right_led.set_color(0, 0, 0)
        
    blink_state = not blink_state
    time.sleep(0.1)

# Connection Successful!
print("Link Active! Driving Mode Engaged.")
alvik.left_led.set_color(0, 1, 0) # Green
alvik.right_led.set_color(0, 1, 0)

# --- PHASE 2: MAIN CONTROL LOOP ---
try:
    while True:
        # 1. Update Data
        ctl.update()
        
        # 2. Safety Check: Is the controller still there?
        if not ctl.is_connected():
            # STOP EVERYTHING!
            alvik.set_wheels_speed(0, 0)
            print("Link Lost! Waiting...")
            
            # Go back to blinking yellow until reconnected
            while not ctl.is_connected():
                ctl.update()
                alvik.left_led.set_color(1, 0, 0) # Red flash for error
                alvik.right_led.set_color(0, 0, 0)
                time.sleep(0.1)
                alvik.left_led.set_color(0, 0, 0)
                alvik.right_led.set_color(1, 0, 0)
                time.sleep(0.1)
            
            # Reconnected
            print("Link Restored.")
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
        
        # 3. Tank Drive Logic
        # Left Stick Y controls Left Wheel, Right Stick Y controls Right Wheel
        speed_L = ctl.left_stick_y * MAX_SPEED
        speed_R = ctl.right_stick_y * MAX_SPEED
        alvik.set_wheels_speed(speed_L, speed_R)
        
        # 4. Analog Brightness (NanoLED)
        # R2 Trigger is 0.0 to 1.0
        if ctl.R2 < 0.05:
            nano_led.off()
        else:
            brightness_percent = int(ctl.R2 * 100)
            nano_led.set_brightness(brightness_percent)
        
        # 5. Button Events
        # Toggle Headlights with Cross
        if cross_btn.get_touch():
            print("Headlights: RED")
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)

        # Toggle Headlights with Triangle
        if triangle_btn.get_touch():
            print("Headlights: GREEN")
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)

except KeyboardInterrupt:
    print("Program Stopped.")
finally:
    alvik.stop()
    nano_led.off()

