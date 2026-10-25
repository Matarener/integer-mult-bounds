# SPDX-License-Identifier: Apache-2.0
"""Bounded cold replay groups; direct modules also expose focused commands."""
import argparse
import importlib
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))


def run(suite):
    groups = {
        "sources": (("check_selected", ()), ("check_prime", ()), ("check_bounds", ()),
                    ("check_cover", ()), ("check_scalar", ())),
        "execution": (("check_bank", ()), ("check_parking", ()), ("check_grid", ()),
                      ("check_root_streams", ()), ("check_monomial", ()), ("check_machine", (2,)),
                      ("check_machine", (3,)), ("check_failures", ()), ("check_root", (False,)),
                      ("check_root", (True,))),
        "planning": (("check_root_plan", ()),),
    }
    results = []
    for name, arguments in groups[suite]:
        started = time.monotonic()
        result = importlib.import_module(name).run(*arguments)
        record = dict(check=name, arguments=arguments, result=result,
                      elapsed_seconds=round(time.monotonic() - started, 3))
        results.append(record)
        print(json.dumps(record, sort_keys=True), flush=True)
    print(json.dumps(dict(status="PASS_PHYSICAL_COMPLEX_" + suite.upper(), checks=len(results)), sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("sources", "execution", "planning"), required=True)
    run(parser.parse_args().suite)
