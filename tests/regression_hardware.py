import time

def test_nano_led(bot):
    try:
        # Test RGB
        bot.nano_led.set_rgb(255, 0, 0)
        time.sleep(0.1)
        # Test Color (on/off binary)
        bot.nano_led.set_color(0, 1, 0)
        time.sleep(0.1)
        # Test Brightness
        bot.nano_led.set_brightness(50)
        time.sleep(0.1)
        # Test Off
        bot.nano_led.off()
        return 1, ""
    except Exception as e:
        return 0, str(e)

def test_motor_drive(bot):
    try:
        # Drive forward 2cm, then back 2cm
        bot.nav.drive_distance(2.0, speed_cm_s=15, blocking=True)
        bot.nav.drive_distance(-2.0, speed_cm_s=15, blocking=True)
        return 1, ""
    except Exception as e:
        # Attempt to stop just in case
        try: bot.alvik.brake()
        except: pass
        return 0, str(e)

def test_motor_rotate(bot):
    try:
        # Rotate 45 deg, then -45 deg
        bot.nav.rotate_precise(45.0)
        time.sleep(0.1)
        bot.nav.rotate_precise(-45.0)
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
        bot.btn_up.is_pressed()
        bot.btn_down.is_pressed()
        bot.btn_left.is_pressed()
        bot.btn_right.is_pressed()
        bot.btn_ok.is_pressed()
        bot.btn_cancel.is_pressed()
        return 1, ""
    except Exception as e:
        return 0, str(e)

def test_api_integrity(bot):
    # Updating required methods to reflect the new object hierarchy
    if not hasattr(bot, 'nav'):
        return 0, "Missing bot.nav"
    if not hasattr(bot, 'vision'):
        return 0, "Missing bot.vision"
    if not hasattr(bot, 'ui'):
        return 0, "Missing bot.ui"
        
    required_methods = [
        ("nav", "drive_distance"),
        ("nav", "approach_tag"),
        ("nav", "turn_to_heading"),
        (None, "get_closest_distance"),
        ("vision", "center_on_tag"),
    ]

    missing = []
    for attr, method in required_methods:
        target = bot if attr is None else getattr(bot, attr)
        if not hasattr(target, method):
            missing.append(f"{attr if attr else 'bot'}.{method}")

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

def test_servo(bot):
    try:
        # Assuming the standard Alvik servo interface
        # Adjust the range/angles based on your specific servo requirements
        bot.alvik.set_servo_positions(0,0)
        time.sleep(0.5)
        bot.alvik.set_servo_positions(90,90)
        time.sleep(0.5)
        bot.alvik.set_servo_positions(180,180)
        time.sleep(0.5)
        bot.alvik.set_servo_positions(90,90)
        return 1, "Servo sweep successful"
    except Exception as e:
        return 0, f"Servo test failed: {str(e)}"