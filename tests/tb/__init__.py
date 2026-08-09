# tests/tb/ -- the solution testbench. V01
#
# plant.py      the world model: where the robot and the line really are
# simtime.py    the simulation clock, standing in for MicroPython's time
# fakes/        the BFM: arduino_alvik and nhs_robotics stand-ins
# wiring.py     the single global the fakes reach for
# monitor.py    every call the DUT made, in order, timestamped
# scoreboard.py checks, all computed from the plant and never from the DUT
# stimulus.py   generated approaches and coverage
# env.py        wires it together and runs one unmodified solution
