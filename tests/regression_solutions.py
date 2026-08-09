# tests/regression_solutions.py -- solution-level regression. V01
#
# Runs the real files out of solutions/, unmodified, inside the testbench.
# Every test returns (status, message) the way the rest of the suite does:
# 1 pass, 0 fail, 2 skip.

import os

from tb import scoreboard
from tb.env import Environment, solution
from tb.plant import Plant, DEFAULT_DEFECTS
from tb.stimulus import ApproachStimulus, Coverage

P08 = "sol08_line_alignment.py"
P08_STATES = ("DRIVE", "SEARCH", "ALIGN", "APPROACH")

# Bumped when a run needs longer; a run that needs more than this is a bug.
WATCHDOG_MS = 90000


def _have(name):
    return os.path.exists(solution(name))


def _run_approach(stim, watchdog_ms=WATCHDOG_MS):
    plant = Plant(line_point=(40.0, 0.0),
                  line_angle_deg=stim.line_angle_deg,
                  start=stim.start_pose(),
                  defects=stim.defects)
    env = Environment(plant=plant, watchdog_ms=watchdog_ms)
    env.run(solution(P08))
    return env


def _first_failure(*checks):
    for status, message in checks:
        if status == 0:
            return 0, message
    return 1, ""


# --------------------------------------------------------------------------
# P08 -- line alignment
# --------------------------------------------------------------------------

def test_p08_squares_up_from_one_approach():
    """One directed case, so a failure has a readable repro."""
    if not _have(P08):
        return 2, "%s not written yet" % P08
    stim = ApproachStimulus(seed=1)
    env = _run_approach(stim)
    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_squared_up(env),
        scoreboard.check_on_the_line(env),
        scoreboard.check_no_rotate(env.monitor),
        scoreboard.check_stopped_cleanly(env.monitor),
    )


def test_p08_random_approaches():
    """Generated approaches, both sides, defects on.

    This is the test that matters. Every seed puts the line somewhere
    else, aims the robot at it from a different acute angle, and picks a
    fresh theta over-report out of the measured range. The check is
    against the plant's truth, so a DUT that agrees with its own bad
    odometry still fails.
    """
    if not _have(P08):
        return 2, "%s not written yet" % P08

    coverage = Coverage()
    failures = []
    for seed in range(40):
        stim = ApproachStimulus(seed)
        env = _run_approach(stim)
        coverage.sample(stim, env.monitor)
        status, message = _first_failure(
            scoreboard.check_run_completed(env.result),
            scoreboard.check_squared_up(env),
            scoreboard.check_on_the_line(env),
        )
        if status == 0:
            failures.append("%r: %s" % (stim, message))
            if len(failures) >= 3:
                break

    holes = coverage.holes(P08_STATES)
    if failures:
        return 0, "%d/%d approaches failed. First: %s" % (
            len(failures), coverage.runs, failures[0])
    if holes:
        return 0, "all approaches passed but coverage has holes: %s" % "; ".join(holes)
    return 1, ""


def test_p08_immune_to_odometry_scale():
    """The halving claim, made executable.

    P08 works by taking half of a measured angle, so a consistent scale
    error on theta must divide out. Sweep theta_scale well past its
    measured 8-13% -- from honest to absurd -- and the robot must still
    end up square. If somebody ever "fixes" the halving toward yaw, or
    hard-codes a turn, this is what catches it.
    """
    if not _have(P08):
        return 2, "%s not written yet" % P08

    for scale in (0.80, 1.00, 1.08, 1.13, 1.50):
        stim = ApproachStimulus(seed=7)
        stim.defects["theta_scale"] = scale
        env = _run_approach(stim)
        status, message = _first_failure(
            scoreboard.check_run_completed(env.result),
            scoreboard.check_squared_up(env),
        )
        if status == 0:
            return 0, "theta_scale=%.2f: %s" % (scale, message)
    return 1, ""


def test_p08_reaches_every_state():
    if not _have(P08):
        return 2, "%s not written yet" % P08
    env = _run_approach(ApproachStimulus(seed=3))
    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_reached_states(env.monitor, P08_STATES),
    )


def test_p08_dead_sensors_never_drive():
    """Sensors that never come up must stop the run, loudly and still.

    This is the silent-failure case: a robot that treats 'no answer' as
    'no line' drives forward forever, certain the floor is clear.
    """
    if not _have(P08):
        return 2, "%s not written yet" % P08

    defects = dict(DEFAULT_DEFECTS)
    defects["sensor_dead_ms"] = 10 ** 9         # never report
    plant = Plant(defects=defects)
    env = Environment(plant=plant, watchdog_ms=20000)
    env.run(solution(P08))

    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_never_moved_before_sensors(env, env.monitor),
        scoreboard.check_lights_out(env.monitor),
    )


def test_p08_slow_sensors_still_work():
    """Sensors dead for the first 150 ms, then fine. Must still square up."""
    if not _have(P08):
        return 2, "%s not written yet" % P08
    stim = ApproachStimulus(seed=11)
    stim.defects["sensor_dead_ms"] = 150
    env = _run_approach(stim)
    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_squared_up(env),
    )


def test_p08_survives_clock_rollover():
    """Start ticks_ms() just short of its rollover.

    Anything using plain subtraction instead of ticks_diff() stops working
    the moment the counter wraps, and does it silently.
    """
    if not _have(P08):
        return 2, "%s not written yet" % P08
    stim = ApproachStimulus(seed=5)
    plant = Plant(line_point=(40.0, 0.0),
                  line_angle_deg=stim.line_angle_deg,
                  start=stim.start_pose(),
                  defects=stim.defects)
    env = Environment(plant=plant, watchdog_ms=WATCHDOG_MS,
                      start_ticks_ms=(1 << 30) - 3000)
    env.run(solution(P08))
    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_squared_up(env),
    )


def test_p08_works_with_no_screen():
    """A loose OLED shows nothing and raises nothing. The robot must still
    do its job -- no project may depend on the display to function."""
    if not _have(P08):
        return 2, "%s not written yet" % P08
    stim = ApproachStimulus(seed=13)
    stim.defects["oled_present"] = False
    env = _run_approach(stim)
    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_squared_up(env),
    )


def test_p08_cancel_stops_it():
    """Cancel held from the start: no motion, clean shutdown."""
    if not _have(P08):
        return 2, "%s not written yet" % P08

    class HoldCancel:
        def touch(self, name, env):
            return name == "cancel"

    plant = Plant()
    env = Environment(plant=plant, stimulus=HoldCancel(), watchdog_ms=20000)
    env.run(solution(P08))
    if env.result.error is not None:
        return 0, "DUT raised %s" % env.result.error
    if env.plant.distance_travelled_cm > 1.0:
        return 0, "moved %.1f cm with Cancel held" % env.plant.distance_travelled_cm
    return scoreboard.check_stopped_cleanly(env.monitor)


# --------------------------------------------------------------------------
# Every solution -- shape checks that need no per-project knowledge
# --------------------------------------------------------------------------

def _all_solutions():
    folder = os.path.dirname(solution("x"))
    return sorted(name for name in os.listdir(folder)
                  if name.startswith("sol") and name.endswith(".py"))


def test_every_solution_compiles():
    bad = []
    for name in _all_solutions():
        try:
            compile(open(solution(name)).read(), name, "exec")
        except SyntaxError as exc:
            bad.append("%s line %s: %s" % (name, exc.lineno, exc.msg))
    if bad:
        return 0, "; ".join(bad)
    return 1, ""


def test_no_solution_uses_floor_division():
    """House rule: int(a / b), never a // b."""
    bad = [name for name in _all_solutions()
           if "//" in open(solution(name)).read()]
    if bad:
        return 0, "floor division in %s" % ", ".join(bad)
    return 1, ""


def test_every_project_scaffold_compiles():
    folder = os.path.dirname(solution("x")).replace("solutions", "projects")
    bad = []
    for name in sorted(os.listdir(folder)):
        if not (name.startswith("p") and name.endswith(".py")):
            continue
        try:
            compile(open(os.path.join(folder, name)).read(), name, "exec")
        except SyntaxError as exc:
            bad.append("%s line %s: %s" % (name, exc.lineno, exc.msg))
    if bad:
        return 0, "; ".join(bad)
    return 1, ""


def test_every_scaffold_has_a_flex_line():
    folder = os.path.dirname(solution("x")).replace("solutions", "projects")
    missing = []
    for name in sorted(os.listdir(folder)):
        if not (name.startswith("p") and name.endswith(".py")):
            continue
        if "FLEX" not in open(os.path.join(folder, name)).read():
            missing.append(name)
    if missing:
        return 0, "no FLEX line in %s" % ", ".join(missing)
    return 1, ""


def coverage_report():
    """Run the generated approaches once more, purely to print coverage."""
    if not _have(P08):
        return "  P08 not written yet"
    coverage = Coverage()
    for seed in range(40):
        stim = ApproachStimulus(seed)
        env = _run_approach(stim)
        coverage.sample(stim, env.monitor)
    return coverage.report(P08_STATES)
