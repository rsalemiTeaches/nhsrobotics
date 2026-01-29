from arduino_alvik import ArduinoAlvik
from time import sleep_ms

# Import the demo modules.
# These files must be on the board in the same directory or Python path.
import line_follower
import hand_follower
import touch_move
import color_maze_runner
import sumo_rev0

# Developed with the assistance of Google Gemini V02

def update_led_status(alvik, val):
    """
    Updates the LED colors based on the current menu selection.
    """
    if val == 0:
        # Blue - Line Follower
        alvik.left_led.set_color(0, 0, 1)
        alvik.right_led.set_color(0, 0, 1)
    elif val == 1:
        # Green - Hand Follower
        alvik.left_led.set_color(0, 1, 0)
        alvik.right_led.set_color(0, 1, 0)
    elif val == 2:
        # Magenta - Touch Move
        alvik.left_led.set_color(1, 0, 1)
        alvik.right_led.set_color(1, 0, 1)    
    elif val == 3:
        # Red - Color Maze
        alvik.left_led.set_color(1, 0, 0)
        alvik.right_led.set_color(1, 0, 0)
    elif val == 4:
        # Yellow - Sumo
        alvik.left_led.set_color(1, 1, 0)
        alvik.right_led.set_color(1, 1, 0)

def blink_start(alvik):
    """
    Visual feedback that a mode has been selected.
    """
    alvik.left_led.set_color(1, 1, 1)
    alvik.right_led.set_color(1, 1, 1)
    sleep_ms(200)
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    sleep_ms(200)

# --- Top Level Initialization ---
alvik = ArduinoAlvik()
alvik.begin()

# Wait for the system to stabilize
sleep_ms(1000)

menu_status = 0
MAX_MENU_ITEMS = 5

print("Alvik Demo Menu Started")
print("Use Up/Down to select, OK (Check) to run.")

try:
    while True:
        # Update the visual indicator for the current menu item
        update_led_status(alvik, menu_status)

        # 1. Navigation Logic (Up/Down)
        if alvik.get_touch_up():
            if menu_status < MAX_MENU_ITEMS - 1:
                menu_status += 1
            # Debounce: Wait for release
            while alvik.get_touch_up():
                sleep_ms(50)
        
        if alvik.get_touch_down():
            if menu_status > 0:
                menu_status -= 1
            # Debounce: Wait for release
            while alvik.get_touch_down():
                sleep_ms(50)

        # 2. Selection Logic (OK/Right)
        # We use get_touch_ok (check mark) as the enter key
        if alvik.get_touch_ok():
            print(f"Starting Demo #{menu_status}")
            blink_start(alvik)

            # --- DISPATCHER ---
            # This calls the run function of the specific module.
            # Crucially, these functions are BLOCKING.
            # They will not return until the user cancels execution 
            # within the specific demo (usually via the X button).
            
            if menu_status == 0:
                print("Running Line Follower...")
                line_follower.run_line_follower(alvik)
            
            elif menu_status == 1:
                print("Running Hand Follower...")
                hand_follower.run_hand_follower(alvik)
            
            elif menu_status == 2:
                print("Running Touch Move...")
                touch_move.run_touch_move(alvik)
            
            elif menu_status == 3:
                print("Running Color Maze Runner...")
                color_maze_runner.run_color_maze_runner(alvik)
            
            elif menu_status == 4:
                print("Running Sumo...")
                sumo_rev0.run_sumo(alvik)

            # --- CLEANUP AFTER DEMO ---
            print("Demo finished. returning to menu.")
            alvik.stop() # Ensure motors are off
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)
            
            # Wait for button release to avoid accidental re-entry
            while alvik.get_touch_ok():
                sleep_ms(100)
            sleep_ms(500)

        sleep_ms(50)

finally:
    # This block ensures motors stop even if the program crashes or is interrupted
    alvik.stop()
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    print("Program Exited Safely.")