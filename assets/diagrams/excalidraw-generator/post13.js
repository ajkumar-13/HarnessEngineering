// The post 13 diagrams, hand-drawn.
//
//   01-hook-lifecycle     960 x 500  NEW, published: it REPLACES a figure that was wrong.
//   02-blocked-command    960 x 600  Mirror, redrawn dense: flow, deny-list, run.
//   03-gates-and-reports  960 x 460  NEW, published: section 3 had no figure.
//
// The clean vector `01-hook-lifecycle.svg` labelled the post-edit hook "(can
// reject)", which is the exact claim section 2 now corrects: a post-tool hook
// surfaces a message and cannot undo the write. It also drew three lifecycle
// points where the post names four. This scene is drawn to the corrected prose
// and promoted over it, which is the one case in this pass where a hand-drawn
// figure replaces a clean vector rather than sitting beside it.

const { T, rect, text, line, arrow, resetSeq } = require('./lib');
const { M, heading, emit, fit, card, rule } = require('./scaffold');

const MONO = 3;

// ---------------------------------------------------------------- diagram 1
function hookLifecycle() {
  resetSeq();
  const W = 960, H = 500;

  const els = [...heading('The four hook points, and what each can actually do',
    'A hook is deterministic code at a fixed point. Only one of the four can stop an action; the others supply or report.')];

  const lbox = (y, h, name, gloss) => [
    rect(100, y, 160, h, { stroke: T.ink, fill: T.surface, strokeWidth: 1.4 }),
    text(100, y + 10, name, { size: 12, align: 'center', width: 160, stroke: T.ink }),
    text(100, y + 30, gloss, { size: 8.5, align: 'center', width: 160, stroke: T.inkMuted }),
  ];
  els.push(...lbox(130, 50, 'REASON', 'the model decides'));
  els.push(...lbox(210, 50, 'ACT', 'a tool executes'));
  els.push(...lbox(290, 50, 'OBSERVE', 'the result returns'));
  els.push(...lbox(370, 44, 'COMMIT', 'the work lands'));

  const BARS = [
    [122, T.neutral3, 'session-start'],
    [194, T.success, 'pre-tool'],
    [274, T.warn, 'post-edit'],
    [354, T.primary, 'pre-commit'],
  ];
  BARS.forEach((b) => {
    els.push(line([[92, b[0]], [268, b[0]]], { stroke: b[1], strokeWidth: 2.5, roughness: 0.4 }));
    els.push(text(274, b[0] - 5, b[2], { size: 8, stroke: b[1] }));
  });

  els.push(arrow([[180, 182], [180, 206]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[180, 262], [180, 286]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[180, 342], [180, 366]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(arrow([[96, 315], [62, 315], [62, 155], [96, 155]], { stroke: T.inkMuted, strokeWidth: 1.3 }));

  els.push(text(340, 84, 'FOUR POINTS, AND WHAT EACH IS ABLE TO DO', { size: 9, stroke: T.inkSubtle }));

  const POINTS = [
    ['SESSION-START', T.neutral3, 'SUPPLIES, CANNOT BLOCK',
      'Once, before the loop begins.',
      'Inject the memory file, load project config, run startup checks.'],
    ['PRE-TOOL', T.success, 'CAN BLOCK THE CALL',
      'Before any tool executes; it sees the proposed call.',
      'A deny-list match, a permission check, a path outside the working tree.'],
    ['POST-EDIT', T.warn, 'REPORTS ONLY',
      'After a file changes. The write has already happened.',
      'Typecheck, tests, formatter. The report is appended as an observation.'],
    ['PRE-COMMIT', T.primary, 'CAN BLOCK THE COMMIT',
      'Before a commit or a pull request; usually an ordinary git hook.',
      'Tests green, no secrets, approval for anything irreversible.'],
  ];
  POINTS.forEach((p, i) => {
    const y = 100 + i * 88;
    els.push(...card(340, y, 580, 76, { spine: p[1], strokeWidth: 1.4 }));
    els.push(text(358, y + 10, p[0], { size: 13, stroke: T.ink }));
    els.push(rect(766, y + 8, 138, 20, { stroke: p[1], fill: p[1], strokeWidth: 1 }));
    els.push(text(766, y + 13, p[2], { size: 9, align: 'center', width: 138, stroke: T.onAccent }));
    els.push(text(358, y + 34, fit(p[3], 9.5, 400, 'point when'), { size: 9.5, stroke: T.inkMuted }));
    els.push(text(358, y + 52, fit(p[4], 9.5, 544, 'point eg'), { size: 9.5, stroke: T.ink }));
  });

  els.push(text(40, 456, 'Pre-tool prevents; post-edit corrects. A post-edit hook does not protect you from a bad edit,',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 478, 'it guarantees you find out about one, immediately, without relying on the model to check.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The four hook lifecycle points, marked by whether each can block',
    desc: 'A hand-drawn figure with a compact loop on the left, running reason, act, observe and '
      + 'commit, and four coloured bars marking where hooks attach. On the right, the four points '
      + 'are listed with what each is able to do. Session-start supplies but cannot block: it runs '
      + 'once before the loop begins, injecting the memory file, loading project config and running '
      + 'startup checks. Pre-tool can block the call: it runs before any tool executes and sees the '
      + 'proposed call, so it can apply a deny-list match, a permission check, or a rule about '
      + 'paths outside the working tree. Post-edit reports only: it runs after a file changes, when '
      + 'the write has already happened, so a typecheck, test run or formatter result is appended '
      + 'as an observation rather than undoing anything. Pre-commit can block the commit: it runs '
      + 'before a commit or pull request, usually as an ordinary git hook, requiring tests green, '
      + 'no secrets, and approval for anything irreversible. Captions record that pre-tool prevents '
      + 'while post-edit corrects, so a post-edit hook does not protect you from a bad edit but '
      + 'guarantees you find out about one immediately, without relying on the model to check.',
  };
}

// ---------------------------------------------------------------- diagram 2
function blockedCommand() {
  resetSeq();
  const W = 960, H = 616;

  const els = [...heading('A deny-list hook blocks a destructive command',
    'The check runs before execution, so the dangerous command never reaches the shell.')];

  // --- row A: one turn, from the proposed call to the observation ----------
  els.push(text(40, 78, 'ONE TURN, FROM CALL TO OBSERVATION',
    { size: 9, stroke: T.inkSubtle }));

  els.push(rect(40, 104, 180, 88, { stroke: T.ink, fill: T.surface, strokeWidth: 1.4 }));
  els.push(text(40, 116, 'MODEL', { size: 12, align: 'center', width: 180, stroke: T.ink }));
  els.push(text(40, 136, 'emits a tool call', { size: 9.5, align: 'center', width: 180, stroke: T.inkMuted }));
  els.push(rect(58, 158, 144, 24, { stroke: T.alert, fill: T.neutral1, strokeWidth: 1.2 }));
  els.push(text(58, 164, 'bash  rm -rf /',
    { size: 10.5, family: MONO, align: 'center', width: 144, stroke: T.alert }));

  els.push(arrow([[224, 148], [272, 148]], { stroke: T.ink, strokeWidth: 1.4 }));

  els.push(rect(276, 92, 240, 112, { stroke: T.success, fill: T.surface, strokeWidth: 1.8 }));
  els.push(text(276, 102, 'PRE-TOOL HOOK', { size: 13, align: 'center', width: 240, stroke: T.success }));
  els.push(text(276, 124, fit('five compiled patterns, case-insensitive', 9.5, 232, 'hook gloss'),
    { size: 9.5, align: 'center', width: 240, stroke: T.inkMuted }));
  els.push(rect(292, 144, 208, 24, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
  els.push(text(292, 150, fit('rm\\s+-rf\\s+(/|~|\\*)', 10, 200, 'matched pattern'),
    { size: 10, family: MONO, align: 'center', width: 208, stroke: T.ink }));
  els.push(text(276, 176, 'the first match wins, and it wins fast',
    { size: 9.5, align: 'center', width: 240, stroke: T.inkMuted }));

  els.push(arrow([[520, 124], [676, 124]],
    { stroke: T.inkSubtle, strokeWidth: 1.3, strokeStyle: 'dashed' }));
  els.push(text(530, 102, 'only without the hook', { size: 9, stroke: T.inkSubtle }));

  els.push(rect(680, 96, 240, 76, { stroke: T.inkSubtle, strokeWidth: 1.3, strokeStyle: 'dashed' }));
  els.push(text(680, 108, 'SHELL AND FILESYSTEM', { size: 12, align: 'center', width: 240, stroke: T.inkSubtle }));
  els.push(text(680, 132, 'never reached', { size: 9.5, align: 'center', width: 240, stroke: T.inkSubtle }));
  els.push(text(680, 178, 'execute() is never called', { size: 9.5, align: 'center', width: 240, stroke: T.inkSubtle }));

  els.push(arrow([[396, 206], [396, 232]], { stroke: T.alert, strokeWidth: 1.5 }));
  els.push(text(404, 210, 'match', { size: 9.5, stroke: T.alert }));

  els.push(rect(276, 236, 320, 74, { stroke: T.alert, fill: T.surface, strokeWidth: 1.8 }));
  els.push(text(276, 248, 'BLOCKED: NOT EXECUTED', { size: 13, align: 'center', width: 320, stroke: T.alert }));
  els.push(text(276, 272, fit('returns "blocked: recursive delete of a broad path"', 9.5, 312, 'verdict'),
    { size: 9.5, align: 'center', width: 320, stroke: T.inkMuted }));

  els.push(arrow([[274, 274], [140, 274], [140, 194]], { stroke: T.inkMuted, strokeWidth: 1.3 }));
  els.push(text(40, 282, 'the reason string returns to the loop', { size: 9, stroke: T.inkMuted }));
  els.push(text(40, 296, 'as the next observation', { size: 9, stroke: T.inkMuted }));

  // The post's own rule table, on the row this figure draws.
  els.push(...card(616, 200, 304, 110, { spine: T.success, strokeWidth: 1.3 }));
  els.push(text(634, 208, 'THIS GATE, AS THE RULE TABLE SCORES IT', { size: 9, stroke: T.inkSubtle }));
  const ROW = [
    ['point', 'pre-tool, inside the loop', T.ink],
    ['can it block', 'yes', T.success],
    ['on violation', 'reason returned as an observation', T.ink],
    ['cost per firing', 'microseconds (a regex)', T.ink],
  ];
  ROW.forEach((r, i) => {
    const y = 226 + i * 20;
    els.push(text(634, y + 1, r[0], { size: 8.5, stroke: T.inkSubtle }));
    els.push(text(716, y - 1, fit(r[1], 9.5, 186, 'gate row'), { size: 9.5, stroke: r[2] }));
  });

  // --- row B, left: the list itself ---------------------------------------
  els.push(...card(40, 322, 560, 250, { spine: T.alert, strokeWidth: 1.4 }));
  els.push(text(58, 332, 'THE FIVE PATTERNS THE HOOK COMPILES ONCE', { size: 10, stroke: T.alert }));
  els.push(text(58, 348, fit('from code/13-hooks, matched case-insensitively against "tool args"', 9.5, 524, 'list gloss'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(rule(58, 582, 366));
  els.push(text(58, 372, 'PATTERN', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(330, 372, 'WHAT IT STOPS', { size: 8.5, stroke: T.inkSubtle }));

  const DENY = [
    ['rm\\s+-rf\\s+(/|~|\\*)', 'recursive delete of a broad path'],
    ['git\\s+push\\s+--force', 'force-push'],
    ['DROP\\s+TABLE', 'destructive SQL'],
    [':\\(\\)\\s*\\{.*\\|:.*\\};\\s*:', 'fork bomb'],
    ['\\bmkfs\\b', 'filesystem format'],
  ];
  DENY.forEach((d, i) => {
    const y = 392 + i * 30;
    if (i) els.push(rule(58, 582, y - 9));
    els.push(text(58, y, fit(d[0], 10.5, 264, 'deny pattern'), { size: 10.5, family: MONO, stroke: T.ink }));
    els.push(text(330, y - 1, fit(d[1], 11, 252, 'deny reason'), { size: 11, stroke: i ? T.ink : T.alert }));
  });

  els.push(rule(58, 582, 532));
  els.push(text(58, 540, fit('Near misses cost more than hits: --force-with-lease is blocked here (a false', 9.5, 524, 'near miss a'),
    { size: 9.5, stroke: T.inkMuted }));
  els.push(text(58, 554, fit('positive), and rm -fr / walks past. A sixth entry, --no-verify, belongs on the list.', 9.5, 524, 'near miss b'),
    { size: 9.5, stroke: T.inkMuted }));

  // --- row B, right: what the companion actually prints --------------------
  els.push(...card(616, 322, 304, 250, { spine: T.primary, strokeWidth: 1.4 }));
  els.push(text(634, 332, 'THE COMPANION RUN, VERBATIM', { size: 10, stroke: T.primary }));
  els.push(text(634, 348, 'python -m hook_system', { size: 9.5, family: MONO, stroke: T.inkMuted }));
  els.push(rule(634, 902, 366));

  const OUT = [
    ["'ls -la'", '-> ran: bash ls -la', T.success],
    ["'rm -rf /'", '-> blocked: recursive delete of a broad path', T.alert],
    ["'git push --force'", '-> blocked: force-push', T.alert],
  ];
  OUT.forEach((o, i) => {
    const y = 382 + i * 44;
    els.push(text(634, y, fit(o[0], 10.5, 268, 'run call'), { size: 10.5, family: MONO, stroke: T.ink }));
    els.push(text(634, y + 18, fit(o[1], 9.5, 268, 'run result'), { size: 9.5, family: MONO, stroke: o[2] }));
  });

  els.push(rule(634, 902, 512));
  els.push(text(634, 520, 'AND THE EXIT CODE', { size: 8.5, stroke: T.inkSubtle }));
  els.push(text(634, 536, fit('2 blocks the call. 1 is a non-blocking', 9.5, 268, 'exit a'),
    { size: 9.5, stroke: T.ink }));
  els.push(text(634, 552, fit('error the model never sees.', 9.5, 268, 'exit b'),
    { size: 9.5, stroke: T.inkMuted }));

  els.push(text(40, 586, 'The judgement of the model is not the safety mechanism. The hook is.',
    { size: 11.5, stroke: T.ink }));

  return {
    W, H, els,
    title: 'A pre-tool deny-list hook stopping a destructive command before execution',
    desc: 'A hand-drawn figure in two tiers. The top tier follows one turn. On the left, the model '
      + 'emits a tool call carrying the command bash rm -rf slash. An arrow leads to a pre-tool '
      + 'hook, which holds five compiled patterns matched case-insensitively, shows the pattern '
      + 'that fired, and notes that the first match wins and wins fast. A dashed arrow to the '
      + 'right shows where the command would have gone only without the hook: a shell and '
      + 'filesystem box, drawn dashed, marked never reached, with a note that execute is never '
      + 'called. The match instead leads down to a box reading blocked, not executed, which returns '
      + 'the string blocked: recursive delete of a broad path, and a return path carries that '
      + 'reason string back to the loop as the next observation. A small panel scores this gate as '
      + 'the rule table does: the point is pre-tool, inside the loop; it can block, yes; on '
      + 'violation the reason is returned as an observation; and the cost per firing is '
      + 'microseconds, a regular expression. The lower tier is the list itself. On the left, the '
      + 'five patterns the hook compiles once, taken from the code companion in code slash '
      + '13-hooks and matched case-insensitively against the tool and its arguments: a recursive '
      + 'delete of a broad path, a force-push, destructive SQL, a fork bomb, and a filesystem '
      + 'format. A footnote records that near misses cost more than hits, since force-with-lease is '
      + 'blocked here as a false positive while rm -fr slash walks past, and that a sixth entry for '
      + 'no-verify belongs on the list. On the right, the companion run verbatim: ls -la ran, rm '
      + '-rf slash was blocked as a recursive delete of a broad path, and git push force was '
      + 'blocked as a force-push; with a note that an exit code of 2 blocks the call while 1 is a '
      + 'non-blocking error the model never sees. A caption records that the judgement of the model '
      + 'is not the safety mechanism; the hook is.',
  };
}

// ---------------------------------------------------------------- diagram 3
function gatesAndReports() {
  resetSeq();
  const W = 960, H = 460;

  const els = [...heading('A gate and a report are different things',
    'The two kinds of hook do different jobs, so they have different signatures and different composition rules.')];

  const col = (x, tint, headline, name, sig, returns, comp, gloss, seen) => {
    const out = card(x, 96, 430, 280, { spine: tint, strokeWidth: 1.4 });
    out.push(text(x + 18, 114, headline, { size: 10, stroke: tint }));
    out.push(text(x + 18, 132, name, { size: 15, stroke: T.ink }));
    out.push(rect(x + 18, 160, 394, 30, { stroke: T.border, fill: T.neutral1, strokeWidth: 1 }));
    out.push(text(x + 30, 168, sig, { size: 10.5, family: MONO, stroke: T.ink }));
    out.push(rule(x + 18, x + 412, 200));
    out.push(text(x + 18, 208, 'IT RETURNS', { size: 8.5, stroke: T.inkSubtle }));
    out.push(text(x + 18, 222, fit(returns, 10.5, 394, 'returns'), { size: 10.5, stroke: T.ink }));
    out.push(rule(x + 18, x + 412, 246));
    out.push(text(x + 18, 254, 'HOW THEY COMPOSE', { size: 8.5, stroke: T.inkSubtle }));
    out.push(text(x + 18, 268, fit(comp, 11.5, 394, 'comp'), { size: 11.5, stroke: tint }));
    gloss.forEach((g, i) => out.push(text(x + 18, 288 + i * 14,
      fit(g, 9, 394, 'comp gloss'), { size: 9, stroke: T.inkMuted })));
    out.push(rule(x + 18, x + 412, 322));
    out.push(text(x + 18, 330, 'WHAT THE MODEL SEES', { size: 8.5, stroke: T.inkSubtle }));
    seen.forEach((s, i) => out.push(text(x + 18, 344 + i * 14,
      fit(s, 9.5, 394, 'seen'), { size: 9.5, stroke: T.ink })));
    return out;
  };

  els.push(...col(40, T.success, 'PREVENTS', 'A pre-tool hook',
    '(tool, args) -> Decision',
    'a verdict: allow, or block with a reason',
    'in order, and the first block wins',
    ['No point asking the rest whether a command already ruled out',
     'is also acceptable, and stopping early keeps the hot path cheap.'],
    ['The reason string, in the same channel a successful',
     'call would have used. Never an exception.']));

  els.push(...col(490, T.warn, 'CORRECTS', 'A post-edit hook',
    '(path, content) -> str | None',
    'a finding: a problem, or nothing at all',
    'all of them, collecting every problem',
    ['The model is about to spend a turn responding and should see',
     'all of what broke, not only the first thing that broke.'],
    ['Every finding at once, appended as one',
     'observation. The edit itself still stands.']));

  els.push(text(40, 398,
    'Collapsing the two into one type invites code that treats a post-edit failure as a block, which the runtime cannot honour.',
    { size: 11.5, stroke: T.ink }));
  els.push(text(40, 420, 'And the reason string is part of the design: a model that cannot tell "blocked by policy" from "the tool broke"',
    { size: 11.5, stroke: T.inkMuted }));
  els.push(text(40, 440, 'will retry the blocked call, which is a doom loop manufactured by your own guardrail.',
    { size: 11.5, stroke: T.inkMuted }));

  return {
    W, H, els,
    title: 'The pre-tool gate and the post-edit report, compared by signature and composition',
    desc: 'A hand-drawn comparison of the two kinds of hook. On the left, a pre-tool hook, which '
      + 'prevents: its signature takes a tool and its arguments and returns a Decision; it returns '
      + 'a verdict, either allow or block with a reason; the hooks compose in order and the first '
      + 'block wins, because there is no point asking the rest whether a command already ruled out '
      + 'is also acceptable, and stopping early keeps the hot path cheap; and the model sees the '
      + 'reason string in the same channel a successful call would have used, never an exception. '
      + 'On the right, a post-edit hook, which corrects: its signature takes a path and the content '
      + 'and returns either a string or nothing; it returns a finding, a problem or nothing at all; '
      + 'all such hooks run and every problem is collected, because the model is about to spend a '
      + 'turn responding and should see all of what broke rather than only the first thing; and the '
      + 'model sees every finding at once, appended as one observation, while the edit itself still '
      + 'stands. Captions record that collapsing the two into one type invites code that treats a '
      + 'post-edit failure as a block, which the runtime cannot honour, and that the reason string '
      + 'is part of the design, since a model that cannot tell a policy block from a broken tool '
      + 'will retry the blocked call, which is a doom loop manufactured by your own guardrail.',
  };
}

module.exports = { hookLifecycle, blockedCommand, gatesAndReports };

if (require.main === module) {
  emit('01-hook-lifecycle', hookLifecycle());
  emit('02-blocked-command', blockedCommand());
  emit('03-gates-and-reports', gatesAndReports());
}
