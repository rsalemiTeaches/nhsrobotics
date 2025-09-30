from arduino_alvik import ArduinoAlvik
alvik = ArduinoAlvik()
alvik.begin()
percentage = alvik.get_battery_charge()
is_charging = alvik.is_battery_charging()
print("--- Alvik Battery Status ---")
print(f"Charge Level: {percentage}%")
if is_charging:
    print("Status: Plugged in and Charging")
else:
    print("Status: Running on Battery")
print("--------------------------")
