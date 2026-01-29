# color_maze_runner.py
# Version: V02
# Refactored for SuperBot Event Architecture

from time import sleep_ms

def turn_left(alvik):
    alvik.left_led.set_color(1, 1, 1)
    alvik.rotate(90)	
    alvik.left_led.set_color(0, 0, 0)
	
def turn_right(alvik):
    alvik.right_led.set_color(1, 1, 1)
    alvik.rotate(-90)	
    alvik.right_led.set_color(0, 0, 0)

def run_color_maze_runner(sb):
    """
    Drives based on floor color.
    Uses SuperBot (sb) for debounced exit.
    """
    print("Maze Runner Active. Press 'X' to exit.")
    sb.update_display("RUNNING:", "Maze Runner", "X to Exit")

    # Initial wait for placement on a color
    while sb.alvik.get_color_label() == 'BLACK' and not sb.get_pressed_cancel():
        sleep_ms(100)
	
    while not sb.get_pressed_cancel():
        color = sb.alvik.get_color_label()
        
        if 'RED' in color or 'PINK' in color:
            turn_left(sb.alvik)
            sb.alvik.move(5, unit='cm')
        elif 'GREEN' in color:
            turn_right(sb.alvik)
            sb.alvik.move(5, unit='cm')
        else:
            # Default search speed
            sb.alvik.set_wheels_speed(40, 40)
            
        sleep_ms(50)
  
    # Clean stop
    sb.alvik.brake()
    print("Maze Runner Stopped.")

# Developed with the assistance of Google Gemini V02