#!/usr/bin/env python3
"""Exact one-insertion Pareto layer for demand (1,2,4) over F2^3.

Self-contained standard-library verifier. It enumerates every ADD-only word
with at most four nonzero gates over R = F2^3, decides every eight-ADD
one-insertion count vector, replays the six new attaining words with a
separate scalar interpreter over F2^3 and over the universal ring F2^4, and
checks the 31-vector aggregate frontier for pairwise non-domination.
Writes no files. Produced by Nick Petalas. Apache-2.0.
"""

import hashlib
import itertools
import json
import pathlib
import sys

ROWS = 3
LAMBDA = (1, 2, 4)  # bitmask encoding x0 + 2 x1 + 4 x2 of PR #5514
ONE = 7
G = 7  # g = lambda_0 + lambda_1 + lambda_2
MAX_GATES = 4
GATES = tuple((i, j, a) for i in range(ROWS) for j in range(ROWS) if i != j
              for a in range(1, 8))
IDENTITY = (ONE, 0, 0, 0, ONE, 0, 0, 0, ONE)
PACKAGE = pathlib.Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json",
                 "verify.py")


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def apply_gate(matrix, gate):
    """Left-multiply a row-major 3x3 matrix over F2^3 by E_ij(a)."""
    i, j, a = gate
    out = list(matrix)
    for c in range(ROWS):
        out[ROWS * i + c] ^= a & matrix[ROWS * j + c]
    return tuple(out)


def unit(r):
    return tuple(1 if t == r else 0 for t in range(ROWS))


def add(u, v):
    return tuple(x + y for x, y in zip(u, v))


def enumerate_levels():
    """levels[k]: matrix -> {count vector: witness word} for exactly k gates."""
    levels = [{IDENTITY: {(0, 0, 0): ()}}]
    for _ in range(MAX_GATES):
        nxt = {}
        for matrix, witnesses in levels[-1].items():
            for gate in GATES:
                image = apply_gate(matrix, gate)
                slot = nxt.setdefault(image, {})
                for counts, word in witnesses.items():
                    grown = add(counts, unit(gate[0]))
                    if grown not in slot:
                        slot[grown] = word + (gate,)
        levels.append(nxt)
    require(len(GATES) == 42, "gate alphabet size")
    return levels


def column(matrix, r):
    return tuple(matrix[ROWS * t + r] for t in range(ROWS))


def expected_totals(root):
    base = (2, 2, 2)
    out = {add(add(base, unit(h)), unit(h)) for h in range(ROWS)}
    out |= {add(add(base, unit(root)), unit(h)) for h in range(ROWS) if h != root}
    return out


def one_insertion_layer(levels):
    for k in range(MAX_GATES):
        for matrix in levels[k]:
            for root in range(ROWS):
                require(column(matrix, root) != LAMBDA,
                        f"a {k}-gate ADD word already splits g e_{root}")
    report, words = {}, {}
    for root in range(ROWS):
        good = {m: w for m, w in levels[MAX_GATES].items()
                if column(m, root) == LAMBDA}
        totals = {add(s, p) for w in good.values() for s in w for p in w}
        require(totals == expected_totals(root), f"eight-ADD totals, root {root}")
        excluded = {add(add((2, 2, 2), unit(j)), unit(k))
                    for j in range(ROWS) for k in range(j + 1, ROWS)
                    if root not in (j, k)}
        require(excluded and not excluded & totals, "non-root (3,3,2) exclusion")
        classes = {}
        for w in good.values():
            key = ",".join("".join(map(str, c)) for c in sorted(w))
            classes[key] = classes.get(key, 0) + 1
        report[root] = {"suffix_matrices": len(good),
                        "count_set_classes": dict(sorted(classes.items())),
                        "totals": sorted(totals), "excluded": sorted(excluded)}
        for h in range(ROWS):
            if h == root:
                continue
            for w in good.values():
                s = add(add((1, 1, 1), unit(h)), (0, 0, 0))
                p = add((1, 1, 1), unit(root))
                if s in w and p in w:
                    prefix = tuple(reversed(w[p]))  # E_ij(a) is an involution
                    words[(root, h)] = prefix + (("P", root, G),) + w[s]
                    break
            require((root, h) in words, f"witness word for root {root}, h {h}")
    return report, words


def lift(a):
    """Map an F2^3 coefficient to the matching sum of universal idempotents."""
    return sum(1 << r for r in range(ROWS) if a >> r & 1)


def run_scalar(word, rows, source, ring_one, lift_coeff):
    """Separate interpreter: dirty rows are dicts {column: ring element}."""
    rows = [dict(r) for r in rows]
    for gate in word:
        if gate[0] == "P":
            _, i, b = gate
            rows[i]["p"] = rows[i].get("p", 0) ^ (lift_coeff(b) & source)
        else:
            i, j, a = gate
            coeff = lift_coeff(a)
            require(coeff != 0, "zero coefficient")
            for key, val in rows[j].items():
                rows[i][key] = rows[i].get(key, 0) ^ (coeff & val)
    return rows


def check_word(word, root, h, ring_one, lam, lift_coeff):
    """Formal columns: one symbolic dirt column per row plus the source."""
    start = [{f"d{r}": ring_one} for r in range(ROWS)]
    end = run_scalar(word, start, ring_one, ring_one, lift_coeff)
    for r in range(ROWS):
        dirt = {k: v for k, v in end[r].items() if k != "p" and v}
        require(dirt == {f"d{r}": ring_one}, f"dirt row {r} not restored")
        require(end[r].get("p", 0) == lam[r], f"source coefficient row {r}")
    counts = [0] * ROWS
    inserts = 0
    for gate in word:
        if gate[0] == "P":
            inserts += 1
        else:
            counts[gate[0]] += 1
    want = add(add((2, 2, 2), unit(root)), unit(h))
    require(inserts == 1 and tuple(counts) == want, "word counts")
    back = run_scalar(tuple(reversed(word)), end, ring_one, ring_one, lift_coeff)
    for r in range(ROWS):
        rest = {k: v for k, v in back[r].items() if v}
        require(rest == {f"d{r}": ring_one}, "reversed word is not the inverse")


def literal_check(word):
    """All 8^3 dirty inputs and 8 sources at width one over F2^3."""
    checked = 0
    for a in itertools.product(range(8), repeat=ROWS):
        for p in range(8):
            vals = list(a)
            for gate in word:
                if gate[0] == "P":
                    vals[gate[1]] ^= gate[2] & p
                else:
                    vals[gate[0]] ^= gate[2] & vals[gate[1]]
            require(tuple(vals) == tuple(a[r] ^ (LAMBDA[r] & p)
                                         for r in range(ROWS)), "literal input")
            checked += 1
    return checked


def frontier():
    vecs = {}
    for i in range(ROWS):
        j, k = [r for r in range(ROWS) if r != i]
        vecs[f"T_{i}"] = (add(unit(i), unit(i)), add(add(unit(j), unit(j)), add(unit(k), unit(k))))
        for h in range(ROWS):
            vecs[f"U_({i},{h})"] = (unit(i), add((2, 2, 2), add(unit(h), unit(h))))
            if h != i:
                vecs[f"V_({i},{h})"] = (unit(i), add((2, 2, 2), add(unit(i), unit(h))))
    vecs["D"] = ((1, 1, 1), (0, 0, 0))
    for i, j in itertools.permutations(range(ROWS), 2):
        k = 3 - i - j
        vecs[f"R_({i},{j};{k})"] = (add(add(unit(i), unit(i)), unit(j)),
                                     add(unit(k), unit(k)))
        vecs[f"M_({i},{j};{k})"] = (add(unit(i), unit(j)),
                                     add(add(unit(i), unit(i)), add(unit(k), unit(k))))
    flat = {n: v[0] + v[1] for n, v in vecs.items()}
    for a, b in itertools.permutations(flat, 2):
        require(not all(x <= y for x, y in zip(flat[a], flat[b])),
                f"{a} dominates {b}")
    # Every one-insertion vector with >= 9 ADDs is dominated: it is >= (2,2,2)
    # plus an excess of total >= 3, and every excess of total exactly 3 already
    # dominates one of the five eight-ADD excesses of its root.
    for root in range(ROWS):
        eight = [tuple(x - 2 for x in t) for t in expected_totals(root)]
        for x in itertools.product(range(4), repeat=ROWS):
            if sum(x) == 3:
                require(any(all(u <= v for u, v in zip(e, x)) for e in eight),
                        f"undominated nine-ADD excess {x}")
    return vecs


def controls(word):
    rejected = 0
    for pos, gate in enumerate(word):
        bad = word[:pos] + word[pos + 1:]
        try:
            literal_check(bad)
        except SystemExit:
            rejected += 1
        if gate[0] != "P":
            changed = word[:pos] + ((gate[0], gate[1], gate[2] ^ 1 or 2),) + word[pos + 1:]
            try:
                literal_check(changed)
            except SystemExit:
                rejected += 1
    require(rejected == 2 * len(word) - 1, f"mutation controls rejected {rejected}")
    return rejected


def main():
    levels = enumerate_levels()
    sizes = [len(level) for level in levels]
    report, words = one_insertion_layer(levels)
    literal = 0
    for (root, h), word in sorted(words.items()):
        check_word(word, root, h, ONE, LAMBDA, lambda a: a)
        check_word(word, root, h, 15, (1, 2, 4), lift)  # universal ring F2^4
        literal += literal_check(word)
    vecs = frontier()
    rejected = controls(words[(0, 1)])
    digests = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
               for name in PACKAGE_FILES}
    receipt = {
        "marker": "PASS_FANOUT_ONE_INSERTION_PARETO",
        "level_sizes": sizes,
        "one_insertion": {str(k): v for k, v in report.items()},
        "new_words": {f"root{r}_extra{h}": [list(g) for g in w]
                      for (r, h), w in sorted(words.items())},
        "literal_input_checks": literal,
        "frontier_size": len(vecs),
        "frontier": {n: list(p) + list(k) for n, (p, k) in sorted(vecs.items())},
        "mutation_controls_rejected": rejected,
        "sha256": digests,
        "python": sys.version.split()[0],
    }
    require(len(vecs) == 31 and sizes[MAX_GATES] == 202192, "frontier totals")
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_FANOUT_ONE_INSERTION_PARETO")


if __name__ == "__main__":
    main()
