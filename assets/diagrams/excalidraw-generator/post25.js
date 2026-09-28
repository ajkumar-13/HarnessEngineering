// The post 25 diagrams, hand-drawn.
//
//   01-layered-harness   960 x 430  Mirror of the existing figure.
//   02-blast-radius      960 x 400  Mirror.
//   03-what-tests-miss   960 x 506  NEW, published: section 10 had no figure.
//
// Section 10 is the strongest section in the build and the one with no picture:
// three real bugs that shipped in this companion, each behind a green suite. The
// argument is not "here are three bugs", it is that the three share a shape --
// the test asserted one property and the defect lived in a different one. That
// pairing is what the figure draws, one row per bug, assertion beside blind spot.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function layered() {
  resetSeq();
  const W = 960, H = 434;

  const els = [...heading('Four bounded layers around a core that does not change',
    'Build #1 is untouched in the middle. Everything added is a gate the call passes through, or a span wrapped around it.')];

  // the tracer, outermost
  els.push(rect(40, 96, 880, 268, { stroke: T.neutral3, strokeWidth: 1, strokeStyle: 'dashed' }));
  els.push(text(56, 104, 'TRACER: every run, iteration, model call and tool call becomes a span',
    { size: 9, stroke: T.neutral3 }));

  // the core
  els.push(...card(370, 190, 220, 110, { spine: T.primary, strokeWidth: 1.8 }));
  els.push(text(386, 204, 'BUILD #1 CORE', { size: 12, stroke: T.ink }));
  ['the loop', 'the tool registry', 'the verification gate'].forEach((l, i) =>
    els.push(text(386, 228 + i * 17, fit(l, 9.5, 190, 'core'), { size: 9.5, stroke: T.inkMuted })));
  els.push(text(386, 282, 'unchanged', { size: 8.5, stroke: T.primary }));

  // the three gates, in order, to the left
  const GATES = [
    [T.alert, '1 HOOK', 'blocks before the call runs', 'deterministic, no model in the way'],
    [T.warn, '2 APPROVAL', 'pauses the irreversible', 'a human, or a stricter policy'],
    [T.accent, '3 SANDBOX', 'bounds what a call can reach', 'allow-list, jail, timeout'],
  ];
  GATES.forEach((g, i) => {
    const y = 132 + i * 78;
    els.push(...card(56, y, 280, 66, { spine: g[0] }));
    els.push(text(70, y + 10, g[1], { size: 11, stroke: T.ink }));
    els.push(text(70, y + 30, fit(g[2], 9.5, 250, 'gate a'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(70, y + 46, fit(g[3], 8.5, 250, 'gate b'), { size: 8.5, stroke: T.inkSubtle }));
    els.push(arrow([[340, y + 33], [366, 236]], { stroke: g[0], strokeWidth: 1.1 }));
  });

  // the sub-agent, right
  els.push(...card(624, 190, 280, 110, { spine: T.success }));
  els.push(text(638, 204, '4 SUB-AGENT', { size: 11, stroke: T.ink }));
  els.push(text(638, 228, fit('a delegate tool spawns a second', 9.5, 250, 'sub a'), { size: 9.5, stroke: T.inkMuted }));
  els.push(text(638, 244, fit('run in its own context window', 9.5, 250, 'sub b'), { size: 9.5, stroke: T.inkMuted }));
  els.push(text(638, 268, fit('the parent sees a result, not a transcript', 8.5, 250, 'sub c'), { size: 8.5, stroke: T.success }));
  els.push(arrow([[594, 240], [620, 240]], { stroke: T.success, strokeWidth: 1.1 }));

  els.push(text(M, 380, fit('Every tool call passes hook, then approval, then sandbox, in that order.', 11.5, 880, 'foot 1'),
    { size: 11.5, stroke: T.ink }));
  els.push(text(M, 402, fit('Block the obviously dangerous, escalate the merely sensitive, bound the rest.', 11.5, 880, 'foot 2'),
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Build #2 layers four hardening components onto Build #1',
    desc: 'A hand-drawn diagram of the four components Build number two adds. A dashed boundary '
      + 'encloses everything and is labelled as the tracer, which turns every run, iteration, model '
      + 'call and tool call into a span. In the centre sits the unchanged Build number one core: the '
      + 'loop, the tool registry and the verification gate. On the left, three gates stack in the '
      + 'order a call passes through them: a hook that blocks before the call runs, deterministically '
      + 'and with no model in the way; an approval gate that pauses the irreversible for a human or a '
      + 'stricter policy; and a sandbox that bounds what a call can reach with an allow-list, a jail '
      + 'and a timeout. Arrows run from each gate into the core. On the right, a fourth component, a '
      + 'sub-agent, is spawned by a delegate tool and runs in its own context window, so the parent '
      + 'sees a result rather than a transcript. A closing line records the order: hook, then '
      + 'approval, then sandbox, blocking the obviously dangerous, escalating the merely sensitive, '
      + 'and bounding the rest.',
  };
}

// ---------------------------------------------------------------- diagram 2
function blastRadius() {
  resetSeq();
  const W = 960, H = 604;

  const els = [...heading('The same wrong call, before and after',
    'Nothing about the model changed. What changed is how far a mistake travels.')];

  // left: build 1
  els.push(...card(M, 108, 420, 208, { spine: T.alert, strokeWidth: 1.6 }));
  els.push(text(56, 122, 'BUILD #1', { size: 13, stroke: T.ink }));
  els.push(text(56, 144, 'one deny-list, then execution', { size: 9, stroke: T.inkSubtle }));
  ['the whole filesystem', 'the network', 'irreversible actions'].forEach((l, i) => {
    els.push(rect(56, 168 + i * 40, 388, 30, { stroke: T.alert, fill: T.neutral1, strokeWidth: 1 }));
    els.push(text(68, 176 + i * 40, fit(l, 10, 360, 'reach'), { size: 10, stroke: T.ink }));
    els.push(text(300, 176 + i * 40, 'reachable', { size: 9, align: 'right', width: 132, stroke: T.alert }));
  });

  // right: build 2
  els.push(...card(500, 108, 420, 208, { spine: T.success, strokeWidth: 1.6 }));
  els.push(text(516, 122, 'BUILD #2', { size: 13, stroke: T.ink }));
  els.push(text(516, 144, 'hook, then approval, then sandbox', { size: 9, stroke: T.inkSubtle }));
  const STOPS = [
    [T.alert, 'a dangerous command', 'blocked by the hook'],
    [T.warn, 'an irreversible action', 'waits for approval'],
    [T.accent, 'out of jail, or not allow-listed', 'refused by the sandbox'],
  ];
  STOPS.forEach((s, i) => {
    els.push(rect(516, 168 + i * 40, 388, 30, { stroke: s[0], fill: T.surface, strokeWidth: 1 }));
    els.push(text(528, 176 + i * 40, fit(s[1], 10, 240, 'stop a'), { size: 10, stroke: T.ink }));
    els.push(text(760, 176 + i * 40, fit(s[2], 9, 132, 'stop b'),
      { size: 9, align: 'right', width: 132, stroke: s[0] }));
  });

  els.push(text(516, 292, fit('what is left reachable: one jailed workspace', 9.5, 388, 'left'),
    { size: 9.5, stroke: T.success }));

  els.push(arrow([[464, 212], [496, 212]], { stroke: T.ink, strokeWidth: 1.3 }));

  // --- second tier: what each of Build #2's three gates actually checks ---
  // Values read from the companion: DEFAULT_DENY in hooks.py and the Sandbox
  // dataclass defaults in sandbox.py.
  els.push(text(M, 330, 'WHAT THE THREE GATES ACTUALLY CHECK, AS THE COMPANION CONFIGURES THEM',
    { size: 10, stroke: T.inkSubtle }));

  els.push(...card(40, 350, 380, 196, { spine: T.alert, strokeWidth: 1.3 }));
  els.push(text(58, 358, '1  HOOK: THE DENY-LIST', { size: 9.5, stroke: T.alert }));
  els.push(text(58, 374, 'five patterns, matched before the tool runs', { size: 8.5, stroke: T.inkSubtle }));
  [['rm -rf /', 'recursive delete of a broad path'],
   ['git push --force', 'force-push'],
   ['DROP TABLE', 'destructive SQL'],
   [':(){ :|:& };:', 'fork bomb'],
   ['mkfs', 'filesystem format']].forEach((r, i) => {
    const y = 396 + i * 28;
    els.push(text(58, y, r[0], { size: 9, family: 3, stroke: T.ink }));
    els.push(text(58, y + 12, fit(r[1], 8.5, 340, 'deny why'), { size: 8.5, stroke: T.inkMuted }));
  });

  els.push(...card(438, 350, 220, 196, { spine: T.warn, strokeWidth: 1.3 }));
  els.push(text(456, 358, '2  APPROVAL', { size: 9.5, stroke: T.warn }));
  els.push(text(456, 374, 'the irreversible waits', { size: 8.5, stroke: T.inkSubtle }));
  ['A call the hook allows can', 'still be one nobody should', 'run unattended.', '',
   'The gate holds it until a', 'human answers, and the', 'run checkpoints rather', 'than blocking.']
    .forEach((l, i) => els.push(text(456, 398 + i * 17, fit(l, 9, 184, 'appr'),
      { size: 9, stroke: T.inkMuted })));

  els.push(...card(676, 350, 244, 196, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(694, 358, '3  SANDBOX', { size: 9.5, stroke: T.success }));
  els.push(text(694, 374, 'allow-list, jail, timeout', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(694, 396, 'echo  ls  cat  git', { size: 9.5, family: 3, stroke: T.ink }));
  els.push(text(694, 414, 'the whole allow-list', { size: 8.5, stroke: T.inkMuted }));
  els.push(rule(694, 904, 434));
  ['python and pytest are not on', 'it: allow-listing an interpreter',
   'allow-lists everything it can', 'run, so a caller that needs', 'them has to opt in.']
    .forEach((l, i) => els.push(text(694, 446 + i * 17, fit(l, 8.5, 208, 'sbx'),
      { size: 8.5, stroke: T.inkMuted })));

  els.push(text(M, 562, fit('The model is exactly as fallible in both panels.', 11.5, 880, 'foot 1'),
    { size: 11.5, stroke: T.ink }));
  els.push(text(M, 584, fit('The right-hand one collapses the worst case from "anything" to "a jailed workspace".', 11.5, 880, 'foot 2'),
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Blast radius before and after the Build #2 hardening',
    desc: 'A hand-drawn two-panel comparison. The left panel, Build number one, has one deny-list '
      + 'and then execution, and lists three things a wrong tool call can reach: the whole '
      + 'filesystem, the network, and irreversible actions, each marked reachable. The right panel, '
      + 'Build number two, applies a hook, then an approval gate, then a sandbox, and shows the same '
      + 'call being stopped at one of three places: a dangerous command is blocked by the hook, an '
      + 'irreversible action waits for approval, and a command that is out of the jail or not on the '
      + 'allow-list is refused by the sandbox. What is left reachable is one jailed workspace. An '
      + 'arrow runs from the left panel to the right. A closing line records that the model is '
      + 'exactly as fallible in both panels, and that the right-hand one collapses the worst case '
      + 'from anything to a jailed workspace. A second tier gives what each of the three gates '
      + 'actually checks, as the code companion configures them. The hook is a deny-list of '
      + 'five patterns matched before the tool runs: a recursive delete of a broad path, a '
      + 'force-push, destructive SQL, a fork bomb and a filesystem format. The approval gate '
      + 'holds a call the hook allowed but which nobody should run unattended, checkpointing '
      + 'the run rather than blocking it. The sandbox carries an allow-list of just echo, ls, '
      + 'cat and git, together with a working-directory jail and a timeout, and a note that '
      + 'python and pytest are deliberately absent because allow-listing an interpreter '
      + 'allow-lists everything it can run.',
  };
}

// ---------------------------------------------------------------- diagram 3
function whatTestsMiss() {
  resetSeq();
  const W = 960, H = 464;

  const els = [...heading('Three bugs that shipped behind a green suite',
    'Each test asserted a real property. In each case the defect lived in a different one.')];

  els.push(text(M, 96, 'THE LAYER', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(228, 96, 'WHAT THE TEST ASSERTED', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(508, 96, 'WHAT IT COULD NOT SEE', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(790, 96, 'THE GAP', { size: 8.5, stroke: T.inkSubtle }));

  const BUGS = [
    [T.accent, 'Sandbox', 'the allow-list',
      ['refuses what it should refuse,', 'allows what it should allow'],
      ['the raw string ran through a shell,', 'so one echo carried a second command'],
      ['tested with the traffic', 'you expect']],
    [T.primary, 'Tracer', 'the span tree',
      ['a run span exists, iterations', 'nest, tool spans appear'],
      ['every value in the tree: a sandbox', 'refusal was landing in ok'],
      ['asserted the shape,', 'never the contents']],
    [T.alert, 'Deny-list', 'the dangerous patterns',
      ['the five strings the regexes', 'were written from'],
      ['rm -fr /, rm -r -f /, git push -f:', 'the same command, respelled'],
      ['tested with its own', 'source material']],
  ];

  BUGS.forEach((b, i) => {
    const y = 112 + i * 96;
    els.push(...card(M, y, 880, 84, { spine: b[0] }));
    els.push(text(M + 16, y + 14, b[1], { size: 12, stroke: T.ink }));
    els.push(text(M + 16, y + 36, fit(b[2], 9, 170, 'layer sub'), { size: 9, stroke: T.inkSubtle }));

    b[3].forEach((l, j) => els.push(text(228, y + 16 + j * 16, fit(l, 9.5, 268, 'asserted'),
      { size: 9.5, stroke: T.ink })));
    els.push(text(228, y + 62, 'PASSES', { size: 8.5, stroke: T.success }));

    b[4].forEach((l, j) => els.push(text(508, y + 16 + j * 16, fit(l, 9.5, 268, 'missed'),
      { size: 9.5, stroke: T.inkMuted })));
    els.push(text(508, y + 62, 'SHIPPED ANYWAY', { size: 8.5, stroke: b[0] }));

    b[5].forEach((l, j) => els.push(text(790, y + 16 + j * 16, fit(l, 9, 130, 'gap'),
      { size: 9, stroke: b[0] })));

    els.push(rule(228, 768, y + 54));
  });

  els.push(text(M, 418, fit('A guardrail\'s tests have to be adversarial in the same way the guardrail is.', 12, 880, 'foot 1'),
    { size: 12, stroke: T.ink }));
  els.push(text(M, 440, fit('"Does this work?" verifies the feature. "How would you get past this?" verifies the boundary.', 11.5, 880, 'foot 2'),
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Three defects that survived a passing test suite, and the property each test missed',
    desc: 'A hand-drawn three-row table of bugs that shipped in this companion despite a green test '
      + 'suite, with columns for the layer, what the test asserted, what it could not see, and the '
      + 'gap between them. Row one, the sandbox allow-list: the tests asserted that it refuses what '
      + 'it should refuse and allows what it should allow, and passed; what they could not see was '
      + 'that the raw string ran through a shell, so one echo could carry a second command. The gap '
      + 'is that the boundary was tested with the traffic you expect. Row two, the tracer span tree: '
      + 'the tests asserted that a run span exists, that iterations nest and that tool spans appear, '
      + 'and passed; what they could not see was every value in the tree, so a sandbox refusal was '
      + 'landing in the ok outcome. The gap is that the tests asserted the shape and never the '
      + 'contents. Row three, the deny-list: the tests asserted the five strings the regular '
      + 'expressions were written from, and passed; what they could not see was that rm space minus '
      + 'fr slash, rm minus r minus f slash and git push minus f are the same commands respelled. '
      + 'The gap is that it was tested with its own source material. A closing pair of lines records '
      + 'that a guardrail\'s tests have to be adversarial in the same way the guardrail is: asking '
      + 'does this work verifies the feature, asking how would you get past this verifies the '
      + 'boundary, and only the first tends to get written.',
  };
}

emit('01-layered-harness', layered());
emit('02-blast-radius', blastRadius());
emit('03-what-tests-miss', whatTestsMiss());
