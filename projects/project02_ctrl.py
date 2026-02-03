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


# WORK Import the ArduinoAlvik class and the sleep_ms() function
from arduino_alvik import ArduinoAlvik #get the alvik controller description
from time import sleep_ms

# WORK Create a new ArduinoAlvik object named bot
alvik = ArduinoAlvik() # get an alvik controller

try:
  alvik.begin() # Start the bot

  # Loop forever
  while True:
    
    # Check to see if the user pressed X
    if alvik.get_touch_cancel():
      break


    # Check to see if the LEFT ARROW is pushed
    # If the LEFT ARROW is upushed set the LEFT
    # LED to GREEN

    if alvik.get_touch_left():
      alvik.left_led.set_color(0,1,0)
    # WORK: Check to see if the RIGHT ARROW is pushed
    # WORK: If the RIGHT ARROW is pushed set the
    # WORK RIGHT LED to GREEN 
    # elif alvik.get_touch_right():
    #  alvik.right_led.set_color(0,1,0)

    # WORK: Check to see if the UP ARROW is pushed.
    # WORK: If the UP ARROW is pushed set both 
    # WORK: LEDS to Yellow (RED, GREEN, OFF)


    # WORK: Check to see if the DOWN ARROW is pushed.
    # WORK: If the DOWN ARROW is pushed set both 
    # WORK: LEDS to PURPLE (RED, OFF, BLUE)

    # Set both LEDs to BLUE
    else:
      alvik.right_led.set_color(0,0,1)
      alvik.left_led.set_color(0,0,1)
    
    # WORK: Sleep for 10 ms

finally:
  # WORK  When you are out of the loop 
  # or there is an interruption
  # turn off both LEDs and stop the robot.
  pass