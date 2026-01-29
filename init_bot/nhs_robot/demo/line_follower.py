from arduino_alvik import ArduinoAlvik
from time import sleep_ms

# Developed with the assistance of Google Gemini V01

def calculate_center(left: int, center: int, right: int):
    """
    Calculates the centroid of the line position.
    Returns a value roughly between 0 (left) and 2 (right).
    """
    centroid = 0
    sum_weight = left + center + right
    sum_values = left + 2 * center + 3 * right
    
    if sum_weight != 0:
        centroid = sum_values / sum_weight
        # Shift range so center is 0
        centroid = 2 - centroid
    return centroid

def run_line_follower(alvik):
    """
    Runs the line follower logic loop.
    Blocks until the 'Cancel' (X) button is touched.
    """
    kp = 50.0
    
    print("Line Follower Started. Press 'X' to stop.")
    
    # Main execution loop for this specific demo
    while not alvik.get_touch_cancel():
        line_sensors = alvik.get_line_sensors()
        # Debug print (optional, can be commented out for speed)
        # print(f'Sensors: {line_sensors}')

        error = calculate_center(*line_sensors)
        control = error * kp

        # Visual feedback based on control effort
        if control > 0.2:
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(0, 0, 0)
        elif control < -0.2:
            alvik.left_led.set_color(1, 0, 0)
            alvik.right_led.set_color(0, 0, 0)
        else:
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)

        # Drive motors
        alvik.set_wheels_speed(30 - control, 30 + control)
        
        # Small delay for loop stability
        sleep_ms(100)
    
    # Cleanup before returning
    alvik.stop()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    print("Line Follower Stopped.")

if __name__ == "__main__":
    # Allow running this file standalone for testing
    alvik = ArduinoAlvik()
    alvik.begin()
    run_line_follower(alvik)
