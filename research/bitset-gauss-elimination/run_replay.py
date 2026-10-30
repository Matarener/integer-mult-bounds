"""Run the unchanged complete contraction replay with one Gauss-sum replacement."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from fast_gauss import gauss, require

SOURCE = ROOT.parent / "clifford-exact-contractions"


def authenticate():
    pin_file = ROOT / "PINS.json"
    require(pin_file.stat().st_size <= 65536, "Bounded pin manifest")
    records = json.loads(pin_file.read_text())
    require(1 <= len(records) <= 64, "Bounded source inventory")
    for name, digest in records.items():
        relative = Path(name)
        require(not relative.is_absolute() and ".." not in relative.parts,
                "Repository-local source name")
        path = SOURCE / name
        require(path.is_file() and not path.is_symlink(), "Regular source input")
        require(path.stat().st_size <= 1048576, "Source input at most 1 MiB")
        require(sha256(path.read_bytes()).hexdigest() == digest, "Changed source: " + name)


def run(mode):
    authenticate()
    source = runpy.run_path(str(SOURCE / "verify.py"), run_name="contraction_replay")
    original = source["C"].gauss
    counts = {"gauss_calls": 0, "maximum_dimension": 0}

    def replacement(n, poly):
        counts["gauss_calls"] += 1
        counts["maximum_dimension"] = max(counts["maximum_dimension"], n)
        value = original(n, poly) if mode == "baseline" else gauss(n, poly)
        if mode == "differential":
            require(value == original(n, poly), "Gauss differential mismatch")
        return value

    source["C"].gauss = replacement
    result = source["run"]()
    expected = json.loads((SOURCE / "RESULT.json").read_text())
    require(result == expected, "Entire committed predecessor result")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("PASS_EXACT_CLIFFORD_CONTRACTIONS")
    print(json.dumps(dict(mode=mode, **counts), sort_keys=True), file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "bitset", "differential"), required=True)
    run(parser.parse_args().mode)
