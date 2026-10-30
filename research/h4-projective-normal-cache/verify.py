"""Conformance and failure controls for projective-normal reuse.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

from contextlib import redirect_stdout
from fractions import Fraction
from hashlib import sha256
from io import StringIO
from itertools import product
import json
from pathlib import Path
import runpy
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
API = runpy.run_path(str(HERE / "accelerator.py"))
need = API["need"]


def rational_key(vector):
    c, d = next(x for x in vector if x != (0, 0))
    denominator = c * c + c * d - d * d
    return tuple((Fraction(a * (c + d) - b * d, denominator),
                  Fraction(b * c - a * d, denominator)) for a, b in vector)


def check_keys(source):
    alphabet = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))
    scalars = tuple(x for x in product(range(-1, 2), repeat=2) if x != (0, 0))
    scalars += ((2, 0), (0, 2), (-1, 2))
    forward, backward = {}, {}
    vectors = scaled = 0
    for vector in product(alphabet, repeat=4):
        if not any(x != (0, 0) for x in vector):
            continue
        key, exact = API["projective_key"](vector), rational_key(vector)
        need(forward.setdefault(key, exact) == exact, "no false key collision")
        need(backward.setdefault(exact, key) == key, "no split projective class")
        vectors += 1
        for scalar in scalars:
            other = tuple(source.mul(x, scalar) for x in vector)
            need(API["projective_key"](other) == key, "field-scale invariance")
            need(rational_key(other) == exact, "independent scale comparison")
            scaled += 1
    return {"vectors": vectors, "projective_classes": len(forward),
            "nonzero_field_scalings": scaled}


def check_flats(source):
    roots, _ = source.geometry()
    permutations = (roots, roots[::-1], roots[17:] + roots[:17],
                    [source.negate(r) if i % 2 else r for i, r in enumerate(roots)])
    counts = []
    for variant in permutations:
        stats = {}
        expected = source.hyperplanes(variant)
        actual = API["hyperplanes"](variant, source, stats)
        need(list(expected.items()) == list(actual.items()),
             "complete flat masks, first normals and insertion order")
        counts.append(stats)
    return counts


def complete_output(source):
    output = StringIO()
    with redirect_stdout(output):
        source.main()
    raw = output.getvalue()
    need(len(raw) <= 8192, "complete output capacity")
    result = json.loads(raw)
    need(result["status"] == "PASS_H4_ROOT_LINEAR_COPY_FLOOR", "complete status")
    return raw, result


def check_controls(source):
    zero = ((0, 0),) * 4
    bad = (zero, zero[:3], ((1, 0),) * 3 + ([1, 0],),
           ((True, 0),) + zero[1:], ((1.0, 0),) + zero[1:],
           ((API["LIMIT"] + 1, 0),) + zero[1:])
    rejected = 0
    for vector in bad:
        try:
            API["projective_key"](vector)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid normal accepted")
    API["projective_key"](((API["LIMIT"], 0),) + zero[1:])
    roots, _ = source.geometry()
    namespace = API["hyperplanes"].__globals__
    with patch.dict(namespace, {"projective_key": lambda vector: (1,)}):
        try:
            API["hyperplanes"](roots, source)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("colliding key mutation accepted")
    return rejected


def check_source_control():
    read = API["read_bounded"]
    def changed(path, capacity):
        raw = read(path, capacity)
        return raw + b"\n" if path.as_posix().endswith(API["SOURCE"]) else raw
    with patch.dict(API["load_source"].__globals__, {"read_bounded": changed}):
        try:
            API["load_source"]()
        except ValueError as error:
            need(str(error) == "source SHA256", "source corruption rejection phase")
        else:
            raise ValueError("changed source accepted")


def main():
    source = API["load_source"]()
    keys = check_keys(source)
    flats = check_flats(source)
    baseline, result = complete_output(source)
    accelerated, _ = complete_output(API["accelerated_source"]())
    need(baseline == accelerated, "byte-identical complete historical stdout")
    controls = check_controls(source)
    check_source_control()
    files = sorted(p for p in HERE.iterdir() if p.is_file())
    need(len(files) <= 16, "package inventory capacity")
    hashes = {p.name: sha256(API["read_bounded"](p, 1048576)).hexdigest() for p in files}
    print(json.dumps({"status": "PASS_H4_PROJECTIVE_NORMAL_CACHE", "keys": keys,
                      "flat_variants": flats, "new_rejections": controls + 1,
                      "complete_original_result": result,
                      "complete_stdout_sha256": sha256(baseline.encode()).hexdigest(),
                      "package_sha256": hashes, "no_new_kappa": True}, sort_keys=True))


if __name__ == "__main__":
    main()
