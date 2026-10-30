"""Exact source supports and a fixed restriction price.

Source: PR5827 and its retained P104 authors.
New work: Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
KAPPA = Q(".003124767")
LARGE_TARGET = Q(".00312476680") * Q(101, 100)
SCALE = 10**12


def need(ok, message):
    if not ok:
        raise ValueError(message)


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def source():
    pins = json.loads((HERE / "INPUTS.json").read_text())
    for name, pin in pins["files"].items():
        data = (HERE / "inputs" / name).read_bytes()
        need(sha256(data).hexdigest() == pin["sha256"], "Source digest")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(sha1(blob).hexdigest() == pin["git_blob"], "Source Git blob")
    return json.loads(gzip.decompress((HERE / "inputs/WORD.json.gz").read_bytes()))


def supports(word):
    public = word["public"]
    size = public + word["owned_fields"]
    ports = set(word["live"])
    main = ports | {r + 112 for r in ports}
    groups = [[r, r + 112] for r in sorted(ports)]
    groups += [[r] for r in range(public) if r not in main]
    owner = {r: i for i, group in enumerate(groups) for r in group}
    dims = list(map(len, word["frames"]))
    coefficients = {e[-2]: Q(e[-2]) for e in word["program"]
                    if e[0] in ("ADD", "COPY", "SCALE")}

    def add(dst, src, scale):
        for j, value in src.items():
            value = dst.get(j, Q(0)) + scale * value
            if value:
                dst[j] = value
            else:
                dst.pop(j, None)

    def apply(rows, event, reverse):
        op, r = event[:2]
        if op == "MOVE":
            return
        if op in ("INIT", "CLEAR"):
            rows[r] = {}
        elif op == "SCALE":
            rows[r] = {j: coefficients[event[-2]] * v
                       for j, v in rows[r].items()}
        elif reverse:
            need(op in ("ADD", "COPY"), "Scalar opcode")
            add(rows[event[2]], rows[r], coefficients[event[-2]])
            if op == "COPY":
                rows[r] = {}
        else:
            need(op in ("ADD", "COPY"), "Scalar opcode")
            if op == "COPY":
                rows[r] = {}
            add(rows[r], rows[event[2]], coefficients[event[-2]])

    def mask(row):
        return sum(1 << j for j in {owner[r] for r in row})

    rows = [{r: Q(1)} for r in range(size)]
    queries = {}
    for i, e in enumerate(word["program"]):
        if e[0] == "MOVE":
            queries[i] = {"event": i, "role": e[1],
                          "rank": abs(dims[e[3]] - dims[e[2]]),
                          "input": mask(rows[e[1]])}
        apply(rows, e, False)
    for r, row in enumerate(rows):
        expected = {r: Q(1)} if r < public else {}
        if r - 112 in ports:
            expected[r - 112] = Q(1)
        need(row == expected, "Complete forward endpoint")
    rows = [{r: Q(1)} if r < public else {} for r in range(size)]
    for i in range(len(word["program"]) - 1, -1, -1):
        e = word["program"][i]
        if e[0] == "MOVE":
            queries[i]["output"] = mask(rows[e[1]])
        apply(rows, e, True)
    for r, row in enumerate(rows):
        expected = {r: Q(1)} if r < public else {}
        if r in ports:
            expected[r + 112] = Q(1)
        need(row == expected, "Complete transpose endpoint")
    need(len(groups) == 666 and len(ports) == 104, "Source group census")
    need(len(queries) == 3455, "Source query census")
    return groups, list(queries.values())


def log_bounds(value):
    exponent = value.bit_length() - 1

    def series(z):
        power, total = z, Q(0)
        for j in range(32):
            total += 2 * power / (2*j + 1)
            power *= z*z
        return total, total + 2*power / (65*(1-z*z))

    a, b = series(Q(1, 3))
    u = Q(value, 2**exponent)
    c, d = series((u-1)/(u+1))
    return exponent*a+c, exponent*b+d


def power_bounds(rank, kappa=KAPPA):
    if rank == 1:
        return Q(1), Q(1)
    lower, upper = log_bounds(rank)

    def partial(x, degree):
        need(0 <= x < 1, "Alternating exponential domain")
        term = total = Q(1)
        for j in range(1, degree+1):
            term *= -x/j
            total += term
        return total

    return rank*partial(kappa*upper, 13), rank*partial(kappa*lower, 14)


def invoice(word, groups, queries, kappa=KAPPA):
    dims = list(map(len, word["frames"]))
    local_paid = Counter(q["rank"] for q in queries)
    local_targets = Counter(dims[word["final"][g[0]]] - dims[word["initial"][g[0]]]
                            for g in groups if len(g) == 1)
    source_result = json.loads((HERE / "inputs/PR5827-RESULT.json").read_text())
    need(local_paid == Counter({int(k): v for k, v in source_result["local"]["paid"].items()}),
         "Source local paid invoice")
    need(local_targets == Counter({int(k): v for k, v in source_result["local"]["helpers"].items()}),
         "Source local target invoice")
    paid = Counter({r: 18*n for r, n in local_paid.items()})
    targets = Counter({r: 18*n for r, n in local_targets.items()})
    paid[1] += 15*104
    targets[145] += 2*104
    for length in (7, 8):
        for j in range(1, length+1):
            paid[8*(j+1)] += 2*104
            targets[1+8*(j+1)] += 2*104
    for key, actual in (("paid", paid), ("targets", targets)):
        expected = Counter({int(k): v for k, v in source_result["complete_cost"][key].items()})
        need(actual == expected, "Complete source " + key)
    ranks = set(range(1, 10)) | {145}
    ranks |= {8*(j+1)+s for length in (7, 8)
              for j in range(1, length+1) for s in (0, 1)}
    powers = {r: power_bounds(r, kappa) for r in ranks}
    main = (2*powers[145][1] + 2*sum(
        powers[1+8*(j+1)][1] - powers[8*(j+1)][0]
        for length in (7, 8) for j in range(1, length+1)) - 15) / 18

    def ceil(q):
        return -((-q.numerator)//q.denominator)

    costs = []
    for group in groups:
        rank = dims[word["final"][group[0]]] - dims[word["initial"][group[0]]]
        value = main if len(group) == 2 else powers[rank][1]
        costs.append(ceil(SCALE*value))
    rewards = [(SCALE*powers[q["rank"]][0]).numerator //
               (SCALE*powers[q["rank"]][0]).denominator for q in queries]
    need(all(x > 0 for x in costs + rewards), "Positive tariff")
    return costs, rewards, sum(costs)-sum(rewards)


def relaxation(queries, rewards, yes, no):
    terms = Counter()
    for q, reward in zip(queries, rewards):
        a, b = q["input"], q["output"]
        left, right = not a & no, not b & no
        if not left and not right:
            continue
        required = (a & b) if left and right else (a if left else b)
        terms[required & ~yes] += reward
    return [(key, terms[key]) for key in sorted(terms)]
