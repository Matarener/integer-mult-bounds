"""Resource-supervised Glucose4 solve followed by independent RUP checking."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from proof_run import execute, digest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cnf", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--checker", required=True)
    parser.add_argument("--selectors")
    parser.add_argument("--seconds", type=int, default=600)
    parser.add_argument("--checker-seconds", type=int, default=300)
    args = parser.parse_args()
    if not 1 <= args.seconds <= 900 or not 1 <= args.checker_seconds <= 600:
        parser.error("outside pilot limits")
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    cnf = Path(args.cnf).resolve()
    report = {"status": "RUNNING", "input_cnf": str(cnf),
              "input_cnf_sha256": digest(cnf),
              "checker_binary_sha256": digest(args.checker),
              "independent_cnf_unsat_verified": False,
              "proof_system": "RUP (DRAT-trim -U, no RAT additions accepted)",
              "original_problem_equivalence_requires_encoding_audit": True}
    (out / "CHECK.json").write_text(json.dumps(report, indent=2) + "\n")
    command = [str(Path(args.python).resolve()), "-B", str(Path(__file__).with_name("pysat_worker.py")),
               "--cnf", str(cnf), "--out", str(out), "--seconds", str(args.seconds)]
    if args.selectors:
        command += ["--selectors", str(Path(args.selectors).resolve())]
    report["solver_execution"] = execute(command, out / "solver.log", args.seconds + 30, 4096,
                                         out / "proof.raw", 512)
    result = out / "SOLVER.json"
    if result.exists():
        report["solver"] = json.loads(result.read_text())
    if result.exists() and report["solver"]["status"] == "unsat" and not report["solver_execution"]["watchdog_stop"]:
        proof = out / "proof.raw"
        report["proof_sha256"] = digest(proof)
        report["proof_bytes"] = proof.stat().st_size
        report["checker"] = execute(
            [str(Path(args.checker).resolve()), str(cnf), str(proof),
             "-U", "-t", str(args.checker_seconds)],
            out / "checker.log", args.checker_seconds + 10, 4096)
        text = (out / "checker.log").read_text()
        report["independent_cnf_unsat_verified"] = (
            report["checker"]["exit_code"] == 0 and not report["checker"]["watchdog_stop"]
            and "s VERIFIED" in text.splitlines())
        report["status"] = "CNF_UNSAT_VERIFIED" if report["independent_cnf_unsat_verified"] else "PROOF_NOT_VERIFIED"
    else:
        report["status"] = "NO_VERIFIED_PROOF"
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (out / "CHECK.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)
    raise SystemExit(0 if report["independent_cnf_unsat_verified"] else 1)


if __name__ == "__main__":
    main()
