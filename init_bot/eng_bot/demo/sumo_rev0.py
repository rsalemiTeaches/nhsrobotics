from time import sleep_ms
from arduino_alvik import ArduinoAlvik
alvik = ArduinoAlvik()
alvik.begin()


def turn_left(alvik):
  alvik.rotate(130)	

def run_sumo(alvik):
  print(alvik.get_color_label())
  while True:
    color = alvik.get_color_label()
    print(color)
    if color == "BLACK":
      alvik.left_led.set_color(0,0,0)
      alvik.right_led.set_color(1,1,1)
      alvik.set_wheels_speed(80,80)
      sleep_ms(10)
    else:
      alvik.set_wheels_speed(-40,-40)
      sleep_ms(500)
      alvik.right_led.set_color(0,0,0)
      alvik.left_led.set_color(1,1,1)
      turn_left(alvik)

    if alvik.get_touch_cancel():
      break

if __name__ == "__main__":
  run_sumo(alvik)
  alvik.stop()

