from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# Initialize Hardware
alvik = ArduinoAlvik()
alvik.begin()

# Initialize SuperBot
sb = SuperBot(alvik)
sb.enable_info_logging()

sb.log_info("--- HUSKYLENS TEST (V_FINAL) ---")

if sb.husky is None:
    sb.log_error("CRITICAL FAILURE: HuskyLens not found.")
else:
    sb.log_info("SUCCESS: HuskyLens connected.")
    sb.log_info("Scanning... Using .xCenter and .yCenter")

    try:
        for i in range(20): # Run for ~10 seconds
            sb.husky.request()
            blocks = sb.husky.blocks
            
            if len(blocks) > 0:
                sb.log_info(f"[{i}] Saw {len(blocks)} tags:")
                for b in blocks:
                    # Use the correct attributes from qwiic_huskylens.py class Block
                    # Attributes: xCenter, yCenter, width, height, id
                    
                    try:
                        tag_id = b.id
                        x = b.xCenter
                        y = b.yCenter
                        width = b.width
                        height = b.height
                        
                        sb.log_info(f"   -> ID: {tag_id} | Pos: ({x}, {y}) | Size: {width}x{height}")
                    except AttributeError as e:
                        # Fallback if there is still a mismatch
                        sb.log_error(f"Attribute Error: {e}")
                        sb.log_error(f"Object details: {dir(b)}")
                        
            else:
                print(".", end="")
            
            time.sleep(0.5)

    except Exception as e:
        sb.log_error(f"Loop Error: {e}")

sb.log_info("\n--- TEST END ---")