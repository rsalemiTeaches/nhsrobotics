# Handoff: NHS Robotics guide rebuild

*V04 — written 2026-08-04*

Read this plus `README.md` in this folder. The memory files carry the class
rules and Ray's teaching voice; this file carries where the work stopped.
Read the `guide-teaching-voice` memory before writing a word of a guide — it
came from Ray's own hand edits.

## The job

Rewrite all 14 project guides at an 8th-grade reading level, one project at a
time, with Ray approving each before moving on. Guides are generated from the
markdown in this folder — never hand-edit the `.docx`. If Ray edits one, fold
his change back into the `.md` before rebuilding or the next build reverts him.

## Where it stopped

| Project | Guide | Scaffold | Solution | Ray approved |
|---|---|---|---|---|
| P01 Gamepad Lights | V10 | V04 | V02 | yes |
| P02 Flashing Lights | V15 | V06 | V06 | yes |
| P03 Gamepad Driving | V08 | V04 | V03 | yes |
| P04 Drive to the Wall and Back | V02 | V02 | V03 | not yet |
| **P05 Around the Cone** | **V03** | **V01** | **V01** | **yes** |
| **P06 The Magic Circle** | **V01** | **V01** | **V01** | **runs on hardware, guide under review** |
| P07–P14 | old | old | old | no |

**P01–P03 and now P05 are the reference set.** Everything from P07 down is
still in the old voice and calls a library API that no longer exists.

`projects/p06_sensor_assist.py` is the old P06 and is now orphaned. Ray has
not said to delete it.

## What P05 became, and why

P05 is a **port of Ray's PRIZM "Turning the Robot" project**, which his
students enjoyed. Physical course on a foamboard: start box, drive out, curve
180° around a cone, drive back, park in a box **level with the start box**.
Randomized per-student numbers so nobody can copy. Tune by trial, not by
calculation.

- WORK 1 straight out, WORK 2 the arc (`drive()` with both arguments — the
  new idea), WORK 3 straight into the box. One tuned number per leg.
- **FLEX:** the two boxes are level, so leg 3 is the same length as leg 1.
  Read the pose after leg 1 and use `alvik.move(distance_out)` instead of a
  tuned time. Guide points at P04 rather than printing the code.
- **No pose anywhere in the WORK.** Ray's call: P05 is pure tuning, and the
  pose is P06's reveal. Pain before the fix, at the project level.
- Per-student speed comes from a **formula, not a list**: multiply your
  student number by 5, subtract 41 until under 41, divide by 10, add 4.
  24 distinct values, 4.3–8.0 cm/s, no two adjacent numbers closer than 0.5.
- Board geometry: boxes 24 cm apart centre to centre, so the arc radius is
  12 cm and the board fixes it. That is what makes the random speed do work —
  each student must find their own turn rate.
- `p05_distance_sensor.py` and `sol05_distance_sensor.py` were deleted.

## What to teach, and why — the thread through the movement API

Ray's own words: *"I have a tendency to want to teach them a bunch of cool
things the robot can do, but then lose the thread in terms of why."* This is
the thread we landed on.

There are only two ideas, at two levels:

|  | Per wheel | Per robot |
|---|---|---|
| **Set a speed** (runs forever) | `set_wheels_speed()` | `drive()` |
| **Set a destination** (stops itself) | `set_wheels_position()` | `move()`, `rotate()` |

**The question that picks the method: does the robot need to pay attention
while it moves?** `move()` and `rotate()` block — the robot is deaf and blind
until it arrives. `drive()` returns instantly, so your code stays free to
watch something. That is a real engineering idea, not robot trivia.

Reach for each one because:

- **`move()` / `rotate()`** — you know where you are going and nothing on the
  way can change your mind. Accurate, self-correcting, one line. For a
  beginner these are usually the right answer.
- **`drive()`** — the robot has to keep its eyes open (stop at a wall, follow
  a line, turn until a sensor fires, respond to a controller), or you need a
  **curve**, which nothing else can do.
- **`set_wheels_speed()`** — conceptual value only. Two motors, two numbers,
  no abstraction; it is how a student *feels* what a differential drive is.
  P03's gamepad mapping is perfect for it. Teach it once, never return.
- **`set_wheels_position()`** — no classroom use anyone could construct. Cut.

Also cut: the `'%'` angular unit (the constant behind it was broken, and
percent-of-max teaches nothing cm/s does not).

Where this puts the sequence:

| | What it adds |
|---|---|
| P03 | Two motors, two numbers. Feel the hardware. |
| P04 | Watch a sensor while moving vs. go somewhere blind — both families, contrasted in one project |
| P05 | The second argument. Curves. Tune by trial. |
| **P06** | The pose. Let the robot measure itself instead of tuning. |
| later | Line alignment — watch a line sensor *while* turning |

Each is "here is a new thing worth watching," not "here is another command."
P04 already does this right, using `drive()` to approach the wall because it
must watch the sensor, then `move()` and `rotate()` for the blind trip home.
The guide could name that out loud.

## P06: The Magic Circle — built 2026-08-04, runs on hardware

**The earlier "poll theta and build your own rotate()" sketch is dead.** Ray
killed it and replaced it wholesale. Do not resurrect it. It failed on his own
constraint — `alvik.rotate()` already turns an accurate fixed angle, so a
theta-polling turn in place adds nothing — and its WORK 1 was a print
statement, which is an observation and not a capability.

`projects/p06_magic_circle.py`, `solutions/sol06_magic_circle.py`, `p06.md`.

**The project.** The robot hides an invisible ring on the floor within 100 cm
of itself, 20 cm across. The student drives with the P03 gamepad and finds it
using only the feedback they build. Roll inside and the robot brakes, spins to
celebrate, and hides a new one.

**The thing being taught is not the pose. It is translating information into
feedback a person can act on.** Ray's words. The three WORK items are three
translations, one each:

- WORK 1 number → screen. Pythagoras on the two offsets, distance on the OLED.
- WORK 2 sign → two lights. Light the LED on the side the ring is on, both off
  when aimed.
- WORK 3 number → color. Nano LED red when hot, blue when cold, via `set_rgb`.

The dance and the next ring are GIVEN, because an outcome is not a translation.
FLEX is the robot playing its own game with no gamepad.

**`Circle` is defined in the student file**, not in `nhs_lib`. Ray's call: a
curious student can read it, and nothing has to be imported. It is not a
SuperBot capability. API is `circle = Circle(max_dist, diameter)` then
`dir, dx, dy = circle.get_bearings()`, with dir 1 left, −1 right, 0 aimed.

**No trigonometry reaches the student.** Ray was explicit. The class computes
the relative bearing internally and returns only a sign, which needs `sin` and
`cos` but never `atan2` — and because no angle is ever produced there is no
±180 wrap to handle, and unbounded theta (4424°) passes straight through since
`sin` is periodic. Students write Pythagoras and the color proportion, which
are 8th-grade math they own.

**Three numbers that are one decision.** `MAX_DIST_CM` 100, `TOLERANCE_DEG` 6,
`RING_DIAMETER_CM` 20. The naive rule `max_dist × sin(tolerance) < radius`
fails here (10.45 into 10) and it does not matter: the tolerance is divided by
distance, so the aimed window is a fixed number of degrees and a shrinking
number of centimetres as the robot closes — 10 cm of slack at a metre, 2 cm at
twenty. The lights re-aim the student continuously. What *would* break the game
is a tolerance too tight to hold with tank-drive sticks; 6° is a 12° window.
Full reasoning is in the solution header.

**Why this project is immune to the hardware defects.** Nothing depends on an
accurate distance or an accurate angle. The ring exists only in the robot's own
pose frame, so there is no physical ring for a drifting pose to disagree with,
and the student is the control loop. This is "hide it through project design"
taken as far as it goes.

**Ray verified it on hardware 2026-08-04.** The game plays, the win fires at
20 cm, the dance runs.

## Line alignment — designed, deferred

Ray's design from 2026-08-02, **now scheduled after P06**, not at P05. It
needs theta-polling and sensor-polling and turning-without-`rotate()` all at
once, which is a cliff straight after P04. Slot number undecided; it displaces
something.

The design: drive until one line sensor sees the line, reset pose, turn until
the *other* sensor sees it, read the angle, turn back half of it, drive until
you see the line again.

Two rules Ray set:

- **Never `alvik.rotate()` in this project.** Every turn watches something.
- **The second sensor lands on the far crossing, not the near one.** Both
  sensors sweep the same circle and it cuts the line twice. Turning toward the
  side that has *not* seen the line puts the second sensor on the other cut,
  which is what makes halving the angle mean anything.

`alvik.get_line_sensors()` returns `(left, center, right)`. `LINE_THRESHOLD =
500`, line reads *above* it on the white field — see
[[line-sensor-thresholds-final]]; the sumo ring is opposite polarity.

**Collision:** P11 "Find the Line" still claims to introduce the line sensors.
P07 sumo already reads them. P11 needs new content or a new name.

## Hardware truth, measured 2026-08-03

Full detail is in the `alvik-drive-measured-behavior` memory. The short form:

- **`drive()` delivers 92.6% of what you ask, in both axes**, plus a 0.21 s
  startup lag. Same on three robots of different ages, so it is firmware, not
  wear. Almost certainly a time-base error in the STM32 velocity loop; the
  physical geometry measures correct (34 mm wheels, 88 mm track).
- **`move()` is accurate** (495 mm on a 500 mm command) and **`get_pose()` is
  honest on all three values** — theta accumulates without wrapping and
  matched a by-eye turn count to 2%.
- **Negative angular velocity turns right**, positive turns left. Measured.
- **`brake()` stops in about 0.5 s** — 6 mm at 4.6 cm/s, 6.4° at 36 deg/s.
- **`ROBOT_MAX_DEG_S` was exactly 2× too big.** Ray fixed both working copies
  on 2026-08-03 — `nhs_lib/arduino_alvik/` and the fork submodule
  `libs_on_github/arduino-alvik-mpy/`. Staged, not committed, PR not filed.

**`init_bot/factory_alivk/` is an archive — leave it alone.** Ray's
instruction. It is a dump of what was actually inside a robot out of the box,
including an older Alvik library that still has the old constant. Nothing
references it. Do not "fix" anything in there.

**Ray's ruling: students never see the 92.6%.** They are beginners and will
have enough trouble with `drive()` and `get_pose()` assuming correct
behaviour. Do NOT put a compensation constant in `nhs_lib` — it would fix the
rate but not the lag, and it would wrap the API being taught. Hide it through
project design instead: **never write a step of the form "drive for N
seconds" that asks a student to compute the time.** Tuning a time by hand is
fine — the error gets absorbed and never surfaces, which is exactly what P05
does.

### Test programs in `dev/` (not student projects)

- `spin_rate_test.py` — three timed spins, count turns by eye
- `spin_ramp_test.py` — 10 Hz theta logging to `/spin_data.csv`, one OK press
  runs the whole thing. The fleet-check tool.
- `straight_line_test.py` — timed drive vs `move()`, logs to `/line_data.csv`
- `turn_sign_test.py` — which way is positive

### What 2026-08-04 added

A day of measuring on hardware. This supersedes parts of the entry above and
parts of the `alvik-drive-measured-behavior` memory — read this section as the
newer truth where they disagree.

- **theta from `get_pose()` is wheel odometry. yaw from `get_orientation()` is
  the IMU. They are separate packets from the STM32 and never touch.** Proven
  by lifting the robot and turning it by hand (yaw moves, theta does not) and
  by spinning the wheels in the air (theta climbs, robot has not moved).
  `dev/pose_source_test.py` does both on the OLED with no cable.
- **yaw does not drift.** Parked for two minutes, no creep. It is the only
  heading source on the robot that no wheel error can touch.
- **yaw is 0–360 and it wraps.** Observed running 358.8 → 359.2 → 4.6. Any use
  of yaw needs unwrapping, which is a trap for student code as much as ours.
- **theta over-reports rotation by 8–13%** against yaw as ground truth. On one
  spin the robot physically turned about 146° on a 180° command (81%), while
  theta claimed 163°.
- **Wheels measure 33 mm, track measures 88 mm.** Both Ray's measurements. That
  geometry predicts only a 3% theta over-report, so **geometry does not explain
  the 8–13%** and the residual is in the STM32 binary. An earlier guess in this
  file that the track was really ~93 mm was wrong — Ray re-measured 88.
  Remember the Python constants are documentation; the firmware has its own.
- **The pose origin is the midpoint of the wheel axle**, not the nose. Proven by
  the spin log: x and y sat at 0.0 through a full rotation, which could not
  happen if the origin were offset forward.
- **The pose keeps integrating under `set_wheels_speed()`**, not just `drive()`.
  Confirmed by P06 working at all. Mixing `'J'` and `'V'` packets in one program
  is also fine — P06's dance uses `drive()` between tank-drive commands.

**Ray's ruling on calibration, 2026-08-04: do not build one.** No calibration
program, no per-robot constant saved to the filesystem. A 33-vs-34 wheel would
be one honest number, but the real error is an unexplained residual that
differs between the linear and angular axes, sits in a binary nobody can read,
and comes with a 0.21 s lag. Hidden per-robot state also fails silently and
differently on each of 24 shared robots, and gets stomped every time a student
breaks `main.py`. **Design the projects instead.** If calibration ever belongs
in the course it is a project, not plumbing.

### Still unmeasured

- **`rotate()` has never been tested.** Accuracy is inferred from `move()`.
  P04's WORK 3 depends on it. P06 does not use it.
- **`drive()` with both arguments has never been tested.** Prediction: the
  curve radius is right even though the traverse is 7.4% slow, because the
  radius is forward ÷ turn and the error cancels in the division. P05 rests
  on this. P06 does not.
- **Saturation behaviour is unknown.** Budget rule: `forward + turn ÷ 13 ≤
  12.5` in cm/s and deg/s. Nobody knows what the firmware does past that.
- `dev/curve_pose_test.py` was written to answer the first two and Ray has not
  run it. It also measures whether pose y is honest through a curve, which
  nothing has ever checked.

### The dev/ test programs are not in the repo

HANDOFF V03 listed `spin_rate_test.py`, `spin_ramp_test.py`,
`straight_line_test.py` and `turn_sign_test.py` in `dev/`. **None of them are
there.** `dev/` holds six unrelated files and git shows nothing deleted. The
2026-08-03 measurement code may exist only on a robot. The two programs that do
exist are `dev/pose_source_test.py` and `dev/curve_pose_test.py`, both from
2026-08-04.

## A flat controller battery fails silently, and nothing catches it

Cost an hour of debugging on 2026-08-04. A dying PS4 controller does **not**
raise. `RobotController.update()` opens with
`if not self.is_connected(): self._reset_state()`, which zeroes every stick and
clears every button, and the socket path catches `OSError` and calls
`_close_ws()`. Nothing propagates.

So the symptom is a robot that quietly stops driving. Everything else in the
loop keeps running. The obvious reading — "it crashed, the `finally` block
cleaned up" — is wrong, and I chased it a long way before checking the code.
**Read `nhs_lib/controller.py` before theorising about gamepad failures.**

A `try`/`except` around the gamepad read is useless here; one was added and
reverted the same day.

**The only real fix would be polling `RobotController.is_connected()`, and
Ray's ruling 2026-08-04 is that it is not worth it.** Closed, not open. It
would mean reaching through `gamepad.controller.`, which is a level worse than
the banned `sb.<subthing>.method()` shape, and reversing the earlier decision
to pull `is_connected()` out of the student-facing API. Do not propose it again.

**P01 and P03 have the same silent behaviour, and that is accepted.** The
diagnostic fact above is the thing worth keeping: when a gamepad project
mysteriously stops driving, check the controller battery before the code.

## Older open items, unchanged

- **The worksheet.** `Robotics_Project_Worksheet.docx` is parked until Ray
  settles Part A's wording and Part B question 1. See the
  `robotics-worksheet-open-questions` memory. **Do not touch it.**
- **Version prints.** `gamepad.py`, `ui.py`, `navigation.py`, `vision.py`,
  `line_follower.py` and `controller.py` still do not print theirs. P01's
  guide already promises students they will see them.
- **Library version.** `nhs_robotics/__init__.py` still says V03 despite real
  changes. Bumping it means chasing P14's "Requires library V03" line.
- **SuperBot internals.** Ray: "SuperBot is a mess." Settle student-facing
  names per project; leave the constructor, the vision/HuskyLens tangle and
  the swallowed exceptions until all 14 guides are done.
- **`sb.drive_to_line()` passthrough** before P11 is printed. P11 currently
  makes students type `sb.nav.drive_to_line(...)`, which breaks the rule that
  students never write `sb.<subthing>.method()`.
- **P08 is an empty placeholder**, between Capstone 1 and P09, so it has to be
  a step up from a competition robot. Candidate in `projects/p08_placeholder.py`.
- **Stale downstream framing:** `p06_sensor_assist.py` and `p08_move_with_code.py`
  still teach blocking moves via `sb.nav.*`; P06 still calls the SuperBot
  `bot`, not `sb`.
- **Repo strays** from 2026-08-03 testing: `spin_test.py` in the root,
  `init_bot/nhs_robot/line_data.csv`, `tests/spin_data.csv`, `csvs/`, and
  `P05_TIme_Renames.docx` in Project Guides. Ask before deleting.

## Build

```bash
./build-all.sh p05.md -d     # build one guide and deploy it
./build-all.sh -d            # build all and deploy
```

Odd page counts are padded to even for duplex printing. Length only matters
when a change crosses onto a new *sheet* — 7 and 8 pages are both 4 sheets.
P05 sits at 6 pages, 3 sheets, with about half a page of slack.

**Images must be real PNGs.** The builder reads the PNG header and refuses
anything else, and it renders at natural pixel size capped at 624 px wide.
A JPEG renamed `.png` fails the build; an oversized canvas silently eats a
sheet. Crop tight and export around 300–500 px wide.

## Tests

```bash
python3 tests/run_host_regression.py    # no robot needed
```

Any change to `nhs_lib` needs a test in `tests/regression_host.py` and a line
in both runners. Five tests pass today.
