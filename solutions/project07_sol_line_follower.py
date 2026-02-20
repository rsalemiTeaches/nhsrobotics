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
    STATE_FORWARD = 0
    STATE_LINE_LEFT = 1
    STATE_LINE_RIGHT = 2
    STATE_LOST_LINE = 3
    STATE_CHECK_LINE = 4
    
    
    BLACK_THRESHOLD = 59
    LOST_DELAY_MS = 2000  # Must lose the line for 1000ms before stopping
    FAST_SPEED = 20
    SLOW_SPEED = 5
    lost_time = None
    # --- Initial Setup ---
    current_state = STATE_FORWARD
    sb.enable_info_logging()
    print("Press X to stop.")
    sb.log_info("SYSTEM START: Line Follower SM")

    def make_log_line(state, l_sensor, c_sensor, r_sensor):
        return state + " - L:" + str(l_sensor) + " C:" + str(c_sensor) + " R:" + str(r_sensor)    

    # --- Main Loop ---
    while not alvik.get_touch_cancel():
        sleep_ms(10)
        # 1. SENSE
        # We use an underscore '_' to unpack and ignore the center sensor
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()
        if current_state == STATE_FORWARD:
            # --- ACTIONS ---
            alvik.set_wheels_speed(FAST_SPEED, FAST_SPEED)
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)
            sb.log_info(make_log_line("STATE_FORWARD", l_sensor, c_sensor, r_sensor))
            
            # --- TRANSITIONS ---
            if l_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_LEFT
                
            elif r_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_RIGHT
            elif max(l_sensor, c_sensor, r_sensor) < BLACK_THRESHOLD:
                current_state = STATE_LOST_LINE;

        elif current_state == STATE_LINE_LEFT:
            # --- ACTIONS ---
            alvik.set_wheels_speed(SLOW_SPEED, FAST_SPEED)
            alvik.left_led.set_color(0, 1, 0) # Green
            alvik.right_led.set_color(0, 0, 0) # Off
            sb.log_info(make_log_line("STATE_LINE_LEFT", l_sensor, c_sensor, r_sensor))
            # --- TRANSITIONS ---
            if l_sensor < BLACK_THRESHOLD:
                current_state = STATE_FORWARD
            elif max(l_sensor, c_sensor, r_sensor) < BLACK_THRESHOLD:
                current_state = STATE_LOST_LINE;

        elif current_state == STATE_LINE_RIGHT:
            # --- ACTIONS ---
            alvik.set_wheels_speed(FAST_SPEED, SLOW_SPEED)
            alvik.left_led.set_color(0, 0, 0) # Off
            alvik.right_led.set_color(0, 1, 0) # Green
            sb.log_info(make_log_line("STATE_LINE_RIGHT", l_sensor, c_sensor, r_sensor))

            # --- TRANSITIONS ---
            if r_sensor < BLACK_THRESHOLD:
                current_state = STATE_FORWARD
            elif max(l_sensor, c_sensor, r_sensor) < BLACK_THRESHOLD:
                current_state = STATE_LOST_LINE;

        #Flex: Make the robot stop if has not seen the line for a while

        elif current_state == STATE_LOST_LINE :
            lost_time = ticks_ms()
            if l_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_LEFT       
            elif r_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_RIGHT
            elif c_sensor > BLACK_THRESHOLD:
                current_state = STATE_FORWARD
            else:
                current_state = STATE_CHECK_LINE
            sb.log_info(make_log_line("STATE_LOST_LINE", l_sensor, c_sensor, r_sensor))
            
        elif current_state == STATE_CHECK_LINE:
            alvik.left_led.set_color(1, 0, 0) # Red
            alvik.right_led.set_color(1, 0, 0) # Red
            sb.log_info(make_log_line("STATE_CHECK_LINE", l_sensor, c_sensor, r_sensor))
            if l_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_LEFT       
            elif r_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_RIGHT
            elif c_sensor > BLACK_THRESHOLD:
                current_state = STATE_FORWARD
            elif ticks_diff(ticks_ms(), lost_time) > LOST_DELAY_MS:
                sb.log_info("Line lost for too long. Stopping.")
                break
finally:
    # Cleanup when the X button is pressed
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    sb.update_display("Program", "Stopped")
    alvik.stop()
    print("Program ended.")
    
