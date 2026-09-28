// The post 08 diagrams, hand-drawn.
//
//   01-filesystem-durable-state  960 x 560  Mirror of the existing figure, plus
//                                           the section 3 price of one offload,
//                                           in the post's own numbers.
//   02-handoff-lifecycle         960 x 588  Mirror, carrying the whole section 6
//                                           handoff file and the rule per field.
//   03-where-state-belongs       960 x 470  NEW, published: sections 5 and 6 had no figure.
//
// Sections 5 and 6 are the ones a reader has to apply, and they are the same
// decision stated twice: state has a right place, decided by *when* it is
// needed. Drawing the two zones with the two mirror-image mistakes underneath
// is the only form in which "put it on disk" stops being unqualified advice.
//
// Every number in figures 1 and 2 is read out of index.md: the offload
// arithmetic is section 3's table verbatim (and its rate is labelled
// illustrative there, so it is labelled illustrative here), and the handoff
// body, the branch, the checkpoint hash and the 5-of-7 test count are section
// 6's example file verbatim.

const { T, rect, ellipse, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

const MONO = 3;

// ---------------------------------------------------------------- diagram 1
function durableState() {
  resetSeq();
  const W = 960, H = 560;

  const els = [...heading('The filesystem is the loop durable memory',
    'The window is small, volatile and expensive. Disk is large, durable and cheap, and git makes it reversible.')];

  // --- the window -----------------------------------------------------------
  els.push(...card(40, 118, 250, 190, { spine: T.primary, strokeWidth: 1.5 }));
  els.push(text(58, 128, 'CONTEXT WINDOW', { size: 14, stroke: T.ink }));
  els.push(text(58, 150, fit('what the model reads this turn', 9, 214, 'window gloss'),
    { size: 9, stroke: T.inkMuted }));
  els.push(rect(58, 168, 92, 44, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.3 }));
  ['200,000 tokens', 'and more on the box;', 'usable is less']
    .forEach((s, i) => els.push(text(160, 170 + i * 14, fit(s, 8.5, 112, 'window box note'),
      { size: 8.5, stroke: T.inkSubtle })));
  ['- small relative to the work', '- priced per token, on every call',
    '- volatile: wiped at every reset', '- and gone on any crash']
    .forEach((b, i) => els.push(text(58, 228 + i * 18, fit(b, 9, 214, 'window bullet'),
      { size: 9, stroke: T.inkMuted })));

  // --- the two arrows across the gap ---------------------------------------
  els.push(arrow([[292, 168], [376, 168]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(text(296, 148, fit('write, offload', 9, 80, 'arrow label'), { size: 9, stroke: T.inkMuted }));
  els.push(arrow([[376, 252], [292, 252]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(text(296, 258, fit('read on demand', 9, 80, 'arrow label'), { size: 9, stroke: T.inkMuted }));

  // --- the durable store ----------------------------------------------------
  els.push(...card(380, 88, 540, 232, { spine: T.success, strokeWidth: 1.5 }));
  els.push(text(400, 96, 'DURABLE STORE, ON DISK', { size: 10, stroke: T.success }));

  els.push(rect(396, 118, 258, 190, { stroke: T.inkMuted, fill: T.surface, strokeWidth: 1.0 }));
  els.push(text(410, 124, 'FILESYSTEM', { size: 9, stroke: T.inkSubtle }));
  [
    ['plan.md', 'rewritten each step, not appended'],
    ['scratch/build.log', '2,000 lines, ~100 KB: a pointer goes back'],
    ['output.json', 'the artefact itself, not transcript text'],
    ['handoff.md', 'spec, done, next, state: survives a reset'],
  ].forEach((f, i) => {
    const ry = 142 + i * 38;
    els.push(rect(408, ry, 234, 32, { stroke: T.border, fill: T.neutral1, strokeWidth: 1.0 }));
    els.push(text(416, ry + 3, fit(f[0], 9.5, 218, 'file name'),
      { size: 9.5, family: MONO, stroke: T.ink }));
    els.push(text(416, ry + 17, fit(f[1], 8.5, 218, 'file gloss'),
      { size: 8.5, stroke: T.inkMuted }));
  });

  els.push(rect(668, 118, 238, 190, { stroke: T.inkMuted, fill: T.surface, strokeWidth: 1.0 }));
  els.push(text(680, 124, 'GIT: VERSIONED STATE', { size: 9, stroke: T.inkSubtle }));
  els.push(text(786, 138, 'revert', { size: 9, align: 'center', width: 80, stroke: T.alert }));
  els.push(arrow([[866, 163], [866, 154], [786, 154], [786, 163]],
    { stroke: T.alert, strokeWidth: 1.3 }));
  [[706, 'c1', 'checkpoint', T.success], [786, 'c2', 'checkpoint', T.success],
    [866, 'c3', 'bad step', T.alert]].forEach((c) => {
    els.push(ellipse(c[0] - 11, 165, 22, 22, { stroke: c[3], fill: T.surface, strokeWidth: 1.3 }));
    els.push(text(c[0] - 11, 170, c[1], { size: 9, align: 'center', width: 22, stroke: T.ink }));
    els.push(text(c[0] - 35, 192, fit(c[2], 8.5, 70, 'commit label'),
      { size: 8.5, align: 'center', width: 70, stroke: T.inkMuted }));
  });
  els.push(line([[717, 176], [775, 176]], { stroke: T.inkMuted, strokeWidth: 1.0 }));
  els.push(line([[797, 176], [855, 176]], { stroke: T.inkMuted, strokeWidth: 1.0 }));
  els.push(rule(680, 894, 210));
  els.push(text(680, 218, 'CHECKPOINT AND ROLLBACK', { size: 8, stroke: T.inkSubtle }));
  ['git add -A -- src/ tests/', 'git reset --hard a41c9f2', 'git clean -fd -- src/ tests/']
    .forEach((c, i) => els.push(text(680, 234 + i * 14, fit(c, 8.5, 214, 'git command'),
      { size: 8.5, family: MONO, stroke: T.ink })));
  els.push(text(680, 280, fit('check the return code:', 8.5, 214, 'git note'),
    { size: 8.5, stroke: T.inkMuted }));
  els.push(text(680, 292, fit('a failed commit still leaves a hash', 8.5, 214, 'git note'),
    { size: 8.5, stroke: T.inkMuted }));

  // --- what one offload is worth, in the post's own arithmetic --------------
  els.push(rule(40, 920, 332));
  els.push(text(40, 344, fit('WHAT ONE OFFLOAD IS WORTH: A 2,000-LINE BUILD LOG, ABOUT 25,000 TOKENS, ARRIVING AT ITERATION 3 OF A 12-ITERATION RUN',
    10, 880, 'band label'), { size: 10, stroke: T.inkSubtle }));

  const ledger = (x, w, tint, head, rows, tail) => {
    els.push(...card(x, 362, w, 132, { spine: tint, strokeWidth: 1.3 }));
    const ix = x + 18, right = x + w - 18;
    els.push(text(ix, 370, fit(head, 9.5, w - 36, 'ledger head'), { size: 9.5, stroke: tint }));
    els.push(rule(ix, right, 386));
    rows.forEach((r, i) => {
      const ry = 394 + i * 18;
      els.push(text(ix, ry, fit(r[0], 9, 180, 'ledger label'), { size: 9, stroke: T.inkMuted }));
      els.push(text(right - 114, ry - 1, r[1],
        { size: 9.5, family: MONO, align: 'right', width: 114, stroke: T.ink }));
    });
    els.push(rule(ix, right, 444));
    els.push(text(ix, 452, fit(tail[0], 9, 180, 'ledger label'), { size: 9, stroke: T.inkMuted }));
    els.push(text(right - 114, 451, tail[1],
      { size: 9.5, family: MONO, align: 'right', width: 114, stroke: T.ink }));
    els.push(text(ix, 472, fit(tail[2], 8.5, w - 36, 'ledger tail'), { size: 8.5, stroke: T.inkMuted }));
  };

  ledger(40, 340, T.alert, 'LEFT IN THE WINDOW', [
    ['added at iteration 3', '~25,000'],
    ['re-read on the 9 later calls', '~225,000'],
    ['total input tokens', '~250,000'],
  ], ['at ~$5 per million input', '~$1.25', 'and it dies at the reset']);

  ledger(396, 340, T.success, 'OFFLOADED, POINTER RETURNED', [
    ['added at iteration 3', '~30'],
    ['re-read on the 9 later calls', '~270'],
    ['total input tokens', '~300'],
  ], ['at the same rate', '~$0.0015', 'plus ~100 KB on disk, still greppable']);

  els.push(...card(752, 362, 168, 132, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(770, 370, 'THE RATIO', { size: 9.5, stroke: T.primary }));
  els.push(text(768, 392, '~800x', { size: 28, align: 'center', width: 136, stroke: T.primary }));
  els.push(text(768, 434, 'less to carry one', { size: 9.5, align: 'center', width: 136, stroke: T.ink }));
  els.push(text(768, 450, 'tool result', { size: 9.5, align: 'center', width: 136, stroke: T.ink }));
  els.push(text(768, 472, 'the rate is illustrative',
    { size: 8, align: 'center', width: 136, stroke: T.inkSubtle }));

  els.push(text(40, 512,
    'If it might be needed later but not now, write it to disk: the window is a small, expensive cache over the store.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 536,
    'Git makes the disk side reversible: checkpoint after each verified step, and reset to the last good commit when the next fails.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The small volatile window beside a durable filesystem under git, and what one offload is worth',
    desc: 'A hand-drawn figure in two tiers. The upper tier sets the context window against the '
      + 'durable store. On the left the window is drawn deliberately small: it holds what the model '
      + 'reads this turn, is noted as two hundred thousand tokens and more on the box though usable '
      + 'capacity is less, and is listed as small relative to the work, priced per token on every '
      + 'call, volatile and wiped at every reset, and gone on any crash. On the right the durable '
      + 'store on disk holds two panels. The filesystem panel lists four files with their roles: '
      + 'plan.md, rewritten each step rather than appended; scratch slash build.log, two thousand '
      + 'lines and about a hundred kilobytes, with a pointer left behind to fetch it back; '
      + 'output.json, the artefact itself rather than transcript text; and handoff.md, holding '
      + 'spec, done, next and state, which survives a reset. The git panel draws three commits in a '
      + 'row, two checkpoints and a bad step, with a revert arrow arcing back from the bad step to '
      + 'the last checkpoint, and beneath them the checkpoint and rollback commands: git add dash A '
      + 'restricted to src and tests, git reset hard to a41c9f2, and git clean restricted to the '
      + 'same paths, with the warning to check the return code because a failed commit still leaves '
      + 'a hash. Two arrows cross the gap: write and offload out to disk, read on demand back. The '
      + 'lower tier prices one offload, taking a two-thousand-line build log of about twenty-five '
      + 'thousand tokens arriving at iteration three of a twelve-iteration run. Left in the window '
      + 'it adds about twenty-five thousand tokens, is re-read on the nine later calls for about '
      + 'two hundred and twenty-five thousand more, totals about two hundred and fifty thousand '
      + 'input tokens and about one dollar twenty-five at an illustrative five dollars per million, '
      + 'and dies at the reset. Offloaded with a pointer returned it adds about thirty tokens, '
      + 'about two hundred and seventy on re-reads, about three hundred in total and a fraction of '
      + 'a cent, plus about a hundred kilobytes on disk that is still greppable. A third card gives '
      + 'the ratio as about eight hundred times less to carry one tool result, and notes that the '
      + 'rate is illustrative. Captions record that anything which might be needed later but not '
      + 'now should be written to disk, the window being a small expensive cache over the store, '
      + 'and that git makes the disk side reversible by checkpointing after each verified step and '
      + 'resetting to the last good commit when the next fails.',
  };
}

// ---------------------------------------------------------------- diagram 2
function handoffLifecycle() {
  resetSeq();
  const W = 960, H = 588;

  const els = [...heading('The handoff file: state that survives a context reset',
    'A structured file carries the spec, the progress and the next steps across a fresh window, session or agent.')];

  els.push(text(56, 92, 'THE WINDOW: VOLATILE, AND WIPED AT THE RESET', { size: 10, stroke: T.inkSubtle }));

  els.push(rect(56, 112, 300, 100, { stroke: T.ink, fill: T.surface, strokeWidth: 1.5 }));
  els.push(text(74, 122, 'SESSION 1: a fresh window', { size: 11, stroke: T.ink }));
  els.push(text(74, 146, fit('reads the handoff, does a chunk of work,', 9.5, 264, 'session line'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(74, 162, fit('and rewrites the file before the reset', 9.5, 264, 'session line'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(74, 186, fit('writes it at the checkpoint, before the risky step', 8.5, 264, 'session note'),
    { size: 8.5, stroke: T.warn }));

  els.push(rect(396, 112, 150, 100, { stroke: T.alert, strokeWidth: 1.5, strokeStyle: 'dashed' }));
  els.push(text(396, 130, 'CONTEXT', { size: 13, align: 'center', width: 150, stroke: T.alert }));
  els.push(text(396, 150, 'RESET', { size: 13, align: 'center', width: 150, stroke: T.alert }));
  els.push(text(396, 176, 'the window is wiped;', { size: 8.5, align: 'center', width: 150, stroke: T.inkMuted }));
  els.push(text(396, 190, 'nothing in it survives', { size: 8.5, align: 'center', width: 150, stroke: T.inkMuted }));

  els.push(rect(586, 112, 318, 100, { stroke: T.ink, fill: T.surface, strokeWidth: 1.5 }));
  els.push(text(604, 122, 'SESSION 2: a fresh window', { size: 11, stroke: T.ink }));
  els.push(text(604, 146, fit('reads handoff.md and resumes at Next:', 9.5, 282, 'session line'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(604, 164, fit('pytest tests/test_rows.py', 9, 282, 'session command'),
    { size: 9, family: MONO, stroke: T.ink }));
  els.push(text(604, 186, fit('checks State against the tree before trusting it', 8.5, 282, 'session note'),
    { size: 8.5, stroke: T.success }));

  els.push(arrow([[358, 162], [392, 162]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[548, 162], [582, 162]], { stroke: T.inkMuted, strokeWidth: 1.3 }));

  els.push(rule(40, 920, 234));
  els.push(text(56, 246, 'DISK: PERSISTENT', { size: 10, stroke: T.inkSubtle }));

  // --- the rule that makes each field usable -------------------------------
  els.push(...card(40, 278, 364, 166, { spine: T.primary, strokeWidth: 1.5 }));
  els.push(text(58, 286, 'WHAT MAKES EACH FIELD USABLE', { size: 9.5, stroke: T.primary }));
  els.push(rule(58, 388, 306));
  [
    ['Spec', 'the goal, not the history; it does not change'],
    ['Done', 'what is verified, with a count: 5 of 7 tests green'],
    ['Next', 'an executable instruction, not a topic'],
    ['State', 'checkable: branch, checkpoint hash, test count'],
  ].forEach((f, i) => {
    const ry = 316 + i * 26;
    els.push(text(58, ry, f[0], { size: 9.5, family: MONO, stroke: T.success }));
    els.push(text(106, ry + 1, fit(f[1], 9, 282, 'field rule'), { size: 9, stroke: T.ink }));
  });
  els.push(text(58, 424, fit('and it is rewritten every session, never appended', 8.5, 330, 'field note'),
    { size: 8.5, stroke: T.inkMuted }));

  // --- the file itself ------------------------------------------------------
  els.push(...card(424, 278, 496, 166, { spine: T.success, strokeWidth: 1.5 }));
  els.push(text(442, 286, 'handoff.md', { size: 12, stroke: T.ink }));
  els.push(text(694, 288, 'SURVIVES THE RESET', { size: 8.5, align: 'right', width: 208, stroke: T.success }));
  els.push(rule(442, 902, 306));
  [
    ['## Spec', T.success],
    ['Parse the vendor CSV export into rows.json, one object per line item.', T.ink],
    ['## Done', T.success],
    ['Header detection and type coercion. 5 of 7 tests green.', T.ink],
    ['## Next', T.success],
    ['Run pytest tests/test_rows.py; fix test_multiline_quoted and', T.ink],
    ['test_negative_amounts. Leave the header code alone.', T.ink],
    ['## State', T.success],
    ['branch feat/csv-parser, last checkpoint a41c9f2, 5/7 tests green.', T.ink],
  ].forEach((l, i) => els.push(text(442, 312 + i * 14, fit(l[0], 9.5, 460, 'handoff line'),
    { size: 9.5, family: MONO, stroke: l[1] })));

  els.push(arrow([[206, 214], [206, 256], [520, 256], [520, 276]], { stroke: T.ink, strokeWidth: 1.3 }));
  els.push(text(340, 240, 'write', { size: 9.5, stroke: T.inkMuted }));
  els.push(arrow([[760, 276], [760, 214]], { stroke: T.success, strokeWidth: 1.3 }));
  els.push(text(766, 240, 'read', { size: 9.5, stroke: T.inkMuted }));

  // --- the two rules that keep the file trustworthy ------------------------
  els.push(...card(40, 462, 440, 62, { spine: T.warn, strokeWidth: 1.3 }));
  els.push(text(58, 470, 'THE TIMING RULE', { size: 9, stroke: T.warn }));
  els.push(text(58, 486, fit('Write the handoff at the checkpoint, before the risky step, so it is', 9, 406, 'rule line'),
    { size: 9, stroke: T.ink }));
  els.push(text(58, 502, fit('a plan, and what remains if the risky step never returns.', 9, 406, 'rule line'),
    { size: 9, stroke: T.inkMuted }));

  els.push(...card(500, 462, 420, 62, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(518, 470, 'THE WRITE RULE', { size: 9, stroke: T.primary }));
  els.push(text(518, 486, fit('Replace it atomically: write handoff.md.tmp beside it, then', 9, 386, 'rule line'),
    { size: 9, stroke: T.ink }));
  els.push(text(518, 502, fit('os.replace it over the target. A torn file resumes as truth.', 9, 386, 'rule line'),
    { size: 9, stroke: T.inkMuted }));

  els.push(text(40, 542,
    'The window is wiped at the reset; the file is not. Each fresh session reads the handoff and resumes where the last one stopped.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 564, 'The file is the source of truth and the window is disposable, which is exactly the Ralph loop of Post 18.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A handoff file carrying work across a context reset between two sessions',
    desc: 'A hand-drawn figure in three bands. The upper band is the window, volatile and wiped at '
      + 'the reset. It holds session one, a fresh window that reads the handoff, does a chunk of '
      + 'work and rewrites the file before the reset, noting that it writes at the checkpoint '
      + 'before the risky step; then a dashed box marked context reset, where the window is wiped '
      + 'and nothing in it survives; then session two, another fresh window that reads handoff.md, '
      + 'resumes at the Next field by running pytest on tests slash test_rows.py, and checks the '
      + 'State field against the tree before trusting it. The middle band is disk, persistent, and '
      + 'holds two cards. The first gives the rule that makes each field usable: Spec is the goal '
      + 'and not the history, so it does not change; Done is what is verified, with a count, five '
      + 'of seven tests green; Next is an executable instruction and not a topic; State is '
      + 'checkable, being a branch, a checkpoint hash and a test count; and the file is rewritten '
      + 'every session, never appended. The second card is handoff.md itself, marked as surviving '
      + 'the reset, showing the whole file: a Spec section reading parse the vendor CSV export into '
      + 'rows.json, one object per line item; a Done section reading header detection and type '
      + 'coercion, five of seven tests green; a Next section reading run pytest on tests slash '
      + 'test_rows.py and fix test_multiline_quoted and test_negative_amounts, leaving the header '
      + 'code alone; and a State section reading branch feat slash csv-parser, last checkpoint '
      + 'a41c9f2, five of seven tests green. An arrow runs down from session one to the file, '
      + 'marked write, and another runs up from the file to session two, marked read. The lower '
      + 'band carries two rules: the timing rule, to write the handoff at the checkpoint before the '
      + 'risky step so that it is a plan and what remains if the risky step never returns; and the '
      + 'write rule, to replace it atomically by writing handoff.md.tmp beside it and using '
      + 'os.replace over the target, since a torn file resumes as truth. Captions record that the '
      + 'window is wiped at the reset while the file is not, so each fresh session resumes where '
      + 'the last stopped, and that the file being the source of truth with a disposable window is '
      + 'exactly the Ralph loop of post 18.',
  };
}

// ---------------------------------------------------------------- diagram 3
function whereStateBelongs() {
  resetSeq();
  const W = 960, H = 470;

  const els = [...heading('Where a piece of state belongs, and the two ways to get it wrong',
    'The question is not how big it is. It is when you need it: this turn and every turn, or later and only sometimes.')];

  els.push(text(40, 92, 'NEEDED THIS TURN, AND EVERY TURN: THE WINDOW', { size: 10, stroke: T.primary }));
  els.push(text(500, 92, 'NEEDED LATER, OR ONLY SOMETIMES: DISK', { size: 10, stroke: T.accent }));

  els.push(...card(40, 108, 430, 190, { spine: T.primary, strokeWidth: 1.4 }));
  els.push(...card(490, 108, 430, 190, { spine: T.accent, strokeWidth: 1.4 }));
  els.push(line([[480, 108], [480, 298]], { stroke: T.inkSubtle, strokeWidth: 1.2, strokeStyle: 'dashed' }));

  const rows = (x, items, tint) => {
    const out = [];
    items.forEach((it, i) => {
      const y = 126 + i * 42;
      els.push(text(x + 18, y, fit(it[0], 11.5, 394, 'state name'), { size: 11.5, stroke: T.ink }));
      els.push(text(x + 18, y + 17, fit(it[1], 9, 394, 'state gloss'), { size: 9, stroke: T.inkMuted }));
    });
    return out;
  };
  rows(40, [
    ['The task, and the current step of the plan', 'what the model is reasoning about right now'],
    ['The last tool result it is acting on', 'the observation that decides the next move'],
    ['The rules that apply on every turn', 'a short memory file, injected each session (Post 10)'],
    ['A pointer to everything else', 'a path, and one line saying what is in it'],
  ], T.primary);
  rows(490, [
    ['The full plan, and the scratchpad', 'plan.md and task.md, re-read when the thread slips'],
    ['Big tool output', 'scratch/build.log, with a pointer left in the window'],
    ['Artefacts: the actual product', 'generated code, output.json, the report'],
    ['The handoff: spec, done, next, state', 'handoff.md, the one file that survives a reset'],
  ], T.accent);

  els.push(text(40, 320, 'THE TWO MIRROR-IMAGE MISTAKES', { size: 10, stroke: T.inkSubtle }));

  els.push(...card(40, 336, 430, 68, { spine: T.alert, strokeWidth: 1.4 }));
  els.push(text(58, 344, 'State in the window that should be on disk', { size: 11.5, stroke: T.ink }));
  els.push(text(58, 364, 'a 2,000-line log pasted into the transcript, or the plan kept', { size: 9, stroke: T.inkMuted }));
  els.push(text(58, 378, 'only in the conversation: it bloats the window and dies at the reset', { size: 9, stroke: T.inkMuted }));

  els.push(...card(490, 336, 430, 68, { spine: T.alert, strokeWidth: 1.4 }));
  els.push(text(508, 344, 'State on disk that should be in the window', { size: 11.5, stroke: T.ink }));
  els.push(text(508, 364, 'a fact the model needs on every turn hidden behind a file read:', { size: 9, stroke: T.inkMuted }));
  els.push(text(508, 378, 'the agent then spends its turns doing filesystem bookkeeping', { size: 9, stroke: T.inkMuted }));

  els.push(text(40, 420,
    'Two more, both easy to miss: an unversioned working directory, because no git means no rollback;',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 442, 'and an append-only notes.md that never compacts, which recreates the window problem on disk.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'Which state belongs in the window, which belongs on disk, and the two mistakes',
    desc: 'A hand-drawn figure split by a dashed line. On the left, state needed this turn and '
      + 'every turn, which belongs in the window: the task and the current step of the plan, since '
      + 'that is what the model is reasoning about right now; the last tool result it is acting on, '
      + 'the observation that decides the next move; the rules that apply on every turn, meaning a '
      + 'short memory file injected each session; and a pointer to everything else, being a path '
      + 'and one line saying what is in it. On the right, state needed later or only sometimes, '
      + 'which belongs on disk: the full plan and the scratchpad, re-read when the thread slips; '
      + 'big tool output such as a build log, with only a pointer left in the window; artefacts, '
      + 'meaning the actual product such as generated code, output.json or a report; and the '
      + 'handoff file carrying spec, done, next and state, the one file that survives a reset. '
      + 'Below, the two mirror-image mistakes: state in the window that should be on disk, such as '
      + 'a two-thousand-line log pasted into the transcript or a plan kept only in the '
      + 'conversation, which bloats the window and dies at the reset; and state on disk that should '
      + 'be in the window, such as a fact the model needs every turn hidden behind a file read, '
      + 'which makes the agent spend its turns on filesystem bookkeeping. Two further mistakes are '
      + 'noted: an unversioned working directory, since no git means no rollback, and an '
      + 'append-only notes file that never compacts, which recreates the window problem on disk.',
  };
}

module.exports = { durableState, handoffLifecycle, whereStateBelongs };

if (require.main === module) {
  emit('01-filesystem-durable-state', durableState());
  emit('02-handoff-lifecycle', handoffLifecycle());
  emit('03-where-state-belongs', whereStateBelongs());
}
