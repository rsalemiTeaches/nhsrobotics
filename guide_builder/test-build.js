// Tests for the guide builder. No robot, no Word, no network.
// V01
//
//   node test-build.js
//
// Exits non-zero on the first failure, so it can gate a commit.
//
// Everything is built in a temp folder, so running this never touches the .docx
// files in this directory.

const fs = require('fs');
const os = require('os');
const path = require('path');
const {execFileSync} = require('child_process');
const JSZip = require('jszip');

const HERE = __dirname;
const MAKE = path.join(HERE, 'make.js');

let failures = 0;
function check(name, ok, detail) {
  console.log((ok ? '  PASS  ' : '  FAIL  ') + name);
  if (!ok) {
    failures++;
    if (detail) console.log('        ' + detail);
  }
}

// Run make.js with the temp folder as the working directory, so the .docx it
// writes lands there. build.js resolves images against its own folder, so the
// pictures are still found.
function build(work, mdPath) {
  try {
    execFileSync('node', [MAKE, mdPath], {cwd: work, stdio: 'pipe'});
    return {ok: true, err: ''};
  } catch (e) {
    return {ok: false, err: (e.stderr || '').toString() + (e.stdout || '').toString()};
  }
}

// The visible words of a .docx, in order, with no markup.
async function textOf(docxPath) {
  const zip = await JSZip.loadAsync(fs.readFileSync(docxPath));
  const xml = await zip.file('word/document.xml').async('string');
  return {
    text: [...xml.matchAll(/<w:t[^>]*>([^<]*)<\/w:t>/g)].map(m => m[1]).join(''),
    xml,
  };
}

function scratch() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'guide-test-'));
}

function guide(body, out = 'Test.docx') {
  return `---
out: ${out}
version: V01
title: "Test guide"
number: "99"
scaffold: test.py
---

${body}
`;
}

async function main() {
  // --- Every real guide still builds ------------------------------------
  console.log('Every guide builds');
  const work = scratch();
  for (const md of fs.readdirSync(HERE).filter(f => /^p\d+\.md$/.test(f)).sort()) {
    const r = build(work, path.join(HERE, md));
    check(md, r.ok, r.err.trim());
  }

  // --- A link prints as its label ---------------------------------------
  console.log('\nLinks print as their label, never as a target');
  const w2 = scratch();
  const src = path.join(w2, 'g.md');
  fs.writeFileSync(src, guide(
    'You built this in [Gamepad Driving](p03.md) and again in [[p08|the Security Bot]].\n\n' +
    'The literal syntax `[[p03]]` must survive inside backticks.\n\n' +
    '![[p09_ring.png]]'
  ));
  const r2 = build(w2, src);
  check('builds', r2.ok, r2.err.trim());
  if (r2.ok) {
    const {text, xml} = await textOf(path.join(w2, 'Test.docx'));
    check('markdown link shows its label', text.includes('built this in Gamepad Driving'));
    check('wikilink alias shows its label', text.includes('again in the Security Bot'));
    check('no link target reaches the page', !/\]\(|\[\[p08/.test(text), text.slice(0, 200));
    check('link syntax inside backticks is left alone', text.includes('[[p03]]'));
    check('an Obsidian image embed resolves to images/', /r:embed|<a:blip/.test(xml));
  }

  // --- A bare link prints its target ------------------------------------
  console.log('\nA bare link prints its target, which is usually what you want');
  const w5 = scratch();
  const src5 = path.join(w5, 'g.md');
  fs.writeFileSync(src5, guide('You will find what you need in [[robot_setup]].'));
  const r5 = build(w5, src5);
  check('builds', r5.ok, r5.err.trim());
  if (r5.ok) {
    const {text} = await textOf(path.join(w5, 'Test.docx'));
    check('the name prints as typed', text.includes('what you need in robot_setup.'));
    check('no brackets reach the page', !text.includes('[['), text.slice(0, 200));
  }

  // --- ...except a bare link to another guide ---------------------------
  console.log('\nA bare link to another guide is refused: "p03" means nothing to a student');
  const w3 = scratch();
  const src3 = path.join(w3, 'g.md');
  fs.writeFileSync(src3, guide('You built this in [[p03]] last week.'));
  const r3 = build(w3, src3);
  check('build fails', !r3.ok);
  check('the message names the fix', /\[\[p03\|/.test(r3.err), r3.err.trim());

  // --- Frontmatter links are not guide-body links -----------------------
  console.log('\nBare links in frontmatter are fine, and change nothing');
  const w4 = scratch();
  const plain = path.join(w4, 'plain.md');
  const withFm = path.join(w4, 'withfm.md');
  fs.writeFileSync(plain, guide('A plain paragraph.', 'A.docx'));
  fs.writeFileSync(withFm, guide('A plain paragraph.', 'B.docx')
    .replace('scaffold: test.py', 'scaffold: test.py\ntags:\n  - demo\nrelated:\n  - "[[p03]]"'));
  const ra = build(w4, plain), rb = build(w4, withFm);
  check('both build', ra.ok && rb.ok, (ra.err + rb.err).trim());
  if (ra.ok && rb.ok) {
    const a = await textOf(path.join(w4, 'A.docx'));
    const b = await textOf(path.join(w4, 'B.docx'));
    check('properties do not change the page', a.text === b.text);
  }

  // --- The same markdown always gives the same document -----------------
  // The file will not be byte-identical -- docProps carries a clock -- but
  // every part a reader ever sees must be.
  console.log('\nBuilding twice gives the same document');
  const w6 = scratch(), w7 = scratch();
  const one = fs.readdirSync(HERE).filter(f => /^p\d+\.md$/.test(f)).sort()[0];
  const ra2 = build(w6, path.join(HERE, one));
  const rb2 = build(w7, path.join(HERE, one));
  check('both build', ra2.ok && rb2.ok, (ra2.err + rb2.err).trim());
  if (ra2.ok && rb2.ok) {
    const name = fs.readdirSync(w6).find(f => f.endsWith('.docx'));
    const za = await JSZip.loadAsync(fs.readFileSync(path.join(w6, name)));
    const zb = await JSZip.loadAsync(fs.readFileSync(path.join(w7, name)));
    const differ = [];
    for (const key of Object.keys(za.files)) {
      if (za.files[key].dir || key === 'docProps/core.xml') continue;
      const a = await za.files[key].async('base64');
      const b = await zb.files[key].async('base64');
      if (a !== b) differ.push(key);
    }
    check('every part but the clock is identical', differ.length === 0, differ.join(', '));
  }

  console.log(failures === 0
    ? '\nAll checks passed.'
    : `\n${failures} check(s) failed.`);
  process.exit(failures === 0 ? 0 : 1);
}

main();
