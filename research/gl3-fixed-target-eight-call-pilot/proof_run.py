"""Bounded native DIMACS/DRAT run with a separate DRAT-trim process."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

import psutil


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(command, log_path, seconds, memory_mb=4096, watched_file=None, disk_mb=512, cwd=None):
    started = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    peak = 0
    stop = None
    observed = {}
    with Path(log_path).open("wb") as output:
        process = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT, cwd=cwd)
        monitor = psutil.Process(process.pid)
        while process.poll() is None:
            try:
                family = [monitor] + monitor.children(recursive=True)
                total = 0
                for child in family:
                    try:
                        total += child.memory_info().rss
                        observed[child.pid] = child
                    except psutil.NoSuchProcess:
                        pass
                peak = max(peak, total)
            except psutil.NoSuchProcess:
                break
            if time.perf_counter() - start > seconds:
                stop = "wall_clock_limit"
            elif peak > memory_mb * 1024 * 1024:
                stop = "resident_memory_limit"
            elif watched_file and Path(watched_file).exists() and Path(watched_file).stat().st_size > disk_mb * 1024 * 1024:
                stop = "proof_disk_limit"
            if stop:
                for pid, child in list(observed.items()):
                    if pid != process.pid:
                        try:
                            child.kill()
                        except psutil.NoSuchProcess:
                            pass
                process.kill()
                break
            time.sleep(0.1)
        code = process.wait(timeout=10)
    result = {"command": list(map(str, command)), "cwd": str(cwd) if cwd else None, "started_utc": started,
            "elapsed_seconds": time.perf_counter() - start, "exit_code": code,
            "watchdog_stop": stop, "peak_rss_bytes_sampled": peak,
            "memory_sample_scope": "sum of process and recursive descendants",
            "observed_process_count": len(observed),
            "wall_limit_seconds": seconds, "rss_limit_mb": memory_mb,
            "log_sha256": digest(log_path)}
    Path(str(log_path) + ".json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cnf", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--z3", required=True)
    parser.add_argument("--checker", required=True)
    parser.add_argument("--seconds", type=int, default=600)
    parser.add_argument("--checker-seconds", type=int, default=300)
    parser.add_argument("--memory-mb", type=int, default=4096)
    parser.add_argument("--disk-mb", type=int, default=512)
    args = parser.parse_args()
    if not (1 <= args.seconds <= 900 and 1 <= args.checker_seconds <= 600
            and 256 <= args.memory_mb <= 4096 and 1 <= args.disk_mb <= 512):
        parser.error("outside pilot limits")
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    cnf = Path(args.cnf).resolve()
    # This Z3 build's CLI silently fails when the output argument ends in .drat.
    # .raw is calibrated; the file content is standard ASCII DRAT.
    proof = out / "proof.raw"
    report = {"status": "RUNNING", "input_cnf": str(cnf),
              "input_cnf_sha256": digest(cnf), "z3_binary_sha256": digest(args.z3),
              "checker_binary_sha256": digest(args.checker),
              "psutil_version": psutil.__version__, "proof_disk_limit_mb": args.disk_mb,
              "independent_cnf_unsat_verified": False,
              "original_problem_equivalence_requires_encoding_audit": True}
    (out / "CHECK.json").write_text(json.dumps(report, indent=2) + "\n")
    command = [str(Path(args.z3).resolve()), "-dimacs", f"-T:{args.seconds}",
               f"-memory:{args.memory_mb}", "-st", "sat.threads=1", "sat.random_seed=0",
               "sat.drat.binary=false", "sat.drat.file=proof.raw", str(cnf)]
    report["solver"] = execute(command, out / "solver.log", args.seconds + 10,
                               args.memory_mb, proof, args.disk_mb, cwd=out)
    output = (out / "solver.log").read_text(errors="replace")
    report["solver_reported_unsat"] = "s UNSATISFIABLE" in output.splitlines()
    if proof.exists():
        report["proof_sha256"] = digest(proof)
        report["proof_bytes"] = proof.stat().st_size
    if report["solver_reported_unsat"] and not report["solver"]["watchdog_stop"]:
        report["checker"] = execute(
            [str(Path(args.checker).resolve()), str(cnf), str(proof),
             "-t", str(args.checker_seconds)],
            out / "checker.log", args.checker_seconds + 10, args.memory_mb)
        checked = (out / "checker.log").read_text(errors="replace")
        report["independent_cnf_unsat_verified"] = (
            report["checker"]["exit_code"] == 0 and
            not report["checker"]["watchdog_stop"] and
            "s VERIFIED" in checked.splitlines())
        report["status"] = "CNF_UNSAT_VERIFIED" if report["independent_cnf_unsat_verified"] else "PROOF_NOT_VERIFIED"
    else:
        report["status"] = "NO_VERIFIED_PROOF"
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    (out / "CHECK.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)
    raise SystemExit(0 if report["independent_cnf_unsat_verified"] else 1)


if __name__ == "__main__":
    main()
