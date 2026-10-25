#!/usr/bin/env python3
"""Independent inventory of PR5285's recorded search domain, not its pricing.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The tables, plan and generator semantics are credited to Matarener and eumemic.
No predecessor Python module is imported or executed.
"""
import argparse
import ast
from collections import Counter, defaultdict
import csv
import gzip
from hashlib import sha1, sha256
import io
import itertools
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/bit-h8-receiver-census/"
PLAN = "research/e8-bit-p111/data/plan-l3.json"
ROOTS = "research/e8-bit-carrier-skeleton/code/skeleton/e8.py"
PARTITION = "research/e8-bit-carrier-skeleton/data/skeleton/d4part-pairs.json"
P589 = (10, 15, 51, 53, 56, 66, 72, 89, 111)
COLUMN = "receivers_10_15_51_53_56_66_72_89_111"
ASSIGNMENT_SEED = 95


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=ROOT):
    """Check exact bytes and Git blob IDs before reading any predecessor data."""
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    data = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        raw = (root / row["path"]).read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == row["git_blob"], "source Git blob: " + row["path"])
        data[row["path"]] = raw
    return data


def csv_rows(raw, compressed=False):
    if compressed:
        raw = gzip.decompress(raw)
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8"), newline=""))
    need(reader.fieldnames and len(set(reader.fieldnames)) == len(reader.fieldnames),
         "duplicate CSV column")
    rows = list(reader)
    need(rows and all(None not in r and None not in r.values() for r in rows),
         "malformed CSV row")
    return rows


def punctures(text):
    p = tuple(int(x) for x in text.split())
    need(len(p) == 9 and tuple(sorted(set(p))) == p and all(8 <= x < 120 for x in p),
         "invalid puncture key")
    return p


def code(text):
    need(len(text) == 9 and set(text) <= set("123"), "invalid receiver code")
    return tuple(int(x) for x in text)


def default_codes(plan, labels):
    """Normalize the plan's default receiver to its explicit 1/2/3 selection.

    For an eligible puncture p, the two unhosted cells of its four-frame both
    contain p (gen_p3.eligible). They are exactly the two plan rcv keys incident
    to p. gen_p3.build keeps existing receiver bits, setting bit 0 if both are 0.
    This uses the source's eligibility premise, not a new geometry proof.
    """
    entries = [(tuple(c), r) for c, r in plan["rcv"]]
    need(len(entries) == 60 and len(dict(entries)) == 60, "plan receiver inventory")
    for c, r in entries:
        need(len(c) == 2 and tuple(sorted(set(c))) == c and r in c,
             "invalid plan receiver")
    receivers = dict(entries)
    result = {}
    for p in labels:
        cells = sorted(c for c in receivers if p in c)
        need(len(cells) == 2, "eligible puncture needs two incident receiver cells")
        mask = sum(1 << i for i, c in enumerate(cells) if receivers[c] == p)
        result[p] = mask or 1
    return result


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def enumerate_sets(data):
    """Rebuild the source's eligibility/affine rule with integer arithmetic.

    Unlike sets.py, this does not load Geom, numpy or the generator. Read only
    the four binary Hamming generators, then emit positive-leading root lines
    directly, form orthogonal four-frames, and exhaust the 18-choose-9 subsets.
    This verifies the finite declared domain, not a producer or native theorem.
    """
    module = ast.parse(data[ROOTS])
    function = next(n for n in module.body if isinstance(n, ast.FunctionDef)
                    and n.name == "_roots_hamming")
    assignment = next(n for n in function.body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == "g" for t in n.targets))
    generators = ast.literal_eval(assignment.value)
    need(len(generators) == 4 and all(len(g) == 8 and set(g) <= {0, 1} for g in generators),
         "Hamming generator shape")
    lines = [tuple(2 * int(i == j) for j in range(8)) for i in range(8)]
    for coefficients in itertools.product((0, 1), repeat=4):
        support = [i for i in range(8)
                   if sum(c * generators[j][i] for j, c in enumerate(coefficients)) % 2]
        if len(support) != 4:
            continue
        for signs in itertools.product((1, -1), repeat=3):
            row = [0] * 8
            for i, sign in zip(support, (1,) + signs):
                row[i] = sign
            lines.append(tuple(row))
    need(len(lines) == len(set(lines)) == 120, "root-line inventory")

    def dot(a, b):
        return sum(x * y for x, y in zip(lines[a], lines[b]))

    blocks = [[i for i in range(120) if int(h, 16) >> i & 1]
              for h in json.loads(data[PARTITION])]
    need(len(blocks) == 10 and all(len(b) == 12 for b in blocks) and
         sorted(itertools.chain.from_iterable(blocks)) == list(range(120)), "D4 partition")
    frames = [f for block in blocks for f in itertools.combinations(block, 4)
              if all(dot(a, b) == 0 for a, b in itertools.combinations(f, 2))]
    need(len(frames) == 30 and sorted(itertools.chain.from_iterable(frames)) == list(range(120)),
         "orthogonal four-frame partition")
    phi = {p: f for f in frames for p in f}
    plan = json.loads(data[PLAN])
    partner, kline, qhost = (dict(plan[name]) for name in ("partner", "kline", "qhost"))
    need(all(set(mapping) == set(range(120)) for mapping in (partner, kline, qhost)),
         "plan label inventory")
    keeper = {}
    for f in frames:
        local = {}
        for p in f:
            need(partner[p] in f and partner[p] != p and qhost[p] in f and qhost[p] != p,
                 "plan frame membership")
            cell = tuple(x for x in f if x not in (p, partner[p]))
            need(cell not in local, "distinct dual cells")
            local[cell] = kline[p]
        keeper.update(local)
    cells = {c for f in frames for c in itertools.combinations(f, 2)}
    hosted = {tuple(sorted((p, qhost[p]))) for p in range(120)}
    unhosted = cells - hosted
    need(len(hosted) == 120 and unhosted == {tuple(c) for c, _ in plan["rcv"]},
         "plan receiver cells must be exactly unhosted cells")
    eligible = []
    for p in range(8, 120):
        in_frame = [c for c in unhosted if phi[c[0]] == phi[p]]
        dcell = tuple(x for x in phi[p] if x not in (p, partner[p]))
        if len(in_frame) == 2 and all(p in c for c in in_frame) and keeper[dcell] not in (p, qhost[p]):
            eligible.append(p)
    need(len(eligible) == 18, "eligible label inventory")
    need(all(dot(p, b) % 2 == 0 for p in eligible for b in range(120)), "integral half Gram")
    augmented = {p: (1 << 120) | sum(((dot(p, b) // 2) % 2) << b for b in range(120))
                 for p in eligible}
    candidates = list(itertools.combinations(eligible, 9))
    admissible = {p for p in candidates if len({phi[x] for x in p}) == 9
                  and binary_rank(augmented[x] for x in p) == 9}
    return admissible, {"root_lines": 120, "orthogonal_four_frames": 30,
                        "eligible_labels": eligible, "nine_subsets_checked": len(candidates),
                        "admissible_sets": len(admissible)}


def analyze(a, b, c, tuned, plan, assignment_seed=ASSIGNMENT_SEED):
    """Count projected (puncture set, receiver vector) keys; never price a word."""
    sets = [punctures(r["punctured"]) for r in a]
    need(len(sets) == 17478 and len(set(sets)) == len(sets), "stage A unique set inventory")
    need(all(r["status"] == "ok" for r in a), "stage A failed row")
    defaults = default_codes(plan, set(itertools.chain.from_iterable(sets)))
    covered = {p: {tuple(defaults[x] for x in p)} for p in sets}
    by_draw = defaultdict(dict)
    explicit_b = defaultdict(set)
    need(len(b) == 6200, "stage B row count")
    for row in b:
        p = punctures(row["punctured"])
        need(p in covered and row["status"] == "ok", "stage B domain or status")
        draw = int(row["draw"])
        need(draw not in by_draw[p], "duplicate stage B draw")
        if draw == 0:
            need(row["receivers"] == "default", "stage B draw zero is default")
            selection = tuple(defaults[x] for x in p)
        else:
            pairs = [tuple(map(int, item.split(":"))) for item in row["receivers"].split()]
            need(len(pairs) == 9 and tuple(x for x, _ in pairs) == p,
                 "stage B receiver labels")
            selection = tuple(x for _, x in pairs)
            need(set(selection) <= {1, 2, 3}, "stage B receiver alphabet")
            rng = random.Random(1000003 * draw + sum(x << (7 * i) for i, x in enumerate(p)))
            need(selection == tuple(rng.choice((1, 2, 3)) for _ in p),
                 "stage B draw disagrees with retained sampling rule")
            explicit_b[p].add(selection)
        by_draw[p][draw] = selection
        covered[p].add(selection)
    need(len(by_draw) == 200 and P589 in by_draw and
         all(set(draws) == set(range(31)) for draws in by_draw.values()),
         "stage B must contain draws 0..30 on exactly 200 sets")

    c_codes = [code(row[COLUMN]) for row in c]
    universe = set(itertools.product((1, 2, 3), repeat=9))
    need(len(c_codes) == len(universe) and set(c_codes) == universe and
         all(row["status"] == "ok" for row in c), "stage C complete receiver inventory")
    covered[P589].update(c_codes)
    tuned_codes = [code(row[COLUMN]) for row in tuned]
    need(len(tuned_codes) == 52 and len(set(tuned_codes)) == 52 and
         set(tuned_codes) <= set(c_codes), "tuning receiver inventory")

    histogram = Counter(map(len, covered.values()))
    represented = sum(map(len, covered.values()))
    total = len(sets) * len(universe)
    # Choose the seed-indexed A-only set, then change one default coordinate.
    a_only = sorted(set(sets) - set(by_draw))
    p = a_only[assignment_seed % len(a_only)]
    default = tuple(defaults[x] for x in p)
    alternative = list(default)
    index = assignment_seed % len(p)
    alternative[index] = default[index] % 3 + 1
    need(tuple(alternative) not in covered[p], "witness must be absent")
    return {
        "domain": {"puncture_sets_listed": len(sets), "receiver_choices_per_set": len(universe),
                   "projected_pairs": total, "geometry_eligibility": "inherited from PR5285/PR555"},
        "stage_A": {"rows": len(a), "receivers_per_set": "one normalized default"},
        "stage_B": {"rows": len(b), "sets": len(by_draw), "draws_per_set": 31,
                    "explicit_nondefault_draws": 6000,
                    "distinct_explicit_receiver_keys": sum(map(len, explicit_b.values())),
                    "repeated_explicit_keys": 6000 - sum(map(len, explicit_b.values())),
                    "draws_reproduced": 6000},
        "stage_C": {"rows": len(c), "sets": 1, "punctures": list(P589), "complete": True},
        "tuning": {"rows": len(tuned), "distinct_receivers": len(set(tuned_codes)),
                   "sets": 1, "additional_projected_pairs": 0},
        "coverage": {"represented_pairs": represented, "unrepresented_pairs": total - represented,
                     "represented_fraction": f"{represented}/{total}",
                     "sets_by_receiver_count": {str(k): v for k, v in sorted(histogram.items())},
                     "full_joint_coverage": represented == total},
        "missing_key": {"assignment_seed": assignment_seed, "punctures": list(p),
                        "recorded_default": "".join(map(str, default)),
                        "unrepresented_receivers": "".join(map(str, alternative)),
                        "changed_line": p[index], "stage_A_only": True,
                        "interpretation": "Unrepresented generator input, not a successfully built or better word."},
        "scope": "Exact coverage of recorded input keys, projected across NODEOPT efforts. "
                 "No full-family exclusion, word validity, price optimality, tuned optimum or new kappa is established.",
    }


def effort_discrepancy(data):
    driver = ast.parse(data[SOURCE + "producer/run_stageC.py"])
    calls = [n for n in ast.walk(driver) if isinstance(n, ast.Call)
             and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
             and n.func.value.id == "one" and n.func.attr == "evaluate"]
    need(len(calls) == 1 and len(calls[0].args) == 4, "stage C evaluate call shape")
    actual = ast.literal_eval(calls[0].args[3])
    replay = ast.parse(data[SOURCE + "verify.py"])
    spot = next(n for n in replay.body if isinstance(n, ast.FunctionDef) and n.name == "spot_replays")
    picks = [n for n in ast.walk(spot) if isinstance(n, ast.Tuple) and len(n.elts) == 5
             and isinstance(n.elts[0], ast.Constant) and n.elts[0].value == "C"]
    need(len(picks) == 1, "stage C spot replay tuple")
    spot_effort = ast.literal_eval(picks[0].elts[3])
    documentation = data[SOURCE + "producer/README.md"].decode()
    need("receivers of PR589's set, NODEOPT 2000)" in documentation,
         "retained documented stage C effort changed")
    return {"saved_driver_NODEOPT": actual, "documented_NODEOPT": 2000,
            "spot_replay_NODEOPT": spot_effort,
            "resolved_historical_run_effort": None,
            "finding": "Source-description mismatch; not evidence that table prices or spot checks are false."}


def inputs(data):
    tables = [csv_rows(data[SOURCE + f"data/STAGE-{s}.csv.gz"], True) for s in "ABC"]
    return (*tables, csv_rows(data[SOURCE + "data/TUNED.csv"]), json.loads(data[PLAN]))


def report(data):
    result = analyze(*inputs(data))
    admissible, enumeration = enumerate_sets(data)
    a = csv_rows(data[SOURCE + "data/STAGE-A.csv.gz"], True)
    need(admissible == {punctures(row["punctured"]) for row in a},
         "stage A differs from independently enumerated source domain")
    result["domain"]["geometry_eligibility"] = "independently recomputed finite PR555/PR5285 rule"
    result["domain_enumeration"] = enumeration
    result["effort_provenance"] = effort_discrepancy(data)
    result["schema"] = "h8-recorded-census-coverage/v1"
    result["status"] = "PASS_H8_CENSUS_COVERAGE"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="explicitly write a newly derived receipt")
    args = parser.parse_args()
    try:
        result = report(authenticate())
        if args.write_result:
            args.write_result.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        else:
            need(result == json.loads((HERE / "RESULT.json").read_text()), "complete receipt mismatch")
        print(result["status"] + " represented=" + str(result["coverage"]["represented_pairs"])
              + " unrepresented=" + str(result["coverage"]["unrepresented_pairs"])
              + " full_joint_coverage=false no_new_kappa")
        return 0
    except (ValueError, OSError, KeyError, StopIteration) as exc:
        print("FAIL_H8_CENSUS_COVERAGE: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
