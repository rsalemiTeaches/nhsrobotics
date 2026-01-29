# touch_move.py
# Version: V02
# Refactored for SuperBot Event Architecture

from time import sleep_ms

def flash_status(alvik, r, g, b):
    alvik.left_led.set_color(r, g, b)
    alvik.right_led.set_color(r, g, b)
    sleep_ms(200)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)

def execute_sequence(sb, sequence):
    """Runs the recorded movements."""
    sb.update_display("EXECUTING...", f"Steps: {len(sequence)}", "X to Abort")
    for move in sequence:
        if sb.get_pressed_cancel(): break # Abort run
        
        if move == 'F': sb.alvik.move(15)
        elif move == 'B': sb.alvik.move(-15)
        elif move == 'L': sb.alvik.rotate(90)
        elif move == 'R': sb.alvik.rotate(-90)
        
    sb.alvik.brake()

def run_touch_move(sb):
    """
    Record movements with buttons, then run with OK.
    Uses SuperBot (sb) events for "programming".
    """
    movements = []
    print("Touch Move Programming. Press 'X' to exit.")
    
    while not sb.get_pressed_cancel():
        sb.update_display("RECORDING:", f"Moves: {len(movements)}", "OK to Run")
        
        # Add to sequence
        if sb.get_pressed_up():
            movements.append('F')
            flash_status(sb.alvik, 0, 1, 0) # Green
        elif sb.get_pressed_down():
            movements.append('B')
            flash_status(sb.alvik, 1, 0, 0) # Red
        elif sb.get_pressed_left():
            movements.append('L')
            flash_status(sb.alvik, 0, 0, 1) # Blue
        elif sb.get_pressed_right():
            movements.append('R')
            flash_status(sb.alvik, 1, 1, 0) # Yellow
            
        # Run sequence
        if sb.get_pressed_ok() and len(movements) > 0:
            execute_sequence(sb, movements)
            movements.clear() # Reset after run

        sleep_ms(20)

    sb.alvik.brake()
    print("Touch Move Stopped.")

# Developed with the assistance of Google Gemini V02