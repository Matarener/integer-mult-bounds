"""Authenticated PR2979 base-T74 context; no PR3148/T740 reconstruction.

Credit: Marius-Paul Dumitrean/PR2979; Nick Petalas/PR3187; Jacob
Sussman/PR4268; the retained physical-stream and E8 lineage. Prepared by
ToikY with substantial OpenAI Codex assistance. No original source is edited.
"""

import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
MAIN = "12fa8c5c844be21bfefb38a19503fbd867a11244"
PREFIX = "research/rank7-joint-endframes/allocation/"
PINS = {
    "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json": "d9a4f84211182ca200c081ea061d724c8a2cfb70",
    "research/rank7-idle-star-stream-obstruction/algebra.py": "6a7ff3b2fd184428569e997261a4d00bbf993455",
    "research/rank7-idle-star-stream-obstruction/source.py": "76ff8121ca6c8861f2c89f24f4f8c89957b50da3",
    PREFIX + "DISPATCH.json": "9544fee4e6ee1f202cee22bfaeaf229ee3b2515e",
    PREFIX + "FILL.json.gz": "8d4fd644d60ba2c98106dc770803b647afdf0963",
    PREFIX + "ORDER.json": "7409c4df1092241729739596c7648bda504e6aad",
    PREFIX + "PROVIDERS.json": "e1d99e12cfa3ac8375984d85c0b040dc36ea1312",
    PREFIX + "vendor/PLAN.json.gz": "7a1db55a4d53ee99280be4f3ab7d29f7b2033adf",
    PREFIX + "vendor/TEMPLATE.json.gz": "114808c32b1799da53524bdc25cea67efb60009e",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_inputs(root):
    raw = {}
    receipt = []
    for relative, expected_blob in PINS.items():
        path = root / relative
        require(path.is_file() and not path.is_symlink(), "missing/linked pinned input: " + relative)
        require(path.stat().st_size <= 32_000_000, "oversized pinned input")
        data = path.read_bytes()
        header = b"blob " + str(len(data)).encode("ascii") + b"\0"
        blob = hashlib.sha1(header + data, usedforsecurity=False).hexdigest()
        require(blob == expected_blob, "input Git blob mismatch: " + relative)
        raw[relative] = data
        receipt.append({"path": relative, "git_blob": blob,
                        "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    return raw, receipt


def decode(data):
    if data[:2] == b"\x1f\x8b":
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
            data = stream.read(32_000_001)
    require(len(data) <= 32_000_000, "oversized decoded input")
    return json.loads(data)


def load_retained(root):
    """Import the unmodified, already authenticated files by exact file paths."""
    directory = root / "research/rank7-idle-star-stream-obstruction"
    source_spec = importlib.util.spec_from_file_location("_mixed_cut_retained_source", directory / "source.py")
    source_module = importlib.util.module_from_spec(source_spec)
    source_spec.loader.exec_module(source_module)
    algebra_spec = importlib.util.spec_from_file_location("_mixed_cut_retained_algebra", directory / "algebra.py")
    algebra_module = importlib.util.module_from_spec(algebra_spec)
    absent = object()
    previous = sys.modules.get("source", absent)
    sys.modules["source"] = source_module
    try:
        algebra_spec.loader.exec_module(algebra_module)
    finally:
        if previous is absent:
            del sys.modules["source"]
        else:
            sys.modules["source"] = previous
    return algebra_module


def load(root=ROOT):
    raw, pins = read_inputs(root)
    phases = decode(raw["research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"])
    order = decode(raw[PREFIX + "ORDER.json"])
    dispatch_rows = decode(raw[PREFIX + "DISPATCH.json"])
    fill = decode(raw[PREFIX + "FILL.json.gz"])
    providers = decode(raw[PREFIX + "PROVIDERS.json"])
    plan = decode(raw[PREFIX + "vendor/PLAN.json.gz"])
    template = decode(raw[PREFIX + "vendor/TEMPLATE.json.gz"])
    require(len(order) == 666 and len({tuple(row) for row in order}) == 666,
            "original T74 call chronology")
    require(sorted({replica for _, replica in order}) == list(range(74)), "original 74 replicas")
    require(all([stage for stage, rep in order if rep == replica] == list(range(9))
                for replica in range(74)), "nine original stages per replica")
    require(fill["columns"] == ["time", "helper", "owner_replica", "child", "port", "offset"],
            "literal FILL columns")
    require(len(fill["rows"]) == 271728, "base T74 row count, no ten-copy lift")
    dispatch = {(stage, replica): tag for stage, replica, tag in dispatch_rows}
    require(len(dispatch) == 666 and set(dispatch) == {tuple(row) for row in order}, "dispatch domain")
    require(set(providers) == {"extra", "gauge44"}, "actual two-provider domain")
    require(all(len(provider["widths"]) == 408 for provider in providers.values()), "actual 408 helpers")
    recipes = phases["recipes"]
    require(len(recipes) == 112 and [row["port"] for row in recipes] == list(range(112)),
            "explicit recipe-per-port mapping")
    return {"order": order, "dispatch": dispatch, "rows": fill["rows"],
            "providers": providers, "plan": plan, "template": template,
            "recipes": recipes, "pins": pins, "algebra": load_retained(root)}
