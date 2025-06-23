# Flash the LEDs

from arduino_alvik import ArduinoAlvik
from time import sleep_ms

bot = ArduinoAlvik()
bot.begin()
while not bot.get_touch_cancel():
  bot.right_led.set_color(0,0,1)
  bot.left_led.set_color(0,0,1)
  if bot.get_touch_left():
    bot.left_led.set_color(0,1,0)
  if bot.get_touch_right():
    bot.right_led.set_color(0,1,0)
  if bot.get_touch_up():
    bot.right_led.set_color(1,1,0)
    bot.left_led.set_color(1,1,0)
  if bot.get_touch_down():
    bot.right_led.set_color(0,1,1)
    bot.left_led.set_color(0,1,1)
  sleep_ms(10)
bot.right_led.set_color(0,0,1)
bot.left_led.set_color(0,0,1)
bot.stop()
