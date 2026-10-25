#!/usr/bin/env python3
"""Exact literal P104 repair-rank check. Apache-2.0; see README for credit."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PIVOTS = (0, 1, 3, 6, 22, 31, 93, 103)
ZERO = (0, 0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def authenticate():
    inputs = {}
    for item in read_json(HERE / "SOURCES.json")["files"]:
        if item["usage"] != "input":
            continue
        path = ROOT / item["path"]
        require(not path.is_symlink(), "source symlink")
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item["sha256"],
                "source SHA256: " + item["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == item["git_blob"], "source Git blob: " + item["path"])
        inputs[item["path"]] = item["sha256"]
    require(len(inputs) == 4, "complete declared source inventory")
    return inputs


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def geometry():
    # Enumerate one representative of each +/- doubled E8 root.
    roots = set()
    for positions in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[positions[0]], row[positions[1]] = 2, 2 * sign
            roots.add(tuple(row))
    for tail in itertools.product((-1, 1), repeat=7):
        if sum(x == -1 for x in tail) % 2 == 0:
            roots.add((1,) + tail)
    require(len(roots) == 120, "root representatives")
    fixture = read_json(ROOT / "research/p104-native-channel/inputs/P104-FIXTURE.json")
    section = fixture["section4_explicit_P104"]
    removed = set(map(tuple, section["F0"] + section["C"]))
    require(len(removed) == 16 and removed <= roots, "two deleted frames")
    original = sorted(roots - removed)
    order = list(PIVOTS) + [i for i in range(104) if i not in PIVOTS]
    ports = [original[i] for i in order]
    require(all(dot(a, b) % 4 == 0 for a in ports for b in ports), "dyadic Gram")
    gram2 = [[dot(a, b) // 4 for b in ports] for a in ports]
    require(all(gram2[i][j] == 2 * (i == j) for i in range(8) for j in range(8)),
            "actual pivot block is I")
    b2 = [row[8:] for row in gram2[:8]]
    require(all(sum(b2[i][s] * b2[j][s] for s in range(96)) == 48 * (i == j)
                for i in range(8) for j in range(8)), "BB^t = 12I")
    require(all(sum(b2[k][i] * b2[k][j] for k in range(8)) == 2 * gram2[8+i][8+j]
                for i in range(96) for j in range(96)), "A_NN = B^t B")
    d2 = [[gram2[i][j] - 2 * (i == j and i >= 8) for j in range(104)]
          for i in range(104)]
    source = read_json(ROOT / "research/p104-two-axis-compatibility/RESULT.json")
    labels = source["physical_labels"]
    require(len(labels) == len(set(labels)) == 104, "physical port labels")
    require(all(type(x) is int and 0 < x < 512 and x.bit_count() % 2 for x in labels),
            "odd nine-bit physical labels")
    require(all(((labels[i] & labels[j]).bit_count() % 2) == ((gram2[i][j] + 1) % 2)
                for i in range(104) for j in range(104)), "physical label/Gram binding")
    require(source["dirty_roles"] == 72, "helper boundary")
    cols = [[(i, d2[i][j]) for i in range(104) if d2[i][j]] for j in range(104)]
    return labels, b2, cols


def phase(value, exponent):
    x, y = value
    return ((x, y), (-y, x), (-x, -y), (y, -x))[exponent % 4]


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def minus(a, b):
    return a[0] - b[0], a[1] - b[1]


def half(value):
    require(value[0] % 2 == value[1] % 2 == 0, "exact integer replay scale")
    return value[0] // 2, value[1] // 2


def accumulate(state, role, value):
    new = plus(state.get(role, ZERO), value)
    if new != ZERO:
        state[role] = new
    else:
        state.pop(role, None)


def old_p(state, t, sign=1):
    """Literal old correction: second bank += T^-1 first bank."""
    out = state.copy()
    for role, value in state.items():
        if role < 104:
            v = phase(value, -t[role])
            accumulate(out, 104 + role, (sign * v[0], sign * v[1]))
    return out


def encode(state, t, dcols, swap=True):
    """Execute L then the literal N-slot exchange, not a defect formula."""
    ordered = {r: v for r, v in state.items() if r >= 104}
    for role, value in state.items():
        if role < 104:
            for target, coefficient in dcols[role]:
                v = half((coefficient * value[0], coefficient * value[1]))
                accumulate(ordered, target, v)
        elif 112 <= role < 208:
            accumulate(ordered, role - 104, phase(value, t[role - 104]))
    if not swap:
        return ordered
    return {(r + 104 if 8 <= r < 104 else r - 104 if 112 <= r < 208 else r): v
            for r, v in ordered.items()}


def difference(left, right):
    out = left.copy()
    for role, value in right.items():
        accumulate(out, role, (-value[0], -value[1]))
    return out


def b_multiply(b2, values, transpose=False):
    rows = list(zip(*b2)) if transpose else b2
    result = []
    for row in rows:
        real = sum(c * v[0] for c, v in zip(row, values))
        imag = sum(c * v[1] for c, v in zip(row, values))
        result.append(half((real, imag)))
    return result


def predicted_defect(state, t, b2):
    """New kernel calculation: E depends only on the two N inputs."""
    out = {}
    a_n = [state.get(i, ZERO) for i in range(8, 104)]
    b_n = [state.get(104+i, ZERO) for i in range(8, 104)]
    for offset, (a, b) in enumerate(zip(a_n, b_n)):
        i = offset + 8
        ka, kb = phase(a, -t[i]), phase(b, -t[i])
        accumulate(out, i, (-ka[0], -ka[1]))
        accumulate(out, 104+i, minus(kb, a))
    for j, value in enumerate(b_multiply(b2, a_n)):
        accumulate(out, 104+j, phase(value, -t[j]))
    return out


def repair(state, t, b2, first_bank_only=False, summary_noise=None):
    """Abstract exact postprocessor; not a native lowering.

    Two 96-array summaries are v=r_N and e=w_N-B^t r_J. Then
    a_N=(K+T)v-e. Helpers are untouched, not initialized clean.
    """
    r_j = [state.get(j, ZERO) for j in range(8)]
    code = b_multiply(b2, r_j, transpose=True)
    v_n = [state.get(i, ZERO) for i in range(8, 104)]
    e_n = [minus(state.get(104+i, ZERO), code[i-8]) for i in range(8, 104)]
    if summary_noise is not None:  # Deliberate dirty-summary failure control.
        bank, index, value = summary_noise
        require(bank in (0, 1) and 0 <= index < 96, "summary noise coordinate")
        target = v_n if bank == 0 else e_n
        target[index] = plus(target[index], value)
    a_n = []
    for offset, i in enumerate(range(8, 104)):
        v, e = v_n[offset], e_n[offset]
        a_n.append(minus(plus(phase(v, -t[i]), phase(v, t[i])), e))
    out = state.copy()
    for offset, i in enumerate(range(8, 104)):
        accumulate(out, i, phase(a_n[offset], -t[i]))
        if not first_bank_only:
            increment = minus(a_n[offset], phase(v_n[offset], -t[i]))
            accumulate(out, 104+i, increment)
    if not first_bank_only:
        for j, value in enumerate(b_multiply(b2, a_n)):
            v = phase(value, -t[j])
            accumulate(out, 104+j, (-v[0], -v[1]))
    return out


def validate_column(column, defect, t, b2):
    require(defect == predicted_defect({column: (4, 0)}, t, b2),
            "complete literal defect column")
    # A concrete 192-square minor, independent of the B output rows.
    projected = {r: v for r, v in defect.items() if 8 <= r < 104 or 112 <= r < 208}
    expected = {}
    if 8 <= column < 104:
        k = phase((4, 0), -t[column])
        expected = {column: (-k[0], -k[1]), column+104: (-4, 0)}
    elif 112 <= column < 208:
        expected = {column: phase((4, 0), -t[column-104])}
    require(projected == expected, "invertible N-by-N block minor")
    if column < 8 or 104 <= column < 112 or column >= 208:
        require(not defect, "complete 88-array kernel including helpers")


def phase_census(labels, b2, dcols):
    records = []
    for character in range(512):
        t = [(character & label).bit_count() % 2 for label in labels]
        digest = hashlib.sha256()
        for column in range(280):
            state = {column: (4, 0)}
            wrong = old_p(encode(state, t, dcols), t)
            correct = encode(old_p(state, t), t, dcols)
            defect = difference(wrong, correct)
            validate_column(column, defect, t, b2)
            require(repair(wrong, t, b2) == correct, "postprocessor complete boundary")
            for endpoint in (wrong, correct):
                helpers = {r: v for r, v in endpoint.items() if r >= 208}
                require(helpers == ({column: (4, 0)} if column >= 208 else {}),
                        "arbitrary dirty helper restoration")
            digest.update(canonical([column, sorted(defect.items())]))
        records.append({"character": character, "odd_N_charts": sum(t[8:]),
                        "minor_determinant": -1 if sum(t[8:]) % 2 else 1,
                        "defect_sha256": digest.hexdigest()})
    return records


def check_controls(labels, b2, dcols):
    t = [(7 & label).bit_count() % 2 for label in labels]
    rejected = []

    def reject(name, function):
        try:
            function()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)

    source = {8: (4, 0)}
    wrong = old_p(encode(source, t, dcols), t)
    correct = encode(old_p(source, t), t, dcols)
    defect = difference(wrong, correct)
    truncated = {r: v for r, v in defect.items() if r < 104}
    reject("first-bank-only-defect", lambda: validate_column(8, truncated, t, b2))
    reject("first-bank-only-repair", lambda: require(
        repair(wrong, t, b2, first_bank_only=True) == correct, "second bank not repaired"))
    opposite = {r: (-v[0], -v[1]) for r, v in defect.items()}
    reject("rank-preserving-wrong-sign", lambda: validate_column(8, opposite, t, b2))
    pivot = {0: (4, 0)}
    ordered = difference(old_p(encode(pivot, t, dcols, swap=False), t),
                         encode(old_p(pivot, t), t, dcols, swap=False))
    require(bool(ordered), "ordered-kernel control must differ")
    reject("same-rank-wrong-slot-kernel", lambda: validate_column(0, ordered, t, b2))
    reject("dirty-helper-leak", lambda: validate_column(208, {8: (4, 0)}, t, b2))
    dirt = {208: (4, 0)}
    restored = repair(old_p(encode(dirt, t, dcols), t), t, b2)
    require(restored == dirt, "nonzero arbitrary dirty fixture")
    lost = restored.copy()
    del lost[208]
    reject("erased-dirty-helper", lambda: require(lost == dirt, "helper return"))
    # Actually insert independent dirt in each summary coordinate, rather than
    # assuming those summaries are clean. Every direction changes real output.
    for bank in (0, 1):
        for index in range(96):
            noisy = repair({}, t, b2, summary_noise=(bank, index, (4, 0)))
            require(bool(noisy), "dirty summary must have nonzero output response")
    noisy = repair({}, t, b2, summary_noise=(1, 0, (4, 0)))
    reject("uncancelled-summary-dirt", lambda: require(not noisy, "summary dirt leaked"))
    dense = {r: (4 * ((r * 17) % 11 - 5), 4 * ((r * 13) % 7 - 3)) for r in range(280)}
    dense = {r: v for r, v in dense.items() if v != ZERO}
    wrong = old_p(encode(dense, t, dcols), t)
    correct = encode(old_p(dense, t), t, dcols)
    require(repair(wrong, t, b2) == correct, "dense Gaussian arbitrary-dirty control")
    return rejected


def compute():
    pins = authenticate()
    labels, b2, dcols = geometry()
    records = phase_census(labels, b2, dcols)
    controls = check_controls(labels, b2, dcols)
    require(authenticate() == pins, "source changed during replay")
    return {"schema": "p104-literal-repair-rank/v1", "status": "PASS",
            "source_sha256": pins, "scope": "ideal exact linear boundary; not native tariff",
            "ports": 104, "pivot_ports": list(PIVOTS), "nonpivot_ports": 96,
            "dirty_helpers": 72, "characters": 512, "columns_per_character": 280,
            "literal_columns": 143360, "postprocessor_columns": 143360,
            "rank_per_address": 192, "data_kernel_per_address": 16,
            "complete_kernel_per_address": 88, "minimum_linear_summary_arrays": 192,
            "dirty_summary_directions_checked": 192,
            "B_nonzero_entries": sum(bool(v) for row in b2 for v in row),
            "minor_determinant_counts": dict(Counter(str(r["minor_determinant"]) for r in records)),
            "semantic_rejections": controls, "patterns": records, "new_kappa": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit freshly derived receipt to stdout")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(canonical(result) == canonical(read_json(HERE / "RESULT.json")),
                "complete typed receipt mismatch")
        print("PASS_P104_LITERAL_REPAIR_RANK rank=192 data_kernel=16 dirty_helpers=72 "
              "characters=512 columns=143360 summary_arrays=192 controls=7 no_new_kappa")


if __name__ == "__main__":
    main()
