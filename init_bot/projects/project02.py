# Flash the LEDs

#################################
#    Project 01b                #
# Controlling LEDs with buttons #
#################################

# In the first project you checked the cancel button (X)
# to know when to stop the program. In this program, you'll
# use the other buttons to control which LEDs

# I will get the robot running for you

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
bot = ArduinoAlvik()
bot.begin()

# Now we loop until someone holds down
# the X button.
while not bot.get_touch_cancel():
    # I set both LEDs to BLUE
    bot.right_led.set_color(0,0,1)
    bot.left_led.set_color(0,0,1)
    # I am checkng the LEFT button. If it is
    # pressed I set the left LED to GREEN.
    if bot.get_touch_left():
        bot.left_led.set_color(0,1,0)
    # Now you check the RIGHT button. If it is
    # pressed you set the righ LED to GREEN

    # WORK: Your code here

    # Now check the UP button. If it is pressed
    # set both LEDs to YELLOW (RED and GREEN on)

    # WORK: Your code here

    # Now check the DOWN button. If it is pressed
    # set both LEDs to AQUA (GREEN and BLUE on)

    # WORK: Your code here
    
    sleep_ms(100) # A good habit in loops

# Someone held the X button. Turn off the LEDs and
# stop the robot.

# WORK: Your code here to turn off the LEDs

bot.stop()
