from arduino_alvik import ArduinoAlvik, sleep_ms

def toggle_light():
    global alvik , light_on
    light_on = not light_on

alvik = ArduinoAlvik()
light_on = False
try:
    alvik.begin()
    alvik.on_touch_cancel_pressed(toggle_light)
    while True:
        sleep_ms(20)
        if light_on:
            print('light on')
            alvik.left_led.set_color(1,0,0)
        else:
            print('light off')
            alvik.left_led.set_color(0,0,0 )
finally:
    alvik.stop()