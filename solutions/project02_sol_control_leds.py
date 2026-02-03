# ==========================================================
#                      Control the LEDs                     
#       In this project, you'll use the buttons on the      
#      back of the ALVIK to control the LEDs.  It works     
#                         like this:                        
#                  No button--Two blue LEDs                 
#                  Left--Left LED is green                 
#                  Right--Right LED is green                
#                  Up--Both LEDs are yellow                 
#                  Down--Both LEDs are purple
#                  Cancel--Stop Running                   
# ==========================================================
# Version: V01

# Import the ArduinoAlvik class and the sleep_ms() function
from arduino_alvik import ArduinoAlvik # get the alvik controller description
from time import sleep_ms

# Create a new ArduinoAlvik object named alvik
alvik = ArduinoAlvik() # get an alvik controller

try:
    alvik.begin() # Start the bot

    # Loop forever
    while True:
        
        # Check to see if the user pressed X (Cancel)
        if alvik.get_touch_cancel():
            break

        # Check to see if the LEFT ARROW is pushed
        # If the LEFT ARROW is pushed set the LEFT LED to GREEN
        if alvik.get_touch_left():
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 0, 0) # Keep other LED off for clarity

        # Check to see if the RIGHT ARROW is pushed
        # If the RIGHT ARROW is pushed set the RIGHT LED to GREEN 
        elif alvik.get_touch_right():
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 1, 0)

        # Check to see if the UP ARROW is pushed.
        # If the UP ARROW is pushed set both LEDS to Yellow (RED + GREEN)
        elif alvik.get_touch_up():
            alvik.left_led.set_color(1, 1, 0)
            alvik.right_led.set_color(1, 1, 0)

        # Check to see if the DOWN ARROW is pushed.
        # If the DOWN ARROW is pushed set both LEDS to PURPLE (RED + BLUE)
        elif alvik.get_touch_down():
            alvik.left_led.set_color(1, 0, 1)
            alvik.right_led.set_color(1, 0, 1)

        # No directional button--Two blue LEDs
        else:
            alvik.left_led.set_color(0, 0, 1)
            alvik.right_led.set_color(0, 0, 1)
        
        # Small delay to keep the processor from running too fast
        sleep_ms(10)

finally:
    # Cleanup: Stop the robot and turn off LEDs
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    alvik.stop()

# Developed with the assistance of Google Gemini
