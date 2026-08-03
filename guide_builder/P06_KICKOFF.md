# Kickoff prompt for Project 06

Paste this into a new thread.

---

Read `nhsrobotics/guide_builder/HANDOFF.md` and `README.md` in that same folder
before doing anything. Read the `guide-teaching-voice` memory before writing a
word of a guide — it came from my own edits. Also read the
`alvik-drive-measured-behavior` memory; we spent a day measuring the robot and
you should not re-derive it.

Don't touch the worksheet. Don't generate anything I haven't asked for. Limit
your commentary to things that matter to me — status, or something you need me
to do. Don't narrate your thinking.

We're building Project 06. It teaches `get_pose()` — all three numbers, not
just x.

P05 is the setup for it. Students drove a course by tuning four numbers by
hand: how long to drive out, how hard to turn, how long to turn, how long to
drive back. It works, and they enjoy it, but every one of those numbers was a
guess refined by trial. The hook for P06 is that the robot knew all of them
the whole time.

The sketch in the handoff is mine and it is not settled:

- WORK 1 drive a curve and print all three pose numbers; find out y is not zero
- WORK 2 poll theta while turning and brake at the angle you wanted — they
  build their own `rotate()`
- WORK 3 a path proved closed by x, y and theta all near zero
- FLEX live position on the OLED

Start by talking it through with me. Tell me what you think the one new idea
is, and whether that sketch actually delivers it. Then propose the WORK 1 / 2 /
3 / FLEX shape and wait for me to agree before you write anything.

Things I already decided that constrain you:

- Students never see the 7.4% velocity error. Don't teach it, don't compensate
  for it, and don't write a step that asks them to compute a time from a speed.
- `alvik.rotate()` already turns an accurate fixed angle, so a SuperBot method
  that just wraps it adds nothing. If WORK 2 has them build a theta-polling
  turn, that has to earn its place on something `rotate()` cannot do.
- One demo per project. Goals are additive, so nothing in WORK 3 may replace
  the behaviour from WORK 1.

There is one thing I have to test on hardware before you can rely on it: nobody
has ever measured `alvik.rotate()`, or `drive()` with both arguments at once.
Tell me if P06 depends on either and write me the test.
