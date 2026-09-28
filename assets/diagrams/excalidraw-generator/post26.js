// The post 26 diagrams, hand-drawn.
//
//   01-capstone-architecture     960 x 470  Mirror of the existing figure.
//   02-multi-context-run         960 x 400  Mirror.
//   03-eval-observability-loop   960 x 380  Mirror.
//
// The capstone already ships three figures covering the three things it needs a
// picture for: what the harness is, how state survives a context reset, and the
// loop that improves the harness rather than the model. Nothing here is
// promoted; all three scenes are alternates, as in post 01.

const { T, rect, text, line, arrow, circle, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function architecture() {
  resetSeq();
  const W = 960, H = 470;

  const els = [...heading('Every component of the series, wired into one harness',
    'The spec on the left is the source of truth. Everything right of it turns that spec into verified commits, unattended.')];

  // spec
  els.push(...card(M, 132, 140, 96, { spine: T.ink, strokeWidth: 1.6 }));
  els.push(text(54, 146, 'THE SPEC', { size: 11, stroke: T.ink }));
  els.push(text(54, 168, fit('the source of truth,', 9, 118, 'spec a'), { size: 9, stroke: T.inkMuted }));
  els.push(text(54, 182, fit('re-read every task', 9, 118, 'spec b'), { size: 9, stroke: T.inkMuted }));
  els.push(text(54, 206, 'Post 18', { size: 8.5, stroke: T.inkSubtle }));
  els.push(arrow([[180, 178], [212, 178]], { stroke: T.ink, strokeWidth: 1.2 }));

  // driver
  els.push(...card(216, 132, 150, 96, { spine: T.primary, strokeWidth: 1.8 }));
  els.push(text(230, 146, 'RALPH DRIVER', { size: 11, stroke: T.ink }));
  els.push(text(230, 168, fit('one task per fresh', 9, 128, 'drv a'), { size: 9, stroke: T.inkMuted }));
  els.push(text(230, 182, fit('context, then reset', 9, 128, 'drv b'), { size: 9, stroke: T.inkMuted }));
  els.push(text(230, 206, 'Posts 18, 19', { size: 8.5, stroke: T.inkSubtle }));
  els.push(arrow([[370, 178], [402, 178]], { stroke: T.ink, strokeWidth: 1.2 }));

  // three roles
  els.push(rect(406, 118, 250, 124, { stroke: T.border, strokeWidth: 1, strokeStyle: 'dashed' }));
  els.push(text(418, 124, 'THREE SEPARATED ROLES  ·  Post 12', { size: 8.5, stroke: T.inkSubtle }));
  [['PLANNER', 'sequences the tasks', T.accent],
   ['GENERATOR', 'proposes the code', T.primary],
   ['EVALUATOR', 'verifies it, independently', T.success]].forEach((r, i) => {
    const y = 142 + i * 32;
    els.push(rect(418, y, 226, 26, { stroke: r[2], fill: T.surface, strokeWidth: 1 }));
    els.push(text(428, y + 7, r[0], { size: 9, stroke: r[2] }));
    els.push(text(506, y + 7, fit(r[1], 8.5, 136, 'role'), { size: 8.5, stroke: T.inkMuted }));
  });
  els.push(arrow([[660, 178], [692, 178]], { stroke: T.ink, strokeWidth: 1.2 }));

  // gates
  els.push(...card(696, 132, 224, 96, { spine: T.alert }));
  els.push(text(710, 146, 'THE BUILD #2 GATES', { size: 10.5, stroke: T.ink }));
  els.push(text(710, 168, fit('hook, sandbox, approval,', 9, 200, 'g a'), { size: 9, stroke: T.inkMuted }));
  els.push(text(710, 182, fit('every tool call, every task', 9, 200, 'g b'), { size: 9, stroke: T.inkMuted }));
  els.push(text(710, 206, 'Posts 13, 14, 15', { size: 8.5, stroke: T.inkSubtle }));

  // durable stores
  els.push(text(M, 258, 'WHAT CROSSES BETWEEN TASKS', { size: 8.5, stroke: T.inkSubtle }));
  [['THE WORKSPACE', 'commits, so work survives a reset', 'Post 08', T.neutral3, M],
   ['THE RATCHET', 'rules, so a failure is not repeated', 'Post 10', T.success, 480]].forEach((s) => {
    els.push(...card(s[4], 276, 440, 62, { spine: s[3] }));
    els.push(text(s[4] + 14, 288, s[0], { size: 10.5, stroke: T.ink }));
    els.push(text(s[4] + 14, 308, fit(s[1], 9, 400, 'store'), { size: 9, stroke: T.inkMuted }));
    els.push(text(s[4] + 360, 288, s[2], { size: 8.5, align: 'right', width: 64, stroke: T.inkSubtle }));
  });

  // tracer + meter
  [['THE TRACER', 'every run, iteration and call becomes a span', 'Post 21', T.primary, M],
   ['THE COST METER', 'a budget ceiling the run stops against', 'Post 23', T.warn, 480]].forEach((s) => {
    els.push(...card(s[4], 352, 440, 62, { spine: s[3] }));
    els.push(text(s[4] + 14, 364, s[0], { size: 10.5, stroke: T.ink }));
    els.push(text(s[4] + 14, 384, fit(s[1], 9, 400, 'obs'), { size: 9, stroke: T.inkMuted }));
    els.push(text(s[4] + 360, 364, s[2], { size: 8.5, align: 'right', width: 64, stroke: T.inkSubtle }));
  });

  els.push(text(M, 436, fit('Traces feed evaluation and A/B tests, and what they find is fixed in the harness rather than asked of the model.', 11.5, 880, 'foot'),
    { size: 11.5, stroke: T.ink }));

  return {
    W, H, els,
    title: 'The full capstone harness architecture',
    desc: 'A hand-drawn architecture of the capstone. On the left the spec is the source of truth, '
      + 're-read every task, from Post 18. It feeds a Ralph driver that runs one task per fresh '
      + 'context and then resets, from Posts 18 and 19. The driver runs each task through three '
      + 'separated roles inside a dashed boundary, from Post 12: a planner that sequences the tasks, '
      + 'a generator that proposes the code, and an evaluator that verifies it independently. Tool '
      + 'calls then pass through the Build number two gates, from Posts 13, 14 and 15: hook, sandbox '
      + 'and approval, on every tool call of every task. Below, two durable stores cross between '
      + 'tasks: the workspace, which commits so work survives a reset, from Post 08; and the ratchet, '
      + 'which holds rules so a failure is not repeated, from Post 10. Below those, a tracer turns '
      + 'every run, iteration and call into a span, from Post 21, and a cost meter enforces a budget '
      + 'ceiling the run stops against, from Post 23. A closing line records that traces feed '
      + 'evaluation and A/B tests, and that what they find is fixed in the harness rather than asked '
      + 'of the model.',
  };
}

// ---------------------------------------------------------------- diagram 2
function multiContext() {
  resetSeq();
  const W = 960, H = 556;

  const els = [...heading('The context resets; the state and the learning do not',
    'Three tasks, three fresh windows. Everything that has to survive lives on disk between them.')];

  const TASKS = [
    [M, 'TASK 1', ['starts clean', 'writes parser.py', 'commits it', 'fails once, learns a rule']],
    [340, 'TASK 2', ['starts clean', 'reads the workspace', 'reads the rule', 'does not repeat the failure']],
    [640, 'TASK 3', ['starts clean', 'reads both again', 'commits', 'adds one more rule']],
  ];
  TASKS.forEach((t, i) => {
    els.push(...card(t[0], 112, 280, 118, { spine: T.primary, strokeStyle: 'dashed' }));
    els.push(text(t[0] + 14, 124, t[1], { size: 11, stroke: T.ink }));
    els.push(text(t[0] + 14, 144, 'a fresh context window', { size: 8.5, stroke: T.inkSubtle }));
    t[2].forEach((l, j) => els.push(text(t[0] + 14, 164 + j * 15, fit(l, 9, 250, 'task'),
      { size: 9, stroke: T.inkMuted })));
    // The window boundary between tasks. There is 20px of gap here, which is not
    // enough for a word, so the separator carries it and the caption below names it.
    if (i < 2) {
      els.push(line([[t[0] + 290, 124], [t[0] + 290, 218]],
        { stroke: T.alert, strokeWidth: 1.3, strokeStyle: 'dotted' }));
    }
  });
  els.push(text(M, 244, fit('each dotted divider is a context reset: everything above this line is discarded at the end of its task', 9, 880, 'discard'),
    { size: 9, stroke: T.alert }));
  els.push(line([[M, 258], [920, 258]], { stroke: T.alert, strokeWidth: 1.2, strokeStyle: 'dashed' }));

  // The two stores, with what each of them is holding by the end of task 3.
  [['THE WORKSPACE', 'accumulates committed files', T.neutral3, M,
    ['after task 1   parser.py, committed', 'after task 2   parser.py, unchanged and re-read',
     'after task 3   parser.py plus the task 3 file'],
    'git is the versioning, so a bad task is a revert rather than a rebuild'],
   ['THE RATCHET', 'accumulates learned rules', T.success, 480,
    ['after task 1   one rule, learned from the failure', 'after task 2   the same rule, injected and obeyed',
     'after task 3   two rules, both in every later context'],
    'append-only: a rule is recorded once, then carried into every attempt after it'],
  ].forEach((s) => {
    els.push(...card(s[3], 274, 440, 168, { spine: s[2], strokeWidth: 1.6 }));
    els.push(text(s[3] + 14, 286, s[0], { size: 11, stroke: T.ink }));
    els.push(text(s[3] + 14, 306, fit(s[1], 9.5, 340, 'store'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(s[3] + 350, 286, 'durable', { size: 8.5, align: 'right', width: 74, stroke: s[2] }));
    els.push(rule(s[3] + 14, s[3] + 426, 326));
    s[4].forEach((l, i) => els.push(text(s[3] + 14, 340 + i * 20, fit(l, 9, 408, 'store row'),
      { size: 9, stroke: T.ink })));
    els.push(text(s[3] + 14, 410, fit(s[5], 8.5, 408, 'store note'),
      { size: 8.5, stroke: T.inkSubtle }));
  });

  els.push(text(M, 466, fit('A reset is not a loss, as long as everything the next task needs was written down before the window closed.', 11.5, 880, 'foot'),
    { size: 11.5, stroke: T.ink }));
  els.push(text(M, 490, fit('Task 2 does not repeat task 1 failure, and it never saw task 1 window: it read the rule that outlived it.', 11.5, 880, 'foot 2'),
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Durable state crossing fresh contexts in a multi-context run',
    desc: 'A hand-drawn figure of three tasks running left to right, each in its own fresh context '
      + 'window drawn with a dashed border. Task one starts clean, writes parser.py, commits it, '
      + 'fails once and learns a rule. Task two starts clean, reads the workspace, reads the rule, '
      + 'and does not repeat the failure. Task three starts clean, reads both again, commits, and '
      + 'adds one more rule. Between the tasks, dotted markers labelled reset show the window being '
      + 'discarded. A dashed line across the figure marks that everything above it is discarded at '
      + 'the end of its task. Below the line sit two durable stores, each showing what it holds '
      + 'after every task: the workspace, which accumulates '
      + 'committed files, and the ratchet, which accumulates learned rules, both labelled durable. A '
      + 'closing line records that a reset is not a loss, as long as everything the next task needs '
      + 'was written down before the window closed.',
  };
}

// ---------------------------------------------------------------- diagram 3
function evalLoop() {
  resetSeq();
  const W = 960, H = 580;

  const els = [...heading('The loop that improves the harness, not the model',
    'Four stages. The model is fixed the whole way round; what changes each turn is the machine around it.')];

  const STAGES = [
    [M, T.primary, '1', 'THE HARNESS RUNS', ['and emits traces: spans for', 'every run, call and gate']],
    [268, T.accent, '2', 'TRACES FEED EVALS', ['harness A/B on a fixed task', 'set, scored on trajectories']],
    [496, T.warn, '3', 'FAILURES LOCALISE', ['a regression points at one', 'component, not at the model']],
    [724, T.success, '4', 'THE FIX IS RATCHETED', ['a rule, a hook, or a replay', 'added to the regression set']],
  ];
  STAGES.forEach((s, i) => {
    els.push(...card(s[0], 116, 196, 116, { spine: s[1], strokeWidth: 1.4 }));
    els.push(circle(s[0] + 24, 140, 13, { stroke: s[1], fill: T.surface, strokeWidth: 1.2 }));
    els.push(text(s[0] + 18, 133, s[2], { size: 11, stroke: s[1] }));
    els.push(text(s[0] + 46, 133, s[3], { size: 10, stroke: T.ink }));
    els.push(text(s[0] + 16, 172, fit(s[4][0], 9, 172, 'stage a'), { size: 9, stroke: T.inkMuted }));
    els.push(text(s[0] + 16, 188, fit(s[4][1], 9, 172, 'stage b'), { size: 9, stroke: T.inkMuted }));
    if (i < 3) els.push(arrow([[s[0] + 202, 174], [s[0] + 224, 174]], { stroke: T.ink, strokeWidth: 1.2 }));
  });

  // the return leg
  els.push(arrow([[822, 236], [822, 268], [138, 268], [138, 236]],
    { stroke: T.success, strokeWidth: 1.3, strokeStyle: 'dashed' }));
  els.push(text(348, 274, fit('the fix changes the harness, and the cycle repeats', 9.5, 300, 'return'),
    { size: 9.5, stroke: T.success }));

  // --- second tier: stage one, as the demo actually emits it -------------
  // The span tree is the companion's unabridged output, quoted in section 7.
  els.push(text(M, 306, 'STAGE ONE IS NOT ABSTRACT: THIS IS THE SPAN TREE THE DEMO PRINTS',
    { size: 10, stroke: T.inkSubtle }));

  els.push(...card(40, 326, 520, 186, { spine: T.primary, strokeWidth: 1.3 }));
  [[0, 'build.run  [spec_tasks=2 stop.reason=spec_complete]', T.ink],
   [1, 'task  [task=add passed=True]', T.ink],
   [2, 'attempt  [index=1 outcome=fail]', T.alert],
   [3, 'generate', T.inkMuted],
   [3, 'evaluate  [ok=False]', T.alert],
   [2, 'attempt  [index=2 outcome=pass]', T.success],
   [3, 'generate', T.inkMuted],
   [3, 'evaluate  [ok=True]', T.success],
   [1, 'task  [task=is_even passed=True]', T.ink]].forEach((r, i) => {
    els.push(text(58 + r[0] * 14, 340 + i * 18, r[1], { size: 8.5, family: 3, stroke: r[2] }));
  });

  els.push(...card(578, 326, 342, 186, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(596, 334, 'WHAT THE TREE MAKES POSSIBLE', { size: 9.5, stroke: T.success }));
  [['the shape is the eval', 'one failed attempt then a pass is a', 'trajectory, not just a final answer'],
   ['the failure has an address', 'attempt 1 of task add, at evaluate:', 'a component, not "the agent"'],
   ['the fix has a regression', 'that attempt becomes a replay, so', 'the next harness cannot lose it']]
    .forEach((r, i) => {
      const y = 356 + i * 52;
      els.push(text(596, y, r[0], { size: 9, stroke: T.ink }));
      els.push(text(596, y + 15, fit(r[1], 8.5, 306, 'why a'), { size: 8.5, stroke: T.inkMuted }));
      els.push(text(596, y + 28, fit(r[2], 8.5, 306, 'why b'), { size: 8.5, stroke: T.inkMuted }));
    });

  els.push(text(M, 534, fit('Nothing in this cycle upgrades the model. Every turn of it makes the same model produce better runs.', 11.5, 880, 'foot'),
    { size: 11.5, stroke: T.ink }));
  els.push(text(M, 556, fit('The tree is what turns "it felt flaky" into an attempt, a stage and a component you can name.', 11.5, 880, 'foot 2'),
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The closed improvement loop around the harness',
    desc: 'A hand-drawn cycle of four numbered stages running left to right. Stage one, the harness '
      + 'runs and emits traces, with spans for every run, call and gate. Stage two, traces feed '
      + 'evaluations: harness A/B on a fixed task set, scored on whole trajectories. Stage three, '
      + 'failures localise, so a regression points at one component rather than at the model. Stage '
      + 'four, the fix is ratcheted: a rule, a hook, or a replay added to the regression set. A '
      + 'dashed return arrow runs from the fourth stage back to the first, labelled to say the fix '
      + 'changes the harness and the cycle repeats. A closing line records that nothing in this cycle '
      + 'upgrades the model, and that every turn of it makes the same model produce better runs. '
      + 'A second tier shows that the first stage is not abstract, quoting the span tree the demo '
      + 'actually prints: a build run over two spec tasks ending with the stop reason spec '
      + 'complete, the first task passing on its second attempt after the first attempt failed '
      + 'its evaluation, and the second task passing on its first. A panel beside it gives what '
      + 'the tree makes possible: the shape is the eval, because one failed attempt then a pass '
      + 'is a trajectory rather than a final answer; the failure has an address, at attempt one '
      + 'of the add task, at evaluate; and the fix has a regression, because that attempt becomes '
      + 'a replay the next harness cannot lose.',
  };
}

emit('01-capstone-architecture', architecture());
emit('02-multi-context-run', multiContext());
emit('03-eval-observability-loop', evalLoop());
