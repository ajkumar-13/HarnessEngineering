// The post 22 diagrams, hand-drawn.
//
//   01-output-vs-trajectory   960 x 636  Mirror of the existing figure, densified.
//   02-harness-ab-pipeline    960 x 560  Mirror, densified.
//   03-production-funnel      960 x 622  NEW, published: section 5 had no figure.
//
// Sections 1 to 4 are about proxies you run before shipping, and they have two
// figures between them. Section 5 is the one that connects all of it to the
// ledger, and it had none: three stages, each a stricter filter than the last,
// ending in the only number a business actually asks about.
//
// Every number drawn here is read out of the post itself, and each one is
// labelled where the post labels it illustrative:
//   fig 1  277,000 input tokens over 12 iterations, about $0.83 at an
//          illustrative $3 per million   (section 6)
//          the "what changed / which eval" decision table   (section 1)
//   fig 2  60 tasks, 3 seeds, 2 configs = 360 runs, ~72 min at 20-way, ~$300
//          (section 6's cadence table); the sign-test worked case, 12
//          discordant pairs at 8-4 giving p = 0.39 and at 10-2 giving
//          p = 0.039, and the +/- 20 point unpaired interval   (section 8)
//   fig 3  the one-week illustrative ledger: 200 runs, 118 vs 132 accepted
//          (59% vs 66% first-pass), 9 vs 14 reverted (7.6% vs 10.6% escape),
//          109 vs 118 shipped, $170 vs $510 model spend, $5,170 vs $5,900
//          review, $49 vs $54 per merged PR   (section 10)

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

const MONO = 3;

// ---------------------------------------------------------------- diagram 1
function outputVsTrajectory() {
  resetSeq();
  const W = 960, H = 636;

  const els = [...heading('The unit of evaluation moves from one answer to one run',
    'On the left, grade a single completion. On the right, grade a whole trajectory by whether the task resolved.')];

  // --- left panel: one answer in, one score out ---------------------------
  els.push(...card(40, 90, 430, 320, { spine: T.neutral3, strokeWidth: 1.4 }));
  els.push(text(58, 98, 'OUTPUT EVAL, PER COMPLETION', { size: 10, stroke: T.inkSubtle }));
  els.push(text(58, 114, fit('the Context Engineering lens: one answer in, one score out', 9, 398, 'left sub'),
    { size: 9, stroke: T.inkMuted }));

  [['prompt', 'one task', 'one fixed wording, sampled once, with no tools and no environment'],
   ['output', 'one completion', 'the final message only: nothing about how the model got there'],
   ['judge', 'a score from 0.0 to 1.0', 'one number per completion, comparable across every prompt edit'],
  ].forEach((b, i) => {
    const y = 134 + i * 56;
    els.push(rect(58, y, 394, 42, { stroke: T.ink, fill: T.surface, strokeWidth: 1.3 }));
    els.push(text(72, y + 6, b[0], { size: 11.5, stroke: T.ink }));
    els.push(text(176, y + 8, fit(b[1], 9.5, 260, 'left row value'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(72, y + 24, fit(b[2], 8.5, 366, 'left row detail'), { size: 8.5, stroke: T.inkMuted }));
    if (i) els.push(arrow([[255, y - 12], [255, y - 3]], { stroke: T.inkMuted, strokeWidth: 1.2 }));
  });

  els.push(rule(56, 452, 300));
  els.push(text(58, 306, 'THE GRADERS IT CAN USE', { size: 9, stroke: T.inkSubtle }));
  els.push(text(58, 322, fit('exact match, regular expression, rubric, model judge', 9.5, 394, 'left graders'),
    { size: 9.5, stroke: T.ink }));
  els.push(text(58, 344, 'WHAT ONE SCORE CANNOT SEE', { size: 9, stroke: T.inkSubtle }));
  els.push(text(58, 360, fit('the recovery, the loop, the tool errors, the stop', 9.5, 394, 'left blind'),
    { size: 9.5, stroke: T.ink }));
  els.push(text(58, 382, 'Cheap, deterministic and repeatable, and the right tool', { size: 9, stroke: T.inkMuted }));
  els.push(text(58, 396, 'for tuning a prompt. It runs on every commit.', { size: 9, stroke: T.inkMuted }));

  // --- right panel: a whole run, then an outcome --------------------------
  els.push(...card(490, 90, 430, 320, { spine: T.success, strokeWidth: 1.4 }));
  els.push(text(508, 98, 'TRAJECTORY AND OUTCOME EVAL, PER RUN', { size: 10, stroke: T.success }));
  els.push(text(508, 114, fit('a whole multi-step run: did the real task resolve?', 9, 398, 'right sub'),
    { size: 9, stroke: T.inkMuted }));

  [['iteration 1', 'model.call, then tool: bash', false],
   ['iteration 2', 'model.call, then tool: edit', false],
   ['iteration 3', 'model.call, then tool: run tests', false],
   ['iterations 4 to 12', 'about 277,000 input tokens re-read', true],
  ].forEach((b, i) => {
    const y = 134 + i * 32;
    els.push(rect(508, y, 394, 26, {
      stroke: b[2] ? T.inkSubtle : T.border, fill: b[2] ? T.surface : T.neutral1,
      strokeWidth: 1, strokeStyle: b[2] ? 'dashed' : 'solid',
    }));
    els.push(text(520, y + 6, b[0], { size: 9.5, stroke: b[2] ? T.inkMuted : T.ink }));
    els.push(text(650, y + 7, fit(b[1], 8.5, 240, 'iteration detail'),
      { size: 8.5, family: b[2] ? 5 : MONO, stroke: T.inkMuted }));
  });
  els.push(text(508, 262, fit('about $0.83 a run at an illustrative $3 per million (Post 23)', 8.5, 394, 'run cost'),
    { size: 8.5, stroke: T.inkSubtle }));

  els.push(rect(508, 278, 394, 38, { stroke: T.success, fill: T.surface, strokeWidth: 1.6 }));
  els.push(text(522, 286, 'outcome check', { size: 11.5, stroke: T.success }));
  els.push(text(660, 288, 'tests pass? PR merged?', { size: 9.5, stroke: T.inkMuted }));

  els.push(rule(506, 902, 326));
  els.push(text(508, 332, 'WHAT THE RUN ALSO REPORTS', { size: 9, stroke: T.inkSubtle }));
  els.push(text(508, 348, fit('iterations to resolution, tokens per resolved task,', 9.5, 394, 'traj cols'),
    { size: 9.5, stroke: T.ink }));
  els.push(text(508, 364, fit('tool-call errors, redundant reads, gate fires, stop reason', 9.5, 394, 'traj cols'),
    { size: 9.5, stroke: T.ink }));
  els.push(text(508, 382, 'Expensive and stochastic, but honest: it scores the machine', { size: 9, stroke: T.inkMuted }));
  els.push(text(508, 396, 'rather than the sentence. One binary per run: resolved-rate.', { size: 9, stroke: T.inkMuted }));

  // --- the band: which eval the thing you touched actually calls for ------
  els.push(...card(40, 424, 880, 140, { spine: T.primary, strokeWidth: 1.4 }));
  els.push(text(58, 432, 'SOMETHING CHANGED, SO WHAT DO YOU RUN? THE UNIT FOLLOWS FROM THE THING YOU TOUCHED',
    { size: 10, stroke: T.inkSubtle }));
  const COLS = [[62, 190, 'WHAT YOU CHANGED'], [262, 250, 'WHICH EVAL'],
                [522, 200, 'THE UNIT'], [732, 170, 'WHEN IT RUNS']];
  COLS.forEach((c) => els.push(text(c[0], 452, c[2], { size: 8.5, stroke: T.inkSubtle })));
  els.push(rule(56, 904, 466));

  const ROWS = [
    ['Prompt wording', 'output eval (Context Engineering 20)', 'one completion', 'every commit'],
    ['A tool schema', 'a subset of the internal set', 'one run', 'every PR'],
    ['A harness component', 'an A/B with a per-task diff', 'the same task under both', 'every PR on the loop'],
    ['The model version', 'the frozen set as a regression gate', 'one run per task per seed', 'every model upgrade'],
    ['Nothing: live traffic', 'the production funnel', 'a merged unit of work', 'continuously'],
  ];
  ROWS.forEach((r, i) => {
    const y = 474 + i * 18;
    r.forEach((cell, j) => els.push(text(COLS[j][0], y, fit(cell, 9.5, COLS[j][1], 'table cell'),
      { size: 9.5, stroke: j === 0 ? T.ink : T.inkMuted })));
  });

  els.push(text(40, 580, 'A good output is not a resolved task: harness quality lives on the right, over a fixed task set.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 602, 'Read the table top to bottom and the cost rises, the feedback slows, and the authority of the answer increases.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'An output eval on one completion beside a trajectory eval on a whole run',
    desc: 'A hand-drawn comparison in two panels above a decision table. On the left, an output '
      + 'eval per completion, the Context Engineering lens of one answer in and one score out: a '
      + 'prompt holding one task in one fixed wording sampled once with no tools and no '
      + 'environment; an output holding one completion, the final message only and nothing about '
      + 'how the model got there; and a judge returning one number per completion, a score from '
      + 'zero to one, comparable across every prompt edit. Its graders are exact match, regular '
      + 'expression, rubric and model judge, and what one score cannot see is the recovery, the '
      + 'loop, the tool errors and the stop. It is cheap, deterministic and repeatable, the right '
      + 'tool for tuning a prompt, and it runs on every commit. On the right, a trajectory and '
      + 'outcome eval per run: three iterations, each pairing a model call with a tool call for '
      + 'bash, an edit and a test run, then a dashed row for iterations four to twelve, which '
      + 're-read about two hundred and seventy-seven thousand input tokens, roughly eighty-three '
      + 'cents a run at an illustrative three dollars per million. An outcome check then asks '
      + 'whether the tests pass and the pull request merged. The run also reports iterations to '
      + 'resolution, tokens per resolved task, tool-call errors, redundant reads, gate fires and '
      + 'stop reason. It is expensive and stochastic but honest, because it scores the machine '
      + 'rather than the sentence and yields one binary per run: resolved-rate. Below, a table '
      + 'maps what changed to which eval, its unit, and when it runs: prompt wording to an output '
      + 'eval on one completion every commit; a tool schema to a subset of the internal set on one '
      + 'run every pull request; a harness component to an A/B with a per-task diff on the same '
      + 'task under both configurations, on every pull request that touches the loop; the model '
      + 'version to the frozen set as a regression gate, one run per task per seed, on every model '
      + 'upgrade; and nothing but live traffic to the production funnel on a merged unit of work, '
      + 'continuously. Captions record that a good output is not a resolved task, and that reading '
      + 'the table downward the cost rises, the feedback slows, and the authority of the answer '
      + 'increases.',
  };
}

// ---------------------------------------------------------------- diagram 2
function abPipeline() {
  resetSeq();
  const W = 960, H = 560;

  const els = [...heading('A/B a whole harness on one fixed task set',
    'Change one component, hold the model fixed, run identical tasks, and compare resolved-rate against cost.')];

  els.push(rect(40, 80, 880, 24, { stroke: T.inkSubtle, fill: T.neutral1, strokeWidth: 1.1 }));
  els.push(text(40, 86, 'the model is held fixed across both branches: only the harness differs',
    { size: 9, align: 'center', width: 880, stroke: T.inkMuted }));

  // --- the fixed set, sized and costed ------------------------------------
  els.push(...card(40, 132, 236, 180, { spine: T.primary, strokeWidth: 1.5 }));
  els.push(text(58, 142, 'TASK SET', { size: 13, stroke: T.ink }));
  els.push(rule(56, 262, 166));
  ['60 tasks, frozen and versioned', '3 seeds per task, per config', 'objective graders only']
    .forEach((l, i) => els.push(text(58, 174 + i * 18, fit(l, 9.5, 204, 'task set fact'),
      { size: 9.5, stroke: T.inkMuted })));
  els.push(rule(56, 262, 226));
  ['360 runs in a full sweep', 'about 72 min at 20-way', 'about $300 of model spend']
    .forEach((l, i) => els.push(text(58, 234 + i * 18, fit(l, 9.5, 204, 'sweep fact'),
      { size: 9.5, stroke: T.ink })));
  els.push(text(58, 288, 'illustrative constants, Post 23', { size: 8.5, stroke: T.inkSubtle }));

  const ARMS = [
    [130, 173, 'Harness A', 'config: no verify gate', T.neutral3,
      ['won 4 tasks outright', 'lost 8 to B', 'the rest tied']],
    [226, 269, 'Harness B', 'config: with a verify gate', T.success,
      ['won 8 tasks outright', 'lost 4 to A', 'the rest tied']],
  ];
  ARMS.forEach((a) => {
    els.push(...card(300, a[0], 250, 86, { spine: a[4], strokeWidth: 1.4 }));
    els.push(text(318, a[0] + 10, a[2], { size: 13, stroke: T.ink }));
    els.push(text(318, a[0] + 34, fit(a[3], 9.5, 214, 'arm config'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(318, a[0] + 54, 'same tasks, same model, same seeds', { size: 9, stroke: T.inkSubtle }));
    els.push(arrow([[278, 222], [296, a[1]]], { stroke: T.inkMuted, strokeWidth: 1.2 }));
    els.push(...card(580, a[0], 190, 86, { spine: a[4], strokeWidth: 1.3 }));
    a[5].forEach((l, i) => els.push(text(598, a[0] + 12 + i * 22, l, { size: 10, stroke: T.ink })));
    els.push(arrow([[552, a[1]], [576, a[1]]], { stroke: T.inkMuted, strokeWidth: 1.2 }));
    els.push(arrow([[772, a[1]], [806, 221]], { stroke: T.inkMuted, strokeWidth: 1.2 }));
  });

  els.push(...card(810, 150, 110, 142, { spine: T.success, strokeWidth: 1.6 }));
  els.push(text(824, 160, 'COMPARE', { size: 11, stroke: T.success }));
  ['net 4 tasks', 'a 6.7-point lift', 'p = 0.39'].forEach((l, i) => {
    els.push(text(824, 186 + i * 22, l, { size: 10, stroke: T.ink }));
  });
  els.push(text(824, 258, 'not yet a', { size: 8.5, stroke: T.inkMuted }));
  els.push(text(824, 270, 'verdict', { size: 8.5, stroke: T.inkMuted }));

  // --- second tier: could the difference have been a coin flip? -----------
  els.push(text(40, 338, 'AND BEFORE THE VERDICT: IS THE DIFFERENCE REAL? A WORKED CASE ON A 60-TASK SET',
    { size: 10, stroke: T.inkSubtle }));

  const CASES = [
    [40, T.alert, 'B wins 8 tasks, A wins 4', '12 discordant pairs, a net of 4 tasks: a 6.7-point lift',
      'sign test  p = 0.39', 'a fair coin lands this lopsided two times in five'],
    [496, T.success, 'B wins 10 tasks, A wins 2', 'the same 12 discordant pairs, split differently',
      'sign test  p = 0.039', 'the same headline lift, and evidence behind it'],
  ];
  CASES.forEach((c) => {
    els.push(...card(c[0], 358, 424, 94, { spine: c[1], strokeWidth: 1.4 }));
    els.push(text(c[0] + 18, 368, fit(c[2], 12, 388, 'case head'), { size: 12, stroke: T.ink }));
    els.push(text(c[0] + 18, 390, fit(c[3], 9, 388, 'case gloss'), { size: 9, stroke: T.inkMuted }));
    els.push(text(c[0] + 18, 408, fit(c[4], 11.5, 388, 'case verdict'), { size: 11.5, stroke: c[1] }));
    els.push(text(c[0] + 18, 430, fit(c[5], 9, 388, 'case note'), { size: 9, stroke: T.inkMuted }));
  });
  els.push(text(40, 464, fit('Ties carry no direction and drop out. Unpaired on 50 tasks near 50%, the 95% interval on the difference is about 20 points either way: pair by construction.',
    9.5, 880, 'pairing note'), { size: 9.5, stroke: T.inkMuted }));

  els.push(text(40, 492, 'One controlled variable, and the lift is not yet the verdict: 8 to 4 on twelve discordant pairs is a coin flip two times in five.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 514, 'Read the per-task win and loss list too: a better mean can hide five tasks fixed and three broken.',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 536, 'The same machinery runs in reverse: hold the harness fixed and change the model, as a regression gate on every upgrade.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Two harness configurations run over one fixed task set, compared and then significance-tested',
    desc: 'A hand-drawn pipeline above a significance test, with illustrative numbers. A banner '
      + 'records that the model is held fixed across both branches and only the harness differs. On '
      + 'the left, a task set card: sixty tasks, frozen and versioned, three seeds per task per '
      + 'config, objective graders only, which comes to three hundred and sixty runs in a full '
      + 'sweep, about seventy-two minutes at twenty-way parallelism and about three hundred dollars '
      + 'of model spend, on illustrative constants from post 23. It feeds two branches. Harness A '
      + 'is configured without a verify gate and wins four tasks outright, losing eight to B. '
      + 'Harness B is configured with a verify gate and wins eight tasks outright, losing four to '
      + 'A, and the rest tie. Both feed a compare box, which records a net of four tasks, a six '
      + 'point seven point lift and a sign-test p-value of nought point three nine, and calls that '
      + 'not yet a verdict. A second tier works the same case through over a '
      + 'sixty-task set. On the left, B wins eight tasks and A wins four: twelve discordant pairs, '
      + 'a net of four tasks and a six point seven point lift, on which the sign test returns a '
      + 'p-value of nought point three nine, because a fair coin lands this lopsided two times in '
      + 'five. On the right, the same twelve discordant pairs split ten to two return a p-value of '
      + 'nought point nought three nine: the same headline lift with evidence behind it. A note '
      + 'records that ties carry no direction and drop out, and that two configs run unpaired on '
      + 'fifty tasks near fifty percent leave a ninety-five percent interval on the difference of '
      + 'about twenty points either way, so comparisons should be paired by construction. Captions '
      + 'record that this is one controlled variable and one verdict, that the per-task win and '
      + 'loss list should be read too because a better mean can hide five tasks fixed and three '
      + 'broken, and that the same machinery runs in reverse by holding the harness fixed and '
      + 'changing the model, as a regression gate on every upgrade.',
  };
}

// ---------------------------------------------------------------- diagram 3
function productionFunnel() {
  resetSeq();
  const W = 960, H = 622;

  const els = [...heading('The production funnel, once the harness is live',
    'Benchmarks and internal evals are proxies you run before shipping. These are outcomes, with money attached.')];

  const STAGES = [
    [40, 520, 100, T.primary, 'RUNS THE AGENT ATTEMPTED', 'everything it was asked to do',
      'one week: A 200 runs, B 200 runs',
      'First-pass success rate', 'the fraction a human accepted with no', 'rework: the resolved-rate of section 3, live',
      'A 59%     B 66%'],
    [100, 400, 190, T.warn, 'RESULTS A HUMAN ACCEPTED', 'the work that looked right at the time',
      'one week: A 118 accepted, B 132',
      'Defect-escape rate', 'of those, the fraction later reverted,', 'reopened, or caught downstream',
      'A 7.6%     B 10.6%'],
    [160, 280, 280, T.success, 'WORK THAT ACTUALLY SHIPPED', 'merged, deployed, and still standing',
      'one week: A 109 shipped, B 118',
      'Dollars per merged PR', 'tokens, retries and human review,', 'divided by the units that shipped',
      'A $49     B $54'],
  ];
  STAGES.forEach((s, i) => {
    els.push(rect(s[0], s[2], s[1], 76, { stroke: s[3], fill: T.surface, strokeWidth: 1.6 }));
    els.push(text(s[0] + 20, s[2] + 11, fit(s[4], 12.5, s[1] - 40, 'stage name'), { size: 12.5, stroke: T.ink }));
    els.push(text(s[0] + 20, s[2] + 33, fit(s[5], 9.5, s[1] - 40, 'stage gloss'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(s[0] + 20, s[2] + 52, fit(s[6], 9.5, s[1] - 40, 'stage count'), { size: 9.5, stroke: s[3] }));
    if (i) els.push(arrow([[300, s[2] - 12], [300, s[2] - 2]], { stroke: T.inkMuted, strokeWidth: 1.3 }));

    els.push(arrow([[s[0] + s[1] + 2, s[2] + 38], [596, s[2] + 38]], { stroke: s[3], strokeWidth: 1.2 }));
    els.push(...card(600, s[2], 320, 76, { spine: s[3], strokeWidth: 1.4 }));
    els.push(text(618, s[2] + 8, s[7], { size: 12, stroke: T.ink }));
    els.push(text(618, s[2] + 28, fit(s[8], 9, 284, 'metric gloss'), { size: 9, stroke: T.inkMuted }));
    els.push(text(618, s[2] + 42, fit(s[9], 9, 284, 'metric gloss'), { size: 9, stroke: T.inkMuted }));
    els.push(text(618, s[2] + 58, fit(s[10], 10.5, 284, 'metric value'), { size: 10.5, stroke: s[3] }));
  });

  // --- the ledger under the funnel ---------------------------------------
  els.push(text(40, 376, 'THE LEDGER UNDERNEATH, THE SAME WEEK, ALL FIGURES ILLUSTRATIVE, REVIEW AT A LOADED $120 AN HOUR',
    { size: 10, stroke: T.inkSubtle }));

  const LEDGER = [
    [40, T.neutral3, 'HARNESS A', [['model spend, 200 runs', '$170'], ['human review and rework', '$5,170'],
      ['reverts to redo', '9']], 'at $0.85 a run, 15 min a review'],
    [336, T.success, 'HARNESS B, heavier verification', [['model spend, 200 runs', '$510'],
      ['human review and rework', '$5,900'], ['reverts to redo', '14']], 'at $2.55 a run, 45 min a redo'],
  ];
  LEDGER.forEach((c) => {
    els.push(...card(c[0], 396, 288, 112, { spine: c[1], strokeWidth: 1.4 }));
    els.push(text(c[0] + 18, 406, fit(c[2], 11.5, 252, 'ledger head'), { size: 11.5, stroke: T.ink }));
    els.push(rule(c[0] + 16, c[0] + 272, 424));
    c[3].forEach((r, i) => {
      const y = 430 + i * 19;
      els.push(text(c[0] + 18, y, fit(r[0], 9.5, 160, 'ledger label'), { size: 9.5, stroke: T.inkMuted }));
      els.push(text(c[0] + 172, y, r[1], { size: 9.5, align: 'right', width: 100, stroke: T.ink }));
    });
    els.push(text(c[0] + 18, 489, c[4], { size: 8.5, stroke: T.inkSubtle }));
  });

  els.push(...card(632, 396, 288, 112, { spine: T.accent, strokeWidth: 1.6 }));
  els.push(text(650, 406, 'DOLLARS PER MERGED PR', { size: 11, stroke: T.accent }));
  els.push(rule(648, 904, 424));
  [['A', '$49'], ['B', '$54']].forEach((r, i) => {
    els.push(text(650, 434 + i * 26, r[0], { size: 13, stroke: T.ink }));
    els.push(text(700, 434 + i * 26, r[1], { size: 13, stroke: T.ink }));
  });
  els.push(text(650, 489, fit('B wins the eval, loses the ledger by 11%', 9, 252, 'verdict note'),
    { size: 9, stroke: T.inkMuted }));

  els.push(text(40, 526, 'A production outcome outranks an internal eval, which outranks a public benchmark.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 548, 'Seven points of first-pass rate lost the ledger: the heavier loop tripled the model spend, and five more reverts ate the saving.',
    { size: 11, stroke: T.inkMuted }));
  els.push(text(40, 570, 'A high first-pass rate with a high escape rate is plausible work that does not hold, which is worse than an honest failure.',
    { size: 11, stroke: T.inkMuted }));
  els.push(text(40, 592, 'And when the A/B and the funnel disagree, the funnel wins: the disagreement is the size of the drift in your eval set.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Three narrowing production stages with their metrics, and the week they cost',
    desc: 'A hand-drawn funnel of three narrowing stages, each paired with its metric and priced '
      + 'over one illustrative week. The widest stage is the runs the agent attempted, meaning '
      + 'everything it was asked to do, two hundred runs under each of harness A and harness B; its '
      + 'metric is first-pass success rate, the fraction a human accepted with no rework, which is '
      + 'the internal resolved-rate measured live, at fifty-nine percent for A against sixty-six '
      + 'for B. The middle stage is the results a human accepted, the work that looked right at the '
      + 'time, one hundred and eighteen for A against one hundred and thirty-two for B; its metric '
      + 'is defect-escape rate, the fraction of those later reverted, reopened, or caught '
      + 'downstream, at seven point six percent for A against ten point six for B. The narrowest '
      + 'stage is the work that actually shipped, merged and deployed and still standing, one '
      + 'hundred and nine for A against one hundred and eighteen for B; its metric is dollars per '
      + 'merged pull request, meaning tokens, retries and human review divided by the units that '
      + 'shipped, at forty-nine dollars for A against fifty-four for B. Beneath the funnel a ledger '
      + 'for the same week, with review priced at a loaded hundred and twenty dollars an hour, '
      + 'gives harness A a hundred and seventy dollars of model spend over two hundred runs, five '
      + 'thousand one hundred and seventy dollars of human review and rework, and nine reverts to '
      + 'redo; and harness B five hundred and ten dollars of model spend, five thousand nine '
      + 'hundred dollars of review and rework, and fourteen reverts. The verdict card sets forty-'
      + 'nine dollars per merged pull request against fifty-four, because B wins the eval and loses '
      + 'the ledger by about eleven percent. Captions record that a production outcome outranks an '
      + 'internal eval which outranks a public benchmark, that seven points of first-pass rate lost '
      + 'the ledger because the heavier loop tripled the model spend and five more reverts ate the '
      + 'saving, that a high first-pass rate with a high escape rate is plausible work that does '
      + 'not hold and is worse than an honest failure, and that when the A/B and the funnel '
      + 'disagree the funnel wins, because the disagreement is the size of the drift in your eval '
      + 'set.',
  };
}

module.exports = { outputVsTrajectory, abPipeline, productionFunnel };

if (require.main === module) {
  emit('01-output-vs-trajectory', outputVsTrajectory());
  emit('02-harness-ab-pipeline', abPipeline());
  emit('03-production-funnel', productionFunnel());
}
