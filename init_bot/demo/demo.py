from arduino_alvik import ArduinoAlvik
from time import sleep_ms

from demo.line_follower import run_line_follower
from demo.touch_move import run_touch_move
from demo.hand_follower import run_hand_follower
from demo.color_maze_runner import run_color_maze_runner
from demo.sumo_rev0 import run_sumo

alvik = ArduinoAlvik()
alvik.begin()

menu_status = 0


def update_led_status(val):
    if val == 0:
        alvik.left_led.set_color(0, 0, 1)
        alvik.right_led.set_color(0, 0, 1)
    elif val == 1:
        alvik.left_led.set_color(0, 1, 0)
        alvik.right_led.set_color(0, 1, 0)
    elif val == 2:
        alvik.left_led.set_color(1, 0, 1)
        alvik.right_led.set_color(1, 0, 1)    
    elif val == 3:
        alvik.left_led.set_color(1, 0, 0)
        alvik.right_led.set_color(1, 0, 0)
    elif val == 4:
        alvik.left_led.set_color(1, 1, 0)
        alvik.right_led.set_color(1, 1, 0)


while True:

    update_led_status(menu_status)

    try:

        if alvik.get_touch_ok():
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)
            sleep_ms(500)
            while not alvik.get_touch_cancel():
                if menu_status == 0:
                    print("run_line_follower")
                    run_line_follower(alvik)
                if menu_status == 1:
                    print("run_hand_follower")
                    run_hand_follower(alvik)
                if menu_status == 2:
                    print("run_touch_move")
                    if run_touch_move(alvik) < 0:
                        break
                if menu_status == 3:
                    print("run_color_maze_runner")
                    run_color_maze_runner(alvik)
                if menu_status == 4:
                    print("run_sumo")
                    run_sumo(alvik)
            alvik.left_led.set_color(0, 0, 0)
            alvik.right_led.set_color(0, 0, 0)
            sleep_ms(500)
            alvik.brake()

        if alvik.get_touch_up() and menu_status < 5:
            menu_status += 1
            update_led_status(menu_status)
            while alvik.get_touch_up():
                sleep_ms(100)
        if alvik.get_touch_down() and menu_status > 0:
            menu_status -= 1
            update_led_status(menu_status)
            while alvik.get_touch_down():
                sleep_ms(100)

        sleep_ms(100)

    except KeyboardInterrupt as e:
        print('over')
        alvik.stop()
        break
