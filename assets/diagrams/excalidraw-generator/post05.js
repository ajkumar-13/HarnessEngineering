// The post 05 diagrams, hand-drawn.
//
//   01-failure-modes-grid      960 x 596  Mirror of the existing figure.
//   02-where-failures-strike   960 x 452  Mirror.
//   03-trace-signatures        960 x 470  NEW, published: section 4 had no figure.
//
// Section 4 is the section that turns the taxonomy into something you can act
// on, because it says what each mode *looks like in a trace*. Six sketched
// signatures put that on the page: the shape you are pattern-matching against
// is the whole content of the section, and a bulleted list cannot show a shape.

const { T, rect, ellipse, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function grid() {
  resetSeq();
  const W = 960, H = 596;

  const els = [...heading('Six agent failure modes, and the harness fix for each',
    'Autonomous agents fail in a small set of nameable ways. Each maps to one component to change.')];

  const MODES = [
    ['1', 'Victory declaration', 'Announces the task is complete', 'when the tests are still red.',
      'Verification loop', 'Post 11', T.success],
    ['2', 'Context anxiety', 'Rushes and cuts corners as the', 'context window fills.',
      'Compaction and resets', 'Post 09', T.primary],
    ['3', 'One-shotting', 'Attempts the whole task in a', 'single undocumented leap.',
      'Planner / evaluator split', 'Post 12', T.primary],
    ['4', 'Doom loop', 'Repeats the same failing action,', 'making no change at all.',
      'No-progress stop', 'Post 03', T.success],
    ['5', 'Silent drift', 'Quietly ignores your project', 'conventions, run after run.',
      'Memory file plus hook', 'Posts 10 and 13', T.accent],
    ['6', 'Destructive action', 'Runs rm -rf, a force-push, or a', 'DROP TABLE.',
      'Deny-list hook plus sandbox', 'Posts 13 and 14', T.alert],
  ];

  MODES.forEach((m, i) => {
    const px = 40 + (i % 3) * 296;
    const py = 96 + Math.floor(i / 3) * 248;
    els.push(...card(px, py, 288, 224, { spine: m[6], strokeWidth: 1.3 }));
    els.push(rect(px + 16, py + 16, 26, 20, { stroke: m[6], fill: m[6], strokeWidth: 1 }));
    els.push(text(px + 16, py + 18, m[0], { size: 12, align: 'center', width: 26, stroke: T.onAccent }));
    els.push(text(px + 52, py + 14, fit(m[1], 15, 220, 'mode name'), { size: 15, stroke: T.ink }));
    els.push(rule(px + 16, px + 272, py + 52));
    els.push(text(px + 16, py + 62, 'SYMPTOM', { size: 9, stroke: T.inkSubtle }));
    els.push(text(px + 16, py + 80, fit(m[2], 11.5, 256, 'symptom'), { size: 11.5, stroke: T.ink }));
    els.push(text(px + 16, py + 100, fit(m[3], 11.5, 256, 'symptom'), { size: 11.5, stroke: T.ink }));
    els.push(rule(px + 16, px + 272, py + 134));
    els.push(text(px + 16, py + 144, 'HARNESS FIX', { size: 9, stroke: T.inkSubtle }));
    els.push(text(px + 16, py + 162, fit(m[4], 12.5, 256, 'fix'), { size: 12.5, stroke: m[6] }));
    els.push(text(px + 16, py + 188, m[5], { size: 10, stroke: T.inkMuted }));
  });

  els.push(text(40, 578,
    '"My agent is flaky" is not a diagnosis. Name the mode, and the component to change names itself.',
    { size: 12, stroke: T.ink }));

  return {
    W, H, els,
    title: 'Six named agent failure modes with the harness component that fixes each',
    desc: 'A hand-drawn gallery of six cards, each giving a failure mode, its symptom, and the '
      + 'harness component that fixes it. One, victory declaration: it announces the task is '
      + 'complete when the tests are still red, and the fix is a verification loop, covered in post '
      + '11. Two, context anxiety: it rushes and cuts corners as the context window fills, and the '
      + 'fix is compaction and resets, in post 09. Three, one-shotting: it attempts the whole task '
      + 'in a single undocumented leap, and the fix is a planner and evaluator split, in post 12. '
      + 'Four, doom loop: it repeats the same failing action making no change at all, and the fix '
      + 'is a no-progress stop condition, in post 03. Five, silent drift: it quietly ignores your '
      + 'project conventions run after run, and the fix is a memory file backed by a hook, in posts '
      + '10 and 13. Six, destructive action: it runs rm -rf, a force-push, or a DROP TABLE, and the '
      + 'fix is a deny-list hook inside a sandbox, in posts 13 and 14. A closing line records that '
      + 'my agent is flaky is not a diagnosis, and that naming the mode names the component to '
      + 'change.',
  };
}

// ---------------------------------------------------------------- diagram 2
function whereTheyStrike() {
  resetSeq();
  const W = 960, H = 636;

  const els = [...heading('Where each failure strikes in the loop',
    'Failures cluster at loop stages, and the stage that shows the symptom is rarely the stage that carries the fix.')];

  els.push(text(40, 86, 'THE LOOP, AND WHERE DETECTION SITS', { size: 10, stroke: T.inkSubtle }));
  els.push(text(408, 86, 'THE SIX MODES, NUMBERED AS IN THE FIRST FIGURE', { size: 10, stroke: T.inkSubtle }));

  // --- left: the loop, each stage carrying the thing you watch there -------
  els.push(rect(40, 100, 340, 224, { stroke: T.accent, strokeWidth: 1.3, strokeStyle: 'dashed' }));

  // The detection point rides inside the box rather than beside it: the three
  // arrows own the space around the boxes, and a caption there collides.
  const stage = (x, y, w, label, tint, tag) => [
    rect(x, y, w, 54, { stroke: tint, fill: T.surface, strokeWidth: 1.5 }),
    text(x, y + 9, label, { size: 13, align: 'center', width: w, stroke: tint }),
    text(x, y + 31, fit(tag, 8.5, w - 16, 'stage tag'),
      { size: 8.5, align: 'center', width: w, stroke: T.inkSubtle }),
  ];
  els.push(...stage(168, 126, 180, 'REASON', T.primary, 'watch: the stop decision'));
  els.push(...stage(212, 244, 136, 'ACT', T.alert, 'watch: the tool call'));
  els.push(...stage(64, 244, 120, 'OBSERVE', T.warn, 'watch: repetition'));

  els.push(arrow([[308, 182], [294, 241]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[210, 271], [188, 271]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[148, 242], [176, 184]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(text(44, 330, 'the dashed ring is every turn, taken together', { size: 9.5, stroke: T.accent }));

  // --- right: the four addresses, each card carrying its trace signal ------
  const group = (x, y, headline, gloss, items, tint, note) => {
    const out = card(x, y, 246, 118, { spine: tint, strokeWidth: 1.3 });
    out.push(text(x + 16, y + 8, fit(headline, 10, 214, 'group head'), { size: 10, stroke: tint }));
    out.push(text(x + 16, y + 23, fit(gloss, 9.5, 214, 'group gloss'), { size: 9.5, stroke: T.inkMuted }));
    out.push(rule(x + 16, x + 230, y + 38));
    items.forEach((it, i) => {
      const iy = y + 45 + i * 34;
      out.push(rect(x + 16, iy, 22, 17, { stroke: tint, fill: tint, strokeWidth: 1 }));
      out.push(text(x + 16, iy + 2, it[0], { size: 10, align: 'center', width: 22, stroke: T.onAccent }));
      out.push(text(x + 46, iy - 1, fit(it[1], 12, 184, 'group item'), { size: 12, stroke: T.ink }));
      out.push(text(x + 46, iy + 17, fit(it[2], 9, 184, 'group signal'), { size: 9, stroke: T.inkMuted }));
    });
    if (note) {
      out.push(rule(x + 16, x + 230, y + 79));
      note.forEach((ln, i) => out.push(
        text(x + 16, y + 84 + i * 12, fit(ln, 8.5, 214, 'group note'),
          { size: 8.5, stroke: T.inkMuted })));
    }
    return out;
  };

  els.push(...group(408, 100, 'AT REASON - THE MODEL DECIDES', 'the judgement failures', [
    ['3', 'One-shotting', 'one turn does almost everything'],
    ['1', 'Victory declaration', 'completed, but a later check failed'],
  ], T.primary));
  els.push(...group(674, 100, 'AT ACT - A TOOL RUNS', 'the blast-radius failure', [
    ['6', 'Destructive action', 'a deny-listed command was attempted'],
  ], T.alert, [
    'blocked, denied and refused are successes;',
    'ok on a deny-listed command is the incident',
  ]));
  els.push(...group(408, 232, 'AT OBSERVE - THE LOOP TURNS AGAIN', 'the iteration failures', [
    ['4', 'Doom loop', 'identical (tool, args) across turns'],
    ['2', 'Context anxiety', 'quality falls with turn index'],
  ], T.warn));
  els.push(...group(674, 232, 'ACROSS TURNS - THE WHOLE LOOP', 'the consistency failure', [
    ['5', 'Silent drift', 'the same finding, run after run'],
  ], T.accent, [
    'read the assembled prompt for that run:',
    'a rule never in it is a missing memory file',
  ]));

  // --- lower tier: symptom address against fix address --------------------
  els.push(text(40, 366, 'THE ADDRESS OF A FAILURE IS NOT ALWAYS THE ADDRESS OF ITS FIX',
    { size: 10, stroke: T.inkSubtle }));
  els.push(...card(40, 382, 880, 176, { strokeWidth: 1.3 }));
  els.push(text(56, 391, 'FAILURE MODE', { size: 9, stroke: T.inkSubtle }));
  els.push(text(262, 391, 'SYMPTOM SHOWS AT', { size: 9, stroke: T.inkSubtle }));
  els.push(text(420, 391, 'THE FIX INSTALLS AT', { size: 9, stroke: T.inkSubtle }));
  els.push(rule(56, 904, 407));

  const ROWS = [
    ['1', 'Victory declaration', 'REASON', T.primary,
      'at the loop exit - the gate runs before stop 1 can fire'],
    ['2', 'Context anxiety', 'no single stage', T.warn,
      'between turns - compaction on the accumulated window'],
    ['3', 'One-shotting', 'REASON', T.primary,
      'before the run - the plan is written before any code exists'],
    ['4', 'Doom loop', 'OBSERVE', T.warn,
      'at the turn-end check - stop 4, a window of 3 identical calls'],
    ['5', 'Silent drift', 'every turn', T.accent,
      'at session start when memory is injected, and again pre-tool'],
    ['6', 'Destructive action', 'ACT', T.alert,
      'before the call - the only mode whose fix must run first'],
  ];
  ROWS.forEach((r, i) => {
    const ry = 416 + i * 24;
    els.push(rect(56, ry - 2, 20, 16, { stroke: r[3], fill: r[3], strokeWidth: 1 }));
    els.push(text(56, ry, r[0], { size: 9.5, align: 'center', width: 20, stroke: T.onAccent }));
    els.push(text(84, ry - 3, fit(r[1], 11.5, 170, 'row mode'), { size: 11.5, stroke: T.ink }));
    els.push(text(262, ry - 3, fit(r[2], 11, 124, 'row stage'), { size: 11, stroke: r[3] }));
    els.push(arrow([[392, ry + 5], [410, ry + 5]], { stroke: T.inkSubtle, strokeWidth: 1 }));
    els.push(text(420, ry - 3, fit(r[4], 11, 484, 'row fix'), { size: 11, stroke: T.ink }));
  });

  els.push(text(40, 574,
    'Instrument at the stage where the symptom shows; install the fix at the stage that controls it.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 594,
    'Five of the six are performance failures; destructive action alone is a safety failure, because there is no after.',
    { size: 11, stroke: T.inkMuted }));
  els.push(text(40, 614,
    'Worked example (section 3): with stop 4 a doom loop ends at turn 6 for about 84,000 input tokens; '
    + 'without it, the 40-turn cap costs about 3.28 million - a factor of 39.',
    { size: 9, stroke: T.inkSubtle }));

  return {
    W, H, els,
    title: 'The six failure modes placed at the loop stage where each strikes, and where each fix installs',
    desc: 'A hand-drawn figure in two tiers. The upper tier has the agent loop on the left, drawn as '
      + 'REASON, ACT and OBSERVE inside a dashed ring that stands for every turn taken together, with '
      + 'the thing to watch printed inside each stage box: the stop decision at reason, the tool call '
      + 'at act, repetition at observe. On the right, four cards place the six modes at the stage where '
      + 'each strikes and give the trace signal for each. At reason, the judgement failures: three, '
      + 'one-shotting, where one turn does almost everything, and one, victory declaration, where the '
      + 'run completed but a later check failed. At act, the blast-radius failure: six, destructive '
      + 'action, a deny-listed command attempted; the card adds that blocked, denied and refused are '
      + 'successes on the tool span, while ok on a deny-listed command is the incident. At observe, '
      + 'the iteration failures: four, doom loop, identical tool and arguments across turns, and two, '
      + 'context anxiety, quality falling with turn index. Across turns, the consistency failure: '
      + 'five, silent drift, the same finding run after run; the card adds that if the rule was never '
      + 'in the assembled prompt this is a missing memory file rather than drift. The lower tier is a '
      + 'six-row table headed the address of a failure is not always the address of its fix, giving '
      + 'for each mode where the symptom shows and where the fix installs: victory declaration shows '
      + 'at reason and is fixed at the loop exit, before stop 1 can fire; context anxiety has no '
      + 'single stage and is fixed between turns by compaction; one-shotting shows at reason and is '
      + 'fixed before the run, when the plan is written; doom loop shows at observe and is fixed at '
      + 'the turn-end check, stop 4, on a window of three identical calls; silent drift spans every '
      + 'turn and is fixed at session start when memory is injected and again pre-tool; destructive '
      + 'action shows at act and is fixed before the call. Closing lines record the working rule, '
      + 'instrument where the symptom shows and install the fix where it is controlled; that five of '
      + 'the six are performance failures while destructive action alone is a safety failure; and a '
      + 'section 3 worked example, in which stop 4 ends a doom loop at turn 6 for about 84,000 input '
      + 'tokens where the 40-turn cap alone would cost about 3.28 million, a factor of 39.',
  };
}

// ---------------------------------------------------------------- diagram 3
function traceSignatures() {
  resetSeq();
  const W = 960, H = 582;

  const els = [...heading('What each failure mode leaves in the trace',
    'You cannot fix what you cannot see. Each mode has a shape, and the shape is what you pattern-match against.')];

  els.push(text(40, 84, 'SIX SHAPES, READABLE FROM AN ORDINARY RUN LOG', { size: 10, stroke: T.inkSubtle }));

  const panel = (i, num, name, tint, signal1, signal2, draw) => {
    const px = 40 + (i % 3) * 296;
    const py = 100 + Math.floor(i / 3) * 162;
    const out = card(px, py, 288, 146, { spine: tint, strokeWidth: 1.3 });
    out.push(rect(px + 16, py + 12, 22, 17, { stroke: tint, fill: tint, strokeWidth: 1 }));
    out.push(text(px + 16, py + 14, num, { size: 10, align: 'center', width: 22, stroke: T.onAccent }));
    out.push(text(px + 46, py + 11, fit(name, 12.5, 226, 'sig name'), { size: 12.5, stroke: T.ink }));
    out.push(...draw(px + 16, py + 42));
    out.push(text(px + 16, py + 104, fit(signal1, 9, 256, 'signal'), { size: 9, stroke: T.inkMuted }));
    out.push(text(px + 16, py + 118, fit(signal2, 9, 256, 'signal'), { size: 9, stroke: T.inkMuted }));
    return out;
  };

  // 1 - victory declaration: turns, a green final-answer exit, a failing check after it.
  els.push(...panel(0, '1', 'Victory declaration', T.success,
    'completed runs with failing outcomes: the loop',
    'exited on stop 1 and the work was not done', (x, y) => {
      const out = [];
      for (let i = 0; i < 5; i++) {
        out.push(rect(x + i * 22, y + 10, 16, 16,
          { stroke: T.ink, fill: i === 4 ? T.success : T.surface, strokeWidth: 1.1 }));
      }
      out.push(arrow([[x + 114, y + 18], [x + 140, y + 18]], { stroke: T.inkMuted, strokeWidth: 1.2 }));
      out.push(rect(x + 144, y + 6, 108, 24, { stroke: T.alert, strokeWidth: 1.4 }));
      out.push(text(x + 144, y + 12, 'check fails later',
        { size: 9, align: 'center', width: 108, stroke: T.alert }));
      out.push(text(x, y + 38, 'turns 1 to 5, then "done"', { size: 8.5, stroke: T.inkSubtle }));
      return out;
    }));

  // 2 - context anxiety: quality against turn number.
  els.push(...panel(1, '2', 'Context anxiety', T.primary,
    'late-run answers are worse than early ones,',
    'as a function of turns rather than difficulty', (x, y) => [
      line([[x, y + 40], [x + 252, y + 40]], { stroke: T.inkSubtle, strokeWidth: 1 }),
      line([[x + 8, y + 6], [x + 70, y + 10], [x + 132, y + 18], [x + 194, y + 28], [x + 248, y + 36]],
        { stroke: T.alert, strokeWidth: 1.6 }),
      text(x, y + 44, 'turn 1', { size: 8.5, stroke: T.inkSubtle }),
      text(x + 172, y + 44, 'turn N, quality falling', { size: 8.5, stroke: T.inkSubtle }),
    ]));

  // 3 - one-shotting: one enormous turn, then nothing.
  els.push(...panel(2, '3', 'One-shotting', T.primary,
    'one turn does almost everything: a single',
    'enormous diff with no intermediate steps', (x, y) => {
      const out = [line([[x, y + 40], [x + 252, y + 40]], { stroke: T.inkSubtle, strokeWidth: 1 })];
      const HS = [36, 4, 3, 4, 3];
      HS.forEach((h, i) => {
        out.push(rect(x + 6 + i * 30, y + 40 - h, 22, h,
          { stroke: T.ink, fill: i === 0 ? T.accent : T.neutral2, strokeWidth: 1.1 }));
      });
      out.push(text(x, y + 44, 'change per turn', { size: 8.5, stroke: T.inkSubtle }));
      return out;
    }));

  // 4 - doom loop: the same call signature, over and over.
  els.push(...panel(3, '4', 'Doom loop', T.success,
    'identical (tool, args) across turns: three',
    'in a row is what stop 4 breaks the run on', (x, y) => {
      const out = [];
      for (let i = 0; i < 4; i++) {
        out.push(rect(x + i * 62, y + 8, 56, 24, { stroke: T.warn, fill: T.surface, strokeWidth: 1.2 }));
        out.push(text(x + i * 62, y + 15, 'test.sh', { size: 8.5, align: 'center', width: 56, stroke: T.ink }));
      }
      // The bar spans the last three chips: that window is the shipped default.
      out.push(line([[x + 62, y + 36], [x + 242, y + 36]], { stroke: T.alert, strokeWidth: 1.3 }));
      out.push(text(x, y + 41, 'the default window is 3 identical calls',
        { size: 8.5, stroke: T.inkSubtle }));
      return out;
    }));

  // 5 - silent drift: the same finding, run after run.
  els.push(...panel(4, '5', 'Silent drift', T.accent,
    'a rule you already fixed keeps reappearing',
    'in reviewer or lint findings, run after run', (x, y) => {
      const out = [line([[x, y + 30], [x + 252, y + 30]], { stroke: T.inkSubtle, strokeWidth: 1 })];
      for (let i = 0; i < 6; i++) {
        const cx = x + 14 + i * 44;
        out.push(line([[cx, y + 26], [cx, y + 34]], { stroke: T.inkSubtle, strokeWidth: 1 }));
        if (i % 2 === 0) {
          out.push(ellipse(cx - 6, y + 8, 12, 12, { stroke: T.accent, fill: T.accent, strokeWidth: 1 }));
        }
      }
      out.push(text(x, y + 40, 'runs 1 to 6; the dot is the finding recurring',
        { size: 8.5, stroke: T.inkSubtle }));
      return out;
    }));

  // 6 - destructive action: a deny-listed command, ideally never run.
  els.push(...panel(5, '6', 'Destructive action', T.alert,
    'a deny-listed command was attempted, and if',
    'the hook is doing its job it never ran', (x, y) => [
      rect(x, y + 8, 140, 24, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.2 }),
      text(x + 10, y + 15, 'rm -rf build/', { size: 9.5, family: 3, stroke: T.ink }),
      rect(x + 152, y + 8, 100, 24, { stroke: T.alert, fill: T.alert, strokeWidth: 1.4 }),
      text(x + 152, y + 15, 'BLOCKED', { size: 9.5, align: 'center', width: 100, stroke: T.onAccent }),
      text(x, y + 40, 'the deny-list hook fired before the tool ran',
        { size: 8.5, stroke: T.inkSubtle }),
    ]));

  // --- the order to run the tests in, cheapest evidence first -------------
  // Six shapes are only useful if you know which to look for first. Section 7
  // walks them in cost order, and the ladder is the actionable half.
  els.push(text(40, 424, 'RUN THE TESTS IN COST ORDER; THE FIRST YES IS USUALLY THE DIAGNOSIS',
    { size: 10, stroke: T.inkSubtle }));

  const STEPS = [
    ['the stop reason', 'how did the run end?', 'free - the loop records it'],
    ['call signatures', 'the same call again?', 'one pass over the transcript'],
    ['quality by turn', 'late turns worse than early?', 'needs a metric per turn'],
    ['an LLM judge', 'is the answer actually right?', 'over sampled runs, last'],
  ];
  STEPS.forEach((s, i) => {
    const sx = 40 + i * 226;
    els.push(...card(sx, 440, 202, 58, { strokeWidth: 1.2 }));
    els.push(text(sx + 12, 448, String(i + 1), { size: 10, stroke: T.inkSubtle }));
    els.push(text(sx + 26, 446, fit(s[0], 12, 164, 'step name'), { size: 12, stroke: T.ink }));
    els.push(text(sx + 12, 466, fit(s[1], 9, 178, 'step question'), { size: 9, stroke: T.inkMuted }));
    els.push(text(sx + 12, 481, fit(s[2], 9, 178, 'step cost'), { size: 9, stroke: T.inkSubtle }));
    if (i < 3) {
      els.push(arrow([[sx + 206, 469], [sx + 222, 469]], { stroke: T.inkSubtle, strokeWidth: 1 }));
    }
  });

  els.push(text(40, 514,
    'When an agent misbehaves, do not ask why the model is bad. Ask which of the six this is, and where in the loop it struck.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 536, 'The trace usually answers both, which is why observability is a prerequisite rather than a nicety.',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 558,
    'Four of the six are shapes over turns rather than facts about a single turn, which is why a per-call log is not enough.',
    { size: 10, stroke: T.inkSubtle }));

  return {
    W, H, els,
    title: 'The trace signature of each of the six agent failure modes, and the order to test for them',
    desc: 'A hand-drawn gallery of six small trace sketches, one per failure mode. One, victory '
      + 'declaration: five turn boxes ending in a green one, then an arrow to a box reading check '
      + 'fails later, so the signal is completed runs with failing outcomes. Two, context anxiety: '
      + 'a quality line sloping downwards against turn number, so the signal is that late-run '
      + 'answers are worse than early ones as a function of turns rather than difficulty. Three, '
      + 'one-shotting: a bar chart of change per turn in which the first bar is enormous and the '
      + 'rest are flat, so the signal is one turn doing almost everything. Four, doom loop: four '
      + 'identical call chips in a row with a bar under the last three, because the shipped default '
      + 'window is three identical calls, so the signal is identical tool and arguments across '
      + 'consecutive turns, which the no-progress exit breaks the run on. Five, silent drift: a run axis '
      + 'with the same finding recurring on alternating runs, so the signal is a rule you already '
      + 'fixed reappearing in reviewer or lint findings. Six, destructive action: a command chip '
      + 'reading rm -rf build slash beside a stamp reading BLOCKED, so the signal is a deny-listed '
      + 'command attempted and, if the hook is doing its job, never run. Below the gallery, a ladder '
      + 'of four steps gives the order to run the tests in, cheapest evidence first: the stop reason, '
      + 'which settles how the run ended and is free because the loop already records it; call '
      + 'signatures, which settle whether it is the same call again and cost one pass over the '
      + 'transcript; quality by turn, which settles whether late turns are worse than early ones and '
      + 'needs a metric per turn; and an LLM judge over sampled runs, run last. Captions record the '
      + 'debugging habit: ask which of the six this is and where in the loop it struck, rather than '
      + 'why the model is bad; and that four of the six are shapes over turns rather than facts about '
      + 'a single turn, which is why a per-call log is not enough.',
  };
}

module.exports = { grid, whereTheyStrike, traceSignatures };

if (require.main === module) {
  emit('01-failure-modes-grid', grid());
  emit('02-where-failures-strike', whereTheyStrike());
  emit('03-trace-signatures', traceSignatures());
}
