# tests/run_solution_regression.py
#
# The solution-level regression. V02
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
    ("Solutions: every solution compiles",
     solutions.test_every_solution_compiles),
    ("Solutions: no floor division",
     solutions.test_no_solution_uses_floor_division),
    ("Scaffolds: every scaffold compiles",
     solutions.test_every_project_scaffold_compiles),
    ("Scaffolds: every scaffold has a FLEX line",
     solutions.test_every_scaffold_has_a_flex_line),

    ("P08: stands its ground runs every state",
     solutions.test_p08_stands_its_ground_runs_the_whole_machine),
    ("P08: lets a fleeing target go",
     solutions.test_p08_lets_a_fleeing_target_go),
    ("P08: empty room never leaves patrol",
     solutions.test_p08_empty_room_never_leaves_patrol),
    ("P08: works with no screen", solutions.test_p08_works_with_no_screen_either),

    ("P09: stays in the ring", solutions.test_p09_stays_in_the_ring),
    ("P09: charges what is in front",
     solutions.test_p09_charges_what_is_in_front_of_it),
    ("P09: edge beats the charge", solutions.test_p09_edge_beats_the_charge),
    ("P09: waits for the start button",
     solutions.test_p09_waits_for_the_start_button),
    ("P09: Cancel stops it before the match",
     solutions.test_p09_cancel_stops_it_before_the_match),

    ("Line: squares up (directed)", solutions.test_line_squares_up_from_one_approach),
    ("Line: squares up (40 generated approaches)",
     solutions.test_line_random_approaches),
    ("Line: immune to odometry scale",
     solutions.test_line_immune_to_odometry_scale),
    ("Line: reaches every state", solutions.test_line_reaches_every_state),
    ("Line: dead sensors never drive",
     solutions.test_line_dead_sensors_never_drive),
    ("Line: slow sensors still work",
     solutions.test_line_slow_sensors_still_work),
    ("Line: survives ticks_ms rollover",
     solutions.test_line_survives_clock_rollover),
    ("Line: works with no screen", solutions.test_line_works_with_no_screen),
    ("Line: Cancel stops it", solutions.test_line_cancel_stops_it),
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
