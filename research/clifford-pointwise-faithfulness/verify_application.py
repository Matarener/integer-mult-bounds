"""Replay the retained passive ceiling and attach the new width bound.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import source
from bounds import pointwise_bound


def run():
    command = [sys.executable, "-I"]
    if sys.flags.optimize:
        command.append("-O")
    command += ["-W", "error", "-B", str(HERE.parent / "passive-saved-query-ceiling/verify.py")]
    process = subprocess.run(command, capture_output=True, text=True, timeout=150, check=True)
    if process.stderr:
        raise ValueError("The retained replay emitted diagnostics")
    original = json.loads(process.stdout)
    expected = json.loads((HERE / "PASSIVE-REPLAY.json").read_text())
    if original != expected:
        raise ValueError("The complete retained passive receipt changed")
    lower = pointwise_bound(17, 72, clifford=True)
    later = pointwise_bound(17, 84, clifford=True)
    if not lower > Fraction(1, 9) or not later > Fraction(125, 126):
        raise ValueError("The application width bound failed")
    return {"status": "PASS_PASSIVE_CEILING_FROM_WIDTH_72_NO_NEW_KAPPA",
            "source_replay": original["status"], "ambient_axes": 17,
            "first_proved_width": 72, "normalized_squared_error_lower_bound": "1/9",
            "operator_norm_error_lower_bound": "1/3",
            "finite_gram_lower_at_72": str(lower),
            "later_width": 84, "later_squared_error_lower_bound": "125/126",
            "finite_gram_lower_at_84": str(later),
            "affected_independent_inputs": original["zero_diagonal_inputs"],
            "late_grade7_words": original["late_grade7_words"],
            "proof_scope": "One frozen passive columnwise Clifford contract; see APPLICATION.md",
            "new_kappa": None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = run()
    path = HERE / "APPLICATION-RESULT.json"
    if args.write_result:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    elif result != json.loads(path.read_text()):
        raise ValueError("The complete application receipt changed")
    print(result["status"])


if __name__ == "__main__":
    main()
