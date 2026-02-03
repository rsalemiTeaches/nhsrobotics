#########################
#       Project 04      #
#     Obstacle Stop     #
#########################
# Version: V01
# --- Imports ---
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms
# --- Initialization ---
alvik = ArduinoAlvik()
sb = SuperBot(alvik)
# --- Configuration ---
DRIVE_SPEED = 30     # Speed in RPM
STOP_DISTANCE = 10   # Stop distance in cm
try:
# --- Robot Startup ---
    alvik.begin()
    print("Project 04: Obstacle Stop Started.")
    print(f"Driving forward; stopping within {STOP_DISTANCE}cm.")
    while True:
# --- Input Check ---
        if alvik.get_touch_cancel():
            print("Cancel button pressed.")
            break
# --- Distance Logic ---
        # WORK: Use the sb object to get the closest distance
        closest_distance = 0 
        if closest_distance < STOP_DISTANCE:
            # WORK: Stop the robot and turn LEDs RED
            pass
        else:
            # WORK: Drive the robot forward and turn LEDs GREEN
            pass
        sleep_ms(50)
finally:
# --- Shutdown ---
    print("Stopping robot.")
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    # WORK: Use alvik.brake() to stop the wheels
    # WORK: Use the correct method to kill the background threads
# Developed with the assistance of Google Gemini
