#!/usr/bin/env python3
"""Exact two-helper release composition, standard library only.

New checker and scoped construction: OpenAI Codex (GPT-6.1 Sol), 2026-10-19.
Apache-2.0. Word format, literal inverse contract and source frame accountant:
PR4076 (Rohan Arun), retaining PR3945 (Dugongue), PR3605 (Ross Richardson),
PR3687 (Sagar Thakrar, crediting Arham Tahir), and predecessors in NOTICE.md.
This checker implements its sparse free-group interpreter without importing the
source interpreter. The pinned source frame accountant is a separate invoice
check, not a new native-phase or owner-allocation proof.
"""
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json

SOURCE_HEAD = '9744f9df268590295a9872b1952c695a678192b9'
PINS = {
    'inputs/OLD-base.json.gz': '08e6c96fbe3dfec96cb8451b3867ef8c1a214109ecd1e5af7fcc28e0f05728d0',
    'inputs/OLD-extra.json.gz': 'd83c2ec9cecc0ad092d34ea4080b28a4fd7199579356b6d5a8fc6cd53ff93299',
    'inputs/NEW-base.json.gz': '8159c67d29ab58efe546ebc4ce20872421996cc71b5f17737ff8b36cbc76d148',
    'inputs/NEW-extra.json.gz': '0147e6b30ef328e227e89113323eb0d02d116e125b0e7c99a00ea4f2652dcc80',
    'vendor/audit_core.py': '888679ca8502cdcb100420fe5382a052529a494bf76cb332928b86e62612b951',
    'NOTICE.md': '91f7f723bb616aca757812f940f6b893559e64e441d6158c907155a79b3b15a7',
    'PROOF.md': '9ebc183172a290f8b7f1527df9d56c3123f80e1a21485bf44c4cc5ecd56108cc',
    'recipe/ENTRIES.json': '00071bc2e54bf5fd05a6aac9292a3861087e72898d86d1f6f7bbda65b07cfbda',
}
CANONICAL = {
    'OLD-base': 'cee1ddcbdf3cdcba99146f281cbb452440dd1ed641aa3a47ccc3343680ae7ddc',
    'OLD-extra': 'cc1826748ed24cd085a5756b46f0090d5a43ad54820c025366cf2848aca589b2',
    'NEW-base': 'ac474908d37c99db0282a094cef8a3a258570e3b4256b87707020ef02a239b84',
    'NEW-extra': 'c0038838293e274efeeca533ba8dbd210e3f43ad11246abf0e89a4160a2efa75',
}
H = {608, 609}
R = {608, 609, 417, 419, 421, 610}
FRAME = [144, 75, 42, 7]
RELEASES = {
    ('add', 121, 609, 1, 2), ('add', 137, 608, -1, 2),
    ('add', 610, 608, -1, 1), ('add', 610, 609, -1, 1),
}
RELEASE_AT = {388: ('add', 121, 609, 1, 2), 410: ('add', 137, 608, -1, 2),
              948: ('add', 610, 608, -1, 1), 950: ('add', 610, 609, -1, 1)}
DUAL = 10**6


def need(ok, why):
    if not ok:
        raise ValueError(why)


def digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def target(r):
    return 112 <= r < 224


def events(w):
    at = {}
    for k, rec in enumerate(w['warps'], 1):
        at.setdefault(rec[0], []).append(['warp', rec[1], k])
    result = []
    for i in range(len(w['B']) + 1):
        result.extend(at.get(i, []))
        if i < len(w['B']):
            result.append(w['B'][i])
    return result


def prefix(w):
    cs = [('corr', c['target'], c['source'], tuple(c['operator_word']), Q(c['coefficient']))
          for c in w['initial_corrections']]
    return cs + w['precondition'] + w['compensation'] + w['A'] + w['cut'] + events(w) + w['restore']


def invert(g):
    if g[0] == 'add':
        return ['add', g[1], g[2], -g[3], g[4], *g[5:]]
    if g[0] == 'scale':
        return ['scale', g[1], g[3], g[2], *g[4:]]
    if g[0] == 'warp':
        return ['warp', g[1], -g[2], *g[3:]]
    need(g[0] == 'corr', 'unknown inverse primitive')
    return ('corr', g[1], g[2], g[3], -g[4])


def cleanup(w):
    restored = set(map(int, w['helper_final']))
    rename = lambda r: r + 704 if r in restored else r
    seq = w['A'][w['prelude_events']:] + events(w) + w['restore']
    out = []
    full = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    for g in reversed(seq):
        if g[0] != 'warp' and target(g[1]):
            continue
        ig = invert(g)
        if ig[0] == 'add':
            out.append(['add', rename(ig[1]), rename(ig[2]), ig[3], ig[4], full])
        elif ig[0] == 'scale':
            out.append(['scale', rename(ig[1]), ig[2], ig[3], full])
        else:
            out.append(['warp', rename(ig[1]), ig[2], full])
    return out


def registers(w):
    live = set(range(704)) - set(w['removed'])
    return sorted(live | {704 + int(r) for r in w['helper_final']})


def left(op, word):
    return word[1:] if word and word[0] == -op else (op,) + word


def axpy(dst, src, q):
    for k, v in src.items():
        n = dst.get(k, 0) + q * v
        if n:
            dst[k] = n
        else:
            dst.pop(k, None)


def interpret(w, seq, dual=False):
    """Every live input and dirty private buffer is a separate independent symbol."""
    rows = {r: {(r, ()): Q(1)} for r in registers(w)}
    dualop = lambda k: (1 if k > 0 else -1) * (abs(k) + DUAL)
    for g in seq:
        if g[0] == 'add':
            d, s, q = g[1], g[2], Q(g[3], g[4])
            need(d != s and q != 0, 'invalid add')
            if dual:
                d, s, q = s, d, -q
            axpy(rows[d], rows[s], q)
        elif g[0] == 'scale':
            q = Q(g[2], g[3])
            need(q != 0, 'invalid scale')
            if dual:
                q = 1 / q
            rows[g[1]] = {k: q * v for k, v in rows[g[1]].items()}
        elif g[0] == 'warp':
            op = dualop(g[2]) if dual else g[2]
            rows[g[1]] = {(i, left(op, wd)): v for (i, wd), v in rows[g[1]].items()}
        else:
            need(g[0] == 'corr', 'unknown forward primitive')
            _, d, s, wd, q = g
            ops = list(reversed(wd))
            if dual:
                d, s, q = s, d, -q
                ops = [-dualop(op) for op in wd]
            moved = {}
            for (i, old), v in rows[s].items():
                for op in ops:
                    old = left(op, old)
                moved[i, old] = v
            axpy(rows[d], moved, q)
    return rows


def endpoint_ok(w, rows, dual=False):
    for r in registers(w):
        expected = {(r, ()): Q(1)}
        if not dual and target(r):
            expected[r - 112, ()] = Q(1)
        if dual and r < 112:
            expected[r + 112, ()] = Q(-1)
        if rows[r] != expected:
            return False
    return True


def column(rows, h, only_targets=False):
    return {(r, wd): q for r, row in rows.items() for (i, wd), q in row.items()
            if i == h and (not only_targets or target(r))}


def encode(poly):
    return [{'register': r, 'word': list(wd), 'coefficient': str(q)}
            for (r, wd), q in sorted(poly.items())]


def opcode(g):
    if g[0] == 'corr':
        return g
    return tuple(g[:3] if g[0] == 'warp' else g[:5] if g[0] == 'add' else g[:4])


def cut_mapping(old, new, entries):
    """Replay ordered edit coordinates with immutable original-event labels."""
    seq = [(i, g) for i, g in enumerate(prefix(old))]
    source_cuts = {}
    for entry in entries:
        h, cut = entry['helper'], entry['cut']
        origin, next_gate = seq[cut]
        source_cuts[h] = (origin, opcode(next_gate))
        deleted = {i for i, (_, g) in enumerate(seq) if i < cut and g[0] == 'add'
                   and g[2] == h and target(g[1]) and abs(Q(g[3], g[4])) == Q(1, 4)}
        need(len(deleted) == 4, 'staged-entry early-read source sites')
        releases = {}
        for rel in entry['releases']:
            q = Q(rel['coefficient'])
            releases[rel['position']] = ['add', rel['register'], h, q.numerator, q.denominator, []]
        changed = []
        for i in range(len(seq) + 1):
            if i in releases:
                changed.append((None, releases[i]))
            if i < len(seq) and i not in deleted:
                changed.append(seq[i])
        seq = changed
    need([opcode(g) for _, g in seq] == [opcode(g) for g in prefix(new)], 'ordered source-index replay')
    out = []
    for h in (608, 609):
        origin, gate = source_cuts[h]
        matches = [i for i, (label, _) in enumerate(seq) if label == origin]
        need(len(matches) == 1, 'source cut label survived')
        out.append({'helper': h, 'source_record_cut': 10535, 'OLD_global_cut': origin,
                    'NEW_global_cut': matches[0], 'next_opcode': list(gate)})
    need([x['NEW_global_cut'] for x in out] == [10523, 10527], 'explicit physical cut mapping')
    return out


def B_location(w, whole_cut):
    ordinary = events(w)
    base = len(prefix(w)) - len(w['restore']) - len(ordinary)
    current = base
    at = Counter(g[0] for g in w['warps'])
    for i in range(len(w['B']) + 1):
        if current <= whole_cut < current + at[i]:
            return {'B_position': i, 'within_warps_before_B': whole_cut - current}
        current += at[i]
        if i < len(w['B']):
            if current == whole_cut:
                return {'B_position': i, 'within_warps_before_B': None}
            current += 1
    raise ValueError('cut outside B word')


def shared_sum(w):
    """Replace NEW B948:951, preserving all four immediately preceding warps."""
    z = deepcopy(w)
    before = [
        ['add', 610, 608, -1, 1, FRAME],
        ['add', 608, 410, -1, 1, FRAME],
        ['add', 610, 609, -1, 1, FRAME],
    ]
    need(z['B'][948:951] == before, 'literal three-gate preimage')
    need(not any(948 < g[0] < 951 for g in z['warps']), 'crossed native warp')
    after = [
        ['add', 608, 609, 1, 1, FRAME],
        ['add', 610, 608, -1, 1, FRAME],
        ['add', 608, 609, -1, 1, FRAME],
        ['add', 608, 410, -1, 1, FRAME],
    ]
    z['B'][948:951] = deepcopy(after)
    for rec in z['warps']:
        if rec[0] >= 951:
            rec[0] += 1
    z['cleanup'] = cleanup(z)
    return z, before, after


def without_releases(w, which):
    z = deepcopy(w)
    changed = 0
    for i, signature in RELEASE_AT.items():
        g = z['B'][i]
        need(tuple(g[:-1]) == signature, 'exact release-site preimage')
        if signature in which:
            # Identity padding preserves exact original warp positions.
            z['B'][i] = ['scale', g[1], 1, 1, g[-1]]
            changed += 1
    need(changed == len(which), 'release identity-padding count')
    z['cleanup'] = cleanup(z)
    return z


def reject(label, fn):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError('control was accepted: ' + label)


def run_provider(w, old, entries, core):
    regs = registers(w)
    need(len(regs) == 723 and len(w['helper_final']) == 91, 'complete 632+91 input domain')
    need(cleanup(w) == w['cleanup'], 'source literal cleanup')
    original = interpret(w, prefix(w) + w['cleanup'])
    need(endpoint_ok(w, original), 'source arbitrary-dirty endpoint')
    need(endpoint_ok(w, interpret(w, prefix(w) + w['cleanup'], dual=True), True), 'source dual endpoint')
    M = interpret(w, prefix(w))
    expected_columns = {
        608: {(608, ()): Q(1), (417, ()): Q(1, 2), (421, ()): Q(-1, 2), (610, ()): Q(-1)},
        609: {(609, ()): Q(1), (417, ()): Q(1, 2), (419, ()): Q(-1, 2), (610, ()): Q(-1)},
    }
    for h in H:
        need(column(M, h) == expected_columns[h], 'complete prefix helper column')
    inverse_seq = [invert(g) for g in reversed(prefix(w))]
    inv = interpret(w, inverse_seq)
    identity = interpret(w, [])
    need(interpret(w, prefix(w) + inverse_seq) == identity, 'full prefix reverse-inverse identity')
    # Unique outside-R pivots prove any alpha supported R with alpha M supported H is zero.
    need(inv[608].get((342, ())) == 2 and not any(i == 342 for i, _ in inv[609]), 'first outside-R pivot')
    need(inv[609].get((276, ())) == -1 and not any(i == 276 for i, _ in inv[608]), 'second outside-R pivot')
    need(inv[608].get((356, ())) == 2 and inv[609].get((292, ())) == -1, 'second factory pair')
    mapped_cuts = cut_mapping(old, w, entries)
    suffix_cuts = []
    for cut in sorted({x['NEW_global_cut'] for x in mapped_cuts} | {10535}):
        suffix = prefix(w)[cut:]
        S = interpret(w, suffix)
        inverse_suffix = [invert(g) for g in reversed(suffix)]
        Sinv = interpret(w, inverse_suffix)
        need(interpret(w, suffix + inverse_suffix) == identity, 'current-state suffix reverse-inverse identity')
        need(all(column(S, h) == expected_columns[h] for h in H), 'current-state suffix helper column')
        need(all(Sinv[h] == inv[h] for h in H), 'current-state suffix inverse rows')
        suffix_cuts.append({'NEW_global_cut': cut, 'next_opcode': list(opcode(prefix(w)[cut])),
                            **B_location(w, cut), 'same_pair_inverse_rows': True,
                            'complete_current_state_dimension': len(regs)})
    residual = without_releases(w, RELEASES)
    residual_rows = interpret(residual, prefix(residual) + residual['cleanup'])
    correction = {h: {k: -v for k, v in column(residual_rows, h, True).items()} for h in H}
    need(correction == {
        608: {(121, ()): Q(1, 2), (137, ()): Q(1, 2)},
        609: {(114, ()): Q(1, 2), (173, ()): Q(1, 2)},
    }, 'complete target-dirt correction columns')
    expected_residual = deepcopy(original)
    for h, poly in correction.items():
        for (r, wd), q in poly.items():
            axpy(expected_residual[r], {(h, wd): Q(1)}, -q)
    need(residual_rows == expected_residual, 'four-release omission has additional input defects')
    minor = correction[608].get((121, ()), 0) * correction[609].get((114, ()), 0) - correction[609].get((121, ()), 0) * correction[608].get((114, ()), 0)
    need(minor == Q(1, 4), 'one-channel augmentation minor')
    shared_only = without_releases(w, {g for g in RELEASES if g[1] == 610})
    shared_rows = interpret(shared_only, prefix(shared_only) + shared_only['cleanup'])
    common = {(114, ()): Q(-1, 2), (121, ()): Q(-1, 2)}
    need(all(column(shared_rows, h, True) == common for h in H), 'shared610 sum channel')
    expected_shared = deepcopy(original)
    for h in H:
        for (r, wd), q in common.items():
            axpy(expected_shared[r], {(h, wd): Q(1)}, q)
    need(shared_rows == expected_shared, 'shared610 omission has additional input defects')
    z, before, after = shared_sum(w)
    need(interpret(z, prefix(z) + z['cleanup']) == original, 'changed full arbitrary-dirty operator')
    need(interpret(z, prefix(z)) == M, 'changed complete boundary operator')
    need(endpoint_ok(z, interpret(z, prefix(z) + z['cleanup'], dual=True), True), 'changed dual operator')
    need(cleanup(z) == z['cleanup'] and len(z['cleanup']) == len(w['cleanup']) + 1, 'regenerated cleanup count')
    core.hygiene(w)
    core.hygiene(z)
    old_bill = core.frame_bill(w, lagrangian=True)
    new_bill = core.frame_bill(z, lagrangian=True)
    need(old_bill[0] == {int(r): n for r, n in w['report']['local_profile'].items()}, 'source profile report')
    need(old_bill[1] == {int(r): n for r, n in w['report']['width_inventory'].items()}, 'source width report')
    need(old_bill[:2] == new_bill[:2] and old_bill[3:] == new_bill[3:], 'complete frame invoice changed')
    def paid_chains(chains):
        return {r: [(d, mask) for _, d, mask in chain if d == 'warp' or d > 0]
                for r, chain in chains.items()}
    need(paid_chains(old_bill[2]) == paid_chains(new_bill[2]), 'ordered positive frame changes differ')
    need(z['report'] == w['report'] and z['start_extra'] == w['start_extra'] and z['helper_final'] == w['helper_final'], 'unchanged widths and endpoint contracts')
    controls = []
    bad = deepcopy(z)
    bad['B'][950][3] = 1
    bad['cleanup'] = cleanup(bad)
    controls.append(reject('wrong sum unmix sign, cleanup regenerated', lambda: need(interpret(bad, prefix(bad) + bad['cleanup']) == original, 'operator mismatch')))
    bad = deepcopy(z)
    k = next(i for i, g in enumerate(bad['cleanup']) if g[:5] == ['add', 608, 609, 1, 1])
    del bad['cleanup'][k]
    controls.append(reject('omitted actual inverse cleanup gate', lambda: need(interpret(bad, prefix(bad) + bad['cleanup']) == original, 'operator mismatch')))
    bad = deepcopy(z)
    bad['cleanup'] = deepcopy(w['cleanup'])
    controls.append(reject('stale literal cleanup', lambda: need(bad['cleanup'] == cleanup(bad), 'literal inverse mismatch')))
    bad = without_releases(w, {('add', 121, 609, 1, 2)})
    controls.append(reject('omitted target release, cleanup regenerated', lambda: need(endpoint_ok(bad, interpret(bad, prefix(bad) + bad['cleanup'])), 'target defect')))
    wrong = deepcopy(correction)
    wrong[609] = dict(wrong[608])
    controls.append(reject('collapsed correction columns', lambda: need(wrong == correction, 'rank2 column mismatch')))
    return {
        'source_word_sha256': digest(w), 'shared_word_sha256': digest(z),
        'inputs': {'live': 632, 'dirty_private_buffers': 91, 'dimension': len(regs)},
        'prefix_columns': {str(h): encode(column(M, h)) for h in sorted(H)},
        'inverse_rows': {str(h): encode(inv[h]) for h in sorted(H)},
        'ordered_staging_cut_mapping': mapped_cuts,
        'arbitrary_current_state_suffix_cuts': suffix_cuts,
        'target_correction_columns': {str(h): encode(correction[h]) for h in sorted(H)},
        'target_minor_rows': [121, 114], 'target_minor': str(minor),
        'natural_receiver_set': sorted(R), 'raw_H_recovery_rank_from_R': 0,
        'shared610_omission_residual_each_helper': encode(common),
        'literal_B_slice': [948, 951], 'old': before, 'new': after,
        'native_warps_at_common_release_cut': [k for k, rec in enumerate(w['warps'], 1) if rec[0] == 948],
        'unchanged_local_profile': w['report']['local_profile'],
        'unchanged_width_inventory': w['report']['width_inventory'],
        'complete_frame_invoice_equal': True,
        'source_counts_delta': {'forward_adds': 1, 'inverse_cleanup_adds': 1, 'total_scalar_adds': 2},
        'cleanup_lengths': [len(w['cleanup']), len(z['cleanup'])],
        'shared_cleanup_sha256': digest(z['cleanup']),
        'semantics': 'all independent live and dirty-buffer columns; forward, dual, complete prefix, reverse-inverse PASS',
        'rejected_controls': controls,
    }


def main():
    ap = ArgumentParser()
    ap.add_argument('--source', required=True, type=Path)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    for rel, pin in PINS.items():
        need(hashlib.sha256((args.source / rel).read_bytes()).hexdigest() == pin, 'source pin: ' + rel)
    entries = json.loads((args.source / 'recipe/ENTRIES.json').read_text())
    need([(x['helper'], x['cut']) for x in entries[:2]] == [(608, 10535), (609, 10535)], 'common staged-entry source cut')
    words = {}
    for name, pin in CANONICAL.items():
        words[name] = json.loads(gzip.decompress((args.source / ('inputs/' + name + '.json.gz')).read_bytes()))
        need(digest(words[name]) == pin, 'canonical source pin: ' + name)
    spec = importlib.util.spec_from_file_location('pinned_frame_accountant', args.source / 'vendor/audit_core.py')
    core = importlib.util.module_from_spec(spec)
    # Compile exact bytes: no bytecode file, package import, or additional source read.
    exec(compile((args.source / 'vendor/audit_core.py').read_bytes(), 'pinned audit_core.py', 'exec'), core.__dict__)
    result = {
        'status': 'PASS_SCOPED_SUM_RELEASE_AND_TWO_CHANNEL_OBSTRUCTION',
        'source_pr': 4076, 'source_head': SOURCE_HEAD, 'required_source_sha256': PINS,
        'providers': {p: run_provider(words['NEW-' + p], words['OLD-' + p], entries, core) for p in ('base', 'extra')},
        'scope': 'Two exact finite NEW providers. No owner walk, native phases, physical hosting, source-window reuse, all-size theorem, or kappa improvement is established.',
    }
    text = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.out:
        args.out.write_text(text)
    print(json.dumps({'status': result['status'], 'providers': list(result['providers']),
                      'minor': '1/4', 'natural_R_recovery_rank': 0,
                      'frame_profile_delta': {}, 'width_inventory_delta': {},
                      'scalar_adds_delta': 2, 'controls_rejected': 10}, sort_keys=True))


if __name__ == '__main__':
    main()
