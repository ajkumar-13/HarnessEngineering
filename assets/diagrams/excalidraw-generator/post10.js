// The post 10 diagrams, hand-drawn.
//
//   01-ratchet-mechanism   960 x 636  Mirror of the existing figure, re-densified.
//   02-ratchet-over-time   960 x 588  Mirror, re-densified.
//   03-life-of-a-rule      960 x 470  NEW, published: sections 3, 5 and 7 had no figure.
//
// The two existing figures both draw the ratchet working. Neither draws the
// thing the post spends its added length on: that a rule has to be *earned*
// before it is durable, and *watched* afterwards. Steps 2, 3 and 5 of the third
// scene are the parts a monotonic mechanism cannot supply for itself.
//
// Scenes 1 and 2 were re-laid out after a density review: both were 960 wide and
// barely 400 tall, so the cards ran to 600px around 300px of text and the
// staircase floated in an empty upper-left quadrant. Scene 1 now carries the
// section 5 table (which teeth a failure actually earns) as a second tier;
// scene 2 now carries a counted y axis, dated x ticks and the section 3 memory
// file that the staircase is building. Every value in both is lifted from the
// post: the four issue ids and dates in section 3's ratcheted file, and the
// behaviour of the companion code in code/26-coding-agent.

const { T, rect, ellipse, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// The ratcheted memory file of section 3, verbatim apart from the markdown
// backticks. Both scenes draw from this one list so a rule and its provenance
// cannot drift apart between the two figures.
const FILE_RULES = [
  ['Use uv add to add a dependency; the lockfile is authoritative.', '#412', '2026-05-02', 'use uv add, not pip'],
  ['Every new module ships with a test file.', '#377', '2026-05-19', 'every module ships a test'],
  ['Run mypy src/ before committing; a failing typecheck blocks the commit.', '#431', '2026-06-01', 'mypy src/ before commit'],
  ['Delete a failing test or fix it; never skip it.', '#455', '2026-06-08', 'never skip a failing test'],
];

// ---------------------------------------------------------------- diagram 1
function ratchetMechanism() {
  resetSeq();
  const W = 960, H = 640;

  const els = [...heading('The ratchet: every mistake becomes a rule',
    'One failure is converted into durable constraints, and section 5 decides which of them it earns.')];

  // --- the failure, as a full-width banner in two columns ------------------
  // The banner used to be a 190px card with the rest of the row empty; it now
  // states the failure on the left and what happens without a ratchet on the
  // right, divided by a hairline, so the whole width carries something.
  els.push(...card(40, 80, 880, 68, { spine: T.alert, strokeWidth: 1.5 }));
  els.push(text(58, 88, 'A FAILURE', { size: 9, stroke: T.alert }));
  els.push(text(58, 106, fit('The agent shipped a change with a test it had quietly commented out.',
    13, 528, 'failure line'), { size: 13, stroke: T.ink }));
  els.push(text(58, 128, fit("Section 4's worked example, after Osmani.", 9, 528, 'failure source'),
    { size: 9, stroke: T.inkSubtle }));

  els.push(line([[596, 90], [596, 140]], { stroke: T.border, strokeWidth: 1, roughness: 0.3 }));
  els.push(text(614, 88, 'IF YOU FIX ONLY THE INSTANCE', { size: 9, stroke: T.inkSubtle }));
  els.push(text(614, 106, fit('the class comes back, and nothing', 10.5, 288, 'failure gloss'),
    { size: 10.5, stroke: T.ink }));
  els.push(text(614, 124, fit('stops the next session repeating it.', 10.5, 288, 'failure gloss'),
    { size: 10.5, stroke: T.ink }));

  els.push(text(0, 158, 'THE RATCHET CONVERTS ONE FAILURE INTO THREE INDEPENDENT, DURABLE CONSTRAINTS',
    { size: 9.5, align: 'center', width: W, stroke: T.accent }));
  [184, 480, 776].forEach((x) => {
    els.push(arrow([[x, 174], [x, 192]], { stroke: T.accent, strokeWidth: 1.3 }));
  });

  // --- the three teeth ------------------------------------------------------
  const TEETH = [
    ['1', 'Memory-file line', T.primary, 'SECTIONS 2-3',
      'Delete a failing test or', 'fix it; never skip it.',
      'AGENTS.md  [#455, 2026-06-08]',
      'At every session start',
      'prepended ahead of the first user turn', 'the model reads it, and usually complies'],
    ['2', 'Hook', T.success, 'POST 13',
      'A pre-commit check greps', 'the diff for skip markers.',
      'listed in .checks/enforce.txt',
      'On every commit',
      'deterministic, whether or not the model agrees', 'the tooth that survives a forgetful model'],
    ['3', 'Reviewer check', T.warn, 'POST 12',
      'A reviewer sub-agent flags', 'a skipped test as a blocker.',
      'an independent reader, not a gate',
      'After the first two',
      'the only tooth for rules nothing can gate', 'so expect drift, and read behind it'],
  ];

  TEETH.forEach((t, i) => {
    const px = 40 + i * 296, py = 196;
    els.push(...card(px, py, 288, 232, { spine: t[2], strokeWidth: 1.3 }));
    els.push(rect(px + 16, py + 16, 26, 20, { stroke: t[2], fill: t[2], strokeWidth: 1 }));
    els.push(text(px + 16, py + 18, t[0], { size: 12, align: 'center', width: 26, stroke: T.onAccent }));
    els.push(text(px + 52, py + 14, fit(t[1], 15, 148, 'tooth name'), { size: 15, stroke: T.ink }));
    els.push(text(px + 160, py + 20, fit(t[3], 9, 112, 'tooth ref'),
      { size: 9, align: 'right', width: 112, stroke: T.inkSubtle }));

    els.push(rule(px + 16, px + 272, py + 52));
    els.push(text(px + 16, py + 62, 'WHAT LANDS', { size: 9, stroke: T.inkSubtle }));
    els.push(text(px + 16, py + 80, fit(t[4], 11.5, 256, 'tooth what'), { size: 11.5, stroke: T.ink }));
    els.push(text(px + 16, py + 100, fit(t[5], 11.5, 256, 'tooth what'), { size: 11.5, stroke: T.ink }));
    els.push(text(px + 16, py + 122, fit(t[6], 9.5, 256, 'tooth where'), { size: 9.5, stroke: T.inkMuted }));

    els.push(rule(px + 16, px + 272, py + 148));
    els.push(text(px + 16, py + 158, 'WHEN IT ACTS', { size: 9, stroke: T.inkSubtle }));
    els.push(text(px + 16, py + 176, fit(t[7], 12.5, 256, 'tooth when'), { size: 12.5, stroke: t[2] }));
    els.push(text(px + 16, py + 198, fit(t[8], 9.5, 256, 'tooth gloss'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(px + 16, py + 212, fit(t[9], 9.5, 256, 'tooth gloss'), { size: 9.5, stroke: T.inkMuted }));
  });

  // --- second tier: which teeth a given failure actually earns (section 5) --
  els.push(...card(40, 444, 880, 140, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(58, 452, 'NOT EVERY FAILURE EARNS ALL THREE: WHICH TEETH THIS ONE BUYS (SECTION 5)',
    { size: 9, stroke: T.accent }));
  els.push(text(58, 472, 'DETECTABLE?', { size: 9, stroke: T.inkSubtle }));
  els.push(text(152, 472, 'APPLIES TO', { size: 9, stroke: T.inkSubtle }));
  els.push(text(258, 472, 'TEETH', { size: 9, stroke: T.inkSubtle }));
  els.push(text(322, 472, 'WHAT THE FAILURE EARNS', { size: 9, stroke: T.inkSubtle }));
  els.push(text(590, 472, 'WHY', { size: 9, stroke: T.inkSubtle }));
  els.push(rule(58, 902, 486));

  const ROWS = [
    ['Yes', T.success, 'every task', [['1', T.primary], ['2', T.success]],
      'Memory line and hook', 'the line prevents most; the hook catches the rest'],
    ['Yes', T.success, 'some tasks', [['2', T.success]],
      'Hook only, no memory line', 'one directory rule should not be read by every task'],
    ['No', T.inkMuted, 'every task', [['1', T.primary], ['3', T.warn]],
      'Memory line and reviewer check', 'nothing can gate it, so expect drift (Post 12)'],
    ['No', T.inkMuted, 'some tasks', [],
      'Neither: a skill loaded on demand', 'advice, not a rule: load it on demand (Post 07)'],
  ];

  ROWS.forEach((r, i) => {
    const y = 494 + i * 22;
    if (i) els.push(rule(58, 902, y - 6));
    els.push(text(58, y, r[0], { size: 10, stroke: r[1] }));
    els.push(text(152, y, r[2], { size: 10, stroke: T.ink }));
    if (r[3].length) {
      r[3].forEach((b, j) => {
        els.push(rect(258 + j * 22, y - 1, 17, 14, { stroke: b[1], fill: b[1], strokeWidth: 1 }));
        els.push(text(258 + j * 22, y, b[0], { size: 9, align: 'center', width: 17, stroke: T.onAccent }));
      });
    } else {
      els.push(text(258, y, 'none', { size: 9.5, stroke: T.inkSubtle }));
    }
    els.push(text(322, y, fit(r[4], 10, 260, 'earns'), { size: 10, stroke: T.ink }));
    els.push(text(590, y, fit(r[5], 9.5, 312, 'why'), { size: 9.5, stroke: T.inkMuted }));
  });

  els.push(text(40, 596,
    'Three independent layers from one failure: the model reads it, a hook blocks it, a reviewer catches it.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 618,
    'A mistake has to defeat all three to happen twice, and the table says how many of the three this one is worth.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'One failure converted into three durable constraints, with a table of which teeth a failure earns',
    desc: 'A hand-drawn figure in two tiers. Across the top, a failure banner in two columns: on '
      + 'the left, the agent shipped a change with a test it had quietly commented out, the worked '
      + 'example of section 4 after Osmani; on the right, if you fix only the instance the class '
      + 'comes back and nothing stops the next session repeating it. Three arrows carry the failure '
      + 'down into three constraint cards. One, a memory-file line reading delete a failing test or '
      + 'fix it, never skip it, recorded in AGENTS.md against issue 455 dated the eighth of June '
      + '2026, acting at every session start because it is prepended ahead of the first user turn, '
      + 'so the model reads it and usually complies, from sections 2 and 3. Two, a hook: a '
      + 'pre-commit check that greps the diff for skip markers, listed in a checks enforcement '
      + 'file, acting on every commit, deterministic whether or not the model agrees, and so the '
      + 'tooth that survives a forgetful model, covered in post 13. Three, a reviewer check: a '
      + 'reviewer sub-agent flags a skipped test as a blocker, an independent reader rather than a '
      + 'gate, acting after the first two, the only tooth available for rules nothing can gate, so '
      + 'expect drift and read behind it, covered in post 12. Below them a table works out which '
      + 'teeth a '
      + 'failure earns. A detectable failure that applies to every task earns teeth one and two, a '
      + 'memory line and a hook, because the line prevents most violations and the hook catches the '
      + 'rest. A detectable failure that applies to only some tasks earns tooth two alone, a hook '
      + 'with no memory line, because one directory rule should not be read by every task. An '
      + 'undetectable failure that applies to every task earns teeth one and three, a memory line '
      + 'and a reviewer check, because nothing can gate it so drift is expected. An undetectable '
      + 'failure that applies to only some tasks earns no teeth at all: it is advice rather than a '
      + 'rule and belongs in a skill loaded on demand, in post 07. Captions record that three '
      + 'independent layers come from one failure, that a mistake has to defeat all three to happen '
      + 'twice, and that the table says how many of the three a given failure is worth.',
  };
}

// ---------------------------------------------------------------- diagram 2
function ratchetOverTime() {
  resetSeq();
  const W = 960, H = 588;

  const els = [...heading('Why it is a ratchet: reliability only climbs',
    'Each failure adds a rule that is never un-learned, so the count of rules in force goes one way.')];

  // --- axes -----------------------------------------------------------------
  // The y axis counts something the post actually states: the four rules in
  // section 3's ratcheted file. Reliability is the reading, not the unit.
  const LEVEL = [300, 254, 208, 162, 116];   // 0 to 4 rules in force
  els.push(arrow([[86, 312], [86, 100]], { stroke: T.inkSubtle, strokeWidth: 1.1 }));
  els.push(arrow([[86, 312], [906, 312]], { stroke: T.inkSubtle, strokeWidth: 1.1 }));
  els.push(text(32, 82, 'RULES IN FORCE', { size: 9, stroke: T.inkSubtle }));
  LEVEL.forEach((y, i) => {
    els.push(text(52, y - 7, String(i), { size: 10, align: 'right', width: 26, stroke: T.inkSubtle }));
    els.push(line([[80, y], [86, y]], { stroke: T.inkSubtle, strokeWidth: 1, roughness: 0.3 }));
  });

  // --- the counterfactual, drawn under the staircase ------------------------
  // A dashed flat line at zero rules: the same sessions without a memory file.
  // It also stops the region under the climb from reading as blank.
  const RISER = [210, 370, 530, 690];
  els.push(line([[100, LEVEL[0]], [880, LEVEL[0]]],
    { stroke: T.inkSubtle, strokeWidth: 1.2, strokeStyle: 'dashed' }));
  els.push(text(596, 278, 'without a memory file: every session starts here',
    { size: 9.5, stroke: T.inkSubtle }));

  // --- the staircase --------------------------------------------------------
  els.push(line([[100, LEVEL[0]], [RISER[0], LEVEL[0]], [RISER[0], LEVEL[1]],
    [RISER[1], LEVEL[1]], [RISER[1], LEVEL[2]], [RISER[2], LEVEL[2]],
    [RISER[2], LEVEL[3]], [RISER[3], LEVEL[3]], [RISER[3], LEVEL[4]], [880, LEVEL[4]]],
  { stroke: T.success, strokeWidth: 2 }));

  RISER.forEach((x, i) => {
    els.push(ellipse(x - 7, LEVEL[i] - 7, 14, 14, { stroke: T.alert, fill: T.alert, strokeWidth: 1 }));
    // The rule the failure earned, hung under the tread it lifted the file to.
    els.push(text(x + 12, LEVEL[i + 1] + 10,
      fit(FILE_RULES[i][3], 9.5, 140, 'riser rule'), { size: 9.5, stroke: T.ink }));
    els.push(text(x + 12, LEVEL[i + 1] + 24,
      'issue ' + FILE_RULES[i][1], { size: 9, stroke: T.inkMuted }));
    // Dated x tick: the day that rule was accepted into the file.
    els.push(line([[x, 312], [x, 318]], { stroke: T.inkSubtle, strokeWidth: 1, roughness: 0.3 }));
    els.push(text(x - 45, 322, FILE_RULES[i][2],
      { size: 9, align: 'center', width: 90, stroke: T.inkSubtle }));
  });

  els.push(text(700, 88, 'one way: it cannot slip back', { size: 9.5, stroke: T.success }));
  els.push(text(100, 342, 'SESSIONS, DATED BY WHEN EACH RULE WAS ACCEPTED INTO AGENTS.md',
    { size: 9, stroke: T.inkSubtle }));

  // --- legend, in the quadrant the staircase leaves empty --------------------
  els.push(...card(112, 84, 306, 106, { spine: T.accent, strokeWidth: 1.2 }));
  els.push(text(130, 92, 'HOW TO READ IT', { size: 9, stroke: T.accent }));
  ['a dot is a failure the agent hit',
    'a riser is the durable rule it earned',
    'the height is rules in force in AGENTS.md'].forEach((l, i) => {
    els.push(text(130, 110 + i * 20, fit(l, 10, 270, 'legend'), { size: 10, stroke: T.ink }));
  });
  els.push(text(130, 170, 'each rule closes a gap, so reliability climbs with the count',
    { size: 9, stroke: T.inkMuted }));

  // --- why there are four steps and not forty (section 6) -------------------
  // Sits in the wedge the staircase leaves empty above its second and third
  // treads, clear of both the tread at level 3 and the label under level 4.
  els.push(...card(438, 84, 232, 62, { spine: T.warn, strokeWidth: 1.2 }));
  els.push(text(456, 92, 'WHAT EARNS A STEP (SECTION 6)', { size: 9, stroke: T.warn }));
  els.push(text(456, 108, fit('it recurred, it was expensive', 10, 196, 'promote'),
    { size: 10, stroke: T.ink }));
  els.push(text(456, 124, fit('to relearn, and it generalises', 10, 196, 'promote'),
    { size: 10, stroke: T.ink }));

  // --- what the staircase has built, by step four ---------------------------
  els.push(...card(40, 360, 880, 122, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 368, 'WHAT AGENTS.md HOLDS AT STEP 4, WITH THE PROVENANCE EACH LINE CARRIES',
    { size: 9, stroke: T.primary }));
  FILE_RULES.forEach((r, i) => {
    const y = 388 + i * 22;
    if (i) els.push(rule(58, 902, y - 6));
    els.push(text(58, y, fit(r[0], 10.5, 582, 'file rule'), { size: 10.5, stroke: T.ink }));
    els.push(text(686, y + 1, '[' + r[1] + ', ' + r[2] + ']',
      { size: 9.5, align: 'right', width: 202, stroke: T.inkMuted }));
  });

  els.push(text(40, 496, 'Each failure adds a step, no rule is ever un-learned, and the staircase only climbs.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 518, 'Without a memory file every session starts at zero rules and re-makes the same mistakes.',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 540, 'It climbs only while the model is held fixed: a model upgrade is the one event that legitimately turns it back.',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 564, 'Runnable in code/26-coding-agent: learn() refuses a duplicate rule, and the fix lands on the second attempt.',
    { size: 10, stroke: T.inkSubtle }));

  return {
    W, H, els,
    title: 'A rising staircase of rules in force, one step per failure, over the dates each rule was accepted',
    desc: 'A hand-drawn staircase rising from left to right. The vertical axis counts the rules in '
      + 'force in the memory file, ticked from zero to four; the horizontal axis is sessions, dated '
      + 'by when each rule was accepted into AGENTS.md. Each riser is marked with a dot standing for '
      + 'a failure and labelled with the rule it earned and its issue number: use uv add rather than '
      + 'pip, from issue 412 on the second of May 2026; every module ships a test, from issue 377 on '
      + 'the nineteenth of May; run mypy on src before commit, from issue 431 on the first of June; '
      + 'and never skip a failing test, from issue 455 on the eighth of June. A dashed flat line '
      + 'runs along zero for the whole width, labelled: without a memory file, every session starts '
      + 'here. A legend records that a '
      + 'dot is a failure the agent hit, a riser is the durable rule it earned, the height is the '
      + 'number of rules in force, and that each rule closes a gap so reliability climbs with the '
      + 'count. A second small panel gives what earns a step, from section 6: it recurred, it was '
      + 'expensive to relearn, and it generalises. A note at the top right records that the '
      + 'mechanism runs one way and cannot slip '
      + 'back. Below the chart, a panel lists what the file holds at step four, each line with the '
      + 'provenance it carries: use uv add to add a dependency since the lockfile is authoritative; '
      + 'every new module ships with a test file; run mypy on src before committing, since a failing '
      + 'typecheck blocks the commit; and delete a failing test or fix it, never skip it. Captions '
      + 'record that each failure adds a step and no rule is ever un-learned so the staircase only '
      + 'climbs, that without a memory file every session starts at zero rules and re-makes the same '
      + 'mistakes, that the climb is monotonic only while the model is held fixed because a model '
      + 'upgrade is the one event that legitimately turns it back, and that the companion code in '
      + 'the twenty-sixth code directory runs the same ratchet, where the learn method refuses a '
      + 'duplicate rule and the fix lands on the second attempt.',
  };
}

// ---------------------------------------------------------------- diagram 3
function lifeOfARule() {
  resetSeq();
  const W = 960, H = 470;

  const els = [...heading('The life of a rule, before and after it is written',
    'The ratchet is monotonic, so a wrong rule is exactly as permanent as a right one. Steps 2, 3 and 5 are what keep it honest.')];

  const stage = (x, w, tint, step, name, lines, note) => {
    const out = card(x, 104, w, 140, { spine: tint, strokeWidth: 1.4 });
    out.push(text(x + 18, 112, step, { size: 9, stroke: tint }));
    out.push(text(x + 18, 130, fit(name, 13, w - 36, 'stage name'), { size: 13, stroke: T.ink }));
    lines.forEach((l, i) => out.push(text(x + 18, 156 + i * 14,
      fit(l, 9, w - 36, 'stage line'), { size: 9, stroke: T.ink })));
    note.forEach((l, i) => out.push(text(x + 18, 208 + i * 14,
      fit(l, 9, w - 36, 'stage note'), { size: 9, stroke: T.inkMuted })));
    return out;
  };

  els.push(...stage(40, 250, T.alert, 'STEP 1', 'A failure',
    ['The agent shipped a test it had', 'quietly skipped.'],
    ['Fixing only the instance means', 'the class comes back.']));
  els.push(...stage(306, 290, T.warn, 'STEP 2', 'A reviewed root cause',
    ['The agent proposes; a person accepts.', 'A plausible cause is not a cause.'],
    ['A wrong rule is as permanent as a', 'right one, and hides the real cause.']));
  els.push(...stage(652, 268, T.primary, 'STEP 3', 'A rule you could hook',
    ['Say what to do, not only what to avoid.', 'One concept per line.', 'Specific enough to check.'],
    ['If you cannot imagine the hook,', 'the line is advice, not a rule.']));

  els.push(arrow([[292, 174], [302, 174]], { stroke: T.inkMuted, strokeWidth: 1.4 }));
  els.push(arrow([[600, 174], [648, 174]], { stroke: T.inkMuted, strokeWidth: 1.4 }));
  els.push(arrow([[786, 246], [786, 262], [200, 262], [200, 272]],
    { stroke: T.inkMuted, strokeWidth: 1.3 }));

  els.push(...card(40, 276, 430, 112, { spine: T.success, strokeWidth: 1.4 }));
  els.push(text(58, 284, 'STEP 4', { size: 9, stroke: T.success }));
  els.push(text(58, 300, 'Three teeth, from one failure', { size: 13, stroke: T.ink }));
  ['1  a memory-file line, read at the start of every session',
    '2  a hook, enforced deterministically (Post 13)',
    '3  a reviewer check, if it slips the first two (Post 12)'].forEach((l, i) => {
    els.push(text(58, 326 + i * 16, fit(l, 9.5, 394, 'tooth'), { size: 9.5, stroke: T.inkMuted }));
  });

  els.push(arrow([[472, 332], [486, 332]], { stroke: T.inkMuted, strokeWidth: 1.4 }));

  els.push(...card(490, 276, 430, 112, { spine: T.accent, strokeWidth: 1.4 }));
  els.push(text(508, 284, 'STEP 5', { size: 9, stroke: T.accent }));
  els.push(text(508, 300, 'What the hook tells you later', { size: 13, stroke: T.ink }));
  ['never fires: the line is working, or the case is gone',
    'fires constantly: the line is not followed, so rewrite it',
    'provenance is what tells those two apart'].forEach((l, i) => {
    els.push(text(508, 326 + i * 16, fit(l, 9.5, 394, 'signal'), { size: 9.5, stroke: T.inkMuted }));
  });

  els.push(text(40, 408, 'Every rule carries its provenance: the failure it came from, with a date or an issue number.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 430, 'Without it, "remove the rules that no longer apply" has no way to identify them, and the file only ever grows.',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 452, 'Add with the ratchet; prune with judgement. The steady state grows on failure and shrinks on obsolescence.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The five stages a rule passes through, from failure to a signal that it still works',
    desc: 'A hand-drawn lifecycle in five stages. Step one, a failure: the agent shipped a test it '
      + 'had quietly skipped, with the note that fixing only the instance means the class comes '
      + 'back. Step two, a reviewed root cause: the agent proposes and a person accepts, because a '
      + 'plausible cause is not a cause, and a wrong rule is as permanent as a right one while also '
      + 'hiding the real cause. Step three, a rule you could hook: say what to do rather than only '
      + 'what to avoid, one concept per line, and specific enough to check, with the test that if '
      + 'you cannot imagine the hook then the line is advice rather than a rule. Step four, three '
      + 'teeth from one failure: a memory-file line read at the start of every session, a hook '
      + 'enforced deterministically, and a reviewer check if it slips the first two. Step five, '
      + 'what the hook tells you later: a hook that never fires means either the line is working or '
      + 'the case is gone; a hook that fires constantly means the line is not being followed and '
      + 'should be rewritten; and provenance is what tells those two apart. Captions record that '
      + 'every rule carries the failure it came from with a date or issue number, that without it '
      + 'the instruction to remove rules that no longer apply has no way to identify them so the '
      + 'file only grows, and that the steady state grows on failure and shrinks on obsolescence.',
  };
}

module.exports = { ratchetMechanism, ratchetOverTime, lifeOfARule };

if (require.main === module) {
  emit('01-ratchet-mechanism', ratchetMechanism());
  emit('02-ratchet-over-time', ratchetOverTime());
  emit('03-life-of-a-rule', lifeOfARule());
}
