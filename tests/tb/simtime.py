# tests/tb/simtime.py -- the simulation clock. V01
#
# The DUT imports `time` and calls ticks_ms(), ticks_diff() and sleep_ms().
# Those are MicroPython names that CPython does not have, so a shim is
# required whatever we do. Making the shim the simulation clock buys three
# things: the regression runs in zero wall time, it is deterministic, and
# the DUT's own sleep becomes the tick that advances the world model.
#
# Nothing in the testbench reads this clock. It exists only for the DUT.


class SimTime:
    """Stands in for the `time` module while a DUT runs.

    Only the calls the course actually uses are implemented. Anything else
    raising AttributeError is the point -- it means a project started using
    a time API the testbench does not model, and that should be a loud
    failure rather than a silent real-time call.
    """

    # ticks_ms() rolls over here, the way MicroPython's does. Deliberately
    # small so a test can drive a run across the boundary in reasonable
    # sim time and prove ticks_diff() is being used instead of subtraction.
    TICKS_PERIOD = 1 << 30
    TICKS_HALF = TICKS_PERIOD // 2

    def __init__(self, on_advance=None, start_ms=0):
        self.now_ms = 0
        self.origin_ms = start_ms      # what ticks_ms() reports at now_ms = 0
        self._on_advance = on_advance

    # --- the world advances only through here ---

    def advance(self, dt_ms):
        """Push simulated time forward and step whatever is watching."""
        if dt_ms <= 0:
            return
        self.now_ms += dt_ms
        if self._on_advance is not None:
            self._on_advance(dt_ms)

    # --- the MicroPython time API the course uses ---

    def ticks_ms(self):
        return (self.origin_ms + self.now_ms) % self.TICKS_PERIOD

    def ticks_diff(self, later, earlier):
        """Signed difference, wrap-aware, exactly like MicroPython's."""
        diff = (later - earlier) % self.TICKS_PERIOD
        if diff >= self.TICKS_HALF:
            diff -= self.TICKS_PERIOD
        return diff

    def sleep(self, seconds):
        self.advance(int(seconds * 1000))

    def sleep_ms(self, milliseconds):
        self.advance(int(milliseconds))

    def sleep_us(self, microseconds):
        self.advance(int(microseconds) // 1000)

    def monotonic(self):
        return (self.origin_ms + self.now_ms) / 1000.0
