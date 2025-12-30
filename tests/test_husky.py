from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# Initialize Hardware
alvik = ArduinoAlvik()
alvik.begin()

# Initialize SuperBot
# SuperBot attempts to initialize self.husky during __init__
sb = SuperBot(alvik)
sb.enable_info_logging()

sb.log_info("--- HUSKYLENS TEST ---")

# 1. Check if the object exists
if sb.husky is None:
    sb.log_error("CRITICAL FAILURE: HuskyLens not found.")
    sb.log_error("Diagnostics:")
    sb.log_error("1. Check the I2C cable connection on the robot.")
    sb.log_error("2. Ensure the HuskyLens screen is turning ON.")
    sb.log_error("3. Try unplugging and replugging the camera.")
else:
    sb.log_info("SUCCESS: HuskyLens connected.")
    sb.log_info("Starting Scan Loop (10 seconds)...")

    # 2. Run a short scan loop
    try:
        for i in range(20): # Run for ~10 seconds
            # Update data from camera
            sb.husky.request()
            
            # Check for detected blocks/tags
            blocks = sb.husky.blocks
            
            if len(blocks) > 0:
                sb.log_info(f"[{i}] Saw {len(blocks)} tags:")
                for b in blocks:
                    # Print ID and Position
                    # We use getattr just in case attributes differ, but .id/.x/.y are standard
                    tag_id = getattr(b, 'id', '?')
                    x = getattr(b, 'x', '?')
                    y = getattr(b, 'y', '?')
                    sb.log_info(f"   -> ID: {tag_id} | Pos: ({x}, {y})")
            else:
                # Print a dot to show the program is running but sees nothing
                print(".", end="")
            
            time.sleep(0.5)

    except Exception as e:
        sb.log_error(f"Loop Error: {e}")

sb.log_info("\n--- TEST END ---")