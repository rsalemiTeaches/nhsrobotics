# Project 16: Remote Control Link
# Architecture: Controller (Driver) -> Lambda Bridge -> Button Class (Logic)

from arduino_alvik import ArduinoAlvik
from controller import Controller
from button_class import Button 
from nanoled import NanoLED 
import machine
import ubinascii
import time

# --- SETUP ---
# 1. Generate Unique Name
id_hex = ubinascii.hexlify(machine.unique_id()).decode()
MY_NAME = f"Alvik-{id_hex[-4:].upper()}"

alvik = ArduinoAlvik()
alvik.begin()
alvik.left_led.set_color(1, 1, 0) # Yellow = Booting

# 2. Setup NanoLED
nano_led = NanoLED()
# Use set_color(1, 1, 0) just like the Alvik LEDs!
# We set it to Yellow so we can dim/brighten it later.
nano_led.set_color(1, 1, 0) 
nano_led.off() 

# 3. Start Controller
print("--------------------------------")
print(f" WIFI CREATED:  {MY_NAME}")
print(f" PASSWORD:      password")
print(f" GO TO BROWSER: http://192.168.4.1")
print("--------------------------------")

ctl = Controller(ssid=MY_NAME)
ctl.begin()

# 4. Create Button Objects (THE LAMBDA BRIDGE)
cross_btn    = Button(lambda: ctl.buttons['cross'])
triangle_btn = Button(lambda: ctl.buttons['triangle'])
bumper_R1    = Button(lambda: ctl.buttons['R1'])
up_btn       = Button(lambda: ctl.buttons['up'])

print("Ready! Connect Chromebook to WiFi.")
alvik.left_led.set_color(0, 0, 1) 
alvik.right_led.set_color(0, 0, 1)

# --- MAIN LOOP ---
while True:
    ctl.update()
    
    # A. Driving
    speed_L = ctl.left_stick_y * 50
    speed_R = ctl.right_stick_y * 50
    alvik.set_wheels_speed(speed_L, speed_R)
    
    # B. Analog Brightness
    if ctl.R2 < 0.05:
        nano_led.off()
    else:
        brightness_percent = int(ctl.R2 * 100)
        nano_led.set_brightness(brightness_percent)
    
    # C. Events
    if cross_btn.get_touch():
        print("ACTION: Red Headlights")
        alvik.left_led.set_color(1, 0, 0)
        alvik.right_led.set_color(1, 0, 0)

    if triangle_btn.get_touch():
        print("ACTION: Green LEDs")
        alvik.left_led.set_color(0, 1, 0) 
        alvik.right_led.set_color(0, 1, 0)
        # NanoLED match (Green)
        nano_led.set_color(0, 1, 0)
        
    if bumper_R1.get_touch():
        print("ACTION: Blue LEDs")
        alvik.left_led.set_color(0, 0, 1)
        alvik.right_led.set_color(0, 0, 1)
        # NanoLED match (Blue)
        nano_led.set_color(0, 0, 1)

    if up_btn.get_touch():
        print("ACTION: Purple LEDs")
        # Purple = Red + Blue
        alvik.left_led.set_color(1, 0, 1)
        alvik.right_led.set_color(1, 0, 1)
        # NanoLED match (Purple)
        nano_led.set_color(1, 0, 1)
        
    time.sleep(0.01)
    