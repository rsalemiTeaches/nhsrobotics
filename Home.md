# NHS Robotics

The vault is the repo. Everything here is plain text and lives in git.

## Start here

- [PROJECT.md](PROJECT.md) — what is being worked on right now.
- [DECISIONS.md](DECISIONS.md) — settled calls, numbered and permanent.
- [REFERENCE.md](REFERENCE.md) — durable knowledge: how guides are made, what
  the course teaches, measured hardware behaviour, silent failure modes.

## The guides

One markdown file per guide, in `guide_builder/`. The printed guides are PDFs
built from these. No office suite is involved, and the markdown is the only copy
anyone can edit.

| Guide | Title | Version |
|---|---|---|
| [p01](guide_builder/p01.md) | Gamepad Lights | V10 |
| [p02](guide_builder/p02.md) | Flashing Lights | V15 |
| [p03](guide_builder/p03.md) | Gamepad Driving | V08 |
| [p04](guide_builder/p04.md) | Drive to the Wall and Back | V06 |
| [p05](guide_builder/p05.md) | Around the Cone | V03 |
| [p06](guide_builder/p06.md) | The Magic Circle | V01 |
| [p07](guide_builder/p07.md) | The Parking Sensor | V08 |
| [p08](guide_builder/p08.md) | The Security Bot | V04 |
| [p09](guide_builder/p09.md) | The Sumo Bot | V01 |

Each guide carries `tags` and `related` in its properties, so the graph and the
backlinks pane show how the projects feed each other.

## Building the guides

```bash
cd guide_builder
./build-all.sh          # build every guide that needs it
./build-all.sh p05.md   # build one
./build-all.sh -d       # build and copy into Project Guides
./build-all.sh -f       # rebuild everything, current or not
```

A guide is only rebuilt when its markdown, one of its pictures, or the builder
itself is newer than the PDF.

[guide_builder/README.md](guide_builder/README.md) explains the markdown the
builder understands.

## Links inside a guide

Link guides to each other however you like. **A link prints as its label and
nothing else**, because a guide is read on paper, where a clickable target is
worthless and a filename is noise.

```
You already built this in [[p03|Gamepad Driving]].
```

prints as *You already built this in Gamepad Driving.*

A link with no label prints its target, so `[[robot_setup]]` prints
*robot_setup*. The one link the build refuses is a bare link to another guide:
`[[p03]]` prints "p03", which is a name no student has ever seen. Write
`[[p03|Project 03]]`.

Dragging a picture into a guide works — Obsidian writes `![[thing.png]]` and the
builder resolves it against `images/`.

Run `node guide_builder/test-build.js` to check the builder after any change.

*V03*
