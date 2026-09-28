// The post 04 diagrams, hand-drawn.
//
//   01-harness-gap           960 x 580  Mirror of the existing figure, densified.
//   02-cotraining-flywheel   960 x 582  Mirror, densified.
//   03-choose-model-order    960 x 470  NEW, published: section 6 had no figure.
//
// Section 6 is where the post stops arguing and tells you what to do, and it is
// an *ordered* procedure whose whole content is the order. A numbered ladder
// with the cost of each rung, plus the jump most teams actually make, says that
// in one look; five numbered paragraphs do not.
//
// Figures 1 and 2 were single-band layouts that carried the vivid number and
// none of the firm ones. Both now carry a second tier: figure 1 puts the score
// beside the rank and grades the four pieces of evidence behind them, and
// figure 2 puts the three published measurements of the flywheel under the
// cycle. Every number in both comes from the post's own prose (sections 2, 3,
// 4, 5 and 7); nothing here is estimated.

const { T, rect, ellipse, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, wrap, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function harnessGap() {
  resetSeq();
  const W = 960, H = 580;

  const els = [...heading('The harness gap: one model, two harnesses',
    'Same weights, same 89 tasks: the harness alone moved the score 52.8% to 66.5%, and the rank about #30 to about #5.')];

  els.push(text(40, 84, 'SAME MODEL: gpt-5.2-codex.   SAME BENCHMARK: 89 CONTAINERISED TASKS.   ONLY THE HARNESS CHANGED.',
    { size: 10, stroke: T.inkSubtle }));

  // --- panel A: the vivid number, which is the rank ------------------------
  els.push(...card(40, 100, 560, 190, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(62, 110, 'THE VIVID NUMBER: LEADERBOARD RANK', { size: 10, stroke: T.inkSubtle }));

  els.push(text(145, 132, 'about 25 leaderboard places',
    { size: 11.5, align: 'center', width: 355, stroke: T.accent }));
  els.push(line([[145, 152], [500, 152]], { stroke: T.accent, strokeWidth: 1.3, roughness: 0.4 }));
  els.push(line([[145, 152], [145, 164]], { stroke: T.accent, strokeWidth: 1.3, roughness: 0.4 }));
  els.push(line([[500, 152], [500, 164]], { stroke: T.accent, strokeWidth: 1.3, roughness: 0.4 }));

  els.push(line([[80, 196], [575, 196]], { stroke: T.inkSubtle, strokeWidth: 1.3 }));
  els.push(text(80, 204, 'worse', { size: 10, stroke: T.inkSubtle }));
  els.push(text(515, 204, 'better', { size: 10, align: 'right', width: 60, stroke: T.inkSubtle }));
  els.push(text(80, 218, 'leaderboard rank on Terminal-Bench 2.0',
    { size: 10, align: 'center', width: 495, stroke: T.inkSubtle }));

  const marker = (x, tint) => [
    line([[x, 182], [x, 210]], { stroke: tint, strokeWidth: 1.5, roughness: 0.4 }),
    ellipse(x - 12, 184, 24, 24, { stroke: tint, fill: tint, strokeWidth: 1.0 }),
    line([[x, 212], [x, 236]], { stroke: T.inkSubtle, strokeWidth: 1.0, strokeStyle: 'dotted' }),
  ];
  els.push(...marker(145, T.neutral3));
  els.push(...marker(500, T.success));

  els.push(...card(62, 236, 178, 44, { spine: T.neutral3, strokeWidth: 1.3 }));
  els.push(text(84, 244, 'Default harness', { size: 12, stroke: T.ink }));
  els.push(text(84, 262, 'about rank 30', { size: 10, stroke: T.inkMuted }));

  els.push(...card(396, 236, 178, 44, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(418, 244, 'Tuned harness', { size: 12, stroke: T.ink }));
  els.push(text(418, 262, 'about rank 5', { size: 10, stroke: T.inkMuted }));

  // --- panel B: the firmer number, which is the score ----------------------
  els.push(...card(620, 100, 300, 190, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(642, 110, 'THE FIRMER NUMBER: RESOLVED RATE', { size: 10, stroke: T.inkSubtle }));

  els.push(text(642, 134, 'DEFAULT HARNESS', { size: 9, stroke: T.inkSubtle }));
  els.push(rect(642, 148, 256, 20, { stroke: T.border, fill: T.neutral1, strokeWidth: 1.0 }));
  els.push(rect(642, 148, 135, 20, { stroke: T.neutral3, fill: T.neutral2, strokeWidth: 1.0 }));
  els.push(text(642, 152, '52.8%', { size: 11, align: 'right', width: 127, stroke: T.onAccent }));

  els.push(text(642, 180, 'TUNED HARNESS', { size: 9, stroke: T.inkSubtle }));
  els.push(rect(642, 194, 256, 20, { stroke: T.border, fill: T.neutral1, strokeWidth: 1.0 }));
  els.push(rect(642, 194, 170, 20, { stroke: T.success, fill: T.success, strokeWidth: 1.0 }));
  els.push(text(642, 198, '66.5%', { size: 11, align: 'right', width: 162, stroke: T.onAccent }));

  els.push(text(642, 226, fit('+13.7 points, model held fixed', 11.5, 256, 'score delta'),
    { size: 11.5, stroke: T.success }));
  els.push(text(642, 248, fit('bar length is the share of the 89 tasks resolved', 9, 256, 'scale note'),
    { size: 9, stroke: T.inkSubtle }));
  els.push(text(642, 264, fit('the rank move on the left is this same result', 9, 256, 'scale note'),
    { size: 9, stroke: T.inkSubtle }));

  // --- the evidence behind both numbers, graded ----------------------------
  els.push(text(40, 300, 'THE EVIDENCE BEHIND THE PICTURE, STRONGEST FIRST',
    { size: 10, stroke: T.inkSubtle }));

  const EV = [
    ['1', 'Before and after', '+13.7 points',
      'A before-and-after with the weights pinned: 52.8% to 66.5% resolved on 89 tasks.',
      'Trivedy, LangChain, 2026', T.success],
    ['2', 'Controlled study', 'up to 28 points',
      'Three scaffolds against five models on GAIA, tasks and attempts held fixed.',
      'Starace, 2026', T.primary],
    ['3', 'Peer-reviewed', '12.5% vs 3.8%',
      'Interface design alone, on the full SWE-bench test set, GPT-4 Turbo fixed.',
      'Yang et al., 2024', T.primary],
    ['4', 'Reported multiple', 'about 6x',
      'A secondary write-up: model, benchmark and base are not stated. A direction only.',
      'MindStudio, 2026', T.neutral3],
  ];

  EV.forEach((e, i) => {
    const x = 40 + i * 222;
    els.push(...card(x, 318, 214, 140, { spine: e[5], strokeWidth: 1.3 }));
    els.push(rect(x + 14, 332, 26, 20, { stroke: e[5], fill: e[5], strokeWidth: 1.0 }));
    els.push(text(x + 14, 334, e[0], { size: 11, align: 'center', width: 26, stroke: T.onAccent }));
    els.push(text(x + 48, 330, fit(e[1], 13, 152, 'evidence title'), { size: 13, stroke: T.ink }));
    els.push(rule(x + 14, x + 200, 362));
    els.push(text(x + 14, 372, fit(e[2], 16, 182, 'evidence number'), { size: 16, stroke: e[5] }));
    els.push(text(x + 14, 398, wrap(e[3], 9.5, 182, 3), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(x + 14, 436, fit(e[4], 9, 182, 'evidence source'), { size: 9, stroke: T.inkSubtle }));
  });

  // --- the deduction -------------------------------------------------------
  els.push(rect(40, 472, 236, 52, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.5 }));
  els.push(text(40, 490, 'Agent = Model + Harness',
    { size: 15, align: 'center', width: 236, stroke: T.ink }));

  els.push(text(296, 476,
    fit('A fixed model cannot move 13.7 points on a fixed benchmark: the harness is the lever.', 11.5, 624, 'deduction'),
    { size: 11.5, stroke: T.ink }));
  els.push(text(296, 498, 'The gap you are looking at is usually a harness gap.',
    { size: 11.5, stroke: T.inkMuted }));

  els.push(text(40, 536,
    fit('Score and change list: Trivedy (LangChain, 2026). Rank via Faros AI (2026). Scaffold study: Starace (2026). Interface result: Yang et al. (2024).', 10, 880, 'attribution'),
    { size: 10, stroke: T.inkSubtle }));
  els.push(text(40, 554,
    fit('Terminal-Bench 2.1 has since revised 28 of the 2.0 tasks, so treat every reported figure as a snapshot and measure your own harness (Post 22).', 10, 880, 'attribution'),
    { size: 10, stroke: T.inkSubtle }));

  return {
    W, H, els,
    title: 'One model at two leaderboard ranks and two scores, moved by the harness alone',
    desc: 'A hand-drawn two-panel figure over a graded evidence row. The left panel is the vivid '
      + 'number: a leaderboard-rank axis for Terminal-Bench 2.0 running from worse on the left to '
      + 'better on the right, with a grey marker for the default harness at about rank 30 and a '
      + 'green marker for the tuned harness at about rank 5, spanned by a bracket labelled about 25 '
      + 'leaderboard places. The right panel is the firmer number: two horizontal bars on a common '
      + 'scale showing the share of the 89 containerised tasks resolved, 52.8 percent for the '
      + 'default harness and 66.5 percent for the tuned one, a gain of 13.7 points with the model '
      + 'held fixed at gpt-5.2-codex. Below, four cards grade the evidence strongest first. One, a '
      + 'before-and-after with the weights pinned, worth plus 13.7 points, reported by Trivedy at '
      + 'LangChain in 2026. Two, a controlled study of three scaffolds against five models on GAIA '
      + 'worth up to 28 points, from Starace in 2026. Three, a peer-reviewed interface-only result '
      + 'of 12.5 percent against 3.8 percent on SWE-bench with GPT-4 Turbo fixed, from Yang and '
      + 'colleagues in 2024. Four, a reported multiple of about six times whose model, benchmark '
      + 'and base are not stated, from MindStudio in 2026, marked as a direction rather than a '
      + 'number. A box reads Agent equals Model plus Harness, beside the deduction that a fixed '
      + 'model cannot move 13.7 points on a fixed benchmark, so the harness is the lever and the '
      + 'gap you are looking at is usually a harness gap. Footnotes attribute each figure and note '
      + 'that Terminal-Bench 2.1 has since revised 28 of the 2.0 tasks, so every reported figure is '
      + 'a snapshot and you should measure your own harness.',
  };
}

// ---------------------------------------------------------------- diagram 2
function flywheel() {
  resetSeq();
  const W = 960, H = 582;

  const els = [...heading('The model-harness co-training flywheel',
    'Useful harness patterns become training signal for the next model. The loop has been run deliberately, and measured.')];

  const STEPS = [
    [44, 98, '1', 'A pattern is found', 'bash as a universal tool, plan', 'files, hooks, a tool-call shape', T.primary],
    [320, 98, '2', 'It is standardised', 'into a product or an SDK: Claude', 'Code, the Codex harness', T.primary],
    [320, 242, '3', 'The next model trains', 'against traces full of that', 'pattern, and learns it as a skill', T.success],
    [44, 242, '4', 'The model gets better', 'at using it, and the next harness', 'exploits the improvement', T.success],
  ];
  STEPS.forEach((s) => {
    els.push(...card(s[0], s[1], 236, 88, { spine: s[6], strokeWidth: 1.3 }));
    els.push(rect(s[0] + 16, s[1] + 12, 22, 17, { stroke: s[6], fill: s[6], strokeWidth: 1.0 }));
    els.push(text(s[0] + 16, s[1] + 14, s[2], { size: 10, align: 'center', width: 22, stroke: T.onAccent }));
    els.push(text(s[0] + 46, s[1] + 11, fit(s[3], 12, 176, 'step title'), { size: 12, stroke: T.ink }));
    els.push(text(s[0] + 16, s[1] + 42, fit(s[4], 9.5, 204, 'step gloss'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(s[0] + 16, s[1] + 58, fit(s[5], 9.5, 204, 'step gloss'), { size: 9.5, stroke: T.inkMuted }));
  });

  els.push(arrow([[284, 142], [316, 142]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(arrow([[438, 190], [438, 238]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(arrow([[316, 286], [284, 286]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(arrow([[162, 238], [162, 190]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(text(48, 336, 'and it repeats, every model generation', { size: 11, stroke: T.inkMuted }));

  // --- why the native harness feels different ------------------------------
  els.push(...card(596, 98, 324, 232, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(618, 108, 'WHY A MODEL FEELS DIFFERENT', { size: 10, stroke: T.inkSubtle }));
  els.push(text(618, 124, 'IN ITS NATIVE HARNESS', { size: 10, stroke: T.inkSubtle }));
  els.push(text(618, 148, wrap('The same weights, dropped into a generic harness, are not the same experience: the model and the harness were shaped together.', 11, 280, 4),
    { size: 11, stroke: T.ink }));
  els.push(rule(618, 898, 202));
  els.push(text(618, 212, 'WHAT FOLLOWS', { size: 9, stroke: T.inkSubtle }));
  els.push(text(618, 228, wrap('A pattern you invent today may be a native model capability one generation later.', 9.5, 280, 2),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(618, 260, wrap('The patterns taken from the native harness are the ones the model is best at.', 9.5, 280, 2),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(618, 292, wrap('Fit, not branding: a harness tuned for your model beats a native SDK you never measured.', 9.5, 280, 2),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(596, 336, 'after Osmani, 2026', { size: 9.5, stroke: T.inkSubtle }));

  // --- the loop, measured --------------------------------------------------
  els.push(text(40, 364, 'THE FLYWHEEL, MEASURED: THREE PUBLISHED RESULTS',
    { size: 10, stroke: T.inkSubtle }));

  const MEASURED = [
    ['Steps 1-2: the pattern pays', '+8.1 points',
      'Automatically discovered procedural scaffolds lift the passed rate on the FeatureBench task set, before anything is distilled.',
      'Ding et al., 2026', T.primary],
    ['Steps 3-4: it enters the weights', '85.2% retained',
      'After the discovered scaffolds are distilled into the weights, the model passes 27.7% with no external scaffold at all.',
      'Ding et al., 2026', T.success],
    ['The consequence: fit, not brand', '33% to 53%',
      'Per-model harness profiles moved tau2-bench for one model, and 43% to 53% for another: ten to twenty points from fit alone.',
      'Trivedy and Daugherty, 2026', T.accent],
  ];

  MEASURED.forEach((m, i) => {
    const x = 40 + i * 299;
    els.push(...card(x, 380, 282, 136, { spine: m[4], strokeWidth: 1.3 }));
    els.push(text(x + 16, 392, fit(m[0], 12, 250, 'measured title'), { size: 12, stroke: T.ink }));
    els.push(rule(x + 16, x + 266, 414));
    els.push(text(x + 16, 424, fit(m[1], 16, 250, 'measured number'), { size: 16, stroke: m[4] }));
    els.push(text(x + 16, 452, wrap(m[2], 9.5, 250, 3), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(x + 16, 492, fit(m[3], 9, 250, 'measured source'), { size: 9, stroke: T.inkSubtle }));
  });

  els.push(text(40, 532, 'The flywheel is why "just use the best model" quietly underrates the harness.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 554, 'The best model was co-trained with a harness you may not be running.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The four-step co-training flywheel, with the three published results that measure it',
    desc: 'A hand-drawn four-step cycle over a row of measured results. One, a pattern is found: '
      + 'bash as a universal tool, plan files, hooks, a tool-call shape. Two, it is standardised '
      + 'into a product or an SDK, such as Claude Code or the Codex harness. Three, the next model '
      + 'trains against traces full of that pattern and learns it as a skill. Four, the model gets '
      + 'better at using it, and the next harness exploits the improvement, which returns to step '
      + 'one. A note records that the cycle repeats every model generation. A panel on the right '
      + 'explains why a model feels different in its native harness: the same weights dropped into '
      + 'a generic harness are not the same experience, because the model and the harness were '
      + 'shaped together. Three things follow: a pattern you invent today may be a native model '
      + 'capability one generation later; the patterns taken from the native harness are the ones '
      + 'the model is best at; and it is fit rather than branding that matters, because a harness '
      + 'tuned for your model beats a native SDK you never measured. Beneath the cycle, three cards '
      + 'carry the published measurements of the loop. Steps one and two: automatically discovered '
      + 'procedural scaffolds lift the FeatureBench passed rate by 8.1 points before anything is '
      + 'distilled, from Ding and colleagues in 2026. Steps three and four: after those scaffolds '
      + 'are distilled into the weights the model retains 85.2 percent of the scaffolded '
      + 'performance, passing 27.7 percent with no external scaffold at all, from the same paper. '
      + 'The consequence: per-model harness profiles moved tau2-bench from 33 to 53 percent for one '
      + 'model and from 43 to 53 percent for another, ten to twenty points from fit alone, reported '
      + 'by Trivedy and Daugherty in 2026. Captions record that the flywheel is why the advice to '
      + 'just use the best model quietly underrates the harness, since the best model was '
      + 'co-trained with a harness you may not be running.',
  };
}

// ---------------------------------------------------------------- diagram 3
function chooseModelOrder() {
  resetSeq();
  const W = 960, H = 470;

  const els = [...heading('When an agent underperforms, in order',
    'Accepting the claim does not mean ignoring model choice. It means ordering the moves correctly.')];

  const RUNGS = [
    ['1', 'Diagnose first (Post 05)',
      'Name the failure mode. If it is one of the six harness-fixable ones, a bigger model is the wrong tool.',
      'free, and minutes', T.primary],
    ['2', 'Exhaust the cheap harness fixes',
      'A verification loop, a stop condition, a hook: hours of work, and where the reported moves came from.',
      'hours', T.primary],
    ['3', 'Use the model native harness',
      'The flywheel means a model performs best in its own SDK; a generic wrapper leaves capability behind.',
      'one migration', T.primary],
    ['4', 'Only now, upgrade the model',
      'The information is in the window, in the right place, and the model still cannot reason through it.',
      'more per token, forever', T.alert],
    ['5', 'Re-measure after every change (Post 22)',
      'Every figure in this post, and yours, is a measurement rather than a law.',
      'an afternoon per change', T.success],
  ];

  RUNGS.forEach((r, i) => {
    const y = 94 + i * 62;
    els.push(...card(40, y, 640, 54, { spine: r[4], strokeWidth: i === 3 ? 1.6 : 1.2 }));
    els.push(ellipse(52, y + 14, 26, 26, { stroke: r[4], fill: r[4], strokeWidth: 1.1 }));
    els.push(text(52, y + 20, r[0], { size: 12, align: 'center', width: 26, stroke: T.onAccent }));
    els.push(text(92, y + 6, fit(r[1], 12.5, 292, 'rung title'), { size: 12.5, stroke: T.ink }));
    els.push(text(496, y + 8, fit(r[3], 10, 164, 'rung cost'),
      { size: 10, align: 'right', width: 164, stroke: r[4] }));
    els.push(text(92, y + 30, fit(r[2], 9.5, 570, 'rung gloss'), { size: 9.5, stroke: T.inkMuted }));
  });

  // The move most teams actually make.
  els.push(arrow([[686, 121], [736, 146], [736, 258], [686, 283]],
    { stroke: T.alert, strokeWidth: 1.5, strokeStyle: 'dashed' }));
  els.push(text(748, 172, 'the common move:', { size: 10, stroke: T.alert }));
  els.push(text(748, 188, 'skip straight to step 4,', { size: 10, stroke: T.alert }));
  els.push(text(748, 204, 'which is also the most', { size: 10, stroke: T.alert }));
  els.push(text(748, 220, 'expensive one', { size: 10, stroke: T.alert }));

  els.push(text(40, 420,
    'The order is the whole point. Reaching for step 4 first is the most common and most expensive mistake in the field:',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 442,
    'you pay more per token, forever, to paper over a gap that a stop condition would have closed for free.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The five ordered moves when an agent underperforms, with the cost of each',
    desc: 'A hand-drawn ladder of five numbered rungs, each with the cost of taking it. One, '
      + 'diagnose first: name the failure mode, because if it is one of the six harness-fixable '
      + 'ones then a bigger model is the wrong tool; the cost is free and minutes. Two, exhaust the '
      + 'cheap harness fixes, meaning a verification loop, a stop condition or a hook, which is '
      + 'hours of work rather than a re-architecture and is where the reported leaderboard moves '
      + 'came from; the cost is hours. Three, use the model native harness where you can, because '
      + 'the co-training flywheel means the frontier model performs best in its own SDK and a '
      + 'generic wrapper leaves capability on the table; the cost is one migration. Four, only now '
      + 'upgrade the model, when the right information is in the window in the right place and the '
      + 'model still cannot reason through the task; the cost is more per token, forever. Five, '
      + 're-measure after every change, since every figure is a measurement rather than a law; the '
      + 'cost is an afternoon per change. A dashed red arrow curves from rung one straight down to '
      + 'rung four, labelled as the common move: skip straight to step four, which is also the most '
      + 'expensive one. Captions record that the order is the whole point, and that skipping ahead '
      + 'means paying more per token forever to paper over a gap a stop condition would have closed '
      + 'for free.',
  };
}

module.exports = { harnessGap, flywheel, chooseModelOrder };

if (require.main === module) {
  emit('01-harness-gap', harnessGap());
  emit('02-cotraining-flywheel', flywheel());
  emit('03-choose-model-order', chooseModelOrder());
}
