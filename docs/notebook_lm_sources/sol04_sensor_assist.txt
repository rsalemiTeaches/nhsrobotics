######################
#     Project 04     #
#   Sensor Assist    #
######################

# Up until now, the robot has only listened to YOU. If you told it
# to drive into a wall, it would drive into a wall!
#
# Real robots combine Human Input (the gamepad) with Sensor Input
# (the Time-of-Flight distance sensors) to make safe decisions.
#
# This program introduces the "SuperBot" library, which makes reading
# the robot's many sensors incredibly easy!

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot, RobotGamepad
from time import sleep_ms

alvik = ArduinoAlvik()

try:
    alvik.begin()

    # The SuperBot library gives us easy commands like get_closest_distance()
    bot = SuperBot(alvik)
    gamepad = RobotGamepad(alvik)
    
    print("Ready! Connect to the robot's Wi-Fi network.")

    MAX_SPEED = 70.0

    while True:
        if alvik.get_touch_cancel():
            break
            
        # ==========================================
        # 1. SENSE (Gather all data)
        # ==========================================
        gamepad.update()
        
        # SuperBot checks all the distance sensors and returns the closest one in cm
        distance_cm = bot.get_closest_distance()

        # ==========================================
        # 2. THINK (Make decisions based on data)
        # ==========================================
        
        # Sensor Override Logic:
        if distance_cm < 15.0:
            # Turn LEDs red to warn the driver!
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            
            # FLEX SOLUTION IMPLEMENTED:
            # Calculate the intended speeds first
            left_speed = gamepad.left_y * MAX_SPEED
            right_speed = gamepad.right_y * MAX_SPEED
            
            # Only stop the wheels if the user is trying to drive FORWARD!
            # If the speed is positive (forward), force it to 0.
            # If it's negative (backward), let it through so they can escape!
            if left_speed > 0:
                left_speed = 0.0
            if right_speed > 0:
                right_speed = 0.0
                
        else:
            # The path is clear! Let the user drive normally.
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
            
            # Calculate normal speeds
            left_speed = gamepad.left_y * MAX_SPEED
            right_speed = gamepad.right_y * MAX_SPEED

        # ==========================================
        # 3. ACT (Send commands to the hardware)
        # ==========================================
        alvik.set_wheels_speed(left_speed, right_speed)

        # FLEX: The code currently stops the robot from driving AT ALL if 
        # it is near a wall. Can you modify the math so it only stops you 
        # from driving FORWARD into the wall, but still lets you drive 
        # backward to escape? (Hint: check if gamepad.left_y is positive).

        sleep_ms(20)

finally:
    print("Program Stopped.")
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
