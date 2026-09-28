// The post 03 diagrams, hand-drawn.
//
//   01-agent-loop          960 x 600  Published figure.
//   02-stateless-model     960 x 580  Published figure.
//   03-batch-vs-streaming  960 x 550  Published figure: section 10 had no figure.
//
// All three were thin when they were first promoted: 960-wide canvases barely
// 440 tall, with empty quadrants and labels where the post has measurements.
// Each now carries a second tier. Every number in them is read from the post
// or from code/03-agent-loop, and the illustrative ones say so on the figure,
// because the post says so in the prose.

const { T, rect, ellipse, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

// ---------------------------------------------------------------- diagram 1
function agentLoop() {
  resetSeq();
  const W = 960, H = 600;

  const els = [...heading('The agent loop: reason, act, observe, and the four exits',
    'A harness is a loop. The body is four lines; the engineering is in how it stops.')];

  const box = (x, y, w, h, name, gloss, o = {}) => {
    const els = [rect(x, y, w, h, { stroke: o.stroke ?? T.ink, fill: o.fill ?? T.surface, strokeWidth: o.strokeWidth ?? 1.3 })];
    els.push(text(x, y + (gloss ? 10 : (h - 16) / 2), name,
      { size: 13, align: 'center', width: w, stroke: o.stroke ?? T.ink }));
    if (gloss) els.push(text(x, y + 32, gloss, { size: 9.5, align: 'center', width: w, stroke: T.inkMuted }));
    return els;
  };

  // --- tier 1, left: the loop body ------------------------------------------
  els.push(...card(40, 88, 560, 280, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 98, 'THE LOOP BODY - ONE TURN IS ONE MODEL CALL', { size: 10, stroke: T.inkSubtle }));
  els.push(text(58, 113, 'call the model, run what it asked for, feed the result back, call again',
    { size: 9, stroke: T.inkSubtle }));

  els.push(...box(58, 148, 116, 38, 'USER TASK', null, { fill: T.neutral1 }));
  els.push(arrow([[176, 167], [196, 167]], { stroke: T.inkMuted, strokeWidth: 1.3 }));

  els.push(...box(200, 140, 168, 56, 'REASON', 'the model thinks and decides', { strokeWidth: 1.5 }));
  els.push(...box(430, 140, 146, 56, 'ACT', 'call a tool'));
  els.push(...box(430, 234, 146, 56, 'OBSERVE', 'read the result'));

  els.push(arrow([[370, 168], [426, 168]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(text(376, 147, 'tool call', { size: 9, stroke: T.inkMuted }));

  els.push(arrow([[503, 198], [503, 230]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(text(510, 204, 'run it', { size: 9, stroke: T.inkMuted }));

  els.push(arrow([[428, 262], [410, 262], [410, 214], [276, 214], [276, 200]],
    { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(text(274, 218, 'observation goes back in', { size: 9, stroke: T.inkMuted }));

  els.push(arrow([[240, 198], [240, 240]], { stroke: T.success, strokeWidth: 1.5 }));
  els.push(text(148, 208, 'no tool call', { size: 9, align: 'right', width: 84, stroke: T.success }));
  els.push(...box(176, 244, 172, 44, 'FINAL ANSWER', 'the model says it is done',
    { stroke: T.success, strokeWidth: 1.5 }));

  // What exit 1 actually is, which is the part a first loop gets wrong.
  els.push(rect(58, 300, 524, 58, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
  els.push(text(70, 306, 'EXIT 1 IS A TERMINAL stop_reason, NOT AN ABSENT TOOL CALL', { size: 9, stroke: T.inkSubtle }));
  els.push(text(70, 322, 'final: end_turn, stop_sequence', { size: 10.5, stroke: T.success }));
  els.push(text(300, 322, 'not final: max_tokens, refusal, pause_turn', { size: 10.5, stroke: T.alert }));
  els.push(text(70, 340, 'a truncated or a declined turn also arrives with no tool call, and neither is an answer',
    { size: 9, stroke: T.inkMuted }));

  // --- tier 1, right: one turn on the wire ----------------------------------
  els.push(...card(624, 88, 296, 280, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(640, 98, 'ONE TURN ON THE WIRE', { size: 10, stroke: T.inkSubtle }));
  els.push(text(640, 113, 'the two messages the API makes you get right', { size: 9, stroke: T.inkSubtle }));

  els.push(rect(640, 132, 264, 66, { stroke: T.border, fill: T.surface, strokeWidth: 1 }));
  els.push(text(652, 138, 'assistant', { size: 10, stroke: T.primary }));
  els.push(text(652, 154, fit('tool_use   id "tu_1"', 10, 240, 'wire assistant'), { size: 10, stroke: T.ink }));
  els.push(text(652, 170, 'name calculator', { size: 9.5, stroke: T.inkMuted }));
  els.push(text(652, 183, fit('input {"expression": "(2 + 3) * 4"}', 9, 240, 'wire input'),
    { size: 9, stroke: T.inkMuted }));

  els.push(arrow([[700, 200], [700, 222]], { stroke: T.accent, strokeWidth: 1.3 }));
  els.push(text(712, 204, 'the same id', { size: 9, stroke: T.accent }));

  els.push(rect(640, 226, 264, 52, { stroke: T.border, fill: T.surface, strokeWidth: 1 }));
  els.push(text(652, 232, 'user', { size: 10, stroke: T.primary }));
  els.push(text(652, 248, fit('tool_result   tool_use_id "tu_1"', 10, 240, 'wire user'), { size: 10, stroke: T.ink }));
  els.push(text(652, 264, 'content "20"', { size: 9.5, stroke: T.inkMuted }));

  els.push(rule(640, 904, 292));
  els.push(text(640, 300, 'TWO RULES OF THE API', { size: 9, stroke: T.inkSubtle }));
  els.push(text(640, 314, fit('a  each result repeats its tool_use id', 9.5, 264, 'api rule a'),
    { size: 9.5, stroke: T.ink }));
  els.push(text(640, 330, fit('b  one turn, one user message of results', 9.5, 264, 'api rule b'),
    { size: 9.5, stroke: T.ink }));
  els.push(text(640, 348, fit('a failed tool returns its error as the observation', 9, 264, 'api rule c'),
    { size: 9, stroke: T.inkMuted }));

  // --- tier 2: the four exits, with the companion's actual defaults ---------
  const EXITS = [
    ['1', 'Final answer', 'a terminal stop_reason', 'and no tool call',
      'StopReason.COMPLETED', 'the only exit that means', 'success - verify it: Post 11', T.success],
    ['2', 'Max iterations', 'the turn counter reaches', 'the hard cap',
      'max_iters = 12', 'a demo number: set a cap', 'above the p95 turn count', T.warn],
    ['3', 'Token budget', 'the tokens spent reach', 'the ceiling for the task',
      'token_budget = None (off)', 'turns bound nothing that', 'you are actually billed for', T.primary],
    ['4', 'No progress', 'N identical tool-call', 'signatures in a row',
      'no_progress_window = 3', 'the doom-loop guard:', 'Post 05, failure mode 4', T.alert],
  ];
  EXITS.forEach((e, i) => {
    const px = 40 + i * 223, py = 386, tint = e[7];
    els.push(...card(px, py, 211, 168, { spine: tint, strokeWidth: 1.3 }));
    els.push(rect(px + 14, py + 14, 24, 19, { stroke: tint, fill: tint, strokeWidth: 1 }));
    els.push(text(px + 14, py + 16, e[0], { size: 11.5, align: 'center', width: 24, stroke: T.onAccent }));
    els.push(text(px + 46, py + 12, fit(e[1], 13.5, 150, 'exit name'), { size: 13.5, stroke: T.ink }));
    els.push(rule(px + 14, px + 197, py + 42));
    els.push(text(px + 14, py + 50, 'FIRES WHEN', { size: 8.5, stroke: T.inkSubtle }));
    els.push(text(px + 14, py + 64, fit(e[2], 10, 183, 'exit when'), { size: 10, stroke: T.ink }));
    els.push(text(px + 14, py + 78, fit(e[3], 10, 183, 'exit when'), { size: 10, stroke: T.ink }));
    els.push(rule(px + 14, px + 197, py + 96));
    els.push(text(px + 14, py + 104, 'IN THE CODE COMPANION', { size: 8.5, stroke: T.inkSubtle }));
    els.push(text(px + 14, py + 117, fit(e[4], 11, 183, 'exit default'), { size: 11, stroke: tint }));
    els.push(text(px + 14, py + 138, fit(e[5], 9, 183, 'exit note'), { size: 9, stroke: T.inkMuted }));
    els.push(text(px + 14, py + 150, fit(e[6], 9, 183, 'exit note'), { size: 9, stroke: T.inkMuted }));
  });

  els.push(text(40, 566,
    'Check the answer exit first, so a run that has just succeeded is not cut off by a guard it was about to satisfy.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 584,
    'Most agent bugs are stop-condition bugs, not reasoning bugs.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The reason, act, observe loop, one turn on the wire, and the four conditions it stops on',
    desc: 'A hand-drawn figure in two tiers. The upper left panel draws the loop body: a user task '
      + 'enters a REASON box, where the model thinks and decides. One arrow marked tool call leads '
      + 'right to ACT, which calls a tool; a second leads down to OBSERVE, which reads the result; '
      + 'and a return path carries the observation back into REASON. A green arrow marked no tool '
      + 'call leads down out of REASON to a FINAL ANSWER box. A strip beneath the loop warns that '
      + 'exit one is a terminal stop reason rather than an absent tool call: end_turn and '
      + 'stop_sequence are final, while max_tokens, refusal and pause_turn are not, because a '
      + 'truncated or a declined turn also arrives with no tool call. The upper right panel shows '
      + 'one turn on the wire: an assistant message carrying a tool_use block with id tu_1, the '
      + 'name calculator and the input expression two plus three, times four; then a user message '
      + 'carrying a tool_result whose tool_use_id repeats tu_1 with the content twenty. Its rules '
      + 'are that each result repeats its tool_use id, that one turn returns one user message of '
      + 'results, and that a failed tool returns its error as the observation. The lower tier gives '
      + 'the four exits as cards, each with what fires it and the code companion default. One, '
      + 'final answer: a terminal stop reason and no tool call, StopReason.COMPLETED, the only exit '
      + 'that means success, verified in post 11. Two, max iterations: the turn counter reaches the '
      + 'hard cap, max_iters equals twelve, a demo number, with a real cap set above the '
      + 'ninety-fifth percentile turn count. Three, token budget: the tokens spent reach the '
      + 'ceiling, token_budget is None and therefore off by default, because turns bound nothing '
      + 'you are billed for. Four, no progress: N identical tool-call signatures in a row, '
      + 'no_progress_window equals three, the doom-loop guard from post 05. Captions record that '
      + 'the answer exit is checked first so a successful run is not cut off by a guard, and that '
      + 'most agent bugs are stop-condition bugs rather than reasoning bugs.',
  };
}

// ---------------------------------------------------------------- diagram 2
function statelessModel() {
  resetSeq();
  const W = 960, H = 580;

  const els = [...heading('The model forgets; the loop remembers',
    'Every iteration is a fresh API call with the whole history re-sent. The model holds no state between calls.')];

  // --- left: what one call actually takes and returns -----------------------
  els.push(...card(40, 88, 296, 292, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(64, 100, 'MODEL', { size: 18, stroke: T.ink }));
  els.push(text(64, 126, 'a stateless function', { size: 11, stroke: T.inkMuted }));
  els.push(rule(58, 318, 148));

  els.push(text(58, 156, 'IN, EVERY CALL - THE CACHE PREFIX ORDER', { size: 9, stroke: T.inkSubtle }));
  const IN = ['1  tools', '2  system prompt', '3  messages: the whole history'];
  IN.forEach((s, i) => {
    const y = 172 + i * 28;
    els.push(rect(58, y, 260, 24, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
    els.push(text(70, y + 6, fit(s, 10.5, 236, 'input row'), { size: 10.5, stroke: T.ink }));
  });
  els.push(text(58, 262, 'change anything in that head and every', { size: 9, stroke: T.accent }));
  els.push(text(58, 274, 'later turn pays full price again', { size: 9, stroke: T.accent }));

  els.push(rule(58, 318, 292));
  els.push(text(58, 300, 'OUT, ONE RESPONSE', { size: 9, stroke: T.inkSubtle }));
  els.push(rect(58, 314, 260, 26, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
  els.push(text(70, 321, fit('content blocks + stop_reason', 10.5, 236, 'output row'), { size: 10.5, stroke: T.ink }));
  els.push(text(58, 352, 'no memory between calls', { size: 12, stroke: T.alert }));

  // --- right: the history the harness holds ---------------------------------
  els.push(...card(400, 88, 520, 292, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(416, 98, 'THE LOOP, IN THE HARNESS: IT HOLDS THE CONVERSATION HISTORY',
    { size: 10, stroke: T.inkSubtle }));

  const CHIPS = [
    ['system prompt', T.neutral1],
    ['user: "the task"', T.neutral1],
    ['assistant: tool call', T.surface],
    ['tool: result', T.surface],
    ['assistant: tool call', T.surface],
    ['tool: result', T.surface],
    ['assistant: final answer', T.surface],
  ];
  CHIPS.forEach((c, i) => {
    const y = 120 + i * 26;
    els.push(rect(416, y, 372, 22, { stroke: T.border, fill: c[1], strokeWidth: 1 }));
    els.push(text(428, y + 4, c[0], { size: 10, stroke: T.ink }));
  });
  const TURNS = [[172, 220, 'turn 1'], [224, 272, 'turn 2'], [276, 298, 'turn 3']];
  TURNS.forEach((t) => {
    els.push(line([[800, t[0]], [800, t[1]]], { stroke: T.inkSubtle, strokeWidth: 1, roughness: 0.4 }));
    els.push(text(808, (t[0] + t[1]) / 2 - 6, t[2], { size: 9.5, stroke: T.inkMuted }));
  });
  els.push(text(416, 306, 'grows every turn: this is the state the model itself lacks',
    { size: 10, stroke: T.accent }));

  els.push(rect(416, 326, 488, 44, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
  els.push(text(428, 332, 'ILLUSTRATIVE SIZES, FROM SECTION 8 OF THE POST', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(428, 347, fit('turn 1 sends about 6,000 tokens; turn 12 about 40,000: roughly +3,100 a turn',
    10, 464, 'growth line'), { size: 10, stroke: T.ink }));

  // --- the two moves that manufacture continuity ----------------------------
  els.push(arrow([[398, 168], [340, 168]], { stroke: T.primary, strokeWidth: 1.5 }));
  els.push(arrow([[340, 248], [398, 248]], { stroke: T.primary, strokeWidth: 1.5 }));
  els.push(ellipse(357, 157, 22, 22, { stroke: T.primary, fill: T.surface, strokeWidth: 1.3 }));
  els.push(text(357, 162, '1', { size: 11, align: 'center', width: 22, stroke: T.primary }));
  els.push(ellipse(357, 237, 22, 22, { stroke: T.primary, fill: T.surface, strokeWidth: 1.3 }));
  els.push(text(357, 242, '2', { size: 11, align: 'center', width: 22, stroke: T.primary }));

  // --- tier 2: what re-sending is billed at ---------------------------------
  els.push(...card(40, 398, 880, 126, { spine: T.warn, strokeWidth: 1.3 }));
  els.push(text(58, 408, 'WHAT THE RE-SENT HISTORY COSTS: THREE RUNS OF ONE TASK, ALL WITH max_iters = 12',
    { size: 9.5, stroke: T.inkSubtle }));
  const COLS = [[58, 'RUN'], [520, 'ITERATIONS'], [630, 'INPUT TOKENS RE-READ'], [820, 'BILLED AT $3/M']];
  COLS.forEach((c) => els.push(text(c[0], 426, c[1], { size: 8.5, stroke: T.inkSubtle })));
  els.push(rule(58, 902, 438));

  const ROWS = [
    ['answers at iteration 6', '6', 'about 83,000', 'about $0.25'],
    ['runs to the cap', '12', 'about 277,000', 'about $0.83'],
    ['runs to the cap, with one 20,000-token log read at turn 5', '12', 'about 417,000', 'about $1.25'],
  ];
  ROWS.forEach((r, i) => {
    const y = 444 + i * 20;
    if (i) els.push(rule(58, 902, y - 6));
    els.push(text(58, y, fit(r[0], 10.5, 450, 'cost run'), { size: 10.5, stroke: T.ink }));
    els.push(text(520, y, r[1], { size: 10.5, stroke: T.ink }));
    els.push(text(630, y, r[2], { size: 10.5, stroke: T.ink }));
    els.push(text(820, y, r[3], { size: 10.5, stroke: T.warn }));
  });
  els.push(text(58, 502, fit('the 20,000-token log read at turn 5 is re-read on all 7 turns that follow it: +140,000 tokens',
    9.5, 844, 'cost note'), { size: 9.5, stroke: T.inkMuted }));

  els.push(text(40, 536,
    '1  The harness sends the full history on every call.    2  It appends the one new message the model returns, and repeats.',
    { size: 11, stroke: T.ink }));
  els.push(text(40, 556,
    'Continuity is the harness re-sending a history that grows every turn. Same cap, five-fold spread in the bill; counts and rate illustrative.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A stateless model, the loop that holds its history, and what re-sending that history is billed',
    desc: 'A hand-drawn figure in two tiers. On the upper left, the model is drawn as a stateless '
      + 'function. What goes in on every call is listed in the cache prefix order: one, tools; two, '
      + 'the system prompt; three, the messages, meaning the whole history, with the warning that '
      + 'changing anything in that head makes every later turn pay full price again. What comes out '
      + 'is one response of content blocks plus a stop_reason, and the model keeps no memory '
      + 'between calls. On the upper right, the loop inside the harness holds the conversation '
      + 'history as a stack of message chips: a system prompt, the user task, then for turn one an '
      + 'assistant tool call and a tool result, for turn two another pair, and for turn three an '
      + 'assistant final answer. The stack grows every turn, and that growth is the state the model '
      + 'itself lacks; an inset gives illustrative sizes from section eight of the post, where turn '
      + 'one sends about six thousand tokens and turn twelve about forty thousand, roughly three '
      + 'thousand one hundred more a turn. Two numbered arrows run between the halves: one, the '
      + 'harness sends the full history on every call; two, it appends the one new message the '
      + 'model returns, and repeats. The lower tier is a table of what the re-sent history costs '
      + 'across three runs of one task, all capped at twelve iterations: a run that answers at '
      + 'iteration six re-reads about eighty-three thousand input tokens and is billed about '
      + 'twenty-five cents; a run to the cap re-reads about two hundred and seventy-seven thousand '
      + 'for about eighty-three cents; and the same run with one twenty-thousand-token log read at '
      + 'turn five re-reads about four hundred and seventeen thousand for about one dollar '
      + 'twenty-five, at three dollars per million input tokens. The token counts and the rate are '
      + 'illustrative. A caption records the five-fold spread in the bill under an identical cap.',
  };
}

// ---------------------------------------------------------------- diagram 3
function batchVsStreaming() {
  resetSeq();
  const W = 960, H = 550;

  const els = [...heading('Batch versus streaming: the same turn, two schedules',
    'The loop logic is identical either way. What moves is the moment the tool is allowed to start.')];

  // --- tier 1, left: the two timelines on one axis --------------------------
  els.push(...card(40, 88, 600, 292, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 98, 'ONE TURN, TWO SCHEDULES, ONE TIME AXIS', { size: 10, stroke: T.inkSubtle }));

  const laneLabel = (y, s) => text(40, y, s, { size: 9.5, align: 'right', width: 68, stroke: T.inkSubtle });
  // Bar labels sit left, not centred: the streaming row's dashed "fully formed"
  // marker falls where a centred label's tail would be, and drawing a line
  // through the words is the one thing that made this figure look broken.
  const bar = (x, y, w, label, fill, ink) => [
    rect(x, y, w, 28, { stroke: T.ink, fill, strokeWidth: 1.3 }),
    text(x + 11, y + 7, fit(label, 10.5, w - 22, 'bar ' + label), { size: 10.5, stroke: ink }),
  ];

  // Row A: batch.
  els.push(text(58, 120, 'BATCH - wait for the complete response, then act', { size: 11.5, stroke: T.primary }));
  els.push(laneLabel(146, 'MODEL'));
  els.push(...bar(118, 140, 290, 'generates the response', T.neutral1, T.ink));
  els.push(laneLabel(184, 'HARNESS'));
  els.push(...bar(414, 178, 126, 'runs the tool', T.primary, T.onAccent));
  els.push(text(546, 185, 'next call', { size: 9.5, stroke: T.inkMuted }));
  els.push(text(118, 212, 'the tool cannot start until the last token has arrived',
    { size: 9, stroke: T.inkMuted }));

  // Row B: streaming.
  els.push(text(58, 238, 'STREAMING - act the moment the tool call is fully formed', { size: 11.5, stroke: T.success }));
  els.push(laneLabel(264, 'MODEL'));
  els.push(...bar(118, 258, 290, 'generates the response', T.neutral1, T.ink));
  els.push(laneLabel(302, 'HARNESS'));
  els.push(line([[318, 250], [318, 294]], { stroke: T.success, strokeWidth: 1.5, strokeStyle: 'dashed' }));
  els.push(...bar(318, 296, 126, 'runs the tool', T.success, T.onAccent));
  els.push(text(450, 303, 'next call', { size: 9.5, stroke: T.inkMuted }));
  els.push(text(118, 330, 'the tool starts mid-stream, as soon as its arguments parse',
    { size: 9, stroke: T.inkMuted }));

  // What the difference is worth.
  els.push(line([[540, 208], [540, 354]], { stroke: T.inkSubtle, strokeWidth: 1, strokeStyle: 'dotted' }));
  els.push(line([[444, 326], [444, 354]], { stroke: T.inkSubtle, strokeWidth: 1, strokeStyle: 'dotted' }));
  els.push(line([[444, 354], [540, 354]], { stroke: T.success, strokeWidth: 1.3, roughness: 0.4 }));
  els.push(text(546, 348, 'latency saved', { size: 9.5, stroke: T.success }));

  els.push(arrow([[118, 368], [590, 368]], { stroke: T.inkSubtle, strokeWidth: 1 }));
  els.push(text(596, 362, 'time', { size: 9.5, stroke: T.inkSubtle }));

  // --- tier 1, right: the fine print ----------------------------------------
  els.push(...card(664, 88, 256, 292, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(680, 98, 'STREAMING: THE FINE PRINT', { size: 10, stroke: T.inkSubtle }));

  els.push(text(680, 118, 'HOW "FULLY FORMED" IS DECIDED', { size: 9, stroke: T.inkSubtle }));
  els.push(text(680, 134, fit('arguments arrive as partial-JSON', 9.5, 224, 'fine print'), { size: 9.5, stroke: T.ink }));
  els.push(text(680, 147, fit('deltas; the harness concatenates', 9.5, 224, 'fine print'), { size: 9.5, stroke: T.ink }));
  els.push(text(680, 160, fit('them until the string parses', 9.5, 224, 'fine print'), { size: 9.5, stroke: T.ink }));
  els.push(text(680, 178, fit('input_json_delta / partial_json', 9.5, 224, 'fine print'), { size: 9.5, stroke: T.primary }));
  els.push(text(680, 194, fit('eager_input_streaming starts them', 9, 224, 'fine print'), { size: 9, stroke: T.inkMuted }));
  els.push(text(680, 206, 'sooner, one tool at a time', { size: 9, stroke: T.inkMuted }));

  els.push(rule(680, 904, 222));
  els.push(text(680, 230, 'WHAT IS GENUINELY STREAMING', { size: 9, stroke: T.inkSubtle }));
  els.push(ellipse(680, 248, 9, 9, { stroke: T.success, fill: T.success, strokeWidth: 1 }));
  els.push(text(696, 244, fit('output appears immediately', 9.5, 208, 'benefit'), { size: 9.5, stroke: T.ink }));
  els.push(ellipse(680, 270, 9, 9, { stroke: T.success, fill: T.success, strokeWidth: 1 }));
  els.push(text(696, 266, fit('a run can be interrupted', 9.5, 208, 'benefit'), { size: 9.5, stroke: T.ink }));
  els.push(text(696, 279, 'mid-turn: Post 15', { size: 9, stroke: T.inkMuted }));

  els.push(rule(680, 904, 298));
  els.push(text(680, 306, 'NOT A STREAMING BENEFIT', { size: 9, stroke: T.inkSubtle }));
  els.push(text(680, 322, fit('interleaved thinking is a property', 9.5, 224, 'non-benefit'), { size: 9.5, stroke: T.ink }));
  els.push(text(680, 335, fit('of the model and the API: it works', 9.5, 224, 'non-benefit'), { size: 9.5, stroke: T.ink }));
  els.push(text(680, 348, fit('on a non-streaming call too', 9.5, 224, 'non-benefit'), { size: 9.5, stroke: T.ink }));

  // --- tier 2: what each schedule costs the harness -------------------------
  const COMPARE = [
    ['BATCH', T.primary, 'the tool starts after the last', 'token of the response arrives',
      'the harness holds nothing extra', 'the default, and the code companion'],
    ['STREAMING', T.success, 'the tool starts once its', 'arguments parse as valid JSON',
      'the harness holds a growing buffer,', 'and must handle a half-received call'],
    ['THE SAME IN BOTH', T.warn, 'reason, act, observe, and the', 'four stop conditions',
      'streaming changes the schedule', 'of one turn, not the logic of the loop'],
  ];
  COMPARE.forEach((c, i) => {
    const px = 40 + i * 298, py = 396;
    els.push(...card(px, py, 284, 104, { spine: c[1], strokeWidth: 1.3 }));
    els.push(text(px + 16, py + 12, fit(c[0], 12, 250, 'compare head'), { size: 12, stroke: c[1] }));
    els.push(rule(px + 16, px + 268, py + 32));
    els.push(text(px + 16, py + 40, fit(c[2], 9.5, 250, 'compare line'), { size: 9.5, stroke: T.ink }));
    els.push(text(px + 16, py + 53, fit(c[3], 9.5, 250, 'compare line'), { size: 9.5, stroke: T.ink }));
    els.push(text(px + 16, py + 72, fit(c[4], 9.5, 250, 'compare line'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(px + 16, py + 85, fit(c[5], 9.5, 250, 'compare line'), { size: 9.5, stroke: T.inkMuted }));
  });

  els.push(text(40, 514,
    'Streaming buys the tail of a response you no longer wait through, and the ability to interrupt a turn part-way.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 532,
    'So start batch, and reach for streaming when latency or interruptibility, rather than correctness, is the bottleneck.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Two turn timelines on one scale, the fine print of streaming, and what each schedule costs',
    desc: 'A hand-drawn figure comparing one agent turn run two ways on the same time axis. In the '
      + 'upper row, batch: a model lane shows a long bar for generating the response, and only '
      + 'after it ends does a harness lane bar begin running the tool, followed by the next call, '
      + 'because the tool cannot start until the last token has arrived. In the lower row, '
      + 'streaming: the model lane bar is exactly as long, but a dashed marker part-way through it '
      + 'shows where the tool call becomes fully formed, and the harness lane starts running the '
      + 'tool from that marker, overlapping the rest of the generation, so the next call begins '
      + 'earlier. A bracket between the two next-call positions is labelled latency saved. A panel '
      + 'on the right gives the fine print: arguments arrive as partial-JSON deltas, carried by '
      + 'input_json_delta events with a partial_json fragment, which the harness concatenates until '
      + 'the string parses, and a per-tool eager_input_streaming flag starts those fragments '
      + 'sooner. Genuinely streaming benefits are that output appears immediately and that a run '
      + 'can be interrupted mid-turn, the primitive behind post 15. Interleaved thinking is not a '
      + 'streaming benefit: it is a property of the model and the API and works on a non-streaming '
      + 'call too. A closing row of three cards contrasts the schedules: under batch the tool '
      + 'starts after the last token and the harness holds nothing extra, which is the default and '
      + 'what the code companion does; under streaming the tool starts once its arguments parse and '
      + 'the harness holds a growing buffer and must handle a half-received call; and in both, '
      + 'reason, act, observe and the four stop '
      + 'conditions are the same, so streaming changes the schedule of one turn rather than the '
      + 'logic of the loop. Captions record that streaming buys the tail of a response you no '
      + 'longer wait through plus the ability to interrupt a turn part-way, so the advice is to '
      + 'start batch and reach for streaming when latency or interruptibility, rather than '
      + 'correctness, is the bottleneck.',
  };
}

module.exports = { agentLoop, statelessModel, batchVsStreaming };

if (require.main === module) {
  emit('01-agent-loop', agentLoop());
  emit('02-stateless-model', statelessModel());
  emit('03-batch-vs-streaming', batchVsStreaming());
}
