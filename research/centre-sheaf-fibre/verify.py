#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound sheaf reduction, deliberately separate from supplier admission."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
    "research/centre-block-repair-information/independent.py":
        "b298ff3902c14db11e4ed057259785efc185e8ae3bb39c0d1c432e2340ceb4ea",
    "research/community-frontier1094-audit/selected-replay.tar.gz":
        "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6",
}


def local_module(name: str, filename: str):
    # Execute the named source bytes directly, ignoring pre-existing bytecode.
    module = types.ModuleType(name)
    module.__file__ = str(HERE / filename)
    exec(compile((HERE / filename).read_bytes(), module.__file__, "exec"), module.__dict__)
    return module


def geometry(root: Path = ROOT):
    for name, expected in PINS.items():
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("missing regular source: " + name)
        if sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("source SHA256 mismatch: " + name)
    name = "research/centre-block-repair-information/independent.py"
    module = types.ModuleType("credited_pr3071_source_extractor")
    module.__file__ = str(root / name)
    exec(compile((root / name).read_bytes(), module.__file__, "exec"), module.__dict__)
    word, phases = module.sources()
    rows, later = module.query_rows(word)
    if later != [[x / 4 for x in row] for row in rows]:
        raise ValueError("source contract H=R/4 fails")
    routes, products, _ = module.route_certificates(word, phases)
    if len(products) != 112 * 111:
        raise ValueError("source route uniqueness")
    for route in routes:
        if len(route) != 73 or any(route[k] != 1 << k for k in range(17, 73)):
            raise ValueError("spectator identity")
        if any(x >> 17 for x in route[:17]):
            raise ValueError("active subspace invariant")
    return rows, [tuple(route[:17]) for route in routes]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-geometry", action="store_true", help="Print authenticated derived geometry for offline verification")
    parser.add_argument("--geometry", type=Path, help="Use an explicitly labelled derived geometry export rather than re-read the source archive")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    engine = local_module("centre_sheaf_engine", "sheaf.py")
    if args.geometry:
        raw = json.loads(args.geometry.read_text())
        rows = [[Q(x) for x in row] for row in raw["rows"]]
        routes = [tuple(row) for row in raw["routes"]]
        source_mode = "derived geometry only; archive extraction not rerun"
    else:
        rows, routes = geometry(args.root)
        source_mode = "authenticated archive and credited PR3071 extractor"
    if args.emit_geometry:
        print("GEOMETRY_JSON=" + json.dumps({"rows": [[str(x) for x in row] for row in rows], "routes": routes}, separators=(",", ":")))
    # Print finite diagnostic before the stronger assertion, so a failed model
    # reduction remains a reproducible result rather than a silent truncation.
    a, b, c = 0, 6, 85
    group = engine.closure([engine.compose(routes[a], routes[b]), engine.compose(routes[a], routes[c])])
    blocks = engine.coset_classes(routes, set(group))
    diagnostic = [{"ports": block, "rank": engine.rank([[row[p] for p in block] for row in rows])} for block in blocks]
    print("COSET_DIAGNOSTIC=" + json.dumps(diagnostic, separators=(",", ":")))
    result = engine.analyse(rows, routes)
    engine.need(result["owners"] == 4080, "pinned subgroup order differs from 4080")
    result["source_mode"] = source_mode
    print("RESULT_JSON=" + json.dumps(result, sort_keys=True, separators=(",", ":")))
    print("PASS_CENTRE_SHEAF_FIBRE owners=4080 all_ports=112 kernel=1 integer_generator_owners=4080 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, TypeError) as error:
        print("FAIL_CENTRE_SHEAF_FIBRE " + str(error), file=sys.stderr)
        raise SystemExit(1) from error
