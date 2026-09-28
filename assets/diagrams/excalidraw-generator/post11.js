// The post 11 diagrams, hand-drawn.
//
//   01-verification-gate         960 x 560  The gate, plus one real run of the companion loop.
//   02-compounding-vs-failfast   960 x 612  The five-step comparison, plus the priced ledger.
//   03-verifier-ladder           960 x 490  NEW, published: sections 2, 3 and 6 had no figure.
//
// Section 2 ranks the kinds of ground truth and section 6 says how often to run
// each, and those are the same table seen from two sides. Drawing it also puts
// section 3's point where it belongs: self-critique is not a weaker gate, it is
// on the other side of a line, along with the judge.
//
// Figures 1 and 2 each carry a second tier, because the mechanism alone is thin.
// Figure 1's is a real trace of code/11-verification-loop, verbatim reports and
// all. Figure 2's is section 5's token ledger, which is the series' running
// example and is labelled in the figure as illustrative rather than measured.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function verificationGate() {
  resetSeq();
  const W = 960, H = 560;

  const els = [...heading('The loop with a verification gate',
    'Nothing exits on "final answer" alone: a gate checks the work against ground truth, and a failure goes back in.')];

  els.push(text(40, 84, 'THE GATE ON THE LOOP EXIT', { size: 9, stroke: T.inkSubtle }));
  els.push(text(660, 84, 'THE TWO WAYS A RUN CAN END', { size: 9, stroke: T.inkSubtle }));

  // --- the loop ------------------------------------------------------------
  els.push(...card(40, 100, 236, 152, { spine: T.primary, strokeWidth: 1.5 }));
  els.push(text(60, 110, 'THE LOOP', { size: 13.5, stroke: T.ink }));
  els.push(text(60, 130, 'reason, act, observe', { size: 9.5, stroke: T.inkMuted }));
  els.push(rule(56, 262, 150));
  els.push(text(60, 160, fit('the loop stops on a bare', 10.5, 200, 'loop line'),
    { size: 10.5, stroke: T.ink }));
  els.push(text(60, 178, fit('final answer, which means', 10.5, 200, 'loop line'),
    { size: 10.5, stroke: T.ink }));
  els.push(text(60, 196, fit('only that the model believes', 10.5, 200, 'loop line'),
    { size: 10.5, stroke: T.ink }));
  els.push(text(60, 214, fit('it is finished', 10.5, 200, 'loop line'),
    { size: 10.5, stroke: T.ink }));
  els.push(text(60, 234, fit('the victory-declaration failure', 9, 200, 'loop ref'),
    { size: 9, stroke: T.inkSubtle }));

  els.push(arrow([[278, 176], [344, 176]], { stroke: T.ink, strokeWidth: 1.5 }));
  els.push(text(288, 152, 'candidate', { size: 9.5, stroke: T.inkMuted }));

  // --- the gate ------------------------------------------------------------
  els.push(rect(346, 100, 244, 152, { stroke: T.ink, fill: T.surface, strokeWidth: 1.8 }));
  els.push(text(346, 112, 'VERIFY', { size: 16, align: 'center', width: 244, stroke: T.ink }));
  els.push(text(346, 138, 'ground truth, outside the model',
    { size: 9, align: 'center', width: 244, stroke: T.inkMuted }));
  els.push(rule(362, 574, 160));
  els.push(text(362, 170, fit('tests and types, every step', 10.5, 212, 'gate line'),
    { size: 10.5, stroke: T.success }));
  els.push(text(362, 192, fit('a schema on every result', 10.5, 212, 'gate line'),
    { size: 10.5, stroke: T.primary }));
  els.push(text(362, 214, fit('a judge, at checkpoints only', 10.5, 212, 'gate line'),
    { size: 10.5, stroke: T.warn }));
  els.push(text(362, 234, fit('the agent must not be able to edit it', 9, 212, 'gate note'),
    { size: 9, stroke: T.inkSubtle }));

  // --- the two endings -----------------------------------------------------
  els.push(arrow([[592, 138], [656, 138]], { stroke: T.success, strokeWidth: 1.5 }));
  els.push(text(604, 116, 'pass', { size: 9, stroke: T.success }));
  els.push(rect(660, 106, 260, 62, { stroke: T.success, fill: T.surface, strokeWidth: 1.8 }));
  els.push(text(660, 114, 'DONE', { size: 15, align: 'center', width: 260, stroke: T.success }));
  els.push(text(660, 140, 'the work is verified, not merely claimed',
    { size: 9, align: 'center', width: 260, stroke: T.inkMuted }));

  els.push(arrow([[592, 214], [656, 214]], { stroke: T.alert, strokeWidth: 1.5 }));
  els.push(text(600, 192, 'cap hit', { size: 9, stroke: T.alert }));
  els.push(rect(660, 188, 260, 64, { stroke: T.alert, fill: T.surface, strokeWidth: 1.8 }));
  els.push(text(660, 196, 'UNVERIFIED', { size: 15, align: 'center', width: 260, stroke: T.alert }));
  els.push(text(660, 222, 'after max_attempts: flag it, roll back',
    { size: 9, align: 'center', width: 260, stroke: T.inkMuted }));
  els.push(text(660, 236, 'or escalate, and count it either way',
    { size: 9, align: 'center', width: 260, stroke: T.inkMuted }));

  // --- the failure path ----------------------------------------------------
  els.push(arrow([[468, 254], [468, 282], [158, 282], [158, 254]],
    { stroke: T.alert, strokeWidth: 1.5 }));
  els.push(text(176, 288, 'fail: the report is injected back as the next observation',
    { size: 9.5, stroke: T.alert }));

  // --- tier two: a real run of the companion ------------------------------
  els.push(text(40, 312, 'ONE RUN OF THAT LOOP, FROM THE COMPANION', { size: 9, stroke: T.inkSubtle }));
  els.push(text(530, 312, 'WHEN THE ATTEMPTS RUN OUT', { size: 9, stroke: T.inkSubtle }));

  els.push(...card(40, 328, 470, 176, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 336, fit('code/11-verification-loop, run offline', 10, 436, 'trace head'),
    { size: 10, stroke: T.primary }));
  els.push(text(58, 352, fit('7 (args, expected) cases for is_prime, max_attempts = 5', 9, 436, 'trace sub'),
    { size: 9, stroke: T.inkSubtle }));
  els.push(rule(56, 494, 366));

  const attempt = (y, n, tint, code, verdict) => {
    const out = [rect(58, y, 22, 17, { stroke: tint, fill: tint, strokeWidth: 1 })];
    out.push(text(58, y + 2, n, { size: 10, align: 'center', width: 22, stroke: T.onAccent }));
    out.push(text(88, y - 2, fit(code, 10.5, 400, 'attempt code'), { size: 10.5, stroke: T.ink }));
    out.push(text(88, y + 16, fit(verdict, 9, 400, 'attempt verdict'), { size: 9, stroke: tint }));
    return out;
  };
  els.push(...attempt(372, '1', T.alert, 'all(n % d for d in range(2, n))',
    'FAIL   is_prime(1,) == True, expected False'));
  els.push(...attempt(408, '2', T.alert, 'all(n % d for d in range(2, int(n**0.5) + 1))',
    'FAIL   faster, and the same report again, unchanged'));
  els.push(...attempt(444, '3', T.success, 'n > 1 and all(n % d for d in range(2, int(n**0.5) + 1))',
    'PASS   all 7 cases; solve returns verified on attempt 3'));
  els.push(rule(56, 494, 478));
  els.push(text(58, 484,
    fit('The report names the case, what came back, and what was expected.', 9, 436, 'trace foot'),
    { size: 9, stroke: T.inkMuted }));

  els.push(...card(530, 328, 390, 176, { spine: T.alert, strokeWidth: 1.3 }));
  els.push(text(548, 336, fit('THREE REAL EXITS', 10, 354, 'exit head'), { size: 10, stroke: T.alert }));
  els.push(text(548, 352, fit('a cap is not a result, and each one is counted', 9, 354, 'exit sub'),
    { size: 9, stroke: T.inkSubtle }));
  els.push(rule(546, 904, 366));

  const exitRow = (y, name, gloss) => [
    text(548, y, fit(name, 11, 354, 'exit name'), { size: 11, stroke: T.ink }),
    text(548, y + 16, fit(gloss, 8.5, 354, 'exit gloss'), { size: 8.5, stroke: T.inkMuted }),
  ];
  els.push(...exitRow(372, 'Surface it, flagged unverified', 'the caller decides whether to ship it'));
  els.push(...exitRow(408, 'Roll back to a checkpoint', 'which is why you checkpoint each verified step'));
  els.push(...exitRow(444, 'Escalate to a human', 'approval for what a rollback cannot undo'));
  els.push(rule(546, 904, 478));
  els.push(text(548, 484,
    fit('A loop that quietly gives up looks exactly like one that never ran.', 8.5, 354, 'exit foot'),
    { size: 8.5, stroke: T.inkMuted }));

  els.push(text(40, 516, 'The gate separates the model believing it is done from the work being done.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 538, 'Success is silent; failures are verbose, because the report is what the next attempt corrects against.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A verification gate on the loop exit, with a real run of the companion loop beneath it',
    desc: 'A hand-drawn figure in two tiers. Along the top, the loop, running reason, act and '
      + 'observe, stops on a bare final answer, which means only that the model believes it is '
      + 'finished: the victory-declaration failure. An arrow carries that candidate into a VERIFY '
      + 'box holding ground truth outside the model, listed as tests and types on every step, a '
      + 'schema on every result, and a judge at checkpoints only, with a note that the agent must '
      + 'not be able to edit it. A green arrow marked pass leads to a DONE box, where the work is '
      + 'verified rather than merely claimed. A red arrow marked cap hit leads to an UNVERIFIED '
      + 'box, where after max_attempts the run is flagged, rolled back or escalated, and counted '
      + 'either way. A red path runs from under the verify box back into the loop, marked fail: '
      + 'the report is injected back as the next observation. The lower tier shows one real run of '
      + 'that loop from the code companion, run offline over seven argument-and-expected pairs for '
      + 'is_prime with max_attempts set to five. Attempt one, all n modulo d for d in range two to '
      + 'n, fails with the report is_prime of one equals True, expected False. Attempt two, the '
      + 'same expression bounded by the square root, is faster and fails with the same report '
      + 'again, unchanged. Attempt three, guarded by n greater than one, passes all seven cases, '
      + 'and solve returns verified on attempt three. A note records that the report names the '
      + 'case, what came back and what was expected. Beside it, three real exits for when the '
      + 'attempts run out, because a cap is not a result: surface the work flagged unverified and '
      + 'let the caller decide, roll back to a checkpoint, which is why you checkpoint each '
      + 'verified step, or escalate to a human, since approval is for what a rollback cannot undo. '
      + 'A loop that quietly gives up looks exactly like one that never ran. Captions record that '
      + 'the gate separates the model believing it is done from the work being done, and that '
      + 'success is silent while failures are verbose, because the report is what the next attempt '
      + 'corrects against.',
  };
}

// ---------------------------------------------------------------- diagram 2
function compoundingVsFailfast() {
  resetSeq();
  const W = 960, H = 612;

  const els = [...heading('A compounding error, against fail-fast',
    'The same task run once without a per-step check and once with one, then the same argument priced.')];

  els.push(text(40, 84, 'THE SAME FIVE-STEP TASK, RUN TWICE', { size: 9, stroke: T.inkSubtle }));

  const panel = (x, tint, headline, steps, footer) => {
    const out = card(x, 100, 430, 236, { spine: tint, strokeWidth: 1.4 });
    out.push(text(x + 18, 108, headline, { size: 10, stroke: tint }));
    out.push(text(x + 272, 110, 'STATE OF THE WORK', { size: 8.5, stroke: T.inkSubtle }));
    steps.forEach((s, i) => {
      const y = 128 + i * 38;
      out.push(rect(x + 18, y, 394, 34, { stroke: s[2], fill: T.surface, strokeWidth: 1.2 }));
      out.push(text(x + 32, y + 9, 'step ' + (i + 1), { size: 10.5, stroke: T.inkMuted }));
      out.push(text(x + 106, y + 9, fit(s[0], 11, 156, 'step gloss'), { size: 11, stroke: s[1] }));
      out.push(text(x + 272, y + 10, fit(s[3], 9.5, 132, 'step state'), { size: 9.5, stroke: s[1] }));
    });
    out.push(text(x + 18, 320, fit(footer, 10, 394, 'panel footer'), { size: 10, stroke: tint }));
    return out;
  };

  els.push(...panel(40, T.alert, 'WITHOUT PER-STEP CHECKS', [
    ['runs clean', T.ink, T.border, 'correct'],
    ['a bug slips in', T.alert, T.alert, 'wrong, unseen'],
    ['builds on the bug', T.alert, T.alert, 'wrong, unseen'],
    ['the error compounds', T.alert, T.alert, 'wrong, unseen'],
    ['wrong output', T.alert, T.alert, 'wrong, and shipped'],
  ], 'A wasted run, surfaced only at the end.'));

  els.push(...panel(490, T.success, 'FAIL-FAST: VERIFY EVERY STEP', [
    ['verify: pass', T.ink, T.border, 'verified'],
    ['verify: FAIL, fixed now', T.accent, T.accent, 'verified after a fix'],
    ['verify: pass', T.ink, T.border, 'verified'],
    ['verify: pass', T.ink, T.border, 'verified'],
    ['verify: pass', T.ink, T.border, 'verified'],
  ], 'Caught at step 2: the cost is one step, not the run.'));

  // --- tier two: the same argument, priced --------------------------------
  els.push(text(40, 348, 'THE SAME ARGUMENT PRICED, ON A LONGER RUN', { size: 9, stroke: T.inkSubtle }));

  els.push(...card(40, 362, 880, 190, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 370, fit('The series running example, illustrative rather than measured: '
    + 'a 12-iteration run reading about 276,000 input tokens, error at iteration 2',
    9.5, 844, 'ledger head'), { size: 9.5, stroke: T.inkMuted }));
  els.push(rule(56, 904, 388));
  els.push(text(58, 394, 'WHAT THE RUN COSTS', { size: 9, stroke: T.inkSubtle }));
  els.push(text(400, 394, 'NO GATE', { size: 10, stroke: T.alert }));
  els.push(text(664, 394, 'A GATE ON EVERY STEP', { size: 10, stroke: T.success }));

  const ledger = (y, label, without, withGate) => [
    text(58, y, fit(label, 10, 332, 'ledger label'), { size: 10, stroke: T.ink }),
    text(400, y, fit(without, 10, 250, 'ledger no-gate'), { size: 10, stroke: T.alert }),
    text(664, y, fit(withGate, 10, 240, 'ledger gate'), { size: 10, stroke: T.success }),
  ];
  els.push(...ledger(416, 'Where the error is caught', 'iteration 12', 'iteration 2'));
  els.push(...ledger(440, 'Iterations built on the error', '10 of 12', 'none'));
  els.push(...ledger(464, 'Input tokens forfeited', '~261,000, or 95% of the run', '~9,100, or 3%'));
  els.push(...ledger(488, 'What the checking itself costs', 'nothing', '12 runs, seconds each, no model call'));
  els.push(...ledger(512, 'What you hold at the end', 'a wrong result, and no signal',
    'a corrected result, one iteration late'));
  els.push(rule(56, 904, 530));
  els.push(text(58, 536, fit('Only the judge carries a token price: twelve judge calls add about '
    + '144,000 tokens to that run, and three at checkpoints add about 36,000, or 13%.',
    8.5, 844, 'ledger foot'), { size: 8.5, stroke: T.inkSubtle }));

  els.push(text(40, 566, 'Verification turns a compounding failure into a one-step correction.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 588, 'Each check costs a little, and it caps the blast radius of any single error to the step that produced it.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Five steps run without a per-step check and with one, then the same run priced in tokens',
    desc: 'A hand-drawn figure in two tiers. The upper tier compares one five-step task run two '
      + 'ways, each step carrying the state of the work after it. On the left, without per-step '
      + 'checks: step one runs clean and the work is correct, step two lets a bug slip in, step '
      + 'three builds on the bug, and step four compounds the error, all three leaving the work '
      + 'wrong and unseen, and step five produces wrong output, so the work is wrong and shipped, '
      + 'the run is wasted, and the problem surfaces only at the end. On the right, with fail-fast '
      + 'verification on every step: step one passes and the work is verified, step two fails its '
      + 'check and is fixed immediately, leaving it verified after a fix, and steps three, four '
      + 'and five pass, so the error is caught at step two and the cost is one step rather than '
      + 'the whole run. The lower tier prices the same '
      + 'argument on a longer run, using the series running example, which is illustrative rather '
      + 'than measured: a twelve-iteration run reading about 276,000 input tokens, with the error '
      + 'entering at iteration two. With no gate the error is caught at iteration twelve, ten of '
      + 'the twelve iterations are built on it, about 261,000 input tokens are forfeited, which is '
      + '95% of the run, the checking itself costs nothing, and what you hold at the end is a wrong '
      + 'result with no signal that it is wrong. With a gate on every step the error is caught at '
      + 'iteration two, no iterations are built on it, about 9,100 tokens are forfeited, which is '
      + '3%, the checking costs twelve runs of seconds each with no model call, and what you hold '
      + 'is a corrected result one iteration late. A note records that only the judge carries a '
      + 'token price: twelve judge calls would add about 144,000 tokens to that run, and three at '
      + 'checkpoints add about 36,000, or 13%. Captions record that verification turns a '
      + 'compounding failure into a one-step correction, and that each check costs a little while '
      + 'capping the blast radius of any single error to the step that produced it.',
  };
}

// ---------------------------------------------------------------- diagram 3
function verifierLadder() {
  resetSeq();
  const W = 960, H = 490;

  const els = [...heading('The verifiers, strongest first, and how often to run each',
    'Reach for the cheapest deterministic check that covers the risk. Escalate only when nothing mechanical will do.')];

  els.push(text(56, 96, 'GROUND TRUTH, STRONGEST FIRST', { size: 9, stroke: T.inkSubtle }));
  els.push(text(480, 96, 'COST', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(640, 96, 'CAN IT BE WRONG?', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(790, 96, 'RUN IT', { size: 8.5, stroke: T.inkSubtle }));

  const row = (y, tint, name, checks, cost, trust, often) => {
    const out = card(40, y, 880, 54, { spine: tint, strokeWidth: 1.3 });
    out.push(text(60, y + 6, fit(name, 12.5, 400, 'verifier name'), { size: 12.5, stroke: T.ink }));
    out.push(text(60, y + 28, fit(checks, 9, 400, 'verifier checks'), { size: 9, stroke: T.inkMuted }));
    out.push(text(480, y + 16, fit(cost, 9.5, 150, 'cost'), { size: 9.5, stroke: T.ink }));
    out.push(text(640, y + 16, fit(trust, 9.5, 140, 'trust'), { size: 9.5, stroke: tint }));
    out.push(text(790, y + 16, fit(often, 9.5, 130, 'often'), { size: 9.5, stroke: T.ink }));
    return out;
  };

  els.push(...row(110, T.success, 'A compiler or type checker',
    'Does it compile, and do the types line up? Code that fails this is wrong.',
    'free, and seconds', 'no: same verdict', 'every step'));
  els.push(...row(172, T.success, 'A test suite',
    'Does the behaviour match the tests? Ones the agent did not write are best.',
    'seconds to minutes', 'no, and repeatable', 'every step or edit'));
  els.push(...row(234, T.primary, 'Schema validation',
    'Does the result parse and satisfy the contract? Post 06, applied to output.',
    'near zero', 'no: it parses or not', 'every structured result'));

  els.push(line([[40, 300], [920, 300]], { stroke: T.alert, strokeWidth: 1.3, strokeStyle: 'dashed' }));
  els.push(text(56, 304, 'below this line the verifier can be wrong, so it is a signal rather than a gate',
    { size: 9, stroke: T.alert }));

  els.push(...row(320, T.warn, 'An independent judge',
    'Is the summary faithful? Is the prose clear? For the not-mechanical cases.',
    'a model call each', 'yes: it can pass a dud', 'at real checkpoints'));
  els.push(...row(382, T.neutral3, "The model's own self-critique",
    'A useful first pass: finding and generating surface different things.',
    'a model call each', 'yes, and skews positive', 'a first pass only'));

  els.push(text(40, 452,
    'Layer them: the cheap deterministic ones on every step, the expensive ones at real checkpoints.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 474, 'A check slower than the work it guards will simply be skipped, and an author grading its own work is not a check at all.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Five kinds of verifier ranked by strength, with cost and how often to run each',
    desc: 'A hand-drawn table of five verifiers, strongest first, with the cost of each, whether it '
      + 'can be wrong, and how often to run it. A compiler or type checker asks whether the code '
      + 'compiles and the types line up, costs nothing and seconds, cannot be wrong since it gives '
      + 'the same verdict every time, and should run on every step. A test suite asks whether the '
      + 'behaviour matches the tests, with tests the agent did not write being strongest of all; it '
      + 'costs seconds to minutes, is repeatable, and should run on every step or edit. Schema '
      + 'validation asks whether the result parses and satisfies the contract; it costs near '
      + 'nothing, either parses or does not, and should run on every structured result. A dashed '
      + 'line marks that below it the verifier can be wrong, so it is a signal rather than a gate. '
      + 'Below the line, an independent judge asks whether a summary is faithful or prose is clear, '
      + 'for what is not mechanically checkable; it costs a model call each time, can pass a bad '
      + 'answer, and belongs at real checkpoints. Last, the self-critique of the model itself is a useful '
      + 'first pass because finding problems and generating surface different things, but it costs '
      + 'a model call, skews positive, and is a first pass only. Captions record that the verifiers '
      + 'should be layered, cheap deterministic ones on every step and expensive ones at '
      + 'checkpoints, that a check slower than the work it guards will be skipped, and that an '
      + 'author grading its own work is not a check at all.',
  };
}

module.exports = { verificationGate, compoundingVsFailfast, verifierLadder };

if (require.main === module) {
  emit('01-verification-gate', verificationGate());
  emit('02-compounding-vs-failfast', compoundingVsFailfast());
  emit('03-verifier-ladder', verifierLadder());
}
