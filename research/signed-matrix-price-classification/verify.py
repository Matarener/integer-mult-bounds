#!/usr/bin/env python3
"""Construct optimal priced words for the complete signed 3-by-3 domain."""

import argparse
import hashlib
import itertools
import json
import random
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
TARGET = (1, 1, 1, 1, 1, -1, 1, -1, 0)
NAMES = ("B0", "B1", "B2", "A0", "A1", "A2")
CHARS = (0, 2, 3, 4, 5, 8)
MAX_CHAR = 256
MAX_WORD = 6 * MAX_CHAR

# Restated from Nick Petalas's PR4241, head ec573175d36cb016661f37293dd9ee2aefb737bb.
# A starred token means c-2 consecutive copies. These are predecessor words.
TEMPLATES = (
    "B1- A1- A2+ B2- A0- B1+ B0+ A1+ B2+ A0+ B0+* A2- B0+",
    "B1+ A0+ B1+* A2+ B0- A1- B1+ A2- B2- A0- B0+ A1+ B2+",
    "A2- B1- B2+ A1- B2+* A0- B0+ B2+ A2+ B1+ A1+ A0+ B0-",
    "A0+* B2+ A0+ A1- B2- B1+ A2- B0+ A0+ A1+ B1- A2+ B0-",
    "A1+ B2+ A1+* B0+ A2+ B1+ A1+ A0+ B0- A2- B2- B1- A0-",
    "A2+ A1- B2- A0- B0+ B1+ A1+ B2+ A2+ A0+ B0- A2+* B1-",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inputs():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    result = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            require(sha(data) == row["sha256"], "source hash: " + row["path"])
            result[row["path"]] = json.loads(data)
    require(len(result) == 2, "two live predecessor inputs")
    return result


def active(matrix):
    columns = tuple(j for j in range(3) if any(matrix[3*i+j] for i in range(3)))
    rows = tuple(3+i for i in range(3) if any(matrix[3*i:3*i+3]))
    return columns + rows


def action(word):
    """Exact coefficients, sufficient for arbitrary noncommuting maps."""
    require(len(word) <= MAX_WORD, "word capacity")
    q, dirt, matrix = [0]*3, [0]*3, [0]*9
    for op, sign in word:
        require(op in range(6) and sign in (-1, 1), "query domain")
        if op < 3:
            q[op] += sign
        else:
            i = op - 3
            dirt[i] += sign
            for j in range(3):
                matrix[3*i+j] += sign*q[j]
    return q + dirt + matrix


def correct(word, matrix, char):
    residual = action(word)
    residual[6:] = [a-b for a, b in zip(residual[6:], matrix)]
    return all((x % char if char else x) == 0 for x in residual)


def profile(word):
    counts = [[0, 0] for _ in range(6)]
    for op, sign in word:
        counts[op][sign < 0] += 1
    return tuple(tuple(pair) for pair in counts)


def orbit():
    """Return one explicit signed-permutation map for each orbit target."""
    result = {}
    signs = tuple(itertools.product((-1, 1), repeat=3))
    for rows, cols in itertools.product(itertools.permutations(range(3)), repeat=2):
        for rs, cs in itertools.product(signs, repeat=2):
            matrix = tuple(rs[i]*cs[j]*TARGET[3*rows[i]+cols[j]]
                           for i in range(3) for j in range(3))
            mapping = tuple((cols.index(j), cs[cols.index(j)]) for j in range(3))
            mapping += tuple((3+rows.index(i), rs[rows.index(i)]) for i in range(3))
            result.setdefault(matrix, mapping)
    require(len(result) == 288, "orbit cardinality")
    return result


def transform(word, mapping):
    return tuple((mapping[op][0], sign*mapping[op][1]) for op, sign in word)


def readout_word(path, pairs, matrix):
    word = []
    needed = active(matrix)
    for slot in range(7):
        for i, (minus, plus) in enumerate(pairs):
            if i+3 in needed:
                if minus == slot:
                    word.append((i+3, -1))
                if plus == slot:
                    word.append((i+3, 1))
        if slot < 6 and path[slot][0] in needed:
            word.append(path[slot])
    return tuple(word)


def support_words():
    """Instantiate PR944's support-word recipe; no exclusion is re-proved."""
    result = {}
    moves = tuple((j, s) for j in range(3) for s in (-1, 1))
    for path in itertools.permutations(moves):
        q, vertices = [0]*3, [(0, 0, 0)]
        for j, sign in path:
            q[j] += sign
            vertices.append(tuple(q))
        pairs = {}
        for minus, plus in itertools.product(range(7), repeat=2):
            row = tuple(a-b for a, b in zip(vertices[plus], vertices[minus]))
            pairs.setdefault(row, (minus, plus))
        for rows in itertools.product(pairs, repeat=3):
            matrix = rows[0] + rows[1] + rows[2]
            if matrix not in result:
                result[matrix] = readout_word(path, [pairs[r] for r in rows], matrix)
    require(len(result) == 19395, "PR944 support-word coverage")
    return result


def template(op, char):
    word = []
    for token in TEMPLATES[op].split():
        query = (NAMES.index(token[:2]), 1 if token[2] == "+" else -1)
        word.extend([query] * (char-2 if token.endswith("*") else 1))
    return tuple(word)


def envelope(matrix, prices, char, obstructed):
    operators = active(matrix)
    if not operators:
        return 0
    sigma = [prices[2*k] + prices[2*k+1] for k in operators]
    mu = [min(prices[2*k:2*k+2]) for k in operators]
    b = [min(s, char*m) if char else s for s, m in zip(sigma, mu)]
    u = [min(2*s, char*m) if char else 2*s for s, m in zip(sigma, mu)]
    return sum(b) + (min(v-w for v, w in zip(u, b)) if obstructed else 0)


def optimal_word(matrix, prices, char, support, transforms, repairs):
    """Price-aware orbit transport followed by local sign conversion."""
    if matrix in support:
        base = support[matrix]
    else:
        mapping = transforms[matrix]
        sigma = [prices[2*k]+prices[2*k+1] for k in range(6)]
        mu = [min(prices[2*k:2*k+2]) for k in range(6)]
        cheap = [k for k in range(6) if char and char*mu[k] <= sigma[k]]
        extra = [min(2*s, char*m)-s if char else s for s, m in zip(sigma, mu)]
        chosen = cheap[0] if cheap else min(range(6), key=extra.__getitem__)
        old = next(k for k in range(6) if mapping[k][0] == chosen)
        if char and (cheap or char*mu[chosen] < 2*sigma[chosen]):
            base = transform(template(old, char), mapping)
            keep = 1 if prices[2*chosen] <= prices[2*chosen+1] else -1
            if mapping[old][1] != keep:
                base = tuple((op, -s) for op, s in base)
        else:
            base = transform(repairs[old], mapping)
    counts = profile(base)
    result = []
    for op, sign in base:
        plus, minus = prices[2*op:2*op+2]
        if char and counts[op] == (1, 1) and char*min(plus, minus) <= plus+minus:
            keep = 1 if plus <= minus else -1
            result.extend([(op, keep)] * (1 if sign == keep else char-1))
        else:
            result.append((op, sign))
    require(len(result) <= MAX_WORD, "constructed word capacity")
    return tuple(result)


def checked_case(matrix, prices, char, support, transforms, repairs):
    word = optimal_word(matrix, prices, char, support, transforms, repairs)
    require(correct(word, matrix, char), "constructed dirty action")
    bill = sum(prices[2*op+(sign < 0)] for op, sign in word)
    expected = envelope(matrix, prices, char, matrix in transforms)
    require(bill == expected, "constructed bill differs from closed envelope")
    return word


def transport_checks(transforms, repairs):
    cases = 0
    for matrix, mapping in transforms.items():
        require(sorted(op for op, _ in mapping) == list(range(6)), "operator permutation")
        for old, char, flip in itertools.product(range(6), (0, 2, 3, 4, 5, 8, 12, 16), (-1, 1)):
            base = template(old, char) if char else repairs[old]
            word = transform(tuple((op, sign*flip) for op, sign in base), mapping)
            require(correct(word, matrix, char), "transported anchor action")
            expected = [(1, 1)]*6
            new, sign = mapping[old]
            expected[new] = ((char, 0) if sign*flip == 1 else (0, char)) if char else (2, 2)
            require(profile(word) == tuple(expected), "transported anchor profile")
            cases += 1
    return cases


def related_values():
    unit = [envelope(TARGET, (1,)*12, c, True) for c in (0, 2, 3, 4, 5, 8)]
    asymmetric = [envelope(TARGET, (1, 3)*6, c, True) for c in (0, 3, 4, 5, 8)]
    require(unit == [14, 12, 13, 14, 14, 14], "PR4233 equal-sign specialization")
    require(asymmetric == [28, 18, 24, 25, 28], "PR4241 canonical specialization")
    return {"PR4233_unit": unit, "PR4241_asymmetric": asymmetric}


def count_profile_bound(matrix, prices, char, obstructed):
    """Independent finite DP over legal per-operator plus/minus counts."""
    costs = {False: 0}
    bound = max(4, 2*char)
    for op in active(matrix):
        choices = {}
        for plus, minus in itertools.product(range(bound+1), repeat=2):
            diff = plus-minus
            if plus+minus < 2 or (diff % char if char else diff) != 0:
                continue
            raised = (plus, minus) != (1, 1)
            price = plus*prices[2*op] + minus*prices[2*op+1]
            choices[raised] = min(choices.get(raised, price), price)
        updated = {}
        for old, value in costs.items():
            for raised, price in choices.items():
                flag = old or raised
                updated[flag] = min(updated.get(flag, value+price), value+price)
        costs = updated
    return costs[True] if obstructed and char != 2 else min(costs.values())


def dense(word, matrix, char, seed):
    """Independent literal 2-coordinate, noncommuting dirty-array execution."""
    a = (((1, 2), (0, 1)), ((0, 1), (-1, 3)), ((2, 0), (1, -1)))
    b = (((1, 0), (1, 1)), ((3, -1), (2, 0)), ((0, 2), (1, 1)))
    initial = [[((seed+3)*(2*i+1)+j*j) % 11 - 5 for j in range(2)] for i in range(7)]
    state = [row[:] for row in initial]
    expected = [row[:] for row in initial]
    for i, j in itertools.product(range(3), repeat=2):
        bx = [sum(b[j][r][s]*initial[j][s] for s in range(2)) for r in range(2)]
        for r in range(2):
            expected[i+3][r] += matrix[3*i+j]*sum(a[i][r][s]*bx[s] for s in range(2))
    for op, sign in word:
        source, target, linear = (op, 6, b[op]) if op < 3 else (6, op, a[op-3])
        increment = [sum(linear[r][s]*state[source][s] for s in range(2)) for r in range(2)]
        for r in range(2):
            state[target][r] += sign*increment[r]
    residual = [state[i][j]-expected[i][j] for i in range(7) for j in range(2)]
    require(all((v % char if char else v) == 0 for v in residual), "dense dirty replay")


def evidence(support, transforms, repairs):
    matrices = tuple(itertools.product((-1, 0, 1), repeat=9))
    require(set(support).isdisjoint(transforms), "classification partition")
    require(set(support) | set(transforms) == set(matrices), "full target domain")
    vectors = ((1,)*12, (1, 3)*6, tuple(range(1, 13)), (3, 1, 1, 7, 4, 2, 2, 9, 6, 1, 5, 3))
    cases = 0
    for matrix, char, prices in itertools.product(matrices, CHARS, vectors):
        checked_case(matrix, prices, char, support, transforms, repairs)
        cases += 1
    dense_cases = random_cases = dp_cases = controls = 0
    rng = random.Random(4241)
    samples = [matrices[0], matrices[-1], (0,)*9, TARGET]
    samples += [matrices[rng.randrange(len(matrices))] for _ in range(28)]
    for case in range(24):
        prices = tuple(Fraction(rng.randrange(1, 20), rng.randrange(1, 8)) for _ in range(12))
        char = (0, 2, 3, 4, 5, 8, 12, 16)[case % 8]
        for matrix in transforms:
            checked_case(matrix, prices, char, support, transforms, repairs)
            random_cases += 1
        for matrix in samples:
            word = checked_case(matrix, prices, char, support, transforms, repairs)
            for seed in range(3):
                dense(word, matrix, char, seed)
                dense_cases += 1
            require(count_profile_bound(matrix, prices, char, matrix in transforms)
                    == envelope(matrix, prices, char, matrix in transforms), "profile DP")
            dp_cases += 1
            if word:
                require(not correct(word[:-1], matrix, char), "deleted last query control")
                controls += 1
    return {"targets": len(matrices), "orbit": len(transforms), "priced_words": cases,
            "rational_orbit_words": random_cases, "profile_dp": dp_cases,
            "dense_cases": dense_cases, "deletion_controls": controls}


def receipt(counts):
    files = {p.name: sha(p.read_bytes()) for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    live = {r["path"]: sha((ROOT/r["path"]).read_bytes())
            for r in manifest["files"] if r["usage"] == "input"}
    return {"schema_version": 1, "counts": counts, "package_sha256": files,
            "input_sha256": live}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write generated source-bound JSON outside checkout")
    args = parser.parse_args()
    if args.receipt:
        require(not args.receipt.resolve().is_relative_to(ROOT), "receipt must be outside checkout")
    data = inputs()
    source = data["research/weighted-signed-connector-seed58/CERTIFICATE.json"]
    repairs = tuple(tuple((NAMES.index(k+str(i)), s) for k, i, s in source["witnesses"][name])
                    for name in NAMES)
    transforms, support = orbit(), support_words()
    listed = data["research/signed-connector-obstruction/CERTIFICATE.json"]["obstructed_patterns"]
    require(set(transforms) == {tuple(v for row in m for v in row) for m in listed}, "orbit input")
    counts = evidence(support, transforms, repairs)
    counts["transported_anchors"] = transport_checks(transforms, repairs)
    counts["related_values"] = related_values()
    result = receipt(counts)
    if args.receipt:
        args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print("PASS_SIGNED_MATRIX_PRICE_CLASSIFICATION " + json.dumps(counts, sort_keys=True))
    print("GENERATED_RECEIPT_SHA256 " + sha(json.dumps(result, sort_keys=True).encode()))


if __name__ == "__main__":
    main()
