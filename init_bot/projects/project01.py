######################
#     Project 01a    #
#  Flashin the LEDs  #
######################

# Welcome to your first robot program.  You are
# writing these programs in MicroPython. If you
# have never programmed before, you should look at
# my programming materials.

# In this program, we're going to make the LEDs on
# the Alvik turn on and off.  We're going to turn
# the left LED to RED and the right one to GREEN. Then
# we will swap them.  Then we'll turn them both
# to the combination of RED and GREEN which gives us
# YELLOW.

# This program runs until the user presses the X button
# on the Alvik.  This is called the "cancel" button.

# Our program needs to talk to the Alvik and measure
# time.  We get resources such as these by using the
# "from" statement to "import" things from modules.

# First we will use "from" to import the ArduinoAlvik
# class.  Then we'll use "from to import the sleep_ms()
# function.

from arduino_alvik import ArduinoAlvik # Get the ArduinoAlvik controller
from time import sleep_ms # get the sleep_ms function

alvik = ArduinoAlvik() # Store a new Alvik controller in alvik

try:
  alvik.begin()  # Start the robot (pressing the start button)

  # The "while True" statement loops until we break out of it.
  # We check the CANCEL buttton 
  # which means that we loop as long as the user is not touching
  # the X button on the Alvik.

  while True:   # Checking that the X button is not pressed
    # indent in Python to be in a loop.

    if (alvik.get_touch_cancel()):
      break

    # alvik.left_led.set_color(RED, GREEN, BLUE) sets the
    # left LED to RED, GREEN, BLUE, or a combination of them.
    # alvik.left_led.set_color(1, 0, 0) sets the left LED
    # to RED.
    # alvik.right_led.set_color(0, 1, 0) sets the right LED
    # to GREEN.
    
    alvik.left_led.set_color(1, 0, 0)
    alvik.right_led.set_color(0, 1, 0)
    # Delay for 1/2 a second (500 milliseconds) so we can
    # see that the LEDs are lit.
    sleep_ms(500)

  # NOW you add code to set the LEDs to other colors.

    # WORK: First, set the left LED to GREEN and the right LED to RED
    # SLeep 500 milliseconds.


    # WORK: Now set the left and right LED to YELLOW by turning
    # on both the RED and GREEN LEDs at the same time.
    # Sleep 500 ms

    # WORK: Turn off both LEDs by setting all the colors to 0
    # WORK: Sleep 500 ms

finally:
  alvik.stop()  # Stop the robot when someone presses the
                # X button or there is an interrupt.



