# project07_scaffold_line_follower.py
# Version: V02
# Description: Alternating Action/Transition scaffold for State Machine
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms, ticks_ms, ticks_diff

alvik = ArduinoAlvik()

try:
    alvik.begin()
    sb = SuperBot(alvik)

    # --- Constants & States ---
    STATE_FORWARD = 0
    STATE_LINE_LEFT = 1
    STATE_LINE_RIGHT = 2
    STATE_LOST_LINE = 3

    # --- Tuning Parameters ---
    BLACK_THRESHOLD = 59
    LOST_DELAY_MS = 2000
    FAST_SPEED = 20
    SLOW_SPEED = 5

    # --- Initial Setup ---
    current_state = STATE_FORWARD
    lost_time = None
    sb.enable_info_logging()
    print("Press X to stop.")

    # --- Main Loop ---
    while not alvik.get_touch_cancel():
        sleep_ms(10)
        
        # 1. SENSE
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()

        # 2. DECIDE & ACT (State Machine)
        if current_state == STATE_FORWARD:
            # ACTION (Provided)
            alvik.set_wheels_speed(FAST_SPEED, FAST_SPEED)
            alvik.left_led.set_color(0, 1, 0) # Green
            alvik.right_led.set_color(0, 1, 0)
            
            # WORK: Implement TRANSITIONS
            # If l_sensor is greater than BLACK_THRESHOLD, go to STATE_LINE_LEFT
            # If r_sensor is greater than BLACK_THRESHOLD, go to STATE_LINE_RIGHT

        elif current_state == STATE_LINE_LEFT:
            # WORK: Implement ACTIONS
            # Set wheel speeds to turn the robot back toward the line (Right wheel faster than Left)
            # Set LEDs to a unique color for this state
            
            # TRANSITION (Provided)
            if l_sensor < BLACK_THRESHOLD:
                current_state = STATE_FORWARD
            elif max(l_sensor, c_sensor, r_sensor) < BLACK_THRESHOLD:
                current_state = STATE_LOST_LINE
                lost_time = ticks_ms()

        elif current_state == STATE_LINE_RIGHT:
            # ACTION (Provided)
            alvik.set_wheels_speed(SLOW_SPEED, FAST_SPEED)
            alvik.left_led.set_color(0, 0, 1) # Blue
            alvik.right_led.set_color(0, 0, 1)
            
            # WORK: Implement TRANSITIONS
            # If r_sensor is back on white, go to STATE_FORWARD
            # If all sensors are white, go to STATE_LOST_LINE (and initialize lost_time)

        elif current_state == STATE_LOST_LINE:
            # WORK: Implement ACTION (The Timeout)
            # If ticks_diff(ticks_ms(), lost_time) > LOST_DELAY_MS, stop and break the loop
            
            # TRANSITION (Provided)
            sb.log_info("LOST", l_sensor, c_sensor, r_sensor)
            if l_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_LEFT
            elif r_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_RIGHT

finally:
    # Cleanup when the X button is pressed
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    sb.log_info("Program", "Stopped")
    alvik.stop()
    print("Program ended.")

# Developed with the assistance of Google Gemini.