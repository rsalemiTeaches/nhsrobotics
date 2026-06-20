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
        # IMPORTANT: Sleep for 10 ms so that the robot 
        # has time to process the button presses.
        sleep_ms(10)
                
# --- Input Check ---
        if alvik.get_touch_cancel():
            print("Cancel button pressed.")
            break
# --- Distance Logic ---
        # Using the SuperBot wrapper method as requested
        closest_distance = sb.get_closest_distance()
        if closest_distance < STOP_DISTANCE:
            # Stop the robot and turn LEDs RED
            alvik.set_wheels_speed(0, 0)
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
        else:
            # Drive forward and turn LEDs GREEN
            alvik.set_wheels_speed(DRIVE_SPEED, DRIVE_SPEED)
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
        sleep_ms(50)
finally:
# --- Shutdown ---
    print("Stopping robot.")
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.brake()  # Stops the robot
    alvik.stop()   # Kills the threads
# Developed with the assistance of Google Gemini
