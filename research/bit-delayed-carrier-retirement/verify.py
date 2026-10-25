#!/usr/bin/env python3
"""Authenticate and replay two separately written exact implementations.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    # Serialized comparison distinguishes JSON true/false from integers1/0.
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main():
    manifest = json.loads((ROOT/"MANIFEST.json").read_text())
    require(manifest["schema_version"] == 1, "manifest schema")
    for name, expected in manifest["files"].items():
        require(sha256((ROOT/name).read_bytes()).hexdigest() == expected,
                "package hash " + name)
    outputs = {}
    # Read each child source once, authenticate those bytes, then execute
    # precisely those bytes. No .pyc import or check-then-reopen path.
    bootstrap = (
        "import hashlib,pathlib,sys\n"
        "p=pathlib.Path(sys.argv[1]); source=p.read_bytes()\n"
        "if hashlib.sha256(source).hexdigest()!=sys.argv[2]:\n"
        " raise ValueError('child source hash')\n"
        "exec(compile(source,str(p),'exec'),"
        "{'__name__':'__main__','__file__':str(p),'__package__':None})\n"
    )
    for script, receipt in (("check.py", "RESULT.json"), ("independent.py", "INDEPENDENT.json")):
        argv = [sys.executable, "-I", "-B"]
        if sys.flags.optimize:
            argv.append("-O")
        argv += ["-c", bootstrap, str(ROOT/script), manifest["files"][script]]
        run = subprocess.run(argv, check=True, capture_output=True, text=True, timeout=300)
        require(not run.stderr, "unexpected checker stderr")
        actual = json.loads(run.stdout)
        expected = json.loads((ROOT/receipt).read_text())
        require(canonical(actual) == canonical(expected), "complete receipt mismatch " + script)
        outputs[script] = actual
    primary, independent = outputs["check.py"], outputs["independent.py"]
    for p_name, i_name in (("boolean", "Boolean"), ("signed", "integer")):
        p, i = primary["words"][p_name], independent["variants"][i_name]
        require(p["word_sha256"] == i["canonical_records_sha256"], "independent word")
        for p_key, i_key in (("queries", "paid_queries"), ("adds", "unit_ADDs"),
                             ("rank_mass", "rank_mass"), ("histogram", "histogram"),
                             ("records", "records"), ("copy_erase_pairs", "COPY")):
            require(canonical(p[p_key]) == canonical(i["invoice"][i_key]),
                    "independent invoice " + p_key)
        require(i["geometry"]["maximum_child_rank"] == 7, "strictly smaller children")
    print("PASS_BIT_DELAYED_CARRIER queries=2913->2912 adds=36005->35947 no_new_kappa")


if __name__ == "__main__":
    main()
