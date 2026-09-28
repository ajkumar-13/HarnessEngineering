// The post 09 diagrams, hand-drawn.
//
//   01-window-timeline      960 x 636  Published: the fill chart, now numbered.
//   02-three-moves          960 x 580  Published: the three moves, now costed.
//   03-escalation-ladder    960 x 626  Published: the ladder, now priced.
//
// The post describes four corrective moves, not three: clearing a spent tool
// result to a stub sits between offloading and compaction, and it is the rung
// most loops never implement. The third scene draws all four, and adds the
// column the prose argues hardest for and no figure showed: what each move does
// to the prompt cache.
//
// Every number drawn in these three scenes is read out of the post itself: the
// illustrative 80/95 per cent triggers and the shipped 100,000 and 150,000
// token triggers (sections 4 and 5), the offload threshold and pointer shape
// from the code in section 3, the handoff contract in section 6, and the whole
// token-equivalent table in section 7. Nothing here is estimated by the figure.

const { T, rect, ellipse, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function windowTimeline() {
  resetSeq();
  const W = 960, H = 636;

  const els = [...heading('Keeping the window small over a long session',
    'A running loop fills its own window. Log the fill every call, and fire the cheap moves before the top.')];

  // --- the chart ------------------------------------------------------------
  // Plot x 116..772, so the right column carries the trigger legend rather than
  // an empty margin. 0 to 100 per cent maps to y 326..116, 2.1px per point.
  const X0 = 116, X1 = 772, PITCH = 82, BW = 54, BASE = 326;
  const yFor = (p) => BASE - 2.1 * p;
  const bx = (i) => X0 + i * PITCH + 14;

  els.push(text(M, 84, 'AN ILLUSTRATIVE RUN: WINDOW FILL PER CALL, AS A PERCENTAGE OF THE MODEL LIMIT',
    { size: 9.5, stroke: T.inkSubtle }));

  // The rot band is the top fifth: its floor is the soft trigger, and the hard
  // trigger sits inside it. No figure here claims a measured threshold for
  // where rot begins, because the post does not have one.
  els.push(rect(X0, yFor(100), X1 - X0, yFor(80) - yFor(100),
    { fill: T.neutral1, stroke: T.neutral2, strokeWidth: 1, opacity: 55, roundness: null }));

  [20, 40, 60].forEach((p) => els.push(line([[X0, yFor(p)], [X1, yFor(p)]],
    { stroke: T.border, strokeWidth: 1, roughness: 0.3 })));
  els.push(line([[X0, BASE], [X1, BASE]], { stroke: T.ink, strokeWidth: 1.3 }));

  [[100, '100 %'], [80, '80 %'], [60, '60 %'], [40, '40 %'], [20, '20 %'], [0, '0 %']]
    .forEach((row) => els.push(text(M, yFor(row[0]) - 6, row[1],
      { size: 9.5, align: 'right', width: 66, stroke: T.inkSubtle })));

  // The unmanaged run: no moves at all, so it climbs until the window is gone.
  const UNMANAGED = [23, 49, 78, 97, 100];
  els.push(line(UNMANAGED.map((p, i) => [bx(i) + BW / 2, yFor(p)]),
    { stroke: T.alert, strokeWidth: 1.8, strokeStyle: 'dashed' }));

  const MANAGED = [21, 44, 68, 82, 39, 58, 96, 31];
  MANAGED.forEach((p, i) => {
    const x = bx(i), h = 2.1 * p;
    els.push(rect(x, BASE - h, BW, h, { stroke: T.ink, fill: T.primary, strokeWidth: 1.2 }));
    els.push(text(x, BASE - h + 7, p + ' %',
      { size: 9.5, align: 'center', width: BW, stroke: T.onAccent }));
    els.push(text(x, 332, 't' + (i + 1), { size: 9.5, align: 'center', width: BW, stroke: T.inkMuted }));
  });

  els.push(text(126, 138, 'CONTEXT ROT ZONE - QUALITY DEGRADES WELL INSIDE THE ADVERTISED LIMIT',
    { size: 8.5, stroke: T.inkMuted }));
  // Above the plot rather than inside it: the band already carries a caption,
  // and the dashed line ends under this label.
  els.push(text(500, 96, 'unmanaged: no moves at all, exhausted by t5',
    { size: 8.5, stroke: T.alert }));

  // Triggers on top of the bars, so a crossing is visible rather than hidden.
  els.push(line([[X0, yFor(95)], [X1, yFor(95)]],
    { stroke: T.alert, strokeWidth: 1.3, strokeStyle: 'dashed' }));
  els.push(line([[X0, yFor(80)], [X1, yFor(80)]],
    { stroke: T.warn, strokeWidth: 1.3, strokeStyle: 'dashed' }));

  [4, 7].forEach((i) => els.push(line([[X0 + i * PITCH, yFor(100)], [X0 + i * PITCH, BASE]],
    { stroke: T.accent, strokeWidth: 1.3, strokeStyle: 'dotted' })));

  // --- the trigger legend ---------------------------------------------------
  els.push(...card(778, 116, 166, 210, { spine: T.accent, strokeWidth: 1.3 }));
  const G = 796, GW = 138;
  els.push(text(G, 124, '95 % HARD TRIGGER', { size: 9, stroke: T.alert }));
  els.push(text(G, 136, 'compact the head', { size: 8, stroke: T.inkMuted }));
  els.push(rule(G, G + GW, 152));
  els.push(text(G, 158, '80 % SOFT TRIGGER', { size: 9, stroke: T.warn }));
  els.push(text(G, 170, fit('offload, clear spent reads', 8, GW, 'soft gloss'),
    { size: 8, stroke: T.inkMuted }));
  els.push(rule(G, G + GW, 186));
  els.push(text(G, 192, 'ILLUSTRATIVE DEFAULTS', { size: 7.5, stroke: T.inkSubtle }));
  [['Shipped triggers are', 206], ['absolute as often:', 218], ['100,000 tokens to', 230],
    ['clear, 150,000 to', 242], ['compact server-side.', 254]]
    .forEach((r) => els.push(text(G, r[1], fit(r[0], 9, GW, 'legend'), { size: 9, stroke: T.ink })));
  els.push(rule(G, G + GW, 268));
  [['95 % of a 200,000-token', 274], ['window leaves only', 286], ['10,000 tokens: too few', 298],
    ['to run the summary in.', 310]]
    .forEach((r) => els.push(text(G, r[1], fit(r[0], 9, GW, 'legend'), { size: 9, stroke: T.inkMuted })));

  // --- what fired, and what it did -----------------------------------------
  const event = (x, w, tint, head, l1, l2) => {
    const e = card(x, 354, w, 56, { spine: tint, strokeWidth: 1.3 });
    e.push(text(x + 18, 366, fit(head, 9, w - 32, 'event head'), { size: 9, stroke: tint }));
    e.push(text(x + 18, 382, fit(l1, 9.5, w - 32, 'event line'), { size: 9.5, stroke: T.ink }));
    e.push(text(x + 18, 396, fit(l2, 9.5, w - 32, 'event line'), { size: 9.5, stroke: T.ink }));
    return e;
  };
  els.push(...event(X0, 320, T.warn, 'AFTER t4 - THE SOFT TRIGGER FIRES AT 80 %',
    'Offload the 2,000-line build log to disk and',
    'clear the spent reads to stubs. No model call.'));
  els.push(...event(452, 320, T.alert, 'AFTER t7 - THE HARD TRIGGER FIRES AT 95 %',
    'Compact t1 to t7 into a structured brief and',
    'keep the recent turns verbatim. One model call.'));

  // --- the five signals -----------------------------------------------------
  els.push(text(M, 424, 'WHAT TO LOG EVERY CALL, AND WHICH BRANCH EACH SIGNAL POINTS TO',
    { size: 9.5, stroke: T.inkSubtle }));

  const SIGNALS = [
    ['WINDOW FILL', T.primary, 'input tokens over the', 'model limit, every call',
      'the number every', 'trigger here depends on'],
    ['TOOL-RESULT SHARE', T.success, 'tool-result tokens as a', 'share of input tokens',
      'over about a half:', 'offload or clear'],
    ['RE-READ RATE', T.warn, 'repeat reads of a path', 'already read this run',
      'a decision was lost', ''],
    ['TURN LENGTH v FILL', T.alert, 'output tokens per turn,', 'plotted against fill',
      'context anxiety, the', 'shape it makes (Post 05)'],
    ['EDITS APPLIED', T.accent, 'cleared tool uses and', 'tokens freed, per call',
      'whether the policy', 'fired, and what it bought'],
  ];

  SIGNALS.forEach((s, i) => {
    const x = M + i * 178, y = 444, iw = 142;
    els.push(...card(x, y, 166, 124, { spine: s[1], strokeWidth: 1.3 }));
    els.push(text(x + 18, y + 10, fit(s[0], 10.5, iw, 'signal name'), { size: 10.5, stroke: T.ink }));
    els.push(rule(x + 18, x + 152, y + 30));
    els.push(text(x + 18, y + 36, 'WHAT TO LOG', { size: 7.5, stroke: T.inkSubtle }));
    els.push(text(x + 18, y + 48, fit(s[2], 8.5, iw, 'signal log'), { size: 8.5, stroke: T.inkMuted }));
    els.push(text(x + 18, y + 60, fit(s[3], 8.5, iw, 'signal log'), { size: 8.5, stroke: T.inkMuted }));
    els.push(rule(x + 18, x + 152, y + 78));
    els.push(text(x + 18, y + 84, 'IT TELLS YOU', { size: 7.5, stroke: T.inkSubtle }));
    els.push(text(x + 18, y + 96, fit(s[4], 9, iw, 'signal tell'), { size: 9, stroke: s[1] }));
    if (s[5]) els.push(text(x + 18, y + 108, fit(s[5], 9, iw, 'signal tell'), { size: 9, stroke: s[1] }));
  });

  els.push(text(M, 582,
    'The window is a budget you spend down every turn, so trigger on fill and not on turn count.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(M, 604,
    'Five turns carrying build logs and twenty terse turns are not the same window, and only the fill number tells them apart.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Window fill across eight turns, with the triggers that fired and the signals to log',
    desc: 'A hand-drawn bar chart of how full the context window is on each of eight calls, drawn '
      + 'as a percentage of the model limit with an axis running from zero to a hundred. A tinted '
      + 'band across the top fifth marks the context rot zone, where quality degrades well inside '
      + 'the advertised limit; its floor is a dashed soft trigger at eighty per cent and a dashed '
      + 'hard trigger sits inside it at ninety-five. The managed run reads twenty-one, forty-four, '
      + 'sixty-eight and eighty-two per cent, where the soft trigger fires and a note records that '
      + 'a two-thousand-line build log was offloaded to disk and the spent reads cleared to stubs '
      + 'with no model call; fill drops to thirty-nine, climbs through fifty-eight to ninety-six, '
      + 'where the hard trigger fires and the first seven turns are compacted into a structured '
      + 'brief with the recent turns kept verbatim; and it ends at thirty-one. A dashed line shows '
      + 'the same run with no moves at all, climbing twenty-three, forty-nine, seventy-eight and '
      + 'ninety-seven per cent until the window is exhausted by the fifth turn. A legend column '
      + 'records that both percentage triggers are illustrative defaults, that shipped triggers are '
      + 'as often absolute, at a hundred thousand input tokens to clear a tool result and a hundred '
      + 'and fifty thousand to compact server-side, and that ninety-five per cent of a two hundred '
      + 'thousand token window leaves only ten thousand tokens, too few to run the summarisation '
      + 'in. Five cards below give the signals to log every call and what each one tells you: '
      + 'window fill, the number every trigger depends on; tool-result share, where over about a '
      + 'half means offload or clear; re-read rate, which says a decision was lost; turn length '
      + 'against fill, the shape context anxiety makes in a trace; and edits applied, which says '
      + 'whether the policy fired at all and what it bought.',
  };
}

// ---------------------------------------------------------------- diagram 2
function threeMoves() {
  resetSeq();
  const W = 960, H = 580;

  const els = [...heading('The three corrective moves: offload, compact, reset',
    'Escalate as the window fills. Offloading is cheap and lossless; a reset is total; compaction sits between.')];

  els.push(text(M, 88, 'cheaper, lossless', { size: 9.5, stroke: T.success }));
  els.push(arrow([[190, 94], [740, 94]], { stroke: T.inkSubtle, strokeWidth: 1.1 }));
  els.push(text(760, 88, 'more aggressive, lossy', { size: 9.5, align: 'right', width: 160, stroke: T.alert }));

  const MOVES = [
    [M, 'OFFLOAD', 'lossless', T.success,
      ['Write a big tool output to disk and return',
        'a pointer: the path, the size, and the',
        'query that gets the rest of it.'],
      ['One tool returned a wall of text and spiked',
        'the window in a single turn.'],
      ['Nothing. It is relocated, not dropped, and',
        'one read brings the whole thing back.'],
      ['Offload over 4,000 characters, about 1,000',
        'tokens. The pointer keeps the first 15 and',
        'the last 15 lines of the output.']],
    [332, 'COMPACT', 'lossy', T.warn,
      ['Summarise the older turns into a structured',
        'brief, and keep the most recent turns',
        'verbatim in the window.'],
      ['History itself is the weight: many ordinary',
        'turns rather than one big one.'],
      ['Some detail. You decide in advance what the',
        'brief is required to preserve.'],
      ['Illustrative triggers: 80 % soft, 95 % hard.',
        'The server-side default is absolute instead:',
        '150,000 input tokens.']],
    [624, 'RESET', 'total', T.alert,
      ['Write a handoff file, discard the window,',
        'and reseed a fresh one from the handoff',
        'file, and from nothing else.'],
      ['The task outgrows one window, or rot has set',
        'in and a summary cannot rescue it.'],
      ['Everything the handoff did not capture.',
        'The loss here is total.'],
      ['Six fields in the handoff contract. A reset',
        'that costs three turns of rediscovery is',
        'short a field.']],
  ];

  MOVES.forEach((m) => {
    const x = m[0], y = 112, tint = m[3], iw = 264;
    els.push(...card(x, y, 296, 302, { spine: tint, strokeWidth: 1.4 }));
    els.push(text(x + 18, y + 12, m[1], { size: 16, stroke: T.ink }));
    els.push(text(x + 18, y + 38, m[2], { size: 9.5, stroke: tint }));

    const block = (label, lines, top, colour) => {
      els.push(rule(x + 18, x + 278, top - 8));
      els.push(text(x + 18, top, label, { size: 8.5, stroke: T.inkSubtle }));
      lines.forEach((l, i) => els.push(text(x + 18, top + 14 + i * 14,
        fit(l, 9.5, iw, 'move line'), { size: 9.5, stroke: colour })));
    };
    block('WHAT IT DOES', m[4], y + 66, T.ink);
    block('WHEN TO USE IT', m[5], y + 134, T.ink);
    block('WHAT IT COSTS YOU', m[6], y + 188, tint);
    block('IN NUMBERS, FROM THE POST', m[7], y + 242, T.inkMuted);
  });

  const band = (x, w, tint, head, lines) => {
    const b = card(x, 430, w, 86, { spine: tint, strokeWidth: 1.3 });
    b.push(text(x + 18, 442, fit(head, 9, w - 32, 'band head'), { size: 9, stroke: tint }));
    lines.forEach((l, i) => b.push(text(x + 18, 460 + i * 16,
      fit(l, 9.5, w - 32, 'band line'), { size: 9.5, stroke: T.ink })));
    return b;
  };
  els.push(...band(M, 448, T.primary, 'PREVENTATIVE - BEFORE THE BYTES ENTER THE PREFIX', [
    'Progressive disclosure keeps tool schemas out of the window, and',
    'offloading at the tool boundary keeps a big output out. Neither move',
    'touches the cached prefix, which is the second reason to build these first.']));
  els.push(...band(504, 416, T.alert, 'CORRECTIVE - AFTER THE BYTES ARE ALREADY CACHED', [
    'Clearing, compaction and reset all rewrite a prefix already built',
    'and cached, so each pays a cache write on the new prefix. Reach',
    'for one only when prevention was not enough.']));

  els.push(text(M, 528,
    'Reach for the cheapest move that works. Offload first; reset only when the window itself is the problem.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(M, 550,
    'A fourth rung sits between the first two: clearing a spent tool result to a stub, which costs no model call at all.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Offload, compact and reset compared by what each does, when, what it costs, and its numbers',
    desc: 'A hand-drawn comparison of three context-management moves, arranged from cheaper and '
      + 'lossless on the left to more aggressive and lossy on the right, each card carrying what '
      + 'the move does, when to use it, what it costs, and the numbers the post gives for it. '
      + 'Offload, marked lossless: it writes a big tool output to disk and returns a pointer '
      + 'carrying the path, the size and the query that gets the rest; use it when one tool '
      + 'returned a wall of text and spiked the window in a single turn; it costs nothing, since '
      + 'the output is relocated rather than dropped and one read brings it back; and its numbers '
      + 'are a threshold of four thousand characters, about a thousand tokens, with the pointer '
      + 'keeping the first fifteen and the last fifteen lines. Compact, marked lossy: it summarises '
      + 'the older turns into a structured brief and keeps the most recent turns verbatim; use it '
      + 'when history itself is the weight, many ordinary turns rather than one big one; it costs '
      + 'some detail, and you decide in advance what the brief must preserve; and its numbers are '
      + 'the illustrative triggers, eighty per cent soft and ninety-five per cent hard, against a '
      + 'server-side default of a hundred and fifty thousand input tokens. Reset, marked total: it '
      + 'writes a handoff file, discards the window and reseeds a fresh one from the handoff alone; '
      + 'use it when the task outgrows one window, or rot has set in and a summary cannot fix it; '
      + 'it costs everything the handoff did not capture; and its numbers are the six fields of the '
      + 'handoff contract, with a reset that costs three turns of rediscovery marking a handoff '
      + 'that is short a field. A band underneath splits the preventative moves, which act before '
      + 'the bytes enter the prefix and leave the cache untouched, from the corrective ones, which '
      + 'rewrite a prefix already built and cached and so pay a cache write on the new prefix. '
      + 'Captions record that you should reach for the cheapest move that works, and that a fourth '
      + 'rung sits between the first two: clearing a spent tool result to a stub, which costs no '
      + 'model call at all.',
  };
}

// ---------------------------------------------------------------- diagram 3
function escalationLadder() {
  resetSeq();
  const W = 960, H = 626;

  const els = [...heading('The four rungs, and what each one costs the cache',
    'Take the cheapest rung that solves the problem. Two of the four need no model call and paraphrase nothing.')];

  els.push(text(56, 96, 'THE LADDER, CHEAPEST FIRST', { size: 10, stroke: T.inkSubtle }));
  els.push(text(560, 96, 'WHAT IS LOST', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(760, 96, 'MESSAGE-HISTORY CACHE', { size: 8.5, stroke: T.inkSubtle }));

  const RUNGS = [
    ['1', 'OFFLOAD', T.success,
      'Write a big tool output to disk and leave a pointer in the window.',
      'One observation spiked the window. No model call, nothing paraphrased.',
      'none: it is only relocated', '', 'untouched'],
    ['2', 'CLEAR', T.success,
      'Replace a tool result that has been acted on with a one-line stub.',
      'Stale reads are the weight and their decisions are already made. No model call.',
      'near none: the stub says', 'what it was and how to get it', 'broken from there on'],
    ['3', 'COMPACT', T.warn,
      'Summarise the older turns into a structured brief; keep recent turns verbatim.',
      'History itself is the weight: many ordinary turns rather than one big one.',
      'some detail, and you decide', 'in advance what must survive', 'rewritten from the cut'],
    ['4', 'RESET', T.alert,
      'Write a handoff file, discard the window, and reseed a fresh one from it.',
      'The task outgrows one window, or rot has set in and a summary cannot rescue it.',
      'everything that did not', 'reach the handoff file', 'starts over'],
  ];

  RUNGS.forEach((r, i) => {
    const y = 112 + i * 76;
    els.push(...card(40, y, 880, 68, { spine: r[2], strokeWidth: 1.4 }));
    els.push(ellipse(56, y + 10, 26, 26, { stroke: r[2], fill: r[2], strokeWidth: 1.1 }));
    els.push(text(56, y + 16, r[0], { size: 12, align: 'center', width: 26, stroke: T.onAccent }));
    els.push(text(96, y + 8, r[1], { size: 13.5, stroke: T.ink }));
    els.push(text(96, y + 30, fit(r[3], 9.5, 440, 'rung what'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(96, y + 46, fit(r[4], 9.5, 440, 'rung when'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(560, y + 16, fit(r[5], 10, 190, 'rung loss'), { size: 10, stroke: r[2] }));
    if (r[6]) els.push(text(560, y + 32, fit(r[6], 10, 190, 'rung loss'), { size: 10, stroke: r[2] }));
    els.push(text(760, y + 16, fit(r[7], 10, 160, 'rung cache'), { size: 10, stroke: T.ink }));
  });

  // --- what a compaction actually costs ------------------------------------
  // Straight out of the token-equivalent table in section 7: a 200,000-token
  // window sitting at 160,000, priced against base input.
  els.push(...card(40, 420, 880, 146, { spine: T.accent, strokeWidth: 1.4 }));
  els.push(text(58, 432,
    'WHAT THE REWRITE COSTS: TOKEN-EQUIVALENTS FOR A 200,000-TOKEN WINDOW SITTING AT 160,000',
    { size: 9, stroke: T.inkSubtle }));

  // The two value columns sit under the two columns of the ladder above.
  const C1 = 560, C2 = 760, CW = 150;
  els.push(text(C1, 450, 'DEEP: 160K TO 25K', { size: 9, stroke: T.success }));
  els.push(text(C2, 450, 'SHALLOW: 160K TO 130K', { size: 9, stroke: T.alert }));

  const COSTS = [
    ['Summary call over the head, read warm at 0.1x base input', '13,500', '3,500', T.inkMuted],
    ['Cache write on the new prefix at 1.25x base input', '31,300', '162,500', T.inkMuted],
    ['The compaction event', '44,800', '166,000', T.ink],
    ['Saved on each later turn, at 0.1x of the tokens removed', '13,500', '3,000', T.inkMuted],
    ['Turns to break even', 'about 3', 'about 55', T.ink],
  ];
  COSTS.forEach((c, i) => {
    const y = 470 + i * 18;
    if (i) els.push(rule(58, 902, y - 4));
    els.push(text(58, y, fit(c[0], 9.5, 540, 'cost row'), { size: 9.5, stroke: c[3] }));
    els.push(text(C1, y, fit(c[1], 9.5, CW, 'cost value'), { size: 9.5, stroke: c[3] }));
    els.push(text(C2, y, fit(c[2], 9.5, CW, 'cost value'), { size: 9.5, stroke: c[3] }));
  });

  els.push(text(M, 578,
    'Rungs 1 and 2 need no model call and paraphrase nothing, which is why they are worth building before rung 3.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(M, 600,
    'Compact rarely and deeply: a shallow compaction pays nearly the whole write premium and buys almost no read saving.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Four context-management rungs, their loss, their cache cost, and the price of a compaction',
    desc: 'A hand-drawn ladder of four context-management moves, cheapest first, each with what is '
      + 'lost and what happens to the cached message history. Rung one, offload: write a big tool '
      + 'output to disk and leave a pointer in the window, for when one observation spiked it; no '
      + 'model call and nothing paraphrased; nothing is lost because the output is only relocated; '
      + 'and the cache is untouched. Rung two, clear: replace a tool result that has been acted on '
      + 'with a one-line stub, for when stale reads are the weight and their decisions are already '
      + 'made; no model call; near-nothing is lost because the stub says what it was and how to get '
      + 'it back; and the cache is broken from that point on. Rung three, compact: summarise the '
      + 'older turns into a structured brief while keeping recent turns verbatim, for when history '
      + 'itself is the weight; some detail is lost, and you decide in advance what must survive; '
      + 'and the history is rewritten from the cut. Rung four, reset: write a handoff file, discard '
      + 'the window and reseed a fresh one, for when the task outgrows one window or rot has '
      + 'already set in; everything that did not reach the handoff is lost; and the cache starts '
      + 'over. A table underneath prices the rewrite in token-equivalents for a two hundred '
      + 'thousand token window sitting at a hundred and sixty thousand, comparing a deep compaction '
      + 'down to twenty-five thousand against a shallow one down to a hundred and thirty thousand. '
      + 'The summary call over the head, read warm at a tenth of base input, costs thirteen '
      + 'thousand five hundred against three thousand five hundred; the cache write on the new '
      + 'prefix at one and a quarter times base input costs thirty-one thousand three hundred '
      + 'against a hundred and sixty-two thousand five hundred; the compaction event totals '
      + 'forty-four thousand eight hundred against a hundred and sixty-six thousand; each later '
      + 'turn saves thirteen thousand five hundred against three thousand; and break-even arrives '
      + 'in about three turns against about fifty-five. Captions record that the first two rungs '
      + 'need no model call and paraphrase nothing, so they are worth building before the third, '
      + 'and that you should compact rarely and deeply, because a shallow compaction pays nearly '
      + 'the whole write premium and buys almost no read saving.',
  };
}

module.exports = { windowTimeline, threeMoves, escalationLadder };

if (require.main === module) {
  emit('01-window-timeline', windowTimeline());
  emit('02-three-moves', threeMoves());
  emit('03-escalation-ladder', escalationLadder());
}
