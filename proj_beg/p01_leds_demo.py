######################
#     Project 01a    #
#  Flashin the LEDs  #
#  (Demonstration)   #
######################

from arduino_alvik import ArduinoAlvik # Get the ArduinoAlvik controller
from time import sleep_ms # get the sleep_ms function

alvik = ArduinoAlvik() # Store a new Alvik controller in alvik

try:
  alvik.begin()  # Start the robot (pressing the start button)

  while True:   # Checking that the X button is not pressed
    if (alvik.get_touch_cancel()):
      break

    # 1. Red Left, Green Right
    alvik.left_led.set_color(1, 0, 0)
    alvik.right_led.set_color(0, 1, 0)
    sleep_ms(500)

    # 2. Green Left, Red Right
    alvik.left_led.set_color(0, 1, 0)
    alvik.right_led.set_color(1, 0, 0)
    sleep_ms(500)

    # 3. Both Yellow (Red + Green)
    alvik.left_led.set_color(1, 1, 0)
    alvik.right_led.set_color(1, 1, 0)
    sleep_ms(500)

    # 4. Both Off
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    sleep_ms(500)

finally:
  alvik.stop()  # Stop the robot
