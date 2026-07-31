// Markdown -> block list for build.js.
// V01
//
// Supported:
//   ---            frontmatter (out, version, title)
//   #  Heading     Part heading      -> h1
//   ## Heading     Section heading   -> h2
//   > text         grey italic note  -> note
//   **text**       (whole paragraph) -> bold lead line
//   - item         bullet list       -> b
//   1. item        numbered list     -> n
//   ```            fenced code block -> code
//   text           paragraph         -> p
//
// Placeholders {{SAVE}}, {{PARTA}}, {{GRADING}} are substituted before parsing.
// Inline `backticks` are left alone; build.js turns them into monospace runs.

function frontmatter(src) {
  const m = src.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return [{}, src];
  const meta = {};
  for (const line of m[1].split(/\r?\n/)) {
    const kv = line.match(/^(\w+):\s*(.*)$/);
    if (kv) meta[kv[1]] = kv[2].trim().replace(/^["']|["']$/g, "");
  }
  return [meta, src.slice(m[0].length)];
}

function parse(src, vars = {}) {
  for (const [k, v] of Object.entries(vars)) {
    src = src.split("{{" + k + "}}").join(v);
  }
  const [meta, body] = frontmatter(src);
  const lines = body.split(/\r?\n/);
  const blocks = [];
  let i = 0;

  const flushList = (marker, kind) => {
    const items = [];
    while (i < lines.length && marker.test(lines[i])) {
      items.push(lines[i].replace(marker, "").trim());
      i++;
    }
    blocks.push([kind, items]);
  };

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) { i++; continue; }

    if (line.startsWith("```")) {              // fenced code
      i++;
      const buf = [];
      while (i < lines.length && !lines[i].startsWith("```")) buf.push(lines[i++]);
      i++;                                      // skip closing fence
      blocks.push(["code", buf.join("\n")]);
      continue;
    }
    if (/^##\s+/.test(line)) { blocks.push(["h2", line.replace(/^##\s+/, "").trim()]); i++; continue; }
    if (/^#\s+/.test(line))  { blocks.push(["h1", line.replace(/^#\s+/, "").trim()]);  i++; continue; }
    if (/^>\s?/.test(line))  { blocks.push(["note", line.replace(/^>\s?/, "").trim()]); i++; continue; }
    if (/^-\s+/.test(line))  { flushList(/^-\s+/, "b"); continue; }
    if (/^\d+\.\s+/.test(line)) { flushList(/^\d+\.\s+/, "n"); continue; }

    // A paragraph that is entirely bold is the lead line.
    const bold = line.trim().match(/^\*\*(.+)\*\*$/);
    if (bold) { blocks.push(["lead", bold[1]]); i++; continue; }

    blocks.push(["p", line.trim()]);
    i++;
  }

  if (meta.title) blocks.unshift(["title", meta.title]);
  return [meta, blocks];
}

module.exports = {parse};
