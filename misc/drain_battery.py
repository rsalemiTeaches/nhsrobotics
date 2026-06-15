from arduino_alvik import ArduinoAlvik
from nhs_robotics import SuperBot
import time

# Initialize the base Alvik robot and hardware threads
alvik = ArduinoAlvik()
alvik.begin()

# Initialize the custom high school library layer
sb = SuperBot(alvik)

# --- CONFIGURATION CONSTANTS (Percentages) ---
TARGET_STORAGE_CHARGE = 50      # Target storage capacity percentage (~3.85V equivalent)
START_MAX_CHARGE = 100          # Maximum baseline percentage for color mapping scale
DRAIN_MOTOR_SPEED = 100         # Direct power percentage (using "%") for maximum velocity
CHECK_INTERVAL_MS = 1000        # Interval for polling battery health (1 second)

try:
    print("---------------------------------------")
    print(" ALVIK DYNAMIC PERCENTAGE DRAINER      ")
    print(f" Target Storage Window: {TARGET_STORAGE_CHARGE}%")
    print(" NanoLED Code: Red (Full) -> Green (Near Target)")
    print("---------------------------------------")

    storage_charge_reached = False
    last_check_time = time.ticks_ms()

    while not alvik.get_touch_cancel():
        now = time.ticks_ms()

        # Non-blocking state check every 1 second
        if time.ticks_diff(now, last_check_time) >= CHECK_INTERVAL_MS:
            last_check_time = now
            
            # Fetch the real-time battery charge percentage (returns an integer value like 63)
            current_charge = alvik.get_battery_charge()
            print(f"Current Battery Status: {current_charge:.1f}%")

            if current_charge > TARGET_STORAGE_CHARGE:
                # --- ACTIVE HIGH-DRAIN STATE ---
                storage_charge_reached = False
                
                # Calculate progress from START_MAX_CHARGE down to TARGET_STORAGE_CHARGE (0.0 to 1.0)
                bounded_charge = min(max(current_charge, TARGET_STORAGE_CHARGE), START_MAX_CHARGE)
                total_range = START_MAX_CHARGE - TARGET_STORAGE_CHARGE
                progress = (START_MAX_CHARGE - bounded_charge) / total_range
                
                # Map progress to Red and Green channels (0-255)
                red_intensity = int((1.0 - progress) * 255)
                green_intensity = int(progress * 255)
                
                # Apply the dynamic color mix directly via SuperBot's wrapper
                sb.set_nano_rgb(red_intensity, green_intensity, 0)
                
                # Keep main headlights full white for extra power consumption
                alvik.left_led.set_color(1, 1, 1)
                alvik.right_led.set_color(1, 1, 1)
                
                # Spin in place on the foamboard using direct power percentage for maximum velocity
                alvik.set_wheels_speed(DRAIN_MOTOR_SPEED, -DRAIN_MOTOR_SPEED, "%")
                
            else:
                # --- TARGET MET STATE (OR MONITORING REBOUND) ---
                alvik.brake()
                time.sleep_ms(100) # Give the battery a moment to drop its load surface charge
                resting_charge = alvik.get_battery_charge()
                
                # If it rests below or exactly at target, it is officially done
                if resting_charge <= TARGET_STORAGE_CHARGE:
                    storage_charge_reached = True
                    
                    # Target notification state: Solid Purple Headlights
                    alvik.left_led.set_color(1, 0, 1)
                    alvik.right_led.set_color(1, 0, 1)
                    
                    # Turn off the dynamic NanoLED using SuperBot's native command
                    sb.nano_off() 
                    
                    print(f"--> Storage ready stabilized at: {resting_charge:.1f}%")
                    sb.update_display("BATTERY READY", f"CHARGE: {resting_charge:.1f}%", "PULL BATTERY NOW")
                    
                    # Break out of loop to finish the script
                    break
                else:
                    print(f"--> Load dropped. Battery rebounded to {resting_charge:.1f}%. Re-draining...")

except Exception as e:
    print(f"Unexpected execution interruption: {e}")

finally:
    # --- FOOLPROOF SAFETY SHUTDOWN CLEANUP ---
    print("Shutting down scripts and cleaning up robot environment...")
    alvik.brake()
    
    # Clean up LEDs to default off states if program was cancelled/aborted
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    sb.nano_off()
    alvik.stop()
    print("Robot safe and script finished.")