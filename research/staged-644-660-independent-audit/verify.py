#!/usr/bin/env python3
"""Independent semantic audit of PR3605's staged 644/660 words against the PR3133 parent words.

Checks, for both providers: the parent single-change control, an independent
reconstruction of the changed words from PROOF.md's prose, exact dirty-input
identity in both orientations by two different algorithms, literal inverse
cleanup, chronological binary frames, the local profile and widths, PROOF.md's
written prefix factorization and target tables, the per-register invoice, and
required-failing mutants.  Standard library only; exact arithmetic throughout.

`python3 -I -B verify.py` replays and compares with RESULT.json; `--write`
regenerates that receipt deliberately.

Sagar Thakrar (thakrarsagar), with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5). Apache-2.0.
"""
from collections import Counter
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import audit_core as C  # noqa: E402  (package-local; bound by the package and commit-byte checks, not hashed here)
from audit_core import need, AuditFailure  # noqa: E402

P = [429, 30]                       # span(429,30): the new entrance and release frame
L = [30]                            # the old entrance
FULL9 = [256, 128, 64, 32, 16, 8, 4, 2, 1]
RANK8 = [256, 128, 64, 32, 16, 8, 5, 3]
# PROOF.md (PR3605 head 3efbb5de), "Two exact prefix directions": deleted raw
# target writes and the releases inserted before old B599 / old B647.
DELETED = {644: (184, 185, 186, 187), 660: (216, 217, 218, 219)}
RELEASE = {644: (599, ((640, 2), (496, -2))), 660: (647, ((656, -1), (520, -2)))}
TABLE = {644: {135: (Q(1, 2), Q(-1, 4), 0), 146: (Q(-1, 2), Q(1, 4), 0),
               162: (Q(1, 2), Q(-1, 4), 0), 220: (Q(1, 2), Q(1, 4), Q(1, 2))},
         660: {141: (Q(1, 2), Q(1, 2), 0), 171: (Q(1, 2), Q(-1, 2), Q(1, 2)),
               185: (Q(-1, 2), Q(-1, 2), 0), 196: (Q(1, 2), Q(1, 2), 0)}}
# PROOF.md "Complete local invoice": per pivot, first donor, second donor.
INVOICE = {'pivot': {2: 1, 3: -1}, 'first donor': {1: 1, 2: 1, 3: -1}, 'second donor': {1: 2, 2: -1}}
ROLES = {644: 'pivot', 640: 'first donor', 496: 'second donor', 660: 'pivot', 656: 'first donor', 520: 'second donor'}
OLD_PROFILE = {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20, 8: 8}
NEW_PROFILE = {1: 2439, 2: 726, 3: 224, 4: 102, 5: 20, 8: 8}
OLD_WIDTHS = {4: 26, 5: 2, 6: 18, 7: 50, 8: 99, 9: 213}
NEW_WIDTHS = {4: 26, 5: 2, 6: 18, 7: 52, 8: 97, 9: 213}
ONE_HELPER_PROFILE = {1: 2436, 2: 725, 3: 226, 4: 102, 5: 20, 8: 8}
ONE_HELPER_WIDTHS = {4: 26, 5: 2, 6: 18, 7: 51, 8: 98, 9: 213}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def canonical(word):
    return hashlib.sha256(json.dumps(word, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def keyed(d):
    return {str(k): v for k, v in sorted(d.items())}


def authenticate():
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for row in sources['files']:
        if row['usage'] == 'input':
            need(sha(ROOT / row['path']) == row['sha256'], 'input pin drift', row['path'])
    for row in sources['snapshot']:
        need(sha(HERE / row['local']) == row['sha256'], 'snapshot pin drift', row['local'])


# ----------------------------------------------------------------------------
# Independent reconstruction of the staged words from PROOF.md's prose
# ----------------------------------------------------------------------------
def stage(parent, helpers=(644, 660), entrance=True, delete=True, release=True, restore210=True,
          release_frame=P, omit=(), flip=()):
    w = copy.deepcopy(parent)
    drop, inserts = set(), {}
    for h in helpers:
        if delete:
            for i in DELETED[h]:
                g = parent['B'][i]
                need(g[0] == 'add' and g[2] == h and C.is_target(g[1]) and g[-1] == L, 'raw target write', h, i)
                drop.add(i)
        if release:
            cut, gates = RELEASE[h]
            for j, (donor, q) in enumerate(gates):
                if (h, j) in omit:
                    continue
                q = -q if (h, j) in flip else q
                inserts.setdefault(cut, []).append(['add', donor, h, q, 1, list(release_frame)])
        if entrance:
            need(w['start_extra'][str(h)] == L and str(h) not in w['helper_final'], 'ordinary L-entering helper', h)
            w['start_extra'][str(h)] = list(P)
    new_b, cutmap = [], {}
    for i in range(len(parent['B']) + 1):
        cutmap[i] = len(new_b)          # warps recorded at old position i fire before the inserted gates
        new_b += inserts.get(i, [])
        if i < len(parent['B']) and i not in drop:
            new_b.append(copy.deepcopy(parent['B'][i]))
    w['B'] = new_b
    for rec in w['warps']:
        rec[0] = cutmap[rec[0]]
    if restore210:
        need(w['restore'][210] == ['scale', 96, -1, 1, RANK8], 'restore 210 preimage')
        w['restore'][210][-1] = list(FULL9)
    w['cleanup'] = C.derive_cleanup(w)
    return w, cutmap


# ----------------------------------------------------------------------------
# Semantic checks
# ----------------------------------------------------------------------------
def semantics(w):
    """Forward (dirty private buffers) and dual by the Schrodinger pass; forward again by reverse pull-back."""
    boundary = {}
    rows = C.forward_rows(w, symbolic_buffers=True,
                          snapshot=lambda r: boundary.setdefault('d', C.boundary_defects(w, r)))
    bad, dirty, leaks, buffer_identity = C.endpoint_defects(w, rows)
    drows = C.forward_rows(w, dual=True, symbolic_buffers=False)
    dbad, ddirty, _, _ = C.endpoint_defects(w, drows, dual=True)
    _, _, dleaks, dbuffer_identity = C.endpoint_defects(w, C.forward_rows(w, dual=True, symbolic_buffers=True), dual=True)
    pulled = C.transpose(C.reverse_columns(w))
    pre = C.transpose(C.reverse_columns(w, upto_cleanup=True))
    pre = {r: pre.get(r, {}) for r in set(pre) | set(range(C.N))}
    return {'forward_bad_registers': bad, 'forward_dirty_buffers': dirty, 'buffer_to_live_leaks': leaks,
            'dirty_buffers_returned_unchanged': buffer_identity, 'boundary_defects': boundary['d'],
            'dual_bad_registers': dbad, 'dual_dirty_buffers': ddirty,
            'dual_buffer_to_live_leaks': dleaks, 'dual_dirty_buffers_returned_unchanged': dbuffer_identity,
            'reverse_pullback_equals_forward': pulled == {r: v for r, v in rows.items() if v},
            'reverse_boundary_defects': C.boundary_defects(w, pre),
            'independent_inputs': C.N - len(w['removed']), 'private_buffers': len(w['helper_final']),
            'final_terms': sum(len(v) for v in rows.values())}


def semantic_pass(s):
    return (not s['forward_bad_registers'] and not s['forward_dirty_buffers'] and not s['buffer_to_live_leaks']
            and not s['boundary_defects'] and not s['dual_bad_registers'] and not s['dual_dirty_buffers']
            and s['reverse_pullback_equals_forward'] and not s['reverse_boundary_defects']
            and s['dirty_buffers_returned_unchanged'] and s['dual_dirty_buffers_returned_unchanged']
            and not s['dual_buffer_to_live_leaks']
            and s['independent_inputs'] == 632 and s['private_buffers'] == 91)


def execute(rows, items):
    """Literal forward execution of primitive items on the given symbolic rows."""
    for g in items:
        if g[0] == 'corr':
            _, t, s, word, c = g
            moved = {}
            for (var, wd), x in rows[s].items():
                for o in reversed(word):
                    wd = C._left(o, wd)
                moved[var, wd] = x
            C._axpy(rows[t], moved, c)
        elif g[0] == 'add':
            need(g[1] != g[2], 'self add')
            C._axpy(rows[g[1]], rows[g[2]], Q(g[3], g[4]))
        elif g[0] == 'scale':
            q = Q(g[2], g[3])
            rows[g[1]] = {key: q * x for key, x in rows[g[1]].items()}
        elif g[0] == 'warp':
            rows[g[1]] = {(var, C._left(g[2], wd)): x for (var, wd), x in rows[g[1]].items()}
        else:
            raise AuditFailure('unknown primitive')
    return rows


def prefix_rows(w, k, before=()):
    """All register rows after the program prefix ending just before B[k] (warps recorded at k included)."""
    removed = set(w['removed'])
    rows = {r: {(r, ()): Q(1)} for r in range(C.N) if r not in removed}
    items = [('corr', c['target'], c['source'], tuple(c['operator_word']), Q(c['coefficient']))
             for c in w['initial_corrections']]
    items += w['precondition'] + w['compensation'] + w['A'] + w['cut']
    at = {}
    for op, rec in enumerate(w['warps'], 1):
        at.setdefault(rec[0], []).append(['warp', rec[1], op])
    for p in range(k + 1):
        items += at.get(p, [])
        if p < k:
            items.append(w['B'][p])
    return execute(rows, list(before) + items)


def prefix_identity(parent, new, cutmap):
    """PROOF.md: P_new = P_old S1 S2 on every register at the boundary after the old-B647 releases."""
    s_gates = [['add', d, h, q, 1, P] for h in (644, 660) for d, q in RELEASE[h][1]]
    old = prefix_rows(parent, 647, s_gates)
    new_rows = prefix_rows(new, cutmap[647] + len(RELEASE[660][1]))
    unchanged = prefix_rows(parent, 647)
    moved = sorted(r for r in old if old[r] != unchanged[r])
    return old == new_rows, moved


def target_tables(parent, k):
    table = {}
    rows = prefix_rows(parent, k)
    for t in range(C.V, 2 * C.V):
        for (var, word), x in rows[t].items():
            if var in ROLES:
                need(word == (), 'operator word on a pivot column', t, var, word)
                table.setdefault(t, {})[var] = x
    return table


def check_tables(table):
    out = {}
    for h, expect in TABLE.items():
        cols = (h, *[d for d, _ in RELEASE[h][1]])
        v = (1, *[q for _, q in RELEASE[h][1]])
        got = {t: tuple(table.get(t, {}).get(c, 0) for c in cols) for t in range(C.V, 2 * C.V)
               if any(table.get(t, {}).get(c, 0) for c in cols)}
        need(got == expect, 'PROOF.md target table differs', h, got)
        need(all(sum(a * b for a, b in zip(row, v)) == 0 for row in got.values()), 'table does not kill v', h)
        out[str(h)] = {str(t): [str(x) for x in row] for t, row in sorted(got.items())}
    return out


def register_bills(chain):
    out = {}
    for r, events in chain.items():
        c = Counter(d for _, d, _ in events if isinstance(d, int) and d > 0)
        if c:
            out[r] = c
    return out


def bill_delta(a, b):
    return {k: b.get(k, 0) - a.get(k, 0) for k in sorted(set(a) | set(b)) if b.get(k, 0) != a.get(k, 0)}


# ----------------------------------------------------------------------------
# Mutants
# ----------------------------------------------------------------------------
def evaluate(word, want_semantics=True):
    out = {}
    try:
        bill, widths, _, _, _ = C.frame_bill(word)
        out.update(frames='PASS', profile=keyed(bill), widths=keyed(widths))
    except AuditFailure as e:
        out['frames'] = 'FAIL: ' + str(e)
    if want_semantics:
        rows = C.forward_rows(word, symbolic_buffers=True)
        bad, dirty, leaks, _ = C.endpoint_defects(word, rows)
        out['forward'] = 'PASS' if not (bad or dirty or leaks) else 'FAIL'
        out['forward_bad_targets'] = [r for r in bad if C.is_target(r)]
        out['forward_bad_other'] = [r for r in bad if not C.is_target(r)]
        out['forward_dirty_buffers'] = dirty
        dbad, ddirty, _, _ = C.endpoint_defects(word, C.forward_rows(word, dual=True, symbolic_buffers=False), dual=True)
        out['dual'] = 'PASS' if not (dbad or ddirty) else 'FAIL'
    return out


def mutants(parent, new):
    res = {}
    for h in (644, 660):
        for j in range(2):
            donor = RELEASE[h][1][j][0]
            res['omit release %d->%d' % (h, donor)] = evaluate(stage(parent, omit={(h, j)})[0])
            res['flip release %d->%d' % (h, donor)] = evaluate(stage(parent, flip={(h, j)})[0])
        res['flip both releases of %d' % h] = evaluate(stage(parent, flip={(h, 0), (h, 1)})[0])
    res['releases added but raw target writes kept'] = evaluate(stage(parent, delete=False)[0])
    res['entrance change only, on the parent'] = evaluate(
        stage(parent, delete=False, release=False, restore210=False)[0], want_semantics=False)
    res['old [30] entrance kept'] = evaluate(stage(parent, entrance=False)[0])
    res['releases at frame [30]'] = evaluate(stage(parent, release_frame=L)[0], want_semantics=False)
    res['restore-210 frame edit dropped'] = evaluate(stage(parent, restore210=False)[0])
    for h in (644, 660):
        res['%d-only staged edit' % h] = evaluate(stage(parent, helpers=(h,), restore210=False)[0])
    stale = copy.deepcopy(new)
    stale['cleanup'] = copy.deepcopy(parent['cleanup'])
    res['parent cleanup on the changed word'] = evaluate(stale)
    short = copy.deepcopy(new)
    del short['cleanup'][next(i for i, g in enumerate(short['cleanup']) if g[0] == 'add' and 644 in g[1:3])]
    res['first 644 cleanup gate removed'] = evaluate(short)
    return res


def require_mutants(m):
    release_mutants = [k for k in m if k.startswith(('omit', 'flip'))] + ['releases added but raw target writes kept']
    for k in release_mutants:
        need(m[k]['forward'] == 'FAIL' and m[k]['forward_bad_targets'], 'release mutant not rejected at a target', k)
    for k in ('parent cleanup on the changed word', 'first 644 cleanup gate removed'):
        need(m[k]['forward'] == 'FAIL', 'cleanup mutant accepted', k)
    for k in ('entrance change only, on the parent', 'releases at frame [30]'):
        need(m[k]['frames'].startswith('FAIL: frame containment fails'), 'frame mutant accepted', k)
    old_entry = m['old [30] entrance kept']
    need(old_entry['forward'] == old_entry['dual'] == 'PASS', 'old-entrance word keeps the identity')
    need(old_entry['profile'] == keyed(Counter(NEW_PROFILE) + Counter({1: 2}))
         and old_entry['widths'] == keyed(OLD_WIDTHS), 'old-entrance bill')
    drop210 = m['restore-210 frame edit dropped']
    need(drop210['forward'] == drop210['dual'] == 'PASS' and drop210['profile'] == keyed(NEW_PROFILE)
         and drop210['widths'] == keyed(NEW_WIDTHS), 'restore-210 edit bill-neutral')
    for h in (644, 660):
        one = m['%d-only staged edit' % h]
        need(one['forward'] == one['dual'] == 'PASS', 'single-helper identity', h)
        need(one['profile'] == keyed(ONE_HELPER_PROFILE) and one['widths'] == keyed(ONE_HELPER_WIDTHS),
             'single-helper bill', h)


# ----------------------------------------------------------------------------
def provider(tag):
    parent_path = ROOT / ('research/rank7-coupled-586-588-carrier-fold/edits/FINAL-WORD-%s.json.gz' % tag)
    new_path = HERE / 'inputs' / ('STAGED644-660-%s.json.gz' % tag)
    parent, new = load(parent_path), load(new_path)
    record = load(HERE / 'inputs' / ('STAGED-PAIR-RECORD-%s.json.gz' % tag))
    out = {}
    # (a) single-change control: the unchanged PR3133 parent word
    need(canonical(parent) == record['source_canonical_sha256'], 'parent canonical digest')
    need(sha(parent_path) == record['source_compressed_sha256'], 'parent compressed digest')
    C.hygiene(parent)
    pbill, pwidths, pchain, _, _ = C.frame_bill(parent, lagrangian=True)
    need(pbill == OLD_PROFILE and pwidths == OLD_WIDTHS, 'parent control table', pbill, pwidths)
    need(C.same_cleanup(C.derive_cleanup(parent), parent['cleanup']), 'parent cleanup is not the literal inverse')
    psem = semantics(parent)
    need(semantic_pass(psem), 'parent control semantics', psem)
    out['parent_control'] = {'canonical_sha256': canonical(parent), 'profile': keyed(pbill), 'widths': keyed(pwidths),
                             'cleanup_literal_inverse': True, 'inherited_hygiene': True, 'semantics': psem}
    # (b) independent reconstruction and full audit of the changed word
    rebuilt, cutmap = stage(parent)
    declared = {'deleted': [[r['index'], r['old']] for r in record['B_deleted']],
                'inserted': [[r['before'], r['gates']] for r in record['B_inserted']],
                'frames': [record['A_frame_edits'], record['B_frame_edits'],
                           [[r['index'], r['old'], r['new']] for r in record['restore_frame_edits']]],
                'starts': record['start_frames']}
    prose = {'deleted': [[i, parent['B'][i]] for h in (644, 660) for i in DELETED[h]],
             'inserted': [[RELEASE[h][0], [['add', d, h, q, 1, P] for d, q in RELEASE[h][1]]] for h in (644, 660)],
             'frames': [[], [], [[210, RANK8, FULL9]]],
             'starts': {str(h): {'old': L, 'new': P} for h in (644, 660)}}
    need(declared == prose, 'declared edit record differs from PROOF.md prose')
    need(canonical(new) == record['target_canonical_sha256'], 'changed canonical digest')
    need(sha(new_path) == record['target_compressed_sha256'], 'changed compressed digest')
    need(set(rebuilt) == set(new), 'field set')
    differing = sorted(k for k in new if k not in ('cleanup', 'report') and new[k] != rebuilt[k])
    need(not differing, 'PROOF.md reconstruction differs from the shipped word', differing)
    need(C.same_cleanup(rebuilt['cleanup'], new['cleanup']), 'shipped cleanup is not the literal inverse')
    C.hygiene(new)
    nbill, nwidths, nchain, nstart, nend = C.frame_bill(new, lagrangian=True)
    need(nbill == NEW_PROFILE and nwidths == NEW_WIDTHS, 'changed profile/widths', nbill, nwidths)
    need({int(k): v for k, v in new['report']['local_profile'].items()} == nbill
         and {int(k): v for k, v in new['report']['width_inventory'].items()} == nwidths, 'report fields')
    nsem = semantics(new)
    need(semantic_pass(nsem), 'changed word semantics', nsem)
    out['changed_word'] = {'canonical_sha256': canonical(new), 'reconstructed_from_PROOF_prose': True,
                           'declared_record_equals_PROOF_prose': True, 'inherited_hygiene': True,
                           'profile': keyed(nbill), 'widths': keyed(nwidths), 'cleanup_literal_inverse': True,
                           'semantics': nsem,
                           'entrance_frame_points': {str(h): C.points(nstart[h]) for h in (644, 660)},
                           'terminal_frames_full': all(nend[h] == C.FULL for h in (644, 660)),
                           'release_positions_new_B': [cutmap[599], cutmap[647]]}
    # (c) second method: per-register written invoice, prefix factorization, target tables
    pb, nb = register_bills(pchain), register_bills(nchain)
    changed = {r: bill_delta(pb.get(r, {}), nb.get(r, {})) for r in sorted(set(pb) | set(nb))
               if bill_delta(pb.get(r, {}), nb.get(r, {}))}
    need(set(changed) == set(ROLES), 'registers whose bill changes', sorted(changed))
    need(all(changed[r] == INVOICE[ROLES[r]] for r in ROLES), 'PROOF.md per-register invoice', changed)
    total = Counter()
    for d in changed.values():
        total.update(d)
    need(dict(total) == bill_delta(OLD_PROFILE, NEW_PROFILE), 'invoice sum')
    same, moved = prefix_identity(parent, new, cutmap)
    need(same, 'P_new != P_old S1 S2 at the old-B647 boundary')
    tables = check_tables(target_tables(parent, 599))
    need(tables == check_tables(target_tables(parent, 647)), 'tables move between the cuts')
    out['second_method'] = {
        'per_register_bill_delta': {str(r): keyed(d) for r, d in changed.items()},
        'roles': {str(r): ROLES[r] for r in ROLES}, 'sum': keyed(total),
        'register_96_bill_unchanged': pb.get(96) == nb.get(96),
        'prefix_identity_all_registers': same, 'registers_moved_by_S': moved,
        'target_tables_before_old_B599_and_B647': tables}
    # (d) mutants
    m = mutants(parent, new)
    require_mutants(m)
    out['mutants'] = m
    return out


def self_test():
    """Interpreter sanity on tiny words: operator order, cancellation, dual symbols, pull-back agreement."""
    tiny = {'removed': list(range(226, C.N)), 'helper_final': {}, 'initial_corrections': [], 'precondition': [],
            'compensation': [], 'A': [], 'cut': [], 'warps': [], 'restore': [], 'cleanup': [],
            'B': [['warp', 224, 1], ['warp', 224, 2], ['add', 225, 224, 3, 2, []], ['warp', 224, -2]]}
    rows = C.forward_rows(tiny, symbolic_buffers=False)
    need(rows[224] == {(224, (1,)): Q(1)} and rows[225] == {(225, ()): Q(1), (224, (2, 1)): Q(3, 2)}, 'free-group order')
    need(C.transpose(C.reverse_columns(tiny)) == {r: v for r, v in rows.items() if v}, 'pull-back disagrees on tiny word')
    dual = C.forward_rows(tiny, dual=True, symbolic_buffers=False)
    # contragredient: 224 <- D1 x224 - 3/2 D2^{-1} x225, with D_k = K_k^{-T} independent symbols
    need(dual[224] == {(224, (1 + C.DUAL,)): Q(1), (225, (-(2 + C.DUAL),)): Q(-3, 2)}
         and dual[225] == {(225, ()): Q(1)}, 'dual symbols')
    need(C.dual_op(-7) == -(7 + C.DUAL) and C._left(5, (-5, 3)) == (3,) and C._right((3, -5), 5) == (3,), 'reduction')
    swapped = copy.deepcopy(tiny)
    swapped['B'][0][2], swapped['B'][1][2] = 2, 1
    need(C.forward_rows(swapped, symbolic_buffers=False)[225] != rows[225], 'operator order ignored')


def main():
    self_test()
    authenticate()
    result = {'status': 'PASS_INDEPENDENT_STAGED_644_660_WORD_AUDIT',
              'scope': 'Finite exact local audit of PR3605 head 3efbb5de words against the PR3133 parent words: '
                       'free-operator dirty-input identity (forward with symbolic private buffers, contragredient '
                       'dual, reverse pull-back), literal inverse cleanup, binary-frame chronology/profile/widths, '
                       'PROOF.md prefix factorization, tables and invoice, and mutants. No native Gaussian phase, '
                       'owner journal, complete admission, kappa or frontier claim.',
              'providers': {}}
    for tag in ('base', 'extra'):
        result['providers'][tag] = provider(tag)
        print('CHECKED', tag, 'parent control, changed word, second method,',
              len(result['providers'][tag]['mutants']), 'mutants', flush=True)
    need(result['providers']['base']['changed_word']['profile'] == result['providers']['extra']['changed_word']['profile'],
         'providers disagree')
    encoded = json.dumps(result, indent=1, sort_keys=True, default=str) + '\n'
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(encoded, encoding='utf-8', newline='\n')
    else:
        need((HERE / 'RESULT.json').read_text(encoding='utf-8') == encoded, 'RESULT.json receipt differs')
    print(result['status'])


if __name__ == '__main__':
    main()
