# nhs_robotics V03
# Changes from V02 (see QA report, July 2026):
#   1. Exports Controller (fixes ImportError in gamepad-based programs).
#   2. Exports LineFollower (new PID line following, V03).

from .superbot import SuperBot
from .peripherals import Button, Buzzer, OLED, NanoLED
from .gamepad import RobotGamepad
from .vision import RobotVision, ApproachVector
from .navigation import RobotNavigation
from .ui import RobotUI
from .line_follower import LineFollower
from controller import Controller

print("Loading nhs_robotics.py V03")
