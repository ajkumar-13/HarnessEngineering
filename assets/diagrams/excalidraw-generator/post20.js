// The post 20 diagrams, hand-drawn.
//
//   01-sdk-feature-matrix  960 x 620  Mirror of the existing figure, densified.
//   02-build-vs-buy        960 x 612  Mirror, densified.
//   03-harness-ab          960 x 636  NEW, published: section 4 had no figure.
//
// The post opens with a feature matrix and then spends a section explaining why
// a feature matrix is the wrong instrument. The A/B it recommends instead had
// nothing to show it with, which left the sketch as the only picture in a post
// arguing that sketches lose to evidence.
//
// Figures 1 and 2 originally drew only their headline shape -- a grid of three
// repeated phrases, and a five-box tree -- and left half of each canvas empty.
// Both now carry the material the post already has and the figure was missing:
// the primitive vocabulary of section 3, the corrections section 3 makes to the
// matrix, the observable signals of section 6, and the measured line counts of
// this series own two builds. Every number in them is read from the post or
// from code/24-minimal-harness and code/25-harness-plus; none is estimated.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function featureMatrix() {
  resetSeq();
  const W = 960, H = 620;

  const els = [...heading('What an SDK gives you (illustrative)',
    'A sketch of the shape, not a live spec sheet. These tools move fast, and the matrix ages faster than they do.')];

  const CW = 150;
  const CX = (j) => 300 + j * 156;

  // Column heads name the concrete product on top and the shape underneath, so
  // the matrix and the section 3 translation table read as the same thing.
  const COLS = [
    ['Claude Agent SDK', 'batteries-included SDK', T.success],
    ['OpenAI Agents SDK', 'code-first framework', T.primary],
    ['LangGraph', 'graph framework', T.warn],
    ['Roll your own', 'Posts 24 to 26', T.neutral3],
  ];
  // Row, the post that covers that component, and the four marks.
  const ROWS = [
    ['The agent loop', 'Post 03', [2, 2, 1, 0]],
    ['Tools and MCP', 'Post 07', [2, 2, 1, 0]],
    ['Context management', 'Post 09', [2, 1, 1, 0]],
    ['Hooks and permissions', 'Posts 13 to 15', [2, 1, 1, 0]],
    ['Sub-agents', 'Post 16', [2, 1, 1, 0]],
    ['Observability', 'Post 21', [1, 1, 1, 0]],
  ];
  const MARK = [
    ['you build it', T.neutral2],
    ['partial: you wire it', T.warn],
    ['built-in', T.success],
  ];

  COLS.forEach((c, j) => {
    els.push(text(CX(j), 82, fit(c[0], 10, CW, 'col name'),
      { size: 10, align: 'center', width: CW, stroke: T.ink }));
    els.push(text(CX(j), 98, fit(c[1], 8.5, CW, 'col shape'),
      { size: 8.5, align: 'center', width: CW, stroke: T.inkSubtle }));
  });

  ROWS.forEach((r, i) => {
    const y = 116 + i * 40;
    els.push(text(40, y + 1, fit(r[0], 11.5, 250, 'row label'), { size: 11.5, stroke: T.ink }));
    els.push(text(40, y + 19, r[1], { size: 8.5, stroke: T.inkSubtle }));
    els.push(rule(40, 920, y + 34));
    r[2].forEach((v, j) => {
      els.push(rect(CX(j), y + 3, CW, 25,
        { stroke: T.ink, fill: MARK[v][1], strokeWidth: 1.1 }));
      els.push(text(CX(j), y + 10, MARK[v][0],
        { size: 8.5, align: 'center', width: CW, stroke: T.onAccent }));
    });
  });

  // --- the vocabulary strip -------------------------------------------------
  // Three repeated phrases say nothing about what you would actually type. The
  // primitives from the section 3 table do, and the last column is priced in
  // lines rather than named, because it is the only column with a real number.
  els.push(text(40, 364, 'ITS OWN VOCABULARY', { size: 9, stroke: T.inkSubtle }));
  els.push(text(40, 384, 'The same map, four dialects.', { size: 10.5, stroke: T.ink }));
  els.push(text(40, 402, 'The last column is priced in', { size: 10.5, stroke: T.inkMuted }));
  els.push(text(40, 418, 'lines instead (section 6).', { size: 10.5, stroke: T.inkMuted }));

  const VOCAB = [
    ['hooks: PreToolUse,', 'PostToolUse, PreCompact', 'four permission modes',
      'MCP servers, sub-agents,', 'automatic compaction', 'a six-step resolution',
      'order for permissions'],
    ['agents and handoffs', 'guardrails, run beside', 'the turn rather than',
      'inside it', 'sessions', 'built-in tracing'],
    ['a typed state graph', 'checkpointers, saving', 'state at every step',
      'interrupt() and resume', 'time travel across', 'saved checkpoints'],
    ['Build #1 (Post 24):', '520 impl + 138 test,', 'a 10-test suite',
      'Build #2 (Post 25):', '728 + 233, 13 tests', 'union: about 800 impl,',
      'past 1,500 with MCP'],
  ];
  VOCAB.forEach((lines, j) => {
    els.push(...card(CX(j), 360, CW, 96, { spine: COLS[j][2], strokeWidth: 1.2 }));
    lines.forEach((l, k) => {
      els.push(text(CX(j) + 16, 367 + k * 11.5, fit(l, 8.5, CW - 24, 'vocab line'),
        { size: 8.5, stroke: j === 3 ? T.ink : T.inkMuted }));
    });
  });

  // --- what the matrix cannot show -----------------------------------------
  els.push(...card(40, 468, 440, 100, { spine: T.alert, strokeWidth: 1.4 }));
  els.push(text(58, 476, 'THE ROW THIS MATRIX IS MISSING', { size: 9.5, stroke: T.alert }));
  ['Durable state and resumability. A checkpointer makes every step',
   'of a run recoverable, so a process restart resumes rather than',
   'starts over: the one axis where a graph framework wins outright.'].forEach((l, i) => {
    els.push(text(58, 498 + i * 17, fit(l, 9.5, 404, 'missing row'),
      { size: 9.5, stroke: T.ink }));
  });

  els.push(...card(490, 468, 430, 100, { spine: T.primary, strokeWidth: 1.4 }));
  els.push(text(508, 476, 'THE CELL THIS MATRIX IS HARSH ON', { size: 9.5, stroke: T.primary }));
  ['Hooks and permissions, for the graph framework: interrupt() is',
   'a first-class approval primitive, which is the mechanism of Post',
   '15. Read the sketch, then read section 3 for both corrections.'].forEach((l, i) => {
    els.push(text(508, 498 + i * 17, fit(l, 9.5, 394, 'harsh cell'),
      { size: 9.5, stroke: T.ink }));
  });

  els.push(text(40, 580, 'An SDK does not remove harness engineering. It removes the plumbing of harness engineering and leaves you the custom layer.',
    { size: 11, stroke: T.ink }));
  els.push(text(40, 602, '"Just use an SDK" and "harness engineering is dead" are different claims, and only the first one is true.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Six harness components against four ways of getting them, with each option primitives and the two corrections the matrix needs',
    desc: 'A hand-drawn feature matrix, marked as illustrative rather than a live spec sheet. Six '
      + 'harness components run down the side, each carrying the post that covers it: the agent '
      + 'loop, Post 03; tools and MCP, Post 07; context management, Post 09; hooks and permissions, '
      + 'Posts 13 to 15; sub-agents, Post 16; and observability, Post 21. Four options run across '
      + 'the top: the Claude Agent SDK as a batteries-included SDK, the OpenAI Agents SDK as a '
      + 'code-first framework, LangGraph as a graph framework, and rolling your own across Posts 24 '
      + 'to 26. Each cell is marked built-in, partial where you wire it yourself, or you build it. '
      + 'The batteries-included column is built-in everywhere except observability, the code-first '
      + 'column is built-in for the loop and for tools and partial below that, the graph framework '
      + 'column is partial throughout, and the roll-your-own column is entirely you build it. A '
      + 'strip beneath the matrix gives each column its own vocabulary: hooks on PreToolUse, '
      + 'PostToolUse and PreCompact, four permission modes, MCP servers, sub-agents, automatic '
      + 'compaction and a six-step permission resolution order for the first; agents, handoffs, '
      + 'guardrails that run beside the turn rather than inside it, sessions and built-in tracing '
      + 'for the second; a typed state graph, checkpointers saving state at every step, interrupt '
      + 'and resume, and time travel across saved checkpoints for the third. The last column is '
      + 'priced in lines instead, from this series own builds: Build #1 in Post 24 is 520 '
      + 'implementation lines and 138 test lines across a 10-test suite, Build #2 in Post 25 is 728 '
      + 'and 233 across a 13-test suite, their union is about 800 implementation lines, and adding '
      + 'compaction, retries and MCP puts it past 1,500. Two panels record what the matrix cannot '
      + 'show. The missing row is durable state and resumability, where a checkpointer makes every '
      + 'step of a run recoverable so a process restart resumes rather than starts over, the one '
      + 'axis where a graph framework wins outright. The harsh cell is hooks and permissions for '
      + 'the graph framework, because interrupt is a first-class approval primitive and the '
      + 'mechanism of Post 15. Captions record that an SDK does not remove harness engineering but '
      + 'removes its plumbing and leaves you the custom layer, and that "just use an SDK" and '
      + '"harness engineering is dead" are different claims of which only the first is true.',
  };
}

// ---------------------------------------------------------------- diagram 2
function buildVsBuy() {
  resetSeq();
  const W = 960, H = 612;

  const els = [...heading('Build versus buy',
    'Default to an SDK; earn your way to rolling your own, and price the build before you choose it.')];

  // --- the price of the last branch, in the corner the tree left empty ------
  // The one branch of this tree whose cost this series can quote rather than
  // estimate, because it built it twice and counted the lines.
  els.push(...card(40, 84, 250, 148, { spine: T.warn, strokeWidth: 1.4 }));
  els.push(text(58, 88, 'PRICE THE BUILD FIRST', { size: 9.5, stroke: T.warn }));
  [[102, 'Build #1 (Post 24): 520 impl lines,', 1],
   [113, '138 test lines, a 10-test suite', 0],
   [128, 'Build #2 (Post 25): 728 impl lines,', 1],
   [139, '233 test lines, a 13-test suite', 0],
   [154, 'Union, not sum: about 800 impl lines,', 1],
   [165, 'plus about 250 more of tests', 0],
   [180, 'Add compaction, retries, MCP and a', 1],
   [191, 'permission order: past 1,500 lines.', 1],
   [206, 'And both builds shipped defects their', 1],
   [217, 'own passing tests could not see.', 0]].forEach((l) => {
    els.push(text(58, l[0], fit(l[1], 8.5, 218, 'price line'),
      { size: 8.5, stroke: l[2] ? T.ink : T.inkMuted }));
  });

  // --- a shape the tree does not branch on ---------------------------------
  els.push(...card(700, 76, 220, 66, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(716, 82, 'A SHAPE THE TREE SKIPS', { size: 8.5, stroke: T.accent }));
  ['An open harness engine you embed',
   '(Codex, Apache-2.0): fork the loop,',
   'sandbox, approvals; rent the tokens.'].forEach((l, i) => {
    els.push(text(716, 98 + i * 11, fit(l, 8.5, 192, 'skip note'),
      { size: 8.5, stroke: T.inkMuted }));
  });

  // --- the tree ------------------------------------------------------------
  els.push(rect(380, 88, 200, 40, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.4 }));
  els.push(text(380, 100, 'Need an agent harness', { size: 11, align: 'center', width: 200, stroke: T.ink }));
  els.push(arrow([[480, 130], [480, 146]], { stroke: T.inkMuted, strokeWidth: 1.3 }));

  const GATES = [
    [148, 'Targeting one model ecosystem?', 'its native SDK is the best co-trained (Post 04)'],
    [244, 'Need unusual or explicit control flow?', 'custom graphs, research, or portability'],
  ];
  GATES.forEach((g) => {
    els.push(rect(300, g[0], 360, 64, { stroke: T.primary, fill: T.surface, strokeWidth: 1.5 }));
    els.push(text(300, g[0] + 14, g[1], { size: 12, align: 'center', width: 360, stroke: T.ink }));
    els.push(text(300, g[0] + 38, g[2], { size: 9, align: 'center', width: 360, stroke: T.inkMuted }));
  });
  els.push(arrow([[480, 214], [480, 240]], { stroke: T.alert, strokeWidth: 1.3 }));
  els.push(text(488, 216, 'no', { size: 9.5, stroke: T.alert }));

  els.push(arrow([[662, 180], [696, 180]], { stroke: T.success, strokeWidth: 1.3 }));
  els.push(text(666, 156, 'yes', { size: 9.5, stroke: T.success }));
  els.push(arrow([[662, 276], [676, 276]], { stroke: T.success, strokeWidth: 1.3 }));
  els.push(text(664, 252, 'yes', { size: 9.5, stroke: T.success }));
  els.push(arrow([[298, 276], [284, 276]], { stroke: T.alert, strokeWidth: 1.3 }));
  els.push(text(284, 252, 'no', { size: 9.5, stroke: T.alert }));

  const ENDS = [
    [700, 148, 220, 'The native SDK for it', 'best inside its own harness', T.primary],
    [680, 244, 240, 'Graph framework, or your own', 'LangGraph, or Posts 24 to 26', T.warn],
    [40, 244, 240, 'Batteries-included SDK', 'the default for most systems', T.success],
  ];
  ENDS.forEach((e) => {
    els.push(...card(e[0], e[1], e[2], 64, { spine: e[5], strokeWidth: 1.6 }));
    els.push(text(e[0] + 16, e[1] + 10, fit(e[3], 12, e[2] - 32, 'end name'), { size: 12, stroke: T.ink }));
    els.push(text(e[0] + 16, e[1] + 32, fit(e[4], 9, e[2] - 32, 'end gloss'), { size: 9, stroke: T.inkMuted }));
  });

  // --- the signals that answer the gates -----------------------------------
  // A tree branches on questions, and a question like "do you need unusual
  // control flow?" is answered by taste unless you can point at something.
  els.push(text(40, 326, 'REPLACE EACH BRANCH WITH A SIGNAL YOU CAN OBSERVE TODAY (SECTION 6)',
    { size: 9.5, stroke: T.inkSubtle }));
  els.push(text(40, 346, 'THE SIGNAL', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(480, 346, 'THE SHAPE IT POINTS AT', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(710, 346, 'WHAT IT COSTS YOU', { size: 8.5, stroke: T.inkSubtle }));
  els.push(rule(40, 920, 360));

  const SIGNALS = [
    [['One model in production, and no concrete plan to switch'],
      'that model native SDK', T.primary,
      ['portability, and a rewrite', 'if the plan ever changes']],
    [['Branch logic you have already written that the SDK loop keeps',
      'fighting, or runs that must survive a process restart'],
      'a graph framework', T.warn,
      ['the batteries: compaction,', 'permissions, sandboxing']],
    [['You need the vendor loop and sandbox, but your own product',
      'surface around it'],
      'an open harness engine you embed', T.accent,
      ['the integration work, and', 'the model access is rented']],
    [['You cannot name the SDK feature you would be giving up'],
      'a batteries-included SDK, not a build', T.success,
      ['nothing: this is the cheap', 'answer, and the common one']],
    [['A requirement no shipped harness expresses, which you can',
      'state in one sentence'],
      'roll your own', T.neutral2,
      ['everything in the panel', 'above, plus its maintenance']],
  ];
  SIGNALS.forEach((s, i) => {
    const y = 368 + i * 38;
    s[0].forEach((l, k) => els.push(text(40, y + k * 14, fit(l, 9.5, 430, 'signal'),
      { size: 9.5, stroke: T.ink })));
    els.push(rect(480, y - 3, 210, 22, { stroke: T.ink, fill: s[2], strokeWidth: 1.1 }));
    els.push(text(480, y + 2, fit(s[1], 8.5, 210, 'shape pill'),
      { size: 8.5, align: 'center', width: 210, stroke: T.onAccent }));
    s[3].forEach((l, k) => els.push(text(710, y + k * 13, fit(l, 9, 210, 'cost'),
      { size: 9, stroke: T.inkMuted })));
    if (i < 4) els.push(rule(40, 920, y + 31));
  });

  els.push(text(40, 562, 'You still engineer the custom layer whichever you pick; the SDK is only the prebuilt half (Post 02).',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 584, 'Build from scratch to understand what an SDK does. That is what Posts 24 to 26 are for, not a reason to ship what they build.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Two gates between needing a harness and choosing how to get one, the build priced in lines, and the signal that answers each gate',
    desc: 'A hand-drawn decision tree with a price panel beside it and a table of signals below. '
      + 'From needing an agent harness, the first gate asks whether you are targeting one model '
      + 'ecosystem, noting that its native SDK is the best co-trained option; a yes leads to the '
      + 'native SDK for that model, which is best inside its own harness. A no leads to a second '
      + 'gate asking whether you need unusual or explicit control flow, such as custom graphs, '
      + 'research work, or portability; a yes leads to a graph framework or rolling your own, and a '
      + 'no leads to a batteries-included SDK, the default for most systems. A panel on the left '
      + 'prices the build from this series own companions: Build #1 in Post 24 is 520 '
      + 'implementation lines and 138 test lines across a 10-test suite; Build #2 in Post 25 is 728 '
      + 'implementation lines and 233 test lines across a 13-test suite; taking their union rather '
      + 'than their sum gives about 800 implementation lines plus about 250 more of tests; and '
      + 'adding compaction, retries, MCP and a permission resolution order puts it past 1,500 '
      + 'lines. The panel closes by recording that both builds shipped defects their own passing '
      + 'tests could not see. A note on the right records a shape the tree does not branch on, an open harness '
      + 'engine you embed such as Codex under Apache-2.0, where you fork the loop, sandbox and '
      + 'approvals but still rent the tokens. Below, a table replaces each branch with a signal you '
      + 'can observe today, the shape it points at as a coloured pill, and what that shape costs. '
      + 'One model in production with no concrete plan to switch points at that model native SDK, '
      + 'costing portability and a rewrite. Branch logic the SDK loop keeps fighting, or runs that '
      + 'must survive a process restart, points at a graph framework, costing the batteries: '
      + 'compaction, permissions and sandboxing. Needing the vendor loop and sandbox under your own '
      + 'product surface points at an open harness engine, costing the integration work while the '
      + 'model access is still rented. Being unable to name the SDK feature you would give up '
      + 'points at a batteries-included SDK rather than a build, and costs nothing. A requirement '
      + 'no shipped harness expresses, statable in one sentence, points at rolling your own, and '
      + 'costs everything in the price panel plus its maintenance. Captions record that you still '
      + 'engineer the custom layer whichever you pick, and that building from scratch is how you '
      + 'understand what an SDK does rather than a reason to ship what you built.',
  };
}

// ---------------------------------------------------------------- diagram 3
function harnessAB() {
  resetSeq();
  const W = 960, H = 636;

  const els = [...heading('Settle it by measuring, not by arguing',
    'Hold the model and the task set fixed, swap the harness, read four numbers -- then ask whether the gap you found is real.')];

  els.push(text(40, 92, 'HELD FIXED', { size: 9, stroke: T.inkSubtle }));
  els.push(...card(40, 106, 220, 64, { spine: T.neutral3, strokeWidth: 1.4 }));
  els.push(text(58, 118, 'THE MODEL', { size: 12, stroke: T.ink }));
  els.push(text(58, 140, 'the same one on both arms', { size: 9, stroke: T.inkMuted }));

  els.push(...card(40, 182, 220, 114, { spine: T.neutral3, strokeWidth: 1.4 }));
  els.push(text(58, 194, 'THE TASK SET', { size: 12, stroke: T.ink }));
  ['twenty representative jobs', 'from your own backlog, not', 'from a public benchmark',
   'five seeds each: 100 runs per arm']
    .forEach((l, i) => els.push(text(58, 216 + i * 14, fit(l, 9, 190, 'task set'),
      { size: 9, stroke: i === 3 ? T.ink : T.inkMuted })));

  els.push(text(300, 92, 'VARIED: THE ONLY THING THAT CHANGES', { size: 9, stroke: T.inkSubtle }));
  els.push(...card(300, 106, 260, 84, { spine: T.primary, strokeWidth: 1.6 }));
  els.push(text(318, 120, 'HARNESS A', { size: 14, stroke: T.primary }));
  els.push(text(318, 144, 'what you run today', { size: 9.5, stroke: T.inkMuted }));
  els.push(text(318, 164, '61 of 100 resolved, $0.42 a run', { size: 10, stroke: T.ink }));
  els.push(...card(300, 206, 260, 84, { spine: T.accent, strokeWidth: 1.6 }));
  els.push(text(318, 220, 'HARNESS B', { size: 14, stroke: T.accent }));
  els.push(text(318, 244, 'the one you are considering', { size: 9.5, stroke: T.inkMuted }));
  els.push(text(318, 264, '68 of 100 resolved, $0.61 a run', { size: 10, stroke: T.ink }));

  els.push(arrow([[262, 148], [296, 148]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[262, 248], [296, 248]], { stroke: T.inkMuted, strokeWidth: 1.3 }));

  els.push(text(600, 92, 'MEASURED', { size: 9, stroke: T.inkSubtle }));
  els.push(...card(600, 106, 320, 184, { spine: T.success, strokeWidth: 1.4 }));
  els.push(text(618, 114, 'THE NUMBERS THAT MATTER TO YOU', { size: 9, stroke: T.success }));
  [['resolved-rate', '61% against 68%'],
   ['cost per resolved task', '$0.69 against $0.90'],
   ['wall-clock time', 'your instrumentation'],
   ['interventions per run', 'your instrumentation']]
    .forEach(([n, v], i) => {
      els.push(rect(618, 136 + i * 36, 284, 30, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
      els.push(text(630, 145 + i * 36, n, { size: 10, stroke: T.ink }));
      els.push(text(630, 145 + i * 36, v,
        { size: 10, align: 'right', width: 260, stroke: i < 2 ? T.ink : T.inkSubtle }));
    });

  els.push(arrow([[562, 148], [596, 180]], { stroke: T.primary, strokeWidth: 1.3 }));
  els.push(arrow([[562, 248], [596, 216]], { stroke: T.accent, strokeWidth: 1.3 }));

  // The part the first cut of this figure left out. Without it the sheet promised
  // a verdict that section 6 spends a bullet explaining you do not get, and that
  // Post 22 fig 2 works through in the opposite direction on a larger task set.
  els.push(...card(40, 310, 880, 146, { spine: T.warn, strokeWidth: 1.5 }));
  els.push(text(58, 318, 'IS THE SEVEN-POINT GAP REAL? THE ARITHMETIC THAT BELONGS BEFORE THE MIGRATION',
    { size: 9.5, stroke: T.warn }));
  [[58, 'TREAT 100 RUNS AS INDEPENDENT',
    ['standard error near a 65% rate', 'is about 4.8 points, so a', '7-point gap is about 1.5 of them'],
    'suggestive, not settled'],
   [358, 'THEY ARE NOT INDEPENDENT',
    ['five runs share a task, so the', 'honest denominator is the 20', 'tasks: standard error about 11'],
    'detects a large effect, not seven points'],
   [658, 'AND READ THE PER-TASK DIFF',
    ['suppose B fixed nine tasks and', 'broke two: that is the row that', 'decides it (Post 22 s7)'],
    'invisible in either aggregate']]
    .forEach(([x, head, lines, verdict]) => {
      els.push(text(x, 340, head, { size: 9.5, stroke: T.ink }));
      lines.forEach((l, i) => els.push(text(x, 360 + i * 14, fit(l, 9, 234, 'ab arith'),
        { size: 9, stroke: T.inkMuted })));
      els.push(text(x, 408, fit(verdict, 10, 234, 'ab verdict'), { size: 10, stroke: T.alert }));
    });
  els.push(rule(58, 902, 428));
  els.push(text(58, 434, fit('Pairing the two arms task by task is what strips out the task-difficulty variance that swamps the interval (Post 22 s8).',
    9, 844, 'ab footer'), { size: 9, stroke: T.inkSubtle }));

  els.push(...card(40, 472, 430, 100, { spine: T.warn, strokeWidth: 1.4 }));
  els.push(text(58, 480, 'CAUTION: YOU MAY BE MEASURING THE PAIRING', { size: 9.5, stroke: T.warn }));
  ['Judging a model outside its native SDK understates it, because of the',
   'co-training flywheel (Post 04). So an A/B across SDKs is partly measuring',
   'the model-and-harness pairing rather than the harness on its own.'].forEach((l, i) => {
    els.push(text(58, 502 + i * 17, fit(l, 9, 394, 'caution'), { size: 9, stroke: T.ink }));
  });

  els.push(...card(490, 472, 430, 100, { spine: T.warn, strokeWidth: 1.4 }));
  els.push(text(508, 480, 'CAUTION: WHERE THE MIGRATION COST LIVES', { size: 9.5, stroke: T.warn }));
  ['It is rarely the loop. It is dominated by how deeply your custom layer',
   'reached into the types of the SDK, which is a cost you control at design',
   'time rather than at migration time.'].forEach((l, i) => {
    els.push(text(508, 502 + i * 17, fit(l, 9, 394, 'caution'), { size: 9, stroke: T.ink }));
  });

  els.push(text(40, 588, fit('The arithmetic turns "B feels better" into "B costs 30% more per resolved task and regressed two jobs we care about".', 11.5, 880, 'ab close 1'),
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 610, fit('It takes a day, not an afternoon, it still beats any feature matrix -- and on twenty tasks it does not always give a verdict.', 11.5, 880, 'ab close 2'),
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A harness A/B: the model and task set held fixed, the harness varied, and the arithmetic that says whether the gap is real',
    desc: 'A hand-drawn experiment layout. On the left, held fixed: the model, the same one on both '
      + 'arms, and the task set, twenty representative jobs from your own backlog rather than from '
      + 'a public benchmark, at five seeds each for 100 runs per arm. In the middle, the only thing '
      + 'that changes: harness A, what you run today, resolving 61 of 100 runs at $0.42 a run, and '
      + 'harness B, the one you are considering, resolving 68 of 100 at $0.61 a run. On the right, '
      + 'measured: resolved-rate at 61% against 68%, cost per resolved task at $0.69 against $0.90, '
      + 'and wall-clock time and interventions per run, which only your own instrumentation '
      + 'reports. A full-width panel below asks whether the seven-point gap is real and works it '
      + 'through in three columns. Treating the 100 runs as independent puts the standard error near '
      + 'a 65% rate at about 4.8 points, so a 7-point gap is about 1.5 of them: suggestive, not '
      + 'settled. But the runs are not independent, because five of them share a task, so the honest '
      + 'denominator is the 20 tasks, where the standard error is about 11 points, and twenty tasks '
      + 'detect a large effect rather than a seven-point one. And the per-task diff decides it '
      + 'anyway, because B fixing nine tasks and breaking two is invisible in either aggregate. A '
      + 'footer records that pairing the two arms task by task strips out the task-difficulty '
      + 'variance that swamps the interval. Below, two cautions. The first is that you may be '
      + 'measuring the pairing rather than the harness, because judging a model outside its native '
      + 'SDK understates it through the co-training flywheel. The second is that the migration cost '
      + 'is rarely the loop and is dominated by how deeply your custom layer reached into the types '
      + 'of the SDK, which is a cost you control at design time rather than at migration time. '
      + 'Captions record that the arithmetic turns a feeling that B is better into a statement that '
      + 'B costs about 30% more per resolved task and regressed two jobs, that this still beats any '
      + 'feature matrix, and that it takes a day rather than an afternoon and on twenty tasks does '
      + 'not always give a verdict.',
  };
}

module.exports = { featureMatrix, buildVsBuy, harnessAB };

if (require.main === module) {
  emit('01-sdk-feature-matrix', featureMatrix());
  emit('02-build-vs-buy', buildVsBuy());
  emit('03-harness-ab', harnessAB());
}
