# tests/tb/fakes/nhs_robotics/__init__.py -- SuperBot's stand-in. V01
#
# NOT the real SuperBot. The real one needs I2C, a Qwiic bus and an OLED,
# none of which exist on a laptop.
#
# One rule kept deliberately: anything the real SuperBot computes, this
# one computes the same way, by calling the same helper. closest_valid()
# is imported from the real library rather than reimplemented, so a change
# to the real rule shows up here instead of being quietly mirrored. If a
# fake reimplements the thing under test, it stops being a test.

from tb import wiring

try:
    from nhs_robotics.superbot import SuperBot as _RealSuperBot
    _closest_valid = _RealSuperBot.closest_valid
except Exception:                                    # pragma: no cover
    def _closest_valid(readings):
        usable = [r for r in readings if r is not None and r > 0]
        return min(usable) if usable else 999


NO_READING_CM = 999


class NanoLED:
    def __init__(self):
        self.rgb = (0, 0, 0)

    def set_rgb(self, red, green, blue):
        self.rgb = (red, green, blue)
        wiring.active().monitor.record("nano_led", self.rgb)

    def off(self):
        self.set_rgb(0, 0, 0)


class Button:
    """Rising-edge detector, same contract as the real one."""

    def __init__(self, getter):
        self._getter = getter
        self._was_down = False

    def is_pressed(self):
        now_down = bool(self._getter())
        fired = now_down and not self._was_down
        self._was_down = now_down
        return fired


class SuperBot:
    TOUCH_NAMES = ('up', 'down', 'left', 'right', 'ok', 'cancel')

    def __init__(self, alvik):
        self.alvik = alvik
        self.nano_led = NanoLED()
        self._edges = {name: Button(lambda n=name: wiring.active().touch(n))
                       for name in self.TOUCH_NAMES}

    # --- sensing ---

    def get_closest_distance(self):
        return _closest_valid(self.alvik.get_distance())

    def get_yaw(self):
        return self.alvik.get_orientation()[2]

    # --- buttons ---

    def _check(self, name):
        if name not in self.TOUCH_NAMES:
            raise ValueError(
                "No touch button named '%s'. Valid names: %s"
                % (name, ", ".join(self.TOUCH_NAMES)))

    def held(self, name):
        self._check(name)
        return wiring.active().touch(name)

    def pressed(self, name):
        self._check(name)
        return self._edges[name].is_pressed()

    # --- output ---

    def light_both_leds(self, red, green, blue):
        self.alvik.left_led.set_color(red, green, blue)
        self.alvik.right_led.set_color(red, green, blue)

    def update_display(self, line1, line2="", line3=""):
        env = wiring.active()
        if not env.plant.defects["oled_present"]:
            # A dead OLED shows nothing and raises nothing. Modelled, so a
            # test can prove a project does not depend on the screen.
            return
        env.monitor.record("display", str(line1), str(line2), str(line3))

    def log_info(self, *args, sep=' '):
        wiring.active().monitor.record("log", sep.join(str(a) for a in args))


class RobotGamepad:
    """The controller, driven by the environment's stimulus.

    The real constructor blocks until a controller connects. Here it
    returns at once, and the environment supplies stick and button values.
    """

    BUTTON_NAMES = ('cross', 'circle', 'square', 'triangle', 'L1', 'R1',
                    'L2', 'R2', 'share', 'options', 'L3', 'R3',
                    'up', 'down', 'left', 'right', 'ps')

    def __init__(self, alvik, password="password"):
        self.alvik = alvik
        self._edges = {name: Button(lambda n=name: wiring.active().button(n))
                       for name in self.BUTTON_NAMES}
        wiring.active().monitor.record("gamepad_connected")

    def update(self):
        wiring.active().monitor.record("gamepad_update")

    @property
    def left_y(self):
        return wiring.active().stick("left_y")

    @property
    def right_y(self):
        return wiring.active().stick("right_y")

    @property
    def left_x(self):
        return wiring.active().stick("left_x")

    @property
    def right_x(self):
        return wiring.active().stick("right_x")

    def held(self, name):
        if name not in self.BUTTON_NAMES:
            raise ValueError("No button named '%s'" % name)
        return wiring.active().button(name)

    def pressed(self, name):
        if name not in self.BUTTON_NAMES:
            raise ValueError("No button named '%s'" % name)
        return self._edges[name].is_pressed()
