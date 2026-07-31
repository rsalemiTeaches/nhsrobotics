# Handoff: NHS Robotics guide rebuild

*V01 — written 2026-07-31*

Read this plus `README.md` in this folder. Between them they cover the whole job.
The memory files carry the class rules; this file carries where the work stopped.

## The job

Rewrite all 14 project guides at an 8th-grade reading level, one project at a
time, with Ray approving each before moving on. Guides are generated from the
markdown in this folder — never hand-edit the `.docx`.

## Where it stopped

| Project | Guide | Scaffold | Solution | Ray approved |
|---|---|---|---|---|
| P01 Gamepad Lights | V02 | V02 | V02 | yes |
| P02 Flashing Lights | V03 | V03 | V03 | yes |
| P03–P14 | old | current | current | no |

P01 and P02 are both approved references. Match them.

## What P02 V03 changed, and why

The V02 version broke the one-checkoff rule: students overwrote their WORK 2
variables in WORK 3, so a single run could not show both. Ray's fix, in his
words: *"I want them to set the variables, run the code, then change the
variables and run the same code again. Maybe you make them a magic blink
function?"*

So the scaffold now gives students two functions:

```python
def both_leds(r, g, b): ...
def blink(blinks, on_time, off_time, r, g, b): ...
```

and wraps the whole show in `while not alvik.get_touch_cancel():` so it repeats
until Cancel. WORK 1 writes the blink by hand. WORK 2 makes five variables and
calls `blink`. WORK 3 gives those same five variables new values and calls
`blink` with a **character-for-character identical line**. Two identical calls,
two different results. That is the lesson, and nothing may blur it.

Because the scaffold hands students a helper, the guide had to earn it — Ray:
*"If you're going to make that helper you need to explain functions... I'm all
for the helper if you earn it with the teaching."* The guide now teaches the
ladder `set_color` → `both_leds` → `blink`. P02 teaches *calling* functions;
P04 teaches *writing* them.

## Open, decided by Ray, not yet actioned

**The worksheet.** `Robotics_Project_Worksheet.docx` is one shared form for all
14 projects. Two wording problems are unresolved and Ray said he would think
about them. Do not touch the file until he decides. Details are in the
`robotics-worksheet-open-questions` memory. Short version:

- Part A may change from "the key line or lines" to "the most important line."
  If it does, `p02.md` Step 3 must change too — it currently tells students to
  copy five variables into the box.
- Part B question 1 ("Pick one line from your code...") is being replaced. Ray
  called it "pretty terrible." The leading candidate asks about a line that was
  *given* to them, not one they wrote.

## Next actions, in order

1. Fix `p03_gamepad_driving.py` — its WORK 3 still tells students to call
   `alvik.stop()` themselves. That is given code in every project now.
2. Write `p03.md` and build it.
3. Continue P04–P14 one at a time until Ray says to batch the rest.

Everything else outstanding — capstones, pacing plan, the six hardware tests,
the invented distances in `sol08` — is in the `robotics-open-work` memory.

## Build

```bash
./build-all.sh p03.md -d     # build one guide and deploy it
./build-all.sh -d            # build all fourteen and deploy
```

The script pads odd-page guides to even for duplex printing and reports what it
did. Check the Flesch-Kincaid grade after every build; P01 and P02 land around
3.4, which is where Ray wants them.
