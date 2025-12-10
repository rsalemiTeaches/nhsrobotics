from arduino_alvik import ArduinoAlvik
from time import sleep_ms



def turn_left(alvik):
  alvik.left_led.set_color(1,1,1)
  alvik.rotate(90)	
  alvik.left_led.set_color(0,0,0)
	
def turn_right(alvik):
  alvik.right_led.set_color(1,1,1)
  alvik.rotate(-90)	
  alvik.right_led.set_color(0,0,0)

def run_color_maze_runner(alvik):

  while (alvik.get_color_label() == 'BLACK'):
	 sleep_ms(100);
	
  while not alvik.get_touch_cancel():
   color = alvik.get_color_label()
   print(color)
   if (color == 'RED' or 'PINK' in color):
    turn_left(alvik)
    alvik.move(5, unit='cm' )
   elif ('GREEN' in color):
    turn_right(alvik)
    alvik.move(5, unit='cm')
   else:
    alvik.set_wheels_speed(40,40)
  
if __name__ == "__main__":
  alvik = ArduinoAlvik()
  alvik.begin()
  run_color_maze_runner(alvik)
  alvik.stop()
