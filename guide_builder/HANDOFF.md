# Handoff: NHS Robotics guide rebuild

*V03 — written 2026-08-03*

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
| P06–P14 | old | old | old | no |

**P01–P03 and now P05 are the reference set.** Everything from P06 down is
still in the old voice and calls a library API that no longer exists.

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

## P06: the pose project — next up

Ray's original brainstorm (2026-08-02) plus what P05 now sets up. Sketch, not
settled:

- WORK 1 drive a curve and print all three pose numbers; discover y is not
  zero.
- WORK 2 poll theta while turning and brake at the angle you wanted — they
  build their own `rotate()`, and it lands exactly where P05's tuning only
  got close.
- WORK 3 a path proved closed by x, y and theta all near zero.
- FLEX live position on the OLED.

The hook writes itself: *in P05 you tuned four numbers by hand; the robot knew
all of them the whole time.*

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

### Still unmeasured

- **`rotate()` has never been tested.** Accuracy is inferred from `move()`.
  P04's WORK 3 depends on it.
- **`drive()` with both arguments has never been tested.** Prediction: the
  curve radius is right even though the traverse is 7.4% slow, because the
  radius is forward ÷ turn and the error cancels in the division. P05 rests
  on this.
- **Saturation behaviour is unknown.** Budget rule: `forward + turn ÷ 13 ≤
  12.5` in cm/s and deg/s. Nobody knows what the firmware does past that.

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
