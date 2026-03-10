# project07_scaffold.py
# Version: V01
# Description: Student scaffold for the Line Following State Machine
from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms, ticks_ms, ticks_diff
alvik = ArduinoAlvik()
try:
    # --- Initialization ---
    alvik.begin()
    sb = SuperBot(alvik)
    # --- Constants & States ---
    STATE_FORWARD = 0
    STATE_LINE_LEFT = 1
    STATE_LINE_RIGHT = 2
    STATE_LOST_LINE = 3
    STATE_CHECK_LINE = 4
    BLACK_THRESHOLD = 60
    LOST_DELAY_MS = 2000
    BASE_SPEED = 20
    SPEED_INCREMENT = 10
    FAST_SPEED = BASE_SPEED + SPEED_INCREMENT
    SLOW_SPEED = BASE_SPEED - SPEED_INCREMENT
    # --- Variables ---
    current_state = STATE_FORWARD
    lost_time = 0
    sb.enable_info_logging()
    # --- Helper Functions ---
    def make_log_line(state, l, c, r):
        return state + " - L:" + str(l) + " C:" + str(c) + " R:" + str(r)
    # --- Main Loop ---
    while not alvik.get_touch_cancel():
        sleep_ms(10)
        # --- SENSE ---
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()
        # --- THINK & ACT ---
        if current_state == STATE_FORWARD:
            # --- Example State: STATE_FORWARD ---
            alvik.set_wheels_speed(BASE_SPEED, BASE_SPEED)
            sb.log_info(make_log_line("FORWARD", l_sensor, c_sensor, r_sensor))
            # Transitions
            if l_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_LEFT
            elif r_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_RIGHT
            elif max(l_sensor, c_sensor, r_sensor) < BLACK_THRESHOLD:
                current_state = STATE_LOST_LINE
        elif current_state == STATE_LINE_LEFT:
            # --- WORK: Complete the logic for turning left ---
            # Set wheel speeds to pivot left
            # alvik.set_wheels_speed(SLOW_SPEED, FAST_SPEED)
            # --- WORK ---
            sb.log_info(make_log_line("LEFT", l_sensor, c_sensor, r_sensor))
            # --- WORK: Transitions ---
            # If the left sensor is no longer seeing black, go back to FORWARD
            # --- WORK ---
        # --- WORK: Create the elif block for STATE_LINE_RIGHT ---
        # --- WORK ---
        # --- FLEX CHALLENGE: Safety Timeout ---
        elif current_state == STATE_LOST_LINE:
            # --- WORK: Record the time the line was lost ---
            # lost_time = ticks_ms()
            # --- WORK ---
            current_state = STATE_CHECK_LINE
        elif current_state == STATE_CHECK_LINE:
            # --- WORK: Check if any sensor sees the line again ---
            # --- WORK: Use ticks_diff to see if 2 seconds (2000ms) have passed ---
            # if ticks_diff(...) > LOST_DELAY_MS:
            #     break
            # --- WORK ---
            pass
finally:
    # --- Cleanup ---
    alvik.brake()
    sb.update_display("Program", "Stopped")
    alvik.stop()
# Developed with the assistance of Google Gemini. V01
