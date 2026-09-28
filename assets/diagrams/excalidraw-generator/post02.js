// The post 02 diagrams, hand-drawn.
//
//   01-harness-anatomy      960 x 560  Mirror of the existing figure.
//   02-layered-harness      960 x 624  Mirror, rebuilt denser.
//   03-prebuilt-vs-custom   960 x 628  NEW, published: section 9 had no figure.
//
// Section 9 carries the post's most practical claim -- that most of the map is
// inherited and the leverage sits in the custom layer -- and it was running on
// two bullet points. The third scene draws it, and draws the part the prose only
// implies: three components appear on both sides, because the harness ships the
// machinery and you supply the policy. It closes on the three ownership
// questions the section states and the figure previously left in the prose.

const { T, rect, ellipse, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, wrap, card, rule } = require('./scaffold');

// Neighbourhood colour for a component badge, the same key the first figure
// uses: blue feeds the model, green governs it, orange is the scale tier, and
// the loop at the core is ink.
const NEIGH = {
  '01': T.ink,
  '02': T.primary, '03': T.primary, '04': T.primary, '05': T.primary,
  '06': T.success, '07': T.success, '08': T.success, '11': T.success,
  '09': T.warn, '10': T.warn,
};

// A small numbered badge on a filled chip. Ink fills need the light text
// colour; every other tint carries dark ink.
function badge(x, y, num, tint, w = 24, h = 17, size = 10) {
  return [
    rect(x, y, w, h, { stroke: tint, fill: tint, strokeWidth: 1 }),
    text(x, y + 2, num, {
      size, align: 'center', width: w, stroke: tint === T.ink ? T.onFill : T.onAccent,
    }),
  ];
}

// A numbered component card: badge, name, and two lines of gloss.
function comp(x, y, w, h, num, name, l1, l2, tint) {
  const els = card(x, y, w, h, { spine: tint });
  els.push(rect(x + 16, y + 10, 24, 17, { stroke: tint, fill: tint, strokeWidth: 1 }));
  els.push(text(x + 16, y + 12, num, { size: 10, align: 'center', width: 24, stroke: T.onAccent }));
  els.push(text(x + 48, y + 9, fit(name, 12.5, w - 64, 'name ' + num), { size: 12.5, stroke: T.ink }));
  els.push(text(x + 16, y + 34, fit(l1, 9.5, w - 32, 'gloss ' + num), { size: 9.5, stroke: T.inkMuted }));
  els.push(text(x + 16, y + 50, fit(l2, 9.5, w - 32, 'gloss ' + num), { size: 9.5, stroke: T.inkMuted }));
  return els;
}

// ---------------------------------------------------------------- diagram 1
function anatomy() {
  resetSeq();
  const W = 960, H = 560;

  const els = [...heading('The anatomy of a harness',
    'Eleven components around one core. Naming the failing component is most of the work of fixing it.')];

  els.push(text(40, 78, 'FEEDS THE MODEL - WHAT IT KNOWS AND CAN DO', { size: 10, stroke: T.primary }));
  els.push(text(328, 78, 'THE LOOP - THE CORE', { size: 10, stroke: T.ink }));
  els.push(text(648, 78, 'GOVERNS IT - LIMITS AND EVIDENCE', { size: 10, stroke: T.success }));

  const FEEDS = [
    ['02', 'Tools & code execution', 'bash and code beat fifty bespoke tools;', 'schemas, skills, MCP dispatch'],
    ['03', 'State & filesystem', 'durable memory outside the window;', 'git for versioning and rollback'],
    ['04', 'Context management', 'compaction, tool-output offloading,', 'resets, against context rot'],
    ['05', 'Memory & learning', 'carry knowledge across sessions;', 'the ratchet principle'],
  ];
  FEEDS.forEach((c, i) => els.push(...comp(40, 96 + i * 78, 272, 70, c[0], c[1], c[2], c[3], T.primary)));

  const GOVERNS = [
    ['06', 'Verification', 'check each step; fail fast before', 'errors compound'],
    ['07', 'Hooks & enforcement', 'deterministic rules the model', 'cannot be trusted to keep'],
    ['08', 'Permissions & sandbox', 'bound the blast radius;', 'isolate execution'],
    ['11', 'Observability', 'a trace per run; see it, then fix', 'the failing component'],
  ];
  GOVERNS.forEach((c, i) => els.push(...comp(648, 96 + i * 78, 272, 70, c[0], c[1], c[2], c[3], T.success)));

  // The core.
  els.push(...card(328, 96, 304, 304, { spine: T.ink, strokeWidth: 1.6 }));
  els.push(rect(346, 106, 24, 17, { stroke: T.ink, fill: T.ink, strokeWidth: 1 }));
  els.push(text(346, 108, '01', { size: 10, align: 'center', width: 24, stroke: T.onFill }));
  els.push(text(378, 105, 'The agent loop', { size: 13, stroke: T.ink }));

  els.push(ellipse(442, 208, 76, 60, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.4 }));
  els.push(text(442, 228, 'MODEL', { size: 12, align: 'center', width: 76, stroke: T.ink }));

  const step = (x, y, w, label) => [
    rect(x, y, w, 28, { stroke: T.ink, strokeWidth: 1.3 }),
    text(x, y + 6, label, { size: 11.5, align: 'center', width: w, stroke: T.ink }),
  ];
  els.push(...step(430, 142, 100, 'REASON'));
  els.push(...step(548, 224, 66, 'ACT'));
  els.push(...step(346, 224, 84, 'OBSERVE'));

  els.push(arrow([[532, 158], [562, 168], [578, 220]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[562, 254], [480, 282], [428, 256]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[378, 222], [384, 178], [426, 160]], { stroke: T.inkMuted, strokeWidth: 1.3 }));

  els.push(rule(346, 614, 296));
  els.push(text(346, 306, 'STOPS WHEN', { size: 9, stroke: T.inkSubtle }));
  els.push(text(346, 322, 'goal verified - max iterations -', { size: 10.5, stroke: T.ink }));
  els.push(text(346, 338, 'budget spent - no progress', { size: 10.5, stroke: T.ink }));
  els.push(text(346, 364, '(most agent bugs live here)', { size: 10.5, stroke: T.inkMuted }));

  els.push(text(40, 410, 'OPERATES AT LARGER SCALE - MANY AGENTS, OR MANY WINDOWS', { size: 10, stroke: T.warn }));
  els.push(...comp(40, 428, 440, 72, '09', 'Orchestration',
    'coordinate many agents as units, one level up from', 'a single-agent harness; and when not to', T.warn));
  els.push(...comp(496, 428, 424, 72, '10', 'Long-horizon patterns',
    'Ralph loops and context bridging, for work that', 'outgrows a single window', T.warn));

  els.push(text(40, 522,
    'Blue feeds the model, green governs it, orange works at larger scale. The numbers index the eleven components and the posts that cover them.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The eleven components of a harness, arranged around the agent loop',
    desc: 'A hand-drawn map of a harness. At the centre sits component one, the agent loop: a '
      + 'model in the middle with reason, act and observe cycling around it, and a note that the '
      + 'loop stops when the goal is verified, the maximum iterations are reached, the budget is '
      + 'spent, or no progress is being made, with the remark that most agent bugs live here. Down '
      + 'the left, four components feed the model: tools and code execution, where bash and code '
      + 'beat fifty bespoke tools; state and filesystem, durable memory outside the window with git '
      + 'for versioning and rollback; context management, meaning compaction, tool-output '
      + 'offloading and resets against context rot; and memory and continual learning, carrying '
      + 'knowledge across sessions through the ratchet principle. Down the right, four components '
      + 'govern it: verification, which checks each step before errors compound; hooks and '
      + 'enforcement, deterministic rules the model cannot be trusted to keep; permissions and '
      + 'sandbox, which bound the blast radius; and observability, a trace per run that localises '
      + 'the failing component. Along the bottom, two components work at larger scale: '
      + 'orchestration, coordinating many agents as units, and long-horizon patterns such as Ralph '
      + 'loops for work that outgrows a single window.',
  };
}

// ---------------------------------------------------------------- diagram 2
function layered() {
  resetSeq();
  const W = 960, H = 636;

  const els = [...heading('A mature harness, decoded',
    'The same component map, regrouped as the layers of a shipping system (Claude Code, after Osmani, 2026).')];

  els.push(text(92, 74, 'LAYER', { size: 9.5, stroke: T.inkSubtle }));
  els.push(text(324, 74, 'WHAT IT HOLDS', { size: 9.5, stroke: T.inkSubtle }));
  els.push(text(666, 74, 'COMPONENTS FROM THE MAP', { size: 9.5, stroke: T.inkSubtle }));

  // Band name, gloss, the two lines of parts, the component badges the band
  // covers, a gloss on that mapping, and the band's neighbourhood colour.
  const LAYERS = [
    ['INPUT', 'what the user and the world send in',
      'UI - sessions', 'permission gates', ['08'],
      'the gate is 08; a UI is not required', T.success],
    ['KNOWLEDGE', 'what the model knows this turn',
      'skills - context compaction', 'task state - memory', ['02', '03', '04', '05'],
      'all four feeds-the-model components', T.primary],
    ['INTEGRATION', 'capabilities from elsewhere',
      'MCP runtime', 'external servers', ['02'],
      'component 02, extended at runtime (Post 07)', T.primary],
    ['EXECUTION', 'how a turn actually runs',
      'tool dispatch - streaming runtime', 'prompt caching', ['01', '02'],
      'the loop, plus the wiring that runs a call', T.ink],
    ['OBSERVABILITY', 'seeing what happened afterwards',
      'event bus', 'background execution', ['11'],
      'a trace per run, and why the loop stopped', T.success],
    ['MULTI-AGENT', 'many agents at once',
      'sub-agent coordination', 'worktree isolation', ['09'],
      'the scale tier: agents coordinated as units', T.warn],
  ];

  LAYERS.forEach((l, i) => {
    const y = 96 + i * 65;
    els.push(...card(40, y, 880, 57, { spine: l[6] }));
    els.push(...badge(54, y + 11, String(i + 1), l[6], 26, 19, 11));
    els.push(text(92, y + 6, fit(l[0], 13.5, 208, 'layer name'), { size: 13.5, stroke: l[6] }));
    els.push(text(92, y + 29, fit(l[1], 9.5, 208, 'layer gloss'), { size: 9.5, stroke: T.inkMuted }));
    els.push(line([[308, y + 9], [308, y + 48]], { stroke: T.border, strokeWidth: 1, roughness: 0.3 }));
    els.push(text(324, y + 7, fit(l[2], 10.5, 316, 'holds line 1'), { size: 10.5, stroke: T.ink }));
    els.push(text(324, y + 28, fit(l[3], 10.5, 316, 'holds line 2'), { size: 10.5, stroke: T.ink }));
    els.push(line([[650, y + 9], [650, y + 48]], { stroke: T.border, strokeWidth: 1, roughness: 0.3 }));
    l[4].forEach((n, k) => els.push(...badge(666 + k * 30, y + 6, n, NEIGH[n])));
    els.push(text(666, y + 30, fit(l[5], 9, 242, 'map gloss'), { size: 9, stroke: T.inkMuted }));
  });

  // What the banding costs, said plainly, so the figure is not read as
  // architecture it is not.
  // The notes are deliberately uncoloured: every tint elsewhere in this figure
  // means a neighbourhood, and these are remarks about the banding, not parts.
  const NOTES = [
    ['SEVEN LAYERS, SIX BANDS',
      'The source estimate names an output layer too, which streams and formats the result '
      + 'back. It folds into execution here: the two share one path.'],
    ['EIGHT OF THE ELEVEN COMPONENTS',
      'Verification (06), hooks (07) and long-horizon patterns (10) are headings nowhere '
      + 'in this cut: banding is one observer\'s reading, not the parts list.'],
    ['AN ESTIMATE, NOT ARCHITECTURE',
      'Fareed Khan\'s breakdown of Claude Code, which Osmani (2026) reports and explicitly '
      + 'labels an estimate rather than published architecture.'],
  ];
  NOTES.forEach((n, i) => {
    const x = 40 + i * 300;
    els.push(...card(x, 492, 280, 88, { spine: T.neutral3 }));
    els.push(text(x + 18, 501, fit(n[0], 9.5, 244, 'note head'), { size: 9.5, stroke: T.ink }));
    els.push(text(x + 18, 518, wrap(n[1], 9.5, 244, 4), { size: 9.5, stroke: T.inkMuted }));
  });

  els.push(text(40, 588,
    'Not a monolith with a clever prompt inside: the same eleven components, wired into layers. Read top-down, surface to base.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 608,
    'Badge colour is the neighbourhood, as in the first figure: blue feeds the model, green governs it, orange is the scale tier, ink is the loop.',
    { size: 10, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A mature harness decoded into six stacked layers, each mapped back to the component map',
    desc: 'A hand-drawn stack of six labelled bands, read from the top down. Each band gives what '
      + 'it holds and which numbered components of the eleven-part map it covers. One, input: what '
      + 'the user and the world send in, holding the user interface, sessions and permission gates, '
      + 'and covering component 08, the permission gate, with the note that a user interface is not '
      + 'required of a harness. Two, knowledge: what the model knows this turn, holding skills, '
      + 'context compaction, task state and memory, and covering components 02, 03, 04 and 05, all '
      + 'four of the components that feed the model. Three, integration: capabilities from '
      + 'elsewhere, holding the Model Context Protocol runtime and external servers, and covering '
      + 'component 02 extended at runtime. Four, execution: how a turn actually runs, holding tool '
      + 'dispatch, the streaming runtime and prompt caching, and covering components 01 and 02, the '
      + 'loop plus the wiring that runs a call. Five, observability: seeing what happened '
      + 'afterwards, holding an event bus and background execution, and covering component 11, a '
      + 'trace per run and why the loop stopped. Six, multi-agent: many agents at once, holding '
      + 'sub-agent coordination and worktree isolation, and covering component 09, the scale tier. '
      + 'Three notes close the figure. The source estimate names seven layers where six are drawn '
      + 'here, because output folds into execution. Only eight of the eleven components appear at '
      + 'all: verification, hooks and long-horizon patterns are headings nowhere in this cut, '
      + 'because banding is one observer\'s reading rather than the parts list. And the whole '
      + 'decomposition is Fareed Khan\'s breakdown, which Osmani reports and explicitly labels an '
      + 'estimate rather than published architecture. A closing line records that a shipping '
      + 'harness is not a monolith with a clever prompt inside, it is the same eleven components '
      + 'wired into layers.',
  };
}

// ---------------------------------------------------------------- diagram 3
function prebuiltVsCustom() {
  resetSeq();
  const W = 960, H = 634;

  const els = [...heading('Prebuilt versus custom: which parts you actually build',
    'Most of the map is inherited. The leverage, and most of the reliability, sits in the layer you add.')];

  els.push(text(40, 84, 'PREBUILT - WHAT THE TOOL OR SDK SHIPS', { size: 10, stroke: T.primary }));
  els.push(text(502, 84, 'CUSTOM - WHAT YOUR TEAM ADDS ON TOP', { size: 10, stroke: T.accent }));

  els.push(...card(40, 100, 418, 308, { spine: T.primary }));
  els.push(...card(502, 100, 418, 308, { spine: T.accent }));

  // The seam between them: a component can sit on both sides.
  els.push(line([[480, 100], [480, 408]], { stroke: T.inkSubtle, strokeWidth: 1.2, strokeStyle: 'dashed' }));

  const row = (x, y, num, name, gloss, tint) => [
    ...badge(x + 16, y, num, tint),
    text(x + 48, y - 1, fit(name, 11.5, 350, 'row name'), { size: 11.5, stroke: T.ink }),
    text(x + 16, y + 20, fit(gloss, 9, 386, 'row gloss'), { size: 9, stroke: T.inkMuted }),
  ];

  const LEFT = [
    ['01', 'The agent loop', 'reason, act, observe, and the conditions it stops on'],
    ['02', 'Tool dispatch', 'the wiring that turns a requested call into a real one'],
    ['04', 'Context management', 'when it compacts, and what it decides to drop'],
    ['07', 'A hook system', 'the lifecycle points a rule is allowed to attach to'],
    ['08', 'A permission model', 'the prompt, the allow-list, and the gate itself'],
    ['11', 'A trace format', 'the spans, tokens and timings it chooses to record'],
  ];
  LEFT.forEach((r, i) => els.push(...row(40, 116 + i * 42, r[0], r[1], r[2], T.primary)));

  const RIGHT = [
    ['05', 'Your memory file', 'the conventions this project actually holds to'],
    ['02', 'Your tools', 'the capabilities your domain needs and nobody prebuilt'],
    ['22', 'Your evals', 'the fixed task set that says whether a change helped'],
    ['07', 'Your enforcement hooks', 'the rules you will not leave to the model judgement'],
    ['08', 'Your sandbox policy', 'what this particular task is allowed to touch'],
  ];
  RIGHT.forEach((r, i) => els.push(...row(502, 116 + i * 42, r[0], r[1], r[2], T.accent)));

  // Rows 2, 4 and 5 line up across the seam on purpose.
  [158, 242, 284].forEach((y) => {
    els.push(arrow([[460, y + 8], [500, y + 8]], { stroke: T.inkMuted, strokeWidth: 1.2 }));
  });

  els.push(rule(56, 442, 366));
  els.push(text(56, 374,
    wrap('You inherit all six. What a vendor ships is the mechanism; the policy that runs on it is never in the box.',
      9.5, 386, 2), { size: 9.5, stroke: T.inkMuted }));

  els.push(rule(518, 904, 330));
  els.push(text(518, 338,
    wrap('This is where most of the reliability lives, and no vendor can ship it for you. '
      + 'Hearing that a team uses an SDK answers far less about a system than it sounds like it '
      + 'does: the mechanism is inherited, the policy is yours.',
      9.5, 386, 4), { size: 9.5, stroke: T.inkMuted }));

  els.push(text(360, 414, 'same component, two owners',
    { size: 9.5, align: 'center', width: 240, stroke: T.inkMuted }));

  els.push(text(40, 440, 'THREE QUESTIONS THAT SETTLE OWNERSHIP FOR ANY COMPONENT ON THE MAP',
    { size: 10, stroke: T.ink }));

  const Q = [
    ['1', 'Does the mechanism differ between tasks inside your organisation?',
      'If not, inherit it. Nobody\'s reason-act-observe loop is special enough to justify writing one.',
      'INHERIT THE MECHANISM', T.primary],
    ['2', 'Would getting it wrong fail silently?',
      'If yes, own the policy and test it. A permission set that is too broad emits no error; '
      + 'neither does a hook that never fires.',
      'OWN IT AND TEST IT', T.accent],
    ['3', 'Could a competitor copy it from your public documentation?',
      'If yes, it is prebuilt in all but name. If not, it is custom by definition: your '
      + 'conventions, your evals, your rules.',
      'CUSTOM BY DEFINITION', T.accent],
  ];
  Q.forEach((q, i) => {
    const x = 40 + i * 300;
    els.push(...card(x, 458, 280, 112, { spine: q[4] }));
    els.push(...badge(x + 16, 469, q[0], q[4], 22, 17, 10));
    els.push(text(x + 46, 467, wrap(q[1], 11, 216, 2), { size: 11, stroke: T.ink }));
    els.push(text(x + 16, 500, wrap(q[2], 9.5, 246, 3), { size: 9.5, stroke: T.inkMuted }));
    els.push(rule(x + 16, x + 264, 544));
    els.push(text(x + 16, 550, fit(q[3], 11, 246, 'verdict'), { size: 11, stroke: q[4] }));
  });

  els.push(text(40, 584,
    'Tools (02), hooks (07) and permissions (08) appear on both sides. The harness ships the machinery; you supply the policy it runs.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 606,
    'So harness engineering is rarely writing a loop. It is choosing a prebuilt harness well, then building the custom layer that makes it trustworthy.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Prebuilt harness versus custom layer, with three components on both sides and the three questions that settle ownership',
    desc: 'A hand-drawn two-column figure divided by a dashed seam. The left column, prebuilt, is '
      + 'what a tool or SDK ships: the agent loop with the conditions it stops on; tool dispatch, '
      + 'the wiring that turns a requested call into a real one; context management, meaning when '
      + 'it compacts and what it drops; a hook system, the lifecycle points a rule may attach to; a '
      + 'permission model, the prompt, the allow-list and the gate; and a trace format, the spans, '
      + 'tokens and timings it records. A footnote under that column records that you inherit all '
      + 'six, and that what a vendor ships is the mechanism while the policy that runs on it is '
      + 'never in the box. The right column, custom, is what your team adds: your memory file, '
      + 'holding the conventions the project actually keeps; your tools, the capabilities your '
      + 'domain needs and nobody prebuilt; your evals, the fixed task set that says whether a '
      + 'change helped; your enforcement hooks, the rules you will not leave to the model '
      + 'judgement; and your sandbox policy, what this particular task may touch. Its footnote '
      + 'records that this is where most of the reliability lives, that no vendor can ship it for '
      + 'you, and that hearing a team uses an SDK answers far less about a system than it sounds '
      + 'like it does. Three short arrows cross the seam, pairing tools, hooks and permissions '
      + 'with their custom counterparts under the label same component, two owners. Below, three '
      + 'panels give the questions that settle ownership for any component on the map. One: does '
      + 'the mechanism differ between tasks inside your organisation? If not, inherit it, because '
      + 'nobody\'s reason-act-observe loop is special enough to justify writing one, so the verdict '
      + 'is inherit the mechanism. Two: would getting it wrong fail silently? If yes, own the '
      + 'policy and test it, because a permission set that is too broad emits no error and neither '
      + 'does a hook that never fires, so the verdict is own it and test it. Three: could a '
      + 'competitor copy it from your public documentation? If yes it is prebuilt in all but name, '
      + 'and if not it is custom by definition: your conventions, your evals, your rules. The '
      + 'closing lines record the consequence: the harness ships the machinery and you supply the '
      + 'policy it runs, so harness engineering is rarely writing a loop but choosing a prebuilt '
      + 'harness well and then building the custom layer that makes it trustworthy.',
  };
}

module.exports = { anatomy, layered, prebuiltVsCustom };

if (require.main === module) {
  emit('01-harness-anatomy', anatomy());
  emit('02-layered-harness', layered());
  emit('03-prebuilt-vs-custom', prebuiltVsCustom());
}
