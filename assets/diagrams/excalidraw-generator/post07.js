// The post 07 diagrams, hand-drawn.
//
//   01-progressive-disclosure  960 x 632  Mirror of the existing figure.
//   02-mcp-dispatch            960 x 600  Mirror.
//   03-three-distances         960 x 470  NEW, published: section 6 had no figure.
//
// Section 6 is the section that settles which of the three mechanisms to reach
// for, and it also carries the correction section 4 makes: MCP moves the tool's
// *code* out of your process, not its *schema* out of your window. Putting the
// two "keeps out of" rows side by side is the only way to see that at a glance.
//
// Figures 1 and 2 each carry a second tier under the mechanism they draw, because
// the mechanism on its own left the lower half of the canvas empty. Figure 1 gains
// the four-step disclosure ladder of section 1, which the post itself says the
// binary loaded-or-dormant strip simplifies. Figure 2 gains the catalogue that
// crosses at connect time and the three runtime concerns of section 9 that the
// protocol does not handle for you. Every number in both is the post's own.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, wrap, card, rule } = require('./scaffold');

const MONO = 3;

// ---------------------------------------------------------------- diagram 1
function progressiveDisclosure() {
  resetSeq();
  const W = 960, H = 632;

  const els = [...heading('Progressive disclosure: load a skill only when the task needs it',
    'The catalogue can be huge; the window stays small. Skills load on demand rather than at startup.')];

  els.push(...card(40, 88, 880, 70, { spine: T.inkSubtle, strokeWidth: 1.2 }));
  els.push(text(58, 94, fit('SKILL CATALOGUE ON DISK: BODIES DORMANT, ONE LINE EACH RESIDENT (LEVEL 1 BELOW)',
    10, 844, 'catalogue label'), { size: 10, stroke: T.inkSubtle }));
  ['pdf', 'sql', 'browser', 'email', 'git', 'image', 'calendar', 'translate'].forEach((s, i) => {
    const x = 58 + i * 106;
    els.push(rect(x, 116, 94, 26, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
    els.push(text(x, 123, s, { size: 10.5, align: 'center', width: 94, stroke: T.inkMuted }));
  });

  // Each turn card names the word the registry of section 5 matched on, because
  // whole-word trigger matching is what that section spends its warning on. The
  // task strings are the post's own, and the matched word is just the one that
  // survives the registry's word split over the lowercased task.
  const TURNS = [
    [40, 'TURN 1', '"read this PDF"', 'trigger word matched: pdf', 'pdf',
      'bash - read - write - pdf'],
    [340, 'TURN 2', '"query the database"', 'trigger word matched: database', 'sql',
      'bash - read - write - sql'],
    [640, 'TURN 3', '"open the page"', 'trigger word matched: page', 'browser',
      'bash - read - write - browser'],
  ];
  TURNS.forEach((t) => {
    const x = t[0];
    els.push(...card(x, 178, 280, 214, { spine: T.accent, strokeWidth: 1.3 }));
    els.push(text(x + 18, 186, t[1], { size: 10, stroke: T.inkSubtle }));
    els.push(text(x + 18, 202, fit(t[2], 12.5, 244, 'task'), { size: 12.5, stroke: T.ink }));
    els.push(text(x + 18, 224, fit(t[3], 9.5, 244, 'trigger'), { size: 9.5, stroke: T.inkMuted }));
    els.push(rule(x + 18, x + 262, 246));
    els.push(text(x + 18, 254, 'LOADS ON DEMAND', { size: 8.5, stroke: T.inkSubtle }));
    els.push(rect(x + 18, 268, 96, 26, { stroke: T.accent, fill: T.accent, strokeWidth: 1.2 }));
    els.push(text(x + 18, 275, t[4], { size: 10.5, align: 'center', width: 96, stroke: T.onAccent }));
    els.push(rule(x + 18, x + 262, 306));
    els.push(text(x + 18, 314, 'IN THE WINDOW THIS TURN', { size: 8.5, stroke: T.inkSubtle }));
    els.push(text(x + 18, 328, fit(t[5], 10.5, 244, 'in window'), { size: 10.5, stroke: T.ink }));
    els.push(text(x + 18, 352, 'STILL DORMANT ON DISK', { size: 8.5, stroke: T.inkSubtle }));
    els.push(text(x + 18, 366, fit('7 of 8 skills; no schema loads', 10, 244, 'dormant'),
      { size: 10, stroke: T.inkMuted }));
  });

  // The four-step gradient of section 1. The post says in as many words that the
  // loaded-or-dormant strip above simplifies this, so the figure had better draw
  // both rather than leave the correction to the prose.
  const LADDER = [
    [40, T.primary, 'LEVEL 1 - ALWAYS RESIDENT', 'Names and descriptions',
      'Every installed skill name and description, about a line each: a hundred '
      + 'skills cost less than one verbose tool schema.', 'always paid, and tiny'],
    [265, T.accent, 'LEVEL 2 - ON RELEVANCE', 'The full SKILL.md',
      'When the model judges the skill relevant to the task, the whole SKILL.md '
      + 'is read into context.', 'paid on the turn that needs it'],
    [490, T.warn, 'LEVEL 3 - ON REFERENCE', 'Bundled files',
      'A REFERENCE.md, a schema or a lookup table, named from SKILL.md and read '
      + 'only if the work reaches it.', 'paid only if the work gets there'],
    [715, T.success, 'OUTSIDE THE LADDER', 'Executable scripts',
      'The agent runs scripts/fill.py; neither the script nor the PDF ever '
      + 'enters the window.', 'never paid: run, not read'],
  ];
  LADDER.forEach((l) => {
    const [x, tint] = l;
    els.push(...card(x, 412, 205, 128, { spine: tint, strokeWidth: 1.3 }));
    els.push(text(x + 16, 420, fit(l[2], 9, 173, 'ladder eyebrow'), { size: 9, stroke: tint }));
    els.push(text(x + 16, 436, fit(l[3], 12.5, 173, 'ladder name'), { size: 12.5, stroke: T.ink }));
    els.push(rule(x + 16, x + 189, 458));
    els.push(text(x + 16, 466, wrap(l[4], 9.5, 173, 4), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(x + 16, 518, fit(l[5], 9, 173, 'ladder tag'), { size: 9, stroke: tint }));
  });

  els.push(text(40, 562, fit('Eager loading keeps all eight skill schemas in the window every turn; each schema runs 300 to 600 tokens.',
    11.5, 880, 'close 1'), { size: 11.5, stroke: T.ink }));
  els.push(text(40, 584, fit('Progressive disclosure keeps about one, so the window stays small and the model has less to choose among.',
    11.5, 880, 'close 2'), { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 606, fit('The thresholds say when to build it: start deferring at 10 or more tools, or past about 10k tokens of definitions.',
    11.5, 880, 'close 3'), { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A dormant skill catalogue, one skill loaded per turn, and the four-step disclosure ladder',
    desc: 'A hand-drawn figure in three tiers. Across the top, a skill catalogue on disk: eight '
      + 'chips reading pdf, sql, browser, email, git, image, calendar and translate, their bodies '
      + 'dormant and only one line each resident. Below it, three turns. Turn one, the task is read '
      + 'this PDF, the trigger word matched is pdf, so the pdf skill loads on demand, the window '
      + 'this turn holds bash, read, write and pdf, and 7 of the 8 skills stay dormant with no '
      + 'schema loaded. Turn two, the task is query the database, the trigger word matched is '
      + 'database, the sql skill loads, and the window holds bash, read, write and sql. Turn three, '
      + 'the task is open the page, the trigger word matched is page, the browser skill loads, and '
      + 'the window holds bash, read, write and browser. The third tier is the four-step disclosure '
      + 'ladder. Level one, always resident: every installed skill name and description, about a '
      + 'line each, so a hundred skills cost less than one verbose tool schema, always paid and '
      + 'tiny. Level two, on relevance: when the model judges the skill relevant to the task the '
      + 'whole SKILL.md is read into context, paid on the turn that needs it. Level three, on '
      + 'reference: a REFERENCE.md, a schema or a lookup table, named from SKILL.md and read only '
      + 'if the work reaches it. Outside the ladder, executable scripts: the agent runs '
      + 'scripts/fill.py and neither the script nor the PDF ever enters the window, so that step is '
      + 'never paid for at all. Closing lines record that eager loading keeps all eight skill '
      + 'schemas in the window every turn and each schema runs 300 to 600 tokens, that progressive '
      + 'disclosure keeps about one, and that the published thresholds say to start deferring at 10 '
      + 'or more tools or past about 10k tokens of definitions.',
  };
}

// ---------------------------------------------------------------- diagram 2
function mcpDispatch() {
  resetSeq();
  const W = 960, H = 600;

  const els = [...heading('MCP dispatch inside one loop turn',
    'The harness is the host; a client speaks MCP to a server that owns the tool. One turn, six steps.')];

  const badge = (x, y, n) => [
    rect(x, y, 22, 17, { stroke: T.ink, fill: T.ink, strokeWidth: 1 }),
    text(x, y + 2, n, { size: 10, align: 'center', width: 22, stroke: T.onFill }),
  ];

  // --- host ------------------------------------------------------------------
  els.push(...card(40, 92, 420, 288, { spine: T.primary, strokeWidth: 1.4 }));
  els.push(text(58, 100, 'HOST: THE HARNESS', { size: 10, stroke: T.primary }));

  els.push(rect(56, 120, 386, 58, { stroke: T.ink, fill: T.surface, strokeWidth: 1.4 }));
  els.push(text(56, 128, 'MODEL', { size: 13, align: 'center', width: 386, stroke: T.ink }));
  els.push(text(56, 152, 'runs the loop and decides when to call a tool',
    { size: 9.5, align: 'center', width: 386, stroke: T.inkMuted }));
  els.push(...badge(66, 128, '1'));

  els.push(rect(56, 218, 386, 62, { stroke: T.ink, fill: T.surface, strokeWidth: 1.4 }));
  els.push(text(56, 226, 'MCP CLIENT', { size: 13, align: 'center', width: 386, stroke: T.ink }));
  els.push(text(56, 250, 'one per server; JSON-RPC over stdio or HTTP',
    { size: 9.5, align: 'center', width: 386, stroke: T.inkMuted }));

  els.push(arrow([[370, 182], [370, 214]], { stroke: T.ink, strokeWidth: 1.4 }));
  els.push(...badge(376, 188, '2'));
  els.push(arrow([[130, 214], [130, 182]], { stroke: T.success, strokeWidth: 1.4 }));
  els.push(...badge(96, 188, '6'));

  // The catalogue crossing at connect time is what the reviewer of the old
  // figure could not see: the schemas are already in the window before step 1,
  // which is exactly the clarification section 8 spends a paragraph on.
  els.push(rect(56, 296, 386, 72, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
  els.push(text(70, 302, 'AT CONNECT, BEFORE STEP 1: tools/list ONCE, THEN CACHED',
    { size: 9, stroke: T.inkSubtle }));
  els.push(text(70, 318, fit('Every returned schema is advertised to the model,', 9.5, 358, 'cat 1'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(70, 332, fit('exactly like a local tool. Five typical servers:', 9.5, 358, 'cat 2'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(70, 346, fit('about 55,000 tokens of definitions before any work.', 9.5, 358, 'cat 3'),
    { size: 9.5, stroke: T.primary }));

  // --- server ----------------------------------------------------------------
  els.push(...card(540, 92, 380, 288, { spine: T.success, strokeWidth: 1.4 }));
  els.push(text(558, 100, 'MCP SERVER: A SEPARATE PROCESS', { size: 10, stroke: T.success }));
  els.push(text(558, 118, 'owns and runs the tool', { size: 11, stroke: T.ink }));
  [['search_docs', 558], ['create_ticket', 736]].forEach((t) => {
    els.push(rect(t[1], 142, 166, 28, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.2 }));
    els.push(text(t[1], 150, t[0], { size: 10.5, align: 'center', width: 166, stroke: T.ink }));
  });
  els.push(...badge(558, 182, '4'));
  els.push(text(588, 181, fit('the tool runs here, in the server process', 9.5, 314, 'server 4'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(558, 204, fit('its code and dependencies never enter yours', 9.5, 344, 'server dep'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(rule(558, 902, 226));

  els.push(text(558, 234, 'WHAT CROSSES BACK, AT STEP 5', { size: 8.5, stroke: T.inkSubtle }));
  els.push(rect(558, 250, 344, 52, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
  els.push(text(572, 258, '{"content": [{"type": "text",', { size: 9.5, family: MONO, stroke: T.ink }));
  els.push(text(572, 274, '   "text": "TICKET-4417 created"}]}', { size: 9.5, family: MONO, stroke: T.ink }));

  els.push(text(558, 312, 'SO THE BOUNDARY BUYS', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(558, 326, fit('the same server works with any host: swap the model', 9.5, 344, 'buys 1'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(558, 340, fit('or the harness and the ticket server is unchanged.', 9.5, 344, 'buys 2'),
    { size: 9.5, stroke: T.inkMuted }));

  // --- the transport ---------------------------------------------------------
  els.push(text(460, 196, 'stdio or HTTP', { size: 9, align: 'center', width: 80, stroke: T.inkSubtle }));
  els.push(...badge(489, 216, '3'));
  els.push(arrow([[462, 240], [536, 240]], { stroke: T.ink, strokeWidth: 1.4 }));
  els.push(arrow([[536, 266], [462, 266]], { stroke: T.success, strokeWidth: 1.4 }));
  els.push(...badge(489, 274, '5'));

  const LEGEND = [
    [40, 398, '1  the model emits a tool call'],
    [40, 416, '2  the host routes it to the client for that server'],
    [40, 434, '3  the client sends tools/call over the transport'],
    [500, 398, '4  the server runs the tool, out of your process'],
    [500, 416, '5  the result returns over the same transport'],
    [500, 434, '6  and becomes the model next observation'],
  ];
  LEGEND.forEach((l) => els.push(text(l[0], l[1], fit(l[2], 9.5, 420, 'legend'),
    { size: 9.5, stroke: T.inkMuted })));

  // The three things the protocol hands back to you. Section 9 names all three,
  // and the third carries the only date in the post.
  const OWNS = [
    [40, T.primary, 'VALIDATION', 'Check the result',
      'The result arrives over the wire as data. A misbehaving server is untrusted '
      + 'input: validate the shape before the model sees it.'],
    [340, T.warn, 'FAILURE', 'An observation, not a crash',
      'A timeout or a disconnect surfaces as "error: ticketing server unavailable", '
      + 'never an exception that kills the loop.'],
    [640, T.alert, 'INJECTION SURFACE', 'The schema arrives first',
      'Tool descriptions are attacker-controlled text that lands before any call. '
      + 'In May 2025 a public-repo issue leaked private ones.'],
  ];
  OWNS.forEach((o) => {
    const [x, tint] = o;
    els.push(...card(x, 458, 280, 100, { spine: tint, strokeWidth: 1.3 }));
    els.push(text(x + 16, 466, fit(o[2], 9, 248, 'owns eyebrow'), { size: 9, stroke: tint }));
    els.push(text(x + 16, 482, fit(o[3], 12.5, 248, 'owns name'), { size: 12.5, stroke: T.ink }));
    els.push(rule(x + 16, x + 264, 502));
    els.push(text(x + 16, 510, wrap(o[4], 9.5, 248, 3), { size: 9.5, stroke: T.inkMuted }));
  });

  els.push(text(40, 572, fit('One turn, six steps, two processes: the catalogue crosses at connect time, and only the result crosses at step 5.',
    11.5, 880, 'close'), { size: 11.5, stroke: T.ink }));

  return {
    W, H, els,
    title: 'An MCP tool call routed from host to client to server and back, with what the harness still owns',
    desc: 'A hand-drawn figure of one loop turn. On the left, the host, which is the harness: a '
      + 'MODEL box that runs the loop and decides when to call a tool, an MCP CLIENT box below it, '
      + 'one per server, speaking JSON-RPC over stdio or HTTP, and under both a panel recording '
      + 'what crosses at connect time, before step one: the host calls tools/list once and caches '
      + 'it, every returned schema is advertised to the model exactly like a local tool, and five '
      + 'typical servers come to about 55,000 tokens of definitions before any work is done. On the '
      + 'right, an MCP server running as a separate process, which owns and runs the tool, shown '
      + 'with two tools named search_docs and create_ticket, a note that the tool runs there and '
      + 'that its code and dependencies never enter yours, the JSON result that crosses back at '
      + 'step five, reading content, type text, text TICKET-4417 created, and a note that what the '
      + 'boundary buys is that the same server works with any host, so the model or the harness can '
      + 'be swapped and the ticket server is unchanged. Six numbered steps trace the call: one, the '
      + 'model emits a tool call; two, the host routes it to the client for that server; three, the '
      + 'client sends tools/call over the transport; four, the server runs the tool out of your '
      + 'process; five, the result returns over the same transport; and six, it becomes the model '
      + 'next observation. A bottom row gives the three runtime concerns the harness owns rather '
      + 'than the protocol. Validation: the result arrives over the wire as data, so a misbehaving '
      + 'server is untrusted input and its shape is validated before the model sees it. Failure: a '
      + 'timeout or a disconnect surfaces as an error saying the ticketing server is unavailable, '
      + 'never an exception that kills the loop. Injection surface: tool descriptions are '
      + 'attacker-controlled text that lands before any call, and in May 2025 a malicious '
      + 'public-repository issue leaked private repositories. A closing line records that the '
      + 'catalogue crosses at connect time and only the result crosses at step five.',
  };
}

// ---------------------------------------------------------------- diagram 3
function threeDistances() {
  resetSeq();
  const W = 960, H = 470;

  const els = [...heading('Three distances from your loop',
    'A general tool, a skill, and an MCP server are the same instinct at three distances: capability on demand.')];

  els.push(rect(40, 184, 130, 90, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.6 }));
  els.push(text(40, 206, 'YOUR LOOP', { size: 12, align: 'center', width: 130, stroke: T.ink }));
  els.push(text(40, 230, 'the harness', { size: 9.5, align: 'center', width: 130, stroke: T.inkMuted }));
  els.push(arrow([[172, 229], [182, 229]], { stroke: T.inkSubtle, strokeWidth: 1.2 }));

  els.push(text(186, 82, 'FURTHER FROM YOUR LOOP', { size: 9, stroke: T.inkSubtle }));

  const ZONES = [
    [186, 238, T.primary, 'IN THE WINDOW, ALWAYS', 'A general tool',
      'Always advertised. One string in,', 'one result out; compose the rest.',
      'the capability is better composed', 'than packaged',
      'nothing: the schema is always there', 'nothing: it runs in your process', 'bash, python'],
    [434, 238, T.accent, 'ON DISK, LOADED ON DEMAND', 'A skill',
      'A folder of tools, guidance and', 'triggers. Dormant until needed.',
      'the capability is cohesive, reusable', 'and only occasionally needed',
      'its schemas, until a turn loads it', 'nothing: it still runs in yours', 'PDF handling'],
    [682, 238, T.success, 'IN ANOTHER PROCESS', 'An MCP server',
      'A separate process behind a standard', 'protocol, usually owned elsewhere.',
      'the capability belongs to a system', 'you do not own or run in-process',
      'nothing by itself: see below', 'its code and all of its dependencies', 'the ticketing system'],
  ];

  ZONES.forEach((z) => {
    const [x, w, tint] = z;
    els.push(...card(x, 104, w, 250, { spine: tint, strokeWidth: 1.4 }));
    const ix = x + 18, iw = w - 34;
    els.push(text(ix, 114, fit(z[3], 9, iw, 'zone head'), { size: 9, stroke: tint }));
    els.push(text(ix, 132, fit(z[4], 15, iw, 'zone name'), { size: 15, stroke: T.ink }));
    els.push(text(ix, 158, fit(z[5], 9.5, iw, 'zone gloss'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(ix, 172, fit(z[6], 9.5, iw, 'zone gloss'), { size: 9.5, stroke: T.inkMuted }));
    els.push(rule(ix, x + w - 16, 192));
    els.push(text(ix, 200, 'REACH FOR IT WHEN', { size: 8.5, stroke: T.inkSubtle }));
    els.push(text(ix, 216, fit(z[7], 9.5, iw, 'zone when'), { size: 9.5, stroke: T.ink }));
    els.push(text(ix, 230, fit(z[8], 9.5, iw, 'zone when'), { size: 9.5, stroke: T.ink }));
    els.push(rule(ix, x + w - 16, 252));
    els.push(text(ix, 260, 'KEEPS OUT OF YOUR WINDOW', { size: 8.5, stroke: T.inkSubtle }));
    els.push(text(ix, 274, fit(z[9], 9.5, iw, 'zone window'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(ix, 294, 'KEEPS OUT OF YOUR PROCESS', { size: 8.5, stroke: T.inkSubtle }));
    els.push(text(ix, 308, fit(z[10], 9.5, iw, 'zone process'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(ix, 328, 'EXAMPLE', { size: 8.5, stroke: T.inkSubtle }));
    els.push(text(ix, 340, fit(z[11], 10, iw, 'zone example'), { size: 10, stroke: tint }));
  });

  els.push(text(40, 376,
    'The window row is the one that surprises people: connecting an MCP server does not shrink your context by itself.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 398, 'The host calls tools/list at connect time and advertises those schemas to the model like any local tool.',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 420, 'Keeping them out of the window is still progressive disclosure, applied to the MCP catalogue.',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 444, 'What the process boundary buys is that the implementation and its dependencies stay out of your process.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'General tool, skill, and MCP server as three distances from the loop',
    desc: 'A hand-drawn comparison of three ways to give an agent a capability, arranged by '
      + 'distance from the loop. Nearest, a general tool: always advertised, one string in and one '
      + 'result out, reached for when the capability is better composed than packaged; it keeps '
      + 'nothing out of your window because its schema is always there, and nothing out of your '
      + 'process; the example is bash or python. Next, a skill: a folder of tools, guidance and '
      + 'triggers that lies dormant until a turn needs it, reached for when the capability is '
      + 'cohesive, reusable and only occasionally needed; it keeps its schemas out of the window '
      + 'until a turn loads it, but nothing out of your process, since it still runs there; the '
      + 'example is PDF handling. Furthest, an MCP server: a separate process behind a standard '
      + 'protocol, often owned by someone else, reached for when the capability belongs to a system '
      + 'you do not own or want to run in-process; it keeps nothing out of the window by itself, '
      + 'but keeps its code and all of its dependencies out of your process; the example is the '
      + 'company ticketing system. Captions record the correction this makes: connecting an MCP '
      + 'server does not shrink your context, because the host calls tools/list at connect time and '
      + 'advertises those schemas like any local tool, so keeping them out is still progressive '
      + 'disclosure applied to the MCP catalogue, while what the process boundary buys is that the '
      + 'implementation and its dependencies stay out of your process.',
  };
}

module.exports = { progressiveDisclosure, mcpDispatch, threeDistances };

if (require.main === module) {
  emit('01-progressive-disclosure', progressiveDisclosure());
  emit('02-mcp-dispatch', mcpDispatch());
  emit('03-three-distances', threeDistances());
}
