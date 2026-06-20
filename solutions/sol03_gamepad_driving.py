######################
#     Project 03     #
#  Gamepad Driving   #
######################

# You've mastered digital inputs (buttons that are True or False).
# Now it's time for analog inputs! The joysticks on your gamepad 
# don't just return True or False; they return a decimal number
# between -1.0 (all the way down) and 1.0 (all the way up).

# We will use these decimal numbers to calculate the exact speed
# we want our wheels to turn.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
from time import sleep_ms

alvik = ArduinoAlvik()

try:
    alvik.begin()

    # The engineers who built the Alvik determined its motors 
    # max out at exactly 70 Revolutions Per Minute.
    # In programming, we store important physical limits like 
    # this in ALL_CAPS variables called Constants.
    MAX_SPEED = 70.0

    gamepad = RobotGamepad(alvik)

    print("Ready! Connect to the robot's Wi-Fi network.")

    while True:
        # Check for exit button
        if alvik.get_touch_cancel():
            break
            
        # 1. LISTEN: Update gamepad data
        gamepad.update()

        # 2. THINK: Calculate speeds
        # The joystick gives us a decimal between -1.0 and 1.0.
        # If we push it all the way up, 1.0 * 70 = 70 RPM!
        # If we push it halfway up, 0.5 * 70 = 35 RPM!
        
        # We also create a "Slow Mode" to make precise driving easier.
        # If the user holds the R1 button (right bumper), we cut the 
        # MAX_SPEED in half!
        if gamepad.buttons['R1']:
            current_max = MAX_SPEED / 2
        else:
            current_max = MAX_SPEED

        left_speed = gamepad.left_y * current_max
        right_speed = gamepad.right_y * current_max

        # 3. ACT: Send the speeds to the motors
        alvik.set_wheels_speed(left_speed, right_speed)

        # FLEX: Add a "Turbo Mode" instead of a Slow Mode! 
        # Change MAX_SPEED to 35 so the robot drives slowly by default.
        # Then, modify the "if" statement so that holding a button
        # makes the robot drive at the true maximum of 70.0 RPM.

        # Give the robot time to think before looping again.
        sleep_ms(20)

finally:
    print("Program Stopped.")
    alvik.set_wheels_speed(0, 0) # Make sure the robot doesn't keep driving!
    alvik.stop()
