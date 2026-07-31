// Build one guide from markdown.
// V01
//
//   node make.js p02.md            -> writes the .docx named in the frontmatter
//   PAD_EVEN=1 node make.js p02.md -> adds a blank page for duplex printing
//
// Use ./build-all.sh to build every guide and pad the odd ones automatically.

const fs = require('fs');
const {parse} = require('./parse');
const {build, SAVE, PARTA, GRADING} = require('./build');

const mdPath = process.argv[2];
if (!mdPath) {
  console.error("usage: node make.js <guide.md>");
  process.exit(1);
}

const src = fs.readFileSync(mdPath, 'utf8');

// Frontmatter is read twice: once to learn the project number so SAVE can be
// built, once for real with all placeholders filled in.
const [meta0] = parse(src);
const vars = {
  SAVE: SAVE(meta0.number, meta0.scaffold),
  PARTA: PARTA,
  GRADING: GRADING,
};

const [meta, blocks] = parse(src, vars);
build(meta.out, meta.version, blocks);
