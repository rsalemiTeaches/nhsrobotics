# tests/run_solution_regression.py
#
# The solution-level regression. V01
#
#     python3 tests/run_solution_regression.py
#     python3 tests/run_solution_regression.py -v      # coverage report too
#
# Runs the real files out of solutions/ inside the testbench in tests/tb/.
# No robot, no simulator, no wall-clock time -- the DUT's own sleep drives
# a simulated clock, so the whole suite finishes in well under a second.
#
# run_host_regression.py calls this too. Use this one when you are working
# on a solution and want the shorter output.

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

for path in (HERE, os.path.join(REPO, "nhs_lib")):
    if path not in sys.path:
        sys.path.insert(0, path)

from regression_utils import RegressionRunner
import regression_solutions as solutions


TESTS = [
    ("Solutions: every solution compiles", solutions.test_every_solution_compiles),
    ("Solutions: no floor division", solutions.test_no_solution_uses_floor_division),
    ("Scaffolds: every scaffold compiles", solutions.test_every_project_scaffold_compiles),
    ("Scaffolds: every scaffold has a FLEX line", solutions.test_every_scaffold_has_a_flex_line),
    ("P08: squares up (directed)", solutions.test_p08_squares_up_from_one_approach),
    ("P08: squares up (40 generated approaches)", solutions.test_p08_random_approaches),
    ("P08: immune to odometry scale", solutions.test_p08_immune_to_odometry_scale),
    ("P08: reaches every state", solutions.test_p08_reaches_every_state),
    ("P08: dead sensors never drive", solutions.test_p08_dead_sensors_never_drive),
    ("P08: slow sensors still work", solutions.test_p08_slow_sensors_still_work),
    ("P08: survives ticks_ms rollover", solutions.test_p08_survives_clock_rollover),
    ("P08: works with no screen", solutions.test_p08_works_with_no_screen),
    ("P08: Cancel stops it", solutions.test_p08_cancel_stops_it),
]


def main():
    verbose = "-v" in sys.argv
    print("Initializing Solution Regression Suite (no robot required)...")
    print("\n--- Running Solution Tests ---")

    runner = RegressionRunner()
    for name, func in TESTS:
        runner.run_test(name, func)

    if verbose:
        print("\n--- Coverage ---")
        print(solutions.coverage_report())

    runner.print_summary()
    return 1 if runner.fails else 0


if __name__ == "__main__":
    sys.exit(main())
