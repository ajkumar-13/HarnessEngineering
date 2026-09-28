// The post 12 diagrams, hand-drawn.
//
//   01-pge-triangle       960 x 604  Mirror of the existing figure.
//   02-sprint-contract    960 x 576  Mirror.
//   03-the-unchecked-edge 960 x 470  NEW, published: section 6 had no figure.
//
// Section 6 says the three-role diagram *hides* the hole in the pattern, which
// is a fair complaint about `01-pge-triangle`. The remedy is not to redraw that
// figure but to draw the hole: the same chain with the one edge nothing checks
// marked as such.
//
// Figures 1 and 2 were four boxes and three step cards on a short canvas, which
// left both of them mostly empty. They now carry what the post already measures:
// the role ledger of section 2, the published cost comparison of section 9, and
// the six-criterion worked contract with its verifier routing from section 3.
// Every number in them is quoted from the post; none is invented.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// A label/value pair on one line, the shape the role ledgers are built from.
const ledger = (lx, vx, y, label, value, vw, tag) => [
  text(lx, y + 2, label, { size: 8.5, stroke: T.inkSubtle }),
  text(vx, y, fit(value, 9.5, vw, tag), { size: 9.5, stroke: T.ink }),
];

// ---------------------------------------------------------------- diagram 1
function pgeTriangle() {
  resetSeq();
  const W = 960, H = 604;

  const els = [...heading('Planner, generator, evaluator',
    'Three roles, three contexts, one artefact between them. The grader never saw the maker’s reasoning.')];

  // --- top band: what goes in, who plans, and why the grader is separate ---
  els.push(...card(40, 92, 260, 92, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 100, 'THE BRIEF THAT GOES IN', { size: 10, stroke: T.primary }));
  ['a 1 to 4 sentence prompt, expanded',
   'into a full product spec: 16 features',
   'across 10 sprints in the published run'].forEach((l, i) => {
    els.push(text(58, 120 + i * 15, fit(l, 9, 224, 'brief'), { size: 9, stroke: T.ink }));
  });
  els.push(text(58, 166, '(Anthropic, 2026)', { size: 8.5, stroke: T.inkSubtle }));

  els.push(arrow([[304, 138], [326, 138]], { stroke: T.inkMuted, strokeWidth: 1.3 }));

  els.push(...card(330, 92, 300, 92, { spine: T.primary, strokeWidth: 1.5 }));
  els.push(text(348, 100, 'PLANNER', { size: 14, stroke: T.primary }));
  els.push(text(348, 122, fit('decomposes the task, writes the criteria', 9.5, 264, 'planner gloss'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(rule(346, 614, 142));
  els.push(...ledger(348, 422, 146, 'READS', 'the task, and the repo it lands in', 192, 'planner reads'));
  els.push(...ledger(348, 422, 166, 'NEVER SEES', 'the work; it does not exist yet', 192, 'planner denied'));

  els.push(...card(660, 92, 260, 92, { spine: T.alert, strokeWidth: 1.3 }));
  els.push(text(678, 100, 'WHY THE GRADER IS SEPARATE', { size: 10, stroke: T.alert }));
  ['A model grading its own output skews',
   'positive: asked about work it made,',
   'it confidently praises it.'].forEach((l, i) => {
    els.push(text(678, 120 + i * 15, fit(l, 9, 224, 'bias'), { size: 9, stroke: T.ink }));
  });
  els.push(text(678, 166, '(Anthropic, 2026; Osmani, 2026)', { size: 8.5, stroke: T.inkSubtle }));

  // --- the fork: a plan down the left, the contract down the right --------
  els.push(arrow([[398, 186], [316, 222]], { stroke: T.ink, strokeWidth: 1.4 }));
  els.push(text(296, 204, 'plan', { size: 9.5, stroke: T.inkMuted }));
  els.push(arrow([[562, 186], [644, 222]], { stroke: T.ink, strokeWidth: 1.4 }));
  els.push(text(656, 204, 'contract', { size: 9.5, stroke: T.inkMuted }));

  // --- the two roles that must not share a context ------------------------
  els.push(...card(40, 228, 340, 124, { spine: T.accent, strokeWidth: 1.5 }));
  els.push(text(58, 236, 'GENERATOR', { size: 14, stroke: T.accent }));
  els.push(text(58, 258, fit('builds to the contract, not to "good enough"', 9.5, 304, 'gen gloss'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(rule(56, 364, 276));
  els.push(...ledger(58, 132, 284, 'READS', 'the plan, the contract, the last verdict', 232, 'gen reads'));
  els.push(...ledger(58, 132, 306, 'WRITES', 'the artefact, and nothing else', 232, 'gen writes'));
  els.push(...ledger(58, 132, 328, 'NEVER SEES', 'why the evaluator ruled as it did', 232, 'gen denied'));

  els.push(...card(580, 228, 340, 124, { spine: T.success, strokeWidth: 1.5 }));
  els.push(text(598, 236, 'EVALUATOR', { size: 14, stroke: T.success }));
  els.push(text(598, 258, fit('a separate agent, with a context of its own', 9.5, 304, 'eval gloss'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(rule(596, 904, 276));
  els.push(...ledger(598, 672, 284, 'READS', 'the contract and the finished work', 232, 'eval reads'));
  els.push(...ledger(598, 672, 306, 'WRITES', 'PASS or NEEDS_WORK, and a report', 232, 'eval writes'));
  els.push(...ledger(598, 672, 328, 'NEVER SEES', 'the generator’s chain of thought', 232, 'eval denied'));

  els.push(arrow([[384, 266], [576, 266]], { stroke: T.ink, strokeWidth: 1.4 }));
  els.push(text(452, 246, 'the work', { size: 9.5, stroke: T.inkMuted }));
  els.push(arrow([[576, 300], [384, 300]], { stroke: T.alert, strokeWidth: 1.4 }));
  els.push(text(396, 306, fit('fail: revise against the report', 9.5, 184, 'fail label'),
    { size: 9.5, stroke: T.alert }));
  els.push(text(400, 326, fit('the loop is capped at 3 revisions', 9, 180, 'cap label'),
    { size: 9, stroke: T.inkSubtle }));

  els.push(arrow([[750, 354], [750, 372]], { stroke: T.success, strokeWidth: 1.4 }));
  els.push(text(758, 354, 'pass', { size: 9.5, stroke: T.success }));

  // --- what the split costs, measured on one published brief --------------
  els.push(...card(40, 376, 500, 152, { spine: T.accent, strokeWidth: 1.4 }));
  els.push(text(58, 384, 'WHAT THE SPLIT COSTS, MEASURED', { size: 10, stroke: T.accent }));
  els.push(text(58, 400, fit('The first two rows are one brief, a 2D retro game maker, run both ways.', 9, 466, 'cost sub'),
    { size: 9, stroke: T.inkMuted }));
  els.push(text(58, 422, 'RUN', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(340, 422, 'WALL CLOCK', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(452, 422, 'COST', { size: 8.5, stroke: T.inkSubtle }));
  els.push(rule(56, 524, 434));
  const RUNS = [
    ['Single agent, one pass', '20 minutes', '$9', T.inkMuted],
    ['Planner / generator / evaluator', '6 hours', '$200', T.ink],
    ['Later simplified harness, other brief', '3 h 50 min', '$124.70', T.inkMuted],
  ];
  RUNS.forEach((r, i) => {
    const y = 442 + i * 22;
    if (i) els.push(rule(56, 524, y - 6));
    els.push(text(58, y, fit(r[0], 10, 274, 'run name'), { size: 10, stroke: r[3] }));
    els.push(text(340, y, r[1], { size: 10, stroke: r[3] }));
    els.push(text(452, y, r[2], { size: 10, stroke: r[3] }));
  });
  els.push(text(58, 502, fit('Over 20 times the price and about 18 times the wall clock (Anthropic, 2026).', 9, 466, 'cost note'),
    { size: 9, stroke: T.inkSubtle }));

  els.push(...card(580, 376, 340, 152, { spine: T.success, strokeWidth: 1.4 }));
  els.push(text(598, 388, 'DONE: THE VERDICT WAS PASS', { size: 11, stroke: T.success }));
  els.push(rule(596, 904, 412));
  ['"Done" now means it meets the',
   'pre-agreed contract, which is a claim',
   'you can check: the criteria are written',
   'down, and every failure is named',
   'against one of them.'].forEach((l, i) => {
    els.push(text(598, 420 + i * 20, fit(l, 9.5, 300, 'done line'), { size: 9.5, stroke: T.ink }));
  });

  els.push(text(40, 546, 'The grader judges the work against the contract, not against the story the maker tells about it.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 570, 'Hand the evaluator the work and the contract, and never the chain of thought that produced them.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A planner, a generator and a separate evaluator in one loop, with what each role is denied and what the split costs',
    desc: 'A hand-drawn figure of three roles. Across the top, a panel records the brief that goes in: '
      + 'a one to four sentence prompt, expanded into a full product spec of 16 features across 10 '
      + 'sprints in the published run. It feeds a planner, which decomposes the task and writes the '
      + 'criteria; the planner reads the task and the repository it lands in, and never sees the '
      + 'work, which does not exist yet. A third panel says why the grader is separate: a model '
      + 'grading its own output skews positive, confidently praising work it made. The planner '
      + 'hands a plan down to a generator on the left and the contract down to an evaluator on the '
      + 'right. The generator reads the plan, the contract and the last verdict, writes the '
      + 'artefact and nothing else, and never sees why the evaluator ruled as it did. The evaluator '
      + 'reads the contract and the finished work, writes PASS or NEEDS_WORK with a report, and '
      + 'never sees the generator’s chain of thought. The work crosses from generator to '
      + 'evaluator; a red arrow carries a failure report back, and the loop is capped at three '
      + 'revisions. On a pass an arrow leads down to a done panel: done now means it meets the '
      + 'pre-agreed contract, a claim you can check because the criteria are written down and every '
      + 'failure is named against one of them. A cost table beside it gives the published '
      + 'measurements: a single agent in one pass took 20 minutes and 9 dollars; the full planner, '
      + 'generator and evaluator harness on the same brief took 6 hours and 200 dollars; a later '
      + 'simplified harness on a different brief took 3 hours 50 minutes and 124 dollars 70. That '
      + 'is over 20 times the price and about 18 times the wall clock. Captions record that the '
      + 'grader judges the work against the contract rather than the story the maker tells about '
      + 'it, and that the evaluator should be handed the work and the contract but never the chain '
      + 'of thought that produced them.',
  };
}

// ---------------------------------------------------------------- diagram 2
function sprintContract() {
  resetSeq();
  const W = 960, H = 576;

  const els = [...heading('The sprint contract',
    'Agree what "done" means before the work starts, then route each criterion to the cheapest verifier that settles it.')];

  // --- the contract itself, written out as the post writes it -------------
  els.push(...card(40, 92, 880, 242, { spine: T.accent, strokeWidth: 1.5 }));
  els.push(text(58, 100, 'THE CONTRACT: A DEFINITION OF DONE, FROZEN BEFORE THE WORK',
    { size: 10, stroke: T.accent }));
  els.push(text(58, 118, fit('One small feature, six numbered criteria, and the cheapest verifier that can settle each.', 9.5, 846, 'contract sub'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(58, 140, 'CRITERION', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(600, 140, 'SETTLED BY', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(786, 140, 'KIND', { size: 8.5, stroke: T.inkSubtle }));
  els.push(rule(56, 904, 154));

  const CRITERIA = [
    ['1', 'parse() accepts an empty list and returns []', 'a unit test', 'objective', T.success],
    ['2', 'parse() raises ValueError on a malformed row, naming it', 'a unit test', 'objective', T.success],
    ['3', 'every public function carries a type annotation', 'a type checker', 'objective', T.success],
    ['4', 'the new behaviour is covered by tests, and the suite passes', 'the test runner', 'objective', T.success],
    ['5', 'the changelog gains one line describing the change', 'a five-line script', 'objective', T.success],
    ['6', 'the error a user sees is understandable without the source', 'the evaluator', 'judged', T.accent],
  ];
  CRITERIA.forEach((c, i) => {
    const y = 160 + i * 23;
    if (i) els.push(rule(56, 770, y - 6));
    els.push(rect(56, y - 1, 20, 16, { stroke: c[4], fill: c[4], strokeWidth: 1 }));
    els.push(text(56, y, c[0], { size: 10, align: 'center', width: 20, stroke: T.onAccent }));
    els.push(text(86, y, fit(c[1], 10, 500, 'criterion'), { size: 10, stroke: T.ink }));
    els.push(text(600, y, fit(c[2], 10, 180, 'verifier'), { size: 10, stroke: T.inkMuted }));
    els.push(rect(786, y - 1, 84, 17, { stroke: c[4], fill: c[4], strokeWidth: 1, roughness: 0.7 }));
    els.push(text(786, y, c[3], { size: 9, align: 'center', width: 84, stroke: T.onAccent }));
  });

  els.push(rule(56, 904, 296));
  els.push(text(58, 302, fit('Five of the six are settled by code that costs nothing per run and cannot hallucinate a pass. The evaluator grades only the residue.', 9, 846, 'note one'),
    { size: 9, stroke: T.ink }));
  els.push(text(58, 318, fit('At real size that routing is the whole game: sprint 3 of the published game-maker run carried 27 criteria for the level editor alone.', 9, 846, 'note two'),
    { size: 9, stroke: T.inkMuted }));

  // --- the three phases the contract sits above ---------------------------
  const PHASES = [
    [40, '1 - NEGOTIATE', T.primary,
      'The planner drafts the criteria and',
      'the evaluator agrees them, up front.',
      'PUSH BACK ON',
      ['- the unmeasurable', '- the impossible as written', '- the assumption of unscheduled work']],
    [340, '2 - GENERATE', T.accent,
      'The generator builds to the contract,',
      'and cannot redefine what done means.',
      'THE GENERATOR IS HANDED',
      ['- the plan and the contract', '- the last verdict, and nothing more', '- never the grader’s reasoning']],
    [640, '3 - JUDGE', T.success,
      'The evaluator scores the work against',
      'the same contract, criterion by criterion.',
      'THE VERDICT',
      ['- PASS ships the sprint', '- NEEDS_WORK names the criterion', '- returns to 2, capped at 3 revisions']],
  ];
  PHASES.forEach((p) => {
    const x = p[0];
    els.push(...card(x, 356, 280, 144, { spine: p[2], strokeWidth: 1.4 }));
    els.push(text(x + 18, 364, p[1], { size: 11, stroke: p[2] }));
    els.push(text(x + 18, 386, fit(p[3], 10, 244, 'phase line'), { size: 10, stroke: T.ink }));
    els.push(text(x + 18, 404, fit(p[4], 10, 244, 'phase line'), { size: 10, stroke: T.ink }));
    els.push(rule(x + 16, x + 264, 424));
    els.push(text(x + 18, 430, p[5], { size: 8.5, stroke: T.inkSubtle }));
    p[6].forEach((it, i) => els.push(text(x + 18, 446 + i * 16,
      fit(it, 9.5, 244, 'phase item'), { size: 9.5, stroke: T.ink })));
    els.push(line([[x + 140, 334], [x + 140, 353]],
      { stroke: T.accent, strokeWidth: 1.2, strokeStyle: 'dotted' }));
  });
  els.push(arrow([[322, 428], [337, 428]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[622, 428], [637, 428]], { stroke: T.inkMuted, strokeWidth: 1.3 }));

  els.push(text(40, 518, 'The bar was written before the work, by a different role, so the generator cannot pass by lowering it.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 542, 'Even a short explicit list turns "make it good" into something an independent grader can check line by line.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A six-criterion sprint contract routed to its verifiers, above the three phases that surround it',
    desc: 'A hand-drawn figure. A wide band across the top holds the contract: a definition of done '
      + 'frozen before the work, written out as one small feature’s six numbered criteria, each '
      + 'with the cheapest verifier that can settle it and whether it is objective or judged. One, '
      + 'parse accepts an empty list and returns an empty list, settled by a unit test, objective. '
      + 'Two, parse raises a ValueError on a malformed row and names it, a unit test, objective. '
      + 'Three, every public function carries a type annotation, a type checker, objective. Four, '
      + 'the new behaviour is covered by tests and the suite passes, the test runner, objective. '
      + 'Five, the changelog gains one line describing the change, a five-line script, objective. '
      + 'Six, the error a user sees is understandable without the source, the evaluator, judged. '
      + 'Notes below record that five of the six are settled by code that costs nothing per run and '
      + 'cannot hallucinate a pass, so the evaluator grades only the residue, and that at real size '
      + 'sprint 3 of the published game-maker run carried 27 criteria for the level editor alone. '
      + 'Dotted lines drop from the band into three phase cards. One, negotiate: the planner drafts '
      + 'the criteria and the evaluator agrees them up front, pushing back on the unmeasurable, the '
      + 'impossible as written, and the assumption of unscheduled work. Two, generate: the '
      + 'generator builds to the contract and cannot redefine what done means; it is handed the '
      + 'plan, the contract and the last verdict, and never the grader’s reasoning. Three, '
      + 'judge: the evaluator scores the work against the same contract criterion by criterion, '
      + 'where PASS ships the sprint and NEEDS_WORK names the criterion and returns to phase two, '
      + 'capped at three revisions. Captions record that the bar was written before the work by a '
      + 'different role, so the generator cannot pass by lowering it, and that even a short '
      + 'explicit list turns "make it good" into something an independent grader can check line by '
      + 'line.',
  };
}

// ---------------------------------------------------------------- diagram 3
function uncheckedEdge() {
  resetSeq();
  const W = 960, H = 470;

  const els = [...heading('The edge nothing checks',
    'The evaluator checks the work against the contract. Nothing checks the contract against the task.')];

  const chain = (x, w, name, tint) => [
    rect(x, 140, w, 56, { stroke: tint, fill: T.surface, strokeWidth: 1.5 }),
    text(x, 156, name, { size: 12, align: 'center', width: w, stroke: tint }),
  ];
  els.push(...chain(40, 120, 'TASK', T.ink));
  els.push(...chain(190, 130, 'PLANNER', T.primary));
  els.push(...chain(350, 140, 'CONTRACT', T.accent));
  els.push(...chain(520, 140, 'GENERATOR', T.accent));
  els.push(...chain(690, 230, 'EVALUATOR', T.success));

  [[162, 188], [322, 348], [492, 518], [662, 688]].forEach((a) => {
    els.push(arrow([[a[0], 168], [a[1], 168]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  });

  els.push(line([[420, 198], [420, 236], [760, 236], [760, 198]],
    { stroke: T.success, strokeWidth: 1.6 }));
  els.push(text(470, 242, 'CHECKED: the evaluator grades the work against the contract',
    { size: 9.5, stroke: T.success }));

  els.push(line([[100, 138], [100, 104], [420, 104], [420, 138]],
    { stroke: T.alert, strokeWidth: 1.8, strokeStyle: 'dashed' }));
  els.push(text(130, 84, 'NOT CHECKED: nothing grades the contract against the task',
    { size: 10, stroke: T.alert }));

  els.push(...card(40, 284, 430, 104, { spine: T.alert, strokeWidth: 1.4 }));
  els.push(text(58, 292, 'THE HOLE IN THE PATTERN', { size: 10, stroke: T.alert }));
  ['A planner that writes incomplete criteria produces a sprint where',
   'the generator satisfies every stated requirement, the evaluator',
   'accepts, and the result is wrong in a way the whole apparatus was',
   'structurally unable to notice.'].forEach((l, i) => {
    els.push(text(58, 312 + i * 17, fit(l, 9.5, 394, 'hole'), { size: 9.5, stroke: T.ink }));
  });

  els.push(...card(490, 284, 430, 104, { spine: T.primary, strokeWidth: 1.4 }));
  els.push(text(508, 292, 'WHERE TO PUT THE MISSING CHECK', { size: 10, stroke: T.primary }));
  ['- a human reads the contract, not the work: it is the cheapest minute',
   '- criteria come from the task, quoted rather than paraphrased',
   '- a contract that always passes first time is too easy, not excellent',
   '- and test the evaluator now and then with work you know is bad'].forEach((l, i) => {
    els.push(text(508, 312 + i * 17, fit(l, 9.5, 394, 'fix'), { size: 9.5, stroke: T.ink }));
  });

  els.push(text(40, 408, 'Every check in a harness pushes the trust problem somewhere else, and it is worth knowing where you pushed it.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 430, 'Here it lands on the contract, which is also the cheapest artefact in the sprint for a person to read.',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 452, 'The evaluator is fallible too: self-preference, length bias, position bias and rubric drift all survive the split.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The planner-generator-evaluator chain with its one unchecked edge marked',
    desc: 'A hand-drawn chain running task, planner, contract, generator, evaluator. A solid green '
      + 'bracket underneath links the contract to the evaluator and is labelled checked: the '
      + 'evaluator grades the work against the contract. A dashed red bracket above links the task '
      + 'to the contract and is labelled not checked: nothing grades the contract against the task. '
      + 'Below, one panel names the hole in the pattern: a planner that writes incomplete criteria '
      + 'produces a sprint where the generator satisfies every stated requirement, the evaluator '
      + 'accepts, and the result is wrong in a way the whole apparatus was structurally unable to '
      + 'notice. A second panel says where to put the missing check: a human reads the contract '
      + 'rather than the work, since that is the cheapest minute; criteria come from the task, '
      + 'quoted rather than paraphrased; a contract that always passes first time is too easy '
      + 'rather than evidence of excellence; and the evaluator should be tested now and then with '
      + 'work you know is bad. Captions record that every check pushes the trust problem somewhere '
      + 'else and it is worth knowing where, that here it lands on the contract, and that the '
      + 'evaluator is fallible too, since self-preference, length bias, position bias and rubric '
      + 'drift all survive the split.',
  };
}

module.exports = { pgeTriangle, sprintContract, uncheckedEdge };

if (require.main === module) {
  emit('01-pge-triangle', pgeTriangle());
  emit('02-sprint-contract', sprintContract());
  emit('03-the-unchecked-edge', uncheckedEdge());
}
