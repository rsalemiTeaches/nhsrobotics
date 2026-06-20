# project07_line_sm.py
# Version: V05 
# Description: A State Machine-based line follower

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms, ticks_ms, ticks_diff

alvik = ArduinoAlvik()

try:
    alvik.begin()
    sb = SuperBot(alvik)

    # --- Constants & States ---
    STATE_LINE_LEFT = 1
    STATE_LINE_RIGHT = 2
    STATE_LOST_LINE = 3
    STATE_CHECK_LINE = 4
    
    
    BLACK_THRESHOLD = 60
    BASE_SPEED = 30
    SPEED_INCREMENT = 15
    # --- Initial Setup ---
    current_state = STATE_LINE_LEFT
    sb.enable_info_logging()
    print("Press X to stop.")
    sb.log_info("SYSTEM START: Line Follower SM")

    
    # --- Main Loop ---
    while not alvik.get_touch_cancel():
        sleep_ms(10)
        # 1. SENSE
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()

        if current_state == STATE_LINE_LEFT:
            # --- ACTIONS ---
            alvik.set_wheels_speed(BASE_SPEED - SPEED_INCREMENT, BASE_SPEED + SPEED_INCREMENT)
            alvik.left_led.set_color(0, 1, 0) # Green
            alvik.right_led.set_color(0, 0, 0) # Off
            #sb.log_info("STATE_LINE_LEFT", l_sensor, c_sensor, r_sensor)
            # --- TRANSITIONS ---
            if r_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_RIGHT
        elif current_state == STATE_LINE_RIGHT:
            # --- ACTIONS ---
            alvik.set_wheels_speed(BASE_SPEED + SPEED_INCREMENT, BASE_SPEED - SPEED_INCREMENT)
            alvik.left_led.set_color(0, 0, 0) # Off
            alvik.right_led.set_color(0, 1, 0) # Green
            #sb.log_info("STATE_LINE_RIGHT", l_sensor, c_sensor, r_sensor)
            # --- TRANSITIONS ---
            if l_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_LEFT

finally:
    # Cleanup when the X button is pressed
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    sb.update_display("Program", "Stopped")
    alvik.stop()
    
    
