// The two animated figures, hand-drawn.
//
//   01-the-loop-turning   760 x 440   the loop advancing one stage at a time
//   02-context-reset      760 x 490   a window filling, resetting, and the file that survives
//
// HARNESS-PLAN section 4 asks for "one or two key moments" as animation, and
// names both of these: the loop turning, and a Ralph loop resetting context to
// a handoff file. They are the two claims in the series that are about *time*,
// which is the one thing a static figure can only imply.
//
// Three rules these follow, and the reason for each:
//
//   1. ONLY OPACITY IS ANIMATED. No transforms, no offset-path, no SMIL. A
//      roughjs shape is a path, so its geometry is not animatable anyway, and
//      opacity keyframes are the one technique every renderer that draws these
//      files already supports.
//
//   2. THE STATIC FRAME IS THE WHOLE DIAGRAM. Everything that carries meaning
//      is drawn at full opacity and never animated. What animates is a layer of
//      highlights on top, which start invisible. So a rasteriser that ignores
//      CSS, a reader with prefers-reduced-motion set, and a PDF export all get
//      a complete, legible figure rather than a half-drawn one.
//
//   3. THE ANIMATION IS INSIDE prefers-reduced-motion: no-preference. Rule 2 is
//      what makes that safe to do: turning the motion off subtracts emphasis,
//      never information.
//
// These emit no .excalidraw scene, unlike the 78 post figures. The animation is
// a stylesheet, and an Excalidraw scene cannot carry one, so a round-trip
// through the editor would silently return a still image. The generator is the
// only source.

const { T, rect, text, line, arrow, renderSvg, resetSeq } = require('./lib');
const { heading, fit, card, rule, flushFit } = require('./scaffold');
const fs = require('fs');
const path = require('path');

const W = 760;

// ------------------------------------------------------------------ helpers

// A ring drawn outside a node rather than a wash drawn under it: the node keeps
// its own fill, so the label underneath stays at full contrast while the ring
// is up.
const ring = (x, y, w, h, cls, stroke = T.accent) =>
  rect(x - 7, y - 7, w + 14, h + 14, { stroke, fill: 'transparent', strokeWidth: 2.6, animClass: cls });

const node = (x, y, w, h, name, gloss, o = {}) => {
  const els = [rect(x, y, w, h, { stroke: o.stroke ?? T.ink, fill: o.fill ?? T.surface, strokeWidth: o.strokeWidth ?? 1.4 })];
  els.push(text(x, y + (gloss ? 12 : (h - 15) / 2), name,
    { size: 13, align: 'center', width: w, stroke: o.stroke ?? T.ink }));
  if (gloss) els.push(text(x, y + 34, gloss, { size: 9, align: 'center', width: w, stroke: T.inkMuted }));
  return els;
};

// ------------------------------------------------------------------ scene 1
function loopTurning() {
  resetSeq();
  const H = 440;

  const els = [...heading('The loop, turning',
    'One stage at a time, and a stop check between every one of them.', W)];

  // --- the cycle, all of it static -----------------------------------------
  els.push(...node(40, 150, 104, 44, 'TASK', null, { fill: T.neutral1 }));
  els.push(...node(170, 124, 150, 60, 'REASON', 'the model decides'));
  els.push(...node(360, 124, 110, 60, 'ACT', 'a tool runs'));
  els.push(...node(360, 236, 110, 60, 'OBSERVE', 'read the result'));
  els.push(...node(170, 236, 150, 60, 'STOP?', 'checked every turn', { stroke: T.warn, strokeWidth: 1.6 }));

  els.push(arrow([[146, 172], [166, 172]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[322, 146], [356, 146]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(text(324, 126, 'tool call', { size: 8.5, stroke: T.inkMuted }));
  els.push(arrow([[415, 186], [415, 232]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(text(421, 200, 'run it', { size: 8.5, stroke: T.inkMuted }));
  els.push(arrow([[356, 266], [324, 266]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(text(326, 246, 'result', { size: 8.5, stroke: T.inkMuted }));
  els.push(arrow([[245, 234], [245, 188]], { stroke: T.success, strokeWidth: 1.4 }));
  els.push(text(251, 202, 'keep going', { size: 8.5, stroke: T.success }));

  // --- the exits, static ----------------------------------------------------
  els.push(...card(500, 116, 220, 180, { spine: T.warn, strokeWidth: 1.4 }));
  els.push(text(518, 124, 'WHAT STOP? IS CHECKING', { size: 9, stroke: T.warn }));
  [['1', 'a terminal stop_reason'], ['2', 'the budget is spent'],
   ['3', 'no progress for N turns'], ['4', 'a guard fired']]
    .forEach(([n, s], i) => {
      els.push(text(518, 150 + i * 30, n, { size: 10, stroke: T.inkSubtle }));
      els.push(text(534, 150 + i * 30, fit(s, 10, 170, 'exit'), { size: 10, stroke: T.ink }));
    });
  els.push(rule(518, 702, 262));
  els.push(text(518, 268, 'only the first is an answer', { size: 8.5, stroke: T.inkSubtle }));

  // --- the animated layer: four rings and four arrow overlays ---------------
  els.push(ring(170, 124, 150, 60, 'he-stage he-s1'));
  els.push(ring(360, 124, 110, 60, 'he-stage he-s2'));
  els.push(ring(360, 236, 110, 60, 'he-stage he-s3'));
  els.push(ring(170, 236, 150, 60, 'he-stage he-s4', T.warn));

  els.push(arrow([[322, 146], [356, 146]], { stroke: T.accent, strokeWidth: 2.4, animClass: 'he-stage he-s2' }));
  els.push(arrow([[415, 186], [415, 232]], { stroke: T.accent, strokeWidth: 2.4, animClass: 'he-stage he-s3' }));
  els.push(arrow([[356, 266], [324, 266]], { stroke: T.accent, strokeWidth: 2.4, animClass: 'he-stage he-s4' }));
  els.push(arrow([[245, 234], [245, 188]], { stroke: T.success, strokeWidth: 2.4, animClass: 'he-stage he-s1' }));

  els.push(text(40, 340, fit('Four stages, and one loop: no stage knows what the last one did except through what is in the context.', 11, 690, 'loop close 1'),
    { size: 11, stroke: T.ink }));
  els.push(text(40, 362, fit('The stop check is the stage engineers leave out. Without it the loop has one exit, and the model chooses it.', 11, 690, 'loop close 2'),
    { size: 11, stroke: T.inkMuted }));
  els.push(line([[40, 392], [720, 392]], { stroke: T.border, strokeWidth: 1 }));
  els.push(text(40, 402, fit('Post 03. Motion is emphasis only: with prefers-reduced-motion set the same figure is drawn still, and only the highlight is lost.', 8.5, 690, 'loop footer'),
    { size: 8.5, stroke: T.inkSubtle }));

  // One 8s revolution, four 2s stages. The ring is up for most of its stage and
  // gone before the next one lights, so exactly one is lit at a time.
  const css = `    .he-stage{opacity:0}
    @media (prefers-reduced-motion:no-preference){
      @keyframes he-stage{0%{opacity:0}3%{opacity:1}22%{opacity:1}25%,100%{opacity:0}}
      .he-s1{animation:he-stage 8s linear infinite 0s}
      .he-s2{animation:he-stage 8s linear infinite 2s}
      .he-s3{animation:he-stage 8s linear infinite 4s}
      .he-s4{animation:he-stage 8s linear infinite 6s}
    }`;

  return {
    W, H, els, css,
    title: 'The agent loop turning: reason, act, observe, and a stop check between every stage',
    desc: 'A hand-drawn cycle, animated. A task enters at the left and reaches reason, where the '
      + 'model decides. Reason passes a tool call to act, where a tool runs; act passes its result '
      + 'down to observe, which reads it; observe passes the result across to a stop check, drawn '
      + 'in warning colour and labelled as checked every turn; and the stop check returns upward '
      + 'to reason on a green keep-going edge, closing the loop. A panel on the right lists what '
      + 'the stop check is testing: a terminal stop reason, a spent budget, no progress for N '
      + 'turns, and a guard firing, with a footer noting that only the first of those is an '
      + 'answer. A highlight ring travels the cycle one stage at a time on an eight-second '
      + 'revolution, lighting each node and the edge that leaves it. The motion is emphasis only: '
      + 'every node, edge and label is drawn at full strength whether or not the animation runs, '
      + 'so a reader who has asked for reduced motion sees the same complete diagram held still. '
      + 'Captions record that no stage knows what the last one did except through what is in the '
      + 'context, and that the stop check is the stage engineers leave out, which leaves the loop '
      + 'with exactly one exit and lets the model choose it.',
  };
}

// ------------------------------------------------------------------ scene 2
function contextReset() {
  resetSeq();
  const H = 490;
  const SEGS = 12, SX = 60, SY = 132, SW = 40, SH = 36, GAP = 4;

  const els = [...heading('A context reset, and the file that survives it',
    'The window is scratch space. The handoff file is the only thing the next window inherits.', W)];

  els.push(text(60, 112, 'ONE CONTEXT WINDOW - SCRATCH, AND IT DOES NOT SURVIVE', { size: 9, stroke: T.inkSubtle }));

  // The empty window: always drawn, so the still frame is a complete figure.
  for (let i = 0; i < SEGS; i++) {
    els.push(rect(SX + i * (SW + GAP), SY, SW, SH, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
  }
  const RIGHT = SX + SEGS * (SW + GAP) - GAP;
  els.push(text(60, SY + SH + 10, 'each block is a turn: the prompt, the tool results, and everything read back', { size: 9, stroke: T.inkMuted }));

  // The reset boundary.
  els.push(line([[RIGHT + 12, 118], [RIGHT + 12, SY + SH + 26]], { stroke: T.alert, strokeWidth: 1.6, strokeStyle: 'dashed' }));
  els.push(text(RIGHT + 26, 112, 'THE RESET', { size: 9, stroke: T.alert }));

  // --- what is below the line: the durable half, always drawn ---------------
  els.push(...card(60, 230, 320, 150, { spine: T.success, strokeWidth: 1.5 }));
  els.push(text(78, 238, 'HANDOFF FILE ON DISK - DURABLE', { size: 9, stroke: T.success }));
  ['# what this run is for', '# what is done, and how it was checked',
   '# what is next, and why that is next', '# what was tried and did not work']
    .forEach((l, i) => els.push(text(78, 264 + i * 22, fit(l, 10, 288, 'handoff'), { size: 10, stroke: T.ink })));
  els.push(rule(78, 362, 350));
  els.push(text(78, 356, 'rewritten before the window fills, not after', { size: 8.5, stroke: T.inkSubtle }));

  els.push(...card(420, 230, 300, 150, { spine: T.primary, strokeWidth: 1.5 }));
  els.push(text(438, 238, 'THE NEXT WINDOW', { size: 9, stroke: T.primary }));
  els.push(text(438, 262, 'starts empty', { size: 11, stroke: T.ink }));
  ['and reads one file: everything the', 'last window learned that was worth',
   'keeping, in the words it chose']
    .forEach((l, i) => els.push(text(438, 288 + i * 14, fit(l, 9.5, 268, `next ${i}`),
      { size: 9.5, stroke: T.inkMuted })));
  els.push(rule(438, 702, 340));
  els.push(text(438, 346, 'the model is identical; only the context changed', { size: 8.5, stroke: T.inkSubtle }));

  els.push(arrow([[240, 390], [240, 406], [560, 406], [560, 390]], { stroke: T.success, strokeWidth: 1.5 }));
  els.push(text(322, 410, 'the one edge that crosses a reset', { size: 9, stroke: T.success }));

  // --- the animated layer ---------------------------------------------------
  for (let i = 0; i < SEGS; i++) {
    els.push(rect(SX + i * (SW + GAP), SY, SW, SH,
      { stroke: T.primary, fill: T.primary, opacity: 34, strokeWidth: 1.2, animClass: `he-seg he-f${i}` }));
  }
  els.push(rect(RIGHT + 26, SY + 6, 72, 30, { stroke: T.alert, fill: 'transparent', strokeWidth: 2, animClass: 'he-flash' }));
  els.push(text(RIGHT + 26, SY + 15, 'RESET', { size: 10, align: 'center', width: 72, stroke: T.alert, animClass: 'he-flash' }));
  els.push(rect(53, 223, 334, 164, { stroke: T.success, fill: 'transparent', strokeWidth: 2.4, animClass: 'he-write' }));
  els.push(rect(413, 223, 314, 164, { stroke: T.primary, fill: 'transparent', strokeWidth: 2.4, animClass: 'he-next' }));

  els.push(text(60, 430, fit('Every block above the line is gone at the reset. The card below it is the entire inheritance,', 10.5, 660, 'reset close 1'),
    { size: 10.5, stroke: T.ink }));
  els.push(text(60, 448, fit('which is why writing it is the work rather than the bookkeeping.', 10.5, 660, 'reset close 2'),
    { size: 10.5, stroke: T.inkMuted }));
  els.push(text(60, 470, fit('Posts 09 and 18. Motion is emphasis only: held still, this is the same figure with the window drawn empty.', 8.5, 660, 'reset footer'),
    { size: 8.5, stroke: T.inkSubtle }));

  // A 12s cycle. Blocks fill from 6% to 50%, hold to 62%, and all clear on the
  // same frame -- a reset, not a drain. The handoff card lights just before the
  // clear, because it has to be written while the context still holds what goes
  // in it; the next window lights after.
  const fills = [];
  for (let i = 0; i < SEGS; i++) {
    const on = 6 + i * 4;
    fills.push(`      @keyframes he-f${i}{0%,${on - 1}%{opacity:0}${on}%,62%{opacity:1}63%,100%{opacity:0}}`);
    fills.push(`      .he-f${i}{animation:he-f${i} 12s linear infinite}`);
  }
  const css = `    .he-seg,.he-flash,.he-write,.he-next{opacity:0}
    @media (prefers-reduced-motion:no-preference){
${fills.join('\n')}
      @keyframes he-flash{0%,62%{opacity:0}63%,72%{opacity:1}73%,100%{opacity:0}}
      .he-flash{animation:he-flash 12s linear infinite}
      @keyframes he-write{0%,52%{opacity:0}54%,68%{opacity:1}70%,100%{opacity:0}}
      .he-write{animation:he-write 12s linear infinite}
      @keyframes he-next{0%,72%{opacity:0}74%,92%{opacity:1}94%,100%{opacity:0}}
      .he-next{animation:he-next 12s linear infinite}
    }`;

  return {
    W, H, els, css,
    title: 'A context window filling, resetting to empty, and the handoff file that carries the run across',
    desc: 'A hand-drawn figure, animated. Along the top, one context window is drawn as twelve empty '
      + 'blocks, captioned as one turn each: the prompt, the tool results, and everything read '
      + 'back. A dashed line in alert colour closes the row and is labelled the reset. Below the '
      + 'line sit the two things that survive it. On the left, a handoff file on disk, marked '
      + 'durable, holding four lines: what this run is for, what is done and how it was checked, '
      + 'what is next and why that is next, and what was tried and did not work, with a footer '
      + 'noting it is rewritten before the window fills rather than after. On the right, the next '
      + 'window, which starts empty and reads that one file, with a footer noting the model is '
      + 'identical and only the context changed. A single green edge runs from the file to the '
      + 'next window and is labelled the one edge that crosses a reset. Over a twelve-second '
      + 'cycle the twelve blocks fill one by one, the handoff card lights just before the '
      + 'boundary, every block clears on the same frame rather than draining, a reset marker '
      + 'flashes, and the next window lights empty. The motion is emphasis only: with reduced '
      + 'motion the same figure is drawn still, with the window empty. Captions record that '
      + 'everything above the line is gone at the reset and the card below it is the entire '
      + 'inheritance, which is why writing it is the work rather than the bookkeeping.',
  };
}

// ------------------------------------------------------------------ emit
function main() {
  const dir = process.argv[2];
  if (!dir) {
    console.error('usage: node animations.js <output-directory>');
    process.exit(2);
  }
  fs.mkdirSync(dir, { recursive: true });
  for (const [name, make] of [['01-the-loop-turning', loopTurning],
                              ['02-context-reset', contextReset]]) {
    const built = make();
    const svg = renderSvg(built.els, {
      width: built.W, height: built.H, title: built.title, desc: built.desc, css: built.css,
    });
    fs.writeFileSync(path.join(dir, `${name}.svg`), svg);
    const warned = flushFit(name);
    console.log(`${name}: ${built.els.length} elements, ${built.W}x${built.H}`
      + (warned ? `  (${warned} fit warning${warned > 1 ? 's' : ''})` : ''));
  }
}

main();
