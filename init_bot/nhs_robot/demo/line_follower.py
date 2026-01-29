# line_follower.py
# Version: V02
# Refactored for SuperBot Event Architecture

from time import sleep_ms

def calculate_center(left, center, right):
    """Centroid calculation for line positioning."""
    sum_weight = left + center + right
    if sum_weight == 0: return 0
    # Values between -1 (left) and 1 (right)
    raw_pos = (left * -1 + center * 0 + right * 1) / sum_weight
    return raw_pos

def run_line_follower(sb):
    """
    Main loop for line following.
    Uses the provided SuperBot (sb) instance.
    """
    kp = 40.0
    print("Line Follower Active. Press 'X' to exit.")
    sb.update_display("RUNNING:", "Line Follower", "X to Exit")

    while not sb.get_pressed_cancel():
        L, C, R = sb.alvik.get_line_sensors()
        error = calculate_center(L, C, R)
        control = error * kp

        # Basic steering logic
        sb.alvik.set_wheels_speed(30 + control, 30 - control)
        
        sleep_ms(50)

    # Clean stop
    sb.alvik.brake()
    print("Line Follower Stopped.")

# Developed with the assistance of Google Gemini V02