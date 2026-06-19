from .peripherals import OLED, Buzzer

class RobotUI:
    def __init__(self, i2c_driver, qwiic_driver):
        self.screen = None
        self.buzzer = None
        
        # Setup OLED
        if i2c_driver:
            try:
                self.screen = OLED(i2c_driver=i2c_driver)
                self.screen.show_lines("SuperBot", "Online", "V60")
            except Exception as e:
                print(f"OLED Init Error: {e}")
                
        # Setup Buzzer
        if qwiic_driver:
            try:
                self.buzzer = Buzzer(i2c_driver=qwiic_driver)
                if self.buzzer._buzzer and self.buzzer._buzzer.is_connected():
                    self.buzzer.connected = True
                else:
                    self.buzzer.connected = False
            except Exception as e:
                print(f"Buzzer Init Error: {e}")
                self.buzzer = None

    def update_display(self, line1, line2="", line3=""):
        if self.screen:
            try:
                l1 = str(line1)
                l2 = str(line2)
                l3 = str(line3)
                if l2 == "" and l3 == "" and len(l1) > 16:
                    l2 = l1[16:32]
                    l3 = l1[32:48]
                    l1 = l1[0:16]
                self.screen.show_lines(l1, l2, l3)
            except Exception as e:
                print(f"OLED Update Error: {e}")

    def log_info(self, *args, sep=' '):
        message = sep.join(str(arg) for arg in args)
        print(message)
        self.update_display(message)

    def log_error(self, *args, sep=' '):
        base_message = sep.join(str(arg) for arg in args)
        full_msg = f"ERROR: {base_message}"
        print(full_msg)
        self.update_display(full_msg)

    def play_effect(self, effect_number):
        if self.buzzer and self.buzzer.connected:
            self.buzzer.play_effect(effect_number)
