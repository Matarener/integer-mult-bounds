#!/usr/bin/env python3
"""Exact finite BIT operator factorization and heterogeneous recursive invoice.

The PR589 word is regenerated from its frozen source, byte-for-byte.  This
new file changes its global controller and its declared physical endpoints.
It does not admit a mixed-target all-size BIT compiler or a new kappa.

Apache-2.0. Substantial OpenAI assistance. Retained local-word attribution:
DreamingOfClouds / PR589, eumemic / PR555 and PR543, and their cited lineage.
The compressed controller is from PR386/436/443/463/510 and the general
global_k.py implementation.  Mixed target accounting is motivated by the
PR4268 proposal, whose transfer hypotheses are not asserted here.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache, reduce
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import math
import platform
import struct
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REFERENCE = ROOT / "research/kappa-next-regime/bit-compression/carrier-reuse/reference"
sys.path.insert(0, str(REFERENCE))
from joint_pair_dag import log_interval, exp_interval, quotient

LOCAL = Counter({1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19})
V, R, H = 111, 439, 8
WORD_HASH = "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"
WORD_CONTENT_HASH = "5642fd0e35a1acc11acff8d0c08350c1617e95f310d4d35ad63a651f9eeeba0b"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def digest(data):
    return sha256(canonical(data)).hexdigest()


def bit_rank(rows, n):
    basis = {}
    for row in rows:
        for pivot in sorted(basis, reverse=True):
            if row >> pivot & 1:
                row ^= basis[pivot]
        if row:
            need(row.bit_length() <= n, "Binary matrix width")
            basis[row.bit_length()-1] = row
    return len(basis)


def bit_mul(a, b):
    return [reduce(int.__xor__, (b[j] for j in range(len(b)) if row >> j & 1), 0)
            for row in a]


def bit_inverse(a):
    n = len(a)
    aug = [row | (1 << (n+i)) for i, row in enumerate(a)]
    for j in range(n):
        k = next((i for i in range(j, n) if aug[i] >> j & 1), None)
        need(k is not None, "Invertible scalar boundary")
        aug[j], aug[k] = aug[k], aug[j]
        for i in range(n):
            if i != j and aug[i] >> j & 1:
                aug[i] ^= aug[j]
    result = [row >> n for row in aug]
    need(bit_mul(a, result) == [1 << i for i in range(n)], "Inverse replay")
    return result


def bit_factor(a):
    """Literal ADD/SWAP program for a constant F2 matrix, checked exactly."""
    n = len(a)
    cur = list(a)
    elimination = []
    for j in range(n):
        k = next(i for i in range(j, n) if cur[i] >> j & 1)
        if k != j:
            cur[j], cur[k] = cur[k], cur[j]
            elimination.append(["SWAP", j, k])
        for i in range(n):
            if i != j and cur[i] >> j & 1:
                cur[i] ^= cur[j]
                elimination.append(["ADD", i, j])
    need(cur == [1 << i for i in range(n)], "Scalar elimination endpoint")
    program = list(reversed(elimination))
    cur = [1 << i for i in range(n)]
    for op, d, s in program:
        if op == "SWAP":
            cur[d], cur[s] = cur[s], cur[d]
        else:
            cur[d] ^= cur[s]
    need(cur == a, "Scalar boundary synthesis")
    # A SWAP may be emitted as three ADDs; the invoice charges that option.
    return program, sum(3 if op == "SWAP" else 1 for op, _, _ in program)


def shift(row, monomial):
    return [{term ^ monomial for term in entry} for entry in row]


def add(a, b):
    return [x ^ y for x, y in zip(a, b)]


def polynomial_coefficients(matrix):
    n = len(matrix)
    coefficients = {}
    for i, row in enumerate(matrix):
        for j, entry in enumerate(row):
            for term in entry:
                coefficients.setdefault(term, [0]*n)[i] ^= 1 << j
    return {term: rows for term, rows in coefficients.items() if any(rows)}


def physical_controller(p, keep, omit_bridge=None):
    """Literal physical operator over F2[(Z/2)^(2p+2)].

    Bit zero is D_P (rank one); bit s+1 is D_Bs (rank seven).
    A complete local invocation on a data pair is D_Bs S(D_P),
    where S is one scalar shear. No scalar bridge is assumed to join
    equal decoded frames: its physical action is multiplied literally.
    """
    n = 2*p
    matrix = [[{0} if i == j else set() for j in range(n)] for i in range(n)]
    events, idle, bridge_number = [], [], 0

    def idle_call(pair, stages, kind):
        monomial = sum(1 << (s+1) for s in stages)
        index = len(idle)
        retained = bool(keep >> index & 1)
        idle.append(dict(index=index, pair=pair, stages=stages, kind=kind,
                         rank=7*len(stages), retained=retained))
        if retained:
            for role in (2*pair, 2*pair+1):
                matrix[role] = shift(matrix[role], monomial)
            events.append(["IDLE", pair, monomial])

    def local(stage, pair, reverse):
        x, y = 2*pair, 2*pair+1
        if reverse:
            x, y = y, x
        matrix[y] = add(matrix[y], shift(matrix[x], 1))
        matrix[x] = shift(matrix[x], 1 << (stage+1))
        matrix[y] = shift(matrix[y], 1 << (stage+1))
        events.append(["LOCAL", stage, pair, reverse])
        if stage % 2 and stage <= 2*p-3:
            idle_call((stage+1)//2, list(range(stage+1)), "initial")
        elif stage % 2 == 0 and 2 <= stage <= 2*p-2:
            idle_call(stage//2, [stage], "middle")
        elif stage == 2*p:
            for j in range(p-1):
                idle_call(j, list(range(2*j+3, 2*p+1)), "terminal")

    def bridge(dst, src):
        nonlocal bridge_number
        for d, s in ((2*dst, 2*src), (2*src+1, 2*dst+1)):
            if bridge_number != omit_bridge:
                matrix[d] = add(matrix[d], matrix[s])
                events.append(["ADD", d, s])
            bridge_number += 1

    local(0, 0, False)
    for j in range(p):
        local(2*j+1, j, True)
        if j < p-1:
            bridge(j, j+1)
        local(2*j+2, j, False)
        if j < p-1:
            bridge(j, j+1)
    for j in reversed(range(p-1)):
        bridge(j+1, j)
    for j in range(p):
        matrix[2*j], matrix[2*j+1] = matrix[2*j+1], matrix[2*j]
        events.append(["SWAP", 2*j, 2*j+1])
    need(len(idle) == 3*(p-1), "Idle enumeration")
    need(bridge_number == 6*(p-1), "Bridge count")
    return polynomial_coefficients(matrix), events, idle


def simultaneous_monomial_factor(coefficients):
    """Return explicit L A R = diagonal monomials, or reject.

    The coefficient matrices of A(1)^-1 A must be pairwise orthogonal
    idempotents.  This is a sufficient and necessary constant-basis test
    for this exact formal diagonal-monomial endpoint.
    """
    n = len(next(iter(coefficients.values())))
    total = [0]*n
    for matrix in coefficients.values():
        total = [a ^ b for a, b in zip(total, matrix)]
    if bit_rank(total, n) != n:
        return None
    inverse = bit_inverse(total)
    projectors = {term: bit_mul(inverse, matrix) for term, matrix in coefficients.items()}
    for term, matrix in projectors.items():
        if bit_mul(matrix, matrix) != matrix:
            return None
        for other, second in projectors.items():
            if term != other and any(bit_mul(matrix, second)):
                return None
    columns, diagonal = [], []
    for term, matrix in sorted(projectors.items()):
        for j in range(n):
            column = sum(((row >> j) & 1) << i for i, row in enumerate(matrix))
            if bit_rank(columns+[column], n) > len(columns):
                columns.append(column)
                diagonal.append(term)
    need(len(columns) == n, "Projector images span")
    right = [sum(((column >> i) & 1) << j for j, column in enumerate(columns))
             for i in range(n)]
    left = bit_mul(bit_inverse(right), inverse)
    exact = {term: bit_mul(bit_mul(left, matrix), right)
             for term, matrix in coefficients.items()}
    expected = {term: [((1 << i) if diagonal[i] == term else 0) for i in range(n)]
                for term in set(diagonal)}
    need(exact == expected, "Full formal operator diagonalization")
    left_program, left_adds = bit_factor(left)
    right_program, right_adds = bit_factor(right)
    return dict(left_rows=left, right_rows=right, diagonal_monomials=diagonal,
                coefficient_projectors={str(t): m for t, m in sorted(projectors.items())},
                left_program=left_program, right_program=right_program,
                boundary_unit_ADDs_per_port=left_adds+right_adds,
                full_coefficient_endpoint_sha256=digest({str(t): x for t, x in sorted(exact.items())}))


def rational_inverse(matrix):
    n = len(matrix)
    work = [[Q(x) for x in row]+[Q(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next(i for i in range(j, n) if work[i][j])
        work[j], work[pivot] = work[pivot], work[j]
        scale = work[j][j]
        work[j] = [x/scale for x in work[j]]
        for i in range(n):
            if i != j and work[i][j]:
                scale = work[i][j]
                work[i] = [a-scale*b for a, b in zip(work[i], work[j])]
    return [row[n:] for row in work]


def matrix_multiply(a, b):
    return [[sum((x*y for x, y in zip(row, column)), Q(0))
             for column in zip(*b)] for row in a]


def frame_projectors(frame_data):
    result = {}
    for name, frame in frame_data.items():
        basis = [[Q(x) for x in row] for row in frame["B"]]
        if not basis:
            projector = [[Q(0)]*8 for _ in range(8)]
        else:
            transpose = list(map(list, zip(*basis)))
            gram = matrix_multiply(basis, transpose)
            projector = matrix_multiply(matrix_multiply(transpose, rational_inverse(gram)), basis)
        need(matrix_multiply(projector, projector) == projector, "Exact frame projector")
        need(sum(projector[i][i] for i in range(8)) == frame["dim"], "Projector trace")
        result[int(name)] = projector
    return result


def audit_local(word_path):
    need(sha256(word_path.read_bytes()).hexdigest() == WORD_HASH, "PR589 gzip source pin")
    raw = gzip.decompress(word_path.read_bytes())
    need(sha256(raw).hexdigest() == WORD_CONTENT_HASH, "PR589 canonical word pin")
    word = json.loads(raw)
    folder = word_path.parent / "records"
    frame_data = json.loads((folder/"frames.json").read_text())["frames"]
    records = list(struct.iter_unpack("<6i", (folder/"249-records.bin").read_bytes()))
    need((word["h"], word["v"], word["R"]) == (8, V, R), "Pinned local type")
    n = 2*V+R
    projectors = frame_projectors(frame_data)
    dimensions = {int(f): z["dim"] for f, z in frame_data.items()}
    pairs = set()
    for op, role, old, new, rank, _ in records:
        if op == 0:
            pairs.add((old, new, rank))
    for old, new, rank in pairs:
        p, q = projectors[old], projectors[new]
        need(matrix_multiply(p, q) == p and matrix_multiply(q, p) == p,
             "Nested exact projectors")
        need(dimensions[new]-dimensions[old] == rank >= 0, "Literal child rank")
    for role in range(2*V, n):
        need(dimensions[word["start"][role]] == 0 and dimensions[word["final"][role]] == 8,
             "Every helper is physically D_I8, not a reset or an unearned job")
    checks = []
    streams = {}
    for reverse in (False, True):
        current = list(word["final"] if reverse else word["start"])+[-1]
        values = [1 << i for i in range(n)]+[0]
        norm = [1]*n+[0]
        maximum = 1
        profile = Counter()
        stream = []
        owned = None
        adds = copies = 0
        for op, x, y, c, f, z in (reversed(records) if reverse else records):
            if op == 0:
                old, new = (c, y) if reverse else (y, c)
                need(current[x] == old, "Local transition entrance")
                current[x] = new
                if f:
                    profile[f] += 1
                stream.append(["MOVE", x, old, new, f])
            elif op == 1:
                need(current[x] == current[y] == f and x != y, "Native common-frame ADD")
                need(owned is None or x != owned, "Owned source remains immutable")
                values[x] ^= values[y] if c & 1 else 0
                norm[x] += abs(c)*norm[y]
                maximum = max(maximum, norm[x])
                adds += 1
                stream.append(["ADD", x, y])
            elif op == (3 if reverse else 2):
                need(owned is None and y == n and values[n] == 0 and current[x] == c,
                     "Private COPY entrance")
                owned = x
                current[n] = f
                values[n] = values[x]
                norm[n] = norm[x]
                rank = abs(dimensions[c]-dimensions[f])
                profile[rank] += 1
                copies += 1
                stream.append(["COPY", x, n])
            else:
                need(op == (2 if reverse else 3) and owned == x and y == n,
                     "Private COPY close")
                need(values[n] == values[x], "Copied field exact cleanup")
                values[n], norm[n], current[n], owned = 0, 0, -1, None
                stream.append(["ERASE", x, n])
        need(owned is None and copies == 9 and adds == 24305, "Complete local word")
        need(current[:n] == (word["start"] if reverse else word["final"]), "All local endpoints")
        expected = [(1 << i) ^ ((1 << (i-V)) if V <= i < 2*V else 0) for i in range(n)]
        need(values == expected+[0], "All arbitrary input columns")
        need(profile == LOCAL, "Complete local bill, including copied centers")
        key = "reverse" if reverse else "forward"
        streams[key] = stream
        checks.append(dict(direction=key, arbitrary_columns=n, dirty_helper_columns=R,
                           owned_COPY_episodes=copies, unit_ADDs=adds,
                           positive_majorant_maximum=maximum, positive_majorant_bits=maximum.bit_length(),
                           profile=dict(sorted(profile.items())), stream_sha256=digest(stream)))
    serial_projectors = {str(f): [[str(x) for x in row] for row in p]
                         for f, p in sorted(projectors.items())}
    return word, streams, dict(status="PASS_FULL_LOCAL_COLUMNS_AND_EXACT_PROJECTORS",
                               frames=len(projectors), nested_transition_pairs=len(pairs),
                               projector_sha256=digest(serial_projectors), signed_directions=checks,
                               helper_endpoint="D_I8 on all 439 arbitrary original helper inputs",
                               private_COPY_contract="Inherited source-owned immutable-copy contract; all nine episodes paid",
                               full_GL_cover_executed=False)


def explicit_unbanked_scalar_replay(p, streams):
    """Fresh physical fields for every local invocation; all dirt columns."""
    calls = 2*p+1
    n = 2*p*V+calls*R
    values = [1 << i for i in range(n)]+[0]
    norms = [1]*n+[0]
    maximum = 1
    adds = 0
    def local(stage, pair, reverse):
        nonlocal maximum, adds
        def role(r):
            if r == 2*V+R:
                return n
            if r < 2*V:
                side, port = divmod(r, V)
                side = 1-side if reverse else side
                return (2*pair+side)*V+port
            return 2*p*V+stage*R+r-2*V
        for event in streams["reverse" if reverse else "forward"]:
            if event[0] == "MOVE":
                continue
            op, x, y = event
            x, y = role(x), role(y)
            if op == "ADD":
                values[x] ^= values[y]
                norms[x] += norms[y]
                maximum = max(maximum, norms[x])
                adds += 1
            elif op == "COPY":
                need(values[y] == 0, "Global private slot empty")
                values[y], norms[y] = values[x], norms[x]
            else:
                need(values[y] == values[x], "Global private slot restored")
                values[y], norms[y] = 0, 0
    def bridge(dst, src):
        nonlocal maximum, adds
        for port in range(V):
            for d, s in ((2*dst*V+port, 2*src*V+port),
                         ((2*src+1)*V+port, (2*dst+1)*V+port)):
                values[d] ^= values[s]
                norms[d] += norms[s]
                maximum = max(maximum, norms[d])
                adds += 1
    local(0, 0, False)
    for j in range(p):
        local(2*j+1, j, True)
        if j < p-1:
            bridge(j, j+1)
        local(2*j+2, j, False)
        if j < p-1:
            bridge(j, j+1)
    for j in reversed(range(p-1)):
        bridge(j+1, j)
    for pair in range(p):
        for port in range(V):
            x, y = 2*pair*V+port, (2*pair+1)*V+port
            values[x], values[y] = values[y], values[x]
            norms[x], norms[y] = norms[y], norms[x]
    need(values == [1 << i for i in range(n)]+[0], "Every global decoded column restored")
    need(adds == calls*24305+6*(p-1)*V, "Literal global scalar bill")
    return dict(all_arbitrary_columns=n, independent_dirty_helpers=calls*R,
                COPY_episodes=9*calls, private_COPY_closed=True,
                unit_ADDs_before_new_boundary_adapters=adds,
                final_free_pair_swaps=p*V,
                positive_majorant_maximum=maximum, positive_majorant_bits=maximum.bit_length(),
                notes="Decoded scalar audit; physical monomial endpoint is checked separately on every coefficient.")


@lru_cache(None)
def h_interval(rank, exponent):
    lo, hi = log_interval(rank)
    elo, ehi = exp_interval(exponent*lo, exponent*hi)
    return Q(rank)/ehi, Q(rank)/elo


def margin_interval(paid, targets, exponent):
    signed = Counter(targets)
    signed.subtract(paid)
    lo = hi = Q(0)
    for rank, count in signed.items():
        a, b = h_interval(rank, exponent)
        lo += count*(a if count >= 0 else b)
        hi += count*(b if count >= 0 else a)
    return lo, hi


def interval_row(bounds):
    lo, hi = bounds
    scale = 1 << 128
    lo = Q(lo.numerator*scale//lo.denominator, scale)
    hi = Q(-((-hi.numerator*scale)//hi.denominator), scale)
    return dict(lower=quotient(lo), upper=quotient(hi),
                display=float((lo+hi)/2), strict_positive=lo > 0, strict_negative=hi < 0)


def price_candidate(p, keep, factor, idle):
    calls, m = 2*p+1, 14*p+8
    paid = Counter({rank:calls*n for rank, n in LOCAL.items()})
    # All idle blocks are explicitly split into perpendicular rank-seven
    # subcalls. No rank14/28/42 child is hidden under a rank8 target.
    paid[7] += 2*V*sum(len(row["stages"]) for row in idle if row["retained"])
    targets = Counter({8:calls*R})
    for monomial in factor["diagonal_monomials"]:
        targets[(monomial & 1)+7*(monomial >> 1).bit_count()] += V
    need(max(paid) < min(targets), "Every child strictly smaller than every job")
    credit = sum(rank*n for rank, n in targets.items())
    bill = sum(rank*n for rank, n in paid.items())
    need(credit-bill == 2*p*V-calls*63, "Full rank credit identity")
    def floating(exponent):
        return sum(n*r**(1-exponent) for r, n in targets.items())-sum(n*r**(1-exponent) for r, n in paid.items())
    lo, hi = 0.0, 0.01
    for _ in range(64):
        middle = (lo+hi)/2
        if floating(middle) > 0:
            lo = middle
        else:
            hi = middle
    lower = Q(math.floor(lo*10**12), 10**12)
    upper = lower+Q(1, 10**12)
    lower_bounds = margin_interval(paid, targets, lower)
    upper_bounds = margin_interval(paid, targets, upper)
    need(lower_bounds[0] > 0 > upper_bounds[1], "Exact root bracket")
    prices = {str(a):interval_row(margin_interval(paid, targets, a))
              for a in (Q("0.001745"), Q("0.002"), Q("0.004"), Q("0.006"))}
    # The old raw-price bad-residue envelope is displayed conservatively.
    # It is not a proof that the new mixed output normalizers inherit it.
    old_residue_envelope = Q(32*m*m*sum(paid.values()), 10**16)
    return dict(pairs=p, stages=calls, keep_idle_mask=keep, ambient_rank=m,
                paid=dict(sorted(paid.items())), targets=dict(sorted(targets.items())),
                total_paid_queries=sum(paid.values()), total_productive_fields=sum(targets.values()),
                rank_bill=bill, rank_credit=credit, rank_margin=credit-bill,
                strict_separation=dict(maximum_child=max(paid), minimum_target=min(targets)),
                bare_mixed_moment_root_bracket=dict(lower=quotient(lower), upper=quotient(upper),
                    lower_display=float(lower), upper_display=float(upper),
                    lower_margin=interval_row(lower_bounds), upper_margin=interval_row(upper_bounds)),
                target_margins=prices, old_raw_bad_residue_envelope=quotient(old_residue_envelope),
                envelope_transfer_proved=False, kappa_claim=False)


def run(max_p=5):
    start = time.monotonic()
    source = HERE / "sources/pr589-regenerated/WORD.json.gz"
    word, streams, local = audit_local(source)
    cases, counts, winners = [], {}, {}
    for p in range(1, max_p+1):
        valid = []
        for keep in range(1 << (3*(p-1))):
            coefficients, events, idle = physical_controller(p, keep)
            factor = simultaneous_monomial_factor(coefficients)
            if factor is None:
                continue
            # Discovery ranks by a floating root; winners receive exact
            # rational price brackets below. All accepted factorizations
            # have already passed exact finite operator identities.
            paid = Counter({r:(2*p+1)*n for r, n in LOCAL.items()})
            paid[7] += 2*V*sum(len(row["stages"]) for row in idle if row["retained"])
            targets = Counter({8:(2*p+1)*R})
            for term in factor["diagonal_monomials"]:
                targets[(term & 1)+7*(term >> 1).bit_count()] += V
            def value(a):
                return sum(n*r**(1-a) for r, n in targets.items())-sum(n*r**(1-a) for r, n in paid.items())
            lo, hi = 0.0, 0.01
            for _ in range(48):
                mid = (lo+hi)/2
                if value(mid) > 0:
                    lo = mid
                else:
                    hi = mid
            valid.append((lo, keep, factor, coefficients, events, idle))
        counts[p] = dict(enumerated=1 << (3*(p-1)), exact_factorizations=len(valid))
        winning = max(valid, key=lambda row:(row[0], row[1]))
        _, keep, factor, coefficients, events, idle = winning
        case = price_candidate(p, keep, factor, idle)
        case.update(factorization=factor, idle_events=idle, physical_events=events,
                    coefficient_matrices={str(term):rows for term, rows in sorted(coefficients.items())},
                    decoded_global_replay=explicit_unbanked_scalar_replay(p, streams))
        case["unit_ADDs_including_constant_boundaries"] = (
            case["decoded_global_replay"]["unit_ADDs_before_new_boundary_adapters"]+
            V*factor["boundary_unit_ADDs_per_port"])
        case["unit_ADDs_if_all_final_SWAPs_use_three_ADDs"] = (
            case["unit_ADDs_including_constant_boundaries"]+3*p*V)
        # Conservative norm multiplier for literal boundary ADDs. This
        # input is offered to a precision compiler, not admitted as one.
        base = case["decoded_global_replay"]["positive_majorant_maximum"]
        norm_bound = base*(1 << (factor["boundary_unit_ADDs_per_port"]+3*p))
        case["positive_majorant_with_boundary_bound"] = str(norm_bound)
        case["positive_majorant_with_boundary_bits"] = norm_bound.bit_length()
        cases.append(case)
        winners[p] = case["bare_mixed_moment_root_bracket"]["lower_display"]
    strongest = max(cases, key=lambda row:row["bare_mixed_moment_root_bracket"]["lower_display"])
    p, keep = strongest["pairs"], strongest["keep_idle_mask"]
    factor = strongest["factorization"]
    # A literal omitted bridge is compared with the ACTUAL advertised
    # target using the same boundary matrices. Mere diagonalizability is
    # deliberately not enough for this negative control.
    rejected = []
    expected = {int(t):bit_mul(bit_mul(factor["left_rows"], rows), factor["right_rows"])
                for t, rows in strongest["coefficient_matrices"].items()}
    for missing in range(6*(p-1)):
        coefficients, _, _ = physical_controller(p, keep, missing)
        wrong = {t:bit_mul(bit_mul(factor["left_rows"], rows), factor["right_rows"])
                 for t, rows in coefficients.items()}
        need(wrong != expected, "Omitted physical bridge rejected")
        rejected.append(missing)
    controls = dict(omitted_bridges_rejected=rejected,
                    rank14_child_under_rank8_job_rejected=not(14 < 8),
                    full_rank8_helper_downgrade_to_rank7_rejected=(8 != 7),
                    all_idle_removed_p2_is_not_constant_monomial_diagonal=(
                        simultaneous_monomial_factor(physical_controller(2, 0)[0]) is None))
    pins = [Path(__file__), source, source.parent/"BASE.json.gz",
            source.parent/"XCHECK.json", source.parent/"records/249-records.bin",
            source.parent/"records/249-states.json", source.parent/"records/frames.json",
            ROOT/"research/e8-bit-p111-tuned/code/gen_p3.py",
            ROOT/"research/e8-bit-p111-tuned/code/xcheck_p.py",
            ROOT/"research/e8-bit-p111-tuned/tune/apply.py",
            ROOT/"research/e8-bit-p111-tuned/tune/wlib.py",
            ROOT/"research/e8-bit-p111-tuned/tune/EXPECTED.json",
            ROOT/"research/e8-bit-carrier-skeleton/code/bit/export_records.py",
            REFERENCE/"joint_pair_dag.py"]
    return dict(schema="finite-bit-mixed-productive-controller/1",
                status="PASS_EXACT_FINITE_OPERATOR_AND_DISPLAYED_MIXED_INVOICE",
                source_recovery="PR589 source regenerated byte-for-byte; not the missing stronger PR4085 BIT word",
                local=local, finite_idle_menu=counts, candidates=cases,
                strongest_pairs=strongest["pairs"], controls=controls,
                exact_algebra="F2[(Z/2)^(2p+2)], represented by every monomial coefficient; no numerical character sampling",
                physical_generator_ranks="D_P rank1, mutually perpendicular D_Bs rank7; helper endpoint D_(P+Bs) rank8",
                not_proved=["Cover routing for these changed independent target projectors",
                            "Canonical weighted BIT output normalizers and their incoming-weight compatibility",
                            "Mixed-target all-size recursion or its fixed uniform precompilation",
                            "Physical tape, row stock, rounding/precision and complete outer multiplication transfer"],
                source_sha256={str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest() for path in pins},
                runtime=dict(python=platform.python_version(), seconds=time.monotonic()-start),
                new_multiplication_kappa=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-p", type=int, default=5)
    parser.add_argument("--output", type=Path, default=HERE/"MIXED-PRODUCTIVE-BIT.json")
    args = parser.parse_args()
    need(1 <= args.max_p <= 6, "Bounded finite controller menu")
    result = run(args.max_p)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps(dict(status=result["status"], strongest_pairs=result["strongest_pairs"],
                         roots={c["pairs"]:c["bare_mixed_moment_root_bracket"]["lower_display"]
                                for c in result["candidates"]}, runtime=result["runtime"]), sort_keys=True))


if __name__ == "__main__":
    main()
