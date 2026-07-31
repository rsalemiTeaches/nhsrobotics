// Guide generator V02.
// Backticks in any text become monospace runs, the Word version of `code`.
const d = require('docx');
const fs = require('fs');
const {Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow,
       TableCell, WidthType, ShadingType, LevelFormat, AlignmentType,
       Footer, PageNumber, BorderStyle, PageBreak} = d;

const CODE_BORDER = "9A9A9A";
const PAGE_W = 9360;

// "Use `x` now" -> [normal "Use ", mono "x", normal " now"]
function runs(text, base = {}) {
  const out = [];
  text.split("`").forEach((chunk, i) => {
    if (chunk === "") return;
    out.push(new TextRun(
      i % 2
        ? {text: chunk, font: "Consolas", size: 20, ...base}
        : {text: chunk, size: 22, ...base}));
  });
  return out;
}

function para(text, o = {}) {
  return new Paragraph({children: runs(text, o.base || {}),
                        spacing: {after: o.after ?? 120, line: 276}});
}
function bulletP(text) {
  return new Paragraph({children: runs(text),
                        numbering: {reference: "gb", level: 0},
                        spacing: {after: 80, line: 276}});
}
function numP(text) {
  return new Paragraph({children: runs(text),
                        numbering: {reference: "gn", level: 0},
                        spacing: {after: 80, line: 276}});
}
function codeBlock(src) {
  const lines = src.split("\n").map(l => new Paragraph({
    children: [new TextRun({text: l === "" ? " " : l, font: "Consolas", size: 19})],
    spacing: {after: 0, line: 240},
  }));
  return new Table({
    columnWidths: [PAGE_W],
    width: {size: PAGE_W, type: WidthType.DXA},
    rows: [new TableRow({
      cantSplit: true,
      children: [new TableCell({
        width: {size: PAGE_W, type: WidthType.DXA},
        borders: {
          top:    {style: BorderStyle.SINGLE, size: 4, color: CODE_BORDER},
          bottom: {style: BorderStyle.SINGLE, size: 4, color: CODE_BORDER},
          left:   {style: BorderStyle.SINGLE, size: 4, color: CODE_BORDER},
          right:  {style: BorderStyle.SINGLE, size: 4, color: CODE_BORDER},
        },
        margins: {top: 120, bottom: 120, left: 180, right: 180},
        children: lines,
      })],
    })],
  });
}

function render(blocks) {
  const out = [];
  for (const [kind, payload] of blocks) {
    if (kind === "title") {
      out.push(new Paragraph({text: payload, heading: HeadingLevel.TITLE,
                              keepNext: true, spacing: {after: 120}}));
    } else if (kind === "h1") {
      out.push(new Paragraph({text: payload, heading: HeadingLevel.HEADING_1,
                              keepNext: true, spacing: {before: 340, after: 160}}));
    } else if (kind === "h2") {
      out.push(new Paragraph({text: payload, heading: HeadingLevel.HEADING_2,
                              keepNext: true, spacing: {before: 260, after: 120}}));
    } else if (kind === "lead") {
      out.push(new Paragraph({children: runs(payload, {bold: true}),
                              spacing: {after: 180, line: 276}}));
    } else if (kind === "note") {
      out.push(new Paragraph({children: runs(payload, {italics: true, color: "595959"}),
                              spacing: {after: 180, line: 276}}));
    } else if (kind === "p") {
      out.push(para(payload));
    } else if (kind === "b") {
      payload.forEach(t => out.push(bulletP(t)));
      out.push(new Paragraph({children: [], spacing: {after: 60}}));
    } else if (kind === "n") {
      payload.forEach(t => out.push(numP(t)));
      out.push(new Paragraph({children: [], spacing: {after: 60}}));
    } else if (kind === "code") {
      out.push(codeBlock(payload));
      out.push(new Paragraph({children: [], spacing: {after: 140}}));
    }
  }
  return out;
}

function version(v) {
  return new Paragraph({
    children: [new TextRun({text: v, italics: true, size: 18, color: "808080"})],
    spacing: {before: 400},
  });
}


function makeFooter(label) {
  const half = PAGE_W / 2;
  const none = {style: BorderStyle.NONE, size: 0, color: "FFFFFF"};
  const cellOf = (kids, align) => new TableCell({
    width: {size: half, type: WidthType.DXA},
    borders: {top: none, bottom: none, left: none, right: none},
    margins: {top: 0, bottom: 0, left: 0, right: 0},
    children: [new Paragraph({children: kids, alignment: align,
                              spacing: {after: 0}})],
  });
  return new Footer({children: [new Table({
    columnWidths: [half, half],
    width: {size: PAGE_W, type: WidthType.DXA},
    borders: {top: none, bottom: none, left: none, right: none,
              insideHorizontal: none, insideVertical: none},
    rows: [new TableRow({children: [
      cellOf([new TextRun({text: label, size: 17, color: "595959"})],
             AlignmentType.LEFT),
      cellOf([new TextRun({text: "Page ", size: 17, color: "595959"}),
              new TextRun({children: [PageNumber.CURRENT], size: 17, color: "595959"}),
              new TextRun({text: " of ", size: 17, color: "595959"}),
              new TextRun({children: [PageNumber.TOTAL_PAGES], size: 17, color: "595959"})],
             AlignmentType.RIGHT),
    ]})],
  })]});
}

async function build(outPath, ver, blocks) {
  const titleBlock = blocks.find(b => b[0] === "title");
  const label = titleBlock ? titleBlock[1] : "";
  // Duplex printing: pad to an even page count so the next guide starts clean.
  const pad = process.env.PAD_EVEN === "1"
    ? [new Paragraph({children: [new PageBreak()]}),
       new Paragraph({children: [new TextRun({
         text: "This page left blank.", size: 18, italics: true, color: "A6A6A6"})]})]
    : [];
  const doc = new Document({
    styles: {default: {
      document: {run: {font: "Calibri", size: 22}},
      title: {run: {font: "Calibri", size: 36, bold: true, color: "000000"}},
      heading1: {run: {font: "Calibri", size: 30, bold: true, color: "000000"}},
      heading2: {run: {font: "Calibri", size: 25, bold: true, color: "000000"}},
    }},
    numbering: {config: [
      {reference: "gb", levels: [{level: 0, format: LevelFormat.BULLET, text: "•",
        alignment: AlignmentType.LEFT,
        style: {paragraph: {indent: {left: 460, hanging: 260}}}}]},
      {reference: "gn", levels: [{level: 0, format: LevelFormat.DECIMAL, text: "%1.",
        alignment: AlignmentType.LEFT,
        style: {paragraph: {indent: {left: 460, hanging: 260}}}}]},
    ]},
    sections: [{
      properties: {page: {size: {width: 12240, height: 15840},
                          margin: {top: 1440, bottom: 1440, left: 1440, right: 1440}}},
      footers: {default: makeFooter(label + "  ·  " + ver)},
      children: [...render(blocks), version(ver), ...pad],
    }],
  });
  fs.writeFileSync(outPath, await Packer.toBuffer(doc));
  console.log("wrote", outPath, ver);
}

// Shared text, same in every guide.
const SAVE = (n, f) =>
  "Save your own copy first. In Thonny, open `" + f + "` and choose File > Save As. " +
  "Pick the Alvik (the MicroPython device) and save it as `/workspace/p" + n + ".py`. " +
  "Do all your work in that copy. Files outside `/workspace` get overwritten when " +
  "the projects are updated.";

const PARTA =
  "Part A of the worksheet has three WORK boxes and a FLEX box. Those match the " +
  "`# WORK` and `# FLEX` comments in your Python file. Copy the key line or lines " +
  "from each one into its box. If you skipped the flex, leave the FLEX box empty.";

const GRADING =
  "There is one checkoff. You run your finished file once and it shows everything " +
  "you built. Nothing gets erased or commented out along the way. You get 19 points " +
  "for doing the work, or 20 if you did the flex. Late work is your points times 0.9. " +
  "A missing robot or a missing worksheet is a 0 and a redo. This class is self-paced, " +
  "so work as fast as you want, but watch the due dates. Finish all fourteen projects " +
  "and you unlock the Lego and servo bin.";

module.exports = {build, SAVE, PARTA, GRADING};
