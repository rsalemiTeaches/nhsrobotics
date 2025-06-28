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
from arduino_alvik import ArduinoAlvik
from time import sleep_ms

# WORK Create a new ArduinoAlvik object named bot
alvik = ArduinoAlvik()

try:
  alvik.begin() # Start the bot

  # Loop while alvik.get_touch_cancel() returns false
  while True:
    
    # Check to see if the user pressed X
    if alvik.get_touch_cancel():
      break

    # Turn off both LEDs
    alvik.right_led.set_color(0,0,1)
    alvik.left_led.set_color(0,0,1)
    # If the left button is pushed, set the left LED to green.
    if alvik.get_touch_left():
      alvik.left_led.set_color(0,1,0)
    # WORK If the right button is pushed, set the right LED to green
    if alvik.get_touch_right():
      alvik.right_led.set_color(0,1,0)
    # WORK If the UP button is pushed set both LEDs to Yellow
    # (RED, GREEN, OFF)
    if alvik.get_touch_up():
      alvik.right_led.set_color(1,1,0)
      alvik.left_led.set_color(1,1,0)
    # WORK If the DOWN button is pushed set both LEDs to Purple
    # (RED, OFF, BLUE)
    if alvik.get_touch_down():
      alvik.right_led.set_color(1,0,1)
      alvik.left_led.set_color(1,0,1)
    
    # WORK: Sleep for 10 ms
    sleep_ms(10)
finally:
  # WORK  When you are out of the loop 
  # or there is an interruption
  # turn off both LEDs and stop the robot.
  alvik.right_led.set_color(0,0,0)
  alvik.left_led.set_color(0,0,0)
  alvik.stop()
