# Alvik Tower Test Program
# For Themes in Engineering - Project 03: The Robot Tower
#
# This program makes the Alvik robot perform a series of random but
# inherently tethered movements for 30 seconds. Each sequence involves
# moving out and back to the starting point before turning, ensuring
# the robot does not wander off the platform.

from arduino_alvik import ArduinoAlvik
from time import sleep_ms, ticks_ms, ticks_diff
import urandom

# --- Configuration Constants ---
RUN_DURATION_MS = 30000  # 30 seconds

# --- Randomization Limits (for each individual movement) ---
MIN_MOVE_CM = 4
MAX_MOVE_CM = 8  # Increased from 5
MIN_ROTATE_DEG = 30
MAX_ROTATE_DEG = 90
PAUSE_MS = 250

# --- New Speed Randomization Limits ---
MIN_DRIVE_SPEED_CM_S = 8
MAX_DRIVE_SPEED_CM_S = 25
MIN_ROTATE_SPEED_DEG_S = 45
MAX_ROTATE_SPEED_DEG_S = 200

alvik = ArduinoAlvik()

try:
    alvik.begin()

    # Wait for the OK button to be pressed before starting the test.
    print("Ready for tower test. Press OK to begin.")
    while not alvik.get_touch_ok():
        alvik.left_led.set_color(0, 0, 1); alvik.right_led.set_color(0, 0, 1)
        sleep_ms(200)
        alvik.left_led.set_color(0, 0, 0); alvik.right_led.set_color(0, 0, 0)
        sleep_ms(200)
        if alvik.get_touch_cancel(): raise KeyboardInterrupt

    print("Starting 30-second test with tethered random movements...")
    alvik.left_led.set_color(0, 1, 0); alvik.right_led.set_color(0, 1, 0)

    start_time = ticks_ms()

    while ticks_diff(ticks_ms(), start_time) < RUN_DURATION_MS:
        
        # --- "THERE AND BACK AGAIN" SEQUENCE ---
        
        # 1. Linear Movement Phase
        move_dist = urandom.randint(MIN_MOVE_CM, MAX_MOVE_CM)
        move_speed = urandom.randint(MIN_DRIVE_SPEED_CM_S, MAX_DRIVE_SPEED_CM_S)
        # To use a variable speed, we must calculate the duration of the move.
        # duration (sec) = distance (cm) / speed (cm/s)
        duration_ms = int((move_dist / move_speed) * 1000)
        
        # Randomly decide to go forward first or backward first
        if urandom.randint(0, 1) == 0:
            print(f"Sequence: Forward {move_dist}cm at {move_speed}cm/s, then Backward")
            alvik.drive(move_speed, 0)
            sleep_ms(duration_ms)
            alvik.brake()
            sleep_ms(PAUSE_MS)
            alvik.drive(-move_speed, 0)
            sleep_ms(duration_ms)
            alvik.brake()
        else:
            print(f"Sequence: Backward {move_dist}cm at {move_speed}cm/s, then Forward")
            alvik.drive(-move_speed, 0)
            sleep_ms(duration_ms)
            alvik.brake()
            sleep_ms(PAUSE_MS)
            alvik.drive(move_speed, 0)
            sleep_ms(duration_ms)
            alvik.brake()
            
        sleep_ms(PAUSE_MS)

        # 2. Rotational Phase
        turn_angle = urandom.randint(MIN_ROTATE_DEG, MAX_ROTATE_DEG)
        turn_speed = urandom.randint(MIN_ROTATE_SPEED_DEG_S, MAX_ROTATE_SPEED_DEG_S)
        # duration (sec) = angle (deg) / speed (deg/s)
        duration_ms = int((turn_angle / turn_speed) * 1000)

        # Randomly decide to turn left or right
        if urandom.randint(0, 1) == 0:
            print(f"Sequence: Turn Left {turn_angle} deg at {turn_speed}deg/s")
            alvik.drive(0, turn_speed) # Positive angular speed is counter-clockwise (left)
            sleep_ms(duration_ms)
            alvik.brake()
        else:
            print(f"Sequence: Turn Right {turn_angle} deg at {turn_speed}deg/s")
            alvik.drive(0, -turn_speed) # Negative angular speed is clockwise (right)
            sleep_ms(duration_ms)
            alvik.brake()

        sleep_ms(PAUSE_MS)

        # Check for cancel button press to allow early exit
        if alvik.get_touch_cancel():
            break

    print("Test complete!")

finally:
    print("Stopping robot.")
    alvik.stop()

