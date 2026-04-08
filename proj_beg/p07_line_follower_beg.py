# project07_line_sm_student.py
# --- Section ---
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms
# --- Section ---
alvik = ArduinoAlvik()
# --- Section ---
try:
# --- Section ---
    alvik.begin()
    sb = SuperBot(alvik)
# --- Section ---
    # --- Constants & States ---
    STATE_LINE_LEFT = 1
    STATE_LINE_RIGHT = 2
    BLACK_THRESHOLD = 60
    BASE_SPEED = 30
    SPEED_INCREMENT = 15
# --- Section ---
    # --- Initial Setup ---
    current_state = STATE_LINE_LEFT
    sb.enable_info_logging()
    print("Press X to stop.")
    sb.log_info("Get to work,you!")
# --- Section ---
    # --- Main Loop ---
    while not alvik.get_touch_cancel():
# --- Section ---
        sleep_ms(10)
# --- Section ---
        # 1. SENSE
        # WORK: Use alvik.get_line_sensors() to get values for l_sensor, c_sensor, and r_sensor
# --- Section ---
        if current_state == STATE_LINE_LEFT:
# --- Section ---
            # WORK: Define ACTIONS for STATE_LINE_LEFT (Set wheel speeds and LEDs)
# --- Section ---
            # WORK: Define TRANSITION to STATE_LINE_RIGHT if the right sensor sees black
            pass
# --- Section ---
        elif current_state == STATE_LINE_RIGHT:
# --- Section ---
            # WORK: Define ACTIONS for STATE_LINE_RIGHT (Set wheel speeds and LEDs)
# --- Section ---
            # WORK: Define TRANSITION to STATE_LINE_LEFT if the left sensor sees black
            pass
# --- Section ---
finally:
# --- Section ---
    # Cleanup when the X button is pressed
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    sb.update_display("Program", "Stopped")
    alvik.stop()
# --- Section ---
# Developed with the assistance of Google Gemini
# V02