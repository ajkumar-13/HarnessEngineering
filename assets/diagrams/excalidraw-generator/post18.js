// The post 18 diagrams, hand-drawn.
//
//   01-ralph-loop              960 x 584  Mirror of the existing figure, filled out.
//   02-multi-context-timeline  960 x 620  Mirror, filled out.
//   03-inside-one-iteration    960 x 490  NEW, published: sections 2 and 3 had no figure.
//
// The first two used to draw the loop from outside and stop there: a strip of
// boxes and a pair of curves, with the post's numbers left in the prose. They
// now carry them. Figure 1 names the three files that survive a reset, the
// literal one-line form of the loop, the guards the driver adds (max_iters=50,
// stale_cap=3, the criteria diff) and the one reported delivery. Figure 2 keeps
// the sawtooth and the staircase and hangs section 4's cache table underneath,
// because the reset's price is the counter-intuitive part of the architecture
// and the only part with real money attached.
//
// The third draws what one iteration's context is made of, which is where the
// re-entry tax, the cacheable prefix and the read-only spec all live.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function ralphLoop() {
  resetSeq();
  const W = 960, H = 584;

  const els = [...heading('The Ralph loop',
    'One task per fresh context against a spec on disk; everything that must survive a reset is written to the repository.', W)];

  // --- the state on disk, which is the whole memory of the agent -----------
  els.push(...card(40, 84, 880, 114, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(60, 90, 'ON DISK - THE STATE THAT SURVIVES EVERY RESET', { size: 10, stroke: T.inkSubtle }));
  els.push(text(520, 90, 'the window is disposable; these three are the memory',
    { size: 9.5, align: 'right', width: 380, stroke: T.inkMuted }));

  const DISK = [
    ['THE SPEC', 'HUMAN-OWNED', T.alert, 'feature_list.json  ·  prd.json',
      'what to build, and what "done" means', 'the loop may flip one field: the pass bit'],
    ['THE HANDOFF', 'LOOP WRITES', T.warn, 'claude-progress.txt  ·  progress.txt',
      'what is done, what is next, what is blocked', 'a log of what happened, not a change to the ask'],
    ['THE REPOSITORY', 'LOOP + GATE', T.primary, 'source  ·  tests  ·  init.sh',
      'whatever the last commit left behind', 'one commit per verifiable increment'],
  ];
  DISK.forEach((d, i) => {
    const x = 60 + i * 286;
    els.push(rect(x, 112, 268, 78, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
    els.push(text(x + 12, 118, d[0], { size: 11.5, stroke: T.ink }));
    els.push(rect(x + 172, 116, 88, 17, { stroke: d[2], fill: d[2], strokeWidth: 1 }));
    els.push(text(x + 172, 119, d[1], { size: 8, align: 'center', width: 88, stroke: T.onAccent }));
    els.push(text(x + 12, 141, fit(d[3], 8.5, 244, 'disk files'), { size: 8.5, family: 3, stroke: T.primary }));
    els.push(text(x + 12, 158, fit(d[4], 8.5, 244, 'disk gloss'), { size: 8.5, stroke: T.inkMuted }));
    els.push(text(x + 12, 174, fit(d[5], 8.5, 244, 'disk rule'), { size: 8.5, stroke: d[2] }));
  });

  // --- the four steps ------------------------------------------------------
  const STEPS = [
    ['FRESH CONTEXT', 'a new process, so no state can', 'leak in; it reads spec + handoff'],
    ['DO ONE TASK', 'the highest-priority criterion', 'not yet satisfied, and only that'],
    ['VERIFY + COMMIT', 'the gate runs end to end, then', 'one commit for that increment'],
    ['RESET', 'the process exits; the window', 'is discarded, nothing carried'],
  ];
  STEPS.forEach((s, i) => {
    const x = 40 + i * 230;
    els.push(rect(x, 240, 190, 74, { stroke: T.ink, fill: T.surface, strokeWidth: 1.5 }));
    els.push(text(x, 249, s[0], { size: 12.5, align: 'center', width: 190, stroke: T.ink }));
    els.push(text(x, 271, fit(s[1], 8.5, 174, 'step gloss'), { size: 8.5, align: 'center', width: 190, stroke: T.inkMuted }));
    els.push(text(x, 285, fit(s[2], 8.5, 174, 'step gloss'), { size: 8.5, align: 'center', width: 190, stroke: T.inkMuted }));
    if (i) els.push(arrow([[x - 36, 277], [x - 6, 277]], { stroke: T.ink, strokeWidth: 1.3 }));
  });

  els.push(arrow([[135, 200], [135, 236]], { stroke: T.accent, strokeWidth: 1.3 }));
  els.push(text(146, 204, 'reads the spec and the handoff into a clean window', { size: 9, stroke: T.accent }));
  els.push(arrow([[595, 236], [595, 200]], { stroke: T.accent, strokeWidth: 1.3 }));
  els.push(text(606, 204, 'commits, and flips one pass bit', { size: 9, stroke: T.accent }));

  els.push(arrow([[825, 316], [825, 338], [135, 338], [135, 318]], { stroke: T.primary, strokeWidth: 1.3 }));
  els.push(text(300, 342, 'repeat - nothing is carried across the reset; the process exits and the next one starts clean',
    { size: 9.5, stroke: T.primary }));

  // --- what the loop actually is, what guards it, what it has met ----------
  els.push(...card(40, 364, 272, 152, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 372, 'THE LITERAL FORM', { size: 10, stroke: T.primary }));
  els.push(rect(56, 388, 240, 50, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
  ['while :; do', '  cat PROMPT.md | claude-code', 'done'].forEach((l, i) => {
    els.push(text(66, 393 + i * 14, fit(l, 8.5, 220, 'one-liner'), { size: 8.5, family: 3, stroke: T.ink }));
  });
  els.push(rule(56, 296, 448));
  ['No state, no iteration count, no convergence',
    'check and no stop condition. Everything that',
    'makes it work sits on disk instead.'].forEach((l, i) => {
    els.push(text(56, 456 + i * 13, fit(l, 8.5, 240, 'one-liner note'), { size: 8.5, stroke: T.inkMuted }));
  });
  els.push(text(56, 498, 'the canonical form (Huntley, 2025)', { size: 8.5, stroke: T.inkSubtle }));

  els.push(...card(344, 364, 272, 152, { spine: T.warn, strokeWidth: 1.3 }));
  els.push(text(362, 372, 'THE GUARDS YOU ADD', { size: 10, stroke: T.warn }));
  const GUARDS = [
    ['max_iters = 50', 'the hard cap', 'a hard iteration cap (Post 03, stop condition 2)'],
    ['stale_cap = 3', 'no new commit', 'three iterations, no new commit: no progress'],
    ['spec-moved', 'the goalposts', 'diff the criteria; only the pass bit may differ'],
  ];
  GUARDS.forEach((g, i) => {
    const y = 392 + i * 42;
    els.push(rect(360, y, 112, 18, { stroke: T.warn, fill: T.neutral1, strokeWidth: 1 }));
    els.push(text(360, y + 4, fit(g[0], 8.5, 104, 'guard code'), { size: 8.5, family: 3, align: 'center', width: 112, stroke: T.ink }));
    els.push(text(482, y + 2, fit(g[1], 9, 116, 'guard name'), { size: 9, stroke: T.ink }));
    els.push(text(360, y + 22, fit(g[2], 8.5, 240, 'guard gloss'), { size: 8.5, stroke: T.inkMuted }));
  });

  els.push(...card(648, 364, 272, 160, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(666, 372, 'THE REPORTED RECORD', { size: 10, stroke: T.accent }));
  els.push(text(664, 390, '$50,000 contract, ~$297 of inference', { size: 11, stroke: T.accent }));
  els.push(text(664, 408, 'delivered as a tested, reviewed MVP;', { size: 8.5, stroke: T.inkMuted }));
  els.push(text(664, 420, 'one reported outcome from the technique', { size: 8.5, stroke: T.inkMuted }));
  els.push(text(664, 432, "author's own account, not a benchmark", { size: 8.5, stroke: T.inkMuted }));
  els.push(rule(664, 904, 448));
  els.push(text(664, 456, 'a 7-month doubling time', { size: 11, stroke: T.primary }));
  els.push(text(664, 474, 'the software-task length a frontier model', { size: 8.5, stroke: T.inkMuted }));
  els.push(text(664, 486, 'completes at 50% reliability has doubled', { size: 8.5, stroke: T.inkMuted }));
  els.push(text(664, 498, 'about every 7 months since 2019 (METR,', { size: 8.5, stroke: T.inkMuted }));
  els.push(text(664, 510, 'Kwa et al., 2025): the horizon moves', { size: 8.5, stroke: T.inkMuted }));

  els.push(text(40, 538, 'The window is disposable and the repository is the memory, which is why nothing has to be carried across a reset.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 560, 'Brute force plus persistence: the loop is deliberately dumb, and the guards, not the cleverness, are what make it safe to leave running.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'One task per fresh context, against a spec on disk, with the guards that make it safe to leave running',
    desc: 'A hand-drawn figure in three tiers. Along the top, the state that survives every reset, as three '
      + 'files: the spec, human-owned, feature_list.json or prd.json, holding what to build and what done '
      + 'means, of which the loop may flip only one field, the pass bit; the handoff, written by the loop, '
      + 'claude-progress.txt or progress.txt, holding what is done, what is next and what is blocked, a log '
      + 'of what happened rather than a change to the ask; and the repository, written by the loop and read '
      + 'by the gate, holding source, tests and init.sh, with one commit per verifiable increment. In the '
      + 'middle, four steps in a cycle: a fresh context, which is a new process so no state can leak in and '
      + 'which reads the spec and handoff; do one task, the highest-priority criterion not yet satisfied and '
      + 'only that; verify and commit, where the gate runs end to end and one commit records the increment; '
      + 'and reset, where the process exits and the window is discarded. An arrow returns from reset to the '
      + 'fresh context, marked repeat, with nothing carried across. Arrows run from the files down into the '
      + 'fresh context, marked reads, and from the commit step back up, marked commits and flips one pass '
      + 'bit. Along the bottom, three panels. The literal form shows the one-line shell loop, while true, '
      + 'cat PROMPT.md piped to the coding agent, done, and notes that it has no state, no iteration count, '
      + 'no convergence check and no stop condition, because everything that makes it work sits on disk '
      + '(Huntley, 2025). The guards you add lists three: max_iters equals 50, a hard iteration cap; '
      + 'stale_cap equals 3, three iterations with no new commit counted as no progress; and spec-moved, a '
      + 'diff of the criteria in which only the pass bit may differ. The reported record carries two '
      + 'numbers: a fifty-thousand-dollar contract delivered as a tested, reviewed minimum viable product '
      + 'for roughly two hundred and ninety-seven dollars of inference, described as one reported outcome '
      + 'from the technique author rather than a benchmark; and a seven-month doubling time, the length of '
      + 'software task a frontier model completes at fifty per cent reliability having doubled about every '
      + 'seven months since 2019, from METR. Closing lines record that the window is disposable and the '
      + 'repository is the memory, and that the guards rather than any cleverness are what make a '
      + 'deliberately dumb loop safe to leave running.',
  };
}

// ---------------------------------------------------------------- diagram 2
function multiContextTimeline() {
  resetSeq();
  const W = 960, H = 620;

  const els = [...heading('One build across many fresh contexts',
    'Every window resets and stays bounded, the progress accumulates on disk, and the reset has a price you can compute.', W)];

  // --- upper chart: context used inside one window ------------------------
  els.push(text(40, 84, 'CONTEXT USED INSIDE ONE WINDOW', { size: 10, stroke: T.inkSubtle }));
  els.push(line([[110, 112], [890, 112]], { stroke: T.alert, strokeWidth: 1.3, strokeStyle: 'dashed' }));
  els.push(text(124, 94, 'context window limit - above this line the context overflows', { size: 9, stroke: T.alert }));
  els.push(line([[110, 246], [890, 246]], { stroke: T.ink, strokeWidth: 1 }));

  const teeth = [];
  for (let i = 0; i < 8; i++) {
    const x0 = 120 + i * 95;
    teeth.push([x0, 246], [x0 + 76, 142], [x0 + 80, 246]);
  }
  els.push(line(teeth, { stroke: T.primary, strokeWidth: 1.5 }));

  els.push(line([[120, 246], [830, 92]], { stroke: T.alert, strokeWidth: 1.3, strokeStyle: 'dashed' }));
  els.push(text(836, 84, 'one unmanaged', { size: 8.5, stroke: T.alert }));
  els.push(text(836, 96, 'context', { size: 8.5, stroke: T.alert }));

  els.push(text(120, 252, 'each tooth is one iteration: the window fills as the task runs, then drops to the floor at the reset',
    { size: 9, stroke: T.primary }));
  els.push(text(120, 266, 'the straight dashed climb is a single unmanaged context instead: it crosses the limit and overflows',
    { size: 9, stroke: T.alert }));
  els.push(text(540, 252, 'eight iterations shown', { size: 9, align: 'right', width: 350, stroke: T.inkSubtle }));
  els.push(text(540, 266, 'the floor is the frozen prefix', { size: 9, align: 'right', width: 350, stroke: T.inkSubtle }));

  // --- lower chart: progress on disk --------------------------------------
  els.push(text(40, 286, 'PROGRESS ON DISK - ONE COMMIT PER VERIFIABLE INCREMENT', { size: 10, stroke: T.inkSubtle }));
  els.push(text(520, 286, fit("the reference build's spec holds over 200 features, each with a pass bit", 9, 400, 'spec size'),
    { size: 9, align: 'right', width: 400, stroke: T.inkMuted }));
  els.push(line([[110, 386], [890, 386]], { stroke: T.ink, strokeWidth: 1 }));

  const stair = [];
  for (let i = 0; i < 8; i++) {
    const y = 378 - i * 9;
    stair.push([120 + i * 95, y], [120 + (i + 1) * 95, y], [120 + (i + 1) * 95, y - 9]);
  }
  els.push(line(stair, { stroke: T.success, strokeWidth: 1.5 }));

  for (let i = 0; i < 8; i++) {
    els.push(line([[120 + i * 95, 386], [120 + i * 95, 391]], { stroke: T.border, strokeWidth: 1 }));
    els.push(text(100 + i * 95 + 47, 392, String(i + 1), { size: 9, align: 'center', width: 40, stroke: T.inkSubtle }));
  }
  els.push(line([[880, 386], [880, 391]], { stroke: T.border, strokeWidth: 1 }));
  els.push(text(120, 408, 'iterations, one per fresh context; the driver caps the run at max_iters = 50', { size: 9, stroke: T.inkSubtle }));
  els.push(text(560, 408, 'progress never comes back down', { size: 9, align: 'right', width: 330, stroke: T.success }));

  // --- what the reset costs ------------------------------------------------
  els.push(...card(40, 424, 596, 132, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(62, 430, 'WHAT THE RESET COSTS', { size: 10, stroke: T.primary }));
  els.push(text(62, 446, fit("the post's worked example: a 12,000-token frozen prefix over 50 iterations, at $3 per million input tokens",
    8.5, 558, 'cost premise'), { size: 8.5, stroke: T.inkMuted }));
  els.push(text(62, 464, 'ITERATION CADENCE AND CACHE TIER', { size: 8, stroke: T.inkSubtle }));
  els.push(text(326, 464, 'WRITES', { size: 8, stroke: T.inkSubtle }));
  els.push(text(430, 464, 'READS', { size: 8, stroke: T.inkSubtle }));
  els.push(text(440, 464, 'PREFIX COST, 50 ITERATIONS', { size: 8, align: 'right', width: 180, stroke: T.inkSubtle }));
  const ROWS = [
    ['no cache configured', 'n/a', 'n/a', '$1.80', T.inkMuted],
    ['under 5 min apart  ·  five-minute tier', '1 x $0.045', '49 x $0.0036', '$0.22', T.success],
    ['about 8 min apart  ·  five-minute tier', '50 x $0.045', 'none', '$2.25', T.alert],
    ['about 8 min apart  ·  one-hour tier', '1 x $0.072', '49 x $0.0036', '$0.25', T.success],
  ];
  ROWS.forEach((r, i) => {
    const y = 480 + i * 18;
    els.push(rule(62, 620, y - 4));
    els.push(text(62, y, fit(r[0], 9, 258, 'cost row'), { size: 9, stroke: r[4] }));
    els.push(text(326, y, r[1], { size: 9, stroke: r[4] }));
    els.push(text(430, y, r[2], { size: 9, stroke: r[4] }));
    els.push(text(540, y, r[3], { size: 9, align: 'right', width: 80, stroke: r[4] }));
  });

  els.push(...card(664, 424, 256, 132, { spine: T.alert, strokeWidth: 1.3 }));
  els.push(text(686, 430, 'THE GATE UNDER THE STAIRCASE', { size: 10, stroke: T.alert }));
  ['The agent changed code and tested it',
    'with unit tests and curl while failing to',
    'notice the feature did not work end to',
    'end. The gate moved to browser',
    'automation instead (Anthropic, 2025).'].forEach((l, i) => {
    els.push(text(684, 448 + i * 12, fit(l, 8.5, 224, 'gate note'), { size: 8.5, stroke: T.inkMuted }));
  });
  els.push(rule(684, 904, 512));
  ['Fifty green commits over a product that',
    'does not run is victory declaration with',
    'nobody present to catch it (Post 05).'].forEach((l, i) => {
    els.push(text(684, 518 + i * 12, fit(l, 8.5, 224, 'gate note'), { size: 8.5, stroke: T.ink }));
  });

  els.push(text(40, 572, 'A single context climbs into overflow; the Ralph loop keeps every window bounded while the build grows on disk.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 594, "Pick the cache tier from the iteration's clock, not the count: at eight minutes apart the default costs about 25% more than no cache.",
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Bounded sawtooth context usage, monotonically rising progress, and what the resets cost',
    desc: 'A hand-drawn figure with two charts over two panels. The upper chart shows the context used '
      + 'inside one window across eight iterations. A dashed line marks the context window limit, above '
      + 'which the context overflows. A sawtooth rises within each iteration and drops back to the floor at '
      + 'every reset, always staying below the limit; a note records that the floor is the frozen prefix. A '
      + 'straight dashed climb shows a single unmanaged context instead, crossing the limit into overflow. '
      + 'The lower chart shows progress on disk, one commit per verifiable increment, as a staircase that '
      + 'rises monotonically and never comes back down, over an axis of iterations numbered one to eight '
      + 'with a note that the driver caps the run at max_iters equals 50, and a note that the reference '
      + 'build spec holds over 200 features each with a pass bit. Below them, a panel on what the reset '
      + 'costs works through the post example of a twelve-thousand-token frozen prefix over fifty '
      + 'iterations at three dollars per million input tokens: with no cache configured the prefix costs a '
      + 'dollar eighty; under five minutes apart on the five-minute tier, one write at four and a half '
      + 'cents plus forty-nine reads, twenty-two cents; about eight minutes apart on the same five-minute '
      + 'tier, fifty writes and no reads at all, two dollars twenty-five, which is more than paying for no '
      + 'cache at all; and about eight minutes apart on the one-hour tier, one write at just over seven '
      + 'cents plus forty-nine reads, twenty-five cents. A second panel, the gate under the staircase, '
      + 'records that the agent changed code and tested it with unit tests and curl while failing to notice '
      + 'the feature did not work end to end, so the gate moved to browser automation, and that fifty green '
      + 'commits over a product that does not run is victory declaration with nobody present to catch it. '
      + 'Closing lines record that a single context climbs into overflow while the Ralph loop keeps every '
      + 'window bounded, and that the cache tier should be picked from the iteration clock rather than the '
      + 'iteration count.',
  };
}


// ---------------------------------------------------------------- diagram 3
function insideOneIteration() {
  resetSeq();
  const W = 960, H = 490;

  const els = [...heading('Inside one iteration',
    'What the fresh context is made of, in what order, and which parts the loop is allowed to change.')];

  els.push(text(88, 92, 'ONE ITERATION CONTEXT, STABLE FIRST', { size: 9, stroke: T.inkSubtle }));

  const BLOCKS = [
    ['SYSTEM PROMPT', 'the harness rules; this never changes', 'CACHED', T.success],
    ['THE SPEC', 'what to build, and what done means', 'CACHED', T.success],
    ['THE HANDOFF', 'what is done, what is next, what is blocked', 'REBUILT', T.warn],
    ['THE REPOSITORY STATE', 'whatever the last commit left behind', 'REBUILT', T.warn],
    ['THIS ITERATION WORK', 'the turns that actually change something', 'REBUILT', T.warn],
  ];
  BLOCKS.forEach((b, i) => {
    const y = 112 + i * 54;
    els.push(rect(88, y, 382, 46, { stroke: T.ink, fill: T.surface, strokeWidth: 1.3 }));
    els.push(text(104, y + 8, b[0], { size: 11.5, stroke: T.ink }));
    els.push(text(104, y + 28, fit(b[1], 9, 256, 'block gloss'), { size: 9, stroke: T.inkMuted }));
    els.push(rect(370, y + 6, 88, 18, { stroke: b[3], fill: b[3], strokeWidth: 1 }));
    els.push(text(370, y + 10, b[2], { size: 8.5, align: 'center', width: 88, stroke: T.onAccent }));
  });
  els.push(line([[60, 112], [60, 212]], { stroke: T.success, strokeWidth: 2.5, roughness: 0.4 }));
  els.push(text(46, 220, 'the cached', { size: 8, stroke: T.success }));
  els.push(text(46, 232, 'prefix', { size: 8, stroke: T.success }));

  ['The first two blocks are byte-identical on every iteration, so a provider prompt',
   'cache serves them. Put the volatile handoff above the fixed spec and you invalidate',
   'the prefix on every reset, for no benefit whatsoever.'].forEach((l, i) => {
    els.push(text(88, 390 + i * 15, fit(l, 9, 470, 'prefix note'), { size: 9, stroke: T.ink }));
  });

  // Sizing.
  els.push(...card(490, 92, 430, 180, { spine: T.primary, strokeWidth: 1.4 }));
  els.push(text(508, 100, 'SIZING ONE TASK', { size: 10, stroke: T.primary }));
  const SIZES = [
    [118, 'TOO LARGE', 26, 360, 'the iteration overflows its window, which is the problem you were solving'],
    [168, 'TOO SMALL', 26, 20, 'the re-entry tax dominates: thousands of tokens spent orienting to move a line'],
    [218, 'ONE VERIFIABLE INCREMENT', 26, 150, 'the smallest change that leaves the tests able to say yes or no'],
  ];
  SIZES.forEach((s) => {
    els.push(text(508, s[0], s[1], { size: 9, stroke: T.ink }));
    els.push(rect(508, s[0] + 12, s[2], 16, { stroke: T.ink, fill: T.neutral2, strokeWidth: 1 }));
    els.push(rect(508 + s[2], s[0] + 12, s[3], 16, { stroke: T.ink, fill: T.primary, strokeWidth: 1 }));
    els.push(text(508, s[0] + 34, fit(s[4], 8.5, 394, 'size note'), { size: 8.5, stroke: T.inkMuted }));
  });
  els.push(line([[860, 112], [860, 262]], { stroke: T.alert, strokeWidth: 1.3, strokeStyle: 'dashed' }));
  els.push(text(786, 100, 'window limit', { size: 8, stroke: T.alert }));

  // Who may edit what.
  els.push(...card(490, 286, 430, 150, { spine: T.accent, strokeWidth: 1.4 }));
  els.push(text(508, 294, 'WHO MAY EDIT WHAT', { size: 10, stroke: T.accent }));
  els.push(text(508, 314, 'THE SPEC: read-only to the loop', { size: 11, stroke: T.ink }));
  els.push(text(508, 332, 'An agent that can move the goalposts will satisfy is_done by', { size: 9, stroke: T.inkMuted }));
  els.push(text(508, 346, 'rewriting what done means. Amending it is a human act.', { size: 9, stroke: T.inkMuted }));
  els.push(text(508, 368, 'THE HANDOFF: read-write', { size: 11, stroke: T.ink }));
  els.push(text(508, 386, 'Progress, decisions and blockers are a log of what happened,', { size: 9, stroke: T.inkMuted }));
  els.push(text(508, 400, 'not a change to what is being asked for.', { size: 9, stroke: T.inkMuted }));
  els.push(text(508, 418, 'Enforce it: refuse to proceed if the spec hash changed mid-iteration.',
    { size: 9, stroke: T.success }));

  els.push(text(40, 452, 'The re-entry tax is real but small, provided the part that never changes sits where a cache can find it.',
    { size: 11, stroke: T.ink }));
  els.push(text(40, 474, 'And the goalposts have to be somewhere the runner cannot reach, which is the property that makes the architecture trustworthy.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The context of one Ralph iteration, its cached prefix, its sizing, and its permissions',
    desc: 'A hand-drawn figure. On the left, the context of a single iteration is stacked stable '
      + 'first: the system prompt, which holds the harness rules and never changes; the spec, which '
      + 'says what to build and what done means; the handoff, holding what is done, what is next '
      + 'and what is blocked; the repository state, whatever the last commit left behind; and this '
      + 'iteration work, the turns that actually change something. The first two are tagged cached '
      + 'and bracketed as the cached prefix; the rest are tagged rebuilt. A note records that the '
      + 'first two blocks are byte-identical on every iteration so a provider prompt cache serves '
      + 'them, and that putting the volatile handoff above the fixed spec invalidates the prefix on '
      + 'every reset for no benefit. On the right, a panel on sizing one task shows three bars '
      + 'against a window limit: too large, where the iteration overflows its window; too small, '
      + 'where the re-entry tax dominates because thousands of tokens are spent orienting to change '
      + 'one line; and one verifiable increment, the smallest change that leaves the tests able to '
      + 'say yes or no. A second panel covers who may edit what: the spec is read-only to the loop, '
      + 'because an agent that can move the goalposts will satisfy the done check by rewriting what '
      + 'done means, so amending it is a human act; the handoff is read-write, because progress, '
      + 'decisions and blockers are a log of what happened rather than a change to what is being '
      + 'asked for; and the rule is enforced by refusing to proceed if the spec hash changed '
      + 'mid-iteration.',
  };
}

module.exports = { ralphLoop, multiContextTimeline, insideOneIteration };

if (require.main === module) {
  emit('01-ralph-loop', ralphLoop());
  emit('02-multi-context-timeline', multiContextTimeline());
  emit('03-inside-one-iteration', insideOneIteration());
}
