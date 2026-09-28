// The post 17 diagrams, hand-drawn.
//
//   01-shared-repo-swarm  960 x 560  Mirror of the existing figure, refilled.
//   02-worktree-isolation 960 x 536  Mirror, refilled.
//   03-at-least-once      960 x 490  NEW, published: section 6 had no figure.
//
// Section 6 is the one that stops the atomic claim from being read as a
// stronger guarantee than it is. The argument is a *sequence* -- claim, stall,
// reclaim, and then both agents finish -- and a sequence is the one thing prose
// is worst at and a timeline is best at.
//
// Figures 1 and 2 were reviewed as thin: 960x400 canvases whose cards carried
// two short lines each and whose lower-right quadrants were empty. Both now
// carry a second tier. Every number in figure 1 is measured: the concurrency
// evidence from section 2 of the post, and the demo output of
// code/17-parallel-agents, run to get it. Figure 2 stays qualitative on
// purpose, because the post has no measured worktree numbers to carry; it
// carries git's actual command and flag names instead.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, wrap, card, rule } = require('./scaffold');

const MONO = 3;

// ---------------------------------------------------------------- diagram 1
function swarm() {
  resetSeq();
  const W = 960, H = 560;

  const els = [...heading('A leaderless swarm on a shared repo',
    'No central orchestrator. The repository is the coordinator, and a claim is an exclusive create.')];

  // --- the board itself ----------------------------------------------------
  els.push(...card(40, 92, 540, 234, { spine: T.primary, strokeWidth: 1.4 }));
  els.push(text(58, 100, 'TASK BOARD: THREE DIRECTORIES IN THE REPO', { size: 10, stroke: T.primary }));

  const COLS = [
    [58, 'open/ 2', ['task-6', 'task-7']],
    [235, 'claimed/ 2', ['task-4.ada', 'task-5.linus']],
    [412, 'done/ 3', ['task-1', 'task-2', 'task-3']],
  ];
  COLS.forEach((c) => {
    els.push(text(c[0], 124, c[1], { size: 10, family: MONO, stroke: T.inkSubtle }));
    c[2].forEach((t, i) => {
      els.push(rect(c[0], 142 + i * 26, 145, 22, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
      els.push(text(c[0] + 8, 147 + i * 26, t, { size: 9, family: MONO, stroke: T.ink }));
    });
  });

  els.push(rule(58, 562, 228));
  els.push(text(58, 236, fit('a claim is one exclusive create, then a move: open/task-4 becomes claimed/task-4.ada', 9.5, 504, 'claim line'),
    { size: 9.5, stroke: T.ink }));
  els.push(text(58, 253, fit('the loser of the race finds its source file already gone, and takes the next task', 9, 504, 'loser line'),
    { size: 9, stroke: T.ink }));
  els.push(text(58, 272, fit('the claim name carries the owner, so a stale claim is attributable, which is what', 9, 504, 'owner line'),
    { size: 9, stroke: T.inkMuted }));
  els.push(text(58, 286, fit('makes the lease sweeper and its fourth state implementable at all', 9, 504, 'sweeper line'),
    { size: 9, stroke: T.inkMuted }));
  els.push(text(58, 306, fit('the board mid-flight: two claims held, three finished, two still open', 9, 504, 'board caption'),
    { size: 9, stroke: T.inkSubtle }));

  // --- the three agents, each carrying its claim, its tree and its history --
  const AGENTS = [
    ['ada', 'WORKING', T.success,
      'holds   claimed/task-4.ada',
      'edits   ../wt-ada on agent/ada',
      'done    task-1'],
    ['linus', 'WORKING', T.success,
      'holds   claimed/task-5.linus',
      'edits   ../wt-linus on agent/linus',
      'done    task-2'],
    ['grace', 'BETWEEN TASKS', T.warn,
      'wrote   task-3 into done/, then let go',
      'edits   ../wt-grace on agent/grace',
      'next    claim one of the 2 in open/'],
  ];
  AGENTS.forEach((a, i) => {
    const y = 92 + i * 78;
    els.push(...card(616, y, 304, 74, { spine: a[2], strokeWidth: 1.3 }));
    els.push(text(634, y + 7, 'agent: ' + a[0], { size: 12.5, stroke: T.ink }));
    els.push(text(634, y + 10, a[1], { size: 8.5, align: 'right', width: 268, stroke: a[2] }));
    [a[3], a[4], a[5]].forEach((l, j) => els.push(
      text(634, y + 28 + j * 15, fit(l, 9, 268, 'agent detail'),
        { size: 9, family: MONO, stroke: j === 2 ? T.inkMuted : T.ink })));
    els.push(arrow([[612, y + 37], [584, y + 37]], { stroke: T.inkMuted, strokeWidth: 1.2 }));
  });

  // --- second tier: the operation, the evidence, the measured run ----------
  const PX = [40, 347, 654], PW = 266, PY = 346, PH = 148;

  els.push(...card(PX[0], PY, PW, PH, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(PX[0] + 16, PY + 9, 'THE CLAIM, IN TWO STEPS', { size: 9, stroke: T.primary }));
  els.push(rule(PX[0] + 16, PX[0] + 250, PY + 26));
  ['token = .claims/task-6',
    'os.open(token,',
    '  O_CREAT | O_EXCL)   # exclude',
    '  -> FileExistsError:',
    '     someone else has it',
    'os.rename(src, dst)   # move'].forEach((l, i) => els.push(
    text(PX[0] + 16, PY + 34 + i * 13, fit(l, 8.5, 234, 'claim code'),
      { size: 8.5, family: MONO, stroke: T.ink })));
  els.push(rule(PX[0] + 16, PX[0] + 250, PY + 116));
  els.push(text(PX[0] + 16, PY + 122,
    wrap('The token is keyed on the task, not the agent: that is what makes it contended.', 8.5, 234),
    { size: 8.5, stroke: T.inkMuted }));

  els.push(...card(PX[1], PY, PW, PH, { spine: T.alert, strokeWidth: 1.3 }));
  els.push(text(PX[1] + 16, PY + 9, 'TWO FAILURES, NOT ONE', { size: 9, stroke: T.alert }));
  els.push(rule(PX[1] + 16, PX[1] + 250, PY + 26));
  els.push(text(PX[1] + 16, PY + 32,
    wrap('Renaming and trusting it: 8 of 8 trials handed one task to two agents.', 9, 234),
    { size: 9, stroke: T.alert }));
  els.push(text(PX[1] + 16, PY + 68,
    wrap('Renaming and checking after: passed, then failed about 1 run in 3.', 9, 234),
    { size: 9, stroke: T.alert }));
  els.push(rule(PX[1] + 16, PX[1] + 250, PY + 108));
  els.push(text(PX[1] + 16, PY + 116,
    wrap('Two agents renaming one source to different names never contend at all.', 8.5, 234),
    { size: 8.5, stroke: T.inkMuted }));

  els.push(...card(PX[2], PY, PW, PH, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(PX[2] + 16, PY + 9, 'THE COMPANION DEMO, DRAINED', { size: 9, stroke: T.success }));
  els.push(rule(PX[2] + 16, PX[2] + 250, PY + 26));
  els.push(text(PX[2] + 16, PY + 32, '$ python -m parallel_agents',
    { size: 8.5, family: MONO, stroke: T.inkMuted }));
  ['ada    3  task-1, task-4, task-7',
    'linus  2  task-2, task-5',
    'grace  2  task-3, task-6'].forEach((l, i) => els.push(
    text(PX[2] + 16, PY + 50 + i * 14, fit(l, 8.5, 234, 'demo row'),
      { size: 8.5, family: MONO, stroke: T.ink })));
  els.push(text(PX[2] + 16, PY + 96, fit('board: open 0, claimed 0, done 7', 8.5, 234, 'demo counts'),
    { size: 8.5, family: MONO, stroke: T.success }));
  els.push(rule(PX[2] + 16, PX[2] + 250, PY + 116));
  els.push(text(PX[2] + 16, PY + 122,
    wrap('9 tests ship with it. Only the threaded one could ever see the race.', 8.5, 234),
    { size: 8.5, stroke: T.inkMuted }));

  els.push(text(40, 508, 'There is no coordinator to lose: the filesystem own atomicity is the concurrency control.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 530, 'Ask the filesystem for exclusivity; do not check afterwards whether you happened to get it.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A file-based task board claimed by three agents, with the claim operation, the race it survives, and a measured demo run',
    desc: 'A hand-drawn figure in two tiers. In the upper tier, on the left, a task board made of '
      + 'files in the repository, in three directories. Open holds task-6 and task-7. Claimed holds '
      + 'task-4 owned by ada and task-5 owned by linus, each claim file carrying the owner name. '
      + 'Done holds task-1, task-2 and task-3. Notes record that a claim is one exclusive create '
      + 'and then a move, from '
      + 'open slash task-4 to claimed slash task-4 dot ada, that the loser of the race sees its '
      + 'source file already gone and takes the next task, and that because the claim name carries '
      + 'the owner a stale claim is attributable and the lease sweeper knows which agent abandoned '
      + 'it. On the right, three agent cards, each with a status, the claim it holds, the worktree '
      + 'and branch it edits in, and its history: ada is working, holds claimed slash task-4 dot '
      + 'ada, edits in wt-ada on branch agent slash ada, and has finished task-1; linus is working '
      + 'on task-5 in wt-linus; grace is between tasks, having written task-3 into done, and will '
      + 'claim one of the two tasks still open. Arrows run from each agent back to the board. The '
      + 'lower tier holds three panels. The first gives the claim in two steps: a token at dot '
      + 'claims slash task-6 is created with O underscore CREAT and O underscore EXCL, which '
      + 'raises FileExistsError for every agent but one, and only then is the task file renamed '
      + 'into claimed. The token is keyed on the task rather than on the agent, which is what '
      + 'makes it a contended name. The second panel records two failures rather than one: '
      + 'renaming and trusting the result handed one task to two agents in 8 of 8 trials, and '
      + 'renaming and checking the result afterwards passed its suite and then failed about one '
      + 'run in three, because two agents renaming one source to different names never contend at '
      + 'all. The third panel gives the companion demo drained: '
      + 'running python dash m parallel underscore agents, ada did 3 tasks, task-1, task-4 and '
      + 'task-7; linus did 2, task-2 and task-5; grace did 2, task-3 and task-6; and the board '
      + 'ends with open 0, claimed 0 and done 7. Nine tests ship with it, of which only the '
      + 'threaded one could ever see the race. Captions record that there is no coordinator to '
      + 'lose because the filesystem own atomicity is the concurrency control, and that the '
      + 'reader should ask the filesystem for exclusivity rather than checking afterwards '
      + 'whether they happened to get it.',
  };
}

// ---------------------------------------------------------------- diagram 2
function worktrees() {
  resetSeq();
  const W = 960, H = 536;

  const els = [...heading('Worktrees isolate each agent edits',
    'One repository, one working copy per agent, so parallel edits never collide.')];

  // --- top row: the command, the repository, the return path ---------------
  els.push(...card(40, 88, 280, 80, { spine: T.primary, strokeWidth: 1.3 }));
  els.push(text(58, 94, 'LIFECYCLE, PER AGENT', { size: 9, stroke: T.primary }));
  ['git worktree add ../wt-ada -b agent/ada',
    'git worktree remove ../wt-ada',
    'git worktree unlock ../wt-linus'].forEach((l, i) => els.push(
    text(58, 110 + i * 13, fit(l, 8.5, 248, 'worktree command'),
      { size: 8.5, family: MONO, stroke: T.ink })));
  els.push(text(58, 151, fit('add, remove, and unlock after a crash', 8.5, 248, 'command note'),
    { size: 8.5, stroke: T.inkMuted }));

  els.push(rect(360, 88, 240, 80, { stroke: T.ink, fill: T.neutral1, strokeWidth: 1.6 }));
  els.push(text(360, 98, 'MAIN REPO', { size: 14, align: 'center', width: 240, stroke: T.ink }));
  els.push(text(360, 124, 'branch: main', { size: 9.5, align: 'center', width: 240, stroke: T.inkMuted }));
  els.push(text(360, 142, 'one object database, one history', { size: 9, align: 'center', width: 240, stroke: T.inkMuted }));

  els.push(...card(660, 88, 260, 80, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(678, 94, 'MERGE GATE', { size: 9, stroke: T.success }));
  ['a branch lands only after the',
    'candidate merge builds and its',
    'tests pass (Post 11)'].forEach((l, i) => els.push(
    text(678, 112 + i * 14, fit(l, 8.5, 224, 'gate line'), { size: 8.5, stroke: T.ink })));
  els.push(arrow([[656, 128], [604, 128]], { stroke: T.inkMuted, strokeWidth: 1.2 }));

  els.push(arrow([[400, 170], [190, 204]], { stroke: T.inkMuted, strokeWidth: 1.2 }));
  els.push(arrow([[480, 170], [479, 204]], { stroke: T.inkMuted, strokeWidth: 1.2 }));
  els.push(arrow([[560, 170], [768, 204]], { stroke: T.inkMuted, strokeWidth: 1.2 }));

  els.push(arrow([[880, 206], [880, 172]],
    { stroke: T.success, strokeWidth: 1.4, strokeStyle: 'dashed' }));
  els.push(text(690, 180, fit('verified branch merging back', 8.5, 180, 'merge label'),
    { size: 8.5, stroke: T.success }));

  // --- the three worktrees, each in a different state ----------------------
  const WT = [
    ['ada', 'RUNNING', T.success,
      'holds claimed/task-4.ada',
      'deps installed here; a tree inherits none',
      'no node_modules, no .env, no build cache'],
    ['linus', 'CRASHED', T.alert,
      'claim expired; the sweeper reopened task-5',
      'tree left locked: unlock, then remove',
      'the branch stays until a policy sweeps it'],
    ['grace', 'VERIFIED', T.primary,
      'task-3 built and its tests passed here',
      'merges through the gate, not directly',
      'then git worktree remove ../wt-grace'],
  ];
  WT.forEach((w, i) => {
    const x = 40 + i * 306;
    els.push(...card(x, 210, 266, 116, { spine: w[2], strokeWidth: 1.4 }));
    els.push(text(x + 18, 219, 'WORKTREE  ' + w[0], { size: 12.5, stroke: T.ink }));
    els.push(text(x + 16, 222, w[1], { size: 8.5, align: 'right', width: 234, stroke: w[2] }));
    els.push(text(x + 18, 242, '../wt-' + w[0], { size: 9, family: MONO, stroke: T.inkMuted }));
    els.push(text(x + 18, 256, 'branch: agent/' + w[0], { size: 9, family: MONO, stroke: T.inkMuted }));
    els.push(rule(x + 16, x + 250, 274));
    [w[3], w[4], w[5]].forEach((l, j) => els.push(
      text(x + 18, 282 + j * 13, fit(l, 8.5, 232, 'worktree detail'),
        { size: 8.5, stroke: j === 0 ? T.ink : T.inkMuted })));
  });

  // --- second tier: the four properties that decide worktree over clone ----
  const PROPS = [
    [T.primary, 'ONE OBJECT DATABASE',
      'A worktree costs a working copy, not a copy of the history, so the tenth agent is cheap '
      + 'even on a repo with years of commits. Merged work is visible to every agent the moment '
      + 'it lands, because there is one history.'],
    [T.success, 'ONE BRANCH, ONE TREE',
      'By default add declines a branch already checked out elsewhere: a free correctness '
      + 'guarantee. The realistic accident is a harness retrying the failed add with --force. '
      + 'Retry under a new name instead.'],
    [T.warn, 'A CHECKOUT, NOT AN ENV',
      'Tracked files only. Every tree needs its own dependency install; .worktreeinclude copies '
      + 'gitignored files such as .env into it; LFS content stays pointer files until git lfs '
      + 'pull runs there.'],
    [T.alert, 'DEBRIS NEEDS A SWEEPER',
      'remove is the exit, and a locked tree needs unlock first. prune only repairs a directory '
      + 'somebody deleted. Nothing sweeps the branches, which a long swarm piles up by the '
      + 'hundred, so they need a written policy.'],
  ];
  PROPS.forEach((p, i) => {
    const x = 40 + i * 224;
    els.push(...card(x, 344, 208, 128, { spine: p[0], strokeWidth: 1.3 }));
    els.push(text(x + 16, 353, fit(p[1], 8.5, 176, 'property title'), { size: 8.5, stroke: p[0] }));
    els.push(rule(x + 16, x + 192, 370));
    els.push(text(x + 16, 377, wrap(p[2], 8.5, 176, 8), { size: 8.5, stroke: T.ink }));
  });

  els.push(text(40, 486, 'A worktree isolates files and nothing else: same processes, same network, same credentials.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 508, 'Where the task runs code the agent wrote, you want a container (Post 14). The 16-agent compiler run gave each agent its own clone.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'One repository with a worktree and a branch per agent, the four properties that make that work, and the boundary it does not give you',
    desc: 'A hand-drawn figure in two tiers. Across the top, a panel gives the per-agent lifecycle '
      + 'in two commands, git worktree add dot dot slash wt-ada dash b agent slash ada and git '
      + 'worktree remove dot dot slash wt-ada, noting that add declines a branch already checked '
      + 'out. Beside it the main repository sits on branch main with one object database and one '
      + 'history. Arrows lead down from it to three worktrees, each shown in a different state. '
      + 'The ada worktree is running: it is at wt-ada on branch agent slash ada, holds the claim '
      + 'on task-4, has its dependencies installed in the tree because a worktree inherits none, '
      + 'and contains no node underscore modules, no dot env and no build cache. The linus '
      + 'worktree has crashed: its claim expired and the sweeper reopened task-5, the tree was '
      + 'left locked so it needs unlock before remove, and its branch stays until a policy sweeps '
      + 'it. The grace worktree is verified: task-3 built and its tests passed there, it merges '
      + 'through the gate rather than directly, and the tree is then removed. A dashed arrow '
      + 'returns from the grace worktree to the main repository, labelled verified branch merges '
      + 'back into main. The lower tier gives the four properties that decide a worktree over a '
      + 'clone. One object database: a worktree costs a working copy and not a copy of the '
      + 'history, so the tenth agent is cheap on a repository with years of commits, and merged '
      + 'work is visible to every agent at once. One branch, one tree: git worktree add declines a '
      + 'branch already checked out elsewhere, and the realistic accident is a harness retrying '
      + 'with force, so retry under a new name instead. A checkout, not an environment: tracked '
      + 'files only, each tree needs its own dependency install, a worktreeinclude file copies '
      + 'gitignored files such as dot env in, and Large File Storage content stays as pointers '
      + 'until git lfs pull runs. Debris needs a sweeper: remove is the exit and a locked tree '
      + 'needs unlock first, prune only repairs a directory somebody deleted, and nothing sweeps '
      + 'the branches, which a long swarm piles up by the hundred. Captions record that a '
      + 'worktree isolates files and nothing else, sharing processes, network and credentials, so '
      + 'where the task runs code the agent wrote you want a container instead, as in the '
      + '16-agent compiler run, which gave each agent its own clone.',
  };
}

// ---------------------------------------------------------------- diagram 3
function atLeastOnce() {
  resetSeq();
  const W = 960, H = 490;

  const els = [...heading('At-least-once, not exactly-once',
    'The atomic claim stops two agents starting together. It does not stop a reclaimed task running twice.')];

  ['AGENT A', 'THE BOARD', 'AGENT B'].forEach((l, i) => {
    els.push(text(40, 132 + i * 56, l, { size: 9.5, align: 'right', width: 110, stroke: T.inkSubtle }));
  });

  const EVENTS = [
    [170, 0, 'claims', 'task-7', T.ink],
    [275, 0, 'starts', 'work', T.ink],
    [380, 0, 'goes quiet', '(a hung call)', T.alert],
    [485, 1, 'lease expires;', 'back to open/', T.warn],
    [590, 2, 'claims', 'task-7', T.ink],
    [695, 2, 'finishes; the', 'change lands', T.ink],
    [800, 0, 'wakes up and', 'finishes too', T.alert],
  ];
  EVENTS.forEach((e, i) => {
    const y = 120 + e[1] * 56;
    els.push(rect(e[0], y, 96, 40, { stroke: e[4], fill: T.surface, strokeWidth: e[4] === T.alert ? 1.7 : 1.2 }));
    els.push(text(e[0], y + 8, e[2], { size: 8.5, align: 'center', width: 96, stroke: e[4] }));
    els.push(text(e[0], y + 22, e[3], { size: 8.5, align: 'center', width: 96, stroke: e[4] }));
    els.push(line([[e[0] + 48, 290], [e[0] + 48, 296]], { stroke: T.inkSubtle, strokeWidth: 1 }));
    els.push(text(e[0], 300, 't' + (i + 1), { size: 8.5, align: 'center', width: 96, stroke: T.inkSubtle }));
  });

  els.push(line([[160, 290], [900, 290]], { stroke: T.inkSubtle, strokeWidth: 1.2 }));
  els.push(text(160, 320, 'Each claim was atomic and the board behaved exactly as designed. The task simply ran twice.',
    { size: 10, stroke: T.alert }));

  const MIT = [
    [40, T.success, 'MAKE THE TASK IDEMPOTENT',
      '"ensure this file matches the spec" rather', 'than "append a line", so running it twice is',
      'indistinguishable from running it once'],
    [340, T.primary, 'LET THE MERGE GATE DEDUPE',
      'The second branch is an empty diff or a', 'conflict, and is discarded rather than',
      'treated as a failure'],
    [640, T.warn, 'COMPARE-AND-SET ON FINISH',
      'The finish checks it still owns the claim', 'and refuses if the lease was revoked:',
      'double work, but a single effect'],
  ];
  MIT.forEach((m) => {
    els.push(...card(m[0], 344, 280, 88, { spine: m[1], strokeWidth: 1.4 }));
    els.push(text(m[0] + 16, 352, m[2], { size: 9, stroke: m[1] }));
    [m[3], m[4], m[5]].forEach((l, i) => els.push(text(m[0] + 16, 372 + i * 15,
      fit(l, 9, 248, 'mitigation'), { size: 9, stroke: T.ink })));
  });

  els.push(text(40, 450, 'Tuning the lease does not help: a shorter one reclaims live agents more often, a longer one leaves dead tasks stuck.',
    { size: 11, stroke: T.ink }));
  els.push(text(40, 472, 'Pick the lease for how long the work legitimately takes, and make double execution harmless by design.',
    { size: 11, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'A timeline in which one task is claimed twice, and the three ways to make that harmless',
    desc: 'A hand-drawn timeline across three lanes: agent A, the board, and agent B. At t1 agent A '
      + 'claims task-7; at t2 it starts work; at t3 it goes quiet, on a hung call. At t4 the board '
      + 'lease expires and the task returns to open. At t5 agent B claims task-7; at t6 it finishes '
      + 'and the change lands. At t7 agent A wakes up and finishes too. A note records that each '
      + 'claim was atomic and the board behaved exactly as designed, and that the task simply ran '
      + 'twice. Three panels give the mitigations in order of preference. Make the task idempotent: '
      + 'phrase it as ensure this file matches the spec rather than append a line, so running it '
      + 'twice is indistinguishable from running it once. Let the merge gate deduplicate: the '
      + 'second branch is an empty diff or a conflict and is discarded rather than treated as a '
      + 'failure. Or make the completion a compare-and-set: the finish checks it still owns the '
      + 'claim and refuses if the lease was revoked, so there is double work but a single effect. '
      + 'Captions record that tuning the lease does not help, since a shorter one reclaims live '
      + 'agents more often while a longer one leaves dead tasks stuck, so the lease should be '
      + 'picked for how long the work legitimately takes and double execution made harmless by '
      + 'design.',
  };
}

module.exports = { swarm, worktrees, atLeastOnce };

if (require.main === module) {
  emit('01-shared-repo-swarm', swarm());
  emit('02-worktree-isolation', worktrees());
  emit('03-at-least-once', atLeastOnce());
}
