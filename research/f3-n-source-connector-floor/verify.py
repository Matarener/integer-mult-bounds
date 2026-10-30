"""Verify the unsigned F3 n-source connector floor package.

Stdlib only. Checks run with explicit exceptions so they stay active under -O.
"""
import hashlib
import itertools
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json",
                 "CERTIFICATE.json", "verify.py")
COUNT_CHECK_MAX_N = 64


class CheckError(Exception):
    pass


def require(cond, message):
    if not cond:
        raise CheckError(message)


def floor_calls(n):
    return 3 * (n + 2 ** n - 1)


def boundaries(path, n):
    q = [0] * n
    out = [tuple(q)]
    for j in path:
        q[j] = (q[j] + 1) % 3
        out.append(tuple(q))
    return out


def mask_vector(m, n):
    return tuple((m >> j) & 1 for j in range(n))


def first_triples(path, n):
    """Map each realizable nonzero binary mask to its first boundary triple."""
    qs = boundaries(path, n)
    found = {}
    for a, b, c in itertools.combinations_with_replacement(range(len(qs)), 3):
        s = tuple((qs[a][i] + qs[b][i] + qs[c][i]) % 3 for i in range(n))
        if max(s) <= 1 and any(s):
            m = sum(bit << i for i, bit in enumerate(s))
            found.setdefault(m, (a, b, c))
    return found


def build_word(path, readouts):
    """Interleave readouts (mask -> boundary tuple) into the source path."""
    at = {}
    for m, bs in readouts.items():
        for t in bs:
            at.setdefault(t, []).append(m)
    word = []
    for t in range(len(path) + 1):
        word.extend(("A", m) for m in sorted(at.get(t, [])))
        if t < len(path):
            word.append(("B", path[t]))
    return word


def simulate(word, n):
    """Generic coefficient simulation over F3 for arbitrary noncommuting maps.

    z is tracked as coefficients of (z0, B_0 x_0, ..., B_{n-1} x_{n-1}); each
    output accumulates A_m applied to that formal sum. The identity is exact
    because A calls read z and B calls only add B_j x_j to z.
    """
    z = [1] + [0] * n
    outs = {}
    for kind, idx in word:
        if kind == "B":
            z[1 + idx] = (z[1 + idx] + 1) % 3
        elif kind == "A":
            acc = outs.setdefault(idx, [0] * (n + 1))
            for i in range(n + 1):
                acc[i] = (acc[i] + z[i]) % 3
        else:
            raise CheckError(f"unknown call kind {kind}")
    return z, outs


def check_word(word, n):
    z, outs = simulate(word, n)
    require(z == [1] + [0] * n, "connector not restored")
    require(set(outs) == set(range(1, 2 ** n)), "output set mismatch")
    for m, acc in outs.items():
        require(acc[0] == 0, f"connector dirt left in output {m}")
        require(tuple(acc[1:]) == mask_vector(m, n), f"wrong row for output {m}")


def operator_counts(word):
    counts = {}
    for call in word:
        counts[call] = counts.get(call, 0) + 1
    return counts


def floor_word(path, n):
    require(sorted(path) == sorted(list(range(n)) * 3), "path must use each source thrice")
    triples = first_triples(path, n)
    require(len(triples) == 2 ** n - 1, f"n={n}: path covers {len(triples)} masks")
    return build_word(path, triples)


def check_floor(cert):
    paths = cert["floor_paths"]
    require(sorted(int(k) for k in paths) == list(range(1, 7)), "floor paths must be n=1..6")
    summary = {}
    for key, path in sorted(paths.items(), key=lambda kv: int(kv[0])):
        n = int(key)
        word = floor_word(path, n)
        check_word(word, n)
        counts = operator_counts(word)
        require(set(counts.values()) == {3}, f"n={n}: some operator not called thrice")
        require(len(counts) == n + 2 ** n - 1, f"n={n}: operator set mismatch")
        require(len(word) == floor_calls(n), f"n={n}: length mismatch")
        summary[n] = len(word)
    return summary


def delete_source(path, j):
    return [i - (i > j) for i in path if i != j]


def check_deletion(cert):
    """Deletion lemma control: removing any source keeps floor attainment."""
    checked = 0
    for key, path in cert["floor_paths"].items():
        n = int(key)
        if n == 1:
            continue
        for j in range(n):
            smaller = delete_source(path, j)
            require(len(first_triples(smaller, n - 1)) == 2 ** (n - 1) - 1,
                    f"deletion of source {j} from n={n} lost coverage")
            checked += 1
    return checked


def check_counting():
    """C(3n+3,3) bounds distinct readout triples; it is below 2^n-1 iff n>=14 here."""
    first_fail = None
    for n in range(1, COUNT_CHECK_MAX_N + 1):
        fails = math.comb(3 * n + 3, 3) < 2 ** n - 1
        if fails and first_fail is None:
            first_fail = n
        require(fails == (n >= 14), f"counting status unexpected at n={n}")
    # For n >= 14 the ratio C(3n+6,3)/C(3n+3,3) < 2, so the gap persists;
    # the deletion lemma gives the same conclusion without this ratio.
    for n in range(14, COUNT_CHECK_MAX_N + 1):
        num = (3 * n + 6) * (3 * n + 5) * (3 * n + 4)
        den = (3 * n + 3) * (3 * n + 2) * (3 * n + 1)
        require(num < 2 * den, "triple-count growth ratio not below two")
    require(math.comb(42, 3) == 11480 and math.comb(45, 3) == 14190, "binomial table")
    return first_fail


def check_seven(cert):
    s = cert["seven_source_upper"]
    n = 7
    path = s["path"]
    require(sorted(path) == sorted(list(range(n)) * 3), "seven-source path counts")
    triples = first_triples(path, n)
    missing = sorted(set(range(1, 2 ** n)) - set(triples))
    require(missing == [s["uncovered_triple_mask"]], f"unexpected uncovered masks {missing}")
    six = tuple(s["six_readout_boundaries"])
    qs = boundaries(path, n)
    total = tuple(sum(qs[t][i] for t in six) % 3 for i in range(n))
    require(total == mask_vector(missing[0], n), "six-readout sum mismatch")
    readouts = dict(triples)
    readouts[missing[0]] = six
    word = build_word(path, readouts)
    check_word(word, n)
    require(len(word) == s["calls"] == floor_calls(n) + 3, "seven-source length")
    return len(word), missing[0]


def check_controls(cert):
    """Mutations that must be rejected."""
    rejected = 0
    path6 = cert["floor_paths"]["6"]
    word = floor_word(path6, 6)
    for mutate in (
        lambda w: w[:-1] if w[-1][0] == "A" else w[1:],
        lambda w: [c for c in w if c != ("A", 63)][:] + [("A", 63)] * 2,
        lambda w: [c for c in w if c != ("B", 0)] + [("B", 0)] * 2,
        lambda w: [("B", 1) if c == ("B", 0) else c for c in w],
    ):
        try:
            check_word(mutate(word), 6)
        except CheckError:
            rejected += 1
    try:
        floor_word([0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3], 4)
    except CheckError:
        rejected += 1
    require(rejected == 5, f"only {rejected} of 5 controls rejected")
    return rejected


def receipt():
    h = hashlib.sha256()
    for name in PACKAGE_FILES:
        data = (HERE / name).read_bytes()
        h.update(name.encode() + b"\0" + hashlib.sha256(data).hexdigest().encode() + b"\n")
    return h.hexdigest()


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    require(cert["field"] == "F3", "field")
    floor = check_floor(cert)
    deletions = check_deletion(cert)
    first_fail = check_counting()
    seven_calls, seven_mask = check_seven(cert)
    controls = check_controls(cert)
    print("floor_calls", " ".join(f"n{n}={c}" for n, c in floor.items()))
    print(f"deletion_checks={deletions} counting_first_failure_n={first_fail} "
          f"seven_source_calls={seven_calls} six_readout_mask={seven_mask} controls={controls}")
    print("receipt_sha256", receipt())
    print(f"PASS_F3_N_SOURCE_CONNECTOR_FLOOR attained_n=1..6 counting_excludes_n>={first_fail} "
          f"n7_upper={seven_calls}")


if __name__ == "__main__":
    try:
        main()
    except CheckError as exc:
        print("FAIL", exc)
        sys.exit(1)
