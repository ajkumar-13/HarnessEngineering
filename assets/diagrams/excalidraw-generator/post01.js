// The post 01 diagrams, hand-drawn.
//
//   01-three-eras     960 x 568  Published figure for section 1.
//   02-nested-rings   960 x 592  Published figure for section 3.
//   03-equation       960 x 524  Published figure for section 2.
//
// These three are the figures the post embeds, so each one carries the numbers
// the post actually states rather than a label standing in for them. Every
// figure here is dated or counted from the post's own prose: the provenance
// dates in section 2's table, the seven-symptom diagnostic table in section 4,
// and the Terminal-Bench and production figures in section 5. Nothing is
// estimated; where the post itself hedges a number ("reported", "about"), the
// hedge is drawn with it.

const { T, rect, ellipse, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, wrap, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function threeEras() {
  resetSeq();
  const W = 960, H = 568;

  const els = [...heading('Three eras of applied LLM engineering',
    'Each era engineers a larger surface than the last, because the last one stopped being the bottleneck.')];

  const ERAS = [
    { x: 40, years: '2022 - 2023', name: 'Prompt engineering',
      surface: 'one message', tint: T.accent, unit: 'a message', bottleneck: 'phrasing',
      body: 'You reword a single message until the answer improves. Nothing else is engineered.' },
    { x: 348, years: '2024 - 2025', name: 'Context engineering',
      surface: 'the whole window', tint: T.primary, unit: 'a window', bottleneck: 'information',
      body: 'You assemble everything the model reads on one call: tools, memory, retrieval, history.' },
    { x: 656, years: '2026 onward', name: 'Harness engineering',
      surface: 'the whole machine', tint: T.success, unit: 'a whole run', bottleneck: 'autonomy and control',
      body: 'You build the machine around the model: the loop, the tools, the verification, the guardrails.' },
  ];

  ERAS.forEach((e, i) => {
    els.push(...card(e.x, 88, 264, 232, { spine: e.tint, strokeWidth: i === 2 ? 1.5 : 1.3 }));
    els.push(text(e.x + 20, 96, e.years, { size: 10, stroke: T.inkSubtle }));
    els.push(text(e.x + 20, 114, fit(e.name, 14, 224, 'era name'), { size: 14, stroke: T.ink }));
    els.push(text(e.x + 20, 140, fit('surface: ' + e.surface, 11, 224, 'surface'),
      { size: 11, stroke: e.tint }));
    els.push(text(e.x + 20, 166, fit(wrap(e.body, 11, 224, 3), 11, 224, 'era body'),
      { size: 11, stroke: T.inkMuted }));
    els.push(rule(e.x + 20, e.x + 244, 220));
    els.push(text(e.x + 20, 228, 'UNIT OF WORK', { size: 9, stroke: T.inkSubtle }));
    els.push(text(e.x + 20, 242, fit(e.unit, 12, 224, 'unit'), { size: 12, stroke: T.ink }));
    els.push(rule(e.x + 20, e.x + 244, 268));
    els.push(text(e.x + 20, 276, 'BOTTLENECK', { size: 9, stroke: T.inkSubtle }));
    els.push(text(e.x + 20, 290, fit(e.bottleneck, 12, 224, 'bottleneck'), { size: 12, stroke: T.ink }));
    if (i) els.push(arrow([[e.x - 40, 204], [e.x - 8, 204]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  });

  // The surface each era engineers, drawn to scale across the same three columns.
  els.push(text(M, 334, 'THE SURFACE YOU ENGINEER', { size: 9, stroke: T.inkSubtle }));
  els.push(text(660, 334, fit('the harness has eleven components (Post 02)', 9, 260, 'components note'),
    { size: 9, stroke: T.inkSubtle }));
  els.push(rect(40, 350, 60, 26, { stroke: T.accent, strokeWidth: 1.3 }));
  els.push(text(108, 356, 'a message', { size: 10, stroke: T.inkMuted }));
  els.push(rect(348, 350, 170, 26, { stroke: T.primary, strokeWidth: 1.3 }));
  els.push(text(526, 356, 'a window', { size: 10, stroke: T.inkMuted }));
  els.push(rect(656, 350, 264, 26, { stroke: T.success, strokeWidth: 1.5 }));
  els.push(text(668, 356, fit('window, loop, tools, state, checks, guards', 10, 246, 'surface bar 3'),
    { size: 10, stroke: T.inkMuted }));

  // Dated provenance: every entry is an article the post cites by month.
  const MARKS = [
    { date: 'Dec 2024', tint: T.success,
      who: 'Anthropic: "Building Effective Agents", model plus loop' },
    { date: 'Jun 2025', tint: T.primary,
      who: 'Karpathy popularises "context engineering"' },
    { date: 'Sep 2025', tint: T.primary,
      who: 'Anthropic: "Effective context engineering for AI agents"' },
    { date: '10 Mar 2026', tint: T.success,
      who: 'Trivedy, LangChain: Agent = Model + Harness' },
    { date: 'Apr 2026', tint: T.success,
      who: 'Osmani popularises it; OpenAI makes it a discipline' },
  ];
  els.push(text(M, 396, 'WHEN EACH NAME LANDED, AND WHO LANDED IT', { size: 9, stroke: T.inkSubtle }));
  els.push(rule(40, 920, 434));
  MARKS.forEach((m, i) => {
    const x = 40 + i * 176;
    els.push(text(x, 412, fit(m.date, 10.5, 168, 'mark date'), { size: 10.5, stroke: m.tint }));
    els.push(line([[x + 4, 428], [x + 4, 440]], { stroke: m.tint, strokeWidth: 1.3 }));
    els.push(text(x, 446, fit(wrap(m.who, 9, 168, 2), 9, 168, 'mark who'),
      { size: 9, stroke: T.inkMuted }));
  });

  els.push(text(M, 496, 'Context engineering did not stop mattering. It became one component inside the larger surface.',
    { size: 12, stroke: T.ink }));
  els.push(text(M, 518, 'The name moved for the same reason both times: the thing that limited results moved.',
    { size: 12, stroke: T.inkMuted }));
  els.push(text(M, 540, fit('And the third era is the first you can measure: same model, same benchmark, 52.8% to 66.5% on harness changes alone.',
    12, 880, 'eras conclusion'), { size: 12, stroke: T.ink }));

  return {
    W, H, els,
    title: 'Three eras of applied LLM engineering, with the dates each name landed',
    desc: 'A hand-drawn timeline in three panels. Prompt engineering, 2022 to 2023, works on the '
      + 'surface of one message: you write a single message and reword it until the answer '
      + 'improves, the unit of work is a message, and the bottleneck is phrasing. Context '
      + 'engineering, 2024 to 2025, works on the whole window: you assemble everything the model '
      + 'reads on one call, including tools, memory, retrieval and history, the unit of work is a '
      + 'window, and the bottleneck is information. Harness engineering, 2026 onward, works on the '
      + 'whole machine: you build the loop, the tools, the verification and the guardrails around '
      + 'the model, the unit of work is a whole run, and the bottleneck is autonomy and control. '
      + 'Beneath the panels the surface each era engineers is drawn to scale, growing from a short '
      + 'bar marked a message, to a wider bar marked a window, to a full-width bar listing a '
      + 'window, a loop, tools, state, checks and guards, noted as eleven components in all. Below '
      + 'that a dated axis records when each name landed: December 2024, Anthropic\'s "Building '
      + 'Effective Agents" and the model-plus-loop framing; June 2025, Karpathy popularising '
      + '"context engineering"; September 2025, Anthropic\'s "Effective context engineering for AI '
      + 'agents"; 10 March 2026, Trivedy of LangChain with Agent equals Model plus Harness; and '
      + 'April 2026, Osmani popularising it while OpenAI makes it a provider-level discipline. '
      + 'Captions note that context engineering did not stop mattering but became one component '
      + 'inside the larger surface, that the name moved both times because the thing limiting '
      + 'results moved, and that the third era is the first that can be measured, with the same '
      + 'model on the same benchmark going from 52.8 to 66.5 per cent on harness changes alone.',
  };
}

// ---------------------------------------------------------------- diagram 2
function nestedRings() {
  resetSeq();
  const W = 960, H = 592;

  const els = [...heading('Model, scaffold, harness, orchestration',
    'The layers nest. Naming the layer a problem lives in is most of the work of fixing it.')];

  els.push(text(M, 76, 'ONE AGENT, FOUR LAYERS', { size: 9, stroke: T.inkSubtle }));
  els.push(text(456, 76, 'WHAT EACH LAYER OWNS, AND WHAT IT SOUNDS LIKE WHEN IT BREAKS',
    { size: 9, stroke: T.inkSubtle }));

  // Four concentric rings. The upper arc of each band carries its name and its
  // share of the seven symptoms in the post's diagnostic table; the lower arc
  // carries where the series treats that ring, so no band is left empty.
  const CX = 236, CY = 264;
  const RINGS = [
    { r: 168, name: 'ORCHESTRATION', share: '1 of 7', taught: 'Part IV',
      ly: 104, cy: 120, ty: 404, tint: T.warn },
    { r: 126, name: 'HARNESS', share: '5 of 7', taught: 'Parts II, III, V',
      ly: 146, cy: 162, ty: 362, tint: T.success },
    { r: 84, name: 'SCAFFOLD', share: '1 of 7', taught: 'the CE series',
      ly: 188, cy: 204, ty: 320, tint: T.primary },
    { r: 42, name: 'MODEL', share: '0 of 7', taught: 'Posts 04, 20',
      ly: 242, cy: 257, ty: 272, tint: T.accent },
  ];
  RINGS.forEach((ring) => {
    els.push(ellipse(CX - ring.r, CY - ring.r, ring.r * 2, ring.r * 2,
      { stroke: ring.tint, strokeWidth: 1.5 }));
  });
  RINGS.forEach((ring) => {
    els.push(text(CX - 90, ring.ly, ring.name,
      { size: 10.5, align: 'center', width: 180, stroke: ring.tint }));
    els.push(text(CX - 90, ring.cy, ring.share,
      { size: 9, align: 'center', width: 180, stroke: T.inkMuted }));
    els.push(text(CX - 90, ring.ty, ring.taught,
      { size: 9, align: 'center', width: 180, stroke: T.inkSubtle }));
  });

  els.push(text(CX - 190, 448,
    fit(wrap("Upper label in each band: its share of the seven symptoms in the post's diagnostic table. Lower label: where the series treats it.",
      9.5, 380, 2), 9.5, 380, 'ring caption'),
    { size: 9.5, align: 'center', width: 380, stroke: T.inkSubtle }));

  els.push(...card(40, 484, 392, 62, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(60, 492, 'WHICH DISCIPLINE GOVERNS WHICH RING', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(60, 508, fit('Context engineering: the inner two rings.', 10.5, 352, 'disc 1'),
    { size: 10.5, stroke: T.primary }));
  els.push(text(60, 524, fit('Harness engineering: the third, gesturing at the fourth.', 10.5, 352, 'disc 2'),
    { size: 10.5, stroke: T.success }));

  // The four layers as cards, each ending in the complaint that lands there and
  // the component that answers it — both taken from the post's symptom table.
  const ROWS = [
    { name: 'Model', tint: T.accent, share: '0 of 7',
      what: 'The neural network. On its own it only responds: text in, text out. Its weights and post-training are levers, but not harness levers.',
      owns: 'nothing outside the call',
      says: '"It still fails with everything in place."', fix: 'A stronger model, Post 04' },
    { name: 'Scaffold', tint: T.primary, share: '1 of 7',
      what: 'The behaviour layer: the system prompt, the tool descriptions, how the output is parsed, and what carries from step to step.',
      owns: 'what the model sees, and how its words are read',
      says: '"It retrieved the wrong file."', fix: 'Context assembly, CE Post 09' },
    { name: 'Harness', tint: T.success, share: '5 of 7',
      what: 'The runtime: it calls the model, handles the tool calls, decides when to stop, catches errors, and enforces guardrails.',
      owns: 'one model, driven through repeated cycles',
      says: '"It says it is done, but it isn\'t."', fix: 'Verification, Post 11' },
    { name: 'Orchestration', tint: T.warn, share: '1 of 7',
      what: 'The layer above: it coordinates several agents as units, splitting work between them and merging the results.',
      owns: 'many agents, as a fleet',
      says: '"My two agents overwrote each other."', fix: 'Shared-repo coordination, Post 17' },
  ];
  ROWS.forEach((r, i) => {
    const py = 96 + i * 114;
    els.push(...card(456, py, 464, 108, { spine: r.tint, strokeWidth: 1.3 }));
    els.push(text(476, py + 9, r.name, { size: 13, stroke: T.ink }));
    els.push(rect(856, py + 10, 48, 20, { stroke: r.tint, fill: r.tint, strokeWidth: 1 }));
    els.push(text(856, py + 12, r.share,
      { size: 10, align: 'center', width: 48, stroke: T.onAccent }));
    els.push(text(476, py + 30, fit(wrap(r.what, 10, 420, 2), 10, 420, 'ring what'),
      { size: 10, stroke: T.inkMuted }));
    els.push(text(476, py + 58, fit('owns: ' + r.owns, 10, 420, 'ring owns'),
      { size: 10, stroke: r.tint }));
    els.push(rule(472, 904, py + 76));
    els.push(text(476, py + 84, fit(r.says, 10, 250, 'ring says'), { size: 10, stroke: T.ink }));
    els.push(text(476, py + 84, fit(r.fix, 10, 200, 'ring fix'),
      { size: 10, align: 'right', width: 424, stroke: r.tint }));
  });

  els.push(text(M, 564, fit('Name the ring and the fix names itself: five of the seven symptoms land on the harness, and none on the model.',
    12, 880, 'rings conclusion'), { size: 12, stroke: T.ink }));

  return {
    W, H, els,
    title: 'Model inside scaffold inside harness inside orchestration, with each ring\'s share of the symptoms',
    desc: 'A hand-drawn figure of four concentric rings beside four cards. Each ring band carries '
      + 'its name and its share of the seven symptoms in the post\'s diagnostic table. At the '
      + 'centre is the model, which takes none of the seven: it is the neural network, which on '
      + 'its own only responds with text in and text out, owns nothing outside the call, and whose '
      + 'weights and post-training are levers but not harness levers; the complaint that lands '
      + 'there is that everything is in place and it still fails, answered by a stronger model in '
      + 'post 04. Around it is the scaffold, which takes one of the seven: the behaviour layer of '
      + 'system prompt, tool descriptions, output parsing and what carries from step to step, '
      + 'owning what the model sees and how its words are read; its complaint is that it retrieved '
      + 'the wrong file, answered by context assembly in Context Engineering post 09. Around that '
      + 'is the harness, which takes five of the seven: the runtime that calls the model, handles '
      + 'the tool calls, decides when to stop, catches errors and enforces guardrails, owning one '
      + 'model driven through repeated cycles; its complaint is that it says it is done but it '
      + 'is not, answered by verification in post 11. The outermost ring is orchestration, which '
      + 'takes one of the seven: the layer that coordinates several agents as units, splitting '
      + 'work and merging results, owning many agents as a fleet; its complaint is that two agents '
      + 'overwrote each other, answered by shared-repo coordination in post 17. A panel records '
      + 'that context engineering governs the inner two rings while harness engineering governs '
      + 'the third and gestures at the fourth, and a closing line notes that naming the ring names '
      + 'the fix, with five of the seven symptoms landing on the harness and none on the model.',
  };
}

// ---------------------------------------------------------------- diagram 3
function equation() {
  resetSeq();
  const W = 960, H = 524;

  const els = [...heading('Agent = Model + Harness',
    'The model is one term in the sum, and often not the one with the most headroom left.')];

  els.push(text(M, 76, 'THE EQUATION', { size: 9, stroke: T.inkSubtle }));

  els.push(...card(40, 88, 210, 168, { spine: T.ink, strokeWidth: 1.5 }));
  els.push(text(60, 100, 'AGENT', { size: 11, stroke: T.inkSubtle }));
  els.push(text(60, 120, fit('The whole thing', 14, 170, 'agent head'), { size: 14, stroke: T.ink }));
  els.push(text(60, 146, fit(wrap('that can act rather than only respond, and chooses its own path instead of following one.',
    10.5, 172, 4), 10.5, 172, 'agent body'), { size: 10.5, stroke: T.inkMuted }));
  els.push(rule(60, 230, 210));
  els.push(text(60, 218, 'WHAT YOU CONTROL', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(60, 232, fit('the whole run, end to end', 11, 170, 'agent control'),
    { size: 11, stroke: T.ink }));

  els.push(text(258, 156, '=', { size: 26, stroke: T.ink }));

  els.push(...card(292, 88, 210, 168, { spine: T.accent, strokeWidth: 1.5 }));
  els.push(text(312, 100, 'MODEL', { size: 11, stroke: T.accent }));
  els.push(text(312, 120, fit('Reasoning', 14, 170, 'model head'), { size: 14, stroke: T.ink }));
  els.push(text(312, 146, fit(wrap('Fixed weights, stateless, and mostly not yours to change: a lever you buy rather than build.',
    10.5, 172, 4), 10.5, 172, 'model body'), { size: 10.5, stroke: T.inkMuted }));
  els.push(rule(312, 482, 210));
  els.push(text(312, 218, 'WHAT YOU CONTROL', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(312, 232, fit('which model you call', 11, 170, 'model control'),
    { size: 11, stroke: T.ink }));

  els.push(text(512, 156, '+', { size: 26, stroke: T.ink }));

  els.push(...card(544, 88, 376, 168, { spine: T.success, strokeWidth: 1.5 }));
  els.push(text(564, 100, 'HARNESS', { size: 11, stroke: T.success }));
  els.push(text(564, 120, fit('Everything else', 14, 336, 'harness head'), { size: 14, stroke: T.ink }));
  const PARTS = [
    'the loop that drives it', 'the tools it acts through',
    'the state it keeps on disk', 'the checks that verify it',
    'the hooks that enforce rules', 'the sandbox that bounds it',
  ];
  PARTS.forEach((p, i) => {
    els.push(text(564 + (i % 2) * 172, 146 + Math.floor(i / 2) * 20,
      fit(p, 10, 164, 'harness part'), { size: 10, stroke: T.inkMuted }));
  });
  els.push(rule(564, 900, 210));
  els.push(text(564, 218, 'WHAT YOU CONTROL', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(564, 232, fit('eleven components: 1 loop, 4 feed, 4 govern, 2 at scale', 10, 336, 'harness control'),
    { size: 10, stroke: T.ink }));

  // The measured case for the second term, all three figures from the post.
  els.push(text(M, 274, 'WHY THE SECOND TERM IS THE ONE WITH HEADROOM LEFT', { size: 9, stroke: T.inkSubtle }));

  els.push(...card(40, 290, 288, 158, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(56, 302, 'ONE MODEL, TWO HARNESSES', { size: 9.5, stroke: T.inkSubtle }));
  els.push(text(56, 320, fit('Terminal-Bench 2.0, 89 tasks', 11, 256, 'tb head'),
    { size: 11, stroke: T.ink }));
  els.push(text(56, 344, 'default harness', { size: 9, stroke: T.inkMuted }));
  els.push(rect(56, 358, 90, 16, { stroke: T.inkMuted, fill: T.neutral1, strokeWidth: 1 }));
  els.push(text(152, 360, fit('52.8%, about 47 of 89', 9, 156, 'tb before'), { size: 9, stroke: T.ink }));
  els.push(text(56, 384, 'tuned harness', { size: 9, stroke: T.inkMuted }));
  els.push(rect(56, 398, 113, 16, { stroke: T.success, fill: T.success, strokeWidth: 1 }));
  els.push(text(175, 400, fit('66.5%, about 59 of 89', 9, 134, 'tb after'), { size: 9, stroke: T.ink }));
  els.push(text(56, 424, fit('+13.7 points, one model held fixed', 9.5, 256, 'tb delta'),
    { size: 9.5, stroke: T.success }));

  els.push(...card(336, 290, 288, 158, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(352, 302, 'WHAT CHANGED WAS PLUMBING', { size: 9.5, stroke: T.inkSubtle }));
  els.push(text(352, 320, fit('seven changes listed, none to the model', 11, 256, 'plumb head'),
    { size: 11, stroke: T.ink }));
  els.push(text(352, 346, fit('verification, via a pre-exit checklist', 9.5, 256, 'plumb 1'),
    { size: 9.5, stroke: T.success }));
  els.push(text(352, 366, fit('context, via start-up environment mapping', 9.5, 256, 'plumb 2'),
    { size: 9.5, stroke: T.primary }));
  els.push(text(352, 386, fit('loop exit (4), via repeated-edit counts', 9.5, 256, 'plumb 3'),
    { size: 9.5, stroke: T.accent }));
  els.push(text(352, 412, fit('the three of the seven that carry most', 9, 256, 'plumb note 1'),
    { size: 9, stroke: T.inkMuted }));
  els.push(text(352, 424, fit('of the story (Post 04 tabulates them all)', 9, 256, 'plumb note 2'),
    { size: 9, stroke: T.inkMuted }));

  els.push(...card(632, 290, 288, 158, { spine: T.warn, strokeWidth: 1.3 }));
  els.push(text(648, 302, 'THE SAME EFFECT IN PRODUCTION', { size: 9.5, stroke: T.inkSubtle }));
  els.push(text(648, 322, fit('about 1,000,000 lines of code', 11.5, 256, 'prod 1'),
    { size: 11.5, stroke: T.ink }));
  els.push(text(648, 344, fit('about 1,500 merged pull requests', 11.5, 256, 'prod 2'),
    { size: 11.5, stroke: T.ink }));
  els.push(text(648, 366, fit('over five months', 11.5, 256, 'prod 3'), { size: 11.5, stroke: T.ink }));
  els.push(text(648, 388, fit('3 engineers growing to 7', 11.5, 256, 'prod 4'), { size: 11.5, stroke: T.ink }));
  els.push(text(648, 414, fit('no line of it written by hand', 9.5, 256, 'prod note'),
    { size: 9.5, stroke: T.warn }));
  els.push(text(648, 428, '(OpenAI, 2026)', { size: 9, stroke: T.inkSubtle }));

  els.push(text(M, 470, fit('A decent model with a great harness beats a great model with a bad harness. Post 04 argues it; the series builds it.',
    12, 880, 'eq conclusion 1'), { size: 12, stroke: T.ink }));
  els.push(text(M, 492, fit('The reported six-times spread across harnesses is secondary; the 13.7 points above are the measured number.',
    12, 880, 'eq conclusion 2'), { size: 12, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The founding equation, Agent equals Model plus Harness, with the measured case for the harness term',
    desc: 'A hand-drawn figure of an equation in three boxes above a band of evidence. On the '
      + 'left, the agent: the whole thing that can act rather than only respond and chooses its '
      + 'own path, where what you control is the whole run end to end. An equals sign leads to the '
      + 'model, which supplies reasoning and is fixed weights, stateless and mostly not yours to '
      + 'change, a lever you buy rather than build, where what you control is which model you '
      + 'call. A plus sign leads to a wider box for the harness, which is everything else, listed '
      + 'as the loop that drives the model, the tools it acts through, the state it keeps on disk, '
      + 'the checks that verify it, the hooks that enforce rules and the sandbox that bounds it, '
      + 'and where what you control is all eleven components: one loop, four that feed it, four '
      + 'that govern it and two that work at a larger scale. Beneath, three panels give the '
      + 'measured case for the second term. One model, two harnesses: on Terminal-Bench 2.0 and '
      + 'its 89 tasks, a default harness scores 52.8 per cent, about 47 tasks, and a tuned harness '
      + 'scores 66.5 per cent, about 59 tasks, a gain of 13.7 points with one model held fixed. '
      + 'What changed was plumbing: seven changes listed and none to the model, of which three '
      + 'carry most of the story, namely verification via a pre-exit checklist, context via '
      + 'start-up environment mapping, and loop exit four via repeated-edit counts. The same '
      + 'effect appears in production, where about a million lines of code arrived in about 1,500 '
      + 'merged pull requests over five months from a team of three engineers growing to seven, '
      + 'with no line of it written by hand. Captions record that a decent model with a great '
      + 'harness beats a great model with a bad harness, and that the reported six-times spread '
      + 'across harnesses is secondary while the 13.7 points are the measured number.',
  };
}

module.exports = { threeEras, nestedRings, equation };

if (require.main === module) {
  emit('01-three-eras', threeEras());
  emit('02-nested-rings', nestedRings());
  emit('03-equation', equation());
}
