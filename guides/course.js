// What the {{PLACEHOLDERS}} in the robotics guides stand for.
//
// The builder is shared with nhsengineering and carries none of this text. It
// is called with the guide's frontmatter, which is how SAVE gets the project
// number and the scaffold filename without the builder knowing either exists.
//
// This text was lifted verbatim out of the old guide_builder/build.js when the
// builder became a submodule. Nothing here changed in the move.

module.exports = meta => ({

  SAVE:
    "Save your own copy first. In Thonny, open `" + meta.scaffold + "` and " +
    "choose File > Save As. Pick the Alvik (the MicroPython device) and save " +
    "it as `/workspace/p" + meta.number + ".py`. Do all your work in that " +
    "copy. Files outside `/workspace` get overwritten when the projects are " +
    "updated.",

  PARTA:
    "Part A of the worksheet has three WORK boxes and a FLEX box. Those match " +
    "the `# WORK` and `# FLEX` comments in your Python file. Copy the key line " +
    "or lines from each one into its box. If you skipped the flex, leave the " +
    "FLEX box empty.",

  GRADING:
    "One checkoff. Run the finished file once and it shows everything you " +
    "built, so nothing gets commented out along the way. The work is 19 " +
    "points, the flex is 20, undone is 0. Late is your points × 0.9. No robot " +
    "or no worksheet is a 0 and a redo. Work at your own speed and watch the " +
    "due dates. Finish all fourteen and the Lego and servo bin unlocks.",

});
