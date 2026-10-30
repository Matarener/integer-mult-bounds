#!/usr/bin/env python3
"""Complete Boolean paid inventory for Norm∘F_(2,1) on PR2808.

Answers weighted-wrapper-contract / #2950 OQ1 with scale+inverse+source-access+
restoration+frame/copy meters on the unchanged Boolean origin-plane fixture.
No new kappa. Admission uses need(); remains active under python -O.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_WEIGHTED_CALLEE_BOOLEAN_NORM_INVOICE "
    "M=3 n=2 a=(2,1) "
    "raw_agreements=9/81 "
    "normalized_agreements=81/81 "
    "scale=2268 inverse=2268 source_access=1134 "
    "restoration=1162 frame_copy=3402 "
    "no_new_kappa"
)
PRIOR_TASK = "research/weighted-wrapper-contract/TASK.json"
PRIOR_README = "research/weighted-wrapper-contract/README.md"
PRIOR_ALGEBRA = "research/weighted-wrapper-contract/algebra.py"
PRIOR_RUNTIME = "research/weighted-wrapper-contract/runtime_check.py"
OUTER = "research/selected-outer-borrowing-wrapper/outer.py"
PADDING = "research/selected-outer-borrowing-wrapper/vendor/pr2786/padding.py"
INPUTS = (
    PRIOR_TASK,
    PRIOR_README,
    PRIOR_ALGEBRA,
    PRIOR_RUNTIME,
    "research/selected-outer-borrowing-wrapper/README.md",
    "research/selected-outer-borrowing-wrapper/VENDOR.json",
    "research/selected-outer-borrowing-wrapper/controls.py",
    OUTER,
    "research/selected-outer-borrowing-wrapper/predecessor.py",
    "research/selected-outer-borrowing-wrapper/vendor/pr2786/PREDECESSOR.json",
    "research/selected-outer-borrowing-wrapper/vendor/pr2786/README.md",
    PADDING,
    "research/selected-outer-borrowing-wrapper/vendor/pr2786/predecessor.tar.gz",
    "research/selected-outer-borrowing-wrapper/vendor/pr2786/source.py",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    need(
        manifest["base_commit"] == "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "base commit pin",
    )
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    pinned = {}
    for row in rows:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        need(len(raw) == row["size_bytes"], "source size: " + row["path"])
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source hash: " + row["path"])
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        need(
            hashlib.sha1(blob, usedforsecurity=False).hexdigest() == row["git_blob"],
            "source git blob: " + row["path"],
        )
        pinned[row["path"]] = raw
    return pinned


def bind_prior_oq(pinned):
    task = pinned[PRIOR_TASK].decode("utf-8")
    readme = pinned[PRIOR_README].decode("utf-8")
    need(
        "Can a proposed weighted callee be normalized cheaply enough" in task,
        "cite: weighted-wrapper-contract TASK OQ1",
    )
    need(
        "count all coordinate scale, inverse, source-access and restoration costs"
        in task,
        "cite: OQ1 first_step complete inventory",
    )
    need(
        "Can one concrete weighted callee be normalized at an affordable complete cost?"
        in readme,
        "cite: weighted-wrapper-contract README OQ",
    )
    need(
        "charging every scale/inverse, source access," in readme
        and "frame change, copy and restoration" in readme,
        "cite: README complete line items",
    )
    need("Theorem 1 (necessary and sufficient contract)" in readme, "cite: Thm 1")
    outer = pinned[OUTER].decode("utf-8")
    need("def body_ordinary" in outer, "cite: unchanged body_ordinary")
    padding = pinned[PADDING].decode("utf-8")
    need("def complete" in padding, "cite: padding.complete")
    need('mode in ("copy", "zero", "discard")' in padding, "cite: scan_rows modes")
    runtime = pinned[PRIOR_RUNTIME].decode("utf-8")
    need("Boolean coordinate" in runtime or "Boolean output" in runtime, "cite: Boolean")


def cross_check_prior_algebra(inv):
    """Prior algebra.word on P_a must recover formula-(5) raw agreements 9/81."""
    algebra = runpy.run_path(str(ROOT / PRIOR_ALGEBRA))
    vectors = [(x0, x1) for x0 in range(3) for x1 in range(3)]
    index = {v: i for i, v in enumerate(vectors)}
    add = tuple(
        tuple(index[tuple((a + b) % 3 for a, b in zip(x, y))] for y in vectors)
        for x in vectors
    )
    sub = tuple(
        tuple(index[tuple((a - b) % 3 for a, b in zip(x, y))] for y in vectors)
        for x in vectors
    )
    weights = inv["WEIGHTS"]
    p_map = []
    pinv_map = []
    for v in vectors:
        p_map.append(index[(weights[0] * v[1] % 3, weights[1] * v[0] % 3)])
        # P(x0,x1)=(w0 x1, w1 x0); inverse: x0 = w1^{-1} y1, x1 = w0^{-1} y0
        x0 = pow(weights[1], -1, 3) * v[1] % 3
        x1 = pow(weights[0], -1, 3) * v[0] % 3
        pinv_map.append(index[(x0, x1)])
    agrees = 0
    for h in range(9):
        for d in range(9):
            oh, od = algebra["word"](h, d, p_map, pinv_map, p_map, pinv_map, add, sub)
            if (oh, od) == (d, h):
                agrees += 1
    need(agrees == inv["RAW_AGREEMENTS"], "prior algebra raw agreements")


def compare_certificate(cert, write: Path | None):
    text = json.dumps(cert, indent=2, sort_keys=True) + "\n"
    path = HERE / "CERTIFICATE.json"
    if write is not None:
        write.write_text(text)
        return
    need(path.is_file(), "CERTIFICATE.json missing")
    committed = path.read_text()
    need(committed == text, "certificate mismatch")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        type=Path,
        help="explicit exclusive path to write a freshly checked certificate",
    )
    args = parser.parse_args(argv)
    pinned = pin_sources()
    bind_prior_oq(pinned)
    inv = runpy.run_path(str(HERE / "invoice.py"))
    cross_check_prior_algebra(inv)
    cert = inv["build_certificate"]()
    need(cert["counts"]["raw_agreements"] == 9, "raw 9")
    need(cert["counts"]["normalized_agreements"] == 81, "norm 81")
    need(cert["counts"]["scale"] == 2268, "scale 2268")
    need(cert["counts"]["inverse"] == 2268, "inverse 2268")
    need(cert["counts"]["source_access"] == 1134, "source_access 1134")
    need(cert["counts"]["restoration"] == 1162, "restoration 1162")
    need(cert["counts"]["frame_copy"] == 3402, "frame_copy 3402")
    need(cert["no_new_kappa"] is True, "no new kappa")
    need(cert["kappa_decimal"] == inv["KAPPA_DECIMAL"], "kappa pin")
    compare_certificate(cert, args.write)
    print(MARKER)


if __name__ == "__main__":
    main()
