# SPDX-License-Identifier: Apache-2.0
"""Scope C1: PR3633's two supplier words (PR3605's staged 644/660 width reduction) through this contributor's merged
PR3053 word lineage, with no code of PR3633, PR3605, PR3630, PR3624 or PR3626.

Inputs (all read with plain `git -C <repo> show <commit>:<path>`, then pinned by git blob id and sha256; nothing of a
PR is imported or executed):
  PR3633 head 72c268f1  research/staged-width-t488/supplier3605/STAGED644-660-{base,extra}.json.gz   (the words)
                        research/staged-width-t488/owners/SOURCE-PINS.json      (its native_source_word_sha256 pins)
                        research/staged-width-t488/owners/PROVIDERS.json        (widths used by its owner journal)
  PR3605 head 3efbb5de  research/staged-644-660-width-reduction/STAGED644-660-*.json.gz  (byte identity only)
  main 20ecf289         research/rank7-coupled-586-588-carrier-fold/edits/FINAL-WORD-*.json.gz  (PR3133 parents;
                        byte-identical copies at research/coupled-carrier-cap740/words/*.json.gz)
                        research/coupled-carrier-cap740/vendor/PR3133-PROVIDERS.json

audit_word(tag, raw, ctx) is the per-word main check (positive run and every negative control):
  staged.pin            sha256(raw) is the pinned value
  vendored word_pipeline (audit_words, PR3053): parse + 36 initial corrections, warp algebra, literal frame recount,
                        words.counts, words.report_fields, words.declared, forward and dual free-operator replay
                        through cleanup, the own exact tracker, words.cleanup (literal inverse-reverse), words.buffers
  staged.providers      recount helper widths == PR3633 PROVIDERS.json entry (base->gauge44, extra->extra)
  staged.providers_paid recount paid profile == the same entry's actual_paid_profile
  staged.pr3133_widths  the widths differ from the parent's PR3133-PROVIDERS entry exactly at helper indices 389, 397
                        (8 -> 7)
  staged.registers      those indices are the live helper registers PR3605 names (644 and 660; ctx['staged_regs'])
  staged.parent_diff.*  localisation against the PR3133 parent word (one rule id per fact):
     .keys / .replace / .warps   same top-level keys; no unequal replace block; warps change only together with B
     .warp_record / .warp_alignment  every warp record unchanged except its B position, which follows the B alignment
     .sections          section-level counts == PR3605's published edit (B: 8 deleted, 4 inserted; cleanup: 4
                        inserted; restore: 1 replaced; report: profile/inventory; start_extra: 644/660; warps: 72
                        moved); every other section unchanged
     .deleted           the 8 deleted B items are helper-to-target writes, 4 from 644 and 4 from 660
     .inserted          the 4 inserted B items are helper-to-helper donor releases, 2 from 644 and 2 from 660
     .cleanup_pairs     the 4 cleanup inserts carry the same (target, source) pairs as the B inserts
     .restore           the replaced restore item is 210 and only its frame changes, to FULL
     .start_extra       start_extra of 644/660 goes from [30] to [429, 30]
Expected counts (words.counts) and why:
  live 632 = 2*112 + 408; helpers 408 (PR3605 README "all 408 helper roles"; PR3633's owner audit gates R==408);
  buffers 91 (PR3605 README "91 private buffers"; PR3633 gates len(zero_buffers)==91); warps 72 and corrections 36
  (the lineage's published EXPECT_COUNTS, main research/t74-3015-restore-edit-audit/verify.py, and the parent word
  recounted by the same function); a_prelude_events and the section lengths = the parent's, except B -4 and
  cleanup +4 (PR3605: eight writes replaced by four releases whose inverses enter the cleanup).
Declared profile/inventory (words.declared): staged {1:2439,2:726,3:224,4:102,5:20,8:8} /
  {4:26,5:2,6:18,7:52,8:97,9:213}; parent {1:2433,2:724,3:228,4:102,5:20,8:8} / {4:26,5:2,6:18,7:50,8:99,9:213}
  (PR3605 README; the parent profile also equals PR3133-PROVIDERS actual_paid_profile).
Negative controls go through audit_word, each on both words, and are counted by audit_lib.expect (exact rule id, and
stage for replays); every rule above has at least one control that only it can reject (the parent_diff facts by
parent mutants that keep the section counts, so each reaches its own fact).  staged.registers is controlled with a
mismatched declared register pair (the data side, P['live'], is the vendored parser's; a relabelled-word control was
not built).  Not mutation-controlled: the fail-closed git/pin reads of fixed inputs (staged.git, staged.pin,
staged.pr3605_identity) and run()'s parent positive control (staged.parent_counts, staged.parent_providers), which
must pass on the pinned bytes.  Standard library only.
"""
import copy
import difflib
import gzip
import json
import os
import subprocess
import sys
import time
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_VENDOR = os.path.join(_HERE, 'vendor', 'pr3053')
if _VENDOR not in sys.path:
    sys.path.insert(0, _VENDOR)
import audit_common as AC   # noqa: E402
import audit_lib as AL      # noqa: E402
import audit_words as AW    # noqa: E402

REPO = os.path.dirname(os.path.dirname(_HERE))
MAIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
PR3633 = '72c268f113368ea0387d188225e3f81ba6d6ef73'
PR3605 = '3efbb5de06a49ffeea6684482f2d3fe48cdca3fb'
V = AL.V
FULL = list(AL.FULL_LIST)
TAGS = ('base', 'extra')
PROVIDER = dict(base='gauge44', extra='extra')

# (commit, path, git blob, sha256)
STAGED = dict(
    base=(PR3633, 'research/staged-width-t488/supplier3605/STAGED644-660-base.json.gz',
          'dc6d321b1e8e2a837a1ff7bb60e8f8f78d043db5', '735c540b1fe29d0ceeb4d2f304ec941e5f2bd3bc92bafc8cce2b4f9a67a3b653'),
    extra=(PR3633, 'research/staged-width-t488/supplier3605/STAGED644-660-extra.json.gz',
           '78e7b2bb0653c8dcc0133980a19dd9d97ebdb67e', '886338fc32da14f3389a82c8120a1bcf9c5e2f0ec3e9b2d377fdae809e1d977f'))
PR3605_PATH = 'research/staged-644-660-width-reduction/STAGED644-660-%s.json.gz'
PARENT = dict(
    base=(MAIN, 'research/rank7-coupled-586-588-carrier-fold/edits/FINAL-WORD-base.json.gz',
          'cb4cc24a4545944627ad595c0c5080196952b9f0', '300a9b8ad1d554f0e6f84f43f3f5fd870a5b4e5f81ad856900b6e8999684892e'),
    extra=(MAIN, 'research/rank7-coupled-586-588-carrier-fold/edits/FINAL-WORD-extra.json.gz',
           'decc8f26d8aab108baf75f0d8b2d1012eb06d076', '495d030f1e03b90e954dad3043994f03293d41b9ed220a3beaef849df435d3f0'))
PARENT_COPY = 'research/coupled-carrier-cap740/words/%s.json.gz'
SOURCE_PINS = (PR3633, 'research/staged-width-t488/owners/SOURCE-PINS.json', '5aa0ee4cb46308e674c5e1cedaa7eefc7bac59bd',
               '7dec42af587af3b7ae66d4fdf3d0c6157f9c85eb744edec66fa266f294378e5e')
PROVIDERS = (PR3633, 'research/staged-width-t488/owners/PROVIDERS.json', 'f321d4185339244b8b004326af70e653e611d84a',
             'd96f2798024ab83edbb8848b62c425992aec182f1f24ef46bb8286dd390618c2')
PR3133_PROVIDERS = (MAIN, 'research/coupled-carrier-cap740/vendor/PR3133-PROVIDERS.json', None,
                    '52eb0d85caa7b2d4a93acdf5011f52b793f61ddca86235fb03cd9a09397ad4cd')

DECLARED = dict(local_profile={1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8},
                width_inventory={4: 26, 5: 2, 6: 18, 7: 52, 8: 97, 9: 213})
DECLARED_PARENT = dict(local_profile={1: 2433, 2: 724, 3: 228, 4: 102, 5: 20, 8: 8},
                       width_inventory={4: 26, 5: 2, 6: 18, 7: 50, 8: 99, 9: 213})
EXPECT_LINEAGE = dict(live=2 * V + 408, helpers=408, buffers=91, warps=72, corrections=36)
SECTION_DELTA = dict(B=-4, cleanup=4)
WIDTH_CHANGES = [(389, 8, 7), (397, 8, 7)]
STAGED_REGS = (644, 660)
LOCALISATION = dict(
    B=dict(deleted=8, inserted=4, replaced=0),
    cleanup=dict(deleted=0, inserted=4, replaced=0),
    restore=dict(deleted=0, inserted=0, replaced=1),
    report=dict(keys=['local_profile', 'width_inventory']),
    start_extra=dict(keys=['644', '660']),
    warps=dict(position_only=72))
STAGE_FWD = 'forward replay, before cleanup'
STAGE_DUAL_BUF = 'dual replay, buffers after cleanup'
STAGE_FWD_FINAL = 'forward replay, final map after cleanup'


# ------------------------------------------------------------------------------------------------- inputs ---
def git(*args):
    p = subprocess.run(['git', '-C', REPO] + list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=AC.git_env())
    AC.need(p.returncode == 0, 'staged.git: git %s failed: %s' % (' '.join(args)[:120], p.stderr.decode()[:200]))
    return p.stdout


def read_pinned(spec):
    """Bytes of commit:path, checked against the pinned git blob id and sha256 (None = not pinned)."""
    commit, path, blob, sha = spec
    data = git('show', '%s:%s' % (commit, path))
    AC.need(blob is None or AC.git_blob_id(data) == blob, 'staged.pin: %s blob %s != %s'
            % (path, AC.git_blob_id(data), blob))
    AC.need(sha is None or AC.sha256(data) == sha, 'staged.pin: %s sha256 %s != %s' % (path, AC.sha256(data), sha))
    return data


def gz_json(raw):
    return json.loads(gzip.decompress(raw).decode('utf-8'))


def gz_bytes(w):
    return gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0)


def counts_of(P, w):
    c = AW.counts(P, w)
    return dict((k, c[k]) for k in sorted(EXPECT_LINEAGE)), c


# ------------------------------------------------------------------------------------------ localisation ---
def list_diff(a, b):
    sm = difflib.SequenceMatcher(None, [json.dumps(x) for x in a], [json.dumps(x) for x in b], autojunk=False)
    out = dict(deleted=0, inserted=0, replaced=0)
    ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
    for tag, i1, i2, j1, j2 in ops:
        if tag == 'delete':
            out['deleted'] += i2 - i1
        elif tag == 'insert':
            out['inserted'] += j2 - j1
        else:
            AC.need(i2 - i1 == j2 - j1, 'staged.parent_diff.replace: unequal replace block %r' % ((tag, i1, i2, j1, j2),))
            out['replaced'] += i2 - i1
    return out, ops, sm


def b_position_map(sm, n_old, n_new):
    """Parent B position -> staged B position for every position inside an equal block (and the end)."""
    m = {n_old: n_new}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                m[i1 + k] = j1 + k
    return m


def localise(parent, w):
    """Section-level differences parent -> staged word (counts only), with the per-item facts of PR3605's edit."""
    loc, facts = {}, {}
    AC.need(sorted(parent) == sorted(w), 'staged.parent_diff.keys: key sets differ %r' % sorted(set(parent) ^ set(w)))
    smB = None
    for k in sorted(w):
        a, b = parent[k], w[k]
        if a == b:
            continue
        if k == 'warps':
            continue
        if isinstance(a, list):
            loc[k], ops, sm = list_diff(a, b)
            if k == 'B':
                smB, opsB = sm, ops
            facts[k] = ops
        elif isinstance(a, dict):
            loc[k] = dict(keys=sorted(x for x in set(a) | set(b) if a.get(x) != b.get(x)))
        else:
            loc[k] = dict(scalar=[a, b])
    if parent['warps'] != w['warps']:
        AC.need(smB is not None and len(parent['warps']) == len(w['warps']), 'staged.parent_diff.warps: warps changed without B')
        pos = b_position_map(smB, len(parent['B']), len(w['B']))
        moved = 0
        for ra, rb in zip(parent['warps'], w['warps']):
            AC.need(ra[1:] == rb[1:], 'staged.parent_diff.warp_record: a warp record changed beyond its position')
            AC.need(ra[0] in pos and pos[ra[0]] == rb[0],
                    'staged.parent_diff.warp_alignment: warp at parent B position %d does not follow the B alignment' % ra[0])
            moved += ra[0] != rb[0]
        loc['warps'] = dict(position_only=moved)
    AC.need(loc == LOCALISATION, 'staged.parent_diff.sections: %r != %r' % (loc, LOCALISATION))
    # per-item facts of the published edit
    dele = [g for t, i1, i2, _, _ in facts['B'] if t == 'delete' for g in parent['B'][i1:i2]]
    ins = [g for t, _, _, j1, j2 in facts['B'] if t == 'insert' for g in w['B'][j1:j2]]
    cins = [g for t, _, _, j1, j2 in facts['cleanup'] if t == 'insert' for g in w['cleanup'][j1:j2]]
    AC.need(all(g[0] == 'add' and V <= g[1] < 2 * V and g[2] in STAGED_REGS for g in dele)
            and Counter(g[2] for g in dele) == Counter({644: 4, 660: 4}),
            'staged.parent_diff.deleted: deleted B items are not 4+4 helper-to-target writes of 644/660')
    AC.need(all(g[0] == 'add' and g[1] >= 2 * V and g[2] in STAGED_REGS for g in ins)
            and Counter(g[2] for g in ins) == Counter({644: 2, 660: 2}),
            'staged.parent_diff.inserted: inserted B items are not 2+2 donor releases of 644/660')
    AC.need(sorted((g[1], g[2]) for g in cins) == sorted((g[1], g[2]) for g in ins),
            'staged.parent_diff.cleanup_pairs: cleanup inserts are not the four inserted (target, source) pairs')
    (_, i1, _, _, _), = facts['restore']
    ra, rb = parent['restore'][i1], w['restore'][i1]
    AC.need(i1 == 210 and ra[:-1] == rb[:-1] and rb[-1] == FULL and ra[-1] != FULL,
            'staged.parent_diff.restore: restore change is not item 210 frame -> FULL')
    AC.need(all(parent['start_extra'][str(r)] == [30] and w['start_extra'][str(r)] == [429, 30] for r in STAGED_REGS),
            'staged.parent_diff.start_extra: start_extra of 644/660 is not [30] -> [429, 30]')
    return dict(sections=loc, b_deleted_sources=dict(Counter(g[2] for g in dele)),
                b_inserted=[g[:3] for g in ins], restore_index=i1, unchanged_sections=sorted(k for k in w
                                                                                            if parent[k] == w[k]))


# ---------------------------------------------------------------------------------------- per-word check ---
def audit_word(tag, raw, ctx):
    """The per-word main check (see module docstring).  Returns (record, helper widths)."""
    AC.need(AC.sha256(raw) == ctx['pins'][tag], 'staged.pin: %s word sha256 %s' % (tag, AC.sha256(raw)))
    w = gz_json(raw)
    rec, P, fr = AW.word_pipeline(w, ctx['declared'], ctx['expect'][tag])
    widths = list(fr['helper_widths'])
    pid = PROVIDER[tag]
    prov = ctx['providers'][pid]
    AC.need(widths == prov['widths'], 'staged.providers: %s recount widths != PROVIDERS.json[%s] (first diff %r)'
            % (tag, pid, next(((i, a, b) for i, (a, b) in enumerate(zip(widths, prov['widths'])) if a != b), None)))
    AC.need(fr['paid'] == AL.intkeys(prov['actual_paid_profile']),
            'staged.providers_paid: %s recount paid profile %r != PROVIDERS.json[%s]' % (tag, fr['paid'], pid))
    old = ctx['pr3133'][pid]['widths']
    diffs = [(i, a, b) for i, (a, b) in enumerate(zip(old, widths)) if a != b]
    AC.need(len(old) == len(widths) and diffs == WIDTH_CHANGES,
            'staged.pr3133_widths: %s diffs vs PR3133-PROVIDERS %r != %r' % (tag, diffs, WIDTH_CHANGES))
    helpers = [r for r in P['live'] if r >= 2 * V]
    AC.need(tuple(helpers[i] for i, _, _ in diffs) == tuple(ctx['staged_regs']),
            'staged.registers: changed indices name registers %r, declared %r'
            % ([helpers[i] for i, _, _ in diffs], ctx['staged_regs']))
    loc = localise(ctx['parents'][tag], w)
    rec = dict(rec, sha256=AC.sha256(raw), provider=pid, pr3133_width_changes=[list(d) for d in diffs],
               changed_registers=list(STAGED_REGS), localisation=loc)
    return rec, widths


# -------------------------------------------------------------------------------------------- controls ---
def word_controls(tag, raw, ctx, out):
    T = '[%s] ' % tag
    w0 = gz_json(raw)

    def through(m, ctx2=None, repin=True):
        """Run the mutant word through audit_word; repin=True gives it a matching pin, so only the deeper checks can
        reject it."""
        r = gz_bytes(m) if isinstance(m, dict) else m
        c = dict(ctx2 or ctx)
        if repin:
            c['pins'] = dict(c['pins'], **{tag: AC.sha256(r)})
        return lambda: audit_word(tag, r, c)

    def expect_count(section, d):
        c2 = dict(ctx, expect=dict(ctx['expect']))
        c2['expect'][tag] = dict(ctx['expect'][tag], sections=dict(ctx['expect'][tag]['sections']))
        c2['expect'][tag]['sections'][section] += d
        return c2

    def with_parent(par):
        return dict(ctx, parents=dict(ctx['parents'], **{tag: par}))

    bad = bytearray(raw)
    bad[len(bad) // 2] ^= 1
    AL.expect(out, T + 'one byte of the gzip stream flipped, pin kept', 'staged.pin', through(bytes(bad), repin=False))

    m = AL.mutant(w0)
    j = next(i for i, g in enumerate(m['B']) if g[0] == 'add' and g[2] in STAGED_REGS and g[1] >= 2 * V)
    m['B'][j][3] = -m['B'][j][3]
    AL.expect(out, T + 'coefficient of the first donor release B[%d] flipped' % j, 'wc.replay', through(m),
              stage=STAGE_FWD)

    m = AL.mutant(w0)
    del m['cleanup'][0]
    AL.expect(out, T + 'first cleanup item deleted, expected cleanup count lowered to match', 'wc.replay',
              through(m, expect_count('cleanup', -1)), stage=STAGE_FWD_FINAL)

    m = AL.mutant(w0)
    cl = m['cleanup']
    i = next(k for k in range(len(cl) - 1) if cl[k][0] == cl[k + 1][0] == 'add'
             and not {cl[k][1], cl[k][2]} & {cl[k + 1][1], cl[k + 1][2]})
    cl[i], cl[i + 1] = cl[i + 1], cl[i]
    P = AL.parse_word(m)
    AL.replay(P, False)
    AL.replay(P, True)
    AW.tracker_check(AW.track(m))
    AL.expect(out, T + 'commuting cleanup items %d/%d swapped (both replays and the tracker accept)' % (i, i + 1),
              'words.cleanup', through(m), replays_and_tracker_accept=True)

    m = AL.mutant(w0)
    k = next(k for k in sorted(m['helper_final'], key=int) if len(m['helper_final'][k]) < len(FULL))
    m['helper_final'][k] = list(FULL)
    AL.forge(m)
    AL.expect(out, T + 'helper_final frame of %s raised to FULL, report forged' % k, 'words.declared', through(m))

    m = AL.mutant(w0)
    restored = set(int(x) for x in m['helper_final'])
    n = 2 * V + m['report']['R']
    helper = next(r for r in range(2 * V, n) if r not in set(m['removed']) and r not in restored)
    m['cleanup'].insert(0, ['add', helper, n + min(restored), 1, 1, list(FULL)])
    AL.expect(out, T + 'cleanup prepended with helper %d += zero buffer (forward-neutral), cleanup count raised'
              % helper, 'wc.replay', through(m, expect_count('cleanup', 1)), stage=STAGE_DUAL_BUF)

    AL.expect(out, T + 'declared profile/inventory of the PR3133 parent', 'words.declared',
              through(raw, dict(ctx, declared=DECLARED_PARENT), repin=False))

    c2 = dict(ctx, expect=dict(ctx['expect']))
    c2['expect'][tag] = dict(ctx['expect'][tag], helpers=409)
    AL.expect(out, T + 'expected helper count 409', 'words.counts', through(raw, c2, repin=False))

    pid = PROVIDER[tag]
    prov = copy.deepcopy(ctx['providers'])
    prov[pid]['widths'][WIDTH_CHANGES[0][0]] = 8
    AL.expect(out, T + 'PROVIDERS.json[%s] width of helper 644 (index 389) back to 8' % pid, 'staged.providers',
              through(raw, dict(ctx, providers=prov), repin=False))

    prov = copy.deepcopy(ctx['providers'])
    prov[pid]['actual_paid_profile']['1'] += 1
    AL.expect(out, T + 'PROVIDERS.json[%s] actual_paid_profile rank-1 count +1, widths kept' % pid,
              'staged.providers_paid', through(raw, dict(ctx, providers=prov), repin=False))

    old = copy.deepcopy(ctx['pr3133'])
    old[pid]['widths'] = list(ctx['providers'][pid]['widths'])
    AL.expect(out, T + 'PR3133-PROVIDERS[%s] replaced by the staged widths (no 8->7 change)' % pid,
              'staged.pr3133_widths', through(raw, dict(ctx, pr3133=old), repin=False))

    AL.expect(out, T + 'declared changed registers (645, 660) instead of PR3605\'s (644, 660)', 'staged.registers',
              through(raw, dict(ctx, staged_regs=(645, 660)), repin=False))

    # parent_diff: each parent mutant keeps every earlier fact, so only the named one can reject it
    P0 = ctx['parents'][tag]
    par = AL.mutant(P0)
    par['note'] = 'extra key'
    AL.expect(out, T + 'parent word with an extra top-level key', 'staged.parent_diff.keys',
              through(raw, with_parent(par), repin=False))

    par = AL.mutant(P0)
    k = next(k for k in range(len(P0['cleanup'])) if P0['cleanup'][k] == w0['cleanup'][k])
    par['cleanup'][k:k + 1] = [['add', 0, 0, 0, 0, []], ['add', 1, 1, 0, 0, []]]
    AL.expect(out, T + 'parent cleanup[%d] replaced by two unmatched items (2-for-1 replace block)' % k,
              'staged.parent_diff.replace', through(raw, with_parent(par), repin=False))

    par = AL.mutant(P0)
    del par['warps'][-1]
    AL.expect(out, T + 'parent with its last warp record removed', 'staged.parent_diff.warps',
              through(raw, with_parent(par), repin=False))

    par = AL.mutant(P0)
    par['A'][par['prelude_events'] + 5][-1] = list(FULL)
    AL.expect(out, T + 'parent word with one A gate frame changed', 'staged.parent_diff.sections',
              through(raw, with_parent(par), repin=False))

    par = AL.mutant(P0)
    par['restore'][210] = copy.deepcopy(w0['restore'][210])
    AL.expect(out, T + 'parent word already carrying the staged restore 210', 'staged.parent_diff.sections',
              through(raw, with_parent(par), repin=False))

    _, opsB, _ = list_diff(P0['B'], w0['B'])
    dels = [i for t, i1, i2, _, _ in opsB if t == 'delete' for i in range(i1, i2)]
    ins_at = [(i1, j1) for t, i1, _, j1, _ in opsB if t == 'insert']
    warp_pos = set(r[0] for r in P0['warps'])

    par = AL.mutant(P0)
    AL.delete_B(par, dels[0])
    AL.expect(out, T + 'parent without deleted write B[%d] (warps re-attached): 7 deletions' % dels[0],
              'staged.parent_diff.sections', through(raw, with_parent(par), repin=False))

    par = AL.mutant(P0)
    par['B'][dels[0]][2] += 1
    AL.expect(out, T + 'parent deleted write B[%d] with source %d -> %d' % (dels[0], P0['B'][dels[0]][2],
                                                                           par['B'][dels[0]][2]),
              'staged.parent_diff.deleted', through(raw, with_parent(par), repin=False))

    # parent B[i1] := the first inserted release: that release becomes matched and the staged copy of the old B[i1]
    # becomes the fourth insertion (counts kept, no warp at i1)
    i1, j1 = ins_at[0]
    AC.need(i1 not in warp_pos and P0['B'][i1] == w0['B'][j1 + 2], 'controls.harness: B insertion point %d' % i1)
    par = AL.mutant(P0)
    par['B'][i1] = copy.deepcopy(w0['B'][j1])
    AL.expect(out, T + 'parent B[%d] replaced by the first inserted release: an ordinary item among the insertions'
              % i1, 'staged.parent_diff.inserted', through(raw, with_parent(par), repin=False))

    _, opsC, _ = list_diff(P0['cleanup'], w0['cleanup'])
    (c1, cj1), = [(i1, j1) for t, i1, _, j1, _ in opsC if t == 'insert'][:1]
    AC.need(P0['cleanup'][c1] == w0['cleanup'][cj1 + 2], 'controls.harness: cleanup insertion point %d' % c1)
    par = AL.mutant(P0)
    par['cleanup'][c1] = copy.deepcopy(w0['cleanup'][cj1])
    AL.expect(out, T + 'parent cleanup[%d] replaced by the first cleanup insert: one insert pair altered' % c1,
              'staged.parent_diff.cleanup_pairs', through(raw, with_parent(par), repin=False))

    par = AL.mutant(P0)
    par['restore'][210][2] -= 2
    AL.expect(out, T + 'parent restore 210 coefficient changed (non-frame field)', 'staged.parent_diff.restore',
              through(raw, with_parent(par), repin=False))

    par = AL.mutant(P0)
    par['start_extra']['644'] = [31]
    AL.expect(out, T + 'parent start_extra[644] = [31]', 'staged.parent_diff.start_extra',
              through(raw, with_parent(par), repin=False))

    par = AL.mutant(P0)
    par['warps'][0][1] += 1
    AL.expect(out, T + 'parent warps[0] lender changed', 'staged.parent_diff.warp_record',
              through(raw, with_parent(par), repin=False))

    par = AL.mutant(P0)
    par['warps'][0][0] += 1
    AL.expect(out, T + 'parent warps[0] B position shifted by one', 'staged.parent_diff.warp_alignment',
              through(raw, with_parent(par), repin=False))


# ------------------------------------------------------------------------------------------------ main ---
def run(controls=True):
    t0 = time.time()
    pins_doc = json.loads(read_pinned(SOURCE_PINS).decode())
    for tag in TAGS:
        AC.need(pins_doc['native_canonical'][tag]['native_source_word_sha256'] == STAGED[tag][3],
                'staged.pin: PR3633 SOURCE-PINS native_source_word_sha256[%s] != %s' % (tag, STAGED[tag][3]))
    providers = json.loads(read_pinned(PROVIDERS).decode())
    pr3133 = json.loads(read_pinned(PR3133_PROVIDERS).decode())
    raws, parents, identity = {}, {}, {}
    for tag in TAGS:
        raws[tag] = read_pinned(STAGED[tag])
        b3605 = git('rev-parse', '%s:%s' % (PR3605, PR3605_PATH % tag)).decode().strip()
        AC.need(b3605 == STAGED[tag][2], 'staged.pr3605_identity: %s blob %s != %s' % (tag, b3605, STAGED[tag][2]))
        same = read_pinned((PR3605, PR3605_PATH % tag, STAGED[tag][2], STAGED[tag][3]))
        AC.need(same == raws[tag], 'staged.pr3605_identity: %s bytes differ' % tag)
        identity[tag] = dict(pr3633=dict(commit=PR3633, path=STAGED[tag][1], git_blob=STAGED[tag][2]),
                             pr3605=dict(commit=PR3605, path=PR3605_PATH % tag, git_blob=b3605),
                             sha256=STAGED[tag][3], identical_bytes=True)
        praw = read_pinned(PARENT[tag])
        AC.need(read_pinned((MAIN, PARENT_COPY % tag, PARENT[tag][2], PARENT[tag][3])) == praw,
                'staged.pin: parent copy %s differs' % (PARENT_COPY % tag))
        parents[tag] = gz_json(praw)
    # parents (positive): the lineage pipeline with PR3605's "before" profile, widths == PR3133-PROVIDERS
    parent_recs, expect = {}, {}
    for tag in TAGS:
        Pp = AL.parse_word(parents[tag])
        lin, cp = counts_of(Pp, parents[tag])
        AC.need(lin == EXPECT_LINEAGE, 'staged.parent_counts: %s %r != %r' % (tag, lin, EXPECT_LINEAGE))
        recp, _, frp = AW.word_pipeline(parents[tag], DECLARED_PARENT, EXPECT_LINEAGE)
        pid = PROVIDER[tag]
        AC.need(list(frp['helper_widths']) == pr3133[pid]['widths']
                and frp['paid'] == AL.intkeys(pr3133[pid]['actual_paid_profile']),
                'staged.parent_providers: parent %s recount != PR3133-PROVIDERS[%s]' % (tag, pid))
        parent_recs[tag] = dict(sha256=PARENT[tag][3], path=PARENT[tag][1], also_at=PARENT_COPY % tag,
                                counts=recp['counts'], profile=recp['profile'], inventory=recp['inventory'],
                                provider=pid, widths_equal_pr3133_providers=True)
        sections = dict(cp['sections'])
        for k, d in SECTION_DELTA.items():
            sections[k] += d
        expect[tag] = dict(EXPECT_LINEAGE, a_prelude_events=cp['a_prelude_events'], sections=sections)
    ctx = dict(pins=dict((t, STAGED[t][3]) for t in TAGS), declared=DECLARED, expect=expect, providers=providers,
               pr3133=pr3133, parents=parents, staged_regs=STAGED_REGS)
    words, widths = {}, {}
    for tag in TAGS:
        words[tag], widths[PROVIDER[tag]] = audit_word(tag, raws[tag], ctx)
    out = []
    if controls:
        AL.harness_selftest()
        n0 = len(AC.ATTEMPTED)
        for tag in TAGS:
            word_controls(tag, raws[tag], ctx, out)
        attempted = len(AC.ATTEMPTED) - n0
    return dict(scope='C1 staged supplier words through the PR3053 word lineage', words=words, parents=parent_recs,
                pr3605_identity=identity, expect=expect, helper_widths=widths, controls=out,
                controls_attempted=attempted if controls else 0, controls_killed=len(out),
                runtime_seconds=round(time.time() - t0, 1))


def summary(res):
    s = dict(runtime_seconds=res['runtime_seconds'], pr3605_identity=res['pr3605_identity'])
    for tag, r in res['words'].items():
        s[tag] = dict(sha256=r['sha256'], counts=r['counts'], profile=r['profile'], inventory=r['inventory'],
                      independent_inputs=r['independent_inputs'], buffers=r['buffers'], cleanup=r['cleanup'],
                      tracker_final=r['tracker']['final_identity'], pr3133_width_changes=r['pr3133_width_changes'],
                      changed_registers=r['changed_registers'], localisation=r['localisation']['sections'],
                      unchanged_sections=r['localisation']['unchanged_sections'])
    s['parents'] = res['parents']
    s['controls'] = [(c['control'], c['expected'], c['rejected_by'] == c['expected']) for c in res['controls']]
    return s


if __name__ == '__main__':
    res = run(controls='--no-controls' not in sys.argv)
    print(json.dumps(summary(res), indent=1, sort_keys=True))
    print('PASS C1: %d words, %d of %d controls killed (%.1fs)' % (len(res['words']), res['controls_killed'],
                                                                    res['controls_attempted'], res['runtime_seconds']))
