"""Cold, bounded checks for the active-width T74 contribution."""

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from time import monotonic

sys.path.insert(0, str(Path(__file__).resolve().parent))
import active_sources


def module(name):
    path = Path(__file__).resolve().parent / (name + ".py")
    spec = importlib.util.spec_from_file_location("active_suite_" + name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = result
    spec.loader.exec_module(result)
    return result


def report(name, function, *args):
    start = monotonic()
    result = function(*args)
    print(json.dumps({"check": name, "seconds": round(monotonic()-start, 3), "result": result}, sort_keys=True), flush=True)


def ordinary_premise(roots):
    root = roots["ordinary-rate-export.tar"]
    script = root / "research/retuned-ordinary-coupling/verify.py"
    result = subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B", str(script),
                             "--suite", "certificate"], cwd=root, capture_output=True, text=True, timeout=120)
    active_sources.require(result.returncode == 0, "ordinary premise replay: " + result.stderr[-2000:])
    value = json.loads(result.stdout)
    active_sources.require(value["status"] == "PASS_RETUNED_ORDINARY_CERTIFICATE"
                           and value["ordinary_saving"] == "576/332929", "actual retained ordinary proof point")
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True,
                        choices=("science", "contracts", "plans", "native", "runtime", "controls", "source-check"))
    parser.add_argument("--archive-name", choices=tuple(active_sources.PINS))
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    if args.suite == "source-check":
        active_sources.require(args.archive_name is not None and args.archive is not None, "explicit source check")
        active_sources.authenticate(args.archive_name, args.archive)
        print("PASS_ACTIVE_T74_SOURCE_BYTES")
    else:
        active_sources.require(args.archive is None and args.archive_name is None, "no replay input override")
        if args.suite == "science":
            with active_sources.exports() as roots:
                report("ordinary-premise", ordinary_premise, roots)
                report("active-width-budget", module("active_budget").run, roots)
            report("single-bit-exposure", module("exposure").run)
        elif args.suite == "controls":
            report("source-controls", module("test_active_controls").run)
        else:
            name = {"contracts": "check_active_contracts", "plans": "check_active_plans",
                    "native": "check_native_flow", "runtime": "check_active_runtime"}[args.suite]
            with active_sources.opened():
                report(args.suite, module(name).run)
        print("PASS_ACTIVE_WIDTH_T74_" + args.suite.upper(), flush=True)
