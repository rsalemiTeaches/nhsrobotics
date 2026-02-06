# tests_core.py
# Version: V01
# Core hardware and API tests.

def test_api_integrity(bot):
    """
    Checks if critical methods exist on the SuperBot instance.
    """
    required_methods = [
        "drive_distance", 
        "approach_tag", 
        "turn_to_heading",
        "get_closest_distance",
        "get_pressed_ok",
        "center_on_tag",
        "set_nano_rgb" # New Requirement
    ]
    
    missing = []
    for method in required_methods:
        if not hasattr(bot, method):
            missing.append(method)
            
    if missing:
        return (0, f"Missing: {', '.join(missing)}")
    return (1, "All methods found")

def test_imu(bot):
    """
    Checks if the IMU returns a valid numeric Yaw.
    """
    yaw = bot.get_yaw()
    if isinstance(yaw, (int, float)):
        return (1, f"Yaw: {yaw:.1f}")
    return (0, f"Invalid Yaw: {yaw}")

def test_tof(bot):
    """
    Checks if ToF sensors return valid positive integers/floats.
    """
    dist = bot.get_closest_distance()
    if isinstance(dist, (int, float)) and dist >= 0:
        return (1, f"Dist: {dist:.1f}cm")
    return (0, "Invalid Reading")

def test_line_sensors(bot):
    """
    Checks if line sensors return valid tuple data.
    """
    # Access low-level alvik just to verify data flow
    l, c, r = bot.alvik.get_line_sensors()
    if isinstance(l, int) and isinstance(c, int):
        return (1, f"L:{l} C:{c} R:{r}")
    return (0, "Invalid Data Structure")