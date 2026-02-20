# project07_line_sm.py
# Version: V05 
# Description: A State Machine-based line follower

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms

alvik = ArduinoAlvik()

try:
    alvik.begin()

    # Create a SuperBot instance to use the logging system
    sb = SuperBot(alvik)

    # --- Constants & States ---
    STATE_FORWARD = 0
    STATE_LINE_LEFT = 1
    STATE_LINE_RIGHT = 2

    BLACK_THRESHOLD = 60

    FAST_SPEED = 20
    SLOW_SPEED = 5

    # --- Initial Setup ---
    current_state = STATE_FORWARD
    sb.enable_info_logging()  # Use the SuperBot's logging system to log info messages
    sb.log_info("SYSTEM START: Line Follower SM")

    def make_log_line(state, l_sensor, c_sensor, r_sensor):
        """
        Helper function to create a log line with
        the current state and sensor readings.
        """
        return state + " - L:" + str(l_sensor) + " C:" + str(c_sensor) + " R:" + str(r_sensor)    

    # --- Main Loop ---
    while not alvik.get_touch_cancel():
        sleep_ms(10)

        # 1. SENSE
        # Read the line sensors
        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()

        # STATE_FORWARD is the default state where the robot 
        # moves forward until it detects a line on either side.
        
        # I have written STATE_FORWARD for you.  
        # Use this state as a template to implement 
        # the other two states: STATE_LINE_LEFT and STATE_LINE_RIGHT.
        
        if current_state == STATE_FORWARD:
            # --- ACTIONS ---
            alvik.set_wheels_speed(FAST_SPEED, FAST_SPEED)
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
            sb.log_info(make_log_line("STATE_FORWARD", l_sensor, c_sensor, r_sensor))
            
            # --- TRANSITIONS ---
            if l_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_LEFT
                
            elif r_sensor > BLACK_THRESHOLD:
                current_state = STATE_LINE_RIGHT

        # In STATE_LINE_LEFT, the robot has detected a line 
        # on the left side and needs to turn left to stay on the line. 
        # It will transition back to STATE_FORWARD once the 
        # left sensor no longer detects the line.
        elif current_state == STATE_LINE_LEFT:
            # --- ACTIONS ---
            # WORK: Set the wheel speeds to turn left
            # WORK: Set the left LED to green and the right LED to off
            # WORK: Use the SuperBot's logging system to log the current state and sensor readings
            # WORK: Remember to use the make_log_line function to format the log message
            # --- TRANSITIONS ---
            # WORK: If the l_sensor no longer detects the line, transition back to STATE_FORWARD
            pass
        # In STATE_LINE_RIGHT, the robot has detected a line 
        # on the right side and needs to turn right to stay on the line. 
        # It will transition back to STATE_FORWARD once the 
        # right sensor no longer detects the line.
        #
        # WORK: Use elif to check if current_state is STATE_LINE_RIGHT
            # --- ACTIONS ---
            # WORK: Set the wheel speeds to turn right
            # WORK: Set the left LED to off and the right LED to green
            # WORK: Use the SuperBot's logging system to log the current state and sensor readings
            # WORK: Remember to use the make_log_line function to format the log message
            # --- TRANSITIONS ---
            # WORK: If the r_sensor no longer detects the line, transition back to STATE_FORWARD
            

finally:
    # Cleanup when the X button is pressed
    alvik.brake()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    sb.update_display("Program", "Stopped")
    alvik.stop()
    
