"""Authenticate the scientific products of all five native stages.

SPDX-License-Identifier: Apache-2.0
Completion flags are not output commitments. This closure is fixed by recorded
honest executions, not regenerated from a caller's cache during verification.
Only two root elapsed-time fields and gzip transport bytes are normalized.
"""
import hashlib
import json
import math
from pathlib import Path

from binding import need, read, sha

HERE = Path(__file__).resolve().parent
STAGES = ("native", "ledgers", "local-replay", "wrappers", "phases")
REFERENCES = {"canonical_word_sha256": "CANONICAL-WORD.json.gz",
              "local_programs_sha256": "LOCAL-PROGRAMS.json.gz",
              "recipe_sha256": "CLIFFORD-RECIPES.json"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def scientific_products(native):
    steps = read(native / "STEPS.json")
    need([s["step"] for s in steps] == list(STAGES)
         and all(type(s["exit_code"]) is int and s["exit_code"] == 0 for s in steps),
         "actual native stage products coverage")
    local = native / "local"
    products = {}
    for path in sorted(local.iterdir()):
        need(path.is_file() and not path.is_symlink(), "ordinary native product")
        value = read(path)
        if path.name in ("SCALAR-FRAME-AUDIT.json", "CLIFFORD-REVIEW.json"):
            seconds = value.pop("seconds")
            need(type(seconds) in (int, float) and math.isfinite(seconds) and seconds >= 0,
                 "finite nonnegative native timing")
        for field, target in REFERENCES.items():
            if field in value:
                need(value[field] == sha(local / target), "stale native reference: " + path.name)
                value[field] = digest(read(local / target))
        products[path.name] = digest(value)
    need({p.relative_to(native).as_posix() for p in native.rglob("*") if p.is_file()}
         == {"STEPS.json"} | {"local/" + n for n in products}, "native output file closure")
    return products


def authenticate_native(pid, word_sha256, native):
    expected = read(HERE / "NATIVE-OUTPUTS.json")["providers"][pid]
    need(expected["word_sha256"] == word_sha256, "native commitment word binding")
    actual = scientific_products(native)
    need(actual == expected["products"], "native scientific output commitment")
    return actual
