# tests/tb/env.py -- the environment. V01
#
# Wires plant, clock, monitor and fakes together, runs one solution file
# unmodified, and hands back the result.
#
# The DUT is never edited to be testable. It is a module-level script that
# builds its own ArduinoAlvik and SuperBot and loops until something stops
# it, so the environment works by making those names resolve to fakes:
# tests/tb/fakes goes on the front of sys.path, and `time` is replaced in
# sys.modules for the duration of the run. Both are restored afterwards.

import os
import sys
import traceback

from tb import wiring
from tb.simtime import SimTime
from tb.plant import Plant
from tb.monitor import Monitor

HERE = os.path.dirname(os.path.abspath(__file__))
FAKES = os.path.join(HERE, "fakes")
REPO = os.path.dirname(os.path.dirname(HERE))

# Modules the fakes shadow. Any real copy already imported has to be moved
# aside for the run, or `from nhs_robotics import SuperBot` inside the DUT
# picks up the real one and immediately reaches for I2C.
SHADOWED = ("arduino_alvik", "nhs_robotics", "time")


class RunResult:
    def __init__(self):
        self.finished = False       # DUT returned on its own
        self.watchdog = False       # we had to force cancel
        self.error = None           # exception the DUT raised
        self.traceback = ""
        self.sim_ms = 0

    @property
    def ok(self):
        return self.error is None

    def __repr__(self):
        if self.error:
            return "<run FAILED %r after %d ms>" % (self.error, self.sim_ms)
        return "<run %s after %d ms>" % (
            "watchdog" if self.watchdog else "finished", self.sim_ms)


class Environment:
    """One run of one solution against one plant.

    stimulus is an optional object with any of:
        touch(name, env)   -> bool
        button(name, env)  -> bool
        stick(name, env)   -> float
    Anything it does not provide reads as not-pressed / centred.
    """

    def __init__(self, plant=None, stimulus=None, watchdog_ms=60000,
                 tick_ms=10, start_ticks_ms=0):
        self.plant = plant or Plant()
        self.stimulus = stimulus
        self.watchdog_ms = watchdog_ms
        self.tick_ms = tick_ms
        self.clock = SimTime(on_advance=self._on_advance,
                             start_ms=start_ticks_ms)
        self.monitor = Monitor(self.clock)
        self.forced_cancel = False
        self.result = RunResult()

    # ---------- time ----------

    def _on_advance(self, dt_ms):
        # Step the plant in small slices so a long sleep cannot jump the
        # robot straight past the line.
        remaining = dt_ms
        while remaining > 0:
            slice_ms = min(self.tick_ms, remaining)
            self.plant.step(slice_ms)
            remaining -= slice_ms
        if self.clock.now_ms >= self.watchdog_ms:
            self.forced_cancel = True

    # ---------- stimulus ----------

    def touch(self, name):
        if name == "cancel" and self.forced_cancel:
            return True
        if self.stimulus and hasattr(self.stimulus, "touch"):
            return bool(self.stimulus.touch(name, self))
        return False

    def button(self, name):
        if name == "options" and self.forced_cancel:
            return True
        if self.stimulus and hasattr(self.stimulus, "button"):
            return bool(self.stimulus.button(name, self))
        return False

    def stick(self, name):
        if self.stimulus and hasattr(self.stimulus, "stick"):
            return float(self.stimulus.stick(name, self))
        return 0.0

    # ---------- running a DUT ----------

    def run(self, dut_path):
        """Execute a solution file with the fakes installed."""
        source = open(dut_path).read()
        saved_path = list(sys.path)
        saved_modules = {name: sys.modules.pop(name)
                         for name in SHADOWED if name in sys.modules}

        sys.path.insert(0, FAKES)
        sys.modules["time"] = self.clock
        previous = wiring.ACTIVE
        wiring.ACTIVE = self

        namespace = {"__name__": "__dut__", "__file__": dut_path}
        try:
            exec(compile(source, dut_path, "exec"), namespace)
            self.result.finished = True
        except BaseException as exc:                  # noqa: BLE001
            self.result.error = exc
            self.result.traceback = traceback.format_exc()
        finally:
            wiring.ACTIVE = previous
            sys.path[:] = saved_path
            sys.modules.pop("time", None)
            for name, module in saved_modules.items():
                sys.modules[name] = module
            import time as _real_time       # restore a real one for the TB
            sys.modules["time"] = _real_time

        self.result.watchdog = self.forced_cancel
        self.result.sim_ms = self.clock.now_ms
        self.namespace = namespace
        return self.result


def solution(name):
    """Absolute path to a file in solutions/."""
    return os.path.join(REPO, "solutions", name)


def project(name):
    return os.path.join(REPO, "projects", name)
