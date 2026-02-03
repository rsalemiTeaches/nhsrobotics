# Project 16: Remote Control Link & Button Test
# Version: V03
# FIX: Added "Waiting for Connection" loop to prevent immediate Blue LEDs.
# FEATURE: Mapped EVERY button to a unique LED color/position.

from arduino_alvik import ArduinoAlvik
# We import Controller from your library
from nhs_robotics import NanoLED, Controller
import machine
import ubinascii
import time

# --- CONFIGURATION ---
MAX_SPEED = 50  # RPM

# --- SETUP HARDWARE ---
alvik = ArduinoAlvik()
alvik.begin()

# NanoLED (Top Board)
nano_led = NanoLED()
nano_led.set_color(1, 1, 0) # Booting Yellow
nano_led.off() 

# --- WIFI SETUP ---
id_hex = ubinascii.hexlify(machine.unique_id()).decode()
MY_NAME = f"Alvik-{id_hex[-4:].upper()}"

print("--------------------------------")
print(f" WIFI CREATED:  {MY_NAME}")
print(f" PASSWORD:      password")
print(f" GO TO BROWSER: http://192.168.4.1")
print("--------------------------------")

ctl = Controller(ssid=MY_NAME)

# --- CRITICAL FIX: WAITING LOOP ---
# The robot will now Blink Yellow until the Controller says "Connected"
print("Waiting for connection...")
while not ctl.is_connected():
    alvik.left_led.set_color(1, 1, 0) # Yellow
    alvik.right_led.set_color(0, 0, 0)
    time.sleep(0.1)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(1, 1, 0)
    time.sleep(0.1)
    ctl.update()

# --- CONNECTION SUCCESS ---
print("Connected!")
# Default State: Green (Link Active)
alvik.left_led.set_color(0, 1, 0)
alvik.right_led.set_color(0, 1, 0)

try:
# --- MAIN LOOP ---
    while True:
        # 1. Update Data
        ctl.update()

        # 2. Safety Check (Link Lost?)
        if not ctl.is_connected():
            print("Link Lost!")
            # Blink Red until reconnected
            while not ctl.is_connected():
                alvik.left_led.set_color(1, 0, 0)
                alvik.right_led.set_color(0, 0, 0)
                time.sleep(0.1)
                alvik.left_led.set_color(0, 0, 0)
                alvik.right_led.set_color(1, 0, 0)
                time.sleep(0.1)
                ctl.update()
            print("Link Restored.")

        # 3. Drive Logic (Tank)
        alvik.set_wheels_speed(ctl.left_stick_y * MAX_SPEED, ctl.right_stick_y * MAX_SPEED)

        # 4. BUTTON LED MAPPING
        # Default: Green (Connected)
        l_r, l_g, l_b = 0, 1, 0
        r_r, r_g, r_b = 0, 1, 0

        # --- RIGHT SIDE (Controls Right LED) ---
        if ctl.buttons['cross']:    r_r, r_g, r_b = 1, 0, 0  # Red
        if ctl.buttons['circle']:   r_r, r_g, r_b = 1, 0, 1  # Purple
        if ctl.buttons['triangle']: r_r, r_g, r_b = 0, 0, 1  # Blue
        if ctl.buttons['square']:   r_r, r_g, r_b = 1, 1, 0  # Yellow
        if ctl.buttons['R1']:       r_r, r_g, r_b = 1, 1, 1  # White
        if ctl.buttons['R3']:       r_r, r_g, r_b = 0, 1, 1  # Cyan
        if ctl.buttons['options']:  break
        if ctl.buttons['R2']:       r_r, r_g, r_b = 1, 0.5, 0 # Orange (Digital Press)

        # --- LEFT SIDE (Controls Left LED) ---
        if ctl.buttons['down']:     l_r, l_g, l_b = 1, 0, 0  # Red
        if ctl.buttons['right']:    l_r, l_g, l_b = 1, 0, 1  # Purple
        if ctl.buttons['up']:       l_r, l_g, l_b = 0, 0, 1  # Blue
        if ctl.buttons['left']:     l_r, l_g, l_b = 1, 1, 0  # Yellow
        if ctl.buttons['L1']:       l_r, l_g, l_b = 1, 1, 1  # White
        if ctl.buttons['L3']:       l_r, l_g, l_b = 0, 1, 1  # Cyan
        if ctl.buttons['share']:    l_r, l_g, l_b = 0, 0, 0  # Off
        if ctl.buttons['L2']:       l_r, l_g, l_b = 1, 0.5, 0 # Orange (Digital Press)

        # --- CENTER ---
        if ctl.buttons['ps']:
            l_r, l_g, l_b = 1, 1, 1 # Both White
            r_r, r_g, r_b = 1, 1, 1

        # Apply Colors
        alvik.left_led.set_color(l_r, l_g, l_b)
        alvik.right_led.set_color(r_r, r_g, r_b)

        time.sleep(0.01)
finally:
    alvik.set_wheels_speed(0, 0)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    print("Program Ended. Motors Stopped, LEDs Off.")
    alvik.stop()
