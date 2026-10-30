"""Exact joint guard counts for k corank-one requests; standard library, read-only."""

import hashlib
import itertools
import json
from fractions import Fraction
from math import factorial
from pathlib import Path

# Binary k=3 spectrum (eigenvalue, signed multiplicity) proved in PROOF.md.
K3_TERMS = ((27, 1), (21, -6), (19, 6), (17, -6), (15, 16), (13, -18), (11, 9), (9, -2))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def gl_order(q, n):
    value = 1
    for i in range(n):
        value *= q**n - q**i
    return value


def pair_total(q, m, k):
    """Number of pairs X (m x k), Y (k x m) with YX = I_k."""
    value = q ** (k * (m - k))
    for i in range(k):
        value *= q**m - q**i
    return value


def k3_closed_form(m):
    n = m - 1
    numerator = sum(mult * base**n for base, mult in K3_TERMS)
    need(numerator >= 0 and numerator % 64 == 0, "integral k=3 numerator")
    return numerator // 64


def increment_weights(q, k, zero_weight=None):
    """Count ordered pairs (y, x) in K^k x K^k by the matrix y x^T."""
    weights = {}
    for y in itertools.product(range(q), repeat=k):
        for x in itertools.product(range(q), repeat=k):
            key = tuple(y[i] * x[j] % q for i in range(k) for j in range(k))
            weights[key] = weights.get(key, 0) + 1
    zero = (0,) * (k * k)
    need(weights[zero] == 2 * q**k - 1, "zero increment multiplicity")
    need(all(w == q - 1 for key, w in weights.items() if key != zero), "rank one")
    if zero_weight is not None:
        weights[zero] = zero_weight
    return weights


def safe(state, k):
    return all(state[i * k + i] != 1 for i in range(k))


def transfer_counts(q, k, maximum, zero_weight=None):
    """C(q, m, k) for m = 1..maximum via the k x k partial Gram walk."""
    weights = increment_weights(q, k, zero_weight)
    steps = [(key, w) for key, w in weights.items()]
    identity = tuple(int(i == j) for i in range(k) for j in range(k))
    current = {(0,) * (k * k): 1}
    counts = {}
    for m in range(1, maximum + 1):
        closing = 0
        for state, ways in current.items():
            last = tuple((identity[i] - state[i]) % q for i in range(k * k))
            closing += ways * weights.get(last, 0)
        counts[m] = closing
        following = {}
        for state, ways in current.items():
            for key, w in steps:
                nxt = tuple((state[i] + key[i]) % q for i in range(k * k))
                if safe(nxt, k):
                    following[nxt] = following.get(nxt, 0) + ways * w
        current = following
    return counts


def character_value(k, bits, off):
    c = dict(zip(off, bits, strict=True))
    total = 0
    for sigma in itertools.product(range(3), repeat=k):
        sources = [i for i in range(k) if sigma[i] == 1]
        targets = [j for j in range(k) if sigma[j] == 2]
        exponent = sum(c[(i, j)] for i in sources for j in targets)
        total += -1 if exponent % 2 else 1
    return total


def binary_spectrum(k):
    """Signed eigenvalue multiplicities of the binary character formula."""
    off = [(i, j) for i in range(k) for j in range(k) if i != j]
    net = {}
    for bits in itertools.product((0, 1), repeat=len(off)):
        value = character_value(k, bits, off)
        net[value] = net.get(value, 0) + (-1) ** sum(bits)
    return {value: mult for value, mult in net.items() if mult}


def character_count(spectrum, k, m):
    total = sum(mult * value ** (m - 1) for value, mult in spectrum.items())
    need(total % 2 ** (k * (k - 1)) == 0, "integral character count")
    return total // 2 ** (k * (k - 1))


def solve_inverse(g, q, m):
    """Gauss-Jordan inverse over the prime field F_q, or None if singular."""
    a = [list(row) + [int(i == j) for j in range(m)] for i, row in enumerate(g)]
    for col in range(m):
        pivot = next((r for r in range(col, m) if a[r][col]), None)
        if pivot is None:
            return None
        a[col], a[pivot] = a[pivot], a[col]
        scale = pow(a[col][col], q - 2, q)
        a[col] = [v * scale % q for v in a[col]]
        for r in range(m):
            if r != col and a[r][col]:
                f = a[r][col]
                a[r] = [(v - f * w) % q for v, w in zip(a[r], a[col], strict=True)]
    return [row[m:] for row in a]


def leading_guards(a, q, m, depth):
    """No-pivot elimination: True iff leading minors of orders 1..depth are nonzero."""
    a = [list(row) for row in a]
    for col in range(depth):
        if a[col][col] == 0:
            return False
        inv = pow(a[col][col], q - 2, q)
        for r in range(col + 1, m):
            if a[r][col]:
                f = a[r][col] * inv % q
                a[r] = [(v - f * w) % q for v, w in zip(a[r], a[col], strict=True)]
    return True


def conjugate_request(g, gi, axis, q, m):
    """G (I - e_axis e_axis^T) G^-1, computed as I - (G e_axis)(e_axis^T G^-1)."""
    return [
        [(int(i == j) - g[i][axis] * gi[axis][j]) % q for j in range(m)]
        for i in range(m)
    ]


def enumerate_headers(q, m, kmax):
    """Literal census over GL_m(F_q): joint pass counts for k = 1..kmax.

    first_only counts headers passing only the order-one guards of the first
    min(kmax, 3) requests; it is a control, not a law.
    """
    total = 0
    joint = dict.fromkeys(range(1, kmax + 1), 0)
    first_only = 0
    for flat in itertools.product(range(q), repeat=m * m):
        g = [list(flat[i * m : (i + 1) * m]) for i in range(m)]
        gi = solve_inverse(g, q, m)
        if gi is None:
            continue
        total += 1
        passes = [
            leading_guards(conjugate_request(g, gi, t, q, m), q, m, m - 1)
            for t in range(kmax)
        ]
        for k in range(1, kmax + 1):
            joint[k] += all(passes[:k])
        first_only += all(
            leading_guards(conjugate_request(g, gi, t, q, m), q, m, 1)
            for t in range(min(kmax, 3))
        )
    need(total == gl_order(q, m), "GL census size")
    return total, joint, first_only


def check_threshold(tables):
    """Binary: a common header exists iff m >= k + 1; count 2 k! at m = k + 1."""
    observed = {}
    for k, table in tables.items():
        if k < 2:
            continue
        need(all(table[m] == 0 for m in range(1, k + 1)), "no header for m <= k")
        need(all(table[m] > 0 for m in table if m > k), "header for m > k")
        observed[k] = table[k + 1]
        if k >= 3:
            need(table[k + 1] == 2 * factorial(k), "row/column decompositions only")
    return observed


def check_correlation(maximum):
    """Binary k=3: strict negative correlation for 4 <= m <= maximum."""
    for m in range(4, maximum + 1):
        joint = Fraction(k3_closed_form(m), pair_total(2, m, 3))
        single = Fraction(3 ** (m - 1), (2**m - 1) * 2 ** (m - 1))
        need(joint < single**3, "negative correlation at m=%d" % m)
    return maximum


def check_sources(package, root):
    sources = json.loads((package / "SOURCES.json").read_text())
    for row in sources["files"]:
        actual = hashlib.sha256((root / row["path"]).read_bytes()).hexdigest()
        need(actual == row["sha256"], "source hash mismatch: " + row["path"])


def emit_receipt(package, root, result):
    paths = sorted(p for p in package.iterdir() if p.is_file() and p.suffix != ".pyc")
    result["sha256"] = {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths
    }
    print("PASS_CORANKONE_TRIPLE_HEADER_LAW " + json.dumps(result, sort_keys=True))


def binary_checks():
    limits = {1: 40, 2: 40, 3: 30, 4: 12}
    tables = {k: transfer_counts(2, k, lim) for k, lim in limits.items()}
    spectra = {k: binary_spectrum(k) for k in (1, 2, 3, 4)}
    need(spectra[3] == dict(K3_TERMS), "k=3 spectrum")
    need(spectra[2] == {9: 1, 7: -2, 5: 1}, "k=2 spectrum (#4261)")
    for k, table in tables.items():
        for m in range(k, limits[k] + 1):
            need(table[m] == character_count(spectra[k], k, m), "character law")
    for m in range(1, limits[3] + 1):
        need(tables[3][m] == k3_closed_form(m), "k=3 closed form")
    for m in range(2, limits[2] + 1):
        n = m - 1
        need(4 * tables[2][m] == 9**n - 2 * 7**n + 5**n, "#4261 binary pair law")
    for m in range(1, limits[1] + 1):
        need(tables[1][m] == 3 ** (m - 1), "#4227 binary corank-one marginal")
    return tables, spectra


def odd_checks():
    limits = {1: 10, 2: 8, 3: 5}
    tables = {k: transfer_counts(3, k, lim) for k, lim in limits.items()}
    for m in range(2, limits[1] + 1):
        need(tables[1][m] == 7 ** (m - 1) * 2, "#4227 ternary corank-one marginal")
    need(Fraction(tables[2][2], pair_total(3, 2, 2)) == Fraction(2 * 1, 3 * 4), "#4239")
    return tables


def header_checks(binary, odd):
    tables = {2: binary, 3: odd}
    cases = ((2, 2), (2, 3), (2, 4), (3, 2), (3, 3))
    results = {}
    for q, m in cases:
        kmax = min(m, 4)
        total, joint, first_only = enumerate_headers(q, m, kmax)
        for k in range(1, kmax + 1):
            fiber = gl_order(q, m - k)
            need(total == pair_total(q, m, k) * fiber, "equal header fibers")
            need(joint[k] == tables[q][k][m] * fiber, "census versus transfer")
        results[f"{q},{m}"] = [total, [joint[k] for k in range(1, kmax + 1)], first_only]
        if q == 2 and m == 4:
            need(first_only != joint[3], "first-pivot-only control differs")
    return results


def controls(binary):
    lost_zero = transfer_counts(2, 3, 6, zero_weight=1)
    need(lost_zero[5] != binary[3][5], "omitted zero multiplicity control")
    joint = Fraction(binary[3][5], pair_total(2, 5, 3))
    single = Fraction(binary[1][5], pair_total(2, 5, 1))
    need(joint != single**3, "independence control")
    wrong = sum(mult * base**3 for base, mult in K3_TERMS if mult > 0) // 64
    need(wrong != binary[3][4], "dropped negative characters control")
    return 3


def main():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    check_sources(package, root)
    binary, spectra = binary_checks()
    odd = odd_checks()
    headers = header_checks(binary, odd)
    result = {
        "binary_counts": {str(k): [t[m] for m in sorted(t)] for k, t in binary.items()},
        "ternary_counts": {str(k): [t[m] for m in sorted(t)] for k, t in odd.items()},
        "binary_spectra": {str(k): sorted(s.items(), reverse=True) for k, s in spectra.items()},
        "threshold_counts": check_threshold(binary),
        "k3_negative_correlation_checked_to_m": check_correlation(400),
        "header_census": headers,
        "controls": controls(binary),
    }
    emit_receipt(package, root, result)


if __name__ == "__main__":
    main()
