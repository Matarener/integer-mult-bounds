"""Portable integrity, CNF regeneration, witness and optional RUP verification.

Brian Ross: conceptual search strategy, research direction and oversight.
Implementation and computational checks: substantial OpenAI Codex assistance.
Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import uuid

from cnf_model import build
from exact_checker import check

ROOT = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(stream):
    result = hashlib.sha256()
    size = 0
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        size += len(block)
        result.update(block)
    return result.hexdigest(), size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proofs", action="store_true",
                        help="actually run the external RUP checker")
    parser.add_argument("--checker", help="locally built DRAT-trim executable")
    args = parser.parse_args()
    require(not args.proofs or args.checker, "--proofs requires --checker")
    count = 0
    for line in (ROOT / "MANIFEST.sha256").read_text().splitlines():
        expected, name = line.split("  ", 1)
        path = ROOT / name
        require(path.resolve().is_relative_to(ROOT), "external manifest path")
        with path.open("rb") as stream:
            actual, _ = digest(stream)
        require(actual == expected, "integrity failure: " + name)
        count += 1
    witness = json.loads((ROOT / "DIRECT_NINE.json").read_text())
    replay = check(witness["word_uvij"])
    require(replay["accepted"] and replay["paid_calls"] == 9,
            "nine-call witness failed exact regular-action replay")
    evidence = json.loads((ROOT / "CERTIFICATES.json").read_text())
    require({x["length"] for x in evidence["certificates"]} == {7, 8},
            "both parity certificates are required")
    reports = []
    for item in evidence["certificates"]:
        cnf, _, _, _, metadata = build(item["length"])
        require((cnf.variables, len(cnf.clauses)) ==
                (item["variables"], item["clauses"]), "CNF counts changed")
        generated = hashlib.sha256()
        generated.update(f"p cnf {cnf.variables} {len(cnf.clauses)}\n".encode("ascii"))
        for clause in cnf.clauses:
            generated.update((" ".join(map(str, clause)) + " 0\n").encode("ascii"))
        with (ROOT / item["cnf"]).open("rb") as stream:
            actual, size = digest(stream)
        require(actual == generated.hexdigest() == item["cnf_sha256"],
                "certified CNF differs from regenerated instance")
        require(size == item["cnf_bytes"], "CNF size mismatch")
        with gzip.open(ROOT / item["proof_gzip"], "rb") as stream:
            proof_hash, proof_size = digest(stream)
        require(proof_hash == item["proof_sha256"] and
                proof_size == item["proof_bytes"], "RUP payload changed")
        require(item["original_checker"]["exit_code"] == 0 and
                item["original_checker"]["result"] == "s VERIFIED",
                "missing original checker record")
        row = {"length": item["length"], "cnf_regenerated": True,
               "proof_payload_hash_valid": True, "proof_replayed": False}
        if args.proofs:
            # Ordinary workspace directory: no dependency on system Temp ACLs.
            work = ROOT / ".verification-work" / uuid.uuid4().hex
            work.mkdir(parents=True)
            proof = work / "proof.rup"
            with gzip.open(ROOT / item["proof_gzip"], "rb") as source, proof.open("wb") as dest:
                shutil.copyfileobj(source, dest)
            command = [str(Path(args.checker).resolve()), str(ROOT / item["cnf"]),
                       str(proof), "-U", "-t", "600"]
            log = work / "checker.log"
            with log.open("w") as output:
                execution = subprocess.run(command, stdout=output,
                                           stderr=subprocess.STDOUT, timeout=610)
            require(execution.returncode == 0 and
                    "s VERIFIED" in log.read_text().splitlines(),
                    "RUP verification failed; log: " + str(log))
            proof.unlink()  # Only this newly decompressed, verified temporary file.
            row["proof_replayed"] = True
            row["checker_log"] = str(log.relative_to(ROOT))
        reports.append(row)
    print(json.dumps({"status": "PASS", "manifest_files": count,
                      "direct_nine_replay": replay, "certificates": reports},
                     indent=2))


if __name__ == "__main__":
    main()
