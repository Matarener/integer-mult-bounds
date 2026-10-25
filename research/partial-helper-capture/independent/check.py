#!/usr/bin/env python3
"""Separate exact local matrix proof and complete BORROW-WORD frame invoice.

No project module is imported. GF(2) frames use reduced row bases, rather than
the point-set bit masks in the PR4076 contract reference. Rational matrices are
composed from elementary row operations on all six independent dirty inputs.
The imported-source format/cleanup contract was read, not independently invented.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
FULL = tuple(1 << k for k in range(8, -1, -1))
N = 704
TARGETS = range(112, 224)
LOCAL = (600, 601, 123, 175, 183, 202)
EXPECTED = {
    "base": "08e6c96fbe3dfec96cb8451b3867ef8c1a214109ecd1e5af7fcc28e0f05728d0",
    "extra": "d83c2ec9cecc0ad092d34ea4080b28a4fd7199579356b6d5a8fc6cd53ff93299",
}


class Invalid(Exception):
    pass


def need(value, description):
    if not value:
        raise Invalid(description)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest_json(value):
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def row_basis(vectors):
    pivots = {}
    for vector in vectors:
        need(type(vector) is int and 0 <= vector < 512, "GF(2) vector outside nine bits")
        x = vector
        for p in sorted(pivots, reverse=True):
            if x & (1 << p):
                x ^= pivots[p]
        if x:
            p = x.bit_length() - 1
            for q in list(pivots):
                if pivots[q] & (1 << p):
                    pivots[q] ^= x
            pivots[p] = x
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def contained(small, large):
    return all(row_basis((*large, v)) == large for v in small)


def hyperplane(port):
    need(type(port) is int and 0 < port < 512, "nonzero port required")
    pivot = (port & -port).bit_length() - 1
    return row_basis((1 << j) ^ ((1 << pivot) if port & (1 << j) else 0)
                     for j in range(9) if j != pivot)


def operands(g):
    need(g[0] in ("add", "scale"), "unknown scalar gate")
    return g[1:3] if g[0] == "add" else g[1:2]


def basis_image(columns, frame, inverse=False):
    need(len(columns) == 9 and row_basis(columns) == FULL, "noninvertible warp")

    def image(x):
        result = 0
        for j in range(9):
            if x & (1 << j):
                result ^= columns[j]
        return result

    if inverse:
        lookup = {image(x): x for x in range(512)}
        return row_basis(lookup[x] for x in frame)
    return row_basis(image(x) for x in frame)


def audit_gate(g, current, stage, index, ledger):
    frame = row_basis(g[-1])
    for r in operands(g):
        need(r in current, f"absent scalar operand {r}")
        old = current[r]
        need(contained(old, frame), f"frame descent at {stage}:{index}, operand {r}")
        rank = len(frame) - len(old)
        if rank:
            ledger.append([r, stage, index, rank, list(old), list(frame)])
        current[r] = frame


def frame_invoice(w):
    need((w['report']['v'], w['report']['R'], w['report']['h']) == (112, 480, 9),
         "fixed geometry")
    removed = set(w['removed'])
    need(len(removed) == len(w['removed']) and removed <= set(range(224, N)),
         "removed helper set")
    live = sorted(set(range(N)) - removed)
    starts = {}
    ends = {}
    for r in live:
        starts[r] = row_basis([w['ports'][r]]) if r < 112 else ()
        ends[r] = hyperplane(w['ports'][r - 112]) if r in TARGETS else FULL
    for key, frame in w['start_extra'].items():
        r = int(key)
        need(r in starts and r >= 224, "helper entrance register")
        starts[r] = row_basis(frame)
    for key, frame in w['helper_final'].items():
        r = int(key)
        need(r in ends and r >= 224, "helper terminal register")
        ends[r] = row_basis(frame)
    current = dict(starts)
    paid = []
    warps = w['warps']
    for pos, r, cols, old, new in warps:
        need(0 <= pos <= len(w['B']) and r in current and r not in TARGETS,
             "native warp address")
        need(len(row_basis(old)) == len(old) == len(new) == len(row_basis(new)),
             "warp frame dimensions")
        need(basis_image(cols, row_basis(old)) == row_basis(new), "warp frame image")
    for i, g in enumerate(w['A']):
        if g[0] == 'warp':
            need(i < w['prelude_events'] and len(g) == 5, "prelude warp record")
            _, r, operator, old, new = g
            need(0 < abs(operator) <= len(warps), "prelude operator index")
            rec = warps[abs(operator) - 1]
            need(rec[1] == r and current[r] == row_basis(old), "prelude warp entrance")
            need(basis_image(rec[2], row_basis(old), operator < 0) == row_basis(new),
                 "prelude warp action")
            current[r] = row_basis(new)
        else:
            if i < w['prelude_events']:
                need(g[1] in TARGETS, "prelude writes helper")
            audit_gate(g, current, 'A', i, paid)
    levels = {112 + int(k): row_basis(v) for k, v in w['target_levels'].items()}
    need(all(current[r] == levels.get(r, ()) for r in TARGETS), "cut target frames")
    for r, entry in zip(w['centers'], w['center_frames']):
        cursor = row_basis(entry)
        need(current[r] == cursor, "center entrance")
        served = {levels.get(g[1], ()) for g in w['cut'] if g[2] == r}
        for destination in sorted(served, key=lambda b: (-len(b), b)):
            need(contained(destination, cursor), "nested center service frames")
            rank = len(cursor) - len(destination)
            if rank:
                paid.append([r, 'center-service', None, rank,
                             list(cursor), list(destination)])
            cursor = destination
    indexed = {}
    for i, rec in enumerate(warps):
        indexed.setdefault(rec[0], []).append((i, rec))
    block_boundaries = {}
    for pos in range(len(w['B']) + 1):
        for k, (_, r, _, old, new) in indexed.get(pos, []):
            need(current[r] == row_basis(old), f"native warp entrance {k + 1}")
            current[r] = row_basis(new)
        if pos in (77, 85):
            block_boundaries[pos] = {r: current[r] for r in LOCAL}
        if pos < len(w['B']):
            audit_gate(w['B'][pos], current, 'B', pos, paid)
    for i, g in enumerate(w['restore']):
        audit_gate(g, current, 'restore', i, paid)
    for r in live:
        need(contained(current[r], ends[r]), f"terminal containment {r}")
        rank = len(ends[r]) - len(current[r])
        if rank:
            paid.append([r, 'terminal', None, rank, list(current[r]), list(ends[r])])
        current[r] = ends[r]
    # The literal tail executes at FULL or on terminal-helper backing buffers;
    # these inverse records are scalar operations, not fresh frame promotions.
    histogram = Counter(record[3] for record in paid)
    widths = Counter(len(ends[r]) - len(starts[r]) for r in live if r >= 224)
    need(all(width >= 0 for width in widths), "negative endpoint width")
    return {
        'profile': dict(sorted(histogram.items())),
        'widths': dict(sorted(widths.items())),
        'paid': paid,
        'starts': starts,
        'ends': ends,
        'block_boundaries': block_boundaries,
    }


def local_matrix(gates):
    rows = [[Fraction(i == j) for j in range(6)] for i in range(6)]
    coordinates = {r: i for i, r in enumerate(LOCAL)}
    for g in gates:
        need(g[0] == 'add' and g[1] in coordinates and g[2] in coordinates,
             "local matrix gate")
        t, s = coordinates[g[1]], coordinates[g[2]]
        q = Fraction(g[3], g[4])
        rows[t] = [a + q * b for a, b in zip(rows[t], rows[s])]
    return rows


def expected_matrix():
    answer = [[Fraction(i == j) for j in range(6)] for i in range(6)]
    for i, sign in [(2, -1), (3, 1), (4, 1), (5, -1)]:
        answer[i][0] = Fraction(sign, 4)
        answer[i][1] = Fraction(1, 4)
    return answer


def candidate_block(original):
    need(original == [
        ['add', 183, 600, 1, 4, [45]], ['add', 202, 600, -1, 4, [45]],
        ['add', 175, 600, 1, 4, [45]], ['add', 123, 600, -1, 4, [45]],
        ['add', 183, 601, 1, 4, [45]], ['add', 202, 601, 1, 4, [45]],
        ['add', 175, 601, 1, 4, [45]], ['add', 123, 601, 1, 4, [45]],
    ], "source block differs from pinned signed columns")
    return [deepcopy(original[i]) for i in (1, 3, 5, 7)] + [
        ['add', 600, 601, 1, 1, [45]],
        ['add', 183, 600, 1, 4, [45]],
        ['add', 175, 600, 1, 4, [45]],
        ['add', 600, 601, -1, 1, [45]],
    ]


def ordinary_actions(w):
    actions = deepcopy(w['A'][w['prelude_events']:])
    indexed = {}
    for k, rec in enumerate(w['warps'], 1):
        indexed.setdefault(rec[0], []).append(['warp', rec[1], k])
    for i in range(len(w['B']) + 1):
        actions.extend(indexed.get(i, []))
        if i < len(w['B']):
            actions.append(w['B'][i])
    actions.extend(w['restore'])
    return actions


def literal_cleanup(w):
    restored = set(map(int, w['helper_final']))

    def backing(r):
        return r + N if r in restored else r

    answer = []
    for g in reversed(ordinary_actions(w)):
        if g[0] == 'warp':
            answer.append(['warp', backing(g[1]), -g[2], list(FULL)])
        elif g[1] in TARGETS:
            continue
        elif g[0] == 'add':
            answer.append(['add', backing(g[1]), backing(g[2]), -g[3], g[4], list(FULL)])
        else:
            need(g[0] == 'scale', "unknown cleanup inverse")
            answer.append(['scale', backing(g[1]), g[3], g[2], list(FULL)])
    return answer


def normalized_tail(gates):
    return [(*g[:-1], row_basis(g[-1])) for g in gates]


def cancel_added_pair(tail, old_tail):
    plus = ['add', 600, 601, 1, 1, list(FULL)]
    minus = ['add', 600, 601, -1, 1, list(FULL)]
    hits = [i for i in range(len(tail) - 1) if tail[i:i + 2] == [plus, minus]]
    need(len(hits) == 1, "unique added adjacent inverse cleanup pair")
    i = hits[0]
    reduced = tail[:i] + tail[i + 2:]
    need(normalized_tail(reduced) == normalized_tail(old_tail), "canceled cleanup equals source")
    return reduced, i


def op_counts(w):
    answer = {}
    totals = Counter()
    sources = {r: {'reads': 0, 'writes': 0} for r in (600, 601)}
    for name in ('precondition', 'compensation', 'A', 'cut', 'B', 'restore', 'cleanup'):
        ops = Counter(g[0] for g in w[name])
        stage_sources = {str(r): {'reads': 0, 'writes': 0} for r in sources}
        answer[name] = {'operations': dict(sorted(ops.items())), 'source_access': stage_sources}
        totals.update(ops)
        for g in w[name]:
            for r in sources:
                if g[0] == 'add' and g[2] == r:
                    sources[r]['reads'] += 1
                    stage_sources[str(r)]['reads'] += 1
                if g[1] == r:
                    sources[r]['writes'] += 1
                    stage_sources[str(r)]['writes'] += 1
    answer['totals_excluding_native_warps_and_corrections'] = dict(sorted(totals.items()))
    answer['native_warps'] = len(w['warps'])
    answer['initial_corrections'] = len(w['initial_corrections'])
    answer['total_executed_records'] = sum(len(w[name]) for name in (
        'precondition', 'compensation', 'A', 'cut', 'B', 'restore', 'cleanup')) \
        + len(w['warps']) + len(w['initial_corrections'])
    answer['source_reads_and_writes'] = sources
    return answer


def count_local(gates):
    return {
        'adds': len(gates),
        'source_reads': {str(r): sum(g[2] == r for g in gates) for r in (600, 601)},
        'source_writes': {str(r): sum(g[1] == r for g in gates) for r in (600, 601)},
        'target_writes': sum(g[1] in TARGETS for g in gates),
    }


def rejected(action):
    try:
        action()
    except Invalid:
        return True
    return False


def controls(original, candidate, w):
    target = expected_matrix()
    bad_sign = deepcopy(candidate)
    bad_sign[5][3] = -1
    wrong_capture = deepcopy(candidate)
    wrong_capture[4][3] = -1
    missing_undo = candidate[:-1]
    bad_frame = deepcopy(w)
    bad_frame['B'][77:85] = deepcopy(candidate)
    bad_frame['B'][81][-1] = [46]
    # A fresh ZERO-frame recipient is legal, but its [45]-frame read-only
    # source cannot be silently admitted at ZERO. This isolates source access.
    control_frames = {700: (), 600: row_basis([45])}
    control_gate = ['add', 700, 600, 1, 1, []]
    bad_inverse = [g for g in reversed(candidate) if g[1] not in TARGETS]
    bad_inverse = deepcopy(bad_inverse)
    for g in bad_inverse:
        g[3] = -g[3]
    bad_inverse[-1][3] *= -1
    only_source_forward = [g for g in candidate if g[1] not in TARGETS]
    identity = [[Fraction(i == j) for j in range(6)] for i in range(6)]
    result = {
        'wrong_agreeing_target_sign_rejected': local_matrix(bad_sign) != target,
        'wrong_capture_sign_rejected': local_matrix(wrong_capture) != target,
        'missing_undo_rejected_on_arbitrary_dirty_sources': local_matrix(missing_undo) != target,
        'wrong_common_frame_rejected': rejected(lambda: frame_invoice(bad_frame)),
        'unpaid_read_only_source_frame_rejected': rejected(
            lambda: audit_gate(control_gate, control_frames, 'control', 0, [])),
        'wrong_cleanup_inverse_sign_rejected':
            local_matrix(only_source_forward + bad_inverse) != identity,
        'clean_zero_sources_do_not_detect_missing_undo':
            all(row[j] == target[i][j] for i, row in enumerate(local_matrix(missing_undo))
                for j in range(2, 6)),
    }
    need(all(result.values()), "one defect-sensitive control failed")
    return result


def load_word(name, manifest):
    rel = f'predecessor4061/frozen/WORD-{name}.json.gz'
    data = (ROOT / rel).read_bytes()
    recs = [s for s in manifest['sources'] if s['local_path'] == rel]
    need(len(recs) == 1, "source export does not identify one frozen word")
    record = recs[0]
    need(sha(data) == EXPECTED[name] == record['sha256'], "frozen word SHA-256")
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    need(blob == record['git_blob'], "frozen word Git blob")
    return json.loads(gzip.decompress(data)), {
        'sha256': sha(data), 'git_blob': blob, 'head': record['head'],
        'original_path': record['original_path'],
    }


def verify_word(name, manifest):
    w, source = load_word(name, manifest)
    need(all(rec[1] not in (600, 601) for rec in w['warps']),
         "capture helpers have no uncounted native-warp accesses")
    need(all(rec['source'] not in (600, 601) for rec in w['initial_corrections']),
         "capture helpers have no uncounted initial-correction reads")
    original = w['B'][77:85]
    candidate = candidate_block(original)
    target = expected_matrix()
    need(local_matrix(original) == target == local_matrix(candidate),
         "complete 36-entry dirty-input rational matrix identity")
    source_only = [g for g in candidate if g[1] not in TARGETS]
    identity = [[Fraction(i == j) for j in range(6)] for i in range(6)]
    need(local_matrix(source_only) == identity, "source subword identity")
    literal_old = literal_cleanup(w)
    need(normalized_tail(literal_old) == normalized_tail(w['cleanup']),
         "source literal inverse recipe")
    changed = deepcopy(w)
    changed['B'][77:85] = candidate
    changed['cleanup'] = literal_cleanup(changed)
    reduced_tail, cancellation_index = cancel_added_pair(changed['cleanup'], w['cleanup'])
    reduced = deepcopy(changed)
    reduced['cleanup'] = reduced_tail
    a = frame_invoice(w)
    b = frame_invoice(changed)
    need(a['profile'] == b['profile'], "full native child profile unchanged")
    need(a['widths'] == b['widths'], "all helper widths unchanged")
    need(a['starts'] == b['starts'] and a['ends'] == b['ends'], "all external boundaries unchanged")
    # Stable sorting groups registers while retaining each chronological path.
    paths_a = sorted([[r, rank, old, new] for r, _, _, rank, old, new in a['paid']],
                     key=lambda rec: rec[0])
    paths_b = sorted([[r, rank, old, new] for r, _, _, rank, old, new in b['paid']],
                     key=lambda rec: rec[0])
    need(paths_a == paths_b, "every positive native climb remains")
    need(a['block_boundaries'] == b['block_boundaries'], "six block boundary frames unchanged")
    entry = a['block_boundaries'][77]
    exit_frames = a['block_boundaries'][85]
    need(all(entry[r] == row_basis([45]) for r in (600, 601)), "block source entry frames")
    need(all(entry[r] == () for r in (123, 175, 183, 202)), "block target entry frames")
    need(all(exit_frames[r] == row_basis([45]) for r in LOCAL), "block exit frames")
    local_paid_a = [rec for rec in a['paid'] if rec[1] == 'B' and 77 <= rec[2] < 85]
    local_paid_b = [rec for rec in b['paid'] if rec[1] == 'B' and 77 <= rec[2] < 85]
    need(Counter(rec[3] for rec in local_paid_a) == Counter({1: 4})
         == Counter(rec[3] for rec in local_paid_b), "four unavoidable local target climbs")
    need(a['profile'] == {int(k): v for k, v in w['report']['local_profile'].items()},
         "independently reconstructed native profile matches frozen report")
    need(a['widths'] == {int(k): v for k, v in w['report']['width_inventory'].items()},
         "independently reconstructed helper widths match frozen report")
    source_chains = {}
    for r in (600, 601):
        before = [rec for rec in a['paid'] if rec[0] == r]
        after = [rec for rec in b['paid'] if rec[0] == r]
        need(before == after, "paid source visits unchanged, including chronological addresses")
        need(a['starts'][r] == row_basis([45]) and a['ends'][r] == FULL,
             "source entrance and terminal frame")
        source_chains[r] = {'entrance': [45], 'terminal': list(FULL), 'paid_visits': before}
    tail_pair = changed['cleanup'][cancellation_index:cancellation_index + 2]
    need(local_matrix(tail_pair) == identity, "added full-frame inverse pair cancels on dirty inputs")
    # These two statements are deliberately distinct: algebraic sufficiency
    # after cancellation does not mean equality to the literal recipe.
    need(normalized_tail(changed['cleanup']) != normalized_tail(w['cleanup']),
         "literal recipe must detect the omitted adjacent pair")
    need(normalized_tail(reduced['cleanup']) == normalized_tail(w['cleanup']),
         "canceled recipe equals old cleanup exactly")
    source_stages = {}
    for label, word in [('original', w), ('literal_capture', changed), ('canceled_capture', reduced)]:
        source_stages[label] = op_counts(word)
    return {
        'source': source,
        'matrix_coordinates': list(LOCAL),
        'matrix_entry_coverage': 36,
        'matrix': [[str(x) for x in row] for row in target],
        'original_block': original,
        'candidate_block': candidate,
        'local_operation_counts': {'before': count_local(original), 'after': count_local(candidate)},
        'literal_cleanup_records_before': len(w['cleanup']),
        'literal_cleanup_records_after': len(changed['cleanup']),
        'canceled_cleanup_records_after': len(reduced['cleanup']),
        'added_cleanup_pair_index': cancellation_index,
        'added_cleanup_pair': tail_pair,
        'old_cleanup_semantically_sufficient_after_exact_pair_cancellation': True,
        'old_cleanup_equals_unsimplified_literal_recipe': False,
        'native_profile': a['profile'],
        'helper_width_inventory': a['widths'],
        'positive_native_climb_count': len(a['paid']),
        'positive_native_rank_mass': sum(g[3] for g in a['paid']),
        'all_positive_climbs_per_register_unchanged': True,
        'positive_climb_signature_sha256': digest_json(paths_a),
        'all_external_frames_unchanged': True,
        'block_boundary_frames': {
            'entry': {str(k): list(v) for k, v in entry.items()},
            'exit': {str(k): list(v) for k, v in exit_frames.items()},
        },
        'block_paid_climbs_before': local_paid_a,
        'block_paid_climbs_after': local_paid_b,
        'block_minimum_profile_under_fixed_monotone_boundaries': {1: 4},
        'paid_source_visits': source_chains,
        'operation_invoice': source_stages,
        'defect_sensitive_controls': controls(original, candidate, w),
    }


def report():
    manifest_bytes = (ROOT / 'SOURCE-EXPORT.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    words = {name: verify_word(name, manifest) for name in EXPECTED}
    need(words['base']['matrix'] == words['extra']['matrix'], "both frozen words local matrix")
    return {
        'schema_version': 1,
        'result': 'EXACT_PARTIAL_CAPTURE_WITH_ZERO_NATIVE_PROFILE_GAIN',
        'coverage': 'Two pinned finite words; exact rational local operator on arbitrary dirty inputs; complete native-frame and helper-width invoice under the BORROW-WORD contract.',
        'physical_lift': 'All eight replaced ADDs and all eight candidate ADDs use the identical [45] representative; exact logical matrix equality gives exact physical equality for any fixed invertible T_[45].',
        'universal_cost_comparison_scope': 'The explicit rewrite retains every positive native climb and endpoint width, so every price depending on that invoice is unchanged. More generally, monotone scalar rewrites at the same six block-boundary frames require all four ZERO-to-[45] target climbs, hence at least four rank-1 children. The original and explicit capture attain that local minimum. No global claim with changed external boundaries or paid itinerary is made.',
        'unresolved': 'Changed entrances or terminals, larger source sets, cross-block retiming, other child/hosting contracts, and global resynthesis are not excluded. No physical supplier, full recurrence improvement or new kappa is established.',
        'source_export_sha256': sha(manifest_bytes),
        'implementation_sha256': sha(Path(__file__).read_bytes()),
        'contract_reference': 'source4076/vendor/audit_core.py was read for BORROW-WORD frame/cleanup semantics; no project module imported. RREF arithmetic and local matrix evaluation implemented separately.',
        'words': words,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Write verified JSON to this absolute path; otherwise compare independent/RESULT.json without writing.')
    args = parser.parse_args()
    result = report()
    serialized = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output is not None:
        need(args.output.is_absolute(), '--output must be absolute')
        args.output.write_text(serialized)
    else:
        expected = (HERE / 'RESULT.json').read_text()
        need(serialized == expected, 'current calculation differs from independent/RESULT.json')
    print('PASS_PARTIAL_CAPTURE_INDEPENDENT')


if __name__ == '__main__':
    main()
