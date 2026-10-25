#!/usr/bin/env python3
"""Hint-free forward RUP check of #4331's GL3 refutations, including the length-eight one.

rupcheck.c / rupcheck.py check every proof addition by reverse unit propagation against the CNF and
the earlier additions, ignoring deletions (sound: every stored clause is entailed), and require the
empty clause. No LRAT hints, no drat-trim, no solver. This file:
  1. checks the vendored length-7 CNF and proof against #4331's pins and replays them with rupcheck.py;
  2. runs two semantic controls on length 7 (a dropped core clause, a flipped literal);
  3. fuzzes rupcheck.py against brute-force satisfiability on small formulas;
  4. checks the recorded rupcheck.c runs (local evidence) for lengths 7 and 8: bound to this
     rupcheck.c and to the length-8 inputs' SHA256 pins in #4331's CERTIFICATES.json.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import gzip
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rupcheck  # noqa: E402

VENDORED = {
    "vendor/length7.cnf": "2f1b925d8cc84ce36f35ac8033d6e4afffe373a2ab37fe5f52d6e29884c1ed0c",
    "vendor/length7.rup.gz": "63bbaaf387740a52ba0874b0766bac682f52d41a4b26ea0e16e030dd3a7b0eec",
    "vendor/CERTIFICATES.json": "f5bc7526ca29724a89ea3126cdf4b3780774c3f15a0328f3f91b227c7ad16042",
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def brute_sat(n, cls):
    return any(all(any((a >> (abs(l) - 1) & 1) == (l > 0) for l in c) for c in cls) for a in range(1 << n))


def fuzz(seed, trials):
    rng, sat_rej, tree_ok = random.Random(seed), 0, 0
    for _ in range(trials):
        n = rng.randint(3, 6)
        cls = [[v * rng.choice((1, -1)) for v in rng.sample(range(1, n + 1), 3)] for _ in range(rng.randint(6, 40))]
        cnf = [f"p cnf {n} {len(cls)}"] + [" ".join(map(str, c)) + " 0" for c in cls]
        proof = [(("d " if rng.random() < 0.1 else "") + " ".join(str(v * rng.choice((1, -1))) for v in rng.sample(range(1, n + 1), rng.randint(0, n))) + " 0")
                 for _ in range(rng.randint(0, 10))] + ["0"]
        if brute_sat(n, cls):
            need(rupcheck.check(cnf, proof)["status"] != "RUP_REFUTATION_VERIFIED", "a satisfiable formula was refuted")
            sat_rej += 1
        else:
            tree = [" ".join(str(v if s >> (v - 1) & 1 else -v) for v in range(1, d + 1)) + " 0"
                    for d in range(n, -1, -1) for s in range(1 << d)]
            need(rupcheck.check(cnf, tree)["status"] == "RUP_REFUTATION_VERIFIED", "a valid tree refutation was rejected")
            tree_ok += 1
    return sat_rej, tree_ok


def main():
    for rel, digest in VENDORED.items():
        need(sha((HERE / rel).read_bytes()) == digest, f"vendored {rel}")
    certs = {c["length"]: c for c in json.loads((HERE / "vendor/CERTIFICATES.json").read_text())["certificates"]}
    cnf7 = (HERE / "vendor/length7.cnf").read_text().splitlines()
    rup7 = gzip.decompress((HERE / "vendor/length7.rup.gz").read_bytes())
    need(sha((HERE / "vendor/length7.cnf").read_bytes()) == certs[7]["cnf_sha256"], "length-7 CNF is #4331's")
    need(sha(rup7) == certs[7]["proof_sha256"], "length-7 proof is #4331's")
    rup7 = rup7.decode().splitlines()

    # 1. replay length 7 in Python
    r7 = rupcheck.check(cnf7, rup7)
    need(r7 == {"status": "RUP_REFUTATION_VERIFIED", "formula_clauses": 61138, "additions_checked": 11728,
                "deletions_ignored": 27449}, f"length 7 replay: {r7}")

    # 2. controls: dropping core clause 100, or flipping the first literal of the first addition, is rejected
    body = [i for i, line in enumerate(cnf7) if line and line[0] not in "cp"]
    dropped = [line for i, line in enumerate(cnf7) if i != body[99]]
    need(rupcheck.check(dropped, rup7) == {"status": "REJECTED", "failed_addition": 136}, "control: dropped core clause")
    first = next(i for i, line in enumerate(rup7) if line and not line.startswith("d"))
    toks = rup7[first].split()
    flipped = rup7[:first] + [" ".join([str(-int(toks[0]))] + toks[1:])] + rup7[first + 1:]
    need(rupcheck.check(cnf7, flipped)["status"] == "REJECTED", "control: flipped literal")

    # 3. soundness and completeness fuzz against brute force
    sat_rej, tree_ok = fuzz(4331, 400)
    need(sat_rej > 100 and tree_ok > 100, "fuzz covered both outcomes")

    # 4. recorded rupcheck.c runs
    text = (HERE / "evidence/RUP-RUNS.txt").read_text()
    need(f"rupcheck.c (SHA256 {sha((HERE / 'rupcheck.c').read_bytes())})" in text, "runs recorded for this rupcheck.c")
    lines = text.splitlines()
    for L in (7, 8):
        need(f"input length{L}.cnf sha256 {certs[L]['cnf_sha256']}" in lines, f"length {L} CNF pin")
        need(f"input length{L}.rup sha256 {certs[L]['proof_sha256']}" in lines, f"length {L} proof pin")
    res = {L: json.loads(next(l for l in lines if l.startswith(f"result length{L} ")).split(" ", 2)[2]) for L in (7, 8)}
    need(res[7]["status"] == "RUP_REFUTATION_VERIFIED" and res[7]["additions_checked"] == 11728, "C length 7 agrees with Python")
    need(res[8]["status"] == "RUP_REFUTATION_VERIFIED" and res[8]["variables"] == certs[8]["variables"]
         and res[8]["formula_clauses"] == certs[8]["clauses"], "C length 8 verified on #4331's formula")
    need(res[8]["additions_checked"] + res[8]["deletions_ignored"] == certs[8]["proof_lines"], "every length-8 proof line accounted for")
    need(res[8]["empty_clause_at_addition"] == res[8]["additions_checked"], "length 8 ends at the empty clause")

    print(json.dumps({
        "status": "PASS_GL3_LENGTH8_RUP_CHECK",
        "length7_python": r7,
        "length8_c": res[8],
        "fuzz": {"satisfiable_rejected": sat_rej, "tree_refutations_accepted": tree_ok},
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
