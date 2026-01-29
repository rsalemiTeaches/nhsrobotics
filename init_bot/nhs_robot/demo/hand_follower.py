# hand_follower.py
# Version: V02
# Refactored for SuperBot Event Architecture

from time import sleep_ms

def run_hand_follower(sb):
    """
    Main loop for hand following.
    Uses the provided SuperBot (sb) instance.
    """
    target_dist = 12.0 # cm
    print("Hand Follower Active. Press 'X' to exit.")
    sb.update_display("RUNNING:", "Hand Follower", "X to Exit")

    while not sb.get_pressed_cancel():
        # Get distances: Left, Center-Left, Center, Center-Right, Right
        _, _, center_dist, _, _ = sb.alvik.get_distance()
        
        if center_dist is None: center_dist = target_dist

        error = center_dist - target_dist
        speed = error * 8
        
        # Deadzone to prevent jitter
        if abs(error) < 1.0: speed = 0
            
        sb.alvik.set_wheels_speed(speed, speed)
        sleep_ms(50)

    # Clean stop
    sb.alvik.brake()
    print("Hand Follower Stopped.")

# Developed with the assistance of Google Gemini V02