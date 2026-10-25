#!/usr/bin/env python3
"""Read-only registered replay of the complete local R438 source-code result."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()

def authenticate():
    manifest = json.loads((HERE / "ARTIFACTS.json").read_bytes())
    for relative, digest in manifest["files"].items():
        path = HERE / relative
        need(not path.is_symlink() and sha(path) == digest, "package input changed: " + relative)
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    for row in sources["files"]:
        if row["usage"] == "input":
            path = REPO / row["path"]
            need(not path.is_symlink() and sha(path) == row["sha256"], "live source changed: " + row["path"])
    expected = json.loads((HERE / "EXPECTED.json").read_bytes())
    need(sha(HERE / "WORD.json.gz") == expected["frozen_gzip_sha256"], "frozen word bytes")
    frozen = json.loads(gzip.decompress((HERE / "WORD.json.gz").read_bytes()))
    need(hashlib.sha256(canonical(frozen)).hexdigest() == expected["canonical_word_sha256"], "frozen complete word")
    return manifest, expected

def replay(out):
    before, expected = authenticate()
    need(not out.exists(), "output must be a fresh path outside the package")
    need(not out.resolve().is_relative_to(HERE), "runtime output inside package")
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    stages = []
    with tempfile.TemporaryDirectory(prefix="r438-python-") as cache:
        for name in ("reconstruct", "check"):
            command = [sys.executable, "-I", "-O", "-B", "-Werror", "-X", "pycache_prefix=" + cache + "/" + name,
                       str(HERE / (name + ".py")), "--repo", str(REPO), "--out", str(out)]
            run = subprocess.run(command, cwd=REPO, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=540)
            out.mkdir(exist_ok=True)
            (out / (name + ".log")).write_text(run.stdout)
            need(run.returncode == 0, name + " failed:\n" + run.stdout[-8000:])
            stages.append(name)
    reconstructed = json.loads((out / "RECONSTRUCTION.json").read_bytes())
    independent = json.loads((out / "INDEPENDENT.json").read_bytes())
    section = json.loads((out / "ancestry/BIT-THREE-ROW.json").read_bytes())
    signed = json.loads((out / "ancestry/BIT-SIGNED-LIFT.json").read_bytes())
    final = json.loads((out / "support/BIT-SUPPORT.json").read_bytes())
    pruned = json.loads((out / "BIT-PRUNED.json").read_bytes())
    need(pruned["controls"] == {"read_deleted_family_rejected":True}, "projection control coverage")
    need(reconstructed["status"] == "PASS_COMPLETE_WORD_RECONSTRUCTION", "reconstruction result")
    need(independent["status"] == "PASS_INDEPENDENT_LOCAL_SIGNED_NATIVE", "independent result")
    need(independent["columns"] == 651 and independent["dirty_helpers"] == 429, "all-column coverage")
    need(independent["projectors"] == 111 and independent["address_columns"] == 3552 and independent["frame_bindings"] == 222, "actual native coverage")
    need(independent["forward"]["profile"] == expected["profile"] and independent["forward"]["counts"] == expected["counts"], "complete native invoice")
    need((len(section["negative_controls"]), len(signed["negative_controls"]), len(final["negative_controls"]), len(independent["controls"])) == (5,2,3,7), "defect control coverage")
    after, _ = authenticate()
    need(before == after, "package manifest changed during replay")
    result = {"status":"PASS_R438_THREE_SOURCE_COPIES_LOCAL_ONLY", "no_new_kappa":True,
              "canonical_frozen_word_sha256":expected["canonical_word_sha256"],
              "semantic_word_sha256":expected["semantic_word_sha256"], "columns":651, "dirty_helpers":429,
              "rank_mass":4989, "rank_saving":132, "profile":expected["profile"], "counts":expected["counts"],
              "independent_controls":independent["controls"], "ancestry_controls":11,
              "native_projectors":111, "address_columns":3552, "frame_bindings":222,
              "stages":stages, "python":sys.version, "seconds":time.monotonic()-started,
              "scope":"Exact local signed and F2 operators, complete common-frame/rank invoice and rational cap ADDRESS identities; no global compiler, precision, owner or kappa admission"}
    (out / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps(result, sort_keys=True))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    need(sys.version_info[:2] == (3,12), "registered environment is Python 3.12")
    if args.out is None:
        with tempfile.TemporaryDirectory(prefix="r438-verification-") as work:
            replay(Path(work) / "result")
    else:
        replay(args.out.resolve())

if __name__ == "__main__":
    main()
