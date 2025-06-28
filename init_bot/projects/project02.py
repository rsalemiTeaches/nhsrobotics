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

# WORK Create a new ArduinoAlvik object named bot

alvik.begin() # Start the bot

# Loop while alvik.get_touch_cancel() returns false
while not alvik.get_touch_cancel():
  # Turn off both LEDs
  alvik.right_led.set_color(0,0,1)
  alvik.left_led.set_color(0,0,1)
  # If the left button is pushed, set the left LED to green.
  if alvik.get_touch_left():
    alvik.left_led.set_color(0,1,0)
  # WORK If the right button is pushed, set the right LED to green

  # WORK If the UP button is pushed set both LEDs to Yellow
  # (RED, GREEN, OFF)

  # WORK If the DOWN button is pushed set both LEDs to Purple
  # (RED, OFF, BLUE)


  # WORK: Sleep for 10 ms


# WORK  When you are out of the loop 
# turn off both LED and stop the robot.

alvik.stop()
