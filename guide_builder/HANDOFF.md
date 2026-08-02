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
| P02 Flashing Lights | V14 | V06 | V06 | yes |
| P03 Gamepad Driving | V08 | V04 | V03 | yes |
| P04 Move With Code | V01 | V01 | V01 | not yet |
| P05–P14 | old | old | old | no |

**P04 changed identity on 2026-08-02.** It was "Button Moves" — three
pre-programmed wheel-speed moves on gamepad buttons. Ray killed it as contrived:
with `held()`, spin and back-up are `set_wheels_speed` with extra steps, and only
the wiggle earned a function. The old P08 "Move With Code" moved down into the
P04 slot instead, because drive-a-square landed right after the sumo tournament
and read as a Term 1 skill at the top of Term 2. **P08 is now an empty
placeholder** — see `projects/p08_placeholder.py`. P13 still needs precise moves
for its avoid maneuver and now gets them from P04.

P04 uses `alvik.move(cm)` and `alvik.rotate(deg)`, not the `RobotNavigation`
wrappers. They are firmware-native, blocking, need no library change, and Ray's
own `init_bot/` demos use them everywhere. `rotate_precise()` is a one-line
wrapper around `alvik.rotate()` and adds nothing.

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

1. **Ray reads P04 Move With Code.** Two hardware checks only he can run: does
   `alvik.move(30)` really travel 30 cm and stop with the wheels at rest, and
   does a *negative* `move()`/`rotate()` still block properly? `_wait_for_target`
   computes `idle_time = distance / MOTOR_CONTROL_MM_S`, which goes negative for
   a negative argument and disables the minimum-wait floor, leaving the return
   entirely dependent on the firmware ack. The guide teaches `move(-30)` and
   `rotate(-90)`.
2. **P05–P14**, one at a time, until Ray says to batch the rest.
3. **Fill the P08 slot.** Empty on purpose; it sits between Capstone 1 and P09,
   so it has to be a step up from a competition robot. Candidate in
   `projects/p08_placeholder.py`.
4. **Before P11 is printed**, add `sb.drive_to_line()` as a passthrough. P11
   currently makes students type `sb.nav.drive_to_line(...)`, which breaks Ray's
   rule that students never write `sb.<subthing>.method()`. The
   `drive_distance` / `rotate_precise` half of this is moot now — P04 uses
   `alvik.move()` and `alvik.rotate()` directly.

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
