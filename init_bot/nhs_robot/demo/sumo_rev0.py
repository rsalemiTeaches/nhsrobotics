# sumo_rev0.py
# Version: V02
# Refactored for SuperBot Event Architecture

from time import sleep_ms

def turn_around(alvik):
    """Quick escape turn when edge is detected."""
    alvik.rotate(130)	

def run_sumo(sb):
    """
    Main Sumo behavior.
    Uses SuperBot (sb) for debounced exit.
    """
    print("Sumo Mode Active. Press 'X' to exit.")
    sb.update_display("RUNNING:", "Sumo Bot", "X to Exit")

    while not sb.get_pressed_cancel():
        color = sb.alvik.get_color_label()
        
        if color == "BLACK":
            # On the mat: Full steam ahead
            sb.alvik.left_led.set_color(0, 1, 0)
            sb.alvik.right_led.set_color(0, 1, 0)
            sb.alvik.set_wheels_speed(80, 80)
        else:
            # Found the white edge: Retreat and turn
            sb.alvik.left_led.set_color(1, 0, 0)
            sb.alvik.right_led.set_color(1, 0, 0)
            sb.alvik.set_wheels_speed(-40, -40)
            sleep_ms(500)
            turn_around(sb.alvik)

        sleep_ms(20)

    # Clean stop
    sb.alvik.brake()
    print("Sumo Mode Stopped.")

# Developed with the assistance of Google Gemini V02