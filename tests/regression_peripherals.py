def test_oled(bot):
    if bot.ui.screen is None:
        return 2, "OLED not connected"
    try:
        bot.ui.screen.show_lines("Regression Test", "Testing...", "OLED OK")
        return 1, ""
    except Exception as e:
        return 0, str(e)

def test_buzzer(bot):
    if bot.ui.buzzer is None or not bot.ui.buzzer.connected:
        return 2, "Buzzer not connected"
    try:
        bot.ui.buzzer.play_effect(bot.ui.buzzer.EFFECT_YES)
        return 1, ""
    except Exception as e:
        return 0, str(e)

def test_huskylens(bot):
    if bot.vision.husky is None:
        return 2, "HuskyLens not connected"
    try:
        bot.vision.husky.request()
        return 1, ""
    except Exception as e:
        return 0, str(e)

def test_gamepad_init(bot):
    try:
        from nhs_robotics import RobotGamepad
        import time
        # We don't want to block forever waiting for connection during a regression test
        # So we'll just instantiate the underlying Controller directly to test hardware init
        from controller import Controller
        pad = Controller(verbose=False)
        # Process one update tick
        pad.update()
        return 1, "Controller initialized and updated"
    except ImportError:
        return 2, "Hardware modules not found (must run on Alvik)"
    except Exception as e:
        return 0, str(e)
