"""Source-bound scalar/bitset replay adapter; Apache-2.0.

Produced by Nick Petalas. Matarener retains the original replay and facts.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from incidence import capacities, require

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
PREDECESSOR = ROOT / "research/p104-bform-nine-term-floor"


def checked_bytes(path, expected):
    require(path.is_file() and not path.is_symlink(), "regular source input")
    require(path.stat().st_size <= 16 * 1024 * 1024, "bounded source input")
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == expected, "source hash mismatch")
    return data


def authenticate():
    manifest = PACKAGE / "SOURCES.json"
    require(manifest.stat().st_size <= 1024 * 1024, "bounded source manifest")
    rows = json.loads(manifest.read_text())["files"]
    require(len(rows) <= 256, "bounded source inventory")
    for row in rows:
        if row["usage"] == "input":
            relative = Path(row["path"])
            require(not relative.is_absolute() and ".." not in relative.parts,
                    "relative source path")
            checked_bytes(ROOT / relative, row["sha256"])


def span_source(engine):
    path = PREDECESSOR / "checks/spanlemma.py"
    source = path.read_text()
    # The original unrecognised \H escape is literal in its docstring.
    # Raw spelling preserves that value while permitting warning-strict compile.
    require(source.startswith('"""Finite facts'), "exact predecessor docstring")
    source = "r" + source
    if engine == "bitset":
        start = source.index("# S0\n")
        end = source.index("# S1 normals\n")
        old = source[start:end]
        definitions = old[len("# S0\n"):old.index("f = {}\n")]
        tail = old[old.index("log('S0 label caps"):]
        source = (source[:start] + definitions + "f = capacities(tuple(P), 9)\n" + tail
                  + source[end:])
    return path, source


def complete_source(engine):
    path = PREDECESSOR / "verify.py"
    source = path.read_text()
    old = "o = run(PKG / 'checks' / 'spanlemma.py')"
    require(source.count(old) == 1, "unique complete-consumer substitution")
    if engine == "bitset":
        new = (f"o = run(Path({str(PACKAGE / 'replay.py')!r}), "
               "'--scope', 'span', '--engine', 'bitset')")
        source = source.replace(old, new)
    return path, source


def replay(scope, engine):
    require(scope in ("span", "complete"), "known replay scope")
    require(engine in ("scalar", "bitset"), "known replay engine")
    require(not sys.flags.optimize, "retain every predecessor assertion")
    authenticate()
    path, source = span_source(engine) if scope == "span" else complete_source(engine)
    namespace = {"__file__": str(path), "__name__": "__main__",
                 "capacities": capacities}
    sys.argv = [str(path)]
    exec(compile(source, str(path), "exec"), namespace)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("span", "complete"), required=True)
    parser.add_argument("--engine", choices=("scalar", "bitset"), required=True)
    args = parser.parse_args()
    replay(args.scope, args.engine)


if __name__ == "__main__":
    main()
