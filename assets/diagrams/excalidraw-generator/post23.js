// The post 23 diagrams, hand-drawn.
//
//   01-loop-cost          960 x 460  Mirror of the existing figure.
//   02-llm-api-vs-haas    960 x 440  Mirror.
//   03-build-vs-rent      960 x 470  NEW, published: section 6 had no figure.
//
// The post ends on a decision and draws everything except the decision. Section
// 6 is three questions whose answers point cleanly one way or the other, which
// is exactly the shape a figure holds better than three paragraphs.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function loopCost() {
  resetSeq();
  const W = 960, H = 596;

  const els = [...heading('The cost of a loop, iteration by iteration',
    'Each turn re-reads a context that grew the step before, so the cost climbs. Caching flattens the re-read of the stable prefix.')];

  // Section 6's worked run, exactly. Input starts at 6,000 and grows by a
  // constant 3,100 fresh tokens a turn, so iteration n sends 6,000 + 3,100(n-1)
  // and all but the newest 3,100 of it is already cached. The published rows
  // (1, 2, 6, 12) fall out of the same line, which is why the fresh slice is
  // drawn the same height on every bar while the re-read below it grows.
  const N = 12, FRESH = 3100, BASE = 6000;
  const MAX = BASE + FRESH * (N - 1);          // 40,100 at iteration 12
  const AX = 132, BASELINE = 372, TOP = 130;   // plot box
  const SCALE = (BASELINE - TOP) / MAX;
  const BW = 44, GAP = 18;

  els.push(text(AX, 96, 'INPUT TOKENS SENT, PER ITERATION', { size: 9, stroke: T.inkSubtle }));
  els.push(line([[AX, BASELINE], [AX + N * (BW + GAP), BASELINE]], { stroke: T.ink, strokeWidth: 1.2 }));
  [[0, '0'], [20000, '20k'], [40000, '40k']].forEach((t) => {
    const y = BASELINE - t[0] * SCALE;
    els.push(text(80, y - 5, t[1], { size: 8.5, align: 'right', width: 44, stroke: T.inkSubtle }));
  });

  for (let i = 0; i < N; i++) {
    const x = AX + 10 + i * (BW + GAP);
    const input = BASE + FRESH * i;
    const fresh = i === 0 ? BASE : FRESH;
    const reread = input - fresh;
    const hR = reread * SCALE, hF = fresh * SCALE;
    if (reread) els.push(rect(x, BASELINE - hR, BW, hR, { stroke: T.ink, fill: T.neutral2, strokeWidth: 1 }));
    els.push(rect(x, BASELINE - hR - hF, BW, hF, { stroke: T.ink, fill: T.primary, strokeWidth: 1 }));
    els.push(text(x, BASELINE + 8, String(i + 1), { size: 8.5, align: 'center', width: BW, stroke: T.inkSubtle }));
  }
  els.push(text(AX + 10, 392, 'loop iterations', { size: 9, stroke: T.inkSubtle }));

  els.push(text(206, 118, 'every bar sends the same 3,100 fresh tokens; only the re-read underneath grows',
    { size: 9, stroke: T.success }));

  [['already cached, re-read each turn', T.neutral2], ['fresh this turn: a flat 3,100', T.primary]]
    .forEach((l, i) => {
      els.push(rect(AX + i * 300, 410, 14, 12, { stroke: T.ink, fill: l[1], strokeWidth: 1 }));
      els.push(text(AX + 20 + i * 300, 410, l[0], { size: 9, stroke: T.inkMuted }));
    });

  // --- second tier: what the run actually cost ----------------------------
  els.push(...card(40, 440, 430, 108, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 448, 'THE RUN TOTAL, TWELVE ITERATIONS', { size: 9, stroke: T.primary }));
  [['input tokens sent', '276,600'], ['of which already cached', '236,500'],
   ['fresh input written', '40,100'], ['output tokens', '7,200']].forEach((r, i) => {
    els.push(text(58, 470 + i * 18, r[0], { size: 9, stroke: T.ink }));
    els.push(text(258, 470 + i * 18, r[1], { size: 9, align: 'right', width: 180, stroke: T.ink }));
  });

  els.push(...card(490, 440, 430, 108, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(508, 448, 'AND WHAT IT COSTS, AT MID-TIER PRICES', { size: 9, stroke: T.accent }));
  els.push(text(508, 470, 'RUN LENGTH', { size: 8, stroke: T.inkSubtle }));
  els.push(text(688, 470, 'UNCACHED', { size: 8, align: 'right', width: 100, stroke: T.inkSubtle }));
  els.push(text(798, 470, 'ROLLING CACHE', { size: 8, align: 'right', width: 106, stroke: T.inkSubtle }));
  [['12 iterations', '$0.94', '$0.33'], ['40 iterations', '$8.33', '$1.60'],
   ['growth factor', '8.9x', '4.8x']].forEach((r, i) => {
    els.push(text(508, 488 + i * 17, r[0], { size: 9, stroke: T.ink }));
    els.push(text(688, 488 + i * 17, r[1], { size: 9, align: 'right', width: 100, stroke: T.ink }));
    els.push(text(798, 488 + i * 17, r[2], { size: 9, align: 'right', width: 106, stroke: T.success }));
  });

  els.push(text(40, 562, 'Cost scales with iterations and with a context that grows at every step, so a run twice as long costs more than twice as much.',
    { size: 11, stroke: T.ink }));
  els.push(text(40, 580, 'Every token trimmed by compaction is a token you stop paying to re-read on every subsequent turn.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Input tokens per iteration across the published twelve-iteration run',
    desc: 'A hand-drawn bar chart of the input tokens sent at each of twelve loop iterations, on '
      + 'an axis marked at zero, twenty thousand and forty thousand. Each bar has two segments: a '
      + 'grey lower segment for the part of the context already cached and re-read that turn, which '
      + 'grows at every iteration, and a blue upper segment for the fresh tokens written that turn, '
      + 'which is a flat three thousand one hundred on every bar after the first. The first '
      + 'iteration is entirely fresh at six thousand tokens; the twelfth sends forty thousand one '
      + 'hundred, of which thirty-seven thousand is re-read. An annotation records that every bar '
      + 'sends the same fresh slice and only the re-read underneath grows. A panel gives the run '
      + 'total: two hundred and seventy-six thousand six hundred input tokens sent, of which two '
      + 'hundred and thirty-six thousand five hundred were already cached, forty thousand one '
      + 'hundred written fresh, and seven thousand two hundred output. A second panel prices it at '
      + 'mid-tier rates: twelve iterations cost ninety-four cents uncached against thirty-three '
      + 'cents on a rolling cache, forty iterations cost eight dollars thirty-three against one '
      + 'dollar sixty, growth factors of 8.9 times and 4.8 times. Captions record that cost scales '
      + 'with iterations and with a context that grows at every step, so a run twice as long costs '
      + 'more than twice as much, and that every token trimmed by compaction is a token you stop '
      + 'paying to re-read on every subsequent turn.',
  };
}

// ---------------------------------------------------------------- diagram 2
function llmApiVsHaas() {
  resetSeq();
  const W = 960, H = 612;

  const els = [...heading('Two boundaries: rent a model, or rent a run',
    'An LLM API returns a completion and leaves the loop to you. A harness API returns a run with the loop inside.')];

  const side = (x, tint, name, io, boundaryLabel, inside, outsideLabel) => {
    const out = card(x, 96, 430, 280, { spine: tint, strokeWidth: 1.5 });
    out.push(text(x + 18, 106, name, { size: 14, stroke: T.ink }));
    out.push(text(x + 18, 130, io, { size: 9.5, stroke: T.inkMuted }));
    const bh = inside ? 178 : 62;
    out.push(rect(x + 18, 152, 394, bh, { stroke: tint, strokeWidth: 1.6, strokeStyle: 'dashed' }));
    out.push(text(x + 30, 158, boundaryLabel, { size: 8.5, stroke: tint }));
    out.push(rect(x + 30, 174, 180, 30, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.2 }));
    out.push(text(x + 30, 182, 'model call', { size: 10, align: 'center', width: 180, stroke: T.ink }));
    const cy = inside ? 214 : 246;
    if (outsideLabel) out.push(text(x + 18, cy, outsideLabel, { size: 8.5, stroke: T.alert }));
    ['loop', 'tools', 'context management', 'hooks'].forEach((c, i) => {
      const cx = x + 30 + (i % 2) * 190;
      const y = cy + 16 + Math.floor(i / 2) * 32;
      out.push(rect(cx, y, 176, 26, { stroke: T.border, fill: T.surface, strokeWidth: 1 }));
      out.push(text(cx, y + 7, c, { size: 9.5, align: 'center', width: 176, stroke: T.ink }));
    });
    return out;
  };

  els.push(...side(40, T.alert, 'LLM API', 'send a prompt, and get back a completion',
    'API BOUNDARY', false, 'YOUR responsibility, outside the API:'));
  els.push(...side(490, T.success, 'HARNESS API (HaaS)', 'send a task, and get back a whole agent run',
    'SERVICE BOUNDARY: the loop lives inside here', true, 'inside the service, and not yours to build:'));

  // --- second tier: the four tiers, and the meter that does not cross -----
  els.push(text(40, 396, 'RENTING IS FOUR TIERS, NOT TWO, AND ONLY ONE COLUMN CROSSES THE BOUNDARY',
    { size: 10, stroke: T.inkSubtle }));

  els.push(...card(40, 416, 596, 130, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 424, 'TIER', { size: 8, stroke: T.inkSubtle }));
  els.push(text(232, 424, 'WHAT YOU PAY FOR THE HARNESS', { size: 8, stroke: T.inkSubtle }));
  els.push(text(482, 424, 'MODEL TOKENS', { size: 8, stroke: T.inkSubtle }));
  [['Model API', 'nothing; there is no harness to pay for', 'billed to you'],
   ['SDK you host', 'your own compute, plus the engineering', 'billed to you'],
   ['Session-metered', '$0.08 per session-hour, while running', 'billed to you'],
   ['Resource-metered', '$0.0895 per vCPU-hour, $0.00945 per GB-hour', 'billed separately']]
    .forEach((r, i) => {
      const y = 444 + i * 22;
      els.push(text(58, y, r[0], { size: 9, stroke: T.ink }));
      els.push(text(232, y, fit(r[1], 9, 244, 'tier pay'), { size: 9, stroke: T.inkMuted }));
      els.push(text(482, y, r[2], { size: 9, stroke: T.accent }));
    });
  els.push(text(58, 528, 'The token bill never crosses: renting turns one meter you understand into two that do not compose.',
    { size: 8.5, stroke: T.inkSubtle }));

  els.push(...card(652, 416, 268, 130, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(670, 424, 'THE SAME RUN, BOTH METERS', { size: 9, stroke: T.accent }));
  els.push(text(670, 444, 'section 5: 36 seconds, $0.329 of tokens', { size: 8.5, stroke: T.inkMuted }));
  [['$0.0008', 'the runtime charge for those 36s'],
   ['$0.64', 'a session held open for eight hours'],
   ['$0.87', 'the same eight hours, by resource']].forEach((r, i) => {
    els.push(text(670, 464 + i * 22, r[0], { size: 11, stroke: T.ink }));
    els.push(text(730, 466 + i * 22, fit(r[1], 8.5, 176, 'meter'), { size: 8.5, stroke: T.inkMuted }));
  });

  els.push(text(40, 562, 'Build-versus-rent turns on where the boundary sits: rent the model and own the harness, or rent the whole run.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 584, 'The runtime meter is a rounding error on short work and a first-class line item on anything that idles or runs long.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'An LLM API boundary beside a harness API boundary',
    desc: 'A hand-drawn comparison of two service boundaries. On the left, an LLM API: you send a '
      + 'prompt and get back a completion, and the API boundary encloses only the model call. '
      + 'Outside that boundary, marked as your responsibility, sit the loop, the tools, context '
      + 'management and hooks. On the right, a harness API or Harness-as-a-Service: you send a task '
      + 'and get back a whole agent run, and the service boundary encloses the model call together '
      + 'with the loop, the tools, context management and hooks, all marked as inside the service '
      + 'and not yours to build. Captions record that build-versus-rent turns on where the boundary '
      + 'sits, so you either rent the model and own the harness or rent the whole run. A second '
      + 'tier lists renting as four tiers rather than two: a model API, where there is no harness '
      + 'to pay for; an SDK you host, where you pay your own compute and the engineering to run '
      + 'it; a session-metered hosted runtime at eight cents per session-hour while running; and '
      + 'a resource-metered one at 8.95 cents per vCPU-hour and 0.945 cents per GB-hour. Model '
      + 'tokens are billed to you in the first three and separately in the last, so the token '
      + 'bill never crosses the boundary and renting turns one meter into two that do not '
      + 'compose. A panel prices the same thirty-six-second run, which cost 32.9 cents in tokens, '
      + 'on both meters: eight hundredths of a cent of runtime, against sixty-four cents for a '
      + 'session held open eight hours and eighty-seven cents for the same hours metered by '
      + 'resource. It also records that you '
      + 'gain time to market while giving up control over the exact behaviour of the loop and '
      + 'visibility into its internals.',
  };
}

// ---------------------------------------------------------------- diagram 3
function buildVsRent() {
  resetSeq();
  const W = 960, H = 486;

  const els = [...heading('Build or rent, in three questions',
    'The answers point cleanly one way or the other, and the third one decides the other two.')];

  const QS = [
    [40, T.primary, 'VOLUME', false,
      ['A rented runtime carries a per-run', 'margin on the loop machinery.'],
      ['a few thousand runs a month, where', 'renting saves months of engineering', 'you would otherwise spend'],
      ['millions of runs, where the aggregate', 'margin exceeds the cost of a team', 'owning the harness outright'],
      ['the crossover is arithmetic, once you', 'have a per-run cost model']],
    [340, T.accent, 'CONTROL', false,
      ['A rented harness is a fixed loop with', 'a fixed set of hook points.'],
      ['the vendor loop, context strategy and', 'hooks already cover your task', 'without contortions'],
      ['you need a bespoke stop condition, a', 'custom verification gate, or a context', 'strategy nobody exposes'],
      ['the more your value lives in the', 'harness, the more you build']],
    [640, T.success, 'DIFFERENTIATION', true,
      ['Is the harness the thing your', 'customers are actually paying for?'],
      ['it is undifferentiated plumbing under', 'a product whose value lies somewhere', 'else entirely'],
      ['it is your product: renting it means', 'renting your moat from a supplier who', 'also rents it to your competitors'],
      ['build what differentiates you;', 'rent what does not']],
  ];

  QS.forEach((q) => {
    const x = q[0];
    els.push(...card(x, 100, 280, 264, { spine: q[1], strokeWidth: q[3] ? 1.8 : 1.3 }));
    els.push(text(x + 16, 112, q[2], { size: 14, stroke: T.ink }));
    if (q[3]) els.push(text(x + 16, 132, 'THE DECIDING QUESTION', { size: 8, stroke: q[1] }));
    q[4].forEach((l, i) => els.push(text(x + 16, 148 + i * 14, fit(l, 9, 248, 'q gloss'),
      { size: 9, stroke: T.inkMuted })));
    els.push(rule(x + 16, x + 264, 180));
    els.push(text(x + 16, 188, 'RENT WHEN', { size: 8.5, stroke: T.inkSubtle }));
    q[5].forEach((l, i) => els.push(text(x + 16, 202 + i * 14, fit(l, 9, 248, 'rent line'),
      { size: 9, stroke: T.ink })));
    els.push(rule(x + 16, x + 264, 250));
    els.push(text(x + 16, 258, 'BUILD WHEN', { size: 8.5, stroke: T.inkSubtle }));
    q[6].forEach((l, i) => els.push(text(x + 16, 272 + i * 14, fit(l, 9, 248, 'build line'),
      { size: 9, stroke: T.ink })));
    q[7].forEach((l, i) => els.push(text(x + 16, 322 + i * 13, fit(l, 8.5, 248, 'q note'),
      { size: 8.5, stroke: q[1] })));
  });

  els.push(text(40, 392, 'Build what differentiates you; rent what does not, one component at a time.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 418, 'The cost model is the same either way, and you can meter a run before you decide.',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 444, 'Iterations multiply the bill, the prefix is re-read every turn, and the discount on it decides whether a run ships.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Three questions that decide whether to build a harness or rent one',
    desc: 'A hand-drawn figure of three questions, each with the case for renting and the case for '
      + 'building. Volume: a rented runtime carries a per-run margin on the loop machinery, so rent '
      + 'at a few thousand runs a month where renting saves months of engineering, and build at '
      + 'millions of runs where the aggregate margin exceeds the cost of a team owning the harness '
      + 'outright; the crossover is arithmetic once you have a per-run cost model. Control: a '
      + 'rented harness is a fixed loop with a fixed set of hook points, so rent when the vendor '
      + 'loop, context strategy and hooks already cover your task without contortions, and build '
      + 'when you need a bespoke stop condition, a custom verification gate, or a context strategy '
      + 'nobody exposes; the more your value lives in the harness, the more you build. '
      + 'Differentiation, marked as the deciding question: is the harness the thing your customers '
      + 'are actually paying for? Rent when it is undifferentiated plumbing under a product whose '
      + 'value lies elsewhere; build when it is your product, because renting it means renting your '
      + 'moat from a supplier who also rents it to your competitors. Captions record that you '
      + 'should build what differentiates you and rent what does not, one component at a time, that '
      + 'the cost model is the same either way so you can meter a run before deciding, and that '
      + 'iterations multiply the bill while the discount on the re-read prefix decides whether a '
      + 'run ships.',
  };
}

module.exports = { loopCost, llmApiVsHaas, buildVsRent };

if (require.main === module) {
  emit('01-loop-cost', loopCost());
  emit('02-llm-api-vs-haas', llmApiVsHaas());
  emit('03-build-vs-rent', buildVsRent());
}
