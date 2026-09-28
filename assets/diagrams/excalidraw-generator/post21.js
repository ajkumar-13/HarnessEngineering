// The post 21 diagrams, hand-drawn.
//
//   01-trace-tree       960 x 460  Mirror of the existing figure.
//   02-trace-to-ratchet 960 x 380  Mirror.
//   03-trace-shapes     960 x 470  NEW, published: section 3 had no figure.
//
// Section 3 claims that failures "deform the shape in characteristic ways" and
// then names four deformations in prose, which is the one claim in this post
// that a picture can settle outright. Five small waterfalls -- one healthy, four
// deformed -- are the section.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

const MONO = 3;

// ---------------------------------------------------------------- diagram 1
function traceTree() {
  resetSeq();
  const W = 960, H = 684;

  const els = [...heading('One agent run as a trace tree',
    'Nested spans laid out on time. The shape shows where the tokens and the seconds actually went.')];

  els.push(text(200, 88, '0s', { size: 9, stroke: T.inkSubtle }));
  els.push(text(600, 88, '18s', { size: 9, align: 'right', width: 90, stroke: T.inkSubtle }));
  els.push(line([[200, 104], [690, 104]], { stroke: T.inkSubtle, strokeWidth: 1 }));

  const SPANS = [
    [0, 'agent.run', 200, 690, T.ink, '3 iterations, 41k tokens, 18s'],
    [1, 'iteration 1', 206, 350, T.primary, ''],
    [2, 'model.call', 212, 270, T.neutral3, '7.2k tokens, 2.1s'],
    [2, 'tool: bash', 276, 344, T.neutral3, 'run tests, 1.0s'],
    [1, 'iteration 2', 356, 520, T.primary, ''],
    [2, 'model.call', 362, 424, T.neutral3, '8.1k tokens, 2.3s'],
    [2, 'tool: bash', 430, 514, T.alert, 'install deps, 3.6s: the outlier'],
    [1, 'iteration 3', 526, 660, T.primary, ''],
    [2, 'model.call', 532, 578, T.neutral3, '6.4k tokens, 1.7s'],
    [2, 'subagent.run', 584, 654, T.accent, 'a child span, 12k tokens'],
    [0, 'verify.gate', 666, 690, T.success, 'pass, so the stop reason is verified'],
  ];
  SPANS.forEach((s, i) => {
    const y = 116 + i * 26;
    els.push(text(96 + s[0] * 14, y + 3, s[1], { size: 9.5, family: MONO, stroke: T.ink }));
    els.push(rect(s[2], y, s[3] - s[2], 18, { stroke: s[4], fill: s[4] === T.alert ? T.alert : T.neutral1, strokeWidth: 1.2 }));
    if (s[5]) els.push(text(706, y + 4, fit(s[5], 8.5, 214, 'span detail'), { size: 8.5, stroke: T.inkMuted }));
  });

  // --- second tier: what the spans above have to carry (section 2) --------
  els.push(text(40, 416, 'WHAT EACH SPAN HAS TO CARRY, AND THE TWO ATTRIBUTES THAT CARRY THE MOST',
    { size: 10, stroke: T.inkSubtle }));

  els.push(...card(40, 436, 536, 186, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 444, 'SPAN', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(190, 444, 'THE ATTRIBUTES THAT EARN THEIR PLACE', { size: 8.5, stroke: T.inkSubtle }));
  const CARRIES = [
    ['agent.run', 'task, harness version, tokens, wall-clock, stop.reason'],
    ['iteration', 'index, and the decision taken that turn'],
    ['model.call', 'model id, input and output tokens, latency'],
    ['tool.<name>', 'redacted arguments, outcome, exit status, latency'],
    ['subagent.run', "the child's task and its own stop reason"],
    ['verify.gate', 'what was checked, and whether it passed'],
  ];
  CARRIES.forEach((c, i) => {
    const y = 462 + i * 22;
    els.push(text(58, y, c[0], { size: 9, family: MONO, stroke: T.ink }));
    els.push(text(190, y, fit(c[1], 9, 368, 'span attrs'), { size: 9, stroke: T.inkMuted }));
  });
  els.push(rule(58, 558, 596));
  els.push(text(58, 604, 'A tool output belongs on disk with the span carrying its path, not inlined.',
    { size: 8.5, stroke: T.inkSubtle }));

  els.push(...card(592, 436, 328, 186, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(610, 444, 'stop.reason', { size: 10, family: MONO, stroke: T.accent }));
  els.push(text(610, 460, 'on the root span; look at it first', { size: 8.5, stroke: T.inkMuted }));
  ['completed: the intended exit, gate passed', 'max_iters: the hard cap was reached',
   'budget: a token or clock ceiling stopped it', 'no_progress: the stall detector fired',
   'error: only a finally block records this']
    .forEach((l, i) => els.push(text(610, 480 + i * 16, fit(l, 8.5, 292, 'stop reason'),
      { size: 8.5, stroke: T.ink })));
  els.push(rule(610, 904, 566));
  els.push(text(610, 576, 'outcome', { size: 10, family: MONO, stroke: T.accent }));
  els.push(text(610, 592, 'on each tool span, recording which layer', { size: 8.5, stroke: T.inkMuted }));
  els.push(text(610, 605, 'decided rather than whether the call ran', { size: 8.5, stroke: T.inkMuted }));

  els.push(text(40, 640, 'The same run as prose is a wall of text; as a tree it is a diagnosis.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 660, 'The flagged bar is a harness bug you can now name, rather than a feeling that the agent seems slow.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A waterfall of nested spans for one agent run',
    desc: 'A hand-drawn waterfall of one agent run laid out on an eighteen-second time axis. A root '
      + 'span, agent.run, covers three iterations and forty-one thousand tokens. Iteration one '
      + 'holds a model call of seven thousand two hundred tokens taking two point one seconds, and '
      + 'a bash tool span running tests in one second. Iteration two holds a model call of eight '
      + 'thousand one hundred tokens taking two point three seconds, and a bash tool span '
      + 'installing dependencies that takes three point six seconds and is flagged as the outlier. '
      + 'Iteration three holds a model call of six thousand four hundred tokens and a sub-agent run '
      + 'as a child span of twelve thousand tokens. A final verify gate passes, so the stop reason '
      + 'is verified. Captions record that the same run as prose is a wall of text while as a tree '
      + 'it is a diagnosis, and that the flagged bar is a harness bug you can name rather than a '
      + 'feeling that the agent seems slow. Below the waterfall, a table lists what each span has to carry: the run span takes the task, harness version, tokens, wall-clock and stop reason; the iteration span its index and the decision taken that turn; the model call its model id, token counts and latency; the tool span its redacted arguments, outcome, exit status and latency; the sub-agent span the child task and its own stop reason; and the verify gate what was checked and whether it passed, with a note that a tool output belongs on disk with the span carrying its path rather than inlined. A panel beside it gives the two attributes that carry the most weight: stop.reason on the root span, with its five values completed, max_iters, budget, no_progress and error, and outcome on each tool span, recording which layer decided rather than whether the call ran.',
  };
}

// ---------------------------------------------------------------- diagram 2
function traceToRatchet() {
  resetSeq();
  const W = 960, H = 560;

  const els = [...heading('A trace is a lead; the ratchet is the fix',
    'Localise the failing component in the trace, then turn that one failure into constraints that outlive it.')];

  els.push(...card(40, 96, 280, 200, { spine: T.alert, strokeWidth: 1.4 }));
  els.push(text(58, 104, 'TRACE', { size: 10, stroke: T.alert }));
  els.push(rect(58, 126, 244, 14, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.1 }));
  els.push(text(66, 128, 'agent.run', { size: 8.5, family: MONO, stroke: T.ink }));
  els.push(rect(76, 146, 226, 14, { stroke: T.alert, fill: T.alert, strokeWidth: 1.1 }));
  els.push(text(84, 148, 'subagent.run', { size: 8.5, family: MONO, stroke: T.onAccent }));
  ['30 iterations, 0 new files,', 'no exit of its own, and then', 'the budget ceiling killed it.'].forEach((l, i) => {
    els.push(text(58, 178 + i * 16, l, { size: 9.5, stroke: T.ink }));
  });
  els.push(text(58, 240, 'The span is the symptom.', { size: 9.5, stroke: T.inkMuted }));
  els.push(rule(58, 302, 258));
  els.push(text(58, 266, 'Read stop.reason on the root first:', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(58, 278, 'it says budget, and not completed.', { size: 8.5, stroke: T.inkSubtle }));

  els.push(arrow([[322, 196], [336, 196]], { stroke: T.inkMuted, strokeWidth: 1.4 }));

  els.push(...card(340, 96, 280, 200, { spine: T.primary, strokeWidth: 1.4 }));
  els.push(text(358, 104, 'LOCALISE', { size: 10, stroke: T.primary }));
  ['Failing component: no-progress', 'detection was missing inside', 'the sub-agent own loop.'].forEach((l, i) => {
    els.push(text(358, 128 + i * 16, l, { size: 10, stroke: T.ink }));
  });
  els.push(rule(358, 602, 190));
  ['Not a model bug.', 'A stop-condition bug, which is a', 'named harness fault (Posts 03, 05).'].forEach((l, i) => {
    els.push(text(358, 200 + i * 16, l, { size: 9.5, stroke: T.inkMuted }));
  });
  els.push(rule(358, 602, 258));
  els.push(text(358, 266, 'A loop that cannot stop needs a stop', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(358, 278, 'condition, not a better prompt.', { size: 8.5, stroke: T.inkSubtle }));

  els.push(arrow([[622, 196], [636, 196]], { stroke: T.inkMuted, strokeWidth: 1.4 }));

  els.push(...card(640, 96, 280, 200, { spine: T.success, strokeWidth: 1.4 }));
  els.push(text(658, 104, 'RATCHET', { size: 10, stroke: T.success }));
  [['rule', 'cap sub-agent iterations in the memory file'],
   ['hook', 'a no-progress detector kills a stalled loop'],
   ['replay', 'add this trace to the regression set (Post 22)']].forEach((r, i) => {
    const y = 128 + i * 50;
    els.push(rect(658, y, 56, 20, { stroke: T.success, fill: T.success, strokeWidth: 1 }));
    els.push(text(658, y + 5, r[0], { size: 9, align: 'center', width: 56, stroke: T.onAccent }));
    els.push(text(658, y + 26, fit(r[1], 9, 244, 'ratchet'), { size: 9, stroke: T.ink }));
  });
  els.push(text(658, 278, 'One trace, three durable constraints.', { size: 9, stroke: T.inkMuted }));

  // --- second tier: what the trace changes about the question (section 1) --
  els.push(text(40, 318, 'THE SAME RUN, DESCRIBED TWO WAYS: THIS IS THE WHOLE VALUE OF THE TREE',
    { size: 10, stroke: T.inkSubtle }));

  const SAID = [
    [40, T.alert, 'WITHOUT A TRACE', '"the agent is flaky"',
     ['A complaint. It names no component, so', 'there is nothing to fix and nothing to',
      'ratchet, and the next run fails the same', 'way with the same explanation.']],
    [490, T.success, 'WITH A TRACE', "\"iteration 14's sub-agent looped",
     ['A bug. The component is named, so it', 'has a rule, a hook and a replay, and the',
      'constraint outlives the run that', 'produced it (Post 10).']],
  ];
  SAID.forEach((c) => {
    els.push(...card(c[0], 338, 430, 142, { spine: c[1], strokeWidth: 1.4 }));
    els.push(text(c[0] + 18, 346, c[2], { size: 10, stroke: c[1] }));
    els.push(text(c[0] + 18, 368, fit(c[3], 11, 394, 'said'), { size: 11, stroke: T.ink }));
    if (c[0] === 490) {
      els.push(text(508, 384, 'without a stop condition"', { size: 11, stroke: T.ink }));
    }
    els.push(rule(c[0] + 18, c[0] + 412, 404));
    c[4].forEach((l, i) => els.push(text(c[0] + 18, 414 + i * 14, fit(l, 9, 394, 'said gloss'),
      { size: 9, stroke: T.inkMuted })));
  });

  els.push(text(40, 500, 'Observability is worthless if it stops at a dashboard.', { size: 11.5, stroke: T.ink }));
  els.push(text(40, 522, 'The loop closes only when the trace becomes a rule, a hook, and a replay.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'One trace localised to a component and converted into three constraints',
    desc: 'A hand-drawn figure in three panels. The first, trace, shows a root agent run span with a '
      + 'flagged sub-agent span beneath it that ran thirty iterations, produced no new files, never '
      + 'exited on its own, and was eventually killed by the budget ceiling; the span is the '
      + 'symptom. The second, localise, names the failing component: no-progress detection was '
      + 'missing inside the sub-agent own loop, which is not a model bug but a stop-condition bug, '
      + 'a named harness fault. The third, ratchet, converts that one failure into three durable '
      + 'constraints: a rule capping sub-agent iterations in the memory file, a hook whose '
      + 'no-progress detector kills a stalled loop, and a replay adding this trace to the '
      + 'regression set. A second tier sets the same run described two ways. Without a trace it is "the agent is flaky": a complaint that names no component, so there is nothing to fix and nothing to ratchet, and the next run fails the same way with the same explanation. With a trace it is "iteration 14 sub-agent looped without a stop condition": a bug whose component is named, so it has a rule, a hook and a replay, and the constraint outlives the run that produced it. Captions record that observability is worthless if it stops at a '
      + 'dashboard, and that the loop closes only when the trace becomes a rule, a hook, and a '
      + 'replay.',
  };
}

// ---------------------------------------------------------------- diagram 3
function traceShapes() {
  resetSeq();
  const W = 960, H = 470;

  const els = [...heading('What a failure looks like in the shape of a run',
    'A healthy run has a recognisable geometry. Each named failure mode deforms it in its own way, before you read a single label.')];

  els.push(...card(40, 96, 880, 96, { spine: T.success, strokeWidth: 1.4 }));
  els.push(text(58, 104, 'HEALTHY: even iterations, alternating calls, gently rising tokens, and a gate at the end',
    { size: 9, stroke: T.success }));
  [['agent.run', 200, 860, T.ink], ['iteration 1', 210, 410, T.primary],
   ['iteration 2', 416, 616, T.primary], ['iteration 3', 622, 800, T.primary],
   ['verify.gate', 806, 860, T.success]].forEach((s, i) => {
    const y = 124 + i * 13;
    els.push(text(58, y - 1, s[0], { size: 8, family: MONO, stroke: T.inkMuted }));
    els.push(rect(s[1], y, s[2] - s[1], 9, { stroke: s[3], fill: T.neutral1, strokeWidth: 1 }));
  });

  const panel = (x, tint, name, draw, tell) => {
    const out = card(x, 212, 210, 180, { spine: tint, strokeWidth: 1.4 });
    out.push(text(x + 16, 220, name, { size: 10, stroke: tint }));
    out.push(...draw(x + 16));
    tell.forEach((l, i) => out.push(text(x + 16, 340 + i * 14,
      fit(l, 8.5, 178, 'tell'), { size: 8.5, stroke: T.inkMuted })));
    return out;
  };
  const bar = (x, y, w, tint) => rect(x, y, w, 7, { stroke: tint, fill: T.neutral1, strokeWidth: 1 });

  els.push(...panel(40, T.alert, 'DOOM LOOP', (x) => {
    const out = [];
    for (let i = 0; i < 7; i++) out.push(bar(x, 246 + i * 12, 122, T.warn));
    return out;
  }, ['the same two spans repeating,', 'no gate span at the end, and', 'token counts still climbing']));

  els.push(...panel(264, T.alert, 'CONTEXT ANXIETY', (x) => {
    const out = [];
    [30, 54, 84, 120, 26].forEach((w, i) => out.push(bar(x, 250 + i * 16, w, i === 4 ? T.alert : T.warn)));
    return out;
  }, ['per-call tokens climb steeply,', 'then one rushed final iteration', 'as the window nears its limit']));

  els.push(...panel(488, T.alert, 'VICTORY DECLARATION', (x) => [
    bar(x, 254, 120, T.warn), bar(x, 274, 110, T.warn),
    rect(x, 300, 90, 18, { stroke: T.alert, strokeWidth: 1.4, strokeStyle: 'dashed' }),
    text(x + 96, 304, 'no gate span', { size: 8, stroke: T.alert }),
  ], ['a short run, and the absence', 'of the gate is the whole tell:', 'nothing checked the work']));

  els.push(...panel(712, T.alert, 'LATENCY OUTLIER', (x) => {
    const out = [];
    [40, 150, 44, 38, 42].forEach((w, i) => out.push(bar(x, 250 + i * 16, w, i === 1 ? T.alert : T.warn)));
    return out;
  }, ['one bar far wider than its', 'siblings: a genuinely slow tool,', 'or a timeout set too generously']));

  els.push(text(40, 412, 'Failures deform the shape in characteristic ways, and learning to read them is most of the skill.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 434, 'The tree turns a felt impression into a visible geometry.', { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 456, 'You stop arguing about whether the agent seems slow, and point at the wide bar.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A healthy trace shape beside four characteristic deformations',
    desc: 'A hand-drawn figure. Across the top, a healthy run: even iterations, alternating calls, '
      + 'gently rising tokens, and a verify gate at the end. Below, four failure shapes. A doom '
      + 'loop is drawn as the same two spans repeating identically down the panel, with no gate '
      + 'span at the end and token counts still climbing. Context anxiety is drawn as bars whose '
      + 'widths climb steeply and then a short rushed final iteration as the window nears its '
      + 'limit. A victory declaration is drawn as two short iterations followed by a dashed empty '
      + 'slot labelled no gate span, since the absence of the gate is the whole tell and nothing '
      + 'checked the work. A latency outlier is drawn as five bars of which one is far wider than '
      + 'its siblings, meaning a genuinely slow tool or a timeout set too generously. Captions '
      + 'record that failures deform the shape in characteristic ways and that learning to read '
      + 'them is most of the skill, that the tree turns a felt impression into a visible geometry, '
      + 'and that you stop arguing about whether the agent seems slow and point at the wide bar '
      + 'instead.',
  };
}

module.exports = { traceTree, traceToRatchet, traceShapes };

if (require.main === module) {
  emit('01-trace-tree', traceTree());
  emit('02-trace-to-ratchet', traceToRatchet());
  emit('03-trace-shapes', traceShapes());
}
