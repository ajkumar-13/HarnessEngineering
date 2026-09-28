// The post 06 diagrams, hand-drawn.
//
//   01-tool-dispatch        960 x 634  Mirror of the existing figure, filled out.
//   02-universal-vs-zoo     960 x 472  Mirror.
//   03-schema-that-teaches  960 x 470  NEW, published: section 3 had no figure.
//
// Section 3 is the section a reader will actually copy from, and it was four
// bullets of advice with nothing to copy. Two versions of the same tool, side by
// side with the four rules numbered onto the lines they change, is the form that
// advice wants to be in.
//
// Diagram 1 carried the flow alone, which left a wide empty band on the right
// and no answer to the obvious question: what does a *caught* call look like?
// It now carries two tiers. The flow, with the exchange from section 2 on the
// wire beside it, and section 7's three kinds of wrongness underneath, each with
// the call that triggers it and the exact string the loop reads back.

const { T, rect, ellipse, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

const MONO = 3;

// ---------------------------------------------------------------- diagram 1
function dispatch() {
  resetSeq();
  const W = 960, H = 634;

  const els = [...heading('Tool dispatch: validate, then execute',
    'The schema is the contract. Check the tool call against it before you run anything.')];

  // -- tier 1: the flow, the schema above it, and the wire beside it ---------
  els.push(...card(230, 76, 250, 70, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(248, 84, fit('SCHEMA: THE CONTRACT (bash_tool.py)', 9, 214, 'schema label'),
    { size: 9, stroke: T.inkSubtle }));
  ['properties: { command: string }', 'required: [command]', 'additionalProperties: false']
    .forEach((l, i) => els.push(text(248, 100 + i * 15, fit(l, 9.5, 214, 'schema line'),
      { size: 9.5, family: MONO, stroke: T.ink })));
  els.push(arrow([[355, 148], [355, 170]], { stroke: T.primary, strokeWidth: 1.3 }));

  const box = (x, y, w, h, name, gloss, o = {}) => [
    rect(x, y, w, h, { stroke: o.stroke ?? T.ink, fill: o.fill ?? T.surface, strokeWidth: o.strokeWidth ?? 1.5 }),
    text(x, y + 14, name, { size: 13, align: 'center', width: w, stroke: o.stroke ?? T.ink }),
    text(x, y + 38, fit(gloss, 9.5, w - 16, 'box gloss'),
      { size: 9.5, align: 'center', width: w, stroke: T.inkMuted }),
  ];

  els.push(...box(40, 174, 140, 64, 'MODEL', 'emits a tool call'));
  els.push(...box(270, 174, 170, 64, 'VALIDATE', 'input against schema'));
  els.push(...box(524, 146, 160, 56, 'EXECUTE', 'run it, get a result', { stroke: T.success }));
  els.push(...box(524, 238, 160, 56, 'ERROR', 'not run; handed back', { stroke: T.alert }));

  els.push(arrow([[184, 214], [266, 214]], { stroke: T.ink, strokeWidth: 1.4 }));
  els.push(text(194, 180, 'tool_use', { size: 9, stroke: T.inkMuted }));
  els.push(text(194, 194, '{name, input}', { size: 9, stroke: T.inkMuted }));

  els.push(arrow([[442, 196], [520, 178]], { stroke: T.success, strokeWidth: 1.4 }));
  els.push(text(452, 158, 'valid', { size: 9.5, stroke: T.success }));
  els.push(arrow([[442, 220], [520, 258]], { stroke: T.alert, strokeWidth: 1.4 }));
  els.push(text(446, 252, 'invalid', { size: 9.5, stroke: T.alert }));

  els.push(line([[684, 168], [698, 168]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(line([[684, 274], [698, 274]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[698, 168], [698, 308], [110, 308], [110, 242]],
    { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(text(150, 314, 'either way, the result returns to the model as the next observation',
    { size: 9.5, stroke: T.inkMuted }));

  // The wire format, quoted from the post, in the band the flow left empty.
  els.push(...card(720, 76, 200, 240, { spine: T.accent, strokeWidth: 1.3 }));
  els.push(text(736, 84, fit('ONE EXCHANGE, FROM SECTION 2', 9, 168, 'wire label'),
    { size: 9, stroke: T.inkSubtle }));
  els.push(text(736, 100, 'the assistant turn', { size: 9.5, stroke: T.primary }));
  ['{"type": "tool_use",',
    ' "id": "toolu_01A",',
    ' "name": "bash",',
    ' "input": {"command":',
    '   "pytest -q tests/',
    '    test_parser.py"}}',
  ].forEach((l, i) => els.push(text(736, 116 + i * 12, fit(l, 8.5, 168, 'wire up'),
    { size: 8.5, family: MONO, stroke: T.ink })));
  els.push(rule(736, 904, 192));
  els.push(text(736, 200, 'the harness reply, next turn', { size: 9.5, stroke: T.success }));
  ['{"type": "tool_result",',
    ' "tool_use_id": "toolu_01A",',
    ' "is_error": false,',
    ' "content": "2 failed,',
    '   11 passed in 0.44s"}',
  ].forEach((l, i) => els.push(text(736, 216 + i * 12, fit(l, 8.5, 168, 'wire down'),
    { size: 8.5, family: MONO, stroke: T.ink })));
  els.push(rule(736, 904, 280));
  els.push(text(736, 286, fit('the id is the only link between', 9, 168, 'wire note'),
    { size: 9, stroke: T.inkMuted }));
  els.push(text(736, 298, 'a request and its answer', { size: 9, stroke: T.inkMuted }));

  // -- tier 2: the three kinds of wrongness, one card each ------------------
  els.push(text(40, 342, 'THREE KINDS OF WRONGNESS, THREE DIFFERENT GATES',
    { size: 10, stroke: T.inkSubtle }));
  els.push(text(390, 342,
    fit('only the first is validation; each comes back as a string', 9.5, 330, 'gate note'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(0, 342, 'code/06-tools-and-bash, 15 tests',
    { size: 9, align: 'right', width: 920, stroke: T.inkSubtle }));

  const GATES = [
    ['1', 'Schema-invalid', 'section 7', '{"cmd": "ls"}',
      'the harness validator', 'before anything is executed',
      'schema.py, a 66-line JSON-Schema subset',
      ['error: invalid input: $: missing required',
        "property 'command'; $: unexpected property 'cmd'"],
      'the model patches the call and retries', T.primary],
    ['2', 'Schema-valid, wrong', 'section 8', '{"command": "cat /tmp/nope"}',
      'the tool itself, at run time', 'the exit status is surfaced, not swallowed',
      'all 4 dispatch branches return a string',
      ['(exit 1) cat: /tmp/nope:',
        'No such file or directory'],
      'the model reads the code and fixes the path', T.warn],
    ['3', 'Schema-valid, dangerous', 'section 5', '{"command": "rm -rf /"}',
      'a deny-list, then a sandbox', 'refused before the runner sees it',
      '12 patterns; 4 other spellings pass',
      ['blocked: command matches a deny-list',
        'rule (\\brm\\s+-[rf])'],
      'the sandbox is what actually holds (Post 14)', T.alert],
  ];

  GATES.forEach((g, i) => {
    const x = 40 + i * 296, y = 356, tint = g[9];
    els.push(...card(x, y, 288, 222, { spine: tint, strokeWidth: 1.3 }));
    els.push(rect(x + 16, y + 14, 24, 18, { stroke: tint, fill: tint, strokeWidth: 1 }));
    els.push(text(x + 16, y + 16, g[0], { size: 11, align: 'center', width: 24, stroke: T.onAccent }));
    els.push(text(x + 48, y + 12, fit(g[1], 13, 210, 'gate name'), { size: 13, stroke: T.ink }));

    els.push(rule(x + 16, x + 272, y + 40));
    els.push(text(x + 16, y + 48, 'THE CALL', { size: 9, stroke: T.inkSubtle }));
    els.push(text(x + 16, y + 48, g[2], { size: 9, align: 'right', width: 256, stroke: T.inkSubtle }));
    els.push(text(x + 16, y + 62, fit(g[3], 9.5, 256, 'gate call'),
      { size: 9.5, family: MONO, stroke: T.ink }));

    els.push(rule(x + 16, x + 272, y + 84));
    els.push(text(x + 16, y + 92, 'CAUGHT BY', { size: 9, stroke: T.inkSubtle }));
    els.push(text(x + 16, y + 104, fit(g[4], 11.5, 256, 'gate catcher'), { size: 11.5, stroke: tint }));
    els.push(text(x + 16, y + 122, fit(g[5], 9.5, 256, 'gate when'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(x + 16, y + 140, fit(g[6], 9, 256, 'gate note'), { size: 9, stroke: T.inkSubtle }));

    els.push(rule(x + 16, x + 272, y + 154));
    els.push(text(x + 16, y + 161, 'WHAT THE LOOP SEES', { size: 9, stroke: T.inkSubtle }));
    g[7].forEach((l, k) => els.push(text(x + 16, y + 175 + k * 13, fit(l, 8.5, 256, 'gate error'),
      { size: 8.5, family: MONO, stroke: T.ink })));
    els.push(text(x + 16, y + 203, fit(g[8], 9.5, 256, 'gate takeaway'),
      { size: 9.5, stroke: T.inkMuted }));
  });

  els.push(text(40, 592,
    'A tool is a contract written in tokens. Validate the call, and a bad call becomes a correctable error.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 612,
    'Skip the validation and the same call becomes a crash, which the loop cannot see and cannot fix.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Tool dispatch as validate-then-execute, with the three kinds of wrongness each gate catches',
    desc: 'A hand-drawn figure in two tiers. The top tier is the dispatch flow. A schema card holds the '
      + 'bash contract: properties command string, required command, additionalProperties false. It '
      + 'feeds down into a VALIDATE box. On the left a MODEL box emits a tool call, drawn as a '
      + 'tool_use message carrying a name and an input, which arrives at VALIDATE where the input is '
      + 'checked against the schema. A green arrow marked valid leads to an EXECUTE box that runs the '
      + 'tool and gets a result; a red arrow marked invalid leads to an ERROR box where nothing is '
      + 'run and the problem is handed back. Both feed a return path that carries the outcome to the '
      + 'model as the next observation. Beside the flow, a panel shows one exchange on the wire, '
      + 'taken from section 2: an assistant turn of type tool_use with id toolu_01A, name bash and an '
      + 'input command of pytest -q tests/test_parser.py, and the harness reply of type tool_result '
      + 'with the same tool_use_id, is_error false, and content reading 2 failed, 11 passed in 0.44 '
      + 'seconds, under a note that the id is the only link between a request and its answer. The '
      + 'lower tier lays out section 7 three kinds of wrongness as three cards. One, schema-invalid: '
      + 'the call is cmd ls, caught by the harness validator before anything is executed, using '
      + 'schema.py, a 66-line JSON-Schema subset; the loop reads back error: invalid input, missing '
      + 'required property command, unexpected property cmd, and the model patches the call and '
      + 'retries. Two, schema-valid but wrong: the call is command cat /tmp/nope, caught by the tool '
      + 'itself at run time with the exit status surfaced rather than swallowed, and all 4 dispatch '
      + 'branches return a string, so the loop reads back exit 1, cat: /tmp/nope: No such file or '
      + 'directory, and the model reads the code and fixes the path. Three, schema-valid and '
      + 'dangerous: the call is command rm -rf /, refused by a deny-list before the runner sees it, '
      + '12 patterns shipped of which 4 other spellings still pass; the loop reads back blocked: '
      + 'command matches a deny-list rule, and the sandbox of post 14 is what actually holds. '
      + 'Captions record that a tool is a contract written in '
      + 'tokens, that validating the call turns a bad call into a correctable error, and that '
      + 'skipping validation turns the same call into a crash the loop can neither see nor fix.',
  };
}

// ---------------------------------------------------------------- diagram 2
function universalVsZoo() {
  resetSeq();
  const W = 960, H = 472;

  const els = [...heading('A few general tools beat a zoo of narrow ones',
    'Give the model general-purpose tools and let it compose. Every schema is tokens it reads on every call.')];

  els.push(...card(40, 96, 440, 250, { spine: T.alert, strokeWidth: 1.3 }));
  els.push(text(56, 106, 'THE TOOL ZOO: ABOUT 50 NARROW TOOLS', { size: 10, stroke: T.alert }));
  const ZOO = ['read_file', 'write_file', 'list_dir', 'grep', 'sed', 'find', 'cat', 'head',
    'tail', 'mkdir', 'mv', 'cp', 'rm', 'chmod', 'curl', 'jq'];
  ZOO.forEach((t, i) => {
    const x = 56 + (i % 4) * 104;
    const y = 128 + Math.floor(i / 4) * 26;
    els.push(rect(x, y, 92, 20, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
    els.push(text(x, y + 4, t, { size: 8.5, align: 'center', width: 92, stroke: T.ink }));
  });
  els.push(text(56, 236, 'and about 34 more', { size: 9.5, stroke: T.inkSubtle }));
  els.push(rule(56, 464, 256));
  const MINUS = [
    'one huge combined schema, read on every call',
    'overlapping and redundant, so the model must choose',
    'fifty ways to be misused, and fifty to sandbox',
    'the model half-knows each one',
  ];
  MINUS.forEach((s, i) => els.push(text(56, 266 + i * 18,
    fit('- ' + s, 9.5, 408, 'zoo minus'), { size: 9.5, stroke: T.inkMuted })));

  els.push(...card(500, 96, 420, 250, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(516, 106, 'A FEW GENERAL TOOLS', { size: 10, stroke: T.success }));
  ['bash', 'python', 'read_file', 'write_file'].forEach((t, i) => {
    const x = 516 + (i % 2) * 200;
    const y = 128 + Math.floor(i / 2) * 44;
    els.push(rect(x, y, 184, 34, { stroke: T.ink, fill: T.surface, strokeWidth: 1.3 }));
    els.push(text(x, y + 9, t, { size: 12, align: 'center', width: 184, stroke: T.ink }));
  });
  els.push(text(516, 220, 'bash and python compose everything on the left.',
    { size: 9.5, stroke: T.inkSubtle }));
  els.push(rule(516, 904, 256));
  const PLUS = [
    'a tiny schema, cheap on every call',
    'compose anything; nothing to choose between',
    'patterns the model was actually trained on',
    'one surface to sandbox (Post 14)',
  ];
  PLUS.forEach((s, i) => els.push(text(516, 266 + i * 18,
    fit('+ ' + s, 9.5, 388, 'general plus'), { size: 9.5, stroke: T.inkMuted })));

  els.push(text(40, 374,
    'Ten focused tools beat fifty overlapping ones, and one general surface is far easier to secure than fifty narrow ones.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 398, 'The rule is not "one tool": it is the fewest general tools that cover the space.',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 420, 'Reach for a bespoke tool only when a general one genuinely cannot express the action.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Fifty narrow tools beside four general ones, priced by what each costs',
    desc: 'A hand-drawn comparison in two panels. The left panel, the tool zoo, shows sixteen small '
      + 'named chips such as read_file, write_file, list_dir, grep, sed, find and jq, with a note '
      + 'that about thirty-four more follow. Beneath it, four costs: one huge combined schema read '
      + 'on every call; overlapping and redundant tools, so the model must choose; fifty ways to be '
      + 'misused and fifty to sandbox; and a model that only half-knows each one. The right panel '
      + 'shows four general tools, bash, python, read_file and write_file, with the note that bash '
      + 'and python compose everything on the left. Beneath it, four gains: a tiny schema that is '
      + 'cheap on every call; the ability to compose anything with nothing to choose between; '
      + 'patterns the model was actually trained on; and one surface to sandbox. Captions record '
      + 'that ten focused tools beat fifty overlapping ones, that one general surface is far easier '
      + 'to secure, that the rule is the fewest general tools that cover the space rather than one '
      + 'tool, and that a bespoke tool is for when a general one genuinely cannot express the '
      + 'action.',
  };
}

// ---------------------------------------------------------------- diagram 3
function schemaThatTeaches() {
  resetSeq();
  const W = 960, H = 470;

  const els = [...heading('A schema that teaches, not one that only describes',
    'The schema and its description are the whole interface the model has. Aim for easy to use well, hard to use badly.')];

  // Left: the version that only describes.
  els.push(...card(40, 96, 380, 196, { spine: T.alert, strokeWidth: 1.3 }));
  els.push(text(60, 106, 'ONLY DESCRIBES', { size: 10, stroke: T.alert }));
  els.push(text(60, 128, 'name:  pytest_invoke', { size: 10.5, family: MONO, stroke: T.ink }));
  els.push(text(60, 148, 'desc:  "Invokes pytest."', { size: 10.5, family: MONO, stroke: T.ink }));
  els.push(text(60, 168, 'input: { args: string }', { size: 10.5, family: MONO, stroke: T.ink }));
  els.push(rule(60, 404, 196));
  els.push(text(60, 206, 'WHAT GOES WRONG', { size: 9, stroke: T.inkSubtle }));
  [['the model must guess what args means', 222],
   ['nothing says when it should not be called', 238],
   ['a malformed call reaches your code and throws', 254]].forEach((r) => {
    els.push(text(60, r[1], fit(r[0], 9.5, 348, 'wrong'), { size: 9.5, stroke: T.inkMuted }));
  });

  // Right: the version that teaches.
  els.push(...card(440, 96, 480, 196, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(460, 106, 'TEACHES JUDGEMENT', { size: 10, stroke: T.success }));
  const CODE = [
    [128, 'name:  run_tests'],
    [148, 'desc:  "Run the suite and return the'],
    [164, '        failures. Use after any code'],
    [180, '        edit. Do NOT use to read a'],
    [196, '        file: use bash for that."'],
    [216, 'input: { path:  string (required),'],
    [232, '         scope: unit | integration | all }'],
    [248, '       additionalProperties: false'],
    [268, 'returns: "error: ..." as a string, not an exception'],
  ];
  CODE.forEach((c) => els.push(text(460, c[0], c[1], { size: 10, family: MONO, stroke: T.ink })));

  [[122, '1'], [142, '2'], [210, '3'], [262, '4']].forEach((b) => {
    els.push(rect(884, b[0], 22, 17, { stroke: T.success, fill: T.success, strokeWidth: 1 }));
    els.push(text(884, b[0] + 2, b[1], { size: 10, align: 'center', width: 22, stroke: T.onAccent }));
  });

  const RULES = [
    ['1', 'Name for the action, not the implementation',
      'The model reasons about intent, not about your stack, so run_tests beats', 'pytest_invoke.'],
    ['2', 'Write the description for the caller',
      'What it is for, what it returns, and most valuable of all, when not to', 'call it.'],
    ['3', 'Constrain the input',
      'An enum instead of a free string, required fields, no additional properties:', 'documentation the model cannot ignore, and a validator for free.'],
    ['4', 'Return errors as information',
      'A tool output, errors included, is the next observation. "error: file not', 'found" is correctable; an exception that escapes the loop is not.'],
  ];
  RULES.forEach((r, i) => {
    const x = 40 + (i % 2) * 470;
    const y = 314 + Math.floor(i / 2) * 56;
    els.push(rect(x, y, 22, 17, { stroke: T.success, fill: T.success, strokeWidth: 1 }));
    els.push(text(x, y + 2, r[0], { size: 10, align: 'center', width: 22, stroke: T.onAccent }));
    els.push(text(x + 30, y - 1, fit(r[1], 11.5, 400, 'rule title'), { size: 11.5, stroke: T.ink }));
    els.push(text(x, y + 22, fit(r[2], 9.5, 440, 'rule gloss'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(x, y + 36, fit(r[3], 9.5, 440, 'rule gloss'), { size: 9.5, stroke: T.inkMuted }));
  });

  els.push(text(40, 434,
    'Every one of these is also a token decision: the description is read on every call, before the user request even appears.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 452, 'So aim for the shortest description that still teaches when not to call. A checklist, not a manual.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The same tool defined twice: one schema that describes and one that teaches',
    desc: 'A hand-drawn comparison of two definitions of the same tool. On the left, a schema that '
      + 'only describes: it is named pytest_invoke, its description reads Invokes pytest, and its '
      + 'input is a single free-form args string. Three notes record what goes wrong: the model '
      + 'must guess what args means, nothing says when it should not be called, and a malformed '
      + 'call reaches your code and throws. On the right, a schema that teaches judgement: it is '
      + 'named run_tests; its description says to run the suite and return the failures, to use it '
      + 'after any code edit, and explicitly not to use it to read a file since bash is for that; '
      + 'its input requires a path string and a scope drawn from unit, integration or all, with no '
      + 'additional properties allowed; and it returns errors as a string rather than raising. Four '
      + 'numbered badges mark the lines that change, matching four rules listed below: name for the '
      + 'action rather than the implementation; write the description for the caller, including '
      + 'when not to call; constrain the input with enums, required fields and no additional '
      + 'properties, which is both documentation and a free validator; and return errors as '
      + 'information, because a tool output is the next observation. Captions record that each rule '
      + 'is also a token decision, since the description is read on every call, so the aim is the '
      + 'shortest description that still teaches when not to call.',
  };
}

module.exports = { dispatch, universalVsZoo, schemaThatTeaches };

if (require.main === module) {
  emit('01-tool-dispatch', dispatch());
  emit('02-universal-vs-zoo', universalVsZoo());
  emit('03-schema-that-teaches', schemaThatTeaches());
}
