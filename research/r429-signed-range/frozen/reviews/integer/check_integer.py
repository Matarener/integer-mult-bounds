#!/usr/bin/env python3
"""Independent dense exact audit of the fixed R429 signed-quotient witness.

Python 3.12 standard library only.  No producer or historical replayer import.
The input word is authenticated before semantic mutation controls are made.
All paths are explicit; no checkout, Git, home directory, or network is used.
Apache-2.0. Substantial OpenAI Codex assistance; not formal-kernel evidence.
"""

import argparse
from collections import Counter
import gzip
import hashlib
from itertools import combinations
import json
from math import gcd
from pathlib import Path

V, N = 111, 651
PINS = {
    "parent_word": "1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870",
    "signed_word": "e802611104c61fc8477837b4ab41abc4f13cf41fbca6ef3de60d0b5e768fb949",
    "raw_word": "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
    # The original uncompressed JSON bytes, allowing a lossless gzip wrapper.
    "matrices": "e5edb9e4e738192f98bd520ae6c1e8f1ddb19a0074ee9a1044e309b81e39c979",
}
PROFILE = {1: 1298, 2: 1342, 3: 79, 4: 44, 5: 93, 6: 11, 7: 9}
COUNTS = {0: 2873, 1: 13223, 2: 3, 3: 3}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def read_pinned(path, label):
    packed = path.read_bytes()
    decoded = gzip.decompress(packed) if packed.startswith(b"\x1f\x8b") else packed
    authenticated = decoded if label == "matrices" else packed
    require(digest(authenticated) == PINS[label], "authentication: " + label)
    value = json.loads(decoded)
    # For matrices the compression wrapper is intentionally not proof-relevant.
    return value, {
        "authenticated_sha256": digest(authenticated),
        "decoded_bytes_sha256": digest(decoded),
        "canonical_json_sha256": digest(canonical(value)),
        "authenticated_representation": "decoded original JSON bytes"
        if label == "matrices" else "frozen gzip bytes",
    }


def integer_rank(matrix):
    """Exact rational rank by fraction-free row elimination and gcd reduction."""
    pivots = {}
    for original in matrix:
        row = original[:]
        for p, basis in sorted(pivots.items()):
            if row[p]:
                a, b = basis[p], row[p]
                row = [a * x - b * y for x, y in zip(row, basis)]
                common = 0
                for x in row:
                    common = gcd(common, x)
                if common:
                    row = [x // common for x in row]
        p = next((j for j, x in enumerate(row) if x), None)
        if p is not None:
            common = 0
            for x in row:
                common = gcd(common, x)
            if row[p] < 0:
                common = -common
            pivots[p] = [x // common for x in row]
    return len(pivots)


def binary_rank(matrix):
    basis = {}
    for value in matrix:
        while value:
            p = value.bit_length() - 1
            if p not in basis:
                basis[p] = value
                break
            value ^= basis[p]
    return len(basis)


def binary_product(left, right):
    result = []
    for mask in left:
        row = 0
        for j, value in enumerate(right):
            if mask & (1 << j):
                row ^= value
        result.append(row)
    return result


def binary_inverse(matrix):
    n = len(matrix)
    left, right = matrix[:], [1 << j for j in range(n)]
    for p in range(n):
        q = next((j for j in range(p, n) if left[j] & (1 << p)), None)
        require(q is not None, "binary code singular")
        left[p], left[q] = left[q], left[p]
        right[p], right[q] = right[q], right[p]
        for j in range(n):
            if j != p and left[j] & (1 << p):
                left[j] ^= left[p]
                right[j] ^= right[p]
    require(left == [1 << j for j in range(n)], "binary inverse reduction")
    return right


def dense_identity(n=N, private=True):
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    return rows + [[0] * n] if private else rows


def parity(rows):
    return [sum((x & 1) << j for j, x in enumerate(row)) for row in rows]


def matrix_digest(rows):
    """SHA256 of each dense signed decimal row, comma-separated, then LF."""
    h = hashlib.sha256()
    for row in rows:
        h.update((",".join(map(str, row)) + "\n").encode())
    return h.hexdigest()


def first_difference(left, right):
    for i, (a, b) in enumerate(zip(left, right)):
        for j, (x, y) in enumerate(zip(a, b)):
            if x != y:
                return {"output_row": i, "input_column": j, "expected": y, "actual": x}
    return None


def integer_product(left, right):
    columns = list(zip(*right))
    return [[sum(x * y for x, y in zip(row, column)) for column in columns] for row in left]


def determinant(matrix):
    """Bareiss determinant, with every claimed integer division checked."""
    a = [r[:] for r in matrix]
    n, previous, sign = len(a), 1, 1
    for p in range(n - 1):
        q = next((j for j in range(p, n) if a[j][p]), None)
        if q is None:
            return 0
        if p != q:
            a[p], a[q], sign = a[q], a[p], -sign
        pivot = a[p][p]
        for i in range(p + 1, n):
            for j in range(p + 1, n):
                numerator = pivot * a[i][j] - a[i][p] * a[p][j]
                require(numerator % previous == 0, "Bareiss exact division")
                a[i][j] = numerator // previous
            a[i][p] = 0
        previous = pivot
    return sign * a[-1][-1]


def value_segment(records, rows):
    """Linear transfer for a complete-snapshot segment, any column width."""
    rows = [row[:] for row in rows]
    width, source, snapshot = len(rows[0]), None, None
    for op, d, s, c, f, phase in records:
        if op == 1:
            require(d < N and d != source, "segment immutable source/private")
            rows[d] = [x + c * y for x, y in zip(rows[d], rows[s])]
        elif op == 2:
            require(source is None and s == N and not any(rows[N]), "segment fresh COPY")
            source, snapshot = d, rows[d][:]
            rows[N] = snapshot[:]
        elif op == 3:
            require(source == d and s == N and rows[N] == rows[d] == snapshot,
                    "segment immutable ERASE")
            rows[N], source, snapshot = [0] * width, None, None
        else:
            require(op == 0, "segment opcode")
    require(source is None and not any(rows[N]), "segment private boundary")
    return rows


def quotient_matrix(records, pivots):
    index = {p: j for j, p in enumerate(pivots)}
    result = []
    for backward in (False, True):
        rows = dense_identity(9, private=False)
        peak = 1
        for op, d, s, c, f, phase in reversed(records) if backward else records:
            require(op == 1 and d in index and s in index and f == 1 and phase == 23,
                    "quotient nine-coordinate alphabet")
            c = -c if backward else c
            dst, src = index[d], index[s]
            rows[dst] = [x + c * y for x, y in zip(rows[dst], rows[src])]
            peak = max(peak, sum(map(abs, rows[dst])))
        require(determinant(rows) == 1, "quotient elementary determinant")
        result.append({"matrix": rows, "prefix_row_l1": peak,
                       "endpoint_row_l1": max(sum(map(abs, row)) for row in rows),
                       "determinant": 1, "sha256": matrix_digest(rows)})
    require(integer_product(result[0]["matrix"], result[1]["matrix"]) ==
            dense_identity(9, private=False), "quotient integer inverse")
    return {"forward": result[0], "inverse": result[1]}


def sign_family_transfer(parent, signed, parent_endpoint, signed_endpoint):
    positions = [i for i, r in enumerate(signed) if r[0] == 1 and r[5] == 23]
    start, stop = positions[0], positions[-1] + 1
    require(positions == list(range(start, stop)), "quotient block must be contiguous")
    pivots = sorted({signed[i][j] for i in positions for j in (1, 2)})
    require(pivots == [0, 1, 2, 4, 8, 9, 14, 30, 59], "nine actual quotient source coordinates")
    require(parent[:start] == signed[:start] and parent[stop:] == signed[stop:],
            "fixed literal prefix/suffix")
    prefix = value_segment(signed[:start], dense_identity())
    reader_full = [prefix[p] for p in pivots]
    require(all(not any(row[V:]) for row in reader_full), "quotient reader has dirty/target dependence")
    reader = [row[:V] for row in reader_full]
    require([[row[p] for p in pivots] for row in reader] == dense_identity(9, private=False),
            "prefix reader does not have the selected-coordinate right inverse")
    embedding = [[int(i == p) for p in pivots] for i in range(N + 1)]
    transfer = value_segment(signed[stop:], embedding)
    require(transfer[:V] == embedding[:V], "suffix source transfer is not the coordinate embedding")
    require(all(not any(row) for row in transfer[V + 3:]), "suffix variation escapes repaired targets")
    ell = transfer[V:V + 3]
    require(integer_rank(ell) == 3, "three-target transfer rank")
    minor_columns = next(c for c in combinations(range(9), 3)
                         if determinant([[row[j] for j in c] for row in ell]))
    minor_det = determinant([[row[j] for j in minor_columns] for row in ell])
    quotients = {"parent": quotient_matrix(parent[start:stop], pivots),
                 "signed": quotient_matrix(signed[start:stop], pivots)}
    dq = [[x - y for x, y in zip(a, b)] for a, b in zip(
        quotients["signed"]["forward"]["matrix"], quotients["parent"]["forward"]["matrix"])]
    delta_readers = integer_product(dq, reader)
    predicted = integer_product(transfer, delta_readers)
    require([[x - y for x, y in zip(a, b)] for a, b in zip(signed_endpoint, parent_endpoint)] ==
            [row + [0] * (N - V) for row in predicted], "full endpoint difference factorization")
    require(determinant(dq) != 0, "current nine-dimensional quotient difference rank")
    return {
        "cut": {"prefix_records": start, "quotient_start_zero_based": start,
                "quotient_stop_exclusive": stop, "quotient_records": stop - start,
                "suffix_records": len(signed) - stop},
        "pivot_source_indices": pivots,
        "prefix_reader_B": reader, "prefix_reader_B_full_sha256": matrix_digest(reader_full),
        "prefix_reader_has_no_target_or_dirty_columns": True,
        "B_on_pivot_columns_equals_I9": True,
        "suffix_transfer_sha256": matrix_digest(transfer),
        "suffix_source_transfer_equals_embedding_U": True,
        "suffix_target_transfer_L": ell,
        "L_full_rank_minor_columns": list(minor_columns), "L_full_rank_minor_determinant": minor_det,
        "suffix_other_targets_helpers_and_private_transfer_zero": True,
        "quotients": quotients,
        "current_delta_Q": dq,
        "current_delta_Q_determinant": determinant(dq),
        "current_delta_Q_rank": 9,
        "universal_difference_law": "Delta A_Z = U * Delta Q * B; "
        "Delta T_Z = P_3 * L * Delta Q * B; Delta E_Z=0; other public blocks unchanged.",
        "universal_rank_laws_over_Q": "rank(Delta A_Z)=rank(Delta Q)<=9; "
        "rank(Delta T_Z)=rank(L*Delta Q)<=3, since B has the displayed right inverse.",
        "universal_source_delta_support": pivots,
        "universal_target_delta_support_subset": [0, 1, 2],
        "all_sign_assignments": 1 << 47,
        "family_scope": "All 2^47 choices of +/-1 coefficients in the existing ordered 47 ADDs. "
        "Each quotient is an integer determinant-one product; all have the same reduction mod2. "
        "The finite prefix/transfer certificate plus linear factorization proves the family law; "
        "the sign assignments are not enumerated.",
        "family_integer_restoration": "Every assignment restores all 429 arbitrary helpers, "
        "has source depending only on x, target self block I, unchanged even E_Z, and closed private "
        "snapshots. The same frame paths and paid profile are retained.",
        "general_matrix_scope": "The difference formula also holds for any substituted 9x9 "
        "integer Q. Invertibility and F2 endpoint require separate conditions on Q. Such a "
        "substitution is not asserted to have the same 47-gate implementation or cost.",
        "not_universal": "Current exact delta ranks9 and3, and all prefix/endpoint norms, are "
        "facts of the two fixed witnesses, not constants throughout the sign family.",
    }


def raw_binary_code(raw, frozen):
    require(raw["v"] == V and raw["R"] == 438, "raw register dimensions")
    rows = [1 << j for j in range(660)]
    for phase in ("D", "A"):
        for frame, dst, sources in raw[phase]:
            require(0 <= dst < 660, "raw destination")
            for src in sources:
                require(0 <= src < 660 and src != dst, "raw source")
                rows[dst] ^= rows[src]
    source_mask = (1 << V) - 1
    target_mask = source_mask << V
    require(all(not rows[j] & target_mask for j in raw["ret"]), "raw retained target dependence")
    r = [rows[j] & source_mask for j in raw["ret"]]
    k = []
    for subset in raw["scatter"]:
        require(len(set(subset)) == len(subset), "duplicate raw scatter")
        require(all(0 <= j < 9 for j in subset), "raw scatter index")
        k.append(sum(1 << j for j in subset))
    require(r == frozen["matrices"]["R"] and k == frozen["matrices"]["K"],
            "frozen R/K differs from direct raw derivation")
    require(len(r) == 9 and len(k) == V, "R/K dimensions")
    w = [0, 0, 0] + k[3:]
    a = [(1 << j) ^ row for j, row in enumerate(binary_product(w, r))]
    ai = binary_inverse(a)
    ident = [1 << j for j in range(V)]
    require(binary_product(a, ai) == binary_product(ai, a) == ident, "two-sided binary inverse")
    jmat = [(1 << j) ^ row for j, row in enumerate(binary_product(k, r))]
    require(binary_rank(r) == 9 and binary_rank(jmat) == 108, "raw R/J ranks")
    require(binary_rank([x ^ y for x, y in zip(a, ident)]) == 9, "rank(A-I)")
    return a, ai, {
        "derivation": "Raw D then A on all 660 F2 columns; retained source rows give R; "
        "raw scatter gives K; W equals K with rows 0,1,2 zero; A=I+WR.",
        "R_rows": r, "K_rows": k, "A_rows": a, "A_inverse_rows": ai,
        "rank_R": 9, "rank_J": 108, "rank_A_minus_I": 9,
        "A_sha256": digest(canonical(a)), "A_inverse_sha256": digest(canonical(ai)),
    }


class Geometry:
    def __init__(self, raw, word):
        roots, frames = raw["lines"], raw["frames"]
        require(len(roots) == V and all(len(r) == 8 for r in roots), "actual root dimensions")
        require(all(sum(x * x for x in r) == 4 for r in roots), "actual root norms")
        self.masks = []
        self.ranks = []
        for f in frames:
            require(f == sorted(set(f)) and all(0 <= j < V for j in f), "frame label set")
            self.masks.append(sum(1 << j for j in f))
            self.ranks.append(integer_rank([roots[j] for j in f]))
        require(self.ranks[0] == 0 and self.ranks[1] == 8, "zero/FULL ranks")
        keep = [j for j in range(660) if j not in range(471, 480)]
        self.start = [raw["start"][j] for j in keep]
        self.final = [raw["final"][j] for j in keep]
        require(word["start"] == self.start and word["final"] == self.final,
                "projected native boundary arrays")
        for p, root in enumerate(roots):
            start = self.start[p]
            cap = self.final[V + p]
            require(self.ranks[start] == 1 and self.ranks[cap] == 7, "actual port line/cap ranks")
            for j in frames[start]:
                dot = sum(x * y for x, y in zip(roots[j], root))
                require(all(4 * x == dot * y for x, y in zip(roots[j], root)), "actual entrance line")
            require(all(sum(x * y for x, y in zip(roots[j], root)) == 0
                        for j in frames[cap]), "actual target cap")
        self.receipt = {
            "frames": len(frames), "ambient_dimension": 8,
            "rank_method": "exact integer fraction-free elimination, with gcd reduction",
            "frame_ranks_sha256": digest(canonical(self.ranks)),
            "start_sha256": digest(canonical(self.start)),
            "final_sha256": digest(canonical(self.final)),
            "actual_line_cap_bindings": 222,
            "native_ADDRESS_identity": "Inherited from pinned PR3645; no physical compiler or "
            "native-vector prefix bound is established by this scalar audit.",
        }


def authenticate_variant(parent, signed):
    require(set(parent) == set(signed), "top-level metadata keys")
    for key in parent:
        if key not in ("records", "format"):
            require(parent[key] == signed[key], "changed metadata: " + key)
    require(parent["format"] == "coded-r429-pruned-three-source-copy-v1", "parent format")
    require(signed["format"] == "coded-r429-signed-quotient-variant-v1", "signed format")
    require(signed["public_registers"] == signed["private_register"] == N, "public/private sizes")
    require(signed["deleted_public_families"] == list(range(471, 480)), "deleted families")
    before, after = parent["records"], signed["records"]
    require(len(before) == len(after) == 16102, "word lengths")
    changed, quotient = [], []
    for i, (a, b) in enumerate(zip(before, after)):
        require(len(b) == 6 and all(type(x) is int for x in b), "literal record schema")
        if b[0] == 1 and b[5] == 23:
            quotient.append(i)
        if a != b:
            require(a[:3] + a[4:] == b[:3] + b[4:] and
                    a[0] == 1 and a[3] == 1 and b[3] == -1 and a[5] == 23,
                    "mutation outside permitted quotient signs")
            changed.append(i)
    require(len(quotient) == 47 and len(changed) == 23, "47 gates / 23 sign changes")
    return {"records": 16102, "quotient_ADDs": 47, "changed_signs": 23,
            "changed_record_indices_zero_based": changed,
            "quotient_signs": [after[i][3] for i in quotient],
            "all_other_records_and_boundaries_identical": True}


def replay(records, geo, backward=False, initial=None, track=True, fault=None):
    rows = dense_identity() if initial is None else [r[:] for r in initial]
    bits = parity(rows)
    frames = (geo.final if backward else geo.start)[:] + [None]
    opened, original_snapshot = None, None
    profile, counts = Counter(), Counter()
    copies, paths = [], [[f] for f in frames]
    prefix = max(sum(map(abs, row)) for row in rows) if track else 0
    maximum = None
    moves = []
    order = range(len(records) - 1, -1, -1) if backward else range(len(records))
    for step, index in enumerate(order):
        op, d, s, c, f, phase = records[index]
        counts[op] += 1
        require(0 <= d <= N, "register destination range")
        if op == 0:
            require(d < N and 0 <= s < len(geo.ranks) and 0 <= c < len(geo.ranks),
                    "MOVE operands")
            old, new = (c, s) if backward else (s, c)
            lo, hi = (s, c)
            require(phase == 0 and frames[d] == old, "MOVE current frame")
            require(not (geo.masks[lo] & ~geo.masks[hi]) and
                    geo.ranks[hi] - geo.ranks[lo] == f > 0, "MOVE containment/rank")
            frames[d] = new
            paths[d].append(new)
            profile[f] += 1
            moves.append([index, d, old, new, f])
        elif op == 1:
            require(d < N, "immutable private field is an ADD destination")
            require(0 <= s <= N and d != s and c in (-1, 1), "ADD operands")
            require(frames[d] == frames[s] == f, "ADD common frame")
            require(d != opened, "copied source changed during snapshot lifetime")
            sign = -c if backward else c
            if fault == ("inverse_sign", index):
                require(backward, "inverse fault direction")
                sign = c
            a, b = rows[d], rows[s]
            rows[d] = [x + y for x, y in zip(a, b)] if sign == 1 else [
                x - y for x, y in zip(a, b)]
            bits[d] ^= bits[s]
            if track:
                size = sum(map(abs, rows[d]))
                if size > prefix:
                    prefix = size
                    maximum = {"record_index_zero_based": index, "execution_step_zero_based": step,
                               "register": d, "row": rows[d][:]}
        elif op == (3 if backward else 2):
            require(opened is None and s == N and not any(rows[N]) and
                    bits[N] == 0 and frames[N] is None, "COPY requires fresh zero private field")
            require(0 <= d < V and frames[d] == c == 1 and
                    not (geo.masks[f] & ~geo.masks[c]) and
                    geo.ranks[c] - geo.ranks[f] == 1, "COPY actual FULL-to-cap rank")
            require(phase == (0 if backward else 1), "COPY rank tag")
            original_snapshot = rows[d][:]
            rows[N], bits[N], frames[N], opened = rows[d][:], bits[d], f, d
            if fault == ("stale_snapshot", index):
                stale = [int(j == d) for j in range(N)]
                require(stale != rows[N], "stale snapshot control is ineffective")
                rows[N], bits[N] = stale, 1 << d
            paths[N].append(f)
            profile[1] += 1
            copies.append({"copy_record_index_zero_based": index, "source": d,
                           "source_frame": c, "private_frame": f, "paid_rank": 1,
                           "snapshot_row_sha256": matrix_digest([original_snapshot])})
        elif op == (2 if backward else 3):
            require(opened == d and s == N and frames[d] == c and frames[N] == f,
                    "ERASE original physical source/frame")
            require(rows[N] == rows[d] == original_snapshot and bits[N] == bits[d],
                    "ERASE private value is not its original unchanged snapshot")
            require(phase == (1 if backward else 0), "ERASE tag")
            copies[-1]["erase_record_index_zero_based"] = index
            rows[N], bits[N], frames[N], opened, original_snapshot = [0] * N, 0, None, None, None
            paths[N].append(None)
        else:
            raise ValueError("unknown opcode")
    require(opened is None and not any(rows[N]) and not bits[N] and frames[N] is None,
            "private endpoint is not zero/closed")
    require(frames[:N] == (geo.start if backward else geo.final), "public endpoint frames")
    require(parity(rows) == bits, "independent integer / F2 replay disagrees")
    result = {
        "prefix_row_l1": prefix, "record_counts": dict(sorted(counts.items())),
        "paid_profile": dict(sorted(profile.items())),
        "paid_children": sum(profile.values()), "rank_mass": sum(k * v for k, v in profile.items()),
        "copies": copies, "maximum_simultaneous_private_snapshots": 1,
        "MOVE_events_sha256": digest(canonical(moves)),
        "all_register_frame_paths_sha256": digest(canonical(paths)),
        "integer_endpoint_sha256": matrix_digest(rows),
        "binary_endpoint_sha256": digest(canonical(bits)),
    }
    return rows, result, maximum


def source_code(records, backward=False):
    code = [r for r in records if r[0] == 1 and r[5] in (21, 22, 23, 24)]
    require(len(code) == 1499, "source-code length")
    rows = dense_identity(V, private=False)
    for _, d, s, c, frame, phase in reversed(code) if backward else code:
        require(0 <= d < V and 0 <= s < V and d != s and frame == 1, "source-only code grammar")
        c = -c if backward else c
        rows[d] = [x + c * y for x, y in zip(rows[d], rows[s])]
    return rows


def endpoints(rows, code, binary_source, backward=False):
    require(rows[:V] == [r + [0] * (N - V) for r in code], "exact source-only integer block")
    for h in range(2 * V, N):
        require(rows[h] == [int(j == h) for j in range(N)], "arbitrary dirty helper restoration")
    for p in range(V):
        require(rows[V + p][V:2 * V] == [int(j == p) for j in range(V)],
                "target identity block")
        require(all(x % 2 == 0 for x in rows[V + p][2 * V:]), "odd target helper leakage")
    want = [1 << j for j in range(N)] + [0]
    for p in range(V):
        want[p] = binary_source[p]
        want[V + p] ^= (1 << p) if backward else binary_source[p]
    require(parity(rows) == want, "complete all-column binary boundary")


def block_summary(rows):
    source = [r[:V] for r in rows[:V]]
    target = [r[:V] for r in rows[V:2 * V]]
    leakage = [r[2 * V:] for r in rows[V:2 * V]]
    result = {}
    for label, matrix in (("A_Z", source), ("T_Z", target), ("E_Z", leakage)):
        coefficients = [x for row in matrix for x in row if x]
        common = 0
        for x in coefficients:
            common = gcd(common, x)
        result[label] = {
            "shape": [len(matrix), len(matrix[0])], "sha256": matrix_digest(matrix),
            "nonzero_entries": len(coefficients), "coefficient_gcd": common,
            "maximum_entry_abs": max(map(abs, coefficients), default=0),
            "maximum_row_l1": max(sum(map(abs, row)) for row in matrix),
        }
    result["source_not_identity_witness"] = first_difference(source, dense_identity(V, private=False))
    result["target_not_A_Z_witness"] = first_difference(target, source)
    result["nonzero_even_helper_witness"] = first_difference(leakage, [[0] * (N - 2 * V) for _ in range(V)])
    return result


def attain_prefix(records, backward, maximum, expected):
    row = maximum["row"]
    chosen = [(x > 0) - (x < 0) for x in row]
    require(max(map(abs, chosen)) == 1, "attaining input must have unit infinity norm")
    values = chosen[:] + [0]
    measured, attained = 1, None
    order = range(len(records) - 1, -1, -1) if backward else range(len(records))
    for index in order:
        op, d, s, c, f, phase = records[index]
        if op == 1:
            values[d] += (-c if backward else c) * values[s]
        elif op == (3 if backward else 2):
            values[N] = values[d]
        elif op == (2 if backward else 3):
            require(values[N] == values[d], "scalar witness ERASE")
            values[N] = 0
        measured = max(measured, abs(values[d]), abs(values[N]))
        if index == maximum["record_index_zero_based"]:
            attained = values[maximum["register"]]
    require(attained == measured == expected and sum(map(abs, row)) == expected,
            "prefix maximum not attained by direct scalar replay")
    return {key: value for key, value in maximum.items() if key != "row"} | {
        "prefix_norm": expected, "attained_value": attained,
        "public_input_signs": chosen,
        "maximizing_row_sparse": [[j, x] for j, x in enumerate(row) if x],
        "maximizing_row_sha256": matrix_digest([row]),
        "direct_scalar_replay_maximum": measured,
        "domain": "scalar lifted word, arbitrary real public inputs with infinity norm <= 1, private=0",
    }


def rejected(label, expected_message, operation):
    try:
        operation()
    except ValueError as error:
        require(str(error) == expected_message,
                "negative control reached an unintended gate: " + label + ": " + str(error))
        return {"name": label, "detected": True, "reason": str(error),
                "expected_semantic_gate_matched": True,
                "authentication_bypassed_only_after_valid_inputs_loaded": True}
    raise ValueError("semantic negative control escaped: " + label)


def negative_controls(records, geo, good, signed_change):
    results = []
    copy_index = next(i for i, r in enumerate(records) if r[0] == 2)
    results.append(rejected("stale_private_snapshot_at_legal_COPY",
                            "ERASE private value is not its original unchanged snapshot",
                            lambda: replay(records, geo, track=False,
                                           fault=("stale_snapshot", copy_index))))
    altered = [r[:] for r in records]
    pivot = altered[copy_index][1]
    altered.insert(copy_index + 1, [1, pivot, (pivot + 1) % V, 1, 1, 99])
    results.append(rejected("mutate_copied_source_before_ERASE",
                            "copied source changed during snapshot lifetime",
                            lambda: replay(altered, geo, track=False)))
    altered = [r[:] for r in records]
    cap = altered[copy_index][4]
    altered.insert(copy_index + 1, [1, N, V + pivot, 1, cap, 99])
    results.append(rejected("mutate_private_copy_before_ERASE",
                            "immutable private field is an ADD destination",
                            lambda: replay(altered, geo, track=False)))
    altered = [r[:] for r in records]
    move_index = next(i for i, r in enumerate(altered) if r[0] == 0)
    altered[move_index][4] += 1
    results.append(rejected("wrong_paid_MOVE_rank", "MOVE containment/rank",
                            lambda: replay(altered, geo, track=False)))
    wrong, _, _ = replay(records, geo, backward=True, initial=good, track=False,
                          fault=("inverse_sign", signed_change))
    identity = dense_identity()
    require(parity(wrong) == parity(identity) and wrong != identity,
            "wrong inverse sign control did not separate Z from F2")
    results.append({"name": "wrong_integer_inverse_sign", "detected": True,
                    "binary_roundtrip_still_identity": True,
                    "integer_roundtrip_failure": first_difference(wrong, identity)})
    altered = [r[:] for r in records]
    altered[signed_change][3] *= -1
    wrong, _, _ = replay(altered, geo, track=False)
    require(parity(wrong) == parity(good) and wrong[:V] != good[:V],
            "wrong quotient coefficient control did not change integer source")
    results.append({"name": "wrong_quotient_coefficient_same_F2", "detected": True,
                    "binary_endpoint_unchanged": True,
                    "integer_endpoint_failure": first_difference(wrong, good)})
    altered = [r[:] for r in records]
    cleanup = max(i for i, r in enumerate(altered) if r[0] == 1 and r[5] == 5 and r[1] >= 2 * V)
    altered[cleanup][3] *= -1
    wrong, _, _ = replay(altered, geo, track=False)
    difference = first_difference(wrong[2 * V:N], good[2 * V:N])
    require(difference is not None and parity(wrong) == parity(good),
            "dirty restoration sign control ineffective")
    difference["output_row"] += 2 * V
    results.append({"name": "dirty_helper_cleanup_wrong_integer_sign", "detected": True,
                    "binary_endpoint_unchanged": True, "integer_helper_failure": difference})
    altered = [r[:] for r in records]
    # A legal FULL-frame source write reads a formerly arbitrary dirty input.
    altered[signed_change][2] = 2 * V
    wrong, _, _ = replay(altered, geo, track=False)
    leakage = next(((i, j, row[j]) for i, row in enumerate(wrong[:V])
                    for j in range(2 * V, N) if row[j]), None)
    require(leakage is not None, "dirty source dependence control ineffective")
    results.append({"name": "source_code_reads_arbitrary_dirty_helper", "detected": True,
                    "witness": {"source_output": leakage[0], "dirty_input": leakage[1],
                                "coefficient": leakage[2]}})
    altered = [r[:] for r in records]
    # Remove an actual zero-frame compensation term, keeping every gate legal.
    compensation = next(i for i, r in enumerate(altered) if r[0] == 1 and r[5] == 10)
    removed = altered.pop(compensation)
    wrong, _, _ = replay(altered, geo, track=False)
    leakage = next(((i, j, row[j]) for i, row in enumerate(wrong[V:2 * V])
                    for j in range(2 * V, N) if row[j] & 1), None)
    require(leakage is not None, "odd dirty target control ineffective")
    results.append({"name": "omitted_dirty_compensation", "detected": True,
                    "removed_record": removed,
                    "witness": {"target_output": V + leakage[0], "dirty_input": leakage[1],
                                "odd_coefficient": leakage[2]}})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-word", type=Path, required=True)
    parser.add_argument("--signed-word", type=Path, required=True)
    parser.add_argument("--raw-word", type=Path, required=True)
    parser.add_argument("--matrices", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="optional deterministic JSON receipt")
    parser.add_argument("--endpoint-out", type=Path, help="optional complete sparse integer endpoint JSON")
    args = parser.parse_args()
    inputs, authentication = {}, {}
    for label in PINS:
        inputs[label], authentication[label] = read_pinned(getattr(args, label), label)
    parent, signed, raw, frozen = (inputs[k] for k in PINS)
    variant = authenticate_variant(parent, signed)
    a, ai, binary = raw_binary_code(raw, frozen)
    geo = Geometry(raw, signed)
    all_rows, runs = {}, {}
    for name, program in (("parent", parent), ("signed", signed)):
        directions, summary = [], {}
        for backward in (False, True):
            rows, invoice, maximum = replay(program["records"], geo, backward)
            require(invoice["record_counts"] == COUNTS and invoice["paid_profile"] == PROFILE,
                    "complete literal invoice")
            code = source_code(program["records"], backward)
            endpoints(rows, code, ai if backward else a, backward)
            invoice["endpoint_blocks"] = block_summary(rows)
            invoice["prefix_attainment"] = attain_prefix(
                program["records"], backward, maximum, invoice["prefix_row_l1"])
            direction = "inverse" if backward else "forward"
            summary[direction], all_rows[name + "_" + direction] = invoice, rows
            directions.append(rows)
        for backward, initial in ((True, directions[0]), (False, directions[1])):
            roundtrip, _, _ = replay(program["records"], geo, backward, initial, track=False)
            require(roundtrip == dense_identity(), "all-column integer two-sided roundtrip")
        summary["both_integer_roundtrips_on_all_651_columns"] = True
        runs[name] = summary
    require([runs["parent"][d]["prefix_row_l1"] for d in ("forward", "inverse")] == [34285, 5839860],
            "parent exact prefixes")
    require([runs["signed"][d]["prefix_row_l1"] for d in ("forward", "inverse")] == [80639, 239014],
            "signed exact prefixes")
    pf, sf, si = (all_rows[k] for k in ("parent_forward", "signed_forward", "signed_inverse"))
    delta_source = [[x - y for x, y in zip(r[:V], s[:V])] for r, s in zip(sf[:V], pf[:V])]
    delta_target = [[x - y for x, y in zip(r[:V], s[:V])] for r, s in zip(sf[V:2 * V], pf[V:2 * V])]
    require(all(x % 2 == 0 for row in delta_source + delta_target for x in row), "odd lift difference")
    require([r[2 * V:] for r in sf[V:2 * V]] == [r[2 * V:] for r in pf[V:2 * V]],
            "forward helper leakage changed")
    require([r[2 * V:] for r in si[V:2 * V]] ==
            [[-x for x in r[2 * V:]] for r in sf[V:2 * V]], "inverse leakage is not negative E_Z")
    changed_targets = [i for i, row in enumerate(delta_target) if any(row)]
    require(changed_targets == [0, 1, 2], "target lift change outside three repaired rows")
    changes = {
        "source_delta_rank_over_Q": integer_rank(delta_source),
        "target_delta_rank_over_Q": integer_rank(delta_target),
        "target_source_block_changed_rows": changed_targets,
        "source_delta_sha256": matrix_digest(delta_source),
        "target_delta_sha256": matrix_digest(delta_target),
        "forward_E_Z_identical_to_parent": True,
        "integer_endpoint_difference_witness": first_difference(sf, pf),
    }
    family = sign_family_transfer(parent["records"], signed["records"], pf, sf)
    controls = negative_controls(signed["records"], geo, sf,
                                 variant["changed_record_indices_zero_based"][0])
    receipt = {
        "schema": "fixed-r429-signed-quotient-independent-integer-audit-v1",
        "status": "PASS_FIXED_SIGNED_QUOTIENT_ALL_COLUMNS_LOCAL_ONLY",
        "no_new_kappa": True,
        "authentication": authentication, "variant": variant,
        "registers": {"sources": V, "arbitrary_targets": V, "arbitrary_dirty_helpers": 429,
                      "public_independent_columns": N, "private_register": N,
                      "private_initial_and_final_value": 0},
        "binary_contract": binary,
        "geometry": geo.receipt,
        "runs": runs, "changed_integer_endpoint": changes,
        "all_sign_family_transfer": family,
        "controls_after_authentication": controls,
        "matrix_digest_encoding": "Dense signed decimal entries separated by comma, LF after "
        "every row; full endpoint includes 652 output rows and 651 public input columns.",
        "integer_contract": {
            "forward": "(x,y,h) -> (A_Z*x, y+T_Z*x+E_Z*h, h)",
            "inverse": "(x,y,h) -> (A_Z^-1*x, y-T_Z*A_Z^-1*x-E_Z*h, h)",
            "binary_forward": "(x,y,h) -> (A*x,y+A*x,h)",
            "binary_inverse": "(x,y,h) -> (A^-1*x,y+x,h)",
            "A_Z_mod_2_and_T_Z_mod_2": "A",
            "E_Z_mod_2": 0,
            "domain": "Every integer, rational, or real public input; every commutative ring "
            "by the same integer-polynomial identities, with a cleared private field. "
            "The binary identity is over F2. Prefix l-infinity equalities concern real scalars.",
        },
        "scope": [
            "Fixed witness and its pinned parent; no sign optimization or optimality claim. "
            "The checked prefix/suffix factorization also proves the stated entire-sign-family law.",
            "All integer and F2 input columns, both orientations, and both roundtrips are exact.",
            "Scalar prefix row norms are exact induced l-infinity norms, with attained inputs.",
            "Native ADDRESS action, native vector cancellations, rounded child defects, precision, "
            "owner allocation, source access, storage, recursive supplier and outer kappa admission "
            "are not proved by this scalar calculation.",
            "No formal-kernel proof; separately authored dense standard-library implementation.",
        ],
    }
    if args.endpoint_out:
        payload = {
            "schema": "sparse-integer-endpoint-rows-v1", "shape": [N + 1, N],
            "indexing": "Rows and columns zero-based; absent entries zero; pairs sorted by column.",
            "matrices": {name: [[[j, x] for j, x in enumerate(row) if x] for row in rows]
                         for name, rows in all_rows.items()},
        }
        args.endpoint_out.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    if args.out:
        args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    else:
        print(json.dumps(receipt, sort_keys=True, indent=2))
    if args.out:
        print(json.dumps({"status": receipt["status"], "signed_prefixes": [80639, 239014],
                          "parent_prefixes": [34285, 5839860],
                          "negative_controls": len(controls), "no_new_kappa": True}, sort_keys=True))


if __name__ == "__main__":
    main()
