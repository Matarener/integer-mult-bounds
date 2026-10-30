"""Check the new interner and its exact frozen-builder adapter.

No predecessor research verifier is run. The original builder is the
comparison implementation for this new engineering result.
Produced by Nick Petalas. Apache-2.0.
"""
import argparse
import hashlib
from itertools import combinations
import json
from pathlib import Path
import subprocess
import statistics
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
CASES = ((4, 3, 3, 2, 1), (6, 3, 3, 1, 0), (6, 3, 3, 1, 1),
         (8, 3, 3, 0, 0), (8, 3, 3, 0, 1), (10, 3, 3, 1, 0),
         (10, 3, 3, 1, 1), (12, 3, 3, 1, 0), (12, 3, 3, 1, 1),
         (8, 1, 3, 0, 1), (8, 3, 1, 1, 1), (8, 2, 2, 0, 1),
         (8, 2, 3, 1, 1), (8, 3, 2, 1, 1))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(raw, expected):
    need(hashlib.sha256(raw).hexdigest() == expected, "source bytes changed")


def check_sources():
    mapping = json.loads((HERE / "SOURCE-MAP.json").read_text())
    need(len(mapping) == 4, "source inventory")
    for row in mapping:
        authenticate((HERE / row["local"]).read_bytes(), row["sha256"])
    exclusion = (HERE / "baseline/exclusion_circuit.py").read_text()
    exclusion = exclusion.replace("import json\n", "import json\nfrom interning import initialize, add\n", 1)
    exclusion = exclusion.replace("        self.lookup={s:i for i,s in enumerate(self.support)}",
                                  "        initialize(self)", 1)
    start = exclusion.index("    def add(self,a,b):")
    stop = exclusion.index("    def total(", start)
    exclusion = exclusion[:start] + "    add = add\n\n" + exclusion[stop:]
    need(exclusion == (HERE / "candidate/exclusion_circuit.py").read_text(),
         "undeclared exclusion adapter change")
    mixed = (HERE / "baseline/mixed_point_circuit.py").read_text()
    mixed = mixed.replace("import heapq\n", "import heapq\nfrom interning import initialize\n", 1)
    mixed = mixed.replace("        self.lookup = {s: i for i, s in enumerate(self.support)}",
                          "        initialize(self)", 1)
    mixed = mixed.replace("        c.lookup = t.lookup",
                          "        c.lookup = t.lookup\n        c.fingerprint = t.fingerprint", 1)
    need(mixed == (HERE / "candidate/mixed_point_circuit.py").read_text(),
         "undeclared mixed-point adapter change")
    return mapping


def compare_call(circuit, a, b, oracle, index, add):
    union = oracle[a] | oracle[b]
    if union not in index:
        index[union] = len(oracle)
        oracle.append(union)
    node = add(circuit, a, b)
    need(node == index[union], "first-decomposition node id changed")
    need(circuit.support[node] == sum(1 << bit for bit in union),
         "full support changed")
    return node


def interner_case(size, bits, initialize, add):
    circuit = SimpleNamespace(support=[0] + [1 << i for i in range(size)],
                              args=[None] * (size + 1))
    initialize(circuit, bits)
    oracle = [frozenset()] + [frozenset((i,)) for i in range(size)]
    index = {value: i for i, value in enumerate(oracle)}
    calls = 0
    for weight in range(2, size + 1):
        for support in combinations(range(size), weight):
            a = index[frozenset(support[:-1])]
            b = index[frozenset((support[-1],))]
            node = compare_call(circuit, a, b, oracle, index, add)
            need(circuit.args[node] == (a, b), "first arguments changed")
            calls += 1
    frozen_args = circuit.args.copy()
    for left in range(1 << size):
        a_set = frozenset(bit for bit in range(size) if left >> bit & 1)
        for right in range(1 << size):
            if left & right:
                continue
            b_set = frozenset(bit for bit in range(size) if right >> bit & 1)
            compare_call(circuit, index[a_set], index[b_set], oracle, index, add)
            calls += 1
    need(circuit.args == frozen_args and len(circuit.support) == 1 << size,
         "equal-support decomposition was replaced")
    for key, bucket in circuit.lookup.items():
        for node in (bucket,) if isinstance(bucket, int) else bucket:
            need(circuit.fingerprint[node] == key, "bucket invariant")
    return calls


def interner_controls(initialize, add):
    circuit = SimpleNamespace(support=[0, 1, 2], args=[None] * 3)
    initialize(circuit, 0)
    need(add(circuit, 1, 2) == 3 and circuit.support[3] == 3,
         "hash-only equality is unsound")
    need(add(circuit, 2, 1) == 3 and circuit.args[3] == (1, 2),
         "first decomposition lost on a collision")
    before = (circuit.support.copy(), circuit.args.copy())
    failures = 0
    for operation in (lambda: add(circuit, 1, 1),
                      lambda: initialize(circuit, -1),
                      lambda: initialize(circuit, 65),
                      lambda: initialize(SimpleNamespace(support=[0, 2, 1])),
                      lambda: initialize(SimpleNamespace(support=[0] * 25002))):
        try:
            operation()
        except ValueError:
            failures += 1
        else:
            raise ValueError("invalid input accepted")
    need(before == (circuit.support, circuit.args), "rejection changed the DAG")
    return failures + 2


def run(variant, case, full=False, factored=False):
    command = [sys.executable, "-I", "-W", "error", "-B"]
    if sys.flags.optimize:
        command.append("-O")
    command += [str(HERE / "run_builder.py"), variant, "--case", *map(str, case)]
    if full:
        command.append("--full")
    if factored:
        command.append("--factored")
    completed = subprocess.run(command, capture_output=True, text=True,
                               timeout=120, check=True)
    need(not completed.stderr, "builder stderr: " + completed.stderr)
    return json.loads(completed.stdout)


def compare_builders(case, full, factored=False):
    baseline = run("baseline", case, full, factored)
    candidate = run("candidate", case, full, factored)
    for key in ("case", "factored", "nodes", "active", "additions", "signature", "errors"):
        need(baseline[key] == candidate[key], "builder mismatch: " + key)
    if full:
        need(baseline["structure"] == candidate["structure"], "DAG bytes differ")
    return {key: baseline[key] for key in ("case", "factored", "nodes", "signature")}


def benchmark_binding():
    report = json.loads((HERE / "BENCHMARK.json").read_text())
    for path, digest in report["source_sha256"].items():
        authenticate((HERE / path).read_bytes(), digest)
    need(report["errors"] == 0 and len(report["samples"]) == 10, "benchmark coverage")
    need([row["variant"] for row in report["samples"]] == ["baseline", "candidate"] * 5,
         "benchmark is not alternating")
    need(len({row["signature"] for row in report["samples"]}) == 1,
         "benchmark structures disagree")
    for row in report["samples"]:
        need(row["nodes"] == 509195 and row["additions"] == 489594,
             "benchmark work was omitted")
        need(row["process_seconds"] >= sum(row[key] for key in
             ("build_seconds", "verify_seconds", "digest_seconds")),
             "inconsistent timed regions")
    for section, metric in (("construction", "build_seconds"),
                            ("complete_process", "process_seconds")):
        for variant in ("baseline", "candidate"):
            values = [row[metric] for row in report["samples"]
                      if row["variant"] == variant]
            need(min(values) > 0, "nonpositive duration")
            need(report[section][variant] == dict(median=statistics.median(values),
                 minimum=min(values), maximum=max(values)), "timing summary changed")
        before = report[section]["baseline"]["median"]
        after = report[section]["candidate"]["median"]
        need(report[section]["speedup"] == before / after and
             report[section]["reduction"] == 1 - after / before, "timing ratio changed")
    return report["samples"][0]["signature"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    mapping = check_sources()
    sys.path.insert(0, str(HERE / "candidate"))
    from interning import initialize, add
    calls = sum(interner_case(size, bits, initialize, add)
                for size in range(2, 9) for bits in (0, 1, 8, 64))
    controls = interner_controls(initialize, add)
    try:
        authenticate(b"changed source", mapping[0]["sha256"])
    except ValueError:
        controls += 1
    else:
        raise ValueError("source corruption accepted")
    builds = [compare_builders(case, True) for case in CASES]
    builds.append(compare_builders((8, 3, 3, 1, 1), True, factored=True))
    builds.append(compare_builders((50, 3, 3, 1, 1), False))
    need(builds[-1]["signature"] == benchmark_binding(), "large benchmark binding")
    result = dict(status="PASS_MIXED_POINT_SUPPORT_INTERNING", source_files=len(mapping),
                  interner_cases=28, exact_union_calls=calls, controls=controls,
                  full_structure_pairs=len(builds) - 1, large_structure_pairs=1,
                  builds=builds, no_new_kappa=True)
    files = [*sorted((HERE / "baseline").glob("*.py")),
             *sorted((HERE / "candidate").glob("*.py")),
             HERE / "verify.py", HERE / "run_builder.py", HERE / "benchmark.py",
             HERE / "BENCHMARK.json", HERE / "SOURCE-MAP.json"]
    result["source_sha256"] = {str(path.relative_to(HERE)):
                              hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in files}
    raw = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.write:
        with args.write.open("x") as stream:
            stream.write(raw)
    else:
        need(json.loads((HERE / "RESULT.json").read_text()) == result,
             "expected result changed")
    print(raw, end="")


if __name__ == "__main__":
    main()
