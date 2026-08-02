import time
import ubinascii
import machine

from .peripherals import Button

class RobotGamepad:

    # A resting thumbstick still reports a little noise. Anything smaller
    # than this counts as centered. Raise it if a controller drifts.
    STICK_DEADZONE = 0.05

    # Every button the controller reports, in the order the packet sends them.
    BUTTON_NAMES = ('cross', 'circle', 'square', 'triangle', 'L1', 'R1',
                    'L2', 'R2', 'share', 'options', 'L3', 'R3',
                    'up', 'down', 'left', 'right', 'ps')

    def __init__(self, alvik, password="password"):
        from controller import Controller
        self.alvik = alvik

        # One rising-edge detector per button, so pressed() works without
        # anyone outside this class having to build a Button.
        self._edges = {}
        for name in self.BUTTON_NAMES:
            self._edges[name] = Button(self._make_getter(name))
        
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

    @classmethod
    def _centered(cls, value):
        """Report a resting stick as exactly 0.0.

        The deadzone is applied here, inside the properties, so nobody using
        this class has to remember it. Raw values are still reachable at
        gamepad.controller.left_y if you ever need to retune STICK_DEADZONE.
        """
        if -cls.STICK_DEADZONE < value < cls.STICK_DEADZONE:
            return 0.0
        return value

    @property
    def left_y(self):
        return self._centered(self.controller.left_y)

    @property
    def right_y(self):
        return self._centered(self.controller.right_y)

    @property
    def left_x(self):
        return self._centered(self.controller.left_x)

    @property
    def right_x(self):
        return self._centered(self.controller.right_x)

    @property
    def buttons(self):
        return self.controller.buttons

    def _make_getter(self, name):
        """A function that reports whether one button is down right now."""
        def getter():
            return bool(self.controller.buttons.get(name, False))
        return getter

    def _check(self, name):
        if name not in self._edges:
            raise ValueError(
                "No gamepad button named '%s'. Valid names: %s"
                % (name, ", ".join(self.BUTTON_NAMES)))

    def held(self, name):
        """True the whole time the button is down."""
        self._check(name)
        return bool(self.controller.buttons.get(name, False))

    def pressed(self, name):
        """True only at the instant the button goes down.

        One push gives one True, however long you hold it.
        """
        self._check(name)
        return self._edges[name].is_pressed()
