// The post 19 diagrams, hand-drawn.
//
//   01-layered-exits       960 x 570  Published figure for section 2.
//   02-nested-loops        960 x 624  Published figure for section 7.
//   03-after-a-guard-exit  960 x 470  NEW, published: section 5 had no figure.
//
// The existing figures answer "how does the loop stop" and "how do loops
// compose". Section 5 asks the question neither of them does: what the loop
// leaves behind when a guard catches it. That is the design decision most loops
// never make, and it is invisible in a diagram of the exits themselves.
//
// Figures 1 and 2 were single-band schematics: a row of labels and a caption.
// They now carry the two tables the post actually argues from -- the exit table
// of section 2 (what fires it, what it means, what it must leave behind) and
// the two-scale exit table of section 7 -- plus the concrete settings the
// repository really ships. Every number in these scenes is read from either
// posts/19-loop-engineering/index.md or code/03-agent-loop/src/agent_loop/loop.py;
// none is invented.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function layeredExits() {
  resetSeq();
  const W = 960, H = 570;

  const els = [...heading('The loop, with four layered exits',
    'After each turn, check the exits in order. The first to fire stops the loop, with a reason.')];

  els.push(text(40, 86, 'WHAT RUNS, AND WHAT IT REPLACES', { size: 9, stroke: T.inkSubtle }));
  els.push(text(274, 86, 'THE FOUR EXITS, CHECKED IN THIS ORDER AFTER EVERY TURN',
    { size: 9, stroke: T.inkSubtle }));

  // --- left column: the loop, the loop it replaces, and the provenance ------
  els.push(...card(40, 104, 210, 126, { spine: T.primary, strokeWidth: 1.5 }));
  els.push(text(58, 116, 'THE LOOP', { size: 14, stroke: T.ink }));
  els.push(text(58, 142, 'reason, act, observe', { size: 10, stroke: T.inkMuted }));
  els.push(text(58, 160, 'one iteration (Post 03)', { size: 10, stroke: T.inkMuted }));
  els.push(rule(58, 234, 180));
  [
    'Check the goal first: a run',
    'that has just succeeded must',
    'not be cut off by a guard.',
  ].forEach((l, i) => els.push(text(58, 190 + i * 12,
    fit(l, 8.5, 178, 'loop note'), { size: 8.5, stroke: T.ink })));

  els.push(...card(40, 246, 210, 128, { spine: T.alert, strokeWidth: 1.4 }));
  els.push(text(58, 256, 'THE BARE LOOP IT REPLACES', { size: 9, stroke: T.alert }));
  els.push(text(58, 274, fit('while not model_says_done()', 9, 178, 'bare loop'),
    { size: 9, stroke: T.ink }));
  els.push(rule(58, 234, 294));
  [
    'One exit, and the worst one:',
    'the model\'s own word that it',
    'is finished. That is victory',
    'declaration with no guard',
    'around it (Post 05).',
  ].forEach((l, i) => els.push(text(58, 302 + i * 12,
    fit(l, 8.5, 178, 'bare loop note'), { size: 8.5, stroke: T.inkMuted })));

  els.push(...card(40, 390, 210, 104, { spine: T.accent, strokeWidth: 1.4 }));
  els.push(text(58, 400, 'WHERE THESE NUMBERS COME FROM', { size: 9, stroke: T.inkSubtle }));
  [
    'max_iters = 12 and a 3-repeat',
    'stall window are the loop',
    'companion defaults, in',
    'code/03-agent-loop. 200,000 is',
    'the ceiling the post works to.',
  ].forEach((l, i) => els.push(text(58, 418 + i * 12,
    fit(l, 8.5, 178, 'provenance line'), { size: 8.5, stroke: T.ink })));

  // --- the rail: one iteration feeds four checks, in order ------------------
  els.push(line([[250, 167], [262, 167]], { stroke: T.ink, strokeWidth: 1.5 }));
  els.push(line([[262, 149], [262, 449]], { stroke: T.ink, strokeWidth: 1.3 }));

  // --- the four exits, carrying the section 2 table -------------------------
  const EXITS = [
    ['1', 'the verifier confirms the goal', 'ground truth, not self-report', T.success,
      'a check against ground truth passes (Post 11)',
      'success, and the only exit that does',
      'the result'],
    ['2', 'a hard max-iterations cap', 'max_iters = 12', T.warn,
      'the loop\'s turn bound is exhausted',
      'did not converge in the turns allowed',
      'the result so far, plus a resumable position'],
    ['3', 'a token or wall-clock budget', 'token_budget = 200,000', T.warn,
      'the next call would cross the ceiling',
      'ran out of what the task was worth',
      'the same, plus the spend to date'],
    ['4', 'no-progress detection', 'window = 3 repeats', T.warn,
      'the chosen stall signal repeats',
      'busy without moving',
      'the same, plus the repeating signature'],
  ];
  EXITS.forEach((e, i) => {
    const y = 104 + i * 100;
    const c = y + 45;
    els.push(arrow([[262, c], [272, c]], { stroke: T.ink, strokeWidth: 1.3 }));
    els.push(...card(274, y, 466, 90, { spine: e[3], strokeWidth: 1.35 }));
    els.push(rect(292, y + 12, 24, 18, { stroke: e[3], fill: e[3], strokeWidth: 1 }));
    els.push(text(292, y + 14, e[0], { size: 10, align: 'center', width: 24, stroke: T.onAccent }));
    els.push(text(326, y + 9, fit(e[1], 13, 240, 'exit name'), { size: 13, stroke: T.ink }));
    els.push(text(274, y + 12, fit(e[2], 9, 170, 'exit setting'),
      { size: 9, align: 'right', width: 450, stroke: e[3] }));
    els.push(rule(292, 722, y + 36));
    [['FIRES', e[4]], ['MEANS', e[5]], ['LEAVES', e[6]]].forEach((row, j) => {
      const ry = y + 42 + j * 16;
      els.push(text(292, ry + 1, row[0], { size: 8, stroke: T.inkSubtle }));
      els.push(text(364, ry, fit(row[1], 9.5, 356, 'exit field'), { size: 9.5, stroke: T.ink }));
    });
    els.push(line([[742, c], [788, 285]], { stroke: T.inkSubtle, strokeWidth: 1.1 }));
  });

  // --- the stop, which always names itself ---------------------------------
  // The four strings are the ones the post's own loop returns, not paraphrases.
  els.push(rect(792, 150, 128, 270, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.6 }));
  els.push(text(792, 162, 'STOP', { size: 15, align: 'center', width: 128, stroke: T.ink }));
  els.push(text(792, 186, 'with a reason', { size: 9.5, align: 'center', width: 128, stroke: T.inkMuted }));
  els.push(rule(806, 906, 210));
  els.push(text(792, 218, 'THE FOUR REASONS', { size: 8, align: 'center', width: 128, stroke: T.inkSubtle }));
  els.push(text(792, 228, 'IT CAN RETURN', { size: 8, align: 'center', width: 128, stroke: T.inkSubtle }));
  [['done', T.success], ['max-iters', T.warn], ['over-budget', T.warn], ['no-progress', T.warn]]
    .forEach((r, i) => els.push(text(792, 248 + i * 20, fit(r[0], 9.5, 112, 'stop reason'),
      { size: 9.5, align: 'center', width: 128, stroke: r[1] })));
  els.push(rule(806, 906, 330));
  [
    'each names the exit',
    'that fired, so a run',
    'is debuggable',
  ].forEach((l, i) => els.push(text(792, 338 + i * 12, fit(l, 8.5, 112, 'stop note'),
    { size: 8.5, align: 'center', width: 128, stroke: T.inkMuted })));
  els.push(text(792, 380, '(Post 21)', { size: 8.5, align: 'center', width: 128, stroke: T.inkSubtle }));

  els.push(text(40, 516, 'Design the loop, not each prompt: layered exits, so it stops for the right reason rather than by luck.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 538, 'Only the first exit means success. The other three are guards, and a run that takes one is a run you need to look at.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'One loop with four exits checked in priority order, each with what fires it and what it must leave behind',
    desc: 'A hand-drawn figure. Down the left, three cards. The loop: reason, act and observe as one '
      + 'iteration, with a note that the goal is checked first so a run that has just succeeded is '
      + 'not cut off by a guard. The bare loop it replaces: while not model_says_done, which has one '
      + 'exit and the worst one, the model\'s own word that it is finished, which is victory '
      + 'declaration with no guard around it. And the provenance of the settings shown: max_iters '
      + 'equals 12 and a three-repeat stall window are the defaults of the loop companion in '
      + 'code/03-agent-loop, while 200,000 is the token ceiling the post works to. A rail leads from '
      + 'the loop into four exit cards checked in order, each giving its setting, what fires it, '
      + 'what it means, and what it must leave behind. One, the verifier confirms the goal, on '
      + 'ground truth rather than self-report: a check against ground truth passes, which means '
      + 'success and is the only exit that does, and it leaves the result. Two, a hard '
      + 'max-iterations cap of 12: the loop\'s turn bound is exhausted, which means it did not '
      + 'converge in the turns allowed, and it leaves the result so far plus a resumable position. '
      + 'Three, a token or wall-clock budget of 200,000 tokens: the next call would cross the '
      + 'ceiling, which means it ran out of what the task was worth, and it leaves the same plus the '
      + 'spend to date. Four, no-progress detection over a window of three repeats: the chosen stall '
      + 'signal repeats, which means busy without moving, and it leaves the same plus the repeating '
      + 'signature. All four converge on a STOP box, which lists the four reasons the loop can '
      + 'return: done, max-iters, over-budget and no-progress. Each names the exit that fired, so a '
      + 'run is debuggable. Captions record that you should design the loop rather than '
      + 'each prompt, so that layered exits make it stop for the right reason rather than by luck, '
      + 'and that only the first exit means success while the other three are guards, so a run that '
      + 'takes one is a run you need to look at.',
  };
}

// ---------------------------------------------------------------- diagram 2
function nestedLoops() {
  resetSeq();
  const W = 960, H = 624;

  const els = [...heading('Composing loops: an inner verify inside an outer task loop',
    'The inner loop gets one step right; the outer loop makes progress across steps.')];

  // --- the composition itself ----------------------------------------------
  els.push(rect(40, 88, 880, 196, { stroke: T.accent, strokeWidth: 1.6, strokeStyle: 'dashed' }));
  els.push(text(58, 96, 'OUTER LOOP: ONE TASK PER PASS (RALPH, POST 18)', { size: 10, stroke: T.accent }));

  els.push(rect(70, 132, 190, 54, { stroke: T.ink, fill: T.surface, strokeWidth: 1.4 }));
  els.push(text(70, 142, 'pick the next task', { size: 11.5, align: 'center', width: 190, stroke: T.ink }));
  els.push(text(70, 164, 'from the spec', { size: 9.5, align: 'center', width: 190, stroke: T.inkMuted }));

  els.push(rect(292, 116, 330, 124, { stroke: T.success, strokeWidth: 1.6, strokeStyle: 'dashed' }));
  els.push(text(308, 122, 'INNER LOOP: VERIFY AND RETRY (POST 11)', { size: 10, stroke: T.success }));
  els.push(rect(308, 142, 298, 48, { stroke: T.ink, fill: T.surface, strokeWidth: 1.4 }));
  els.push(text(308, 152, 'generate, then verify', { size: 11.5, align: 'center', width: 298, stroke: T.ink }));
  els.push(text(308, 172, 'retry until the check passes', { size: 9, align: 'center', width: 298, stroke: T.inkMuted }));
  els.push(text(308, 198, fit('bounded by its own retry cap:', 9, 298, 'inner gloss'),
    { size: 9, stroke: T.inkMuted }));
  els.push(text(308, 214, fit('three to five attempts, then it gives up', 9, 298, 'inner gloss'),
    { size: 9, stroke: T.inkMuted }));

  els.push(rect(654, 132, 190, 54, { stroke: T.ink, fill: T.surface, strokeWidth: 1.4 }));
  els.push(text(654, 142, 'commit and advance', { size: 11.5, align: 'center', width: 190, stroke: T.ink }));
  els.push(text(654, 164, 'the work is durable', { size: 9.5, align: 'center', width: 190, stroke: T.inkMuted }));

  [
    'the spec is the queue, and',
    'the handoff file is the bridge',
  ].forEach((l, i) => els.push(text(76, 200 + i * 14,
    fit(l, 8.5, 178, 'outer note'), { size: 8.5, stroke: T.inkMuted })));
  [
    'one commit per task, so the',
    'outer loop has its progress record',
  ].forEach((l, i) => els.push(text(660, 200 + i * 14,
    fit(l, 8.5, 184, 'outer note'), { size: 8.5, stroke: T.inkMuted })));

  els.push(arrow([[262, 159], [288, 159]], { stroke: T.ink, strokeWidth: 1.4 }));
  els.push(arrow([[624, 159], [650, 159]], { stroke: T.ink, strokeWidth: 1.4 }));
  els.push(arrow([[846, 159], [884, 159], [884, 270], [56, 270], [56, 159], [66, 159]],
    { stroke: T.accent, strokeWidth: 1.4 }));
  els.push(text(392, 248, 'the next task, in a fresh context (Post 18)', { size: 9, stroke: T.accent }));

  // --- the same four exits, re-decided at each scale ------------------------
  els.push(text(40, 296, 'THE SAME FOUR EXITS, RE-DECIDED AT EACH SCALE', { size: 9, stroke: T.inkSubtle }));
  els.push(text(190, 312, 'INNER LOOP: GETTING ONE STEP RIGHT', { size: 8.5, stroke: T.success }));
  els.push(text(546, 312, 'OUTER LOOP: PROGRESS ACROSS STEPS', { size: 8.5, stroke: T.accent }));
  els.push(rule(40, 920, 328));

  const SCALES = [
    ['1', 'goal', T.success,
      'the step\'s check passes: tests green, the diff applies',
      'converged(): the acceptance gate passes on every criterion'],
    ['2', 'iteration cap', T.warn,
      'a retry cap of three to five attempts',
      'a task cap across the whole run'],
    ['3', 'budget', T.warn,
      'a per-step share, or a draw against a shared pool',
      'the run ceiling, which is the one the invoice sees'],
    ['4', 'no-progress', T.warn,
      'the same tool signature repeating',
      'no new commit, or commits that alternate rather than accumulate'],
  ];
  SCALES.forEach((s, i) => {
    const y = 338 + i * 30;
    els.push(rect(40, y - 1, 22, 17, { stroke: s[2], fill: s[2], strokeWidth: 1 }));
    els.push(text(40, y + 1, s[0], { size: 9.5, align: 'center', width: 22, stroke: T.onAccent }));
    els.push(text(70, y - 2, fit(s[1], 11, 110, 'scale name'), { size: 11, stroke: T.ink }));
    els.push(text(190, y - 1, fit(s[3], 9.5, 346, 'inner cell'), { size: 9.5, stroke: T.ink }));
    els.push(text(546, y - 1, fit(s[4], 9.5, 374, 'outer cell'), { size: 9.5, stroke: T.ink }));
    els.push(rule(40, 920, y + 20));
  });

  // --- allocating one budget across both, and the hazard --------------------
  const PANELS = [
    [40, T.primary, 'FIXED PER-TASK SHARE', [
      '200,000 across ten tasks is',
      '20,000 each. Predictable, and',
      'wasteful: a task needing',
      '30,000 fails while nine cheap',
      'tasks leave headroom unused.']],
    [344, T.accent, 'SHARED POOL, PER-TASK CAP', [
      'Each task draws what it needs',
      'from the run ceiling, but never',
      'more than a fraction of it.',
      'Spends the headroom; one bad',
      'task takes a fifth before its cap.']],
    [648, T.alert, 'THE HAZARD NOBODY NAMES', [
      'An inner loop that burns its retry',
      'budget and fails looks like',
      'progress: the state changed on',
      'every pass. Three tasks ending in',
      'retries-exhausted is a stalled run.']],
  ];
  PANELS.forEach((p) => {
    els.push(...card(p[0], 464, 272, 104, { spine: p[1], strokeWidth: 1.35 }));
    els.push(text(p[0] + 16, 472, fit(p[2], 9, 240, 'panel head'), { size: 9, stroke: p[1] }));
    els.push(rule(p[0] + 16, p[0] + 256, 490));
    p[3].forEach((l, i) => els.push(text(p[0] + 16, 496 + i * 14,
      fit(l, 8.5, 240, 'panel line'), { size: 8.5, stroke: T.ink })));
  });

  els.push(text(40, 584, 'Each loop carries its own layered exits at its own scale: the inner caps retries, the outer caps iterations and budget.',
    { size: 11, stroke: T.ink }));
  els.push(text(40, 606, 'The outer detector must watch the inner loop\'s outcome rather than its activity, or a stalled run reads as a busy transcript.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'An inner verify-and-retry loop nested inside an outer task loop, with the exits and budget each scale needs',
    desc: 'A hand-drawn figure of one loop inside another. The outer loop, dashed, runs one task '
      + 'per pass in the manner of a Ralph loop: it picks the next task from the spec, hands it to '
      + 'the inner loop, and then commits and advances so the work is durable, before returning for '
      + 'the next task in a fresh context. Notes on the outer boxes record that the spec is the '
      + 'queue and the handoff file is the bridge, and that one commit per task is what gives the '
      + 'outer loop its progress record. The inner loop, also dashed, generates and then verifies, '
      + 'retrying until the check passes and bounded by its own retry cap of three to five attempts. '
      + 'Below, a table re-decides each of the four exits at each scale. Goal: for the inner loop, '
      + 'the step\'s check passes, with tests green and the diff applying; for the outer, converged, '
      + 'meaning the acceptance gate passes on every criterion. Iteration cap: a retry cap of three '
      + 'to five attempts inside, a task cap across the whole run outside. Budget: a per-step share '
      + 'or a draw against a shared pool inside, and outside the run ceiling, which is the one the '
      + 'invoice sees. No-progress: the same tool signature repeating inside, and outside no new '
      + 'commit, or commits that alternate rather than accumulate. Three panels close the figure. A '
      + 'fixed per-task share divides 200,000 tokens across ten tasks into 20,000 each, which is '
      + 'predictable and wasteful, because a task needing 30,000 fails while nine cheap tasks leave '
      + 'headroom unused. A shared pool with a per-task cap lets each task draw what it needs from '
      + 'the run ceiling but never more than a fraction of it, which spends the headroom while one '
      + 'bad task can take a fifth of it before its cap fires. And the hazard nobody names: an inner '
      + 'loop that burns its retry budget and fails looks like progress because the state changed on '
      + 'every pass, so three tasks ending in retries-exhausted is a stalled run. Captions record '
      + 'that each loop carries its own layered exits at its own scale, with the inner one capping '
      + 'retries and the outer one capping iterations and budget, and that the outer detector must '
      + 'watch the inner loop\'s outcome rather than its activity, or a stalled run reads as a busy '
      + 'transcript.',
  };
}

// ---------------------------------------------------------------- diagram 3
function afterAGuardExit() {
  resetSeq();
  const W = 960, H = 470;

  const els = [...heading('A guard exit is a handoff, not a full stop',
    'What the loop leaves behind when a guard catches it is a design decision, and most loops never make it.')];

  els.push(...card(40, 92, 880, 58, { spine: T.success, strokeWidth: 1.5 }));
  els.push(text(60, 104, '1   The verifier confirms the goal', { size: 13, stroke: T.success }));
  els.push(text(60, 126, 'the intended exit, and the only one that means success', { size: 9, stroke: T.inkMuted }));
  els.push(text(600, 112, 'returns a result', { size: 13, stroke: T.ink }));

  els.push(...card(40, 162, 880, 58, { spine: T.warn, strokeWidth: 1.5 }));
  els.push(text(60, 174, '2, 3, 4   Max iterations, budget spent, no progress', { size: 13, stroke: T.warn }));
  els.push(text(60, 196, 'the run did not finish, and something caught it', { size: 9, stroke: T.inkMuted }));
  els.push(text(560, 182, 'returns a result AND a resumable position', { size: 13, stroke: T.ink }));

  els.push(text(40, 232, 'THREE THINGS A GUARD EXIT SHOULD DO BEFORE IT RETURNS', { size: 9, stroke: T.inkSubtle }));

  const DUTIES = [
    [40, T.success, 'CHECKPOINT THE WORK',
      ['A run stopped at the ceiling has produced',
       'real partial progress: commits, files, a',
       'half-finished refactor. Durable state (Post 08)',
       'makes it resumable: raise the ceiling and go.'],
      ['The whole spend is forfeit, which is odd',
       'from a guard whose purpose was to save it.']],
    [340, T.primary, 'SAY WHAT IT WAS DOING',
      ['The stop reason is necessary and not',
       'sufficient. "over-budget at iteration 12"',
       'plus the handoff file: what is done, what',
       'was next, and what was blocked.'],
      ['A human re-derives the state from a trace',
       'instead of resuming in about a minute.']],
    [640, T.warn, 'ESCALATE IF IT WARRANTS IT',
      ['No-progress and budget-exhausted are',
       'exactly the escalation triggers of Post 15.',
       'A loop that stops silently is a loop that',
       'waits to be noticed.'],
      ['You pay the wall-clock between the stall',
       'and the discovery, often more than the run.']],
  ];
  DUTIES.forEach((d) => {
    els.push(...card(d[0], 250, 280, 156, { spine: d[1], strokeWidth: 1.4 }));
    els.push(text(d[0] + 16, 258, d[2], { size: 10, stroke: d[1] }));
    d[3].forEach((l, i) => els.push(text(d[0] + 16, 278 + i * 15,
      fit(l, 9, 248, 'duty line'), { size: 9, stroke: T.ink })));
    els.push(rule(d[0] + 16, d[0] + 264, 344));
    els.push(text(d[0] + 16, 352, 'IF YOU SKIP IT', { size: 8.5, stroke: T.inkSubtle }));
    d[4].forEach((l, i) => els.push(text(d[0] + 16, 368 + i * 14,
      fit(l, 9, 248, 'skip line'), { size: 9, stroke: T.alert })));
  });

  els.push(text(40, 426, 'The rule of thumb: the intended exit returns a result; a guard exit returns a result and a resumable position.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 448, 'And check the budget before the call that would breach it, or the ceiling is a notification rather than a ceiling.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'What a guard exit must leave behind, against what the intended exit returns',
    desc: 'A hand-drawn figure. Two bands compare the exits. The first, the verifier confirming the '
      + 'goal, is the intended exit and the only one that means success; it returns a result. The '
      + 'second, covering max iterations, budget spent and no progress, means the run did not '
      + 'finish and something caught it; it returns a result and a resumable position. Below, three '
      + 'panels give what a guard exit should do before it returns, each with what happens if you '
      + 'skip it. Checkpoint the work: a run stopped at the ceiling has produced real partial '
      + 'progress in commits, files and half-finished refactors, and durable state makes it '
      + 'resumable, so skipping it forfeits the whole spend, which is odd from a guard whose '
      + 'purpose was to save it. Say what it was doing: the stop reason is necessary but not '
      + 'sufficient, and a message such as over-budget at iteration twelve plus the handoff file '
      + 'giving what is done, what was next and what was blocked is the difference between resuming '
      + 'in a minute and a human re-deriving the state from a trace. Escalate if it warrants it: '
      + 'no-progress and budget-exhausted are exactly the escalation triggers of post 15, and a '
      + 'loop that stops silently waits to be noticed, so skipping it means paying the wall-clock '
      + 'between the stall and the discovery, often more than the run itself. Captions record the '
      + 'rule of thumb, that the intended exit returns a result while a guard exit returns a result '
      + 'and a resumable position, and that the budget should be checked before the call that would '
      + 'breach it, or the ceiling is a notification rather than a ceiling.',
  };
}

module.exports = { layeredExits, nestedLoops, afterAGuardExit };

if (require.main === module) {
  emit('01-layered-exits', layeredExits());
  emit('02-nested-loops', nestedLoops());
  emit('03-after-a-guard-exit', afterAGuardExit());
}
