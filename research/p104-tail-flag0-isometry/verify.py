#!/usr/bin/env python3
"""Apply the channel label isometry to the frames of event 5758.

The transform and the reduced basis are the formulas in the pinned checker
and compiler. This does not import either module's main program, and it does
not search for a new orthonormal basis.
"""

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
CHANNEL = ROOT / "research/p104-native-channel"
TAIL = ROOT / "research/p104-tail-side-correction-seed749717"
MARKER = "PASS_P104_TAIL_FLAG0_ISOMETRY target=34 images=match no_new_kappa"
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]
RANK8 = [499, 23, 232, 32, 112, 15, 7, 2]
CONVERT = "convert=lambda x:sum(dot(x,v)<<j for j,v in enumerate(orth))"
CANON = "return tuple(piv[j]for j in sorted(piv,reverse=True))"


def fail(message):
    raise SystemExit("FAIL_P104_TAIL_FLAG0_ISOMETRY " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canon(values):
    pivots = {}
    for value in values:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    for bit in sorted(pivots):
        for other in pivots:
            if other > bit and pivots[other] >> bit & 1:
                pivots[other] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def convert(value, dual, orthogonal):
    def dot(left, right):
        mixed = sum(((row & right).bit_count() & 1) << index for index, row in enumerate(dual))
        return (left & mixed).bit_count() & 1

    return sum(dot(value, vector) << index for index, vector in enumerate(orthogonal))


def image(frame, dual, orthogonal):
    return list(canon(convert(value, dual, orthogonal) for value in frame))


def checker():
    path = CHANNEL / "vendor/native_verify.py"
    spec = importlib.util.spec_from_file_location("p104_tail_flag0_isometry_native", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-native-channel/NATIVE-RECIPES.json.gz",
        "research/p104-native-channel/check_native.py",
        "research/p104-native-channel/compile.py",
        "research/p104-native-channel/vendor/native_verify.py",
        "research/p104-tail-side-correction-seed749717/AUGMENTED-WITNESS.json.gz",
        "research/p104-tail-side-correction-seed749717/SIDE-TRANSPORTS.json.gz",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def evaluate():
    authenticate()
    require(CONVERT in (CHANNEL / "check_native.py").read_text(encoding="utf-8"), "the transform formula moved")
    require(CANON in (CHANNEL / "compile.py").read_text(encoding="utf-8"), "the basis formula moved")
    recipes = json.loads(gzip.decompress((CHANNEL / "NATIVE-RECIPES.json.gz").read_bytes()))
    iso = recipes["label_isometry"]
    dual = iso["compressed_dual_gram"]
    orthogonal = iso["orthonormal_basis_compressed"]
    module = checker()
    require(list(module.inverse(tuple(iso["compressed_gram"]))) == dual, "the stored dual left the checker inverse")
    tail = json.loads(gzip.decompress((TAIL / "AUGMENTED-WITNESS.json.gz").read_bytes()))
    require(tail["program"][5758] == ["transport", "Y34", RANK8, FULL, 1], "event 5758 changed")
    compiled = json.loads(gzip.decompress((TAIL / "SIDE-TRANSPORTS.json.gz").read_bytes()))
    rows = [
        row for row in compiled["transports"]
        if row["target"] == 34 and row["direction"] == "promote"
    ]
    require(len(rows) == 1, "the promote record moved")
    old = image(RANK8, dual, orthogonal)
    new = image(FULL, dual, orthogonal)
    require(old == rows[0]["old_physical"] and new == rows[0]["new_physical"], "the images left the stored columns")
    return {
        "target": 34,
        "event": 5758,
        "old_physical_image": old,
        "new_physical_image": new,
        "matches_stored_physical": True,
        "dual_matches_checker_inverse": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
