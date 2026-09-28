// The post 16 diagrams, hand-drawn.
//
//   01-topologies-gallery      960 x 632  Mirror of the existing figure, densified.
//   02-orchestration-decision  960 x 620  Mirror, densified.
//   03-the-coordination-tax    960 x 470  NEW, published: section 5 had no figure.
//
// Section 5 exists because "coordination cost" gets asserted a lot and
// quantified rarely, and it is the section that decides whether a topology pays.
// Three small charts price the three costs the post names, using the post's own
// example numbers and nothing invented.
//
// Figures 1 and 2 were four schematics and one gate column on a wide, half-empty
// canvas. They now carry what the post's own tables already say: for each
// topology, Anthropic's name for the pattern, what it costs to debug, and a task
// from the section 5 table that fits it, over the workflow-to-agent axis that
// section 2 says the design actually turns on; and, beside the gates, the section
// 6 arithmetic that prices a "yes" -- token totals, the latency chart, and the
// published evidence on both sides. Every number in both figures is read from
// index.md; the token and latency figures are the post's own illustrative
// example and are labelled as such on the figure.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function topologies() {
  resetSeq();
  const W = 960, H = 632;

  const els = [...heading('Four topologies for arranging agents',
    'Same model, four shapes, and one axis: who writes the control flow. The right default is the top-left one.')];

  // Each panel is a schematic on the left and the post's own table on the right:
  // the pattern name from section 2, what it costs to debug, and a task from the
  // section 5 calibration table that actually fits the shape.
  const panel = (px, py, tint, name, gloss, pattern, debug, ex) => {
    const out = card(px, py, 420, 198, { spine: tint, strokeWidth: 1.3 });
    out.push(text(px + 18, py + 12, name, { size: 12.5, stroke: T.ink }));
    out.push(text(px + 18, py + 31, fit(gloss, 9, 384, 'topology gloss'), { size: 9, stroke: T.inkMuted }));
    out.push(rule(px + 16, px + 404, py + 48));
    out.push(text(px + 218, py + 56, "ANTHROPIC'S NAME FOR IT", { size: 8, stroke: T.inkSubtle }));
    pattern.forEach((l, i) => out.push(
      text(px + 218, py + 70 + i * 14, fit(l, 10, 186, 'pattern name'), { size: 10, stroke: tint })));
    out.push(text(px + 218, py + 102, 'WHAT IT COSTS TO DEBUG', { size: 8, stroke: T.inkSubtle }));
    debug.forEach((l, i) => out.push(
      text(px + 218, py + 116 + i * 13, fit(l, 9, 186, 'debug cost'), { size: 9, stroke: T.ink })));
    out.push(rule(px + 16, px + 404, py + 146));
    out.push(text(px + 16, py + 151, 'A TASK THAT FITS', { size: 8, stroke: T.inkSubtle }));
    ex.forEach((l, i) => out.push(
      text(px + 16, py + 164 + i * 14, fit(l, 10, 388, 'worked example'), { size: 10, stroke: T.ink })));
    return out;
  };

  const node = (x, y, w, h, s, o = {}) => [
    rect(x, y, w, h, { stroke: o.stroke ?? T.ink, fill: o.fill ?? T.surface, strokeWidth: 1.0 }),
    text(x, y + (h - (o.size ?? 8) * 1.25) / 2, s,
      { size: o.size ?? 8, align: 'center', width: w, stroke: o.stroke ?? T.ink }),
  ];

  // --- single agent
  els.push(...panel(40, 86, T.success, 'SINGLE AGENT',
    'one harness decomposes the task into sub-tasks it runs: the default',
    ['Agent'],
    ['one trace, one context:', 'the easiest case in the table'],
    ['Refactor one module. The decisions are interdependent,',
      'so splitting them is the Flappy Bird failure.']));
  els.push(...node(56, 158, 66, 40, 'AGENT', { fill: T.neutral1, size: 9.5 }));
  [0, 1, 2].forEach((i) => {
    els.push(...node(152, 144 + i * 26, 84, 20, 'sub-task'));
    els.push(line([[124, 178], [148, 154 + i * 26]], { stroke: T.inkMuted, strokeWidth: 1.0 }));
  });

  // --- orchestrator and workers
  els.push(...panel(500, 86, T.primary, 'ORCHESTRATOR AND WORKERS',
    'a lead decomposes, workers execute, and the lead synthesises',
    ['Parallelisation (sectioning),', 'or Orchestrator-workers'],
    ['N worker traces plus a merge;', 'most bugs live in the merge'],
    ['Summarise 100 documents. Read-only, so the summaries',
      'never have to agree with each other.']));
  els.push(...node(516, 160, 60, 36, 'LEAD', { fill: T.neutral1, size: 9.5 }));
  [0, 1, 2, 3].forEach((i) => {
    els.push(...node(608, 142 + i * 20, 84, 16, 'worker', { size: 7.5 }));
    els.push(line([[578, 178], [604, 150 + i * 20]], { stroke: T.inkMuted, strokeWidth: 1.0 }));
  });

  // --- pipeline
  els.push(...panel(40, 294, T.accent, 'PIPELINE',
    'agents in sequence: each one transforms the work and passes it on',
    ['Prompt chaining'],
    ['one trace per stage; a bad', 'output localises to a stage'],
    ['Draft, edit and fact-check one report. The stages are',
      'ordered and distinct, and one artefact runs through all.']));
  els.push(text(56, 352, fit('one artefact, three ordered stages', 8, 189, 'pipeline note'),
    { size: 8, stroke: T.inkMuted }));
  ['draft', 'edit', 'fact-check'].forEach((s, i) => {
    els.push(...node(56 + i * 66, 374, 52, 32, s));
    if (i) els.push(arrow([[46 + i * 66, 390], [54 + i * 66, 390]],
      { stroke: T.inkMuted, strokeWidth: 1.0 }));
  });

  // --- swarm
  els.push(...panel(500, 294, T.warn, 'SWARM ON A SHARED REPO',
    'peers coordinate through files, with no central lead at all (Post 17)',
    ['(no counterpart)'],
    ['per-agent traces, interleaved,', 'with no global ordering'],
    ['Fix 50 unrelated bugs in one repository. A write fan-out,',
      'so it pays only with claiming and worktrees (Post 17).']));
  els.push(...node(576, 382, 70, 26, 'repo / tasks', { fill: T.neutral1 }));
  [[516, 352, 566, 368, 592, 382], [516, 412, 566, 412, 592, 406],
    [654, 352, 654, 368, 632, 382], [654, 412, 654, 412, 632, 406]].forEach((p) => {
    els.push(...node(p[0], p[1], 50, 16, 'agent'));
    els.push(line([[p[2], p[3]], [p[4], p[5]]],
      { stroke: T.inkMuted, strokeWidth: 1.0, strokeStyle: 'dashed' }));
  });

  // --- the axis the design turns on, carrying the fifth row of the section 2
  //     table that the four panels cannot show: the re-planning lead.
  els.push(text(40, 504, 'WHO WRITES THE CONTROL FLOW: THE AXIS THE DESIGN ACTUALLY TURNS ON',
    { size: 9.5, stroke: T.inkSubtle }));
  els.push(text(500, 504, 'the crossing, not the agent count, is where runs stop reproducing',
    { size: 9.5, align: 'right', width: 420, stroke: T.inkMuted }));
  els.push(text(40, 520, fit('WORKFLOW: predefined code paths, cheap to bound, trace and reproduce', 9, 420, 'axis left'),
    { size: 9, stroke: T.primary }));
  els.push(text(500, 520, fit('AGENT: the model directs its own process, and the run stops reproducing', 9, 420, 'axis right'),
    { size: 9, align: 'right', width: 420, stroke: T.accent }));
  els.push(arrow([[40, 538], [920, 538]],
    { stroke: T.inkMuted, strokeWidth: 1.0, startArrowhead: 'arrow' }));

  const AXIS = [
    ['pipeline', 'the engineer, at design time', T.accent],
    ['orchestrator-worker', 'fixed plan: the engineer', T.primary],
    ['single agent', 'the model, in one owning loop', T.success],
    ['orchestrator-worker', 're-planning lead: the model', T.primary],
    ['swarm', 'nobody centrally: the repository', T.warn],
  ];
  AXIS.forEach((a, i) => {
    const x = 40 + i * 178;
    els.push(rect(x, 548, 168, 36, { stroke: a[2], fill: T.surface, strokeWidth: 1.0 }));
    els.push(text(x, 554, fit(a[0], 9.5, 156, 'axis chip'),
      { size: 9.5, align: 'center', width: 168, stroke: T.ink }));
    els.push(text(x, 569, fit(a[1], 8, 156, 'axis chip gloss'),
      { size: 8, align: 'center', width: 168, stroke: T.inkMuted }));
  });

  els.push(text(40, 594, 'Four shapes that exist, not four equally endorsed: Cognition (2026) calls the unstructured swarm "mostly a distraction".',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 612, 'Most systems that reach for a swarm needed a single agent with a bigger context, and most that build an orchestrator needed a pipeline.',
    { size: 10.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Four ways to arrange agents, each with its pattern name, debug cost and a task that fits',
    desc: 'A hand-drawn gallery of four topology cards over a control-flow axis. Single agent: one '
      + 'harness decomposing a task into sub-tasks it runs itself, drawn as one agent box feeding '
      + 'three sub-task chips; Anthropic calls it an agent; it costs one trace and one context to '
      + 'debug, the easiest case; the task that fits is refactoring one module, whose decisions are '
      + 'interdependent so splitting them is the Flappy Bird failure. Orchestrator and workers: a '
      + 'lead box feeding four worker chips; Anthropic calls it parallelisation by sectioning, or '
      + 'orchestrator-workers; debugging costs N worker traces plus a merge, and most bugs live in '
      + 'the merge; the task that fits is summarising 100 documents, read-only so the summaries '
      + 'never have to agree. Pipeline: draft, edit and fact-check boxes in a row joined by arrows; '
      + 'Anthropic calls it prompt chaining; one trace per stage, so a bad output localises to a '
      + 'stage; the task that fits is drafting, editing and fact-checking one report. Swarm on a '
      + 'shared repo: four peer agents joined by dashed lines to a central repo and task directory; '
      + 'it has no counterpart in the Anthropic taxonomy; per-agent traces interleave with no '
      + 'global ordering; the task that fits is fixing 50 unrelated bugs in one repository, a write '
      + 'fan-out that pays only with task claiming and worktrees from post 17. Beneath the cards a '
      + 'left-to-right axis runs from workflow, meaning predefined code paths that are cheap to '
      + 'bound, trace and reproduce, to agent, meaning the model directs its own process and the '
      + 'run stops reproducing. Five chips sit along it in order: pipeline, written by the engineer '
      + 'at design time; orchestrator-worker with a fixed plan, also the engineer; single agent, '
      + 'the model inside one owning loop; orchestrator-worker with a re-planning lead, the model '
      + 'at run time; and swarm, nobody centrally, the repository. Captions record that the '
      + 'crossing rather than the agent count is where runs stop reproducing, that these are four '
      + 'shapes that exist rather than four equally endorsed since Cognition in 2026 calls the '
      + 'unstructured swarm mostly a distraction, and that most systems reaching for a swarm needed '
      + 'a single agent with a bigger context while most that build an orchestrator needed a '
      + 'pipeline.',
  };
}

// ---------------------------------------------------------------- diagram 2
function decisionTree() {
  resetSeq();
  const W = 960, H = 620;

  const els = [...heading('Do you need orchestration?',
    'Three gates on the left. What a "yes" at the third one costs, priced, on the right.')];

  // --- left: the gates ------------------------------------------------------
  els.push(text(40, 84, 'THE THREE GATES', { size: 9.5, stroke: T.inkSubtle }));

  els.push(rect(120, 98, 220, 36, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.3 }));
  els.push(text(120, 108, 'START: a task to run', { size: 11.5, align: 'center', width: 220, stroke: T.ink }));
  els.push(arrow([[230, 136], [230, 150]], { stroke: T.inkMuted, strokeWidth: 1.3 }));

  const GATES = [
    [152, 'Independent parallel subtasks?', 'pieces that do not need each other context',
      'reads fan out freely; writes have to agree'],
    [232, 'Is the fragmentation acceptable?', 'each worker sees only its own slice',
      'conflicting implicit decisions: the Flappy Bird failure'],
    [312, 'Is the throughput worth the tax?', 'tokens, slowest-worker latency, partial failure',
      'priced on the right, from section 6'],
  ];
  GATES.forEach((g, i) => {
    els.push(rect(90, g[0], 340, 62, { stroke: T.primary, fill: T.surface, strokeWidth: 1.5 }));
    els.push(text(90, g[0] + 9, fit(g[1], 11.5, 316, 'gate'),
      { size: 11.5, align: 'center', width: 340, stroke: T.ink }));
    els.push(text(90, g[0] + 28, fit(g[2], 8.5, 316, 'gate gloss'),
      { size: 8.5, align: 'center', width: 340, stroke: T.inkMuted }));
    els.push(text(90, g[0] + 42, fit(g[3], 8.5, 316, 'gate detail'),
      { size: 8.5, align: 'center', width: 340, stroke: T.inkMuted }));
    if (i < 2) {
      els.push(arrow([[260, g[0] + 64], [260, g[0] + 78]], { stroke: T.success, strokeWidth: 1.3 }));
      els.push(text(268, g[0] + 64, 'yes', { size: 9, stroke: T.success }));
    }
    els.push(line([[88, g[0] + 31], [62, g[0] + 31]], { stroke: T.alert, strokeWidth: 1.3 }));
    els.push(text(64, g[0] + 16, 'no', { size: 9, stroke: T.alert }));
  });

  els.push(arrow([[62, 183], [62, 402]], { stroke: T.alert, strokeWidth: 1.3 }));

  els.push(rect(40, 406, 190, 62, { stroke: T.success, fill: T.surface, strokeWidth: 1.5 }));
  els.push(text(40, 416, 'SINGLE AGENT', { size: 12.5, align: 'center', width: 190, stroke: T.success }));
  els.push(text(40, 438, fit('one harness, sub-tasks inside', 8.5, 174, 'outcome'),
    { size: 8.5, align: 'center', width: 190, stroke: T.inkMuted }));
  els.push(text(40, 451, fit('and the whole task in one context', 8.5, 174, 'outcome'),
    { size: 8.5, align: 'center', width: 190, stroke: T.inkMuted }));

  els.push(arrow([[260, 376], [260, 404]], { stroke: T.success, strokeWidth: 1.3 }));
  els.push(text(268, 380, 'yes to all three', { size: 9, stroke: T.success }));
  els.push(rect(250, 406, 180, 62, { stroke: T.warn, fill: T.surface, strokeWidth: 1.5 }));
  els.push(text(250, 416, 'ORCHESTRATE', { size: 12.5, align: 'center', width: 180, stroke: T.warn }));
  els.push(text(250, 438, fit('orchestrator-worker,', 8.5, 164, 'outcome'),
    { size: 8.5, align: 'center', width: 180, stroke: T.inkMuted }));
  els.push(text(250, 451, fit('or a swarm (Post 17)', 8.5, 164, 'outcome'),
    { size: 8.5, align: 'center', width: 180, stroke: T.inkMuted }));

  // --- left, below: the two rules that make the framework harder to fool ----
  els.push(...card(40, 478, 420, 90, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(56, 486, 'TWO RULES THAT MAKE THE FRAMEWORK HARDER TO FOOL', { size: 9, stroke: T.inkSubtle }));
  [['Keep writes single-threaded unless you have the',
    'coordination machinery of Post 17 (Cognition, 2026).'],
  ['Settle the partial-failure policy in the same design',
    'session: fail the run, retry then degrade, or escalate.']].forEach((b, i) => {
    const by = 504 + i * 32;
    els.push(rect(56, by + 3, 7, 7, { stroke: T.success, fill: T.success, strokeWidth: 1.0 }));
    b.forEach((l, j) => els.push(
      text(72, by + j * 14, fit(l, 9.5, 372, 'rule'), { size: 9.5, stroke: j ? T.inkMuted : T.ink })));
  });

  // --- right: what a yes costs, priced from section 6 -----------------------
  els.push(text(480, 84, 'WHAT A "YES" AT THE THIRD GATE COSTS', { size: 9.5, stroke: T.inkSubtle }));

  els.push(...card(480, 98, 440, 146, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(496, 106, 'TOKENS: THE SAME WORK, PRICED THREE WAYS', { size: 9, stroke: T.primary }));
  els.push(text(496, 126, 'DESIGN', { size: 8, stroke: T.inkSubtle }));
  els.push(text(690, 126, 'INPUT TOKENS', { size: 8, align: 'right', width: 130, stroke: T.inkSubtle }));
  els.push(text(800, 126, 'VS SINGLE', { size: 8, align: 'right', width: 100, stroke: T.inkSubtle }));
  els.push(rule(496, 900, 139));
  const ROWS = [
    ['single agent', '14,000', '1.0x', T.success],
    ['lead + 4 workers, uncached', '42,000', '3.0x', T.alert],
    ['the same, shared prefix cached', '21,900', '~1.6x', T.warn],
  ];
  ROWS.forEach((r, i) => {
    const ry = 145 + i * 22;
    if (i) els.push(rule(496, 900, ry - 4));
    els.push(text(496, ry, fit(r[0], 9.5, 196, 'token row'), { size: 9.5, stroke: T.ink }));
    els.push(text(690, ry, r[1], { size: 9.5, align: 'right', width: 130, stroke: T.ink }));
    els.push(text(800, ry, r[2], { size: 9.5, align: 'right', width: 100, stroke: r[3] }));
  });
  els.push(text(496, 212, fit('Illustrative rather than a benchmark (section 6): a 6,000-token preamble,', 8, 408, 'token note'),
    { size: 8, stroke: T.inkMuted }));
  els.push(text(496, 224, fit('four 2,000-token slices, and a 4,000-token synthesis pass.', 8, 408, 'token note'),
    { size: 8, stroke: T.inkMuted }));

  els.push(...card(480, 254, 440, 162, { spine: T.warn, strokeWidth: 1.3 }));
  els.push(text(496, 262, 'LATENCY: THE MAXIMUM, NOT THE MEAN, PLUS SYNTHESIS', { size: 9, stroke: T.warn }));
  [['w1 10s', 35, 280], ['w2 10s', 35, 296], ['w3 10s', 35, 312], ['w4 10s', 35, 328],
    ['w5 90s', 315, 344]].forEach((b) => {
    els.push(text(496, b[2] - 1, b[0], { size: 8, stroke: T.inkMuted }));
    els.push(rect(544, b[2], b[1], 9, { stroke: T.ink, fill: T.neutral2, strokeWidth: 1.0 }));
  });
  els.push(text(496, 359, 'lead 5s', { size: 8, stroke: T.inkMuted }));
  els.push(rect(859, 360, 18, 9, { stroke: T.ink, fill: T.accent, strokeWidth: 1.0 }));
  els.push(text(612, 359, fit('the lead synthesis pass, on top of the maximum', 8, 240, 'synthesis note'),
    { size: 8, stroke: T.inkMuted }));
  els.push(line([[877, 274], [877, 375]], { stroke: T.alert, strokeWidth: 1.0, strokeStyle: 'dashed' }));
  els.push(text(620, 377, 'the run is not finished until here: 95s', { size: 8.5, stroke: T.alert }));
  els.push(text(496, 391, fit('95s against the 130s a single agent spends doing the same five', 8.5, 408, 'latency note'),
    { size: 8.5, stroke: T.ink }));
  els.push(text(496, 402, fit('pieces in sequence: five agents bought a 1.4x speed-up, not 5x.', 8.5, 408, 'latency note'),
    { size: 8.5, stroke: T.ink }));

  els.push(...card(480, 426, 440, 146, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(496, 434, 'THE PUBLISHED EVIDENCE, BOTH WAYS', { size: 9, stroke: T.accent }));
  const EV = [
    ['90.2%', T.success, 'a lead on Opus 4 with Sonnet 4 subagents beat single-agent',
      'Opus 4 on an internal research eval (Anthropic, 2025).'],
    ['15x', T.alert, 'the tokens of a chat interaction, for a multi-agent system;',
      'agents on their own use about 4x (Anthropic, 2025).'],
    ['80%', T.alert, 'of the variance on BrowseComp is explained by token usage',
      'alone, so part of what fan-out buys is spending more.'],
  ];
  EV.forEach((e, i) => {
    const ry = 454 + i * 36;
    els.push(text(496, ry, e[0], { size: 15, stroke: e[1] }));
    els.push(text(560, ry + 2, fit(e[2], 8.5, 344, 'evidence'), { size: 8.5, stroke: T.ink }));
    els.push(text(560, ry + 15, fit(e[3], 8.5, 344, 'evidence'), { size: 8.5, stroke: T.inkMuted }));
  });

  els.push(text(40, 584, 'The tax is paid on every run; the benefit only on the runs where the work really was parallel.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 602, 'Isolation is the one exception that skips the gates entirely, because what it buys is containment rather than throughput (Post 14).',
    { size: 10.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Three gates between a task and an orchestrated design, beside the priced cost of a yes',
    desc: 'A hand-drawn decision tree on the left, priced panels on the right. From a task to run, '
      + 'three gates in sequence. First, are there independent parallel subtasks, meaning pieces '
      + 'that do not need each other context, where reads fan out freely and writes have to agree. '
      + 'Second, is the fragmentation acceptable, given each worker sees only its own slice and '
      + 'conflicting implicit decisions produce the Flappy Bird failure. Third, is the throughput '
      + 'worth the tax of tokens, slowest-worker latency and partial failure. A no at any gate '
      + 'routes left and down to a single agent: one harness, sub-tasks inside, the whole task in '
      + 'one context. A yes to all three leads to orchestration, either orchestrator-worker or a '
      + 'swarm from post 17. Below the tree, two rules that make the framework harder to fool: keep '
      + 'writes single-threaded unless you have the coordination machinery of post 17, and settle '
      + 'the partial-failure policy in the same design session, choosing between failing the run, '
      + 'retrying then degrading, and escalating. On the right, three panels price a yes at the '
      + 'third gate. Tokens: a single agent reads 14,000 input tokens, a lead with four workers '
      + 'reads 42,000 uncached at three times the cost, and 21,900 with the shared prefix cached at '
      + 'about 1.6 times, all illustrative rather than a benchmark, from a 6,000-token preamble, '
      + 'four 2,000-token slices and a 4,000-token synthesis pass. Latency: four worker bars of ten '
      + 'seconds, one of ninety, and a lead synthesis bar of five seconds on top, with a dashed '
      + 'line marking that the run is not finished until 95 seconds, against the 130 seconds a '
      + 'single agent spends doing the same five pieces in sequence, so five agents bought a 1.4 '
      + 'times speed-up rather than a fivefold one. Published evidence, both ways: a lead on Opus 4 '
      + 'with Sonnet 4 subagents beat single-agent Opus 4 by 90.2 per cent on an internal research '
      + 'eval, while multi-agent systems use about 15 times the tokens of a chat interaction and '
      + 'agents about 4 times, and 80 per cent of the variance on BrowseComp is explained by token '
      + 'usage alone, so part of what fan-out buys is simply spending more. Captions record that '
      + 'the tax is paid on every run while the benefit is paid only on the runs where the work '
      + 'really was parallel, and that isolation is the one exception that skips the gates '
      + 'entirely because what it buys is containment rather than throughput.',
  };
}

// ---------------------------------------------------------------- diagram 3
function coordinationTax() {
  resetSeq();
  const W = 960, H = 470;

  const els = [...heading('The coordination tax, priced',
    'Three costs that decide whether a topology pays, and that the design usually assumes are smaller than they are.')];

  // --- tokens
  els.push(...card(40, 100, 280, 270, { spine: T.primary, strokeWidth: 1.4 }));
  els.push(text(56, 110, 'TOKENS MULTIPLY WITH', { size: 9, stroke: T.primary }));
  els.push(text(56, 124, 'AGENTS, NOT WITH WORK', { size: 9, stroke: T.primary }));

  els.push(text(56, 148, 'one agent', { size: 9.5, stroke: T.inkMuted }));
  els.push(rect(56, 162, 22, 24, { stroke: T.ink, fill: T.neutral2, strokeWidth: 1 }));
  els.push(rect(78, 162, 88, 24, { stroke: T.ink, fill: T.primary, strokeWidth: 1 }));

  els.push(text(56, 200, 'a lead and four workers', { size: 9.5, stroke: T.inkMuted }));
  els.push(rect(56, 214, 110, 24, { stroke: T.ink, fill: T.neutral2, strokeWidth: 1 }));
  els.push(rect(166, 214, 88, 24, { stroke: T.ink, fill: T.primary, strokeWidth: 1 }));

  els.push(rect(56, 252, 14, 12, { stroke: T.ink, fill: T.neutral2, strokeWidth: 1 }));
  els.push(text(76, 252, 'fixed per-agent overhead', { size: 8.5, stroke: T.inkMuted }));
  els.push(rect(56, 270, 14, 12, { stroke: T.ink, fill: T.primary, strokeWidth: 1 }));
  els.push(text(76, 270, 'the actual work, unchanged', { size: 8.5, stroke: T.inkMuted }));

  ['The overhead is paid whether the', 'slice was large or trivial, so fanning', 'a small task across many workers',
    'can cost several times more.'].forEach((l, i) => {
    els.push(text(56, 300 + i * 15, fit(l, 9, 248, 'token note'), { size: 9, stroke: T.ink }));
  });

  // --- latency
  els.push(...card(340, 100, 280, 270, { spine: T.warn, strokeWidth: 1.4 }));
  els.push(text(356, 110, 'LATENCY IS THE SLOWEST', { size: 9, stroke: T.warn }));
  els.push(text(356, 124, 'WORKER, PLUS SYNTHESIS', { size: 9, stroke: T.warn }));

  [18, 18, 18, 18, 160].forEach((w, i) => {
    const y = 150 + i * 20;
    els.push(rect(356, y, w, 14, { stroke: T.ink, fill: T.neutral2, strokeWidth: 1 }));
    els.push(text(356 + w + 6, y + 1, i === 4 ? '90s' : '10s', { size: 8, stroke: T.inkMuted }));
  });
  els.push(rect(516, 250, 36, 14, { stroke: T.ink, fill: T.accent, strokeWidth: 1 }));
  els.push(text(558, 251, 'synthesis', { size: 8, stroke: T.inkMuted }));
  els.push(line([[552, 146], [552, 272]], { stroke: T.alert, strokeWidth: 1.3, strokeStyle: 'dashed' }));
  els.push(text(400, 278, 'the run is not finished until here', { size: 8.5, stroke: T.alert }));

  ['Parallelism gives you the maximum,', 'not the average, and adds the lead',
    'synthesis pass on top: fan-out over', 'uneven work wins less than it looks.'].forEach((l, i) => {
    els.push(text(356, 300 + i * 15, fit(l, 9, 248, 'latency note'), { size: 9, stroke: T.ink }));
  });

  // --- partial failure
  els.push(...card(640, 100, 280, 270, { spine: T.alert, strokeWidth: 1.4 }));
  els.push(text(656, 110, 'A FAILED WORKER NEEDS', { size: 9, stroke: T.alert }));
  els.push(text(656, 124, 'A POLICY, AND RARELY HAS ONE', { size: 9, stroke: T.alert }));

  [0, 1, 2, 3, 4].forEach((i) => {
    const x = 656 + (i % 3) * 84;
    const y = 150 + Math.floor(i / 3) * 34;
    const bad = i === 4;
    els.push(rect(x, y, 76, 26, { stroke: bad ? T.alert : T.ink, fill: bad ? T.alert : T.surface, strokeWidth: 1.2 }));
    els.push(text(x, y + 8, bad ? 'FAILED' : 'w' + (i + 1),
      { size: 9, align: 'center', width: 76, stroke: bad ? T.onAccent : T.ink }));
  });
  els.push(arrow([[760, 214], [760, 234]], { stroke: T.inkMuted, strokeWidth: 1.2 }));
  els.push(rect(656, 238, 248, 34, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.3 }));
  els.push(text(656, 247, 'LEAD: four results and a hole', { size: 10, align: 'center', width: 248, stroke: T.ink }));

  ['- synthesise anyway?', '- retry the one that failed?', '- abandon the task?'].forEach((l, i) => {
    els.push(text(656, 286 + i * 16, l, { size: 9, stroke: T.ink }));
  });
  els.push(text(656, 338, 'Systems that never decided answer', { size: 9, stroke: T.inkMuted }));
  els.push(text(656, 352, 'the first one, by default.', { size: 9, stroke: T.inkMuted }));

  els.push(text(40, 390, 'None of these makes orchestration wrong. They are the bill the throughput has to cover.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 412, 'The point of naming them is that the bill is usually larger than the design assumed.',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 434, 'And fan out on reads freely: fifty agents summarising fifty documents make no decisions that have to agree.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Three priced costs of coordination: tokens, latency, and partial failure',
    desc: 'A hand-drawn figure in three panels. The first prices tokens: one agent is drawn as a '
      + 'small fixed-overhead segment plus a work segment, while a lead and four workers is drawn '
      + 'as five times the overhead plus exactly the same work, with the note that the overhead is '
      + 'paid whether the slice was large or trivial, so fanning a small task across many workers '
      + 'can cost several times more. The second prices latency: four worker bars of ten seconds '
      + 'and one of ninety, followed by a synthesis bar, with a dashed line marking that the run is '
      + 'not finished until after the synthesis, and the note that parallelism gives you the '
      + 'maximum rather than the average so fan-out over uneven work wins far less than the agent '
      + 'count suggests. The third prices partial failure: five worker chips of which one is marked '
      + 'failed, feeding a lead that holds four results and a hole, with three unanswered questions '
      + 'beneath it: synthesise anyway, retry the one that failed, or abandon the task, and the '
      + 'note that systems which never decided answer the first by default. Captions record that '
      + 'none of this makes orchestration wrong, that these are the bill the throughput has to '
      + 'cover, that the bill is usually larger than the design assumed, and that reads can be '
      + 'fanned out freely because fifty agents summarising fifty documents make no decisions that '
      + 'have to agree.',
  };
}

module.exports = { topologies, decisionTree, coordinationTax };

if (require.main === module) {
  emit('01-topologies-gallery', topologies());
  emit('02-orchestration-decision', decisionTree());
  emit('03-the-coordination-tax', coordinationTax());
}
