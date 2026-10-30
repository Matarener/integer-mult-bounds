#!/usr/bin/env python3
"""Reject deliberate regressions in disposable copies; no source tree edits.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PROOF = "research/native-tensor-cutoff/PROOF.md"
VERIFIER = "research/native-cutoff-independent-audit/verify.py"
MUTATIONS = (
    ("erase_quadratic_phase", "characters",
     "answer += 2 * b *", "answer += 0 * b *", "literal phase mismatch"),
    ("tensor_constant_once", "one-axis",
     "sum(phase(x, c, [a], []) for x in bits) % 4",
     "(c + sum(phase(x, 0, [a], []) for x in bits)) % 4", "one-axis window rank failed"),
    ("omit_span_condition", "characters",
     "if mask not in full:", "if False:", "padding changed character or span"),
    ("forbid_multiplicity_four", "characters",
     "product(range(5), repeat=size)", "product(range(4), repeat=size)", "missing phase character"),
    ("wrong_weight_projector", "one-axis",
     "(-2 * c - 3 * a) % 4", "(-2 * c - 2 * a) % 4", "sharpness trap did not vanish"),
)


def main():
    source = (ROOT / VERIFIER).read_text(encoding="utf-8")
    proof = (ROOT / PROOF).read_bytes()
    records = []
    with tempfile.TemporaryDirectory(prefix="native-cutoff-audit-") as temporary:
        root = Path(temporary)
        script = root / VERIFIER
        pinned = root / PROOF
        script.parent.mkdir(parents=True)
        pinned.parent.mkdir(parents=True)
        for optimized in (False, True):
            for name, section, old, new, expected in (*MUTATIONS,
                    ("changed_source_proof", "controls", None, None, "source proof hash mismatch")):
                if old is not None:
                    if source.count(old) != 1:
                        raise ValueError("mutation target is not unique: " + name)
                    changed = source.replace(old, new)
                else:
                    changed = source
                script.write_text(changed, encoding="utf-8", newline="\n")
                pinned.write_bytes(proof + (b"\nchanged\n" if old is None else b""))
                command = [sys.executable, "-I", *(["-O"] if optimized else []),
                           "-W", "error", "-B", str(script), "--section", section]
                result = subprocess.run(command, cwd=root, capture_output=True,
                                        text=True, encoding="utf-8", timeout=30)
                if result.returncode == 0 or expected not in result.stderr or result.stdout:
                    raise ValueError(f"mutation did not fail as expected: {name}: {result}")
                records.append({"mutation": name, "optimized": optimized,
                                "exit_code": result.returncode, "expected_rejection": expected})
    print(json.dumps({"status": "PASS_NATIVE_CUTOFF_AUDIT_MUTATIONS",
                      "verifier_sha256": sha256((ROOT / VERIFIER).read_bytes()).hexdigest(),
                      "mutation_driver_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
                      "records": records}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
