#!/usr/bin/env python3
"""Finite evidence for the sign-dependent signed-connector tariff."""

import argparse
import hashlib
import itertools
import json
import random
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
TARGET = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
OPERATORS = (("B", 0), ("B", 1), ("B", 2), ("A", 0), ("A", 1), ("A", 2))
NAMES = tuple(kind + str(index) for kind, index in OPERATORS)
CHARACTERISTICS = (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 16)
SYMBOLIC_RANGE = range(2, 41)
MAX_QUERIES = 6 * 2 * 16 + 4

# Each entry is (kind, index, sign, a, b): the query repeated a + b*c times.
# The anchored operator F occurs c times with sign +1; every other operator
# occurs once with each sign.  All repeat counts are nonnegative for c >= 2.
TEMPLATES = {
    "B0": "B1- A1- A2+ B2- A0- B1+ B0+ A1+ B2+ A0+ B0+* A2- B0+",
    "B1": "B1+ A0+ B1+* A2+ B0- A1- B1+ A2- B2- A0- B0+ A1+ B2+",
    "B2": "A2- B1- B2+ A1- B2+* A0- B0+ B2+ A2+ B1+ A1+ A0+ B0-",
    "A0": "A0+* B2+ A0+ A1- B2- B1+ A2- B0+ A0+ A1+ B1- A2+ B0-",
    "A1": "A1+ B2+ A1+* B0+ A2+ B1+ A1+ A0+ B0- A2- B2- B1- A0-",
    "A2": "A2+ A1- B2- A0- B0+ B1+ A1+ B2+ A2+ A0+ B0- A2+* B1-",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_inputs():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = {}
    for entry in manifest["files"]:
        if entry["usage"] == "input":
            path = ROOT / entry["path"]
            data = path.read_bytes()
            require(digest(data) == entry["sha256"], f"source hash: {path}")
            inputs[entry["path"]] = data
    require(len(inputs) == 2, "two live inputs")
    return inputs


def parse_template(text):
    """A token 'X+*' is the block X+ repeated c-2 times."""
    template = []
    for token in text.split():
        require(len(token) in (3, 4) and token[2] in "+-", "template token")
        sign = 1 if token[2] == "+" else -1
        repeat = (-2, 1) if token.endswith("*") else (1, 0)
        template.append((token[0], int(token[1]), sign) + repeat)
    return tuple(template)


def normalize(value, characteristic):
    return value % characteristic if characteristic else value


def coefficient_action(word):
    """Integer source, dirt and read coefficients of a literal query word."""
    require(0 < len(word) <= MAX_QUERIES, "word length outside evidence domain")
    source, dirt = [0, 0, 0], [0, 0, 0]
    rows = [[0, 0, 0] for _ in range(3)]
    for kind, index, sign in word:
        require(kind in "AB" and index in range(3) and sign in (-1, 1), "query")
        if kind == "B":
            source[index] += sign
        else:
            dirt[index] += sign
            for column in range(3):
                rows[index][column] += sign * source[column]
    return source + dirt + [rows[i][j] - TARGET[i][j]
                            for i in range(3) for j in range(3)]


def correct(word, characteristic):
    return all(normalize(value, characteristic) == 0
               for value in coefficient_action(word))


def profile(word):
    """Per operator (number of + queries, number of - queries)."""
    return tuple((sum(q == (kind, index, 1) for q in word),
                  sum(q == (kind, index, -1) for q in word))
                 for kind, index in OPERATORS)


def symbolic_residual(template):
    """Residual as affine pairs (constant, coefficient of c)."""
    source = [(0, 0)] * 3
    dirt = [(0, 0)] * 3
    rows = [[(0, 0)] * 3 for _ in range(3)]
    for kind, index, sign, a, b in template:
        if kind == "B":
            x = source[index]
            source[index] = (x[0] + sign * a, x[1] + sign * b)
            continue
        x = dirt[index]
        dirt[index] = (x[0] + sign * a, x[1] + sign * b)
        for column in range(3):
            s, r = source[column], rows[index][column]
            require(b == 0 or s[1] == 0, "affine product")
            rows[index][column] = (r[0] + sign * a * s[0],
                                   r[1] + sign * (a * s[1] + b * s[0]))
    rows = [[(rows[i][j][0] - TARGET[i][j], rows[i][j][1])
             for j in range(3)] for i in range(3)]
    return source + dirt + [cell for row in rows for cell in row]


def expand(template, characteristic):
    word = []
    for kind, index, sign, a, b in template:
        repeat = a + b * characteristic
        require(repeat >= 0, "negative repeat")
        word.extend([(kind, index, sign)] * repeat)
    return tuple(word)


def flip(word):
    return tuple((kind, index, -sign) for kind, index, sign in word)


def convert(word, name, keep_sign, characteristic):
    """Replace each query of `name` with sign -keep_sign by c-1 keep_sign queries."""
    kind, index = name[0], int(name[1])
    out = []
    for query in word:
        if query == (kind, index, -keep_sign):
            out.extend([(kind, index, keep_sign)] * (characteristic - 1))
        else:
            out.append(query)
    return tuple(out)


def template_checks():
    templates = {name: parse_template(text) for name, text in TEMPLATES.items()}
    cases = 0
    for position, name in enumerate(NAMES):
        template = templates[name]
        residual = symbolic_residual(template)
        require(all(constant == 0 for constant, _ in residual),
                "residual is not a multiple of c")
        for characteristic in SYMBOLIC_RANGE:
            word = expand(template, characteristic)
            require(len(word) == 10 + characteristic, "template length")
            expected = tuple((characteristic, 0) if k == position else (1, 1)
                             for k in range(6))
            require(profile(word) == expected, "template profile")
            require(correct(word, characteristic), "template action")
            require(correct(flip(word), characteristic), "flipped template")
            require(profile(flip(word)) == tuple((b, a) for a, b in expected),
                    "flipped profile")
            cases += 2
    return templates, cases


def conversion_checks(templates, integer_words):
    cases = 0
    for characteristic in range(2, 10):
        bases = [expand(t, characteristic) for t in templates.values()]
        bases += list(integer_words.values())
        for base in bases:
            for choice in itertools.product((0, 1, -1), repeat=6):
                word = base
                for name, keep in zip(NAMES, choice):
                    if keep and profile(base)[NAMES.index(name)] == (1, 1):
                        word = convert(word, name, keep, characteristic)
                require(correct(word, characteristic), "converted word")
                cases += 1
    return cases


def integer_witnesses(inputs):
    data = json.loads(inputs["research/weighted-signed-connector-seed58/CERTIFICATE.json"])
    require(data["matrix"] == [list(row) for row in TARGET], "PR1088 target")
    words = {}
    for position, name in enumerate(NAMES):
        word = tuple(tuple(query) for query in data["witnesses"][name])
        expected = tuple((2, 2) if k == position else (1, 1) for k in range(6))
        require(profile(word) == expected, "PR1088 profile")
        require(correct(word, 0), "PR1088 integer action")
        words[name] = word
    obstruction = json.loads(inputs["research/signed-connector-obstruction/CERTIFICATE.json"])
    patterns = obstruction["obstructed_patterns"]
    require([list(row) for row in TARGET] in patterns, "PR944 lists the target")
    return words


def paired_obstruction():
    """No word with every operator once per sign meets the integer target."""
    calls = [("B", j, s) for j in range(3) for s in (1, -1)]
    paths = 0
    for order in itertools.permutations(calls):
        q, states = [0, 0, 0], [(0, 0, 0)]
        for _, j, s in order:
            q[j] += s
            states.append(tuple(q))
        differences = {tuple(a - b for a, b in zip(u, v))
                       for u in states for v in states}
        require(not all(row in differences for row in TARGET), "paired path")
        paths += 1
    return paths


def envelope(prices, characteristic):
    sigma = [p + m for p, m in prices]
    if characteristic == 0:
        return sum(sigma) + min(sigma)
    cheap = [characteristic * min(p, m) for p, m in prices]
    base = [min(s, x) for s, x in zip(sigma, cheap)]
    upgrade = [min(2 * s, x) for s, x in zip(sigma, cheap)]
    return sum(base) + min(u - b for u, b in zip(upgrade, base))


def profile_minimum(prices, characteristic):
    """Exact optimum over count profiles, independent of the closed formula."""
    limit = 4 if characteristic == 0 else 2 * characteristic + 2
    options = []
    for p, m in prices:
        feasible = [(a * p + b * m, (a, b))
                    for a in range(limit + 1) for b in range(limit + 1)
                    if a + b >= 2 and normalize(a - b, characteristic) == 0]
        options.append(sorted(feasible)[:3])
    best = None
    for choice in itertools.product(*options):
        if characteristic != 2 and all(pair == (1, 1) for _, pair in choice):
            continue
        bill = sum(cost for cost, _ in choice)
        best = bill if best is None else min(best, bill)
    return best


def construct(prices, characteristic, templates, integer_words):
    """A literal word whose bill equals the closed envelope."""
    sigma = [p + m for p, m in prices]
    if characteristic == 0:
        return integer_words[NAMES[sigma.index(min(sigma))]]
    cheap = [characteristic * min(p, m) for p, m in prices]
    anchors = [k for k in range(6) if cheap[k] <= sigma[k]]
    if not anchors:
        extra = [min(s, x - s) for s, x in zip(sigma, cheap)]
        k = extra.index(min(extra))
        if 2 * sigma[k] <= cheap[k]:
            return integer_words[NAMES[k]]
        anchors = [k]
    k = anchors[0]
    word = expand(templates[NAMES[k]], characteristic)
    if prices[k][1] < prices[k][0]:
        word = flip(word)
    for g in anchors[1:]:
        keep = 1 if prices[g][0] <= prices[g][1] else -1
        word = convert(word, NAMES[g], keep, characteristic)
    return word


def bill(word, prices):
    return sum(a * p + b * m for (a, b), (p, m) in zip(profile(word), prices))


def price_set():
    rng = random.Random(20261020)
    sets = [((Fraction(1), Fraction(1)),) * 6]
    for k in range(6):
        for heavy in (Fraction(2), Fraction(5), Fraction(40)):
            sets.append(tuple((Fraction(1), heavy if j == k else Fraction(1))
                              for j in range(6)))
    sets.append(tuple((Fraction(1), Fraction(100)) for _ in range(6)))
    sets.append(tuple((Fraction(j + 1, 3), Fraction(7, j + 2)) for j in range(6)))
    for _ in range(40):
        sets.append(tuple((Fraction(rng.randint(1, 30), rng.randint(1, 4)),
                           Fraction(rng.randint(1, 30), rng.randint(1, 4)))
                          for _ in range(6)))
    return sets


def price_checks(templates, integer_words):
    cases = 0
    for characteristic in CHARACTERISTICS:
        for prices in price_set():
            value = envelope(prices, characteristic)
            require(profile_minimum(prices, characteristic) == value, "profile optimum")
            word = construct(prices, characteristic, templates, integer_words)
            require(correct(word, characteristic), "constructed word action")
            require(bill(word, prices) == value, "constructed word bill")
            if prices[0][0] == prices[0][1] and len(set(prices)) == 1:
                equal = {0: 14, 2: 12, 3: 13}.get(characteristic, 14)
                require(value == equal, "equal-price call count")
            cases += 1
    return cases


def add(left, right, sign, characteristic):
    return tuple(normalize(a + sign * b, characteristic) for a, b in zip(left, right))


def multiply(matrix, vector, characteristic):
    return tuple(normalize(sum(a * b for a, b in zip(row, vector)), characteristic)
                 for row in matrix)


def dual_matrix(seed):
    # Multiplication by a+b*epsilon is [[a,0],[b,a]], epsilon**2=0.
    matrix = [[0] * 4 for _ in range(4)]
    for i in range(2):
        for j in range(2):
            a = (seed + 2 * i + j) % 3 - 1
            b = (2 * seed + i + 3 * j) % 5 - 2
            matrix[2 * i][2 * j] = a
            matrix[2 * i + 1][2 * j] = b
            matrix[2 * i + 1][2 * j + 1] = a
    return tuple(tuple(row) for row in matrix)


def execute(word, bank, operators, characteristic):
    state = list(bank)
    for kind, index, sign in word:
        source, target = (index, 6) if kind == "B" else (6, 3 + index)
        product = multiply(operators[(kind, index)], state[source], characteristic)
        state[target] = add(state[target], product, sign, characteristic)
    return tuple(state)


def target_bank(bank, operators, characteristic, sign=1):
    state = list(bank)
    for i in range(3):
        for j in range(3):
            bx = multiply(operators[("B", j)], bank[j], characteristic)
            abx = multiply(operators[("A", i)], bx, characteristic)
            state[3 + i] = add(state[3 + i], abx, sign * TARGET[i][j], characteristic)
    return tuple(state)


def dense_checks(templates):
    operators = {(kind, j): dual_matrix(1 + j + 4 * (kind == "A"))
                 for kind in "AB" for j in range(3)}
    a, b = operators[("A", 0)], operators[("B", 0)]
    require(multiply(a, multiply(b, (1, 0, 0, 0), 0), 0) !=
            multiply(b, multiply(a, (1, 0, 0, 0), 0), 0), "noncommuting maps")
    banks = [tuple(tuple(int(4 * role + k == column) for k in range(4))
                   for role in range(7)) for column in range(28)]
    banks += [tuple(tuple((seed + 3 * role + 2 * k) % 7 - 3 for k in range(4))
                    for role in range(7)) for seed in (1, 3)]
    cases = 0
    for characteristic in CHARACTERISTICS[1:]:
        for template in templates.values():
            word = expand(template, characteristic)
            for candidate in (word, flip(word)):
                inverse = flip(tuple(reversed(candidate)))
                for raw in banks:
                    bank = tuple(tuple(normalize(x, characteristic) for x in row)
                                 for row in raw)
                    output = execute(candidate, bank, operators, characteristic)
                    require(output == target_bank(bank, operators, characteristic),
                            "dense action")
                    require(execute(inverse, output, operators, characteristic) == bank,
                            "dirty round trip")
                    cases += 1
    return cases


def negative_checks(templates):
    cases = 0
    for template in templates.values():
        for characteristic in range(3, 10):
            word = expand(template, characteristic)
            for index in range(len(word)):
                require(not correct(word[:index] + word[index + 1:], characteristic),
                        "deleted query")
                cases += 1
            for wrong in (0, characteristic + 1, 2 * characteristic + 1):
                require(not correct(word, wrong), "wrong characteristic")
                cases += 1
    return cases


def receipt():
    inputs = read_inputs()
    integer_words = integer_witnesses(inputs)
    templates, template_cases = template_checks()
    counts = {"template_cases": template_cases,
              "conversion_cases": conversion_checks(templates, integer_words),
              "paired_paths": paired_obstruction(),
              "price_cases": price_checks(templates, integer_words),
              "dense_cases": dense_checks(templates),
              "negative_controls": negative_checks(templates)}
    payload = {path.name: digest(path.read_bytes()) for path in sorted(PACKAGE.iterdir())
               if path.is_file() and path.name != "RESULT.json"}
    return {"schema": "signed-sign-price-envelope/v1", "counts": counts,
            "payload_sha256": payload,
            "input_sha256": {path: digest(data) for path, data in sorted(inputs.items())},
            "status": "PASS_SIGNED_SIGN_PRICE_ENVELOPE"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    result = receipt()
    if args.write_receipt:
        destination = args.write_receipt.resolve()
        require(not destination.is_relative_to(ROOT), "receipt output must be outside checkout")
        with destination.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(result == expected, "generated receipt differs")
    print(result["status"], json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
