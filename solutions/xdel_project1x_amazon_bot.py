# Project 17: The Amazon Warehouse Bot (Tow Truck Edition)
#
# SCENARIO:
# 1. Robot starts facing "The Manager" (You).
# 2. You show it an Order (AprilTag ID 1, 2, or 3).
# 3. Robot turns around, finds the matching box, and drives to it.
# 4. NEW: Robot spins 180 and BACKS UP to latch the box.
# 5. Robot tows the box home using the Order Tag for guidance.

from arduino_alvik import ArduinoAlvik
from qwiic_huskylens import QwiicHuskylens
from qwiic_i2c.micropython_i2c import MicroPythonI2C
import time
import sys

# --- CONFIGURATION ---
SCREEN_CENTER_X = 160 
TURN_GAIN = 0.15 
STOP_DISTANCE_CM = 10.0
HOME_STOP_DIST_CM = 15.0 

# --- SETUP ---
alvik = ArduinoAlvik()
alvik.begin()

try:
    i2c = MicroPythonI2C(scl=12, sda=11)
    lens = QwiicHuskylens(i2c)
    lens.begin()
except:
    print("Camera Error! Check wires.")
    sys.exit()

# --- VARIABLES ---
order_id = None 
calibrated_k = None

# =========================================
# HELPER: Load Calibration
# =========================================
def load_calibration():
    print("Loading Calibration...")
    try:
        f = open('config.txt', 'r')
        data = f.read()
        f.close()
        k = float(data)
        print(f"System Calibrated! K = {k:.1f}")
        return k
    except OSError:
        print("WARNING: No Calibration Found!")
        return 2000.0 

# =========================================
# HELPER: Visual Servoing
# =========================================
def track_target(block, k_val):
    error = block.xCenter - SCREEN_CENTER_X
    turn_correction = error * TURN_GAIN
    
    forward_speed = 25
    dist_cm = 0
    
    if k_val:
        dist_cm = k_val / block.width
        if dist_cm > 30:
            forward_speed = 50
        elif dist_cm > 20:
            forward_speed = 35
        else:
            forward_speed = 20 
            
    left = forward_speed + turn_correction
    right = forward_speed - turn_correction
    
    return left, right, dist_cm

# =========================================
# MAIN LOOP
# =========================================
print("--- AMAZON BOT ONLINE ---")
calibrated_k = load_calibration()

print("Waiting for Order...")
alvik.left_led.set_color(1, 0, 1) # Purple = Idle

# PHASE 1: GET THE ORDER
while order_id is None:
    alvik.set_wheels_speed(-15, 15) # Slow spin
    if lens.request():
        for block in lens.blocks:
            if block.id > 0:
                order_id = block.id
                alvik.stop()
                print(f"ORDER RECEIVED: ITEM #{order_id}")
                for _ in range(3):
                    alvik.left_led.set_color(0, 1, 0)
                    time.sleep(0.2)
                    alvik.left_led.set_color(0, 0, 0)
                    time.sleep(0.2)
                break

# PHASE 2: FIND THE SHELF
print("Turning to Warehouse...")
alvik.set_wheels_speed(30, -30)
time.sleep(1.5) 
alvik.stop()
time.sleep(0.5)

# PHASE 3: HUNT AND DOCK (TOW TRUCK LOGIC)
print(f"Searching for Box {order_id}...")
alvik.left_led.set_color(0, 0, 1) # Blue = Hunting

job_complete = False

while not job_complete:
    # 1. Check ToF Distance
    d1, d2, d3, d4, d5 = alvik.get_distance()
    
    # STOP when we are 10cm away
    if d3 > 0 and d3 < (STOP_DISTANCE_CM * 10): 
        print("BOX REACHED. INITIATING DOCKING MANEUVER...")
        alvik.stop()
        time.sleep(0.5)
        
        # --- THE TOW TRUCK MANEUVER ---
        # 1. Spin 180 to face AWAY from box
        print("Spinning 180...")
        alvik.set_wheels_speed(40, -40)
        time.sleep(1.5) # <--- TUNE THIS TIME for perfect 180
        alvik.stop()
        
        # 2. Back Up blindly to engage hook
        print("Backing up to latch...")
        alvik.set_wheels_speed(-25, -25) # Reverse!
        time.sleep(1.5) # <--- TUNE THIS TIME to ensure latching
        
        alvik.stop()
        print("Docked.")
        job_complete = True
        break

    # 2. Check Vision
    target_block = None
    if lens.request():
        for block in lens.blocks:
            if block.id == order_id:
                target_block = block
                break
    
    # 3. Drive Logic
    if target_block:
        l, r, dist = track_target(target_block, calibrated_k)
        alvik.set_wheels_speed(l, r)
        alvik.left_led.set_color(0, 1, 0) 
    else:
        if len(lens.blocks) > 0:
            alvik.set_wheels_speed(15, -15)
        else:
            alvik.set_wheels_speed(20, -20)
        alvik.left_led.set_color(1, 0, 0) 

# PHASE 4: RETURN HOME (TOWING MODE)
print("Returning Home... SHOW ME THE ORDER TAG!")
alvik.left_led.set_color(1, 0, 1) # Purple = Returning

# NOTE: We are already facing home because we spun 180 to pick up the box!
# No extra spin needed here.

home_reached = False

while not home_reached:
    target_block = None
    
    if lens.request():
        for block in lens.blocks:
            if block.id == order_id:
                target_block = block
                break
    
    if target_block:
        l, r, dist = track_target(target_block, calibrated_k)
        
        if dist > 0 and dist < HOME_STOP_DIST_CM:
            print("HOME BASE REACHED!")
            alvik.stop()
            home_reached = True
        else:
            print(f"Homing: {dist:.1f}cm")
            alvik.set_wheels_speed(l, r)
            alvik.left_led.set_color(0, 1, 0)
    else:
        print("Where is the Manager?")
        alvik.set_wheels_speed(20, -20)
        alvik.left_led.set_color(1, 0, 0)

# MISSION COMPLETE
print("DELIVERY COMPLETE")
alvik.set_wheels_speed(0, 0)
while True:
    alvik.left_led.set_color(1, 0, 0)
    alvik.right_led.set_color(0, 0, 1)
    time.sleep(0.2)
    alvik.left_led.set_color(0, 0, 1)
    alvik.right_led.set_color(1, 0, 0)
    time.sleep(0.2)