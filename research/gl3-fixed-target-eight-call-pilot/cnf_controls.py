"""Validate the independent CNF encoder before proof-producing target runs."""
import argparse
import itertools
import json
from pathlib import Path
import subprocess
import time

from cnf_model import CNF, PAIRS, build, address_data, word_assignments
from exact_checker import IDENTITY, TARGET, column, check, product


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--z3", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    passed = []
    for operation in ("and", "xor"):
        for aa, bb in itertools.product((1, -1, 2, -2, 3, -3), repeat=2):
            c = CNF()
            c.variable()
            c.variable()
            result = c.both(aa, bb) if operation == "and" else c.xor(aa, bb)
            for vals in itertools.product((False, True), repeat=c.variables - 1):
                assignment = {1: True, **dict(zip(range(2, c.variables + 1), vals))}
                truth = lambda lit: assignment[abs(lit)] == (lit > 0)
                expected = (truth(aa) and truth(bb)) if operation == "and" else (truth(aa) != truth(bb))
                satisfied = all(any(truth(x) for x in clause) for clause in c.clauses)
                assert satisfied == (truth(result) == expected)
    passed.append("all_gate_truth_tables_including_constants_signs_and_aliases")
    generators = [(u, v, i, j) for u in range(1, 8) for v in range(1, 8)
                  if (u & v).bit_count() % 2 for i, j in PAIRS]
    for gate in generators:
        word = [gate]
        endpoint = [column(word, c) for c in range(3)]
        cnf, selectors, states, elements, _ = build(1, support_bounds=False,
                                                   endpoint_columns=endpoint)
        assert cnf.failed_clauses(word_assignments(word, selectors, states, elements)) == 0
    passed.append("all_168_factors_have_satisfying_independent_CNF_assignments")
    for k in range(32):
        word = [generators[(k * 5) % 168], generators[(k * 37 + 19) % 168]]
        endpoint = [column(word, c) for c in range(3)]
        cnf, selectors, states, elements, _ = build(2, support_bounds=False,
                                                   endpoint_columns=endpoint)
        assert cnf.failed_clauses(word_assignments(word, selectors, states, elements)) == 0
    passed.append("32_mixed_two_factor_full_matrix_assignments")
    elements, index, distance, paths, perms = address_data()
    direct = [(1 << r, 1 << r, *PAIRS[label]) for r in range(3) for label in paths[TARGET[r]]]
    assert len(direct) == 9 and check(direct)["accepted"]
    alias = [(2, 3, 0, 2), (1, 3, 2, 1), (1, 1, 1, 2),
             (3, 1, 0, 1), (1, 1, 2, 1), (1, 1, 1, 0), (1, 3, 0, 1)]
    alias_target = ((4, 1, 2), (7, 2, 4), IDENTITY)
    cases = [
        ("direct_nine", direct, TARGET, True),
        ("omitted_last", direct[:-1], TARGET, False),
        ("natural_alias", alias, alias_target, False),
        ("dirty_third", direct + [(4, 4, 0, 1)], TARGET, False),
    ]
    solver_results = []
    for bounded in (False, True):
        for name, word, target, expected in cases:
            cnf, selectors, states, elements, metadata = build(len(word), target, bounded)
            failed = cnf.failed_clauses(word_assignments(word, selectors, states, elements))
            assert (failed == 0) == expected, (name, bounded, failed)
            for gate, (u, v, labels) in zip(word, selectors):
                for k in range(3):
                    cnf.add(u[k] if gate[0] & (1 << k) else -u[k])
                    cnf.add(v[k] if gate[1] & (1 << k) else -v[k])
                for k, label in enumerate(labels):
                    cnf.add(label if PAIRS[k] == tuple(gate[2:]) else -label)
            path = out / f"{name}-bounded-{int(bounded)}.cnf"
            cnf.write(path)
            completed = subprocess.run([args.z3, "-dimacs", "-T:30", "-memory:2048", str(path)],
                                       capture_output=True, text=True, timeout=40)
            wanted = "s SATISFIABLE" if expected else "s UNSATISFIABLE"
            assert wanted in completed.stdout.splitlines(), (name, bounded, completed.stdout, completed.stderr)
            solver_results.append({"name": name, "support_bounds": bounded,
                                   "expected": wanted, "output": completed.stdout.strip()})
    passed.append("eight_fixed_word_native_SAT_positive_negative_calibrations")
    report = {"status": "PASS", "checks": passed, "solver_cases": solver_results,
              "elapsed_seconds": time.perf_counter() - started}
    (out / "CONTROLS.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "checks": passed,
                      "solver_case_count": len(solver_results),
                      "elapsed_seconds": report["elapsed_seconds"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
