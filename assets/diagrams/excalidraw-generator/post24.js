// The post 24 diagrams, hand-drawn.
//
//   01-minimal-architecture  960 x 430  Mirror of the existing figure.
//   02-task-run-sequence     960 x 400  Mirror.
//   03-the-four-seams        960 x 470  NEW, published: section 9 had no figure.
//
// Section 9 is the build's central design claim -- that four injected seams make
// the swap to production cheap -- and it was carried by a four-row table alone.
// A seam is a thing with two sides, which is a shape a table states and a figure
// shows: the same slot, the double on the left, the live implementation on the
// right, and the blast radius that opens when you swap it.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function architecture() {
  resetSeq();
  const W = 960, H = 430;

  const els = [...heading('The minimal harness, four primitives wired together',
    'One loop at the centre. Tools on one side, the gate on the other, and four exits around all of it.')];

  // the loop, centre
  els.push(...card(360, 150, 240, 130, { spine: T.primary, strokeWidth: 1.8 }));
  els.push(text(376, 164, 'THE LOOP', { size: 13, stroke: T.ink }));
  els.push(text(376, 186, 'harness.py', { size: 9, stroke: T.inkSubtle }));
  ['reason: call the model', 'act: dispatch a tool', 'observe: append result'].forEach((l, i) =>
    els.push(text(376, 208 + i * 16, fit(l, 9.5, 210, 'loop step'), { size: 9.5, stroke: T.inkMuted })));

  // model, left
  els.push(...card(40, 168, 200, 94, { spine: T.neutral3 }));
  els.push(text(56, 182, 'MODEL', { size: 12, stroke: T.ink }));
  els.push(text(56, 202, 'models.py', { size: 9, stroke: T.inkSubtle }));
  els.push(text(56, 220, fit('ScriptedModel offline,', 9.5, 170, 'model a'), { size: 9.5, stroke: T.inkMuted }));
  els.push(text(56, 236, fit('AnthropicModel live', 9.5, 170, 'model b'), { size: 9.5, stroke: T.inkMuted }));
  els.push(arrow([[240, 200], [356, 200]], { stroke: T.ink, strokeWidth: 1.2 }));
  els.push(arrow([[356, 232], [240, 232]], { stroke: T.ink, strokeWidth: 1.2 }));

  // tools, right
  els.push(...card(720, 122, 200, 94, { spine: T.accent }));
  els.push(text(736, 136, 'TOOLS', { size: 12, stroke: T.ink }));
  els.push(text(736, 156, 'tools.py', { size: 9, stroke: T.inkSubtle }));
  els.push(text(736, 174, fit('schema-validated registry,', 9.5, 170, 'tools a'), { size: 9.5, stroke: T.inkMuted }));
  els.push(text(736, 190, fit('bash + write_file', 9.5, 170, 'tools b'), { size: 9.5, stroke: T.inkMuted }));
  els.push(arrow([[600, 180], [716, 168]], { stroke: T.ink, strokeWidth: 1.2 }));

  // gate, right-lower
  els.push(...card(720, 236, 200, 94, { spine: T.success }));
  els.push(text(736, 250, 'THE GATE', { size: 12, stroke: T.ink }));
  els.push(text(736, 270, 'verify.py', { size: 9, stroke: T.inkSubtle }));
  els.push(text(736, 288, fit('done means verified,', 9.5, 170, 'gate a'), { size: 9.5, stroke: T.inkMuted }));
  els.push(text(736, 304, fit('not declared', 9.5, 170, 'gate b'), { size: 9.5, stroke: T.inkMuted }));
  els.push(arrow([[600, 250], [716, 272]], { stroke: T.ink, strokeWidth: 1.2 }));
  els.push(text(424, 302, fit('a failure report goes back in', 9, 172, 'gate loop'),
    { size: 9, align: 'right', width: 172, stroke: T.success }));
  els.push(arrow([[716, 318], [600, 318], [600, 286]],
    { stroke: T.success, strokeWidth: 1.2, strokeStyle: 'dashed' }));

  // the four exits
  els.push(text(40, 318, 'THE FOUR EXITS', { size: 9, stroke: T.inkSubtle }));
  const EX = [['completed', T.success], ['max_iters', T.neutral3],
              ['budget', T.warn], ['no_progress', T.alert]];
  EX.forEach((e, i) => {
    els.push(rect(40 + i * 76, 336, 66, 22, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1 }));
    els.push(text(40 + i * 76, 342, fit(e[0], 8.5, 62, 'exit'),
      { size: 8.5, align: 'center', width: 66, stroke: e[1] }));
  });
  els.push(text(360, 342, fit('only the first returns verified work; the other three are backstops', 9.5, 560, 'exit note'),
    { size: 9.5, stroke: T.inkMuted }));

  els.push(text(40, 392, 'About 520 lines, of which 451 are the engine. Every seam is injected, so the whole thing runs offline.',
    { size: 11.5, stroke: T.ink }));

  return {
    W, H, els,
    title: 'The architecture of the minimal harness',
    desc: 'A hand-drawn block diagram of Build number one. At the centre sits the loop, in '
      + 'harness.py, running reason, act and observe. On the left a model component, models.py, '
      + 'offering a ScriptedModel for offline runs and an AnthropicModel for live ones, with arrows '
      + 'in both directions to the loop. On the upper right a tools component, tools.py, a '
      + 'schema-validated registry holding a bash tool and a write-file tool, receiving dispatched '
      + 'calls from the loop. On the lower right the verification gate, verify.py, where done means '
      + 'verified rather than declared; a dashed return arrow shows a failure report going back into '
      + 'the loop as the next observation. Along the bottom the four exits are drawn as four chips: '
      + 'completed, max_iters, budget and no_progress, with a note that only the first returns '
      + 'verified work and the other three are backstops. A closing line records that the build is '
      + 'about 520 lines, of which 451 are the engine, and that every seam is injected so the whole '
      + 'thing runs offline.',
  };
}

// ---------------------------------------------------------------- diagram 2
function taskRun() {
  resetSeq();
  const W = 960, H = 590;

  const els = [...heading('One task run: declared done, then actually done',
    'The gate is what separates the two, and the failure report is what makes the second attempt informed.')];

  const STEPS = [
    [40, T.alert, '1', 'The model writes', ['is_palindrome, gets it', 'wrong, and declares done'], 'DECLARED'],
    [275, T.warn, '2', 'The gate runs the tests', ['abc is judged a', 'palindrome: it fails'], 'FAILED'],
    [510, T.primary, '3', 'The report is injected', ['the model sees the case', 'it missed and rewrites'], 'INFORMED'],
    [745, T.success, '4', 'The gate re-runs', ['both cases pass, and', 'the run stops verified'], 'VERIFIED'],
  ];

  STEPS.forEach((s) => {
    const x = s[0];
    els.push(...card(x, 110, 175, 150, { spine: s[1], strokeWidth: s[5] === 'VERIFIED' ? 1.8 : 1.3 }));
    els.push(text(x + 14, 122, s[2], { size: 15, stroke: s[1] }));
    els.push(text(x + 14, 148, fit(s[3], 10.5, 150, 'step title'), { size: 10.5, stroke: T.ink }));
    s[4].forEach((l, i) => els.push(text(x + 14, 176 + i * 15, fit(l, 9, 150, 'step body'),
      { size: 9, stroke: T.inkMuted })));
    els.push(rule(x + 14, x + 161, 220));
    els.push(text(x + 14, 228, s[5], { size: 9, stroke: s[1] }));
    if (x < 745) els.push(arrow([[x + 178, 185], [x + 232, 185]], { stroke: T.ink, strokeWidth: 1.2 }));
  });

  // --- second tier: the five things the report can actually say ----------
  // Every string here is a format literal from verify.py in the companion, so
  // the figure shows the gate's real vocabulary rather than a summary of it.
  els.push(text(40, 288, 'WHAT "STRUCTURED" MEANS: THE FIVE REPORTS THE GATE CAN RETURN, FROM verify.py',
    { size: 10, stroke: T.inkSubtle }));

  els.push(...card(40, 308, 596, 176, { spine: T.warn, strokeWidth: 1.3 }));
  [['nothing was written', "no file was written at 'solution.py'"],
   ['it does not import', 'solution.py failed to import: SyntaxError'],
   ['the name is missing', "no callable named 'is_palindrome'"],
   ['a case raised', 'is_palindrome(...) raised TypeError'],
   ['a case is wrong', "is_palindrome('abc') == True, expected False"]].forEach((r, i) => {
    const y = 322 + i * 31;
    els.push(text(58, y, r[0], { size: 9, stroke: T.ink }));
    els.push(text(58, y + 13, fit(r[1], 8.5, 550, 'report'), { size: 8.5, family: 3, stroke: T.warn }));
  });

  els.push(...card(656, 308, 264, 176, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(674, 316, 'WHY IT HAS TO BE THIS', { size: 9, stroke: T.success }));
  ['A bare "failed" gives the model', 'nothing to correct against, so',
   'the second attempt is a guess', 'rather than a fix.', '',
   'Each line names the case, what', 'it returned and what was wanted:', 'the diff the rewrite needs.']
    .forEach((l, i) => els.push(text(674, 338 + i * 16, fit(l, 9, 228, 'why'),
      { size: 9, stroke: T.inkMuted })));

  els.push(text(40, 502, fit('Steps 2 and 3 are the whole point: a run that stopped at step 1 would have shipped a bug and reported success.', 11.5, 880, 'foot 1'),
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 530, fit('The report is structured, not a bare pass or fail, which is what lets the second attempt be a correction rather than a guess.', 11.5, 880, 'foot 2'),
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 558, fit('Victory declaration is the failure this shape exists to prevent.', 11.5, 880, 'foot 3'),
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'One full task run through the minimal harness',
    desc: 'A hand-drawn four-step sequence of a single task run. Step one: the model writes '
      + 'is_palindrome, gets it wrong, and declares the task done; the step is labelled DECLARED. '
      + 'Step two: the verification gate runs the tests and the case abc is judged a palindrome, so '
      + 'the gate fails; labelled FAILED. Step three: the failure report is injected back into the '
      + 'conversation, the model sees the case it missed and rewrites the function; labelled '
      + 'INFORMED. Step four: the gate re-runs, both cases pass, and the run stops as verified; '
      + 'labelled VERIFIED and drawn with a heavier border. Arrows connect the four steps left to '
      + 'right. A second tier lists the five reports the gate can actually return, taken from '
      + 'verify.py in the code companion: no file was written at the expected path; the file '
      + 'failed to import, with the exception named; no callable of the expected name was '
      + 'found; a case raised, with the exception named; and a case returned the wrong value, '
      + 'quoting what it returned and what was expected. A panel beside them explains why the '
      + 'report has to take this shape: a bare failure gives the model nothing to correct '
      + 'against, so the second attempt is a guess rather than a fix, while each of these '
      + 'lines names the case, what it returned and what was wanted. Captions record that '
      + 'steps two and three are the whole point, because a run that '
      + 'stopped at step one would have shipped a bug and reported success; that the report is '
      + 'structured rather than a bare pass or fail, which is what lets the second attempt be a '
      + 'correction rather than a guess; and that victory declaration is the failure this shape '
      + 'exists to prevent.',
  };
}

// ---------------------------------------------------------------- diagram 3
function fourSeams() {
  resetSeq();
  const W = 960, H = 506;

  const els = [...heading('The four seams, and what each one costs to swap',
    'Every seam is a slot with a double on one side and the real thing on the other. Swapping one is cheap; what it widens is not.')];

  els.push(text(M, 96, 'THE SEAM', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(232, 96, 'WHAT THE TESTS INJECT', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(486, 96, 'WHAT PRODUCTION INJECTS', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(742, 96, 'WHAT IT WIDENS', { size: 8.5, stroke: T.inkSubtle }));

  const SEAMS = [
    [T.primary, 'Model', 'ScriptedModel', 'a fixed list of replies',
      'AnthropicModel()', 'plus an install and a key',
      'the run becomes non-deterministic', 'and metered', false],
    [T.accent, 'Shell runner', 'a canned string', 'no process is started',
      'subprocess_runner', 'a real shell, shell=True',
      'commands execute, behind eight', 'regexes that are a pre-filter', true],
    [T.neutral3, 'Workspace', 'a dict of path to text', 'nothing touches disk',
      'not shipped', 'you write the durable one',
      'files outlive the run, and can be', 'overwritten or deleted', false],
    [T.success, 'Verifier', 'python_function_tests', 'in-process, instant',
      'a shell-out to the suite', 'seconds per gate call',
      'a timeout you must set, and a gate', 'slower than the work it guards', false],
  ];

  SEAMS.forEach((s, i) => {
    const y = 112 + i * 84;
    els.push(...card(M, y, 880, 74, { spine: s[0], strokeWidth: s[8] ? 1.8 : 1.2 }));
    els.push(text(M + 16, y + 16, s[1], { size: 12, stroke: T.ink }));
    if (s[8]) els.push(text(M + 16, y + 40, 'WIDEST', { size: 8, stroke: s[0] }));

    els.push(text(232, y + 16, fit(s[2], 10, 240, 'double'), { size: 10, stroke: T.ink }));
    els.push(text(232, y + 36, fit(s[3], 9, 240, 'double note'), { size: 9, stroke: T.inkMuted }));

    els.push(text(486, y + 16, fit(s[4], 10, 240, 'live'), { size: 10, stroke: T.ink }));
    els.push(text(486, y + 36, fit(s[5], 9, 240, 'live note'), { size: 9, stroke: T.inkMuted }));

    // the swap, drawn as the arrow between the two columns
    els.push(arrow([[452, y + 22], [478, y + 22]], { stroke: s[0], strokeWidth: 1.2 }));

    els.push(text(742, y + 16, fit(s[6], 9, 190, 'risk a'), { size: 9, stroke: s[0] }));
    els.push(text(742, y + 32, fit(s[7], 9, 190, 'risk b'), { size: 9, stroke: s[0] }));
  });

  els.push(text(M, 456, fit('Three seams swap in one file you write yourself; the workspace is the one Build #2 has to supply.', 11.5, 880, 'foot 1'),
    { size: 11.5, stroke: T.ink }));
  els.push(text(M, 478, fit('Cheap to swap is not the same as safe to swap: the runner is one line of code and the widest blast radius on the page.', 11.5, 880, 'foot 2'),
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The four injected seams of the minimal harness and the cost of swapping each',
    desc: 'A hand-drawn four-row table of the seams that make Build number one swappable, with '
      + 'columns for the seam, what the tests inject, what production injects, and what the swap '
      + 'widens. The model seam takes a ScriptedModel replaying a fixed list of replies in tests and '
      + 'an AnthropicModel plus an install and a key in production, which makes the run '
      + 'non-deterministic and metered. The shell-runner seam, drawn with a heavier border and '
      + 'marked WIDEST, takes a function returning a canned string in tests, starting no process, '
      + 'and subprocess_runner with a real shell in production, after which commands execute for '
      + 'real behind eight regular expressions that are a pre-filter rather than a boundary. The '
      + 'workspace seam takes a dictionary of path to text in tests, touching nothing on disk, and '
      + 'has no shipped live implementation, so you write the durable one yourself; files then '
      + 'outlive the run and can be overwritten or deleted. The verifier seam takes '
      + 'python_function_tests in-process and instant, and a shell-out to the project suite in '
      + 'production, costing seconds per gate call and needing a timeout. An arrow between the two '
      + 'middle columns marks the swap on every row. A closing line records that three seams swap in '
      + 'one file you write yourself, the workspace is the one Build number two has to supply, and '
      + 'that cheap to swap is not the same as safe to swap.',
  };
}

emit('01-minimal-architecture', architecture());
emit('02-task-run-sequence', taskRun());
emit('03-the-four-seams', fourSeams());
