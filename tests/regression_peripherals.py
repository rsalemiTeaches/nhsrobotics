def test_oled(bot):
    if bot.screen is None:
        return 2, "OLED not connected"
    try:
        bot.screen.show_lines("Regression Test", "Testing...", "OLED OK")
        return 1, ""
    except Exception as e:
        return 0, str(e)

def test_buzzer(bot):
    if bot.buzzer is None or not bot.buzzer.connected:
        return 2, "Buzzer not connected"
    try:
        bot.buzzer.play_effect(bot.buzzer.EFFECT_YES)
        return 1, ""
    except Exception as e:
        return 0, str(e)

def test_huskylens(bot):
    if bot.husky is None:
        return 2, "HuskyLens not connected"
    try:
        bot.husky.request()
        return 1, ""
    except Exception as e:
        return 0, str(e)
