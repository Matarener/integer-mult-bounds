"""Exact, invocation-local reuse of H4 projective normal classes.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from math import gcd
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
SOURCE = "research/h4-root-linear-copy-floor/verify.py"
LIMIT = 1 << 32


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_bounded(path, capacity):
    with path.open("rb") as stream:
        raw = stream.read(capacity + 1)
    need(len(raw) <= capacity, "file capacity: " + str(path))
    return raw


def load_source():
    manifest = json.loads(read_bounded(HERE / "SOURCES.json", 65536))
    pins = [row for row in manifest["files"] if row["path"] == SOURCE]
    need(len(pins) == 1 and pins[0]["usage"] == "input", "one live source pin")
    path = HERE.parents[1] / SOURCE
    need(path.is_file() and not path.is_symlink(), "regular retained source")
    raw = read_bounded(path, 131072)
    need(sha256(raw).hexdigest() == pins[0]["sha256"], "source SHA256")
    source = types.ModuleType("authenticated_h4_source")
    source.__file__ = str(path)
    exec(compile(raw, str(path), "exec", optimize=0), source.__dict__)
    return source


def projective_key(vector):
    """Primitive integer representative after conjugating the first pivot."""
    need(isinstance(vector, tuple) and len(vector) == 4, "normal arity")
    need(all(isinstance(x, tuple) and len(x) == 2 for x in vector), "field pairs")
    need(all(type(a) is int and abs(a) <= LIMIT for x in vector for a in x),
         "integer normal capacity")
    pivot = next((x for x in vector if x != (0, 0)), None)
    need(pivot is not None, "nonzero normal")
    c, d = pivot
    norm = c * c + c * d - d * d
    need(norm != 0, "nonzero field norm")
    # phi' = 1-phi; (a+b phi)(c+d-d phi).
    values = tuple(z for a, b in vector for z in
                   (a * (c + d) - b * d, b * c - a * d))
    divisor = 0
    for value in values:
        divisor = gcd(divisor, value)
    need(divisor > 0, "nonzero primitive divisor")
    signed_divisor = divisor if norm > 0 else -divisor
    return tuple(value // signed_divisor for value in values)


def hyperplanes(roots, source, stats=None):
    need(len(roots) == 60, "H4 root-line capacity")
    flats, known = {}, {}
    nonzero = 0
    for indices in combinations(range(60), 3):
        rows = [roots[i] for i in indices]
        normal = source.normal(rows)
        if all(x == source.ZERO for x in normal):
            continue
        nonzero += 1
        source.need(all(source.dot(normal, row) == source.ZERO for row in rows),
                    "cofactor annihilation")
        key = projective_key(normal)
        if key not in known:
            flat = source.mask(i for i, root in enumerate(roots)
                               if source.dot(normal, root) == source.ZERO)
            known[key] = flat
            flats.setdefault(flat, normal)
    source.need(Counter(x.bit_count() for x in flats) == {4: 600, 6: 660, 15: 60},
                "flat census")
    need(len(known) == len(flats), "one projective class per flat")
    if stats is not None:
        stats.update(triples=34220, nonzero_normals=nonzero, classes=len(known),
                     root_scans=len(known), avoided_root_scans=nonzero-len(known))
    return flats


def accelerated_source():
    source = load_source()
    source.hyperplanes = lambda roots: hyperplanes(roots, source)
    return source
