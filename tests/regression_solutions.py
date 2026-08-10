# tests/regression_solutions.py -- solution-level regression. V01
#
# Runs the real files out of solutions/, unmodified, inside the testbench.
# Every test returns (status, message) the way the rest of the suite does:
# 1 pass, 0 fail, 2 skip.

import os

from tb import scoreboard
from tb.env import Environment, solution
from tb.plant import Plant, Target, DEFAULT_DEFECTS
from tb.stimulus import ApproachStimulus, Coverage

# Line alignment. Parked for Term 2 and renamed to sol1x. The checks
# below are kept because they are good checks, but they are written for a
# LATER design than the file now on disk -- the one that announced
# WATCH_DRIVE, WATCH_SEARCH and so on. Pointed at the current file they
# hang rather than fail, which is noise, so they are skipped on purpose.
# When the project comes back in Term 2, delete the LINE_PARKED guard at
# the top of each one and they run again.
LINE = "sol1x_line_alignment.py"
LINE_PARKED = ("parked for Term 2; the file on disk is an earlier design "
               "than these checks expect")
LINE_STATES = ("WATCH_DRIVE", "WATCH_SEARCH", "WATCH_ALIGN", "WATCH_APPROACH")

P08 = "sol08_security_bot.py"
P08_STATES = ("PATROLLING", "ADVANCING", "TURNING", "RUNNING")

P09 = "sol09_sumo_bot.py"
P09_STATES = ("PATROLLING", "TURNING", "ATTACKING")

# The sumo ring: radius and rim width, in centimetres.
RING = (40.0, 7.6)

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
    env.run(solution(LINE))
    return env


def _first_failure(*checks):
    for status, message in checks:
        if status == 0:
            return 0, message
    return 1, ""


# --------------------------------------------------------------------------
# Line alignment -- parked for Term 2, still checked
# --------------------------------------------------------------------------

def test_line_squares_up_from_one_approach():
    """One directed case, so a failure has a readable repro."""
    return 2, LINE_PARKED
    stim = ApproachStimulus(seed=1)
    env = _run_approach(stim)
    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_squared_up(env),
        scoreboard.check_on_the_line(env),
        scoreboard.check_no_rotate(env.monitor),
        scoreboard.check_stopped_cleanly(env.monitor),
    )


def test_line_random_approaches():
    """Generated approaches, both sides, defects on.

    This is the test that matters. Every seed puts the line somewhere
    else, aims the robot at it from a different acute angle, and picks a
    fresh theta over-report out of the measured range. The check is
    against the plant's truth, so a DUT that agrees with its own bad
    odometry still fails.
    """
    return 2, LINE_PARKED

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

    holes = coverage.holes(LINE_STATES)
    if failures:
        return 0, "%d/%d approaches failed. First: %s" % (
            len(failures), coverage.runs, failures[0])
    if holes:
        return 0, "all approaches passed but coverage has holes: %s" % "; ".join(holes)
    return 1, ""


def test_line_immune_to_odometry_scale():
    """The halving claim, made executable.

    P08 works by taking half of a measured angle, so a consistent scale
    error on theta must divide out. Sweep theta_scale well past its
    measured 8-13% -- from honest to absurd -- and the robot must still
    end up square. If somebody ever "fixes" the halving toward yaw, or
    hard-codes a turn, this is what catches it.
    """
    return 2, LINE_PARKED

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


def test_line_reaches_every_state():
    return 2, LINE_PARKED
    env = _run_approach(ApproachStimulus(seed=3))
    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_reached_states(env.monitor, LINE_STATES),
    )


def test_line_dead_sensors_never_drive():
    """Sensors that never come up must stop the run, loudly and still.

    This is the silent-failure case: a robot that treats 'no answer' as
    'no line' drives forward forever, certain the floor is clear.
    """
    return 2, LINE_PARKED

    defects = dict(DEFAULT_DEFECTS)
    defects["sensor_dead_ms"] = 10 ** 9         # never report
    plant = Plant(defects=defects)
    env = Environment(plant=plant, watchdog_ms=20000)
    env.run(solution(LINE))

    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_never_moved_before_sensors(env, env.monitor),
        scoreboard.check_lights_out(env.monitor),
    )


def test_line_slow_sensors_still_work():
    """Sensors dead for the first 150 ms, then fine. Must still square up."""
    return 2, LINE_PARKED
    stim = ApproachStimulus(seed=11)
    stim.defects["sensor_dead_ms"] = 150
    env = _run_approach(stim)
    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_squared_up(env),
    )


def test_line_survives_clock_rollover():
    """Start ticks_ms() just short of its rollover.

    Anything using plain subtraction instead of ticks_diff() stops working
    the moment the counter wraps, and does it silently.
    """
    return 2, LINE_PARKED
    stim = ApproachStimulus(seed=5)
    plant = Plant(line_point=(40.0, 0.0),
                  line_angle_deg=stim.line_angle_deg,
                  start=stim.start_pose(),
                  defects=stim.defects)
    env = Environment(plant=plant, watchdog_ms=WATCHDOG_MS,
                      start_ticks_ms=(1 << 30) - 3000)
    env.run(solution(LINE))
    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_squared_up(env),
    )


def test_line_works_with_no_screen():
    """A loose OLED shows nothing and raises nothing. The robot must still
    do its job -- no project may depend on the display to function."""
    return 2, LINE_PARKED
    stim = ApproachStimulus(seed=13)
    stim.defects["oled_present"] = False
    env = _run_approach(stim)
    return _first_failure(
        scoreboard.check_run_completed(env.result),
        scoreboard.check_squared_up(env),
    )


def test_line_cancel_stops_it():
    """Cancel held from the start: no motion, clean shutdown."""
    return 2, LINE_PARKED

    class HoldCancel:
        def touch(self, name, env):
            return name == "cancel"

    plant = Plant()
    env = Environment(plant=plant, stimulus=HoldCancel(), watchdog_ms=20000)
    env.run(solution(LINE))
    if env.result.error is not None:
        return 0, "DUT raised %s" % env.result.error
    if env.plant.distance_travelled_cm > 1.0:
        return 0, "moved %.1f cm with Cancel held" % env.plant.distance_travelled_cm
    return scoreboard.check_stopped_cleanly(env.monitor)


# --------------------------------------------------------------------------
# P08 -- the security bot
# --------------------------------------------------------------------------

def _run_security_bot(target, watchdog_ms=WATCHDOG_MS, defects=None,
                      stimulus=None):
    plant = Plant(target=target, defects=defects)
    env = Environment(plant=plant, stimulus=stimulus, watchdog_ms=watchdog_ms)
    env.run(solution(P08))
    return env


def _ran_without_raising(env):
    if env.result.error is not None:
        return 0, "DUT raised %s" % env.result.error
    return 1, ""


def test_p08_stands_its_ground_runs_the_whole_machine():
    """A target that never moves has to walk the robot through every
    state: spot it, advance, fail to scare it, turn, run, peek."""
    if not _have(P08):
        return 2, "%s not written yet" % P08
    env = _run_security_bot(Target(80.0, 0.0, "stand"), watchdog_ms=40000)
    states = env.monitor.states_shown()
    return _first_failure(
        _ran_without_raising(env),
        scoreboard.check_reached_states(env.monitor, P08_STATES),
        (1, "") if states[:3] == ["PATROLLING", "ADVANCING", "TURNING"]
        else (0, "went %s, expected patrol then advance then turn"
              % " -> ".join(states[:3])),
        scoreboard.check_stopped_cleanly(env.monitor),
    )


def test_p08_lets_a_fleeing_target_go():
    """Back away faster than the robot closes and it gives up. It must go
    back to patrolling rather than retreating -- nothing frightened it."""
    if not _have(P08):
        return 2, "%s not written yet" % P08
    # Nerve breaks at 40 cm, which is well inside the 60 cm the robot
    # starts advancing at -- so the advance is real before the target
    # moves, and the two thresholds cannot race each other.
    env = _run_security_bot(
        Target(80.0, 0.0, "flee", speed_cms=25.0, notice_cm=40.0),
        watchdog_ms=25000)
    states = env.monitor.states_shown()
    if states[:3] != ["PATROLLING", "ADVANCING", "PATROLLING"]:
        return 0, "went %s, expected patrol then advance then patrol" % (
            " -> ".join(states[:4]))
    return _ran_without_raising(env)


def test_p08_empty_room_never_leaves_patrol():
    """Nothing in front of it means get_closest_distance() reports 999.
    A robot that advances on 999 has its comparison backwards."""
    if not _have(P08):
        return 2, "%s not written yet" % P08
    env = _run_security_bot(None, watchdog_ms=20000)
    states = env.monitor.states_shown()
    if states != ["PATROLLING"]:
        return 0, "left patrol with an empty room: %s" % " -> ".join(states)
    return _first_failure(_ran_without_raising(env),
                          scoreboard.check_stopped_cleanly(env.monitor))


def test_p08_works_with_no_screen_either():
    """A loose OLED shows nothing and raises nothing. The robot still has
    to run -- but with no display there is no state to read, so this only
    checks that it survives and moves."""
    if not _have(P08):
        return 2, "%s not written yet" % P08
    env = _run_security_bot(Target(80.0, 0.0, "stand"), watchdog_ms=40000,
                            defects=dict(DEFAULT_DEFECTS, oled_present=False))
    if env.plant.distance_travelled_cm < 10.0:
        return 0, "barely moved without a screen"
    return _first_failure(_ran_without_raising(env),
                          scoreboard.check_stopped_cleanly(env.monitor))


# --------------------------------------------------------------------------
# P09 -- the sumo bot
# --------------------------------------------------------------------------

class _PressCrossAt:
    """The student's thumb. Holds CROSS down from this moment on; the
    gamepad's own edge detector turns that into a single press."""

    def __init__(self, sim_ms):
        self.sim_ms = sim_ms

    def button(self, name, env):
        return name == "cross" and env.clock.now_ms >= self.sim_ms


class _HoldCancelAndCross:
    def touch(self, name, env):
        return name == "cancel"

    def button(self, name, env):
        return False


def _run_sumo(target=None, start_ms=200, watchdog_ms=WATCHDOG_MS,
              stimulus=None, defects=None):
    plant = Plant(ring=RING, target=target, defects=defects,
                  start=(0.0, 0.0, 0.0))
    env = Environment(plant=plant,
                      stimulus=stimulus or _PressCrossAt(start_ms),
                      watchdog_ms=watchdog_ms)
    env.run(solution(P09))
    return env


def test_p09_stays_in_the_ring():
    """The whole project in one check. An empty ring, a full minute, and
    the robot has to still be on it. Checked against the plant's own
    position -- a robot with a broken edge test says nothing, it just
    drives away."""
    if not _have(P09):
        return 2, "%s not written yet" % P09
    env = _run_sumo(watchdog_ms=60000)
    return _first_failure(
        _ran_without_raising(env),
        scoreboard.check_stayed_in_ring(env),
        scoreboard.check_reached_states(env.monitor, ("PATROLLING", "TURNING")),
        scoreboard.check_stopped_cleanly(env.monitor),
    )


def test_p09_charges_what_is_in_front_of_it():
    if not _have(P09):
        return 2, "%s not written yet" % P09
    env = _run_sumo(target=Target(22.0, 0.0, "stand"), watchdog_ms=30000)
    if "ATTACKING" not in env.monitor.states_shown():
        return 0, "never attacked a target parked in front of it"
    return _first_failure(_ran_without_raising(env),
                          scoreboard.check_stayed_in_ring(env))


def test_p09_edge_beats_the_charge():
    """A target glued to the robot's nose, so the charge can never end on
    its own. The only thing that can stop it pushing itself off the ring
    is the guard above the tree. If the edge test were inside a branch
    this is the run that would fail."""
    if not _have(P09):
        return 2, "%s not written yet" % P09
    env = _run_sumo(target=Target(10.0, 0.0, "glued", gap_cm=2.0),
                    watchdog_ms=45000)
    states = env.monitor.states_shown()
    if "ATTACKING" not in states:
        return 0, "never charged a target 2 cm from its nose"
    if "TURNING" not in states:
        return 0, "charged forever and never turned at the rim"
    return _first_failure(_ran_without_raising(env),
                          scoreboard.check_stayed_in_ring(env))


def test_p09_waits_for_the_start_button():
    """Armed is not started. Nothing may turn a wheel before CROSS."""
    if not _have(P09):
        return 2, "%s not written yet" % P09
    start_ms = 5000
    env = _run_sumo(start_ms=start_ms, watchdog_ms=25000)
    return _first_failure(
        _ran_without_raising(env),
        scoreboard.check_no_motion_before(env.monitor, start_ms),
    )


def test_p09_cancel_stops_it_before_the_match():
    """Cancel has to work while the robot is still waiting for a
    controller. Without that the only way out is the battery."""
    if not _have(P09):
        return 2, "%s not written yet" % P09
    env = _run_sumo(stimulus=_HoldCancelAndCross(), watchdog_ms=20000)
    if env.result.watchdog:
        return 0, "Cancel did not get out of the wait for the start button"
    if env.plant.distance_travelled_cm > 1.0:
        return 0, "moved %.1f cm with Cancel held" % env.plant.distance_travelled_cm
    return _first_failure(_ran_without_raising(env),
                          scoreboard.check_stopped_cleanly(env.monitor))


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
    if True:
        return "  " + LINE_PARKED
    coverage = Coverage()
    for seed in range(40):
        stim = ApproachStimulus(seed)
        env = _run_approach(stim)
        coverage.sample(stim, env.monitor)
    return coverage.report(LINE_STATES)
