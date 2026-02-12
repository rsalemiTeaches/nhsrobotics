# tests_extras.py
# Version: V01
# Peripheral tests (LEDs, Screens, AI, Audio).

import time

def test_nano_led(bot):
    """
    Cycles the NanoLED to prove connectivity.
    """
    try:
        # Flash Purple to verify
        bot.set_nano_rgb(100, 0, 100)
        time.sleep(0.2)
        bot.nano_off()
        return (1, "LED Responding")
    except Exception as e:
        return (0, str(e))

def test_oled(bot):
    """
    Checks if the OLED object exists and can accept commands.
    """
    if bot.screen:
        try:
            bot.screen.show_lines("Diagnostic Mode", "Running Tests...", "Please Wait")
            return (1, "Display Active")
        except Exception as e:
            return (0, str(e))
    return (2, "Not Detected")

def test_buzzer(bot):
    """
    Checks for the Qwiic Buzzer.
    """
    if hasattr(bot, 'buzzer') and bot.buzzer and bot.buzzer.connected:
        try:
            # Quick Chirp
            bot.buzzer.set_frequency(1000)
            bot.buzzer.on()
            time.sleep(0.1)
            bot.buzzer.off()
            return (1, "Buzzer Chirped")
        except Exception as e:
            return (0, str(e))
    return (2, "Not Detected")

def test_huskylens(bot):
    """
    Pings the HuskyLens via I2C.
    """
    if bot.husky:
        try:
            # Requesting blocks proves the I2C link is alive
            bot.husky.request()
            return (1, "I2C Link OK")
        except Exception as e:
            return (0, f"Comms Fail: {e}")
    return (2, "Not Detected")
