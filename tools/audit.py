#!/usr/bin/env python3
"""Audit the Harness Engineering series.

Run from the repo root:

    python tools/audit.py            # everything
    python tools/audit.py 07         # one post, plus the repo-wide checks

What it checks, in the order a reader would notice a fault:

  structure   every post has index.md, frontmatter.yaml, diagrams/
  frontmatter slug matches the directory, title matches the H1, hero resolves,
              part matches the number's part, reading_time is near the word count
  prose       every image and every relative link resolves, alt text is real,
              no placeholder text, no raster references
  diagrams    the same SVG contract the Context Engineering series uses, plus an
              orphan check for figures nothing embeds
  specs       tools/scene-specs/NN.json agrees with the figures it describes:
              canvas sizes match each SVG's viewBox, a "published" scene really
              is the figure the post embeds, and the generated scene README is
              byte-current with the spec that produced it
  repo        README lists every post once, REFERENCES has a section per post,
              every code/ directory a post points at exists

Exit status is 1 if anything failed, so it can gate a commit.
"""

import io
import json
import os
import re
import sys
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

FAILS = []
WARNS = []

# CamelCase identifiers a post may legitimately name without this repo defining
# them: they belong to another product's API. Keep this list short — every entry
# is a claim the audit stops checking.
EXTERNAL_SYMBOLS = {
    'PreToolUse', 'PostToolUse', 'SessionStart', 'PreCompact', 'SubagentStop',
    'UserPromptSubmit', 'LangGraph', 'AgentSDK',
    # Python builtins a post may legitimately name: they are never `class` or
    # `def` lines in a companion, so the definition scan cannot find them.
    'FileExistsError', 'FileNotFoundError', 'OSError', 'ValueError',
    'TypeError', 'SyntaxError', 'TimeoutError',
}


def fail(where, msg):
    FAILS.append('%s: %s' % (where, msg))


def warn(where, msg):
    WARNS.append('%s: %s' % (where, msg))


def read(p):
    return io.open(p, encoding='utf-8').read()


def est_minutes(body):
    """Reading time, one formula for the whole series.

    Prose at 200 words per minute, fenced code at 25 lines per minute because it
    is read rather than skimmed, and half a minute per figure. Assigning these
    by hand is what produced a series claiming a uniform 12-15 minutes for posts
    that ranged from 6 to 16.
    """
    prose = re.sub(r'```.*?```', '', body, flags=re.S)
    code_lines = sum(len(b.splitlines()) for b in re.findall(r'```.*?```', body, re.S))
    figures = len(re.findall(r'!\[', body))
    return max(1, int(round(len(prose.split()) / 200.0
                            + code_lines / 25.0
                            + figures * 0.5)))


# The part each post number belongs to, from HARNESS-PLAN.md section 3.
PARTS = {}
for lo, hi, name in [
    (1, 5, 'Part I — Foundations'),
    (6, 10, 'Part II — Core Primitives'),
    (11, 15, 'Part III — Control & Reliability'),
    (16, 20, 'Part IV — Scale & Orchestration'),
    (21, 26, 'Part V — Production & Builds'),
]:
    for n in range(lo, hi + 1):
        PARTS[n] = name

POSTS = sorted(glob.glob('posts/*/'))
ONLY = sys.argv[1] if len(sys.argv) > 1 else None
if ONLY:
    POSTS = [p for p in POSTS if os.path.basename(p.rstrip('/\\')).startswith(ONLY)]
    if not POSTS:
        print('no post matches %r' % ONLY)
        sys.exit(2)


def frontmatter(path):
    """A deliberately small YAML reader: these files are flat key/value only."""
    out = {}
    for line in read(path).splitlines():
        m = re.match(r'^([a-z_]+):\s*(.*)$', line)
        if m:
            v = m.group(2).strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            out[m.group(1)] = v
    return out


# --------------------------------------------------------------- posts
seen_dates = []
for d in POSTS:
    slug = os.path.basename(d.rstrip('/\\'))
    num = int(slug[:2])
    idx = os.path.join(d, 'index.md')
    fmp = os.path.join(d, 'frontmatter.yaml')

    if not os.path.exists(idx):
        fail(slug, 'no index.md')
        continue
    if not os.path.exists(fmp):
        fail(slug, 'no frontmatter.yaml')
        continue

    body = read(idx)
    fm = frontmatter(fmp)
    words = len(body.split())

    # -- frontmatter ----------------------------------------------------
    for key in ('slug', 'title', 'date', 'tags', 'hero', 'reading_time', 'part'):
        if key not in fm:
            fail(slug, 'frontmatter missing %s' % key)

    if fm.get('slug') and fm['slug'] != slug:
        fail(slug, 'frontmatter slug is %r, directory is %r' % (fm['slug'], slug))

    if fm.get('part') and fm['part'] != PARTS[num]:
        fail(slug, 'part is %r, should be %r' % (fm['part'], PARTS[num]))

    if fm.get('date'):
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', fm['date']):
            fail(slug, 'date %r is not YYYY-MM-DD' % fm['date'])
        else:
            seen_dates.append((num, fm['date']))

    if fm.get('reading_time'):
        try:
            rt = int(fm['reading_time'])
            if abs(rt - est_minutes(body)) > 2:
                fail(slug, 'reading_time %d, but the formula gives %d'
                     % (rt, est_minutes(body)))
        except ValueError:
            fail(slug, 'reading_time %r is not a number' % fm['reading_time'])

    # -- the H1 must be the title ---------------------------------------
    m = re.search(r'^#\s+(.+)$', body, re.M)
    if not m:
        fail(slug, 'no H1')
    elif fm.get('title') and m.group(1).strip() != fm['title'].strip():
        fail(slug, 'H1 %r does not match frontmatter title %r'
             % (m.group(1).strip(), fm['title']))

    # -- the shape every post in this series shares ---------------------
    for needle, what in [
        ('**TL;DR.**', 'TL;DR block'),
        ('## Common pitfalls', 'Common pitfalls section'),
        ('## Further reading', 'Further reading section'),
        ('## What to read next', 'What to read next section'),
    ]:
        if needle not in body:
            fail(slug, 'missing %s' % what)

    if 'After reading this you will be able to' not in body:
        warn(slug, 'no learning-objectives list in the TL;DR block')

    # -- placeholders ----------------------------------------------------
    for bad in ('TODO', 'TKTK', 'FIXME', 'XXX', 'lorem ipsum', 'TBD'):
        if bad in body:
            fail(slug, 'placeholder text %r' % bad)

    # -- images ----------------------------------------------------------
    for alt, tgt in re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', body):
        if tgt.startswith('http'):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(d, tgt))):
            fail(slug, 'image does not resolve: %s' % tgt)
        if len(alt) < 20:
            fail(slug, 'thin alt text (%d chars) on %s' % (len(alt), tgt))
        if re.search(r'\.(png|jpg|jpeg|gif|webp)$', tgt, re.I):
            fail(slug, 'raster image reference: %s' % tgt)

    # -- links -----------------------------------------------------------
    for text, tgt in re.findall(r'(?<!!)\[([^\]]*)\]\(([^)]+)\)', body):
        if tgt.startswith('http') or tgt.startswith('#') or tgt.startswith('mailto:'):
            continue
        clean = tgt.split('#')[0]
        if not clean:
            continue
        if not os.path.exists(os.path.normpath(os.path.join(d, clean))):
            fail(slug, 'link does not resolve: %s' % tgt)

    # -- hero ------------------------------------------------------------
    if fm.get('hero'):
        hero = os.path.normpath(os.path.join(d, fm['hero']))
        if not os.path.exists(hero):
            fail(slug, 'hero does not resolve: %s' % fm['hero'])
        elif os.path.basename(fm['hero']) not in body:
            warn(slug, 'hero %s is never embedded in the prose' % fm['hero'])

    # -- section cross-references point at sections that exist ------------
    # Renumbering a post is the easiest way to leave a dangling "see §5", and
    # nothing else in the toolchain would notice.
    sections = set(int(n) for n in re.findall(r'^##\s+(\d+)\.', body, re.M))
    for ref in set(re.findall(r'§(\d+)', body)):
        if int(ref) not in sections:
            fail(slug, 'refers to §%s, but the post has sections %s'
                 % (ref, sorted(sections) or 'none'))

    # -- post cross-references stay in range -----------------------------
    for n in re.findall(r'\bPost (\d{2})\b', body):
        if not (1 <= int(n) <= 26):
            fail(slug, 'reference to Post %s, which is outside 01-26' % n)

    # -- diagrams --------------------------------------------------------
    svgs = sorted(glob.glob(os.path.join(d, 'diagrams', '*.svg')))
    if not svgs:
        fail(slug, 'no diagrams')
    for f in svgs:
        s = read(f)
        n = os.path.basename(f)
        w = '%s/%s' % (slug, n)
        stripped = re.sub(r'<style>.*?</style>', '', s, flags=re.S)

        if not s.startswith('<?xml'):
            fail(w, 'missing XML declaration')
        if 'role="img"' not in s:
            fail(w, 'missing role="img"')
        if not re.search(r'<title id="t">.{20,}?</title>', s, re.S):
            fail(w, 'missing or short <title>')
        dm = re.search(r'<desc id="d">(.*?)</desc>', s, re.S)
        if not dm or len(dm.group(1)) < 200:
            fail(w, 'missing or short <desc>')
        if not re.search(r'viewBox="0 0 [\d.]+ [\d.]+"', s):
            fail(w, 'no viewBox')
        if re.search(r'<svg[^>]*\swidth=', s):
            fail(w, 'width on the root <svg>')
        if re.search(r'<svg[^>]*\sheight=', s):
            fail(w, 'height on the root <svg>')
        hexes = re.findall(
            r'(?:fill|stroke|stop-color|flood-color)="(#[0-9A-Fa-f]{3,8})"', stripped)
        if hexes:
            fail(w, 'raw hex in a paint attribute: %s' % ','.join(sorted(set(hexes))))
        if 'prefers-color-scheme:dark' not in s:
            fail(w, 'no dark-mode block')
        if [c for c in stripped if ord(c) >= 0x1F000 or 0x2600 <= ord(c) <= 0x27BF]:
            fail(w, 'emoji glyph')
        if n not in body and n not in read(fmp):
            warn(w, 'published but nothing references it')

    # -- code companions -------------------------------------------------
    # A post that names a file or a class in its companion is making a claim
    # that goes stale the moment the code is refactored. Check it.
    refs = set(re.findall(r'\.\./\.\./code/([a-z0-9-]+)', body))
    for ref in refs:
        if not os.path.isdir(os.path.join('code', ref)):
            fail(slug, 'points at code/%s, which does not exist' % ref)

    if refs:
        pyfiles, symbols = set(), set()
        for ref in refs:
            for f in glob.glob(os.path.join('code', ref, '**', '*.py'), recursive=True):
                pyfiles.add(os.path.basename(f))
                src = read(f)
                symbols.update(re.findall(r'^\s*(?:class|def)\s+(\w+)', src, re.M))

        for name in set(re.findall(r'`([a-z_][a-z0-9_]*\.py)`', body)):
            if name not in pyfiles:
                fail(slug, 'names `%s`, which is not in %s'
                     % (name, ' or '.join('code/' + r for r in sorted(refs))))

        # CamelCase in backticks is a class the post is pointing the reader at.
        for name in set(re.findall(r'`([A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9]*)`', body)):
            if name not in symbols and name not in EXTERNAL_SYMBOLS:
                warn(slug, 'names `%s`, which is not defined in %s'
                     % (name, ' or '.join('code/' + r for r in sorted(refs))))

        # A shell command a reader will paste has to be the real one.
        for cmd in set(re.findall(r'`(python -m [^`]+)`', body)):
            if 'pytest' in cmd and not glob.glob(
                    os.path.join('code', sorted(refs)[0], 'tests', 'test_*.py')):
                fail(slug, 'tells the reader to run %r but there are no tests' % cmd)

# -- dates run forward ---------------------------------------------------
if not ONLY:
    ordered = sorted(seen_dates)
    for (n1, d1), (n2, d2) in zip(ordered, ordered[1:]):
        if d2 < d1:
            fail('dates', 'post %02d is dated %s, before post %02d on %s'
                 % (n2, d2, n1, d1))

# --------------------------------------------------------------- scene specs
# tools/scene-specs/NN.json is hand-written metadata that mk_scene_readme.py turns
# into posts/NN-slug/diagrams/excalidraw/README.md. Nothing in the build reads it,
# so for a long time nothing forced it to agree with the figures it describes, and
# it drifted: 54 of 78 entries carried a pre-density canvas size and a status of
# "alternate" left over from when the hand-drawn render sat beside a clean vector
# rather than being the published figure. Those 26 READMEs shipped that stale
# description to readers. These checks make that class of drift a build failure.
SPECS = sorted(glob.glob('tools/scene-specs/*.json'))
if ONLY:
    SPECS = [p for p in SPECS if os.path.basename(p)[:2] == ONLY]

for sp in SPECS:
    where = sp
    try:
        spec = json.loads(read(sp))
    except ValueError as e:
        fail(where, 'is not valid JSON: %s' % e)
        continue

    slug = spec.get('slug', '')
    pdir = os.path.join('posts', slug)
    if not os.path.isdir(pdir):
        fail(where, 'slug %r is not a post directory' % slug)
        continue
    if spec.get('num') != os.path.basename(sp)[:2]:
        fail(where, 'num %r does not match the filename' % spec.get('num'))

    names = []
    for entry in spec.get('scenes', []):
        if len(entry) != 4:
            fail(where, 'scene entry is not [name, canvas, status, caption]: %r' % (entry,))
            continue
        name, canvas, status, _caption = entry
        names.append(name)

        scene_svg = os.path.join(pdir, 'diagrams', 'excalidraw', name + '.svg')
        scene_json = os.path.join(pdir, 'diagrams', 'excalidraw', name + '.excalidraw')
        if not os.path.exists(scene_svg):
            fail(where, '%s: no rendered scene at %s' % (name, scene_svg))
            continue
        if not os.path.exists(scene_json):
            fail(where, '%s: no editable scene at %s' % (name, scene_json))

        # The recorded canvas must be the canvas the file actually declares.
        m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', read(scene_svg))
        if not m:
            fail(where, '%s: rendered scene has no viewBox' % name)
        else:
            real = '%g x %g' % (float(m.group(1)), float(m.group(2)))
            if real.replace(' ', '') != str(canvas).replace(' ', ''):
                fail(where, '%s: spec records canvas %r, the SVG declares %r'
                            % (name, canvas, real))

        # "published" must mean the figure one directory up IS this render.
        pub = os.path.join(pdir, 'diagrams', name + '.svg')
        if status == 'published':
            if not os.path.exists(pub):
                fail(where, '%s: marked published, but %s does not exist' % (name, pub))
            elif read(pub) != read(scene_svg):
                fail(where, '%s: marked published, but the figure differs from the '
                            'scene render — run `npm run publish`' % name)
        elif status == 'alternate':
            if os.path.exists(pub) and read(pub) == read(scene_svg):
                fail(where, '%s: marked alternate, but the published figure IS this '
                            'render — the spec is stale' % name)
        else:
            fail(where, '%s: status %r is neither published nor alternate' % (name, status))

    if spec.get('example') not in names:
        fail(where, 'example %r is not one of this post\'s scenes' % spec.get('example'))

    # A lede that still counts alternates, or still says a scene sits beside a
    # clean vector, is describing the old publish policy. Past-tense history is
    # fine and deliberately not matched: post 01 and post 13 both say what their
    # figures *replaced*, which is true and worth saying.
    STALE_PHRASES = (
        'alternate', 'alternates',
        'sits beside a clean vector', 'sit beside a clean vector',
        'the clean vectors stay', 'nothing published',
    )
    lede = spec.get('lede', '').lower()
    has_alt = any(e[2] == 'alternate' for e in spec.get('scenes', []) if len(e) == 4)
    if not has_alt:
        for phrase in STALE_PHRASES:
            if re.search(r'\b%s\b' % re.escape(phrase), lede):
                fail(where, 'lede still says %r, but no scene is an alternate; the '
                            'lede is describing the old publish policy' % phrase)
                break

    # The README is a derived artefact. If regenerating it would change a byte,
    # what is on disk is not what the spec says, and a reader gets the older one.
    readme_path = os.path.join(pdir, 'diagrams', 'excalidraw', 'README.md')
    if not os.path.exists(readme_path):
        fail(where, 'no generated README at %s' % readme_path)
    else:
        try:
            sys.path.insert(0, os.path.join(ROOT, 'tools'))
            import mk_scene_readme
            rendered = mk_scene_readme.TEMPLATE.format(
                num=spec['num'], slug=spec['slug'],
                count_word=mk_scene_readme.COUNT[len(spec['scenes'])],
                lede=spec['lede'],
                rows='\n'.join('| `%s` | %s | %s | %s |' % tuple(s) for s in spec['scenes']),
                example=spec['example'],
                notes='\n'.join(spec['notes']),
            )
            if read(readme_path).replace('\r\n', '\n') != rendered:
                fail(where, 'the generated README is out of date; run '
                            '`python tools/mk_scene_readme.py %s`' % sp)
        except Exception as e:                       # noqa: BLE001 - report, do not crash
            fail(where, 'could not regenerate the README to compare: %s' % e)

for d in POSTS:
    slug = os.path.basename(d.rstrip('/\\'))
    if not os.path.exists(os.path.join('tools', 'scene-specs', slug[:2] + '.json')):
        fail(d, 'has no tools/scene-specs/%s.json' % slug[:2])

# --------------------------------------------------------------- repo-wide
readme = read('README.md')
refs = read('REFERENCES.md')
all_slugs = [os.path.basename(p.rstrip('/\\')) for p in sorted(glob.glob('posts/*/'))]

for slug in all_slugs:
    n = int(slug[:2])
    if 'posts/%s/index.md' % slug not in readme:
        fail('README.md', 'does not link posts/%s/' % slug)
    if not re.search(r'^## Post %02d\b' % n, refs, re.M):
        fail('REFERENCES.md', 'no "## Post %02d" section' % n)

for tgt in set(re.findall(r'\]\((posts/[^)#]+)\)', readme)):
    if not os.path.exists(tgt):
        fail('README.md', 'link does not resolve: %s' % tgt)
for tgt in set(re.findall(r'\]\((code/[^)#]+)\)', readme)):
    if not os.path.exists(tgt):
        fail('README.md', 'link does not resolve: %s' % tgt)

for d in sorted(glob.glob('code/*/')):
    if not glob.glob(os.path.join(d, 'README*')):
        warn(d, 'code companion has no README')

# --------------------------------------------------------------- report
print('=== HARNESS ENGINEERING AUDIT ===')
print('  %d post(s) checked' % len(POSTS))
if WARNS:
    print()
    print('  %d WARNING(S)' % len(WARNS))
    for w in WARNS:
        print('    ~ ' + w)
print()
if FAILS:
    print('  %d FAILURE(S)' % len(FAILS))
    for f in FAILS:
        print('    - ' + f)
    sys.exit(1)
print('  all checks passed')
