# tests/test_gamepad.py
# Standalone test to verify PS5 controller functionality with Arduino Alvik and SuperBot.
# This must be run directly on the MicroPython hardware.

import time
import sys

# Standard imports for Alvik testing
try:
    from arduino_alvik import ArduinoAlvik
    from nhs_robotics import SuperBot
    from controller import Controller
except ImportError:
    print("[SKIP] test_gamepad - Hardware modules not found (must run on Alvik)")
    sys.exit(0)

def test_gamepad():
    print("Initializing Alvik...")
    alvik = ArduinoAlvik()
    alvik.begin()

    print("Initializing SuperBot...")
    bot = SuperBot(alvik)

    print("Initializing Web Controller...")
    # This sets up the AP 'Alvik-Link' and starts the server
    pad = Controller(verbose=True)

    print("="*40)
    print("Gamepad Test Ready!")
    print(f"Connect to Wi-Fi: {pad.ssid}")
    print(f"Password: {pad.password}")
    print("Open http://192.168.4.1 in browser")
    print("="*40)
    print("Controls:")
    print("  Left Stick Y: Left Motor")
    print("  Right Stick Y: Right Motor")
    print("  Cross: Buzzer")
    print("  Square: OLED Display")
    print("  Triangle: NanoLED")
    print("  Circle: Built-in LEDs")
    print("  Press 'Options' to exit test.")
    print("="*40)

    running = True
    while running:
        # 1. Update the controller (receives web requests non-blocking)
        pad.update()

        # Only process inputs if connected
        if pad.is_connected():

            # --- Tank Drive ---
            # Stick Y values are -1.0 to 1.0.
            # Controller web UI inverts Y axes so pushing up is positive.
            left_speed = pad.left_stick_y * 100  # Scale to -100...100
            right_speed = pad.right_stick_y * 100

            # Apply deadzone just in case
            if abs(left_speed) < 10: left_speed = 0
            if abs(right_speed) < 10: right_speed = 0

            # Set motor speeds directly
            alvik.set_wheels_speed(left_speed, right_speed)

            # --- Peripherals ---

            # Cross -> Buzzer
            if pad.buttons.get('cross'):
                print("[PASS] Cross pressed - Buzzing!")
                bot.buzz()

            # Square -> OLED
            if pad.buttons.get('square'):
                print("[PASS] Square pressed - OLED Text!")
                bot.text("Gamepad", 0, 0)
                bot.text("Square!", 0, 20)
                bot.show()
                time.sleep(0.1) # Debounce

            # Triangle -> NanoLED
            if pad.buttons.get('triangle'):
                print("[PASS] Triangle pressed - NanoLED!")
                bot.lights(255, 0, 0) # Red
            else:
                bot.lights(0, 0, 0) # Off

            # Circle -> Built-in LEDs (using alvik base directly as bot doesn't wrap it)
            if pad.buttons.get('circle'):
                print("[PASS] Circle pressed - Built-in LEDs!")
                alvik.left_led.set_color(0, 255, 0) # Green
                alvik.right_led.set_color(0, 255, 0)
            else:
                alvik.left_led.set_color(0, 0, 0)
                alvik.right_led.set_color(0, 0, 0)

            # Exit condition
            if pad.buttons.get('options'):
                print("Options pressed. Exiting.")
                running = False

        else:
            # Safety stop if disconnected
            alvik.set_wheels_speed(0, 0)
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)
            bot.lights(0, 0, 0)

        # Short sleep to prevent busy waiting
        time.sleep(0.02)

    # Cleanup
    alvik.set_wheels_speed(0, 0)
    print("Gamepad test finished.")

if __name__ == "__main__":
    test_gamepad()
