// The post 15 diagrams, hand-drawn.
//
//   01-autonomy-spectrum   960 x 564  Mirror of the existing figure, filled out.
//   02-approval-gate       960 x 614  Mirror, rebuilt as three phases plus reference panels.
//   03-anatomy-of-a-gate   960 x 500  NEW, published: sections 2, 5 and 7 had no figure.
//
// The two existing figures answer "where should the human be" and "how does the
// pause work". Neither answers the question the post gained in its expansion:
// what an approval gate is actually made of. The two halves, the four outcomes
// including the one nobody plans for, and the record it writes are one figure.
//
// Figures 1 and 2 were single tiers of one-line cards: a lot of canvas for very
// little argument. Both now carry the post's own tables and its own measured
// numbers, which is where the density was hiding all along. Every number in
// these scenes is quoted from posts/15-human-in-the-loop/index.md; nothing here
// is estimated, and the one arithmetic example is labelled as the post labels
// it, as a worked example rather than a measurement.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

const MONO = 3;

// ---------------------------------------------------------------- diagram 1
function autonomySpectrum() {
  resetSeq();
  const W = 960, H = 564;

  const els = [...heading('The autonomy spectrum',
    'Choose the point per action, not per agent. Autonomy and risk rise together.')];

  els.push(text(40, 80, 'less autonomy', { size: 9.5, stroke: T.inkSubtle }));
  els.push(arrow([[150, 88], [800, 88]], { stroke: T.inkSubtle, strokeWidth: 1.3 }));
  els.push(text(810, 80, 'more autonomy', { size: 9.5, align: 'right', width: 110, stroke: T.inkSubtle }));

  // Each stop now carries all three columns of the post's own table: what the
  // agent does, what the human becomes, and what the stop costs. The single
  // gloss line the figure used to carry was a third of the row.
  const STOPS = [
    [40, 'SUGGEST', T.primary,
      'Proposes an action;', 'does not take it.',
      'The operator', 'doing the work',
      'Maximum control,', 'minimum throughput'],
    [264, 'APPROVE', T.primary,
      'Acts, but only after a', 'decision on each action.',
      'The approver', 'in front of every artefact',
      'The bottleneck', 'Morris names'],
    [488, 'ACT AND NOTIFY', T.success,
      'Acts on its own; only', 'the irreversible is gated.',
      'The supervisor', 'watching, able to interrupt',
      'A small number of', 'real decisions'],
    [712, 'AUTONOMOUS', T.warn,
      'Acts; the work is', 'reviewed afterwards.',
      'The observer', 'reading the result',
      'Fastest, and unrecoverable', 'if the run is wrong'],
  ];
  STOPS.forEach((s) => {
    const x = s[0];
    els.push(...card(x, 104, 210, 186, { spine: s[2], strokeWidth: 1.3 }));
    els.push(text(x + 18, 114, fit(s[1], 14, 180, 'stop name'), { size: 14, stroke: T.ink }));
    els.push(text(x + 18, 138, fit(s[3], 9.5, 180, 'stop gloss'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(x + 18, 152, fit(s[4], 9.5, 180, 'stop gloss'), { size: 9.5, stroke: T.inkMuted }));
    els.push(rule(x + 18, x + 192, 170));
    els.push(text(x + 18, 178, 'THE HUMAN BECOMES', { size: 8.5, stroke: T.inkSubtle }));
    els.push(text(x + 18, 192, fit(s[5], 11, 180, 'human role'), { size: 11, stroke: s[2] }));
    els.push(text(x + 18, 208, fit(s[6], 9, 180, 'human role gloss'), { size: 9, stroke: T.inkMuted }));
    els.push(rule(x + 18, x + 192, 224));
    els.push(text(x + 18, 232, 'WHAT IT COSTS', { size: 8.5, stroke: T.inkSubtle }));
    els.push(text(x + 18, 246, fit(s[7], 9.5, 180, 'cost line'), { size: 9.5, stroke: T.ink }));
    els.push(text(x + 18, 260, fit(s[8], 9.5, 180, 'cost line'), { size: 9.5, stroke: T.ink }));
  });

  // --- second tier, left: the post's own worked mapping -------------------
  els.push(...card(40, 306, 560, 174, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 316, fit('ONE AGENT, ONE RUN: THE ROW IS CHOSEN PER ACTION', 10.5, 504, 'tier head'),
    { size: 10.5, stroke: T.primary }));
  els.push(text(58, 336, 'THE ACTION', { size: 8, stroke: T.inkSubtle }));
  els.push(text(296, 336, 'ITS STOP', { size: 8, stroke: T.inkSubtle }));
  els.push(text(430, 336, 'WHY', { size: 8, stroke: T.inkSubtle }));
  els.push(rule(58, 582, 350));

  const ACTIONS = [
    ['read the logs', 'AUTONOMOUS', T.warn, 'reversible'],
    ['run the test suite', 'AUTONOMOUS', T.warn, 'reversible'],
    ['edit files in the working tree', 'AUTONOMOUS', T.warn, 'reversible: roll back'],
    ['open a pull request', 'APPROVE', T.primary, 'visible before you can undo it'],
    ['deploy to production', 'APPROVE', T.primary, 'irreversible'],
  ];
  ACTIONS.forEach((a, i) => {
    const y = 356 + i * 21;
    els.push(text(58, y, fit(a[0], 10, 230, 'action'), { size: 10, stroke: T.ink }));
    els.push(text(296, y, fit(a[1], 10, 126, 'action stop'), { size: 10, stroke: a[2] }));
    els.push(text(430, y + 1, fit(a[3], 8.5, 152, 'action why'), { size: 8.5, stroke: T.inkMuted }));
  });
  els.push(rule(58, 582, 456));
  els.push(text(58, 460, fit(
    "Anthropic's own recipe gates exactly two under an otherwise-automatic policy: git push and gh pr create.",
    8.5, 524, 'tier note'), { size: 8.5, stroke: T.inkMuted }));

  // --- second tier, right: the measured price of sitting at APPROVE -------
  els.push(...card(624, 306, 296, 174, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(642, 316, 'THE MEASURED COST OF ASKING', { size: 10.5, stroke: T.accent }));
  els.push(rule(642, 902, 336));

  const STATS = [
    [346, '97%', 'of permission prompts in Claude', 'Code are approved'],
    [388, '17% to 5%', 'human block rate, roughly: early', 'in a session, then after 50 prompts'],
    [430, '13.6%', 'of 1,053 testers caught a planted', 'command; a classifier caught 89%'],
  ];
  STATS.forEach((s) => {
    els.push(rect(642, s[0], 78, 26, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
    els.push(text(642, s[0] + 6, fit(s[1], 13, 74, 'stat number'),
      { size: 13, align: 'center', width: 78, stroke: T.ink }));
    els.push(text(730, s[0] + 2, fit(s[2], 8, 174, 'stat label'), { size: 8, stroke: T.ink }));
    els.push(text(730, s[0] + 13, fit(s[3], 8, 174, 'stat label'), { size: 8, stroke: T.ink }));
  });
  els.push(text(642, 462, 'measured in Claude Code (Anthropic, 2026)', { size: 8, stroke: T.inkSubtle }));

  els.push(text(40, 500, 'Full autonomy is rarely the goal: gate the irreversible, and let the reversible run.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 522, 'An agent pinned to one level either wastes attention on safe actions or gives away oversight of dangerous ones.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Four stops on the autonomy spectrum, the per-action mapping, and the measured cost of asking',
    desc: 'A hand-drawn spectrum in four stops, running from less autonomy on the left to more on '
      + 'the right, each stop carrying what the agent does, what the human becomes, and what the '
      + 'stop costs. Suggest: the agent proposes an action and does not take it, the human is the '
      + 'operator doing the work, and the cost is maximum control for minimum throughput. Approve: '
      + 'the agent acts only after a decision on each action, the human is the approver in front of '
      + 'every artefact, and the cost is the bottleneck Morris names. Act and notify: the agent acts '
      + 'on its own and only the irreversible is gated, the human is the supervisor, watching and '
      + 'able to interrupt, and the cost is a small number of real decisions. Autonomous: the agent '
      + 'acts and the work is reviewed afterwards, the human is the observer reading the result, and '
      + 'the cost is that it is fastest and unrecoverable if the run is wrong. Below on the left, one '
      + 'agent in one run with the row chosen per action: reading the logs, running the test suite '
      + 'and editing files in the working tree all sit at autonomous because they are reversible, '
      + 'while opening a pull request sits at approve because it is visible before you can undo it, '
      + 'and deploying to production sits at approve because it is irreversible; a note records that '
      + "Anthropic's own recipe gates exactly two things under an otherwise-automatic policy, git "
      + 'push and gh pr create. On the right, the measured cost of asking, from Claude Code: 97 per '
      + 'cent of permission prompts are approved; the human block rate is roughly 17 per cent early '
      + 'in a session and about 5 per cent after fifty prompts; and 13.6 per cent of 1,053 testers '
      + 'caught a planted command that an automated classifier caught 89 per cent of the time. '
      + 'Captions record that full autonomy is rarely the goal, so gate the irreversible and let the '
      + 'reversible run, and that an agent pinned to one level either wastes attention on safe '
      + 'actions or gives away oversight of dangerous ones.',
  };
}

// ---------------------------------------------------------------- diagram 2
function approvalGate() {
  resetSeq();
  const W = 960, H = 614;

  const els = [...heading('An approval gate, answered asynchronously',
    'Only the flagged action pauses; the reply can arrive later, so the human is not a bottleneck.')];

  // --- tier one, left: three phases, both lanes occupied in every one -----
  els.push(text(48, 74, 'AGENT', { size: 10.5, stroke: T.primary }));
  els.push(text(334, 74, 'HUMAN REVIEWER', { size: 10.5, stroke: T.accent }));
  els.push(line([[308, 92], [308, 338]],
    { stroke: T.border, strokeWidth: 1, strokeStyle: 'dashed', roughness: 0.4 }));

  const PHASES = [
    [92, 'PHASE 1  THE REQUEST', 'one call is flagged; the rest is untouched'],
    [180, 'PHASE 2  THE WAIT', 'neither side is blocked on the other'],
    [268, 'PHASE 3  THE ANSWER', 'a re-check, and only then the call runs'],
  ];
  PHASES.forEach((p) => {
    els.push(text(40, p[0], p[1], { size: 9, stroke: T.inkSubtle }));
    els.push(text(326, p[0] + 1, fit(p[2], 8.5, 210, 'phase gloss'), { size: 8.5, stroke: T.inkMuted }));
  });

  const step = (x, y, tint, n, title, d1, d2) => {
    const out = card(x, y, 250, 56, { spine: tint, strokeWidth: 1.3 });
    out.push(rect(x + 16, y + 10, 20, 15, { stroke: tint, fill: tint, strokeWidth: 1 }));
    out.push(text(x + 16, y + 11, n, { size: 10, align: 'center', width: 20, stroke: T.onAccent }));
    out.push(text(x + 44, y + 9, fit(title, 10.5, 192, 'step title'), { size: 10.5, stroke: T.ink }));
    out.push(text(x + 16, y + 30, fit(d1, 8.5, 220, 'step detail'), { size: 8.5, stroke: T.inkMuted }));
    out.push(text(x + 16, y + 42, fit(d2, 8.5, 220, 'step detail'), { size: 8.5, stroke: T.inkMuted }));
    return out;
  };

  els.push(...step(40, 106, T.primary, '1', 'reaches a flagged action',
    "deploy(target='prod'): a rollback cannot", 'undo it, so the policy gates this call'));
  els.push(...step(326, 106, T.accent, '2', 'the request arrives',
    'out of band: Slack, email or a push, from', 'a permission-request event on the harness'));
  els.push(...step(40, 194, T.primary, '3', 'the run does not block',
    'it continues independent work, or it', 'checkpoints to disk and lets the run exit'));
  els.push(...step(326, 194, T.accent, '4', 'reads the diff, and decides',
    'shown the exact diff, the reason it was', 'gated, and the blast radius if it is wrong'));
  els.push(...step(40, 282, T.success, '5', 'resumes, re-checks, executes',
    'the args about to run must equal the args', 'approved; approve-then-mutate is the bug'));
  els.push(...step(326, 282, T.accent, '6', 'answers in one of five shapes',
    'approve, amend, remember, refuse, redirect;', 'a refusal names an alternative to try'));

  els.push(arrow([[294, 134], [322, 134]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[322, 310], [294, 310]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[265, 164], [265, 190]], { stroke: T.inkMuted, strokeWidth: 1 }));
  els.push(arrow([[265, 252], [265, 278]], { stroke: T.inkMuted, strokeWidth: 1 }));
  els.push(arrow([[551, 164], [551, 190]], { stroke: T.inkMuted, strokeWidth: 1 }));
  els.push(arrow([[551, 252], [551, 278]], { stroke: T.inkMuted, strokeWidth: 1 }));

  // --- tier one, right: the two reference panels -------------------------
  els.push(...card(604, 74, 316, 140, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(622, 82, 'BEFORE IT REACHES A PERSON', { size: 10.5, stroke: T.primary }));
  els.push(text(622, 98, fit('six steps in order; a deny-listed call never reaches a person',
    8, 284, 'order gloss'), { size: 8, stroke: T.inkMuted }));
  els.push(rule(622, 902, 112));
  ['hooks', 'deny rules', 'ask rules', 'the permission mode', 'allow rules', 'the human callback']
    .forEach((s, i) => {
      const y = 118 + i * 15;
      const tint = i === 5 ? T.accent : T.primary;
      els.push(rect(622, y, 18, 13, { stroke: tint, fill: tint, strokeWidth: 1 }));
      els.push(text(622, y, String(i + 1), { size: 8.5, align: 'center', width: 18, stroke: T.onAccent }));
      els.push(text(648, y - 1, fit(s, 9, 250, 'order step'),
        { size: 9, stroke: i === 5 ? T.ink : T.inkMuted }));
    });

  els.push(...card(604, 228, 316, 110, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(622, 236, 'FIVE ANSWERS, NOT TWO', { size: 10.5, stroke: T.success }));
  els.push(rule(622, 902, 252));
  [
    ['Approve', 'input unchanged; the tool runs'],
    ['Approve with changes', 'arguments amended, silently'],
    ['Approve and remember', 'allow, plus a persisted rule'],
    ['Refuse', 'a reason it can act on'],
    ['Refuse and redirect', 'deny, naming the alternative'],
  ].forEach((a, i) => {
    const y = 260 + i * 14;
    els.push(text(622, y, fit(a[0], 8.5, 118, 'answer name'), { size: 8.5, stroke: T.ink }));
    els.push(text(748, y, fit(a[1], 8.5, 156, 'answer gloss'), { size: 8.5, stroke: T.inkMuted }));
  });

  // --- tier two, left: the outcome asynchrony introduces ------------------
  els.push(...card(40, 358, 536, 176, { spine: T.alert, strokeWidth: 1.3 }));
  els.push(text(58, 366, 'WHEN NOBODY ANSWERS', { size: 10.5, stroke: T.alert }));
  els.push(text(58, 382, fit('the case asynchronous approval introduces; synchronous approval never had it',
    8.5, 504, 'wait gloss'), { size: 8.5, stroke: T.inkMuted }));
  els.push(rule(58, 558, 398));

  [
    ['A TIMEOUT, AND A DEFAULT', 'for anything irreversible the default is deny',
      'no answer is not consent; fail closed, as a safety hook does'],
    ['WHAT THE RUN DOES MEANWHILE', 'continue independent work, or checkpoint and defer',
      'rather than hold a process, a budget and a lock open'],
    ['WHO GETS ASKED NEXT', 'this reviewer, then their team, then the on-call',
      'one name is how a queue quietly becomes a dead letter'],
  ].forEach((r, i) => {
    const y = 406 + i * 36;
    els.push(text(58, y, fit(r[0], 9, 170, 'wait label'), { size: 9, stroke: T.inkSubtle }));
    els.push(text(236, y, fit(r[1], 9, 322, 'wait line'), { size: 9, stroke: T.ink }));
    els.push(text(236, y + 13, fit(r[2], 9, 322, 'wait line'), { size: 9, stroke: T.inkMuted }));
  });
  els.push(text(58, 510, fit('The number to watch is queue depth over time; a queue that grows means nobody owns it.',
    9, 504, 'wait note'), { size: 9, stroke: T.ink }));

  // --- tier two, right: the post's own arithmetic, labelled as worked -----
  els.push(...card(604, 358, 316, 176, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(622, 366, 'THE GATE BUDGET, WORKED', { size: 10.5, stroke: T.primary }));
  els.push(text(622, 382, fit("the post's own example: what narrowing the policy buys",
    8, 284, 'budget gloss'), { size: 8, stroke: T.inkMuted }));
  els.push(rule(622, 902, 398));

  [
    [402, '180', 'tool calls in one run,', '34 of them writes'],
    [433, '34', 'requests at tool granularity: about 8.5', 'minutes of reading, at 15 s each'],
    [464, '3', 'requests once the policy reads arguments:', 'about 45 seconds, not an hour'],
    [495, '204', 'prompts over six such runs; past the 50th,', 'block rates are about 5%, not about 17%'],
  ].forEach((b) => {
    els.push(rect(622, b[0], 74, 24, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
    els.push(text(622, b[0] + 5, fit(b[1], 12, 70, 'budget number'),
      { size: 12, align: 'center', width: 74, stroke: T.ink }));
    els.push(text(706, b[0] + 1, fit(b[2], 8, 198, 'budget label'), { size: 8, stroke: T.ink }));
    els.push(text(706, b[0] + 12, fit(b[3], 8, 198, 'budget label'), { size: 8, stroke: T.inkMuted }));
  });

  els.push(text(40, 554, 'Gate the irreversible, let the approval be asynchronous, and decide in advance what happens when the answer never comes.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 576, 'Oversight becomes a queue a human drains on their own schedule, rather than an interrupt that stalls the run and the reviewer at once.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A flagged action pausing for an approval that arrives later, with what precedes and follows it',
    desc: 'A hand-drawn two-lane sequence between an agent and a human reviewer, laid out in three '
      + 'phases with both lanes occupied in each. Phase one, the request: the agent reaches a '
      + 'flagged action, a deploy targeting production that a rollback cannot undo, so the policy '
      + 'gates the call; the request arrives out of band, by Slack, email or a push, from a '
      + 'permission-request event on the harness. Phase two, the wait: the run does not block, '
      + 'continuing independent work or checkpointing to disk and letting the run exit, while the '
      + 'reviewer reads the diff and decides, shown the exact diff, the reason it was gated and the '
      + 'blast radius if it is wrong. Phase three, the answer: the reviewer answers in one of five '
      + 'shapes, and the agent resumes, re-checks that the arguments about to run equal the '
      + 'arguments approved, and executes. Two reference panels sit on the right. The first, before '
      + 'it reaches a person, lists the six evaluation steps in order: hooks, deny rules, ask rules, '
      + 'the permission mode, allow rules and only then the human callback, so a deny-listed call '
      + 'never reaches a person. The second lists five answers rather than two: approve with the '
      + 'input unchanged; approve with changes, where the arguments are amended silently; approve '
      + 'and remember, which adds a persisted rule; refuse, with a reason the agent can act on; and '
      + 'refuse and redirect, which names the alternative. Below on the left, when nobody answers: '
      + 'set a timeout and a default, and for anything irreversible default to deny because no '
      + 'answer is not consent; decide what the run does meanwhile, continuing independent work or '
      + 'checkpointing and deferring rather than holding a process, a budget and a lock open; and '
      + 'decide who gets asked next, this reviewer, then their team, then the on-call, because one '
      + 'name is how a queue quietly becomes a dead letter. The number to watch is queue depth over '
      + "time. On the right, the post's own worked gate budget: a run of 180 tool calls with 34 of "
      + 'them writes produces 34 requests at tool granularity, about 8.5 minutes of reading at '
      + 'fifteen seconds each, and 3 requests once the policy reads arguments, about 45 seconds '
      + 'rather than an hour; 204 prompts accumulate over six such runs, and past the fiftieth the '
      + 'measured block rate is about 5 per cent rather than about 17 per cent. Captions record that '
      + 'you should gate the irreversible, let the approval be asynchronous and decide in advance '
      + 'what happens when the answer never comes, so oversight becomes a queue a human drains on '
      + 'their own schedule rather than an interrupt that stalls the run and the reviewer at once.',
  };
}

// ---------------------------------------------------------------- diagram 3
function anatomyOfAGate() {
  resetSeq();
  const W = 960, H = 500;

  const els = [...heading('What an approval gate is actually made of',
    'Two halves that belong to different people, four outcomes rather than two, and a record of every decision.')];

  const half = (x, tint, headline, sig, lines) => {
    const out = card(x, 92, 430, 132, { spine: tint, strokeWidth: 1.4 });
    out.push(text(x + 18, 100, headline, { size: 10, stroke: tint }));
    out.push(rect(x + 18, 120, 394, 28, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
    out.push(text(x + 30, 127, sig, { size: 10, family: MONO, stroke: T.ink }));
    lines.forEach((l, i) => out.push(text(x + 18, 160 + i * 16,
      fit(l, 9, 394, 'half line'), { size: 9, stroke: T.ink })));
    return out;
  };

  els.push(...half(40, T.primary, 'HALF ONE: THE POLICY', 'needs_approval(tool, args) -> bool', [
    'Ordinary code, so you can assert against it: this call is gated,',
    'that one is not. Start at tool granularity, and move to argument',
    'granularity for the tools where the coarse version fires on things',
    'nobody needs to see.']));
  els.push(...half(490, T.success, 'HALF TWO: THE DECIDER', 'request_approval(tool, args) -> Decision', [
    'A person, or something standing in for one, and never directly',
    'testable. But it is a seam: substitute an auto-approve or an',
    'auto-deny function and the whole flow runs offline, with no',
    'prompt and no human anywhere in it.']));

  els.push(text(56, 240, 'FOUR OUTCOMES, NOT TWO', { size: 9, stroke: T.inkSubtle }));

  const OUT = [
    [40, 'NOT GATED', T.neutral3, 'The policy said no', 'approval is needed.', 'The call runs.'],
    [262, 'APPROVED', T.success, 'A person looked and', 'said yes. The call runs,', 'and the record says who.'],
    [484, 'DENIED', T.warn, 'Returns its reason as an', 'ordinary observation.', 'The run keeps going.'],
    [706, 'NO ANSWER', T.alert, 'The request expired.', 'For anything irreversible', 'the default is deny.'],
  ];
  OUT.forEach((o) => {
    els.push(...card(o[0], 254, 210, 92, { spine: o[2], strokeWidth: 1.4 }));
    els.push(text(o[0] + 16, 264, o[1], { size: 12, stroke: T.ink }));
    [o[3], o[4], o[5]].forEach((l, i) => els.push(text(o[0] + 16, 290 + i * 15,
      fit(l, 9, 180, 'outcome line'), { size: 9, stroke: T.inkMuted })));
  });

  els.push(...card(40, 360, 880, 84, { spine: T.primary, strokeWidth: 1.4 }));
  els.push(text(58, 368, 'WHAT THE GATE WRITES DOWN, EVERY TIME', { size: 10, stroke: T.primary }));
  ['the call and its arguments', 'why it was gated', 'who decided', 'what they decided', 'how long it sat']
    .forEach((f, i) => {
      els.push(rect(58 + i * 172, 388, 160, 26, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
      els.push(text(58 + i * 172, 396, fit(f, 9, 150, 'record field'),
        { size: 9, align: 'center', width: 160, stroke: T.ink }));
    });
  els.push(text(58, 422, 'so the rubber-stamp rate becomes measurable rather than a suspicion, and "who approved this?" has an answer',
    { size: 9.5, stroke: T.inkMuted }));

  els.push(text(40, 458, 'Conflate the two halves and you get a gate nobody can test, then a gate nobody trusts, then a gate somebody disables.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 480, 'And a denial that terminates the run teaches reviewers that saying no is expensive. Make refusal cheap and it gets used honestly.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The two halves of an approval gate, its four outcomes, and the record it keeps',
    desc: 'A hand-drawn anatomy of an approval gate. The first half is the policy, a function '
      + 'taking a tool and its arguments and returning whether approval is needed: ordinary code, '
      + 'so you can assert against it that this call is gated and that one is not, starting at tool '
      + 'granularity and moving to argument granularity for the tools where the coarse version '
      + 'fires on things nobody needs to see. The second half is the decider, a function taking the '
      + 'same call and returning a decision: a person, or something standing in for one, never '
      + 'directly testable, but a seam, so substituting an auto-approve or auto-deny function lets '
      + 'the whole flow run offline with no prompt and no human. Below, four outcomes rather than '
      + 'two: not gated, where the policy said no approval is needed and the call runs; approved, '
      + 'where a person looked and said yes, the call runs and the record says who; denied, which '
      + 'returns its reason as an ordinary observation and lets the run keep going; and no answer, '
      + 'where the request expired and the default for anything irreversible is deny. At the '
      + 'bottom, what the gate writes down every time: the call and its arguments, why it was '
      + 'gated, who decided, what they decided, and how long it sat, so the rubber-stamp rate '
      + 'becomes measurable rather than a suspicion. Captions record that conflating the two halves '
      + 'gives a gate nobody can test, then nobody trusts, then somebody disables, and that a '
      + 'denial which terminates the run teaches reviewers that saying no is expensive.',
  };
}

module.exports = { autonomySpectrum, approvalGate, anatomyOfAGate };

if (require.main === module) {
  emit('01-autonomy-spectrum', autonomySpectrum());
  emit('02-approval-gate', approvalGate());
  emit('03-anatomy-of-a-gate', anatomyOfAGate());
}
