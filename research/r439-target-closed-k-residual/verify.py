"""Split the literal K_equals_D defect of R439 D words into target-read and helper-wrap parts.

Scope: nine repository-pinned R439 words from four lineages (helper-free PR915 target
basis, PR926/PR941 disjoint helper pairs, PR1062 pair control, helper triples, helper
stars). Every word has v = 111 targets and R = 439 helpers (661 columns).

Definitions, all over GF(2) with register r starting as column e_r:
- K_t   helper-column part of target t after the frame-free replay of (A, scatter, B).
- N_t   helper columns named by D gates that write target t (the literal mask).
- N*_t  helper columns reaching target t when D is replayed with every
        helper-to-helper gate skipped (target-read-closed named mask).
- E_t   helper columns reaching target t when D is replayed in full.
- T_t = N*_t + N_t   part carried by target-to-target reads.
- H_t = K_t + N*_t   residual left by helper-to-helper gates (helper wraps).
Then the literal defect K_t + N_t equals T_t + H_t.

Finite certificate on the nine named words only. No kappa, no contract adoption,
no supplier admission, no selected-frontier change.

usage: python3 -B verify.py [--json OUT]
"""
import gzip
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

WORDS = (
    ("pr915", "research/r439-helper-matching/vendor/pr915/candidate.json.gz"),
    ("pr926", "research/r439-helper-matching/vendor/pr926/candidate.json.gz"),
    ("matching", "research/r439-helper-matching/candidate.json.gz"),
    ("matching_floor", "research/r439-helper-matching/floor-word.json.gz"),
    ("triples", "research/r439-helper-triples/candidate.json.gz"),
    ("pr1062_pair_control", "research/r439-bsection-stars-seed01/pair_control.json.gz"),
    ("helper_star", "research/r439-helper-stars-seed19/candidate.json.gz"),
    ("pr1062_composition", "research/r439-bsection-stars-seed01/composition.json.gz"),
    ("pr1062_candidate", "research/r439-bsection-stars-seed01/candidate.json.gz"),
)

# Exact expected table: D gates, helper-to-helper gates, literal defect bits |K+N|,
# target-read bits |T|, residual bits |H|, overlap |T and H|, residual sectors, donors.
EXPECTED = {
    "pr915": (723, 0, 17095, 17095, 0, 0, 0, 0),
    "pr926": (1107, 384, 17485, 13148, 7447, 1555, 192, 192),
    "matching": (1121, 398, 17514, 13008, 7786, 1640, 199, 199),
    "matching_floor": (1121, 398, 17505, 12885, 7776, 1578, 199, 199),
    "triples": (1191, 468, 17541, 12444, 8685, 1794, 232, 232),
    "pr1062_pair_control": (1099, 376, 17504, 13110, 7424, 1515, 188, 188),
    "helper_star": (1165, 442, 17636, 12275, 8767, 1703, 221, 221),
    "pr1062_composition": (1165, 442, 17636, 12275, 8767, 1703, 221, 221),
    "pr1062_candidate": (1195, 472, 17653, 12092, 9163, 1801, 236, 236),
}
# Literal defect totals already published by PR4092 / r439-k-cross-term-tally.
PUBLISHED_LITERAL = {"helper_star": 17636, "pr1062_composition": 17636, "pr1062_candidate": 17653}


def fail(msg):
    print("FAIL_R439_TARGET_CLOSED_K_RESIDUAL " + msg)
    sys.exit(1)


def check_pins():
    with open(os.path.join(HERE, "SOURCES.json")) as f:
        rows = {r["path"]: r["sha256"] for r in json.load(f)["files"] if r["usage"] == "input"}
    for _, path in WORDS:
        with open(os.path.join(ROOT, path), "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != rows[path]:
                fail("sha256 mismatch " + path)


def popcount(x):
    return bin(x).count("1")


def column_set(x, offset):
    out = set()
    i = 0
    x >>= offset
    while x:
        if x & 1:
            out.add(i)
        x >>= 1
        i += 1
    return out


def raw_k(w):
    """Helper part K_t of each target after (A, scatter, B), frames ignored."""
    v, R = w["v"], w["R"]
    val = [1 << r for r in range(2 * v + R)]
    for name in ("A", "scatter", "B"):
        if name == "scatter":
            copies = [val[q] for q in w["ret"]]
            for t, row in enumerate(w["scatter"]):
                acc = 0
                for k in row:
                    acc ^= copies[k]
                val[v + t] ^= acc
        else:
            for _, d, srcs in w[name]:
                acc = 0
                for s in srcs:
                    acc ^= val[s]
                val[d] ^= acc
    hmask = ((1 << R) - 1) << (2 * v)
    return [val[v + t] & hmask for t in range(v)]


def replay_d(v, R, D, skip_helper_gates):
    val = [1 << r for r in range(2 * v + R)]
    for _, d, srcs in D:
        if skip_helper_gates and d >= 2 * v:
            continue
        acc = 0
        for s in srcs:
            acc ^= val[s]
        val[d] ^= acc
    return val


def split(v, R, D, K):
    """Return the decomposition record for one D section against helper parts K."""
    hmask = ((1 << R) - 1) << (2 * v)
    N = [0] * v
    for _, d, srcs in D:
        if v <= d < 2 * v:
            for s in srcs:
                N[d - v] ^= 1 << s
    nonhelper_named = sum(1 for t in range(v) if N[t] & ~hmask)
    full = replay_d(v, R, D, False)
    closed = replay_d(v, R, D, True)
    E = [full[v + t] & hmask for t in range(v)]
    Ns = [closed[v + t] & hmask for t in range(v)]
    Nh = [N[t] & hmask for t in range(v)]
    lit = [K[t] ^ Nh[t] for t in range(v)]
    T = [Ns[t] ^ Nh[t] for t in range(v)]
    H = [K[t] ^ Ns[t] for t in range(v)]
    for t in range(v):
        if lit[t] != T[t] ^ H[t]:
            fail("decomposition identity")
    sectors = set()
    for x in H:
        sectors |= column_set(x, 2 * v)
    donors, dests = set(), set()
    hh = 0
    for _, d, srcs in D:
        if d >= 2 * v:
            hh += 1
            dests.add(d - 2 * v)
            donors |= {s - 2 * v for s in srcs if s >= 2 * v}
    tt_reads = sum(1 for _, d, srcs in D if v <= d < 2 * v and any(v <= s < 2 * v for s in srcs))
    return dict(
        d_gates=len(D),
        helper_gates=hh,
        target_reads=tt_reads,
        nonhelper_named_targets=nonhelper_named,
        E_equals_K=all(E[t] == K[t] for t in range(v)),
        helpers_restored=all(full[r] == 1 << r for r in range(2 * v, 2 * v + R)),
        literal_bits=sum(map(popcount, lit)),
        target_read_bits=sum(map(popcount, T)),
        residual_bits=sum(map(popcount, H)),
        overlap_bits=sum(popcount(a & b) for a, b in zip(T, H)),
        residual_targets=sum(1 for x in H if x),
        residual_sectors=len(sectors),
        donors=len(donors),
        destinations=len(dests),
        donor_destination_overlap=len(donors & dests),
        sectors_equal_donors=sectors == donors,
        sector_local_pass=R - len(sectors),
        literal_sector_count=len(set().union(*(column_set(x, 2 * v) for x in lit))),
    )


def word_records():
    out = {}
    for name, path in WORDS:
        with gzip.open(os.path.join(ROOT, path)) as f:
            w = json.load(f)
        if (w["v"], w["R"]) != (111, 439):
            fail("unexpected shape " + name)
        rec = split(w["v"], w["R"], w["D"], raw_k(w))
        got = (rec["d_gates"], rec["helper_gates"], rec["literal_bits"], rec["target_read_bits"],
               rec["residual_bits"], rec["overlap_bits"], rec["residual_sectors"], rec["donors"])
        if got != EXPECTED[name]:
            fail("table mismatch %s %r" % (name, got))
        if not (rec["E_equals_K"] and rec["helpers_restored"] and rec["sectors_equal_donors"]):
            fail("structural predicate " + name)
        if rec["nonhelper_named_targets"]:
            fail("non-helper column named " + name)
        if name in PUBLISHED_LITERAL and rec["literal_bits"] != PUBLISHED_LITERAL[name]:
            fail("published literal total " + name)
        if rec["literal_bits"] != rec["target_read_bits"] + rec["residual_bits"] - 2 * rec["overlap_bits"]:
            fail("bit count identity " + name)
        out[name] = (rec, w)
    return out


def controls(records):
    n = 0
    # 1. Target-read closure alone: y0 ^= h0; y1 ^= y0. K = (h0, h0). Literal mask names
    #    nothing on y1, so the literal defect is one bit; the closed mask has no residual.
    v, R = 2, 2
    h0 = 1 << 4
    rec = split(v, R, [(0, 2, [4]), (0, 3, [2])], [h0, h0])
    if (rec["literal_bits"], rec["target_read_bits"], rec["residual_bits"]) != (1, 1, 0):
        fail("control target-read closure")
    n += 1
    # 2. Restored helper wrap: h0 ^= h1; y ^= h0; h0 ^= h1, with semantic K = h0 + h1.
    #    Residual is exactly the donor column h1, and E = K.
    #    Registers: x0=0, y0=1, h0=2, h1=3; gates are (frame, dest, srcs).
    v, R = 1, 2
    rec = split(v, R, [(0, 2, [3]), (0, 1, [2]), (0, 2, [3])], [(1 << 2) | (1 << 3)])
    if not (rec["E_equals_K"] and rec["residual_bits"] == 1 and rec["sectors_equal_donors"]
            and rec["target_read_bits"] == 0):
        fail("control restored wrap")
    n += 1
    # 3. Same wrap against K = h0 (the tally package's synthetic edge). Executed delivery
    #    h0 + h1 differs from K, yet the closed mask reports zero residual. So K = N* alone
    #    is not a sound check once helper gates are present; E = K must still be checked.
    rec = split(v, R, [(0, 2, [3]), (0, 1, [2]), (0, 2, [3])], [1 << 2])
    if rec["E_equals_K"] or rec["residual_bits"] != 0:
        fail("control mismatched K")
    n += 1
    # 4. Mutation on a real word: delete the first helper-to-helper gate of the star word.
    #    The helper is no longer restored and E no longer equals K.
    _, w = records["helper_star"]
    first = next(i for i, g in enumerate(w["D"]) if g[1] >= 2 * w["v"])
    D = w["D"][:first] + w["D"][first + 1:]
    rec = split(w["v"], w["R"], D, raw_k(w))
    if rec["E_equals_K"] or rec["helpers_restored"]:
        fail("control deleted helper gate")
    n += 1
    # 5. Mutation: delete the first PR915 target-to-target read that carries helper
    #    columns. The closed mask then leaves a nonzero residual, so the zero residual
    #    is not a property of K alone.
    _, w = records["pr915"]
    v = w["v"]
    hmask = ((1 << w["R"]) - 1) << (2 * v)
    val = [1 << r for r in range(2 * v + w["R"])]
    first = None
    for i, (_, d, srcs) in enumerate(w["D"]):
        carried = 0
        for s in srcs:
            if v <= s < 2 * v:
                carried ^= val[s] & hmask
        if first is None and v <= d < 2 * v and carried:
            first = i
        acc = 0
        for s in srcs:
            acc ^= val[s]
        val[d] ^= acc
    D = w["D"][:first] + w["D"][first + 1:]
    rec = split(w["v"], w["R"], D, raw_k(w))
    if rec["residual_bits"] == 0:
        fail("control deleted target read")
    n += 1
    # 6. PR3904's pair on the PR967 star word: target register 112, helper register 260
    #    (helper index 38), donor of D gate 0 `280 ^= 260`. The bit is in K, absent from
    #    N and N*, so it lies in both the literal defect and the residual H.
    _, w = records["helper_star"]
    v = w["v"]
    t, col = 112 - v, 260
    hmask = ((1 << w["R"]) - 1) << (2 * v)
    K = raw_k(w)
    closed = replay_d(v, w["R"], w["D"], True)
    named = 0
    for _, d, srcs in w["D"]:
        if d == 112:
            for s in srcs:
                named ^= 1 << s
    bit = lambda x: (x >> col) & 1
    if w["D"][0] != [0, 280, [260]] or (bit(K[t]), bit(named), bit(closed[112] & hmask)) != (1, 0, 0):
        fail("control PR3904 pair")
    n += 1
    return n


def main():
    out_path = None
    if len(sys.argv) == 3 and sys.argv[1] == "--json":
        out_path = sys.argv[2]
    elif len(sys.argv) != 1:
        fail("usage: verify.py [--json OUT]")
    check_pins()
    records = word_records()
    n_controls = controls(records)
    table = {name: rec for name, (rec, _) in records.items()}
    if out_path:
        with open(out_path, "w") as f:
            json.dump(table, f, indent=1, sort_keys=True)
    print("PASS_R439_TARGET_CLOSED_K_RESIDUAL words=%d pr915_residual=0 "
          "star_residual=%d/%d/%d sectors_equal_donors=%d/%d controls=%d no_new_kappa" % (
              len(records), table["helper_star"]["residual_bits"],
              table["pr1062_composition"]["residual_bits"], table["pr1062_candidate"]["residual_bits"],
              sum(1 for r in table.values() if r["sectors_equal_donors"]), len(table), n_controls))


if __name__ == "__main__":
    main()
