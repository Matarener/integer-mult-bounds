"""Check that the two independently retained packages use identical source bytes."""
from pathlib import Path
import hashlib, json
root = Path(__file__).resolve().parent
prior = root.parent / "p104-cross-call-paid-reuse"
pairs = [(root / "inputs" / name, prior / "inputs" / name) for name in (
    "DATA-PHASES.json", "NOTICE5718", "clifford_exact.py", "controller5718.json",
    "native_verify.py", "result5718.json", "word5718.json.gz")]
pairs += [(root / "inputs/predecessor-experiment.py", prior / "experiment.py"),
          (root / "inputs/predecessor-SOURCES.json", prior / "SOURCES.json"),
          (root / "inputs/QUERY-MAPS.json.gz", prior / "results/QUERY-MAPS.json.gz")]
for left, right in pairs:
    if left.read_bytes() != right.read_bytes():
        raise ValueError("Publication source mismatch: " + str(right))
print(json.dumps({"status": "PASS_PUBLICATION_SOURCE_JOIN", "identical_files": len(pairs)}))
