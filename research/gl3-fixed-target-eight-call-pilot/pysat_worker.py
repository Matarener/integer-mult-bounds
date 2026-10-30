"""One bounded Glucose4 proof-producing solve; launched by pysat_run.py."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import threading
import time

import pysat
import pysolvers
from pysat.formula import CNF
from pysat.solvers import Solver


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cnf", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--seconds", type=int, required=True)
    parser.add_argument("--disk-mb", type=int, default=512)
    parser.add_argument("--selectors")
    args = parser.parse_args()
    out = Path(args.out)
    formula = CNF(from_file=args.cnf)
    started = time.perf_counter()
    stop = threading.Event()
    interrupted = []
    with Solver(name="g4", bootstrap_with=formula.clauses, with_proof=True,
                use_timer=True) as solver:
        # Official PySAT Glucose4 implementation stores its proof in prfile.
        # fstat does not alter the shared file offset.
        def watch():
            while not stop.wait(0.1):
                if time.perf_counter() - started > args.seconds:
                    interrupted.append("wall_clock_limit")
                elif os.fstat(solver.solver.prfile.fileno()).st_size > args.disk_mb * 1024 * 1024:
                    interrupted.append("proof_disk_limit")
                if interrupted:
                    solver.interrupt()
                    return
        watcher = threading.Thread(target=watch, daemon=True)
        watcher.start()
        answer = solver.solve_limited(expect_interrupt=True)
        stop.set()
        watcher.join(timeout=2)
        report = {"status": "sat" if answer is True else "unsat" if answer is False else "unknown",
                  "interrupted": interrupted, "solve_seconds": solver.time(),
                  "elapsed_seconds": time.perf_counter() - started,
                  "statistics": solver.accum_stats(), "pysat_version": pysat.__version__,
                  "solver": "Glucose4", "pysolvers_path": pysolvers.__file__,
                  "pysolvers_sha256": hashlib.sha256(Path(pysolvers.__file__).read_bytes()).hexdigest()}
        if answer is not True:
            lines = solver.get_proof()
            (out / "proof.raw").write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
            report["proof_lines"] = len(lines)
            report["proof_bytes"] = (out / "proof.raw").stat().st_size
            report["proof_sha256"] = hashlib.sha256((out / "proof.raw").read_bytes()).hexdigest()
        if answer is True and args.selectors:
            truth = {x for x in solver.get_model() if x > 0}
            selectors = json.loads(Path(args.selectors).read_text())
            pairs = [(i, j) for i in range(3) for j in range(3) if i != j]
            word = []
            for u, v, labels in selectors:
                chosen = [k for k, label in enumerate(labels) if label in truth]
                assert len(chosen) == 1
                word.append([sum((1 << k) for k, x in enumerate(u) if x in truth),
                             sum((1 << k) for k, x in enumerate(v) if x in truth),
                             *pairs[chosen[0]]])
            from exact_checker import check
            report["word_uvij"] = word
            report["independent_replay"] = check(word)
        (out / "SOLVER.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
