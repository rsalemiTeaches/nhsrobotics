######################
#     Project 02     #
#  Gamepad and LEDs  #
######################

# In Project 01, you told the robot exactly what to do and
# when to do it. But real robots need to "listen" to the
# outside world and react!

# Today, you will connect your phone or computer to the Alvik
# over Wi-Fi using the RobotGamepad. You will use "if" statements
# to change the LED colors based on which button you press!

from arduino_alvik import ArduinoAlvik
from nhs_robotics import RobotGamepad
from time import sleep_ms

alvik = ArduinoAlvik()

try:
    alvik.begin()

    # Create the gamepad. This will automatically start a Wi-Fi
    # Access Point. Look at the terminal for the IP address!
    gamepad = RobotGamepad(alvik)

    print("Ready! Connect to the robot's Wi-Fi network.")

    # The Polling Loop
    # We must constantly loop to "listen" for new button presses.
    while True:
        # Check if the X button on the robot is pressed to quit
        if alvik.get_touch_cancel():
            break
            
        # 1. LISTEN: Update the gamepad data over Wi-Fi
        gamepad.update()

        # 2. THINK & ACT: Check which button is pressed
        if gamepad.buttons['cross']:
            # If the X (cross) button is held down, turn Blue
            alvik.left_led.set_color(0, 0, 1)
            alvik.right_led.set_color(0, 0, 1)
            
        elif gamepad.buttons['circle']:
            # If the Circle button is held down, turn Red
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(1, 0, 0)
            
        elif gamepad.buttons['triangle']:
            # If the Triangle button is held down, turn Green
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
            
        else:
            # If NO buttons are held down, turn the LEDs off!
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)

        # A tiny delay gives the robot time to think before looping again.
        # FLEX: Change 20 to 1000. What happens to the gamepad?
        # (Hint: Robots can't listen while they are sleeping!)
        sleep_ms(20)

finally:
    print("Program Stopped.")
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()
