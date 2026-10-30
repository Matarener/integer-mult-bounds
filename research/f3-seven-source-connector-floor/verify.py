"""Verify the seven-source unsigned F3 connector floor exclusion.

Default mode: compile both C engines, replay their calibration counts against
CERTIFICATE.json (reduced n <= 6, independent n <= 5; --n7-independent adds
the independent n = 6 count), cross-check the engines and both symmetry
reductions against a pure-Python brute force for n <= 4, check the 405-call
seven-source word cited from PR4232, and run rejection controls.

--n7-shards K,...   replay those reduced-engine shards of the n = 7 census.
--n7-all            replay all 18 reduced-engine shards (about 25 CPU minutes).
--n7-independent    replay all 18 independent-engine shards (about 12.5 minutes
                    wall on 18 cores).  The last two are opt-in.
"""

import argparse
import concurrent.futures
import hashlib
import itertools
import json
import math
import os
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json",
                 "CERTIFICATE.json", "verify.py", "engine/reduced.c",
                 "engine/independent.c")
RESULT_RE = re.compile(r"^RESULT n=(\d+) .*leaves=(\d+) solutions=(\d+)$", re.M)
SOLUTION_RE = re.compile(r"^SOLUTION((?: \d+)+)$", re.M)


def require(cond, message):
    if not cond:
        raise SystemExit("FAIL: " + message)


def compile_engines(workdir):
    binaries = {}
    for name in ("reduced", "independent"):
        out = workdir / name
        subprocess.run(["cc", "-O3", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-o", str(out), str(HERE / "engine" / (name + ".c"))],
                       check=True, capture_output=True, text=True)
        binaries[name] = out
    return binaries


def run_engine(binary, args):
    proc = subprocess.run([str(binary)] + [str(a) for a in args],
                          capture_output=True, text=True, check=True)
    found = RESULT_RE.findall(proc.stdout)
    require(len(found) == 1, f"one RESULT line expected from {binary.name} {args}")
    paths = [tuple(map(int, s.split())) for s in SOLUTION_RE.findall(proc.stdout)]
    return int(found[0][1]), int(found[0][2]), paths


# ---- pure-Python model -------------------------------------------------

def prefix_points(path, n):
    q = [(0,) * n]
    for s in path:
        v = list(q[-1])
        v[s] = (v[s] + 1) % 3
        q.append(tuple(v))
    return q


def served_masks(path, n):
    """Binary masks equal to q_a + q_b + q_c for boundaries a <= b <= c."""
    q = prefix_points(path, n)
    pairs = {tuple((x + y) % 3 for x, y in zip(q[a], q[b]))
             for a, b in itertools.combinations_with_replacement(range(len(q)), 2)}
    served = set()
    for m in range(1, 1 << n):
        bits = [(m >> j) & 1 for j in range(n)]
        if any(tuple((b - x) % 3 for b, x in zip(bits, qc)) in pairs for qc in q):
            served.add(m)
    return served


def all_paths(n):
    """Every arrangement of the multiset {0^3, ..., (n-1)^3}."""
    def rec(prefix, counts):
        if len(prefix) == 3 * n:
            yield tuple(prefix)
            return
        for s in range(n):
            if counts[s] < 3:
                counts[s] += 1
                prefix.append(s)
                yield from rec(prefix, counts)
                prefix.pop()
                counts[s] -= 1
    yield from rec([], [0] * n)


def relabel(path):
    lab = {}
    for s in path:
        lab.setdefault(s, len(lab))
    return tuple(lab[s] for s in path)


def cyclic_gaps(path):
    L = len(path)
    gap = {}
    for s in set(path):
        pos = [i for i, x in enumerate(path) if x == s]
        for k in range(3):
            gap[pos[k]] = (pos[(k + 1) % 3] - pos[k]) % L
    return gap


def reduced_forms(path):
    """Rotations starting at a minimum-gap event, relabelled."""
    gap = cyclic_gaps(path)
    g = min(gap.values())
    return {relabel(path[r:] + path[:r]) for r in gap if gap[r] == g}


# ---- checks --------------------------------------------------------------

def check_calibration(cert, binaries, max_independent):
    for key, rec in cert["calibration"].items():
        n = int(key)
        leaves, sols, _ = run_engine(binaries["reduced"], [n, 1, 0, 1, 0])
        require([leaves, sols] == rec["reduced"], f"reduced engine n={n}: {leaves},{sols}")
        if 2 <= n <= max_independent:
            leaves, sols, _ = run_engine(binaries["independent"], [n, 1, 0])
            require([leaves, sols] == rec["independent"],
                    f"independent engine n={n}: {leaves},{sols}")
    print(f"calibration: reduced n=1..6 and independent n=2..{max_independent} counts match")


def independent_family_size(n):
    """Relabelled paths whose last event differs from the first, in closed form."""
    L = 3 * n
    arrangements = math.factorial(L) // 6 ** n
    same_ends = n * math.factorial(L - 2) // 6 ** (n - 1)
    return (arrangements - same_ends) // math.factorial(n)


def check_independent_sizes(cert):
    for key, rec in cert["calibration"].items():
        if "independent" in rec:
            require(rec["independent"][0] == independent_family_size(int(key)),
                    f"independent family size n={key}")
    require(cert["n7"]["independent"]["total_leaves"] == independent_family_size(7),
            "independent n=7 census size")
    print("independent engine leaf counts equal the closed-form family size for n=2..7")


def check_brute_force(cert, binaries):
    for n in (2, 3, 4):
        paths = list(all_paths(n))
        good = [p for p in paths if len(served_masks(p, n)) == (1 << n) - 1]
        rec = cert["calibration"][str(n)]
        require([len(paths), len(good)] == rec["all_paths"], f"brute force n={n}")
        # Independent engine: relabelled paths whose last event differs from the first.
        canon = {relabel(p) for p in good if p[-1] != p[0]}
        require(len(canon) == rec["independent"][1], f"independent symmetry n={n}")
        # Reduced engine: its solution list must meet every orbit and contain only solutions.
        _, _, red = run_engine(binaries["reduced"], [n, 1, 0, 1, 10 ** 6])
        red = set(red)
        require(len(red) == rec["reduced"][1], f"reduced list n={n}")
        require(all(len(served_masks(p, n)) == (1 << n) - 1 for p in red),
                f"reduced engine reports a non-solution at n={n}")
        require(all(reduced_forms(p) & red for p in good),
                f"a solution orbit is missing from the reduced census at n={n}")
        print(f"brute force n={n}: {len(paths)} paths, {len(good)} solutions; "
              "both reductions meet every solution orbit")


def check_seven_upper(cert):
    w = cert["seven_source_upper_from_pr4232"]
    path, n = w["path"], 7
    require(sorted(path) == sorted(list(range(n)) * 3), "seven-source path counts")
    served = served_masks(path, n)
    require(served == set(range(1, 127)), "PR4232 path serves masks 1..126")
    q = prefix_points(path, n)
    total = [sum(q[b][j] for b in w["six_readout_boundaries"]) % 3 for j in range(n)]
    require(total == [1] * n, "six readouts serve mask 127")
    calls = len(path) + 3 * 126 + 6
    require(calls == w["calls"] == 405, "405 calls")
    require(3 * (n + 2 ** n - 1) == 402, "floor 402")
    print("seven-source 405-call word from PR4232: masks 1..126 by triples, 127 by six readouts")


def check_controls(binaries):
    # A floor path at n = 6 is found (positive control); a sorted path fails.
    _, sols, paths = run_engine(binaries["reduced"], [6, 1, 0, 1, 1])
    require(sols > 0 and len(served_masks(paths[0], 6)) == 63, "n=6 positive control")
    require(len(served_masks(tuple(s for s in range(6) for _ in range(3)), 6)) < 63,
            "sorted six-source path must fail")
    # Shards partition the census: n = 6 reduced leaves add up over 7 shards.
    whole, _, _ = run_engine(binaries["reduced"], [6, 1, 0, 1, 0])
    parts = sum(run_engine(binaries["reduced"], [6, 7, k, 1, 0])[0] for k in range(7))
    require(parts == whole, "shard partition control")
    print("controls rejected/accepted as expected; shards partition n=6")


def run_n7(cert, binaries, engine, shards):
    rec = cert["n7"][engine]
    nshards = rec["shards"]
    args = {k: ([7, nshards, k, 1, 0] if engine == "reduced" else [7, nshards, k])
            for k in shards}
    workers = max(1, min(len(shards), os.cpu_count() or 1))
    with concurrent.futures.ThreadPoolExecutor(workers) as pool:
        results = dict(zip(shards, pool.map(lambda k: run_engine(binaries[engine], args[k]),
                                            shards)))
    for k in shards:
        leaves, sols, _ = results[k]
        require(sols == 0, f"{engine} shard {k} found a floor path")
        require(leaves == rec["leaves"][k], f"{engine} shard {k} leaves {leaves}")
    print(f"n=7 {engine} shards {shards}: 0 floor paths, leaf counts match")
    if sorted(shards) == list(range(nshards)):
        require(sum(rec["leaves"]) == rec["total_leaves"], "total leaves")
        print(f"n=7 {engine} census complete: {rec['total_leaves']} paths, none attains 402")


def receipt():
    h = hashlib.sha256()
    for name in PACKAGE_FILES:
        data = (HERE / name).read_bytes()
        h.update(name.encode() + b"\0" + hashlib.sha256(data).hexdigest().encode() + b"\n")
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n7-shards", default="")
    ap.add_argument("--n7-all", action="store_true")
    ap.add_argument("--n7-independent", action="store_true")
    opts = ap.parse_args()
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        binaries = compile_engines(pathlib.Path(tmp))
        if opts.n7_shards:
            run_n7(cert, binaries, "reduced", [int(k) for k in opts.n7_shards.split(",")])
            marker = "PASS_F3_SEVEN_SOURCE_SHARDS"
        elif opts.n7_all or opts.n7_independent:
            if opts.n7_all:
                run_n7(cert, binaries, "reduced", list(range(cert["n7"]["reduced"]["shards"])))
            if opts.n7_independent:
                check_calibration(cert, binaries, 6)
                run_n7(cert, binaries, "independent",
                       list(range(cert["n7"]["independent"]["shards"])))
            marker = "PASS_F3_SEVEN_SOURCE_CENSUS"
        else:
            check_calibration(cert, binaries, 5)
            check_brute_force(cert, binaries)
            check_independent_sizes(cert)
            check_seven_upper(cert)
            check_controls(binaries)
            marker = "PASS_F3_SEVEN_SOURCE_CALIBRATION"
    print("receipt_sha256", receipt())
    print(marker)


if __name__ == "__main__":
    sys.exit(main())
