# demo.py
# Version: V06
# Main Dispatcher for Natick High School Robotics
# Re-synced with SuperBot V41 architecture.

from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
from time import sleep_ms

# Note: These paths assume files are in a 'demo' folder on the robot
import demo.line_follower as line_follower
import demo.hand_follower as hand_follower
import demo.touch_move as touch_move
import demo.color_maze_runner as color_maze_runner
import demo.sumo_rev0 as sumo_rev0

def update_menu_visuals(sb, index):
    """Updates LEDs and Screen based on menu selection."""
    # 0: Blue, 1: Green, 2: Magenta, 3: Red, 4: Yellow
    colors = [(0,0,1), (0,1,0), (1,0,1), (1,0,0), (1,1,0)]
    r, g, b = colors[index]
    sb.alvik.left_led.set_color(r, g, b)
    sb.alvik.right_led.set_color(r, g, b)
    
    labels = [
        "Line Follower", 
        "Hand Follower", 
        "Touch Move", 
        "Maze Runner", 
        "Sumo Bot"
    ]
    sb.update_display("SELECT DEMO:", labels[index], "OK to Start")

# --- Main Setup ---
alvik = ArduinoAlvik()
alvik.begin()
sb = SuperBot(alvik)

menu_index = 0
MAX_ITEMS = 5 

print("RoboNatick Menu V06 Started.")

try:
    while True:
        # Update visuals for current selection
        update_menu_visuals(sb, menu_index)

        # Rising-edge navigation (tap logic)
        if sb.get_pressed_up():
            menu_index = (menu_index + 1) % MAX_ITEMS
        
        if sb.get_pressed_down():
            menu_index = (menu_index - 1) % MAX_ITEMS

        # Enter Selected Demo
        if sb.get_pressed_ok():
            print(f"Starting Demo: {menu_index}")
            
            # Dispatch to blocking demo functions
            if menu_index == 0:
                line_follower.run_line_follower(sb)
            elif menu_index == 1:
                hand_follower.run_hand_follower(sb)
            elif menu_index == 2:
                touch_move.run_touch_move(sb)
            elif menu_index == 3:
                color_maze_runner.run_color_maze_runner(sb)
            elif menu_index == 4:
                sumo_rev0.run_sumo(sb)
            
            print("Returned to Main Menu.")
            # Clear buttons to ensure return doesn't double-trigger menu navigation
            sleep_ms(200)

        sleep_ms(20)

finally:
    # Safety cleanup
    sb.alvik.stop()
    sb.alvik.brake()
    print("System Shutdown.")

# Developed with the assistance of Google Gemini V06