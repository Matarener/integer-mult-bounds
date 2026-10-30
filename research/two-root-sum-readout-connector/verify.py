#!/usr/bin/env python3
"""Verify the two-root fused sum-readout connector result.

Interface: five read-only sources x_j, 31 dirty outputs y_m (one per nonzero
five-bit mask m), two borrowed dirty roots z1, z2 and the calls

    B_j -> r:  z_r += B_j x_j               (r in {1, 2}, chosen per call)
    A_m <- r:  y_m += A_m z_r               (plain readout of one root)
    A_m <- s:  y_m += A_m (z1 + z2)         (fused sum readout, the new family)

Checks:
  1. The 945 canonical ten-call source words (Richardson, PR943) reach at most
     31 of 32 masks on one connector (positive control of the cited census).
  2. For every word and every assignment of sources to roots, the fewest fused
     reads for the 31-output batch at 72 map calls. The minimum is 30 and every
     feasible case meets the crossing bound 2(2^a - 1)(2^(5-a) - 1) exactly.
  3. The literal 72-call schedule built from the predecessor's ten-call word
     is correct for arbitrary linear maps (symbolic replay over formal terms)
     and for random dense F2 matrices with dirty inputs at L = 1, 2, 3.
  4. Mutation controls (root split of one source, mixed readout ports, one
     dropped read, one fused pair replaced by plain reads, one moved
     boundary) are all rejected.
"""

import json
import random
import sys
from pathlib import Path

N_SOURCES = 5
FULL = (1 << N_SOURCES) - 1
MASKS = tuple(range(1, FULL + 1))
CERTIFICATE = (Path(__file__).resolve().parent.parent
               / "universal-connector-boundary" / "CERTIFICATE.json")


def canonical_words(n):
    """Restricted-growth labelings of perfect matchings on 2n positions."""
    out = []
    lab = []

    def rec(pos, nxt, open_labels):
        if pos == 2 * n:
            if not open_labels:
                out.append(tuple(lab))
            return
        for j in sorted(open_labels):
            open_labels.remove(j)
            lab.append(j)
            rec(pos + 1, nxt, open_labels)
            lab.pop()
            open_labels.add(j)
        if nxt < n:
            open_labels.add(nxt)
            lab.append(nxt)
            rec(pos + 1, nxt + 1, open_labels)
            lab.pop()
            open_labels.remove(nxt)

    rec(0, 0, set())
    return out


def prefixes(word, support):
    """Source-parity prefixes q_0..q_k projected to the sources in support."""
    q = 0
    out = [0]
    for j in word:
        if support >> j & 1:
            q ^= 1 << j
        out.append(q)
    return out


def differences(points):
    return {a ^ b for a in points for b in points}


def crossing_bound(root1):
    a = bin(root1).count("1")
    return 2 * ((1 << a) - 1) * ((1 << (N_SOURCES - a)) - 1)


def fused_reads_needed(word, root1):
    """Fewest fused reads for all 31 masks, or None if some mask is missing.

    At 72 map calls every output is read exactly twice from one port type;
    a plain pair on root r yields D(projection of the word to root r), a
    fused pair yields D(word).
    """
    root2 = FULL ^ root1
    d_all = differences(prefixes(word, FULL))
    d_plain = differences(prefixes(word, root1)) | differences(prefixes(word, root2))
    need = 0
    for m in MASKS:
        if m in d_plain:
            continue
        if m not in d_all:
            return None
        need += 2
    return need


def census(words):
    single_max = max(len(differences(prefixes(w, FULL))) for w in words)
    hist = {}
    attaining = []
    for w in words:
        for root1 in range(1, FULL):
            need = fused_reads_needed(w, root1)
            if need is None:
                continue
            assert need == crossing_bound(root1), (w, root1, need)
            hist[need] = hist.get(need, 0) + 1
            if need == 30:
                attaining.append((w, root1))
    return single_max, hist, attaining


def build_schedule(word, root1):
    """Literal 72-call schedule; readouts placed at the earliest pair."""
    root2 = FULL ^ root1
    ports = {"1": prefixes(word, root1), "2": prefixes(word, root2),
             "s": prefixes(word, FULL)}
    slots = {}
    for m in MASKS:
        slots[m] = find_pair(ports, m)
        assert slots[m] is not None, m
    sched = []
    for t in range(len(word) + 1):
        for m in MASKS:
            port, s, u = slots[m]
            sched.extend(("A", m, port) for b in (s, u) if b == t)
        if t < len(word):
            j = word[t]
            sched.append(("B", j, "1" if root1 >> j & 1 else "2"))
    return sched


def find_pair(ports, m):
    for port in ("1", "2", "s"):
        pts = ports[port]
        for s in range(len(pts)):
            for u in range(s + 1, len(pts)):
                if pts[s] ^ pts[u] == m:
                    return port, s, u
    return None


def symbolic_ok(sched):
    """Replay over formal XOR sums of terms: valid for arbitrary linear maps."""
    z = {"1": {("z1",)}, "2": {("z2",)}}
    y = {m: set() for m in MASKS}
    for op, idx, port in sched:
        if op == "B":
            z[port] ^= {("B", idx)}
        else:
            src = z["1"] ^ z["2"] if port == "s" else z[port]
            y[idx] ^= {("A", idx, term) for term in src}
    if z["1"] != {("z1",)} or z["2"] != {("z2",)}:
        return False
    for m in MASKS:
        want = {("A", m, ("B", j)) for j in range(N_SOURCES) if m >> j & 1}
        if y[m] != want:
            return False
    return True


def matvec(mat, vec):
    out = 0
    for r, row in enumerate(mat):
        out |= (bin(row & vec).count("1") & 1) << r
    return out


def dense_ok(sched, length, rng):
    full_row = (1 << length) - 1
    bmat = [[rng.getrandbits(length) for _ in range(length)] for _ in range(N_SOURCES)]
    amat = {m: [rng.getrandbits(length) for _ in range(length)] for m in MASKS}
    x = [rng.getrandbits(length) for _ in range(N_SOURCES)]
    y0 = {m: rng.getrandbits(length) for m in MASKS}
    z0 = {"1": rng.getrandbits(length), "2": rng.getrandbits(length)}
    z = dict(z0)
    y = dict(y0)
    for op, idx, port in sched:
        if op == "B":
            z[port] ^= matvec(bmat[idx], x[idx])
        else:
            src = z["1"] ^ z["2"] if port == "s" else z[port]
            y[idx] ^= matvec(amat[idx], src)
    if z != z0:
        return False
    for m in MASKS:
        acc = 0
        for j in range(N_SOURCES):
            if m >> j & 1:
                acc ^= matvec(bmat[j], x[j])
        if y[m] != y0[m] ^ matvec(amat[m], acc) & full_row:
            return False
    return True


def mutations(sched):
    """Each returns a broken copy of the schedule."""
    out = {}
    b_idx = next(i for i, c in enumerate(sched) if c[0] == "B")
    op, j, port = sched[b_idx]
    out["one_source_call_moved_to_other_root"] = (
        sched[:b_idx] + [(op, j, "2" if port == "1" else "1")] + sched[b_idx + 1:])
    f_idx = next(i for i, c in enumerate(sched) if c[0] == "A" and c[2] == "s")
    m = sched[f_idx][1]
    out["mixed_ports_fused_and_plain"] = (
        sched[:f_idx] + [("A", m, "1")] + sched[f_idx + 1:])
    out["one_read_dropped"] = sched[:f_idx] + sched[f_idx + 1:]
    out["fused_pair_replaced_by_plain"] = [
        ("A", m, "1") if c == ("A", m, "s") else c for c in sched]
    a_idx = next(i for i in range(len(sched) - 1)
                 if sched[i][0] == "A" and sched[i + 1][0] == "B")
    out["readout_moved_past_source_call"] = (
        sched[:a_idx] + [sched[a_idx + 1], sched[a_idx]] + sched[a_idx + 2:])
    return out


def main():
    words = canonical_words(N_SOURCES)
    assert len(words) == 945, len(words)
    single_max, hist, attaining = census(words)
    assert single_max == 31, single_max
    assert min(hist) == 30, hist
    infeasible = len(words) * (FULL - 1) - sum(hist.values())
    assert infeasible == 28000, infeasible

    cert = json.loads(CERTIFICATE.read_text())
    base = tuple(cert["schedules"]["five_extra_output"]["source_word"])
    assert base == (0, 1, 2, 0, 3, 1, 4, 2, 3, 4), base
    choices = [r for w, r in attaining if w == base]
    assert choices, "predecessor word does not attain 30"
    root1 = min(choices)

    sched = build_schedule(base, root1)
    n_b = sum(c[0] == "B" for c in sched)
    n_a = sum(c[0] == "A" for c in sched)
    n_fused = sum(c[0] == "A" and c[2] == "s" for c in sched)
    assert (n_b, n_a, n_fused) == (10, 62, 30), (n_b, n_a, n_fused)
    assert symbolic_ok(sched)

    rng = random.Random(20261027)
    dense_cases = 0
    for length in (1, 2, 3):
        for _ in range(200):
            assert dense_ok(sched, length, rng)
            dense_cases += 1

    rejected = 0
    for name, bad in mutations(sched).items():
        assert not symbolic_ok(bad), name
        rejected += 1

    summary = {
        "census_histogram": {str(k): hist[k] for k in sorted(hist)},
        "attaining_word_partitions": len(attaining),
        "attaining_words": len({w for w, _ in attaining}),
        "schedule_word": list(base),
        "root1_sources": [j for j in range(N_SOURCES) if root1 >> j & 1],
        "schedule": [list(c) for c in sched],
    }
    if "--json" in sys.argv:
        print(json.dumps(summary, indent=1))
    print("PASS_TWO_ROOT_SUM_READOUT words=945 single_root_max=31 "
          f"min_fused_reads=30 attaining={len(attaining)} "
          f"attaining_words={summary['attaining_words']} infeasible={infeasible} "
          f"histogram={summary['census_histogram']} map_calls={n_b + n_a} "
          f"fused={n_fused} root1={summary['root1_sources']} "
          f"dense_cases={dense_cases} mutations_rejected={rejected}")


if __name__ == "__main__":
    main()
