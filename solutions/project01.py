# Flash the LEDs

from arduino_alvik import ArduinoAlvik
from time import sleep_ms

bot = ArduinoAlvik()

bot.begin()
bot.left_led.set_color(1,0,0)
bot.right_led.set_color(0,1,0)
sleep_ms(500)
bot.left_led.set_color(0,1,0)
bot.right_led.set_color(1,0,0)
sleep_ms(500)
bot.left_led.set_color(1,1,0)
bot.right_led.set_color(1,1,0)
sleep_ms(500)
bot.left_led.set_color(0,0,0)
bot.right_led.set_color(0,0,0)
bot.stop()