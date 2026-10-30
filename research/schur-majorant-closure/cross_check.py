"""Authenticated algorithm-agreement integration, not another oracle.

Compare primary Gaussian elimination with the already-frozen independent
bordered-determinant oracle on its exact original census and partitions.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys
import types

P = Path(__file__).resolve().parent
PRIMARY_SHA = "c5c9de309ae227eae0c9cead43b7bb0ec724e5d7b80cc68fddb3c80d1bf1c040"
ORACLE_SHA = "716bb5e5c7ffb0d2ef44951a13fec49bb875a138e07503de8b6e652276e1f8ab"
ORACLE_ENDPOINT_DIGEST = "5b774faf86a7bd5a9070aaa0710f3437f0e7861954780c8984d78aab0023591d"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path, expected):
    data = path.read_bytes()
    need(sha256(data).hexdigest() == expected, "authenticated integration input: " + name)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(data, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module


def as_primary(matrix):
    return [[(value.real, value.imag) for value in row] for row in matrix]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-path", type=Path, default=P/"primary_verify.py")
    parser.add_argument("--oracle-path", type=Path, default=P/"independent_oracle.py")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    primary = load("schur_cross_primary", args.primary_path, PRIMARY_SHA)
    oracle = load("schur_cross_oracle", args.oracle_path, ORACLE_SHA)
    matrices = partitions = 0
    families = {}
    digest = sha256()
    for label, h, p, rho, kind in oracle.matrix_cases():
        oracle.validate_input(h, p, rho, kind)
        original = oracle.identity_plus(h)
        matrix = as_primary(original)
        n = len(matrix)
        for assignment in product((0, 1, 2), repeat=n):
            eliminated = tuple(i for i, state in enumerate(assignment) if state == 0)
            retained = tuple(i for i, state in enumerate(assignment) if state == 1)
            if not retained:
                continue
            expected = oracle.check_partition(h, p, rho, kind, eliminated, retained)
            actual = primary.schur(matrix, eliminated, retained)
            need(actual == as_primary(expected), "Gaussian-elimination/bordered-determinant exact disagreement")
            digest.update(repr((label, eliminated, retained, expected)).encode())
            partitions += 1
        family = "all_2x2" if label.startswith("all_2x2") else label.rsplit("_", 1)[0]
        families[family] = families.get(family, 0)+1
        matrices += 1
    need(matrices == 2441 and partitions == 13501, "frozen independent census coverage")
    need(digest.hexdigest() == ORACLE_ENDPOINT_DIGEST, "frozen oracle endpoint census digest")
    # The wrong sign still meets a norm bound, but fails the exact
    # block-of-inverse identity: success must not mean merely norm success.
    matrix = [[primary.ONE, primary.z(Q(1, 4))], [primary.z(Q(1, 4)), primary.ONE]]
    proper = primary.schur(matrix, (0,), (1,))
    wrong = [[primary.z(Q(17, 16))]]
    inverse_block = primary.inverse(matrix)[1][1]
    need(primary.inverse(proper)[0][0] == inverse_block
         and primary.inverse(wrong)[0][0] != inverse_block,
         "wrong-sign exact identity control")
    need(max(primary.norms(primary.minus(wrong, primary.identity(1)))) <= Q(1, 2),
         "wrong sign norm-only positive control")
    result = {"status": "PASS_SCHUR_ALGORITHM_AGREEMENT_INTEGRATION_NO_NEW_KAPPA",
              "input_sha256": {"primary_verify.py": PRIMARY_SHA, "independent_oracle.py": ORACLE_SHA},
              "matrices": matrices, "principal_E_K_D_partitions": partitions,
              "families": families, "endpoint_digest": digest.hexdigest(),
              "oracle_invariants_checked_on_every_partition": True,
              "wrong_sign_control": {"inverse_identity_rejected": True, "norm_bound_still_holds": True},
              "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "scope": "Exact agreement of existing primary Gaussian elimination and frozen independent bordered-minor oracle, including modulus-only oracle fixtures. Reusing their code is integration, not a third independent oracle or a universal proof. No source gate compiler, precision or physical program executed."}
    if args.output is not None:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"])


if __name__ == "__main__":
    main()
