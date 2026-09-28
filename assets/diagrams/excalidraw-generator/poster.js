// The one-page poster: the whole series on a single A2-printable canvas.
//
// HARNESS-PLAN section 6 asks for "every component on one canvas: loop, tools,
// state, sandbox, verification, hooks, permissions, orchestration,
// observability". This is that sheet. It is not a bigger version of post 02's
// anatomy figure: that one answers "what is a harness made of", and this one
// has to answer that plus "how does it stop", "how does it fail", "what does it
// cost" and "what order do you build it in", because a poster is read standing
// up and out of order.
//
// Canvas is 1200 x 1700, the same as the Context Engineering sibling's sheet:
// three pixels off the A-series ratio, so it prints at A2 without a crop worth
// noticing. Output goes to poster/ in the repository root rather than under
// assets/, matching that sibling and the build:poster script. HARNESS-PLAN
// section 6 still names assets/poster/harness-anatomy.svg and is stale on that
// point.
//
// Type runs a step smaller than the per-post figures. A poster carries about
// four times the text in the same column and Excalifont is wide, so body sits
// at 11 to 12 where a figure would use 13.
//
// Every number on this sheet is carried from a post that sources it, and the
// post number is printed beside it so a reader can go and check:
//   the eleven components and their bands        post 02
//   the four exits, and the companion's defaults post 19, code/03-agent-loop
//   the six failure modes                        post 05
//   the verifier ladder                          post 11
//   what survives a reset                        posts 08 and 18
//   $0.94 uncached against $0.33 rolling cache   post 23 section 6
//   20 minutes and $9 against 6 hours and $200   post 12 section 9
//   97% of prompts approved, 17% to 5% block     post 15 section 8
//
// Nothing here is illustrative and nothing is rounded for effect.

const { T, rect, text, line, arrow, circle, resetSeq } = require('./lib');
const { heading, emit, fit, wrap, card, rule } = require('./scaffold');

const W = 1200, H = 1700;
const M = 48;                       // poster margin, wider than a figure's 40
const COL = (W - M * 2 - 24) / 2;   // two-column measure with a 24px gutter
const R = M + COL + 24;             // left edge of the right column

// A panel: a titled card with a coloured spine, used for every block below.
function panel(x, y, w, h, tint, title, sub) {
  const out = card(x, y, w, h, { spine: tint, strokeWidth: 1.4 });
  out.push(text(x + 18, y + 10, title, { size: 11, stroke: tint }));
  if (sub) out.push(text(x + 18, y + 27, fit(sub, 9, w - 36, 'panel sub'),
    { size: 9, stroke: T.inkSubtle }));
  return out;
}

function poster() {
  resetSeq();
  const els = [...heading('One page of harness engineering',
    'Eleven components, four exits, six failure modes, and what the whole thing costs to run.', W)];

  // ---------------------------------------------------------------- the claim
  els.push(...panel(M, 84, W - M * 2, 96, T.ink, 'THE CLAIM THE SERIES IS BUILT ON', null));
  els.push(text(M + 18, 112, 'Agent  =  Model  +  Harness', { size: 22, stroke: T.ink }));
  els.push(text(M + 18, 146, wrap('The model is bought and moves a few times a year. The harness is written, and it is where almost all of the engineering is. Two systems on the same model differ by their harness, and that is the whole gap.', 10, 640),
    { size: 10, stroke: T.inkMuted }));
  els.push(rule(760, W - M - 18, 108));
  els.push(text(760, 118, 'Viv Trivedy, LangChain, 10 March 2026,', { size: 9, stroke: T.inkSubtle }));
  els.push(text(760, 132, 'popularised by Addy Osmani. Post 01.', { size: 9, stroke: T.inkSubtle }));
  els.push(text(760, 152, 'If you are not the model, you are', { size: 9.5, stroke: T.accent }));
  els.push(text(760, 166, 'the harness.', { size: 9.5, stroke: T.accent }));

  // ------------------------------------------------------- eleven components
  els.push(...panel(M, 196, W - M * 2, 396, T.primary,
    'THE ELEVEN COMPONENTS, IN THE THREE BANDS THEY FALL INTO',
    'The number on each card is the post that covers it. Naming the failing component is most of the work of fixing it.'));

  const BANDS = [
    ['FEEDS THE MODEL', 'what it knows and can do', T.primary, M + 18, [
      ['02', 'Tools & code execution', 'bash and code beat fifty bespoke tools'],
      ['03', 'State & filesystem', 'durable memory outside the window'],
      ['04', 'Context management', 'compaction, offloading, resets'],
      ['05', 'Memory & learning', 'carry knowledge across sessions'],
    ]],
    ['GOVERNS IT', 'limits and evidence', T.success, M + 18 + 372, [
      ['06', 'Verification', 'check each step; fail before errors compound'],
      ['07', 'Hooks & enforcement', 'deterministic rules the model cannot skip'],
      ['08', 'Permissions & sandbox', 'bound the blast radius'],
      ['11', 'Observability', 'a trace per run; see it, then fix it'],
    ]],
  ];
  BANDS.forEach((b) => {
    els.push(text(b[3], 254, b[0] + ' · ' + b[1], { size: 9, stroke: b[2] }));
    b[4].forEach((c, i) => {
      const y = 272 + i * 62;
      els.push(rect(b[3], y, 348, 54, { stroke: T.border, fill: T.surface, strokeWidth: 1 }));
      els.push(rect(b[3] + 8, y + 8, 22, 16, { stroke: b[2], fill: b[2], strokeWidth: 1 }));
      els.push(text(b[3] + 8, y + 12, c[0], { size: 8.5, align: 'center', width: 22, stroke: T.onAccent }));
      els.push(text(b[3] + 38, y + 10, fit(c[1], 11, 300, 'comp'), { size: 11, stroke: T.ink }));
      els.push(text(b[3] + 38, y + 30, fit(c[2], 8.5, 300, 'comp sub'), { size: 8.5, stroke: T.inkMuted }));
    });
  });

  // the core, between the two bands
  const CX = M + 18 + 372 + 372 + 12;
  els.push(rect(CX, 254, 296, 250, { stroke: T.ink, fill: T.surface, strokeWidth: 1.6 }));
  els.push(text(CX + 16, 262, '01  THE AGENT LOOP', { size: 10, stroke: T.ink }));
  els.push(text(CX + 16, 278, 'the core everything else wraps', { size: 8.5, stroke: T.inkSubtle }));
  ['REASON', 'ACT', 'OBSERVE'].forEach((s, i) => {
    const y = 302 + i * 46;
    els.push(rect(CX + 40, y, 216, 34, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.2 }));
    els.push(text(CX + 40, y + 10, s, { size: 11, align: 'center', width: 216, stroke: T.ink }));
    if (i < 2) els.push(arrow([[CX + 148, y + 34], [CX + 148, y + 46]], { stroke: T.inkMuted, strokeWidth: 1 }));
  });
  els.push(arrow([[CX + 34, 415], [CX + 22, 415], [CX + 22, 319], [CX + 34, 319]],
    { stroke: T.inkMuted, strokeWidth: 1 }));
  els.push(rule(CX + 16, CX + 280, 454));
  els.push(text(CX + 16, 464, 'One turn is one model call.', { size: 9, stroke: T.ink }));
  els.push(text(CX + 16, 480, 'Most agent bugs live in how it stops.', { size: 9, stroke: T.inkMuted }));

  // the scale tier, across the bottom of the panel
  els.push(text(M + 18, 524, 'OPERATES AT A LARGER SCALE · many agents, or many windows', { size: 9, stroke: T.warn }));
  [['09', 'Orchestration', 'coordinate many agents as units, one level up from a single agent'],
   ['10', 'Long-horizon patterns', 'Ralph loops and context bridging, for work that outgrows one window']]
    .forEach((c, i) => {
      const x = M + 18 + i * 552;
      els.push(rect(x, 540, 528, 36, { stroke: T.border, fill: T.surface, strokeWidth: 1 }));
      els.push(rect(x + 8, 548, 22, 16, { stroke: T.warn, fill: T.warn, strokeWidth: 1 }));
      els.push(text(x + 8, 552, c[0], { size: 8.5, align: 'center', width: 22, stroke: T.onAccent }));
      els.push(text(x + 38, 548, c[1], { size: 10.5, stroke: T.ink }));
      els.push(text(x + 178, 550, fit(c[2], 8.5, 340, 'scale sub'), { size: 8.5, stroke: T.inkMuted }));
    });

  // ------------------------------------------------- how it stops / how it fails
  els.push(...panel(M, 608, COL, 300, T.accent, 'HOW THE LOOP STOPS',
    'Four exits, checked in this order after every turn. Only the first means success.'));
  [['1', 'the verifier confirms the goal', 'ground truth, not self-report', T.success],
   ['2', 'a hard max-iterations cap', 'max_iters = 12', T.accent],
   ['3', 'a token or wall-clock budget', 'the spend the task is worth', T.accent],
   ['4', 'no-progress detection', 'no_progress_window = 3', T.accent]]
    .forEach((e, i) => {
      const y = 652 + i * 52;
      els.push(circle(M + 30, y + 8, 11, { stroke: e[3], strokeWidth: 1.2 }));
      els.push(text(M + 20, y + 3, e[0], { size: 9, align: 'center', width: 20, stroke: e[3] }));
      els.push(text(M + 56, y + 1, fit(e[1], 10.5, 440, 'exit'), { size: 10.5, stroke: T.ink }));
      els.push(text(M + 56, y + 19, fit(e[2], 8.5, 440, 'exit sub'), { size: 8.5, stroke: T.inkMuted }));
    });
  els.push(rule(M + 18, M + COL - 18, 866));
  els.push(text(M + 18, 876, 'The two caps are the loop companion’s own defaults,', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(M + 18, 890, 'in code/03-agent-loop. Posts 03 and 19.', { size: 8.5, stroke: T.inkSubtle }));

  els.push(...panel(R, 608, COL, 300, T.alert, 'HOW IT FAILS',
    'Six modes. Five cost you a run; the sixth costs you something you cannot get back.'));
  [['Victory declaration', 'it exits on "done" and the work is not done', T.alert],
   ['Context anxiety', 'late-run answers are worse than early ones', T.alert],
   ['One-shotting', 'one enormous diff with no intermediate steps', T.alert],
   ['Doom loop', 'the same call and arguments, turn after turn', T.alert],
   ['Silent drift', 'a rule you already fixed keeps reappearing', T.alert],
   ['Destructive action', 'the one that is not merely a wasted run', T.warn]]
    .forEach((f, i) => {
      const y = 656 + i * 36;
      els.push(rect(R + 18, y, 14, 14, { stroke: f[2], fill: f[2], strokeWidth: 1 }));
      els.push(text(R + 40, y - 1, fit(f[0], 10.5, 460, 'mode'), { size: 10.5, stroke: T.ink }));
      els.push(text(R + 40, y + 16, fit(f[1], 8.5, 460, 'mode sub'), { size: 8.5, stroke: T.inkMuted }));
    });
  els.push(rule(R + 18, R + COL - 18, 868));
  els.push(text(R + 18, 876, '"My agent is flaky" is not a diagnosis. Name the mode, and the', { size: 9, stroke: T.ink }));
  els.push(text(R + 18, 890, 'component to change names itself. Post 05.', { size: 9, stroke: T.ink }));

  // -------------------------------------------- verification / durable state
  els.push(...panel(M, 924, COL, 268, T.success, 'THE VERIFIER LADDER',
    'Cheapest first. Every rung above the line is ground truth; below it, a judgement.'));
  [['a compiler or type checker', 'free, cannot be wrong', T.success],
   ['a test suite', 'cheap, cannot be wrong', T.success],
   ['schema validation', 'free, cannot be wrong', T.success],
   ['an independent judge', 'costs a call, can be wrong', T.warn],
   ['the model’s own self-critique', 'nearly free, and the weakest', T.alert]]
    .forEach((v, i) => {
      const y = 968 + i * 38;
      els.push(text(M + 18, y, fit(v[0], 10.5, 340, 'rung'), { size: 10.5, stroke: T.ink }));
      els.push(text(M + 360, y + 2, fit(v[1], 8.5, 176, 'rung cost'),
        { size: 8.5, align: 'right', width: 176, stroke: v[2] }));
      if (i === 2) els.push(line([[M + 18, y + 26], [M + COL - 18, y + 26]],
        { stroke: T.inkSubtle, strokeWidth: 1, strokeStyle: 'dashed' }));
    });
  els.push(rule(M + 18, M + COL - 18, 1148));
  els.push(text(M + 18, 1158, 'Success is silent; failures are verbose, because the report', { size: 9, stroke: T.ink }));
  els.push(text(M + 18, 1172, 'is what the next attempt corrects against. Post 11.', { size: 9, stroke: T.ink }));

  els.push(...panel(R, 924, COL, 268, T.warn, 'WHAT SURVIVES A RESET',
    'The window is disposable. What the next context needs has to be on disk before this one closes.'));
  [['the spec', 'human-owned: what to build, and what "done" means'],
   ['the handoff', 'loop-written: what is done, what is next, what is blocked'],
   ['the repository', 'one commit per verifiable increment, behind a gate'],
   ['the memory file', 'the ratchet: a rule learned once, injected ever after']]
    .forEach((r, i) => {
      const y = 972 + i * 46;
      els.push(rect(R + 18, y, 500, 38, { stroke: T.border, fill: T.surface, strokeWidth: 1 }));
      els.push(text(R + 30, y + 6, r[0], { size: 10.5, stroke: T.ink }));
      els.push(text(R + 30, y + 22, fit(r[1], 8.5, 470, 'store sub'), { size: 8.5, stroke: T.inkMuted }));
    });
  els.push(rule(R + 18, R + COL - 18, 1148));
  els.push(text(R + 18, 1158, 'A reset is not a loss, as long as everything the next task', { size: 9, stroke: T.ink }));
  els.push(text(R + 18, 1172, 'needs was written down first. Posts 08, 10 and 18.', { size: 9, stroke: T.ink }));

  // ------------------------------------------------------------- what it costs
  els.push(...panel(M, 1208, W - M * 2, 240, T.primary, 'WHAT IT COSTS, MEASURED',
    'Three numbers the series actually ran, each from the post that shows its working.'));
  const COSTS = [
    ['A twelve-iteration run', [['uncached', '$0.94'], ['on a rolling cache', '$0.33']],
     'Every turn re-reads a context that grew the step before, so the bill is dominated by re-reading, not by new tokens.', 'Post 23'],
    ['One brief, two harnesses', [['a single agent, one pass', '20 min, $9'], ['planner / generator / evaluator', '6 h, $200']],
     'Over twenty times the price and about eighteen times the wall clock, for a harness that catches what one pass does not.', 'Post 12'],
    ['The cost of asking a human', [['of prompts are approved', '97%'], ['block rate, early then after 50', '17% to 5%']],
     'A gate you fire too often trains the reviewer to say yes, and the approval stops being oversight at all.', 'Post 15'],
  ];
  COSTS.forEach((c, i) => {
    const x = M + 18 + i * 368;
    els.push(text(x, 1256, c[0], { size: 11, stroke: T.ink }));
    c[1].forEach((row, j) => {
      const y = 1280 + j * 24;
      els.push(text(x, y, fit(row[0], 9, 216, 'cost label'), { size: 9, stroke: T.inkMuted }));
      els.push(text(x + 220, y - 2, row[1], { size: 12, align: 'right', width: 112, stroke: T.ink }));
    });
    els.push(rule(x, x + 332, 1336));
    els.push(text(x, 1348, wrap(c[2], 8.5, 332), { size: 8.5, stroke: T.inkMuted }));
    els.push(text(x, 1414, c[3], { size: 8.5, stroke: T.primary }));
  });

  // --------------------------------------------------------- the build order
  els.push(...panel(M, 1464, W - M * 2, 156, T.ink, 'THE ORDER TO BUILD IT IN',
    'Each rung is only worth adding once the one before it holds. Skipping ahead is how a harness gets complicated without getting better.'));
  ['a loop that stops for a named reason',
   'a verifier, so "done" means verified',
   'durable state, so a reset is not a loss',
   'a hook and a sandbox, to bound the blast radius',
   'a trace, so a failure has an address',
   'a ratchet, so it is fixed once',
   'a second agent, only if one with a bigger context could not']
    .forEach((s, i) => {
      const x = M + 18 + (i % 4) * 276;
      const y = 1518 + Math.floor(i / 4) * 48;
      els.push(circle(x + 10, y + 8, 11, { stroke: T.ink, strokeWidth: 1.2 }));
      els.push(text(x, y + 3, String(i + 1), { size: 9, align: 'center', width: 20, stroke: T.ink }));
      els.push(text(x + 32, y + 3, wrap(s, 9, 220), { size: 9, stroke: T.ink }));
    });

  els.push(text(M, 1648, 'The model is the ceiling. The harness is how close you get to it.',
    { size: 13, stroke: T.ink }));
  els.push(text(M, 1670, 'Harness Engineering for LLM Agents · twenty-six posts · every number on this sheet is carried from the post that sources it.',
    { size: 9.5, stroke: T.inkSubtle }));

  return {
    W, H, els,
    title: 'One page of harness engineering: the whole series on a single sheet',
    desc: 'A hand-drawn A2 poster of the Harness Engineering series on one canvas. At the top, the '
      + 'claim the series is built on: agent equals model plus harness, attributed to Viv Trivedy '
      + 'of LangChain in March 2026 and popularised by Addy Osmani, with the note that if you are '
      + 'not the model, you are the harness. Below it, the eleven components in three bands. The '
      + 'band that feeds the model holds tools and code execution, state and filesystem, context '
      + 'management, and memory and learning. The band that governs it holds verification, hooks '
      + 'and enforcement, permissions and sandbox, and observability. Between them sits the agent '
      + 'loop itself, reason, act and observe, with the note that one turn is one model call and '
      + 'that most agent bugs live in how the loop stops. A third band across the bottom holds the '
      + 'two components that operate at a larger scale, orchestration and long-horizon patterns. '
      + 'Each card carries the number of the post that covers it. Beneath that, two panels. How '
      + 'the loop stops gives four exits checked in order after every turn: the verifier confirming '
      + 'the goal against ground truth, a hard cap of twelve iterations, a token or wall-clock '
      + 'budget, and no-progress detection over a window of three, the last two being the loop '
      + 'companion own defaults. How it fails gives six modes: victory declaration, context '
      + 'anxiety, one-shotting, doom loops, silent drift, and destructive action, the last marked '
      + 'apart as the one that is not merely a wasted run. Two more panels follow. The verifier '
      + 'ladder runs cheapest first, from a compiler or type checker, a test suite and schema '
      + 'validation, which are ground truth, across a dashed line to an independent judge and the '
      + 'model own self-critique, which are judgements. What survives a reset lists the spec, the '
      + 'handoff, the repository and the memory file, with what each one is for. A costs panel '
      + 'gives three measured comparisons: a twelve-iteration run at ninety-four cents uncached '
      + 'against thirty-three cents on a rolling cache; one brief taking twenty minutes and nine '
      + 'dollars through a single agent against six hours and two hundred dollars through a '
      + 'planner, generator and evaluator harness; and the cost of asking a human, where ninety-'
      + 'seven per cent of permission prompts are approved and the block rate decays from '
      + 'seventeen per cent to five. A final panel gives the order to build in, seven numbered '
      + 'rungs from a loop that stops for a named reason through to a second agent, which is only '
      + 'worth adding if one agent with a bigger context could not do the work. The sheet closes '
      + 'with the line that the model is the ceiling and the harness is how close you get to it.',
  };
}

emit('one-page-of-harness-engineering', poster());
