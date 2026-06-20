import time
import ubinascii
import machine

class RobotGamepad:
    def __init__(self, alvik, password="password"):
        from controller import Controller
        self.alvik = alvik
        
        ssid = "Alvik-" + ubinascii.hexlify(machine.unique_id()).decode('utf-8').upper()[-4:]
        self.controller = Controller(ssid=ssid, password=password)
        
        print(f"Starting Wi-Fi Access Point... SSID: {ssid}")
        print("Waiting for connection... Connect phone and press a button.")
        
        led_toggle = False
        while not self.controller.is_connected():
            self.controller.update()
            if led_toggle:
                self.alvik.left_led.set_color(1, 1, 0)
                self.alvik.right_led.set_color(1, 1, 0)
            else:
                self.alvik.left_led.set_color(0, 0, 0)
                self.alvik.right_led.set_color(0, 0, 0)
            led_toggle = not led_toggle
            time.sleep(0.2)
            
        print("Connected!")
        # Set to connected color (green) by default
        self.alvik.left_led.set_color(0, 1, 0)
        self.alvik.right_led.set_color(0, 1, 0)

    def update(self):
        self.controller.update()

    @property
    def left_y(self):
        return self.controller.left_y

    @property
    def right_y(self):
        return self.controller.right_y

    @property
    def buttons(self):
        return self.controller.buttons
