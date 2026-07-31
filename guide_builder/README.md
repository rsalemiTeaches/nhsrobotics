# Guide Builder

Generates the printed lab guides in `Class Development/Robotics/Project Guides/`.

*V01*

## Why this exists

The guides are not hand-edited Word files. They are generated from these scripts
so that all fourteen stay consistent. Edit the script, rebuild, redeploy. If you
edit the `.docx` directly, fold your change back into the script or the next
rebuild will wipe it.

## Run it

```bash
npm install docx          # once
node p01.js               # writes P01_Gamepad_Lights_Guide.docx
```

Then check the page count and pad to an even number for duplex printing:

```bash
soffice --headless --convert-to pdf P01_Gamepad_Lights_Guide.docx
pdftoppm -jpeg -r 40 P01_Gamepad_Lights_Guide.pdf x
# if the page count is odd:
PAD_EVEN=1 node p01.js
```

Copy the finished `.docx` to `Class Development/Robotics/Project Guides/`.

## Writing a guide script

`build(outPath, version, blocks)`. Each block is `[kind, payload]`:

| kind | payload | renders as |
|---|---|---|
| `title` | string | document title |
| `lead` | string | the bold "In this project you build…" line |
| `note` | string | grey italic note, used for the save-your-copy text |
| `h1` | string | Part heading |
| `h2` | string | numbered section heading |
| `p` | string | paragraph |
| `b` | array of strings | bullet list |
| `n` | array of strings | numbered list |
| `code` | string, `\n` separated | bordered monospace block |

**Backticks become monospace.** Write ``"Call `alvik.stop()` at the end."`` and the
code part renders in Consolas. That is the Word equivalent of markdown backticks,
which is Ray's house style for any variable name or keyword.

`SAVE(n, filename)`, `PARTA` and `GRADING` are shared strings — every guide uses
the same three, so grading and worksheet rules can never drift between guides.

## Print rules baked in

Guides are printed on paper, not read on screen. The builder handles:

- footer with project name, version and "Page N of M"
- code blocks with a thin border and white fill (grey shading prints muddy)
- black headings, not blue, to save toner
- `keepNext` on every heading so none strand at a page bottom
- `cantSplit` on code blocks
- even page count via `PAD_EVEN=1`

## House rules for the content

- 8th-grade reading level. Short sentences, plain words, no jargon.
- Keep the voice and the analogies. They are the point.
- WORK 1 / WORK 2 / WORK 3 / FLEX is the only nomenclature. No "Goal N", no
  "Day N" — the class is self-paced.
- Part 1 teaches everything the project needs. Students read it when stuck.
- The guide is the only place the flex is described. Scaffolds must not spoil it.

P01 is the approved reference. Match it.
