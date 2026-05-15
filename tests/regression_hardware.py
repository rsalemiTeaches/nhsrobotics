import time

def test_nano_led(bot):
    try:
        # Test RGB
        bot.set_nano_rgb(255, 0, 0)
        time.sleep(0.1)
        # Test Color (on/off binary)
        bot.set_nano_color(0, 1, 0)
        time.sleep(0.1)
        # Test Brightness
        bot.set_nano_brightness(50)
        time.sleep(0.1)
        # Test Off
        bot.nano_off()
        return 1, ""
    except Exception as e:
        return 0, str(e)

def test_motor_drive(bot):
    try:
        # Drive forward 2cm, then back 2cm
        bot.drive_distance(2.0, speed_cm_s=15, blocking=True)
        bot.drive_distance(-2.0, speed_cm_s=15, blocking=True)
        return 1, ""
    except Exception as e:
        # Attempt to stop just in case
        try: bot.alvik.brake()
        except: pass
        return 0, str(e)

def test_motor_rotate(bot):
    try:
        # Rotate 45 deg, then -45 deg
        bot.rotate_precise(45.0)
        time.sleep(0.1)
        bot.rotate_precise(-45.0)
        return 1, ""
    except Exception as e:
        try: bot.alvik.brake()
        except: pass
        return 0, str(e)

def test_sensor_yaw(bot):
    try:
        yaw = bot.get_yaw()
        if not isinstance(yaw, (int, float)):
            return 0, f"Invalid yaw type: {type(yaw)}"
        return 1, f"Yaw: {yaw:.1f}"
    except Exception as e:
        return 0, str(e)

def test_buttons(bot):
    try:
        # Just ensure they don't crash when called
        bot.get_pressed_up()
        bot.get_pressed_down()
        bot.get_pressed_left()
        bot.get_pressed_right()
        bot.get_pressed_ok()
        bot.get_pressed_cancel()
        return 1, ""
    except Exception as e:
        return 0, str(e)

def test_api_integrity(bot):
    required_methods = [
        "drive_distance",
        "approach_tag",
        "turn_to_heading",
        "get_closest_distance",
        "get_pressed_ok",
        "center_on_tag",
        "set_nano_rgb"
    ]

    missing = []
    for method in required_methods:
        if not hasattr(bot, method):
            missing.append(method)

    if missing:
        return 0, f"Missing: {', '.join(missing)}"
    return 1, ""

def test_tof(bot):
    try:
        dist = bot.get_closest_distance()
        if isinstance(dist, (int, float)) and dist >= 0:
            return 1, f"Dist: {dist:.1f}cm"
        return 0, "Invalid Reading"
    except Exception as e:
        return 0, str(e)

def test_line_sensors(bot):
    try:
        l, c, r = bot.alvik.get_line_sensors()
        if isinstance(l, int) and isinstance(c, int):
            return 1, f"L:{l} C:{c} R:{r}"
        return 0, "Invalid Data Structure"
    except Exception as e:
        return 0, str(e)

def test_builtin_leds(bot):
    import time
    try:
        bot.alvik.left_led.set_color(0, 1, 0)
        bot.alvik.right_led.set_color(0, 1, 0)
        time.sleep(0.1)
        bot.alvik.left_led.set_color(0, 0, 0)
        bot.alvik.right_led.set_color(0, 0, 0)
        return 1, ""
    except Exception as e:
        return 0, str(e)
