# Guide Builder

Generates the printed lab guides in `Class Development/Robotics/Project Guides/`
from markdown.

*V02*

## Why this exists

The guides are not hand-edited Word files. Each one is a markdown file here, and
`build-all.sh` turns them into `.docx`. That keeps all fourteen consistent: the
grading rule, the worksheet instructions and the print layout live in one place,
so they cannot drift apart.

If you edit a `.docx` directly, fold your change back into the markdown or the
next build will wipe it.

## Build

```bash
npm install docx          # once
./build-all.sh            # build every guide
./build-all.sh p02.md     # build just one
./build-all.sh -d         # build all and copy into Project Guides
```

The script counts pages and rebuilds with a blank page when the count is odd, so
every guide is even for duplex printing. It reports what it did.

## Writing a guide

Copy `p02.md`. Frontmatter first:

```yaml
---
out: P03_Gamepad_Driving_Guide.docx
version: V01
title: "Project 03: Gamepad Driving"
number: "03"
scaffold: p03_gamepad_driving.py
---
```

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

So ``Call `alvik.stop()` at the end.`` renders the code part in Roboto Mono.
Backticks are Ray's house style for any variable name or keyword.

Code spans are matched first, so asterisks inside backticks stay literal. A
paragraph that is bold *end to end* is still the lead line, not a bold
paragraph — that rule is unchanged.

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
