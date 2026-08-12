# Guide Builder

Generates the printed lab guides in `Class Development/Robotics/Project Guides/`
from markdown. **The guide is a PDF.** A Word file is built on the way there,
in a temp folder, and deleted — no office suite is needed to make a guide or to
print one, and there is no editable copy to hand-edit by mistake.

*V03*

## Why this exists

Each guide is a markdown file here, and `build-all.sh` turns it into a PDF. That
keeps them all consistent: the grading rule, the worksheet instructions and the
print layout live in one place, so they cannot drift apart.

The markdown is the only copy anyone can edit. That used to be a rule people had
to remember; now it is just true.

## Build

```bash
npm install docx          # once
./build-all.sh            # build every guide that needs it
./build-all.sh p02.md     # build just one
./build-all.sh -d         # build and copy into Project Guides
./build-all.sh -f         # rebuild everything, current or not
```

The script counts pages and rebuilds with a blank page when the count is odd, so
every guide is even for duplex printing. It reports what it did.

**It skips guides that are already current**, the way make does. A guide is
rebuilt when its markdown, one of its pictures, or the builder itself
(`build.js`, `parse.js`, `make.js`) is newer than the `.docx`. Page counting
runs the file through LibreOffice, which is slow, so a no-op run drops from
about a minute to about a second.

With `-d`, the deployed copy is compared too, so a guide that was built earlier
without `-d` still gets copied.

Built guides are not committed. The markdown is the source, the build reproduces
them, and keeping the repo text-only is the point. The copies that matter live
in `Project Guides`, with the retired ones in its `Previous Versions` folder.

## Writing a guide

Copy `p02.md`. Frontmatter first:

```yaml
---
out: P03_Gamepad_Driving_Guide.docx
version: V01
title: "Project 03: Gamepad Driving"
number: "03"
scaffold: p03_gamepad_driving.py
tags:
  - gamepad
  - driving
related:
  - "[[p02]]"
  - "[[p04]]"
---
```

The builder reads only `out`, `version`, `title`, `number` and `scaffold`.
Every other key is ignored, so `tags` and `related` change nothing in the
`.docx`.

Then plain markdown:

| You write | You get |
|---|---|
| `**bold line**` alone | the "In this project you…" lead line |
| `> text` | grey italic note |
| `# Heading` | Part heading |
| `## Heading` | section heading |
| `- item` | bullet list |
| `1. item` | numbered list |
| ` ``` ` fence | bordered code block |
| `![alt](images/x.png)` alone | centered picture |
| `![[x.png]]` alone | centered picture, as Obsidian writes it |
| anything else | paragraph |

**Pictures** live in `guide_builder/images/` and are referenced by path from this
folder. PNG only. The builder reads the file's real dimensions, scales it down to
the 6.5-inch text column if it is wider, and keeps its proportions — you never
give a size. A missing file or a non-PNG stops the build with the path it tried.
The picture is set `keepNext`, so it will not strand at the bottom of a page away
from the text that follows it.

Three placeholders pull in the shared text, so grading and worksheet rules are
identical in every guide:

- `{{SAVE}}` — the save-your-copy note, built from `number` and `scaffold`
- `{{PARTA}}` — how the worksheet's WORK and FLEX boxes work
- `{{GRADING}}` — one checkoff, 19/20, late ×0.9, self-paced, Lego unlock

Edit those three in `build.js`, not in a guide.

**Inline markup works inside any paragraph, bullet or heading text:**

| You write | You get |
|---|---|
| `` `alvik.stop()` `` | monospace, for any variable name or keyword |
| `**text**` | bold |
| `*text*` | italic |
| `[[p03\|Gamepad Driving]]` | the words *Gamepad Driving*, plain |
| `[Gamepad Driving](p03.md)` | the same thing |

So ``Call `alvik.stop()` at the end.`` renders the code part in Roboto Mono.
Backticks are Ray's house style for any variable name or keyword.

Code spans are matched first, so asterisks inside backticks stay literal. A
paragraph that is bold *end to end* is still the lead line, not a bold
paragraph — that rule is unchanged.

## Editing these files in Obsidian

The repo is an Obsidian vault, so these guides open as notes. Link them freely
and drag pictures in — both work.

**A link prints as its label and nothing else.** Guides are read on paper, where
a clickable target is worthless and a filename is noise. So

```
You already built this in [[p03|Gamepad Driving]].
```

prints as *You already built this in Gamepad Driving.* The same is true of
`[Gamepad Driving](p03.md)`. Use whichever you prefer; Obsidian counts both.

**A link with no label prints its target**, which is what you want whenever the
name is the thing the student needs: `you will find it in [[robot_setup]]`
prints *you will find it in robot_setup*.

**One link is refused: a bare link to another guide.** `[[p03]]` prints "p03",
and no student has ever seen that name — the guide on their desk says *Project
03: Gamepad Driving*. It is also the first thing Obsidian's autocomplete offers,
so it is the one that would slip through onto a handout. Write `[[p03|Project
03]]`. The `related` property is exempt; it is bare guide links on purpose and
is never printed.

**Dragging a picture in works.** Obsidian writes `![[thing.png]]` and puts the
file in `images/`, which is where the builder looks. The older
`![alt](images/thing.png)` still works too.

`build-all.sh` builds every file matching `p*.md` in this folder, so a note
whose name starts with `p` becomes a guide. Name scratch notes anything else.

## Tests

```bash
node test-build.js
```

Builds every guide plus a few synthetic ones in a temp folder and checks what
lands on the page. No robot and no Word needed. It touches none of the `.docx`
files here.

## Files

- `p01.md`, `p02.md`, … — one per guide, the only thing you normally edit
- `images/` — PNGs used by the guides
- `build.js` — docx rendering, shared strings, print rules
- `parse.js` — markdown to block list
- `make.js` — builds one guide; `build-all.sh` wraps it

## Print rules baked in

Guides are printed on paper, not read on screen. The builder handles:

- footer with project name, version and "Page N of M"
- code blocks with a thin border and white fill (grey shading prints muddy)
- black headings, not blue, to save toner
- `keepNext` on every heading so none strand at a page bottom
- `cantSplit` on code blocks
- even page count

## House rules for the content

- **Headings use sentence case**, from the Siemens style guide. "A loop that
  counts", not "A Loop That Counts". Proper nouns keep their capitals — Alvik,
  Python, Thonny, Chrome, WiFi, PS5 — as do WORK and FLEX. The first word after
  a colon is capitalized: "Variables: Name it once".
- 8th-grade reading level. Short sentences, plain words, no jargon.
- Keep the voice and the analogies. They are the point.
- WORK 1 / WORK 2 / WORK 3 / FLEX is the only nomenclature. No "Goal N", no
  "Day N" — the class is self-paced.
- Part 1 teaches everything the project needs. Students read it when stuck.
- The guide is the only place the flex is described. Scaffolds must not spoil it.
- Every concept the solution uses must be taught in the guide.

P01 and P02 are the approved references. Match them.
