"""Check the new coalesced word, not the predecessor's supplier claim.

Produced by Nick Petalas. Apache-2.0. The imported checker retains its credit.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from construct import construct, need

CHECKER = "research/p104-unread-path-resynthesis/local.py"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def sources():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for pin in pins["files"]:
        if pin["usage"] == "input":
            need(digest(ROOT / pin["path"]) == pin["sha256"], "Source bytes: " + pin["path"])
    path = ROOT / CHECKER
    spec = importlib.util.spec_from_file_location("owned_coalescence_checker", path)
    need(spec is not None and spec.loader is not None, "Checker import specification")
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    raw = (HERE / "inputs/pr6144-WORD.json.gz").read_bytes()
    predecessor = json.loads((HERE / "PREDECESSOR.json").read_text())
    need(len(raw) == predecessor["size"] and sha256(raw).hexdigest() == predecessor["sha256"],
         "Exact retained predecessor word")
    return checker, json.loads(gzip.decompress(raw))


def inventory(word):
    """Count events and literal prices; no predecessor endpoint replay."""
    need(len(word["program"]) <= 26000, "Finite program bound")
    scalar = 0
    paid = Counter()
    events = Counter()
    for event in word["program"]:
        op = event[0]
        events[op] += 1
        if op == "MOVE":
            paid[abs(len(word["frames"][event[2]]) - len(word["frames"][event[3]]))] += 1
        elif op in ("INIT", "CLEAR"):
            scalar += 2
        else:
            q = Fraction(event[-2])
            n, d = abs(q.numerator), q.denominator
            if op == "SCALE":
                scalar += 2 * (abs(n.bit_length() - d.bit_length()) + int(q < 0))
            else:
                scalar += 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)
    return {"scalar_units": scalar, "paid": dict(sorted(paid.items())),
            "events": dict(sorted(events.items()))}


def rejected(action):
    try:
        action()
    except (ValueError, IndexError, KeyError):
        return True
    raise ValueError("Fault was accepted")


def controls(checker, source, word):
    results = {}
    sites = {
        "missing_source_init": next(i for i, e in enumerate(word["program"]) if e == ["INIT", 790, 549]),
        "missing_half": next(i for i, e in enumerate(word["program"]) if e == ["SCALE", 790, "1/2", 549]),
        "missing_clear": next(i for i, e in enumerate(word["program"]) if e == ["CLEAR", 790, 593]),
        "missing_descent": next(i for i, e in enumerate(word["program"]) if e == ["MOVE", 790, 549, 553, True]),
        "missing_first_read": next(i for i, e in enumerate(word["program"]) if e == ["ADD", 169, 790, "-2", 553]),
    }
    for name, site in sites.items():
        bad = deepcopy(word)
        bad["program"].pop(site)
        results[name] = rejected(lambda: checker.replay(bad))
    bad = deepcopy(word)
    bad["program"][sites["missing_half"]][2] = "-1/2"
    results["wrong_half_sign"] = rejected(lambda: checker.replay(bad))
    bad = deepcopy(source)
    bad["program"][14000] = ["ADD", 791, 770, "1", 549]
    results["hidden_source_use"] = rejected(lambda: construct(bad))
    bad = deepcopy(source)
    bad["program"][13659][3] = "2"
    results["wrong_copy_anchor"] = rejected(lambda: construct(bad))
    bad = deepcopy(source)
    bad["owned_fields"] = 28
    results["wrong_inventory"] = rejected(lambda: construct(bad))
    return results


def run():
    checker, source = sources()
    word = construct(source)
    before, after = inventory(source), inventory(word)
    need(before["scalar_units"] == 189658 and after["scalar_units"] == 189646,
         "Exactly twelve scalar units saved")
    need(before["paid"] == after["paid"], "Every paid rank count preserved")
    moves = lambda w: Counter(tuple(e[2:]) for e in w["program"] if e[0] == "MOVE")
    need(moves(source) == moves(word), "Every signed native frame boundary preserved")
    need(all(source[key] == word[key] for key in source if key not in ("program", "owned_fields")),
         "Every public boundary and frame retained")
    local = checker.replay(word)
    columns = checker.reverse_columns(word)
    need((local["owned_fields"], local["owned_lifetimes"], local["peak_owned_fields"]) == (28, 30, 13),
         "New complete ownership inventory")
    need(local["real_scalar_allowance"] == after["scalar_units"] and
         local["paid"] == after["paid"], "Independent literal counts agree")
    faults = controls(checker, source, word)
    hashes = {str(p.relative_to(HERE)): digest(p) for p in sorted(HERE.rglob("*"))
              if p.is_file() and p.name != "RESULT.json" and "__pycache__" not in p.parts}
    word_hash = sha256(json.dumps(word, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"status": "PASS_OWNED_LIFETIME_COALESCENCE", "source_hashes": hashes,
            "constructed_word_payload_sha256": word_hash,
            "before": before, "after": after, "edited_events": len(word["program"]),
            "local": local, "transpose": columns, "rejection_controls": faults,
            "claim_type": "finite circuit certificate and scoped substitution proof",
            "limits": ["No new kappa or paid-profile improvement.",
                       "Peak owned occupancy remains thirteen.",
                       "Rounded, native, physical caller and all-size admission are not replayed."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt-out", type=Path)
    args = parser.parse_args()
    result = run()
    payload = (json.dumps(result, sort_keys=True, indent=2) + "\n").encode()
    if args.receipt_out:
        need(HERE not in args.receipt_out.resolve().parents, "Receipt output belongs outside the package")
        args.receipt_out.write_bytes(payload)
    else:
        need((HERE / "RESULT.json").read_bytes() == payload, "Exact generated receipt")
    columns = result["transpose"]
    saved = result["before"]["scalar_units"] - result["after"]["scalar_units"]
    print(result["status"], f"columns={columns['columns']} coefficients={columns['coefficients']}",
          f"controls={len(result['rejection_controls'])} scalar_saved={saved}")


if __name__ == "__main__":
    main()
