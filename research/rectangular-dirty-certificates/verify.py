"""Finite corroboration of the typed closure and path-witness theorem."""

from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_certificate import check
from typed_words import decide, require, validate, witness


def expanded(problem, side):
    """Independent literal path expansion, used only for small fixtures."""
    registers = [{(i, ()): Fraction(1)} for i in range(len(problem["roles"]))]
    for ins in problem[side]:
        op, d = ins["op"], ins["dst"]
        if op == "swap":
            s = ins["src"]
            registers[s], registers[d] = registers[d], registers[s]
            continue
        if op == "scale":
            registers[d] = {k: Fraction(ins["c"]) * v for k, v in registers[d].items() if v}
            continue
        s = ins.get("src", d)
        source = registers[s].copy()
        if op in ("query", "apply"):
            source = {(i, (ins["arrow"],) + w): c for (i, w), c in source.items()}
        if op == "apply":
            registers[d] = source
            continue
        for k, v in source.items():
            registers[d][k] = registers[d].get(k, 0) + Fraction(ins["c"]) * v
        registers[d] = {k: v for k, v in registers[d].items() if v}
    return [{k: v for k, v in row.items() if v} for row in registers]


def residual(problem):
    result = []
    for left, right in zip(expanded(problem, "left"), expanded(problem, "right"), strict=True):
        row = {k: left.get(k, 0) - right.get(k, 0) for k in left.keys() | right.keys()}
        result.append({k: v for k, v in row.items() if v})
    return result


def execute(problem, side, matrices, initial):
    """Literal rectangular matrix execution, independent of dependency states."""
    values = [row[:] for row in initial]
    for ins in problem[side]:
        op, d = ins["op"], ins["dst"]
        if op == "swap":
            s = ins["src"]
            values[s], values[d] = values[d], values[s]
            continue
        if op == "scale":
            values[d] = [Fraction(ins["c"]) * v for v in values[d]]
            continue
        source = values[ins.get("src", d)][:]
        if op in ("query", "apply"):
            source = [sum(a * b for a, b in zip(row, source, strict=True))
                      for row in matrices[ins["arrow"]]]
        if op == "apply":
            values[d] = source
        else:
            values[d] = [a + Fraction(ins["c"]) * b for a, b in zip(values[d], source, strict=True)]
    return values


def literal_witness(problem, certificate):
    concrete = witness(problem, certificate)
    initial = [[0] * concrete["dimensions"][t] for t in problem["roles"]]
    initial[certificate["input"]][concrete["input_coordinate"]] = 1
    left = execute(problem, "left", concrete["matrices"], initial)
    right = execute(problem, "right", concrete["matrices"], initial)
    o, j = certificate["output"], concrete["output_coordinate"]
    require(left[o][j] - right[o][j] == Fraction(certificate["coefficient"]), "literal witness failed")
    require(sum(concrete["dimensions"].values()) == len(certificate["word"]) + 1, "visit-count bound")
    return concrete


def query(src, dst, arrow, c=1):
    return {"op": "query", "src": src, "dst": dst, "arrow": arrow, "c": c}


def echo_problem():
    return {"roles": ["A", "B", "C"], "arrows": {"P": ["A", "B"], "Q": ["B", "C"]},
            "left": [query(0, 1, "P"), query(1, 2, "Q"), query(0, 1, "P", -1), query(1, 2, "Q", -1)],
            "right": [query(1, 2, "Q", -1), query(0, 1, "P"), query(1, 2, "Q"), query(0, 1, "P", -1)]}


def random_problem(rng, index):
    roles = ["A", "B", "A", "C"]
    arrows = {f"{s}{t}": [s, t] for s in ("A", "B", "C") for t in ("A", "B", "C")}
    left = []
    for _ in range(9):
        s, d = rng.randrange(4), rng.randrange(4)
        op = rng.randrange(5)
        c = rng.choice(["1/2", "-3/2", -1, 0, 1, 2])
        if op == 0:
            left.append({"op": "scale", "dst": d, "c": c})
        elif op == 1:
            left.append({"op": "apply", "dst": d, "arrow": roles[d] * 2})
        elif op == 2 and roles[s] == roles[d]:
            left.append({"op": "swap", "src": s, "dst": d})
        elif op == 3 and roles[s] == roles[d]:
            left.append({"op": "add", "src": s, "dst": d, "c": c})
        else:
            left.append(query(s, d, roles[s] + roles[d], c))
    right = deepcopy(left)
    if index % 2:
        right.append(query(0, 1, "AB", rng.choice([-1, "1/2", 2])))
    else:
        right += [query(1, 3, "BC"), query(1, 3, "BC", -1)]
    return {"roles": roles, "arrows": arrows, "left": left, "right": right}


def chain_problem(length):
    """Iterative dirty commutator construction; no recursive Python calls."""
    roles = ["A" if j % 2 == 0 else "B" for j in range(length + 1)]
    arrows = {f"a{j}": [roles[j], roles[j + 1]] for j in range(length)}
    word = [query(length - 1, length, f"a{length - 1}")]
    for j in range(length - 2, -1, -1):
        inverse = [{**ins, "c": -ins["c"]} for ins in reversed(word)]
        word = [query(j, j + 1, f"a{j}")] + word + [query(j, j + 1, f"a{j}", -1)] + inverse
    return {"roles": roles, "arrows": arrows, "left": word, "right": []}


def verify_differentials():
    rng = random.Random(780231)
    counts = {"program_pairs": 0, "equal": 0, "different": 0, "literal_witnesses": 0}
    for i in range(160):
        problem = random_problem(rng, i)
        expected = residual(problem)
        certificate = decide(problem)
        check(problem, certificate)
        require(certificate["equal"] == (not any(expected)), "explicit-word verdict disagrees")
        counts["program_pairs"] += 1
        if certificate["equal"]:
            counts["equal"] += 1
        else:
            counts["different"] += 1
            o, s, w = certificate["output"], certificate["input"], tuple(certificate["word"])
            require(expected[o][s, w] == Fraction(certificate["coefficient"]), "coefficient disagreement")
            require(len(w) == min(len(k[1]) for row in expected for k in row), "not shortest")
            literal_witness(problem, certificate)
            counts["literal_witnesses"] += 1
    return counts


def verify_echo():
    problem = echo_problem()
    certificate = decide(problem)
    result = check(problem, certificate)
    require(certificate["equal"], "rectangular echo mismatch")
    rng = random.Random(91)
    cases = 0
    for a in range(4):
        for b in range(4):
            for c in range(4):
                dims = {"A": a, "B": b, "C": c}
                matrices = {k: [[rng.randrange(-2, 3) for _ in range(dims[s])]
                                for _ in range(dims[t])] for k, (s, t) in problem["arrows"].items()}
                width = sum(dims[t] for t in problem["roles"])
                for axis in range(width + 1):
                    initial = [[0] * dims[t] for t in problem["roles"]]
                    flat = [(r, j) for r, t in enumerate(problem["roles"]) for j in range(dims[t])]
                    if axis < width:
                        r, j = flat[axis]
                        initial[r][j] = 1
                    require(execute(problem, "left", matrices, initial) ==
                            execute(problem, "right", matrices, initial), "unequal-space echo")
                    cases += 1
    return {**result, "dimension_vectors": 64, "full_column_or_zero_tests": cases}, certificate


def must_reject(callback):
    try:
        callback()
    except (ValueError, TypeError, KeyError, ZeroDivisionError):
        return
    raise ValueError("invalid control accepted")


def verify_controls(certificate):
    controls = []
    for name in ("arrow-type", "cross-type-add", "bad-index", "float", "zero-denominator", "unknown-op"):
        p = echo_problem()
        if name == "arrow-type": p["left"][0]["arrow"] = "Q"
        if name == "cross-type-add": p["left"][0] = {"op": "add", "src": 0, "dst": 1, "c": 1}
        if name == "bad-index": p["left"][0]["src"] = True
        if name == "float": p["left"][0]["c"] = 0.5
        if name == "zero-denominator": p["left"][0]["c"] = "1/0"
        if name == "unknown-op": p["left"][0]["op"] = "erase"
        must_reject(lambda: validate(p))
        controls.append(name)
    for name in ("initial", "closure", "basis", "missing-arrow", "nonboolean"):
        bad = deepcopy(certificate)
        if name == "initial": bad["initial"][0][0] = str(Fraction(bad["initial"][0][0]) + 1)
        if name == "closure": bad["closure"]["P"][0][0] = str(Fraction(bad["closure"]["P"][0][0]) + 1)
        if name == "basis": bad["basis"][0]["word"] = ["P", "Q"]
        if name == "missing-arrow": del bad["closure"]["P"]
        if name == "nonboolean": bad["equal"] = 1
        must_reject(lambda: check(echo_problem(), bad))
        controls.append(name)
    for event in (0, 2, 3):
        p = echo_problem()
        del p["left"][event]
        c = decide(p)
        require(not c["equal"], "missing restoration/sign not detected")
        check(p, c)
        literal_witness(p, c)
        controls.append(f"deleted-event-{event}")
    return controls


def main():
    root = Path(__file__).resolve().parent
    sources = json.loads((root / "SOURCES.json").read_text())
    repo = root.parent.parent
    for item in sources["files"]:
        if item["usage"] == "input":
            require(hashlib.sha256((repo / item["path"]).read_bytes()).hexdigest() == item["sha256"],
                    f"source bytes changed: {item['path']}")
    differentials = verify_differentials()
    echo, certificate = verify_echo()
    controls = verify_controls(certificate)
    chains = []
    for length in range(1, 7):
        p = chain_problem(length)
        c = decide(p)
        require(not c["equal"] and len(c["word"]) == length, "chain degree")
        check(p, c)
        w = literal_witness(p, c)
        require(not any(residual(p)[:-1]), "chain lost dirty input")
        chains.append({"length": length, "instructions": len(p["left"]),
                       "dimensions": w["dimensions"], "coefficient": c["coefficient"]})
    for name, expected in (("echo", echo_problem()), ("chain6", chain_problem(6))):
        problem = json.loads((root / f"{name}.json").read_text())
        saved = json.loads((root / f"{name}.certificate.json").read_text())
        require(problem == expected and saved == decide(problem), "committed example mismatch")
        check(problem, saved)
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(root.iterdir()) if p.is_file()}
    print(json.dumps({"status": "PASS_RECTANGULAR_DIRTY_CERTIFICATES", "differentials": differentials,
                      "echo": echo, "chain_witnesses": chains, "controls": controls,
                      "source_hashes": files}, sort_keys=True))


if __name__ == "__main__":
    main()
