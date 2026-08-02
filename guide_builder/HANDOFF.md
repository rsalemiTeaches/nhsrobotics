# Handoff: NHS Robotics guide rebuild

*V02 — written 2026-08-02*

Read this plus `README.md` in this folder. The memory files carry the class
rules and Ray's teaching voice; this file carries where the work stopped.

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
| P05–P14 | old | old | old | no |

**P04 changed identity twice on 2026-08-02.** It was "Button Moves" — three
pre-programmed wheel-speed moves on gamepad buttons. Ray killed it as contrived:
with `held()`, spin and back-up are `set_wheels_speed` with extra steps, and only
the wiggle earned a function. The old P08 "Move With Code" moved into the slot
next, because drive-a-square landed right after the sumo tournament and read as a
Term 1 skill at the top of Term 2. Ray then rejected that too as a hodge podge —
it merged three sources and had no spine. **P08 is an empty placeholder either
way**; see `projects/p08_placeholder.py`.

What P04 is now: the robot runs itself from `main.py`, waits for OK, drives to a
wall on the distance sensor, reads its own pose, turns around and drives back.
WORK 1 is `import workspace.p04` plus the flash-and-wait gate, WORK 2 is the
drive-and-stop, WORK 3 is pose-turn-return, FLEX is the OLED with units.

P04 uses `alvik.move()`, `alvik.rotate()` and `alvik.drive()`, not the
`RobotNavigation` wrappers. They are firmware-native, need no library change, and
Ray's own `init_bot/` demos use them everywhere. `rotate_precise()` is a one-line
wrapper around `alvik.rotate()` and adds nothing.

**Nobody writes a function in P04, and that is fine.** P02 V14 ended its function
section with "In P04 you write your own." Ray scrapped that line on 2026-08-02 —
*"why limit ourselves"* — so P02 V15 says "Before long you will be writing your
own" and no project is on the hook for it.

**Stale downstream framing this created:** `p05_distance_sensor.py` still claims
to introduce `get_closest_distance()`; `p08_move_with_code.py` still teaches
blocking moves via `sb.nav.*`; P05 and P06 still call the SuperBot `bot`, not
`sb`.

**P01, P02 and P03 are the reference set. Match them.** Everything below P03 is
still in the old voice and calls a library API that no longer exists.

## What changed on 2026-08-02

This was a big day. The rules that came out of it are in memory —
`guide-teaching-voice` is the most important one, and it was learned from Ray's
own hand edits to P02 and P03. Read it before writing a word.

**Teaching shape.** Guides now show the pain before the fix, give the tool
before the theory, enumerate instead of summarizing, and never introduce a word
the reader has not been given. Headings are unnumbered and say what you can do.

**Students transcribe.** New code is printed in the guide and typed in by hand;
scaffolds are skeletons with `# WORK` markers, not fill-in-the-blank. Part 2 is
one step per WORK block, each with the exact code and a run-it checkpoint. The
FLEX is never printed — they work it out.

**Library API.** `alvik.get_touch_cancel()` and `gamepad.buttons['x']` are gone
from student code. Both classes now answer `held(name)` and `pressed(name)`.
`RobotGamepad` applies `STICK_DEADZONE` inside all four stick properties, so a
resting stick reads exactly 0.0. `SuperBot` gained `log_info()` and
`light_both_leds()`. Every project builds a `SuperBot` now, including P01.

**Builder.** `build.js` V03 does inline `` `code` ``, `**bold**` and `*italic*`;
places PNGs with `![alt](images/x.png)`; uses Roboto Mono at 9.5pt because Ray
prints through Google Drive; and no longer stamps the version in the body, only
the footer.

## Next actions, in order

1. **Ray reads P04 Drive to the Wall and Back.** Hardware checks only he can run:
   - Does `import workspace.p04` in `main.py` actually run at power-up? The
     pattern is proven (`init_bot/nhs_robot/main.py` does `import demo.demo` with
     no `__init__.py`), but nobody has run it against `/workspace`.
   - Does `alvik.move(distance_out)` travel that distance and stop with the
     wheels at rest?
   - `get_closest_distance()` crashes on `None > 0` if any of the five TOF
     values is still `None`. That happens before the first packet, and *forever*
     if the firmware sends the 3-sensor `'d'` packet instead of the 7-value `'f'`
     matrix. P04 is safe by luck — the OK gate plus `reset_pose()`'s internal
     1 s sleep buy the time. Needs a `nhs_lib` guard and a host test either way.
   - `initialize_robot.sh` v29 leaves `main.py` alone unless `-c` is passed, so
     re-initializing no longer wipes a student's WORK 1. A robot with no
     `main.py` at all still gets the shipped one. Ray verified the
     modified-main.py case on hardware 2026-08-02: untouched after a plain
     init. The `-c` reset and the no-main.py cases are still logic-tested only.
2. **P05–P14**, one at a time, until Ray says to batch the rest.
3. **Fill the P08 slot.** Empty on purpose; it sits between Capstone 1 and P09,
   so it has to be a step up from a competition robot. Candidate in
   `projects/p08_placeholder.py`.
4. **Before P11 is printed**, add `sb.drive_to_line()` as a passthrough. P11
   currently makes students type `sb.nav.drive_to_line(...)`, which breaks Ray's
   rule that students never write `sb.<subthing>.method()`. The
   `drive_distance` / `rotate_precise` half of this is moot now — P04 uses
   `alvik.move()` and `alvik.rotate()` directly.

## P05, designed 2026-08-02, not built

Ray's design. **"A pretty tough P05."** The robot finds a taped line and squares
itself up on it:

1. Drive until the left or right line sensor sees the line.
2. Reset the pose.
3. Turn until the *other* sensor sees the line.
4. Read the angle off the pose.
5. Turn back half that angle.
6. Drive until you see the line. The robot is now aligned.

Two rules Ray set:

- **Never `alvik.rotate()` in this project.** Every turn is wheels turning while
  something gets polled — a line sensor in steps 3 and 6, the pose angle in
  step 5. `rotate()` takes a fixed angle and blocks, so it cannot watch a sensor.
- **The second sensor lands on the far crossing, not the near one.** Both sensors
  sweep the same circle around the pivot and that circle cuts the line twice.
  Turning toward the side that has *not* seen the line puts the second sensor on
  the other cut, which is what makes halving the angle mean anything. Turn the
  other way and the sweep is just the fixed angle between the two sensors.

`alvik.get_line_sensors()` returns `(left, center, right)`. `LINE_THRESHOLD = 500`
and the line reads *above* it on the white field — see
[[line-sensor-thresholds-final]]; the sumo ring is the opposite polarity.

**Collision to settle:** P11 "Find the Line" still claims to introduce the line
sensors. P07 sumo already reads them for edge detection, so that was stale before
this; P05 makes it worse. P11 needs new content or a new name, the same way P08
did.

P05 no longer teaches the distance sensor — P04 took it. `p05_distance_sensor.py`
is now misnamed.

## Open, decided but not actioned

- **The worksheet.** `Robotics_Project_Worksheet.docx` is parked until Ray
  settles Part A's wording and Part B question 1. See the
  `robotics-worksheet-open-questions` memory. P02's Step 5 still tells students
  to copy five variables plus the `blink()` call, which a one-line Part A rule
  would contradict.
- **Version prints.** Ray wants every module to print its version on load.
  `gamepad.py`, `ui.py`, `navigation.py`, `vision.py`, `line_follower.py` and
  `controller.py` still do not. P01's guide already promises students they will
  see them.
- **Library version.** `nhs_robotics/__init__.py` still says V03 despite real
  changes. Bumping it means chasing P14's "Requires library V03" line.
- **SuperBot internals.** Ray: "SuperBot is a mess." Agreed plan is to settle
  student-facing names per project and leave the constructor, the vision and
  HuskyLens tangle, and the swallowed exceptions until all 14 guides are done.

## Build

```bash
./build-all.sh p04.md -d     # build one guide and deploy it
./build-all.sh -d            # build all and deploy
```

Odd page counts are padded to even for duplex printing. Length only matters when
a change crosses onto a new *sheet* — 7 and 8 pages are both 4 sheets.

## Tests

```bash
python3 tests/run_host_regression.py    # no robot needed
```

Any change to `nhs_lib` needs a test in `tests/regression_host.py` and a line in
both runners. Five tests pass today.
