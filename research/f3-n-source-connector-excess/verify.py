"""Verify the excess-deletion bound and the exact eight-source F3 optimum.

Checks, with the standard library only:

1. Every certified word in CERTIFICATE.json is built call by call and
   simulated with generic noncommuting coefficients.  Its call count must equal
   the recorded value.
2. The lower-bound table: excess X(7) = 1 (cited from PR4250), the deletion
   step X(n) >= X(n-1) + 1 and the counting bound, for n = 7..64.  The
   eight-source word must meet the n = 8 bound, which makes 795 exact.
3. The deletion map of section 3 of the README applied to every source of
   every certified word: each result is simulated and its excess must equal
   X - load_j, as the proof states.
4. Mutation controls that a correct checker must reject.
"""

import hashlib
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json",
                 "CERTIFICATE.json", "verify.py")
MAX_TABLE_N = 64


def require(cond, message):
    if not cond:
        raise SystemExit("FAIL: " + message)


def floor_calls(n):
    return 3 * (n + 2 ** n - 1)


def prefix_counts(n, path):
    """q_t in F3^n after t source events, t = 0..len(path)."""
    q = [(0,) * n]
    for s in path:
        v = list(q[-1])
        v[s] = (v[s] + 1) % 3
        q.append(tuple(v))
    return q


def mask_vector(n, m):
    return tuple((m >> j) & 1 for j in range(n))


def vsum(n, vectors):
    out = [0] * n
    for v in vectors:
        for j in range(n):
            out[j] = (out[j] + v[j]) % 3
    return tuple(out)


def first_triples(n, path):
    """Lexicographically first boundary triple a <= b <= c for each mask."""
    q = prefix_counts(n, path)
    first = {}
    for a in range(len(q)):
        for b in range(a, len(q)):
            for c in range(b, len(q)):
                key = vsum(n, (q[a], q[b], q[c]))
                first.setdefault(key, (a, b, c))
    readouts = {}
    for m in range(1, 2 ** n):
        key = mask_vector(n, m)
        if key in first:
            readouts[m] = list(first[key])
    return readouts


def build_word(path, readouts):
    """Literal call list: readouts at boundary t, then source event t."""
    at = {}
    for m, bounds in readouts.items():
        for t in bounds:
            at.setdefault(t, []).append(m)
    word = []
    for t in range(len(path) + 1):
        word.extend(("A", m) for m in sorted(at.get(t, ())))
        if t < len(path):
            word.append(("B", path[t]))
    return word


def simulate(n, word):
    """Generic noncommuting simulation.

    z is a formal sum c0*z0 + sum_j c_j*(B_j x_j).  A call A_m left-multiplies
    z, so y_m accumulates c0*(A_m z0) + sum_j c_j*(A_m B_j x_j).  No relation
    between A_m and B_j is used.  Returns True when every y_m equals its mask
    row with no z0 term, z is restored, and every operator is used.
    """
    z = [1] + [0] * n
    y = {m: [0] * (n + 1) for m in range(1, 2 ** n)}
    used = set()
    for kind, idx in word:
        used.add((kind, idx))
        if kind == "B":
            require(0 <= idx < n, "source index in range")
            z[idx + 1] = (z[idx + 1] + 1) % 3
        else:
            require(idx in y, "output index in range")
            y[idx] = [(a + b) % 3 for a, b in zip(y[idx], z)]
    if z != [1] + [0] * n:
        return False
    for m, row in y.items():
        if row != [0] + list(mask_vector(n, m)):
            return False
    return True


def excess(n, word):
    extra = len(word) - floor_calls(n)
    require(extra >= 0 and extra % 3 == 0, "call count is floor + 3X")
    return extra // 3


def delete_source(n, path, readouts, j):
    """README section 3 deletion: drop source j, keep the cheaper preimage."""
    new_path = [s - (s > j) for s in path if s != j]
    # Old boundary t maps to the new boundary after the same non-j events.
    to_new = []
    seen = 0
    for t in range(len(path) + 1):
        to_new.append(seen)
        if t < len(path) and path[t] != j:
            seen += 1
    new_readouts = {}
    for mp in range(1, 2 ** (n - 1)):
        low = mp & ((1 << j) - 1)
        high = (mp >> j) << (j + 1)
        options = [low | high, low | high | (1 << j)]
        best = min(options, key=lambda m: (len(readouts[m]), m))
        new_readouts[mp] = [to_new[t] for t in readouts[best]]
    return new_path, new_readouts


def deleted_excess(n, path, readouts, j):
    """X' = sum_{i != j} e_i + sum_{m'} min(r_{m'}, r_{m' + e_j})."""
    r = {m: len(b) // 3 - 1 for m, b in readouts.items()}
    e = sum(path.count(i) // 3 - 1 for i in range(n) if i != j)
    total = 0
    for mp in range(1, 2 ** (n - 1)):
        low = mp & ((1 << j) - 1)
        high = (mp >> j) << (j + 1)
        total += min(r[low | high], r[low | high | (1 << j)])
    return e + total


def load(n, path, readouts, j):
    e_j = path.count(j) // 3 - 1
    r = sum(len(b) // 3 - 1 for m, b in readouts.items() if (m >> j) & 1)
    return e_j + r


def lower_bound_table():
    """X_lb(n) for n = 7..MAX_TABLE_N.

    Deletion step: X(n) >= X(n-1) + 1 for n >= 8.
    Counting: a word with E extra source triples has a 3n+3E event path whose
    boundary values take at most 3n+3E distinct points (q_0 = q_P), so at most
    C(3n+3E+2, 3) masks have three readouts; each other mask costs >= 1 excess.
    """
    table = {7: 1}
    count_bound = {}
    for n in range(8, MAX_TABLE_N + 1):
        masks = 2 ** n - 1
        best = None
        for e in range(0, masks + 1):
            value = e + max(0, masks - math.comb(3 * n + 3 * e + 2, 3))
            best = value if best is None else min(best, value)
            if value == e:
                break
        count_bound[n] = best
        table[n] = max(table[n - 1] + 1, best)
    return table, count_bound


def check_word(n, path, calls, label):
    require(all(path.count(s) % 3 == 0 and path.count(s) > 0 for s in range(n)),
            f"{label}: every source count is a positive multiple of three")
    readouts = first_triples(n, path)
    require(len(readouts) == 2 ** n - 1, f"{label}: every mask has a triple")
    word = build_word(path, readouts)
    require(len(word) == calls, f"{label}: {len(word)} calls, expected {calls}")
    require(simulate(n, word), f"{label}: literal word is correct")
    return readouts, word


def receipt():
    h = hashlib.sha256()
    for name in PACKAGE_FILES:
        data = (HERE / name).read_bytes()
        h.update(name.encode() + b"\0" + hashlib.sha256(data).digest())
    return h.hexdigest()


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    table, count_bound = lower_bound_table()
    for key, value in cert["lower_bound_excess"].items():
        require(table[int(key)] == value, f"lower bound X({key}) = {value}")

    exact = []
    for entry in cert["words"]:
        n, path, calls = entry["n"], entry["path"], entry["calls"]
        readouts, word = check_word(n, path, calls, f"n={n}")
        x = excess(n, word)
        require(x == entry["excess"], f"n={n}: excess {x}")
        if n >= 8:
            require(x >= table[n], f"n={n}: word respects the lower bound")
        if x == table.get(n, -1):
            exact.append(n)
        # Deletion map, every source: legal word with excess X - load_j.
        for j in range(n):
            new_path, new_readouts = delete_source(n, path, readouts, j)
            new_word = build_word(new_path, new_readouts)
            require(simulate(n - 1, new_word), f"n={n}: deletion of {j} is legal")
            require(excess(n - 1, new_word) == deleted_excess(n, path, readouts, j)
                    <= x - load(n, path, readouts, j),
                    f"n={n}: deletion of {j} has excess at most X - load_j")
    require(exact == cert["exact_n"], f"exact optima at n = {exact}")

    # PR4250's 405-call seven-source word (from PR4232), as a deletion input:
    # its excess is 1, so some source has load 1 and deletes to excess 0.
    p7 = cert["pr4232_seven_source_word"]
    q7 = prefix_counts(7, p7["path"])
    r7 = first_triples(7, p7["path"])
    r7[127] = p7["mask127_readouts"]
    require(vsum(7, [q7[t] for t in r7[127]]) == mask_vector(7, 127),
            "PR4232 mask 127 readouts")
    w7 = build_word(p7["path"], r7)
    require(len(w7) == 405 and simulate(7, w7), "PR4232 405-call word")
    loads7 = [load(7, p7["path"], r7, j) for j in range(7)]
    require(loads7 == [1] * 7, "every source of the 405 word has load 1")
    for j in range(7):
        new_path, new_readouts = delete_source(7, p7["path"], r7, j)
        new_word = build_word(new_path, new_readouts)
        require(simulate(6, new_word) and len(new_word) == floor_calls(6),
                f"405 word: deletion of {j} is a 207-call six-source word")

    # Mutation controls.
    e8 = next(e for e in cert["words"] if e["n"] == 8)
    readouts, word = check_word(8, e8["path"], e8["calls"], "control base")
    require(not simulate(8, word[:-1]), "control: dropped call rejected")
    bad = list(word)
    i = next(k for k, c in enumerate(bad) if c[0] == "B")
    bad[i] = ("B", (bad[i][1] + 1) % 8)
    require(not simulate(8, bad), "control: relabelled source call rejected")
    bad = list(word)
    i = next(k for k, c in enumerate(bad) if c[0] == "A")
    bad[i] = ("A", bad[i][1] % 255 + 1)
    require(not simulate(8, bad), "control: relabelled readout rejected")
    short = [s for s in e8["path"] if s != 0] + [0, 0, 0]
    require(len(first_triples(8, short)) < 255,
            "control: undoubling source 0 leaves some mask without a triple")
    require(table[8] == 2 and count_bound[8] == 0,
            "control: n = 8 bound comes from deletion, not counting")

    print("lower bound X_lb(n), n=7..20:",
          " ".join(f"{n}:{table[n]}" for n in range(7, 21)))
    print("receipt", receipt())
    print("PASS_F3_N_SOURCE_CONNECTOR_EXCESS opt8=795 excess_lb=n-6 exact_n="
          + ",".join(map(str, exact)))


if __name__ == "__main__":
    sys.exit(main())
