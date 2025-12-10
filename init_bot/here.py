# Project 10: The Line Racer (Starter Code)
from arduino_alvik import ArduinoAlvik
import time
from nhs_robotics import get_closest_distance

# State Constants
STATE_WAITING = 1
STATE_RACING = 2
STATE_AVOID_1_TURN_LEFT_45 = 3
STATE_AVOID_2_DRIVE = 4
STATE_AVOID_3_TURN_RIGHT_90 = 5
STATE_AVOID_4_FIND_LINE = 6

# Sensor Thresholds
OBSTACLE_DISTANCE = 9
LINE_BLACK_THRESHOLD = 700

# Motor Speeds
RACE_SPEED = 60
FIND_LINE_SPEED = 30

# Maneuver Constants
AVOID_TURN_1 = 45
AVOID_DRIVE_CM = 25
AVOID_TURN_2 = -90

def get_turn_adjustment(l_sensor, c_sensor, r_sensor):
    global LINE_BLACK_THRESHOLD
    
    sum_all = l_sensor + c_sensor + r_sensor
    if sum_all < (LINE_BLACK_THRESHOLD / 2):
        return 0

    weighted_sum = (l_sensor * 1) + (c_sensor * 2) + (r_sensor * 3)
    centroid = weighted_sum / sum_all
    
    error = centroid - 2.0
    
    KP = 25
    
    adjustment = error * KP
    return adjustment

print("Starting Project 10: The Line Racer...")

alvik = ArduinoAlvik()
alvik.begin()

current_state = STATE_WAITING

try:
    while not alvik.get_touch_cancel():

        l_sensor, c_sensor, r_sensor = alvik.get_line_sensors()
        
        dist_left, dist_front_left, dist_center, dist_front_right, dist_right = alvik.get_distance()
        closest_dist = get_closest_distance(dist_left, dist_front_left, dist_center, dist_front_right, dist_right) 
        
        sees_obstacle = closest_dist < OBSTACLE_DISTANCE

        if current_state == STATE_WAITING:
            alvik.left_led.set_color(0, 0, 1)
            alvik.right_led.set_color(0, 0, 1)
            time.sleep(0.2)
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)
            time.sleep(0.2)
            
            if alvik.get_touch_ok():
                print("Button pressed! Starting race...")
                current_state = STATE_RACING

        elif current_state == STATE_RACING:
            alvik.left_led.set_color(0, 1, 0)
            alvik.right_led.set_color(0, 1, 0)
            
            adjustment = get_turn_adjustment(l_sensor, c_sensor, r_sensor)
            
            left_speed = RACE_SPEED - adjustment
            right_speed = RACE_SPEED + adjustment
            
            alvik.set_wheels_speed(left_speed, right_speed)
            
            if sees_obstacle:
                print("Obstacle detected! Starting avoidance...")
                alvik.stop()
                current_state = STATE_AVOID_1_TURN_LEFT_45

        elif current_state == STATE_AVOID_1_TURN_LEFT_45:
            print("AVOID: 1. Turning LEFT 45 degrees")
            alvik.left_led.set_color(1, 1, 0)
            alvik.right_led.set_color(1, 1, 0)
            
            alvik.rotate(AVOID_TURN_1)
            print("Turn complete, moving to drive state")
            current_state = STATE_AVOID_2_DRIVE

        elif current_state == STATE_AVOID_2_DRIVE:
            print("AVOID: 2. Driving 25 cm")
            alvik.left_led.set_color(1, 1, 0)
            alvik.right_led.set_color(1, 1, 0)
            
            alvik.move(AVOID_DRIVE_CM)
            print("Drive complete, moving to turn right state")
            current_state = STATE_AVOID_3_TURN_RIGHT_90

        elif current_state == STATE_AVOID_3_TURN_RIGHT_90:
            print("AVOID: 3. Turning RIGHT 90 degrees")
            alvik.left_led.set_color(1, 1, 0)
            alvik.right_led.set_color(1, 1, 0)
            
            alvik.rotate(AVOID_TURN_2)
            print("Right turn complete, moving to find line state")
            current_state = STATE_AVOID_4_FIND_LINE
 
        elif current_state == STATE_AVOID_4_FIND_LINE:
            print("AVOID: 4. Driving forward to FIND line...")
            alvik.left_led.set_color(1, 0, 1)
            alvik.right_led.set_color(1, 0, 1)
            
            alvik.set_wheels_speed(FIND_LINE_SPEED, FIND_LINE_SPEED)

            if c_sensor > LINE_BLACK_THRESHOLD:
                print("Line found (center sensor)! Resuming race...")
                alvik.stop()
                current_state = STATE_RACING

        else:
            print("Error: Unknown state!")
            current_state = STATE_RACING

        # Only sleep if we're not in a blocking state
        if current_state == STATE_RACING or current_state == STATE_AVOID_4_FIND_LINE or current_state == STATE_WAITING:
            time.sleep(0.01)

finally:
    print("Stopping program.")
    alvik.stop()