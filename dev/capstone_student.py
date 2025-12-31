# Capstone Project: Autonomous Warehouse Robot
# Student Name: [Student Name Here]
# Version: V02
#
# Goal:
# 1. Start on the "Home" area.
# 2. Find and Align with the AprilTag on the box.
# 3. Drive up to the box and pick it up.
# 4. Turn around 180 degrees.
# 5. Drive back until you see the black line (Warehouse Edge).
# 6. Drop the box.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import Button
from forklift_bot import ForkLiftBot
import time
import sys

# --- Configuration ---
# Distances
ALIGN_DIST = 25.0    # How far away to stop when aligning
PICKUP_DIST = 8.0    # How close to get to the box
BOX_ID = 1           # The ID of the AprilTag on the box

# Speeds
APPROACH_SPEED = 5   # Go slow when approaching the box
RETURN_SPEED = 15    # Go faster when bringing it back

# Line Sensor Threshold
# Since the floor is white and the line is black tape:
# White is LOW (< 500), Black is HIGH (> 500)
BLACK_LINE_THRESHOLD = 500 

# --- State Machine Definitions ---
# We use numbers for states, just like in the Line Racer project.
STATE_IDLE = 0
STATE_ALIGN = 1
STATE_APPROACH = 2
STATE_LIFT = 3
STATE_RETURN_SPIN = 4
STATE_RETURN_DRIVE = 5
STATE_DROP = 6
STATE_DONE = 7
STATE_ERROR = 99

# --- Setup ---
alvik = ArduinoAlvik()
alvik.begin()

# We use the special ForkLiftBot class
forklift = ForkLiftBot(alvik)
forklift.enable_info_logging() # Turn on the screen messages

# Check if the camera is working
if forklift.husky is None:
    forklift.log_error("Camera Error!")
    while True:
        # Flash Red light forever
        forklift.bot.left_led.set_color(1, 0, 0)
        time.sleep(0.5)
        forklift.bot.left_led.set_color(0, 0, 0)
        time.sleep(0.5)

# Buttons
start_button = Button(forklift.bot.get_touch_center)
cancel_button = Button(forklift.bot.get_touch_cancel)

# Start in IDLE state
current_state = STATE_IDLE

print("Capstone Project Loaded.")

# --- Main Loop ---
try:
    while True:
        # Always allow us to exit
        if cancel_button.get_touch():
            break

        # ----------------------------------------------------------------
        # STATE 0: IDLE (Waiting to start)
        # ----------------------------------------------------------------
        if current_state == STATE_IDLE:
            forklift.update_display("Ready...", "Press Center")
            
            # Blink Blue lights like in previous projects
            forklift.bot.left_led.set_color(0, 0, 1)
            forklift.bot.right_led.set_color(0, 0, 1)
            time.sleep(0.2)
            forklift.bot.left_led.set_color(0, 0, 0)
            forklift.bot.right_led.set_color(0, 0, 0)
            time.sleep(0.2)
            
            if start_button.get_touch():
                forklift.log_info("Starting!")
                forklift.lower_fork() # Make sure fork is down
                current_state = STATE_ALIGN

        # ----------------------------------------------------------------
        # STATE 1: ALIGN (Find the tag and face it)
        # ----------------------------------------------------------------
        elif current_state == STATE_ALIGN:
            forklift.log_info("Aligning...")
            
            # Use the helper function to align
            # It returns True if it worked, False if it failed
            result = forklift.align_to_tag(target_id=BOX_ID, align_dist=ALIGN_DIST)
            
            if result == True:
                forklift.log_info("Aligned!")
                current_state = STATE_APPROACH
            else:
                forklift.log_error("Tag not found!")
                current_state = STATE_ERROR

        # ----------------------------------------------------------------
        # STATE 2: APPROACH (Drive to the box)
        # ----------------------------------------------------------------
        elif current_state == STATE_APPROACH:
            forklift.log_info("Approaching...")
            
            # Use the helper function to drive to the box
            # We use 'blocking=True' so it waits until it finishes
            result = forklift.approach_tag(
                target_id=BOX_ID, 
                stop_distance=PICKUP_DIST, 
                speed=APPROACH_SPEED,
                blocking=True
            )
            
            if result == True:
                forklift.log_info("At the box.")
                current_state = STATE_LIFT
            else:
                forklift.log_error("Lost the box!")
                current_state = STATE_ERROR

        # ----------------------------------------------------------------
        # STATE 3: LIFT (Pick it up)
        # ----------------------------------------------------------------
        elif current_state == STATE_LIFT:
            forklift.log_info("Lifting...")
            # Note: raise_fork is now blocking, so we don't need time.sleep()
            forklift.raise_fork(10) # 10 is max height
            current_state = STATE_RETURN_SPIN

        # ----------------------------------------------------------------
        # STATE 4: SPIN (Turn around)
        # ----------------------------------------------------------------
        elif current_state == STATE_RETURN_SPIN:
            forklift.log_info("Turning around...")
            forklift.bot.rotate(180) # Simple 180 turn
            time.sleep(0.5)
            current_state = STATE_RETURN_DRIVE

        # ----------------------------------------------------------------
        # STATE 5: RETURN (Drive until line)
        # ----------------------------------------------------------------
        elif current_state == STATE_RETURN_DRIVE:
            forklift.log_info("Driving home...")
            
            # Start driving forward
            forklift.bot.drive(RETURN_SPEED, 0)
            
            # Loop until we see the line
            while True:
                # Read sensors
                l, c, r = forklift.bot.get_line_sensors()
                
                # Check if ANY sensor sees the black line (> 500)
                if l > BLACK_LINE_THRESHOLD or c > BLACK_LINE_THRESHOLD or r > BLACK_LINE_THRESHOLD:
                    forklift.bot.brake() # STOP!
                    forklift.log_info("Home found!")
                    break # Exit the loop
                
                time.sleep(0.01) # Short delay
            
            current_state = STATE_DROP

        # ----------------------------------------------------------------
        # STATE 6: DROP
        # ----------------------------------------------------------------
        elif current_state == STATE_DROP:
            forklift.log_info("Dropping...")
            forklift.lower_fork()
            time.sleep(1.0)
            current_state = STATE_DONE

        # ----------------------------------------------------------------
        # STATE 7: DONE (Celebrate!)
        # ----------------------------------------------------------------
        elif current_state == STATE_DONE:
            forklift.log_info("Success!")
            forklift.bot.left_led.set_color(0, 1, 0) # Green
            forklift.bot.right_led.set_color(0, 1, 0)
            time.sleep(2)
            current_state = STATE_IDLE # Go back to start

        # ----------------------------------------------------------------
        # STATE 99: ERROR (Failure)
        # ----------------------------------------------------------------
        elif current_state == STATE_ERROR:
            forklift.bot.left_led.set_color(1, 0, 0) # Red
            forklift.bot.right_led.set_color(1, 0, 0)
            time.sleep(2)
            current_state = STATE_IDLE

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    forklift.bot.stop()

# Developed with the assistance of Google Gemini