from arduino_alvik import ArduinoAlvik

# Initialize the robot
alvik = ArduinoAlvik()

# Print the library version
print("Library Version:", alvik.get_lib_version())

# Optional: Print the internal STM32 carrier firmware version as well
print("Firmware Version:", alvik.get_fw_version())

# Start the internal UART communication with the carrier board
alvik.begin()
print("")

# Check the version again
print("Firmware Version:", alvik.get_fw_version())
percentage = alvik.get_battery_charge()
is_charging = alvik.is_battery_charging()
print("--- Alvik Battery Status ---")
print(f"Charge Level: {percentage}%")
if is_charging:
    print("Status: Plugged in and Charging")
else:
    print("Status: Running on Battery")
print("--------------------------")