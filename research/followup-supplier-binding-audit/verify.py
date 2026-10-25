#!/usr/bin/env python3
"""Replay an authenticated historical checker and prove its missing binding."""

import argparse
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
CERTIFICATE = "research/climbed-48/certificate.json"
CHECKER = "scripts/audit_followup_candidate.py"
RECEIPT = "docs/research/community-followup-arithmetic.json"
HISTORICAL_PASS = "PASS independent PR49 moments, rank mass, seven margins and strict arithmetic"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def historical_sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    result = {}
    for row in manifest["files"]:
        require(row["usage"] == "provenance", "audit sources must remain historical")
        reference = manifest["base_commit"] + ":" + row["path"]
        raw = subprocess.run(
            ["git", "--no-replace-objects", "cat-file", "blob", reference],
            cwd=ROOT, check=True, capture_output=True, timeout=30,
        ).stdout
        blob = subprocess.run(
            ["git", "--no-replace-objects", "rev-parse", "--verify", reference],
            cwd=ROOT, check=True, capture_output=True, text=True, timeout=30,
        ).stdout.strip()
        require(blob == row["git_blob"], "historical blob mismatch: " + row["path"])
        require(sha256(raw).hexdigest() == row["sha256"],
                "historical SHA256 mismatch: " + row["path"])
        result[row["path"]] = raw
    return result


def unit_log_lower(x):
    require(1 <= x <= 2, "unit logarithm domain")
    t = (x - 1) / (x + 1)
    return 2 * sum((t ** (2 * j + 1) / (2 * j + 1) for j in range(24)), Q(0))


def log_lower(x):
    require(x >= 1, "logarithm domain")
    k = 0
    while x > 2:
        x /= 2
        k += 1
    lower = unit_log_lower(x) + k * unit_log_lower(Q(2))
    grid = 10 ** 30
    return Q((lower * grid).__floor__(), grid)


def consumed_moment_lower(data):
    """Positive atanh and exp truncations; the proof and domain are in README."""
    item = data["complex"]
    m, width = item["counts"]["m"], item["counts"]["W"]
    saving = Q(data["assembly"]["parameters"]["a_complex"])
    require(type(m) is int and type(width) is int and m > 0 and width > 0,
            "positive integer denominator domain")
    require(0 < saving < 1, "saving domain")
    total = Q(0)
    for rank, count in item["child_width_multiplicities"]:
        require(type(rank) is int and type(count) is int and 0 < rank < m and count > 0,
                "positive integer child domain")
        z = saving * log_lower(Q(m, rank))
        lower_exp = 1 + z + z*z/2 + z**3/6 + z**4/24
        total += Q(rank * count, m * width) * lower_exp
    return total


def write_candidate(root, data):
    path = root / CERTIFICATE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run():
    sources = historical_sources()
    original = json.loads(sources[CERTIFICATE])
    mutant = deepcopy(original)
    rows = mutant["complex"]["child_width_multiplicities"]
    require(rows[-1] == [756, 516232080], "original mutation target")
    require(mutant["complex"]["saving"] == "717/10000000", "original saving")
    rows[-1][1] += 5
    mutant["complex"]["saving"] = "717/20000000"
    lower = consumed_moment_lower(mutant)
    require(lower > 1 + Q(4, 10**10), "consumed moment must strictly exceed one")

    with TemporaryDirectory(prefix="supplier-binding-") as directory:
        temp = Path(directory)
        fixture = temp / "historical"
        for path in (CHECKER, "scripts/audit_community_candidate.py", CERTIFICATE, RECEIPT):
            target = fixture / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(sources[path])
        env = os.environ.copy()
        env.pop("PYTHONOPTIMIZE", None)
        # Each child imports only newly materialized source, with a private cache.
        env["PYTHONPYCACHEPREFIX"] = str(temp / "bytecode")
        python = [sys.executable, "-B"] + ["-O"] * sys.flags.optimize

        def invoke(arguments, success, diagnostic):
            result = subprocess.run(python + list(map(str, arguments)), cwd=temp,
                                    env=env, capture_output=True, text=True, timeout=30)
            require((result.returncode == 0) == success,
                    "unexpected CLI exit: " + result.stdout + result.stderr)
            require(diagnostic in result.stdout + result.stderr, "missing CLI diagnostic")
            if not success:
                require("PASS" not in result.stdout, "failure emitted PASS")
            return result.returncode

        checker = fixture / CHECKER
        receipt = fixture / RECEIPT
        original_output = temp / "original.json"
        invoke([checker, "--candidate-root", fixture, "--check", receipt,
                "--output", original_output], True, HISTORICAL_PASS)
        require(json.loads(original_output.read_bytes()) == json.loads(sources[RECEIPT]),
                "original receipt changed")
        invoke([PACKAGE / "guard.py", fixture / CERTIFICATE], True,
               "PASS_SUPPLIER_SAVING_BINDING_ONLY")

        candidate = temp / "mutant"
        mutant_path = write_candidate(candidate, mutant)
        mutant_output = temp / "mutant.json"
        invoke([checker, "--candidate-root", candidate, "--output", mutant_output],
               True, HISTORICAL_PASS)
        audit = json.loads(mutant_output.read_bytes())
        declared_upper = Q(audit["moments"]["complex"]["upper"])
        require(declared_upper < 1, "weaker declared moment must contract")
        require(audit["certificate_sha256"] == sha256(mutant_path.read_bytes()).hexdigest(),
                "mutant receipt binding")
        invoke([checker, "--candidate-root", candidate, "--check", receipt],
               False, "receipt mismatch")
        invoke([PACKAGE / "guard.py", mutant_path], False,
               "complex.saving does not match assembly.parameters.a_complex")

        bit_mismatch = deepcopy(original)
        bit_mismatch["assembly"]["parameters"]["a_bit"] = "1/100000"
        bit_path = write_candidate(temp / "bit-mismatch", bit_mismatch)
        invoke([checker, "--candidate-root", bit_path.parents[2]], True, HISTORICAL_PASS)
        invoke([PACKAGE / "guard.py", bit_path], False,
               "bit.saving does not match assembly.parameters.a_bit")

        equivalent = deepcopy(original)
        for name in ("bit", "complex"):
            value = Q(equivalent[name]["saving"])
            equivalent["assembly"]["parameters"]["a_" + name] = (
                f"{value.numerator * 2}/{value.denominator * 2}")
        equivalent_path = write_candidate(temp / "equivalent", equivalent)
        invoke([PACKAGE / "guard.py", equivalent_path], True,
               "PASS_SUPPLIER_SAVING_BINDING_ONLY")

        consistent = deepcopy(mutant)
        consistent["complex"]["saving"] = consistent["assembly"]["parameters"]["a_complex"]
        consistent_path = write_candidate(temp / "consistent", consistent)
        invoke([PACKAGE / "guard.py", consistent_path], True,
               "PASS_SUPPLIER_SAVING_BINDING_ONLY")
        invoke([checker, "--candidate-root", consistent_path.parents[2]], False,
               "complex moment does not contract")

    return {
        "scope": "Historical standalone arithmetic acceptance lacks supplier saving equality; no CI bypass or producer-realizability claim.",
        "original_fixed_receipt": "PASS",
        "mutant_standalone_arithmetic": "PASS",
        "mutant_fixed_receipt": "REJECT receipt mismatch",
        "declared_complex_saving": mutant["complex"]["saving"],
        "assembly_complex_saving": mutant["assembly"]["parameters"]["a_complex"],
        "declared_complex_moment_upper": str(declared_upper),
        "independent_consumed_complex_moment_lower": str(lower),
        "consumed_moment_excess_lower": str(lower - 1),
        "strict_excess_threshold": "1/2500000000",
        "guard_controls": {
            "original": "PASS", "complex_mismatch": "REJECT", "bit_mismatch": "REJECT",
            "equivalent_rationals": "PASS", "consistent_noncontracting": "PASS binding only",
        },
        "consistent_noncontracting_historical_arithmetic": "REJECT complex moment does not contract",
        "bit_mismatch_historical_arithmetic": "PASS",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write the checked deterministic evidence")
    args = parser.parse_args()
    result = run()
    require(result == json.loads((PACKAGE / "EXPECTED.json").read_bytes()),
            "audit evidence differs from EXPECTED.json")
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PASS_FOLLOWUP_SUPPLIER_BINDING_AUDIT_ONLY")


if __name__ == "__main__":
    main()
