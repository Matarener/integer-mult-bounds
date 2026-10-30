#!/usr/bin/env python3
"""Source-bound QQ16 budget gap; unchanged-idle screens are conditional."""

import argparse
import gzip
import hashlib
import io
import json
import stat
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST_HASH = "11697814cc7d28f23843035cd0dd6167364275249644dfbb8668274c86f4ad93"
PREFIX = "research/"
INPUTS = (
    PREFIX + "community-frontier1094-audit/ASSEMBLY.json",
    PREFIX + "community-frontier1094-audit/INDEPENDENT1094.json",
    PREFIX + "complex-local-word-ceiling/README.md",
    PREFIX + "joint-query/certificate.json.gz",
    PREFIX + "qq16-entry-frame-tariff/README.md",
    PREFIX + "qq16-entry-frame-tariff/RESULT.json",
    PREFIX + "qq16-line-normalized-decoder/README.md",
    PREFIX + "qq16-line-normalized-decoder/WORD.json",
)
CASES = ("F_0", "B_1_2", "F_2", "B_3_4", "F_4", "B_5_6", "F_6", "B_7_8", "F_8")
CORE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def pairs(items):
    need(len(items) <= 20000, "JSON object capacity")
    result = dict(items)
    need(len(result) == len(items), "duplicate JSON key")
    return result


def parse(raw):
    return json.loads(raw, object_pairs_hook=pairs)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def regular(path, limit=16_000_000):
    relative = path.relative_to(ROOT)
    current = ROOT
    for part in relative.parts:
        current = current / part
        need(not stat.S_ISLNK(current.lstat().st_mode), "source symlink")
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_size <= limit, "regular file/capacity")
    return path.read_bytes()


def sources():
    raw = regular(HERE / "SOURCES.json", 16384)
    need(hashlib.sha256(raw).hexdigest() == MANIFEST_HASH, "source manifest binding")
    manifest = parse(raw)
    need(
        type(manifest["schema_version"]) is int and manifest["schema_version"] == 1,
        "schema type",
    )
    rows = manifest["files"]
    expected = dict.fromkeys(INPUTS, "input")
    expected.update(
        {
            "certificates/selected-result.json": "provenance",
            "docs/research/agent-task-catalog.json": "provenance",
        }
    )
    need(len(rows) == len(expected), "source inventory size")
    need({r["path"]: r["usage"] for r in rows} == expected, "source usage/inventory")
    loaded = {}
    for row in rows:
        if row["usage"] == "input":
            raw = regular(ROOT / row["path"])
            need(
                hashlib.sha256(raw).hexdigest() == row["sha256"],
                "input hash " + row["path"],
            )
            loaded[row["path"]] = raw
    return loaded


def histogram(value):
    need(type(value) is dict and 0 < len(value) <= 73, "histogram shape")
    result = {}
    for rank, count in value.items():
        need(type(rank) is str and rank.isdecimal(), "rank type")
        r = int(rank)
        need(0 < r < 73 and str(r) == rank, "rank domain")
        need(type(count) is int and count > 0, "count type/domain")
        result[r] = count
    return result


def mass(profile):
    return sum(rank * count for rank, count in profile.items())


def producer(raw):
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        decoded = stream.read(12_000_001)
    need(len(decoded) <= 12_000_000, "expanded certificate capacity")
    data = parse(decoded)
    for side in ("forward", "backward"):
        word = data["core_words"][side]
        need(len(word) == 25155, "core event count")
        profile = Counter(e[5] for e in word if e[0] == "climb")
        need(dict(profile) == CORE, "literal clean-J profile")
    totals = Counter()
    for name in CASES:
        word = data["programs"][name]
        need(len(word) <= 600, "producer case capacity")
        flat = []
        for event in word:
            body = event[2] if event[0] in ("cover_sweep", "private_sweep") else [event]
            need(len(body) <= 2000, "producer body capacity")
            need(
                all(e[0] not in ("cover_sweep", "private_sweep") for e in body),
                "nested sweep",
            )
            flat.extend(body)
        need(len(flat) <= 4000, "flattened producer capacity")
        count = Counter(e[0] for e in flat)
        expected = 8 if name.startswith("F") else 24
        need(
            count["native_line"] == expected and count["retained_core"] == 1,
            "producer invoice",
        )
        totals.update(count)
    return dict(totals)


def selected(assembly, independent):
    profile = histogram(assembly["complex_profile"])
    idle = histogram(independent["owner"]["idle"])
    need(
        profile == histogram(independent["owner"]["profile"]),
        "selected profile binding",
    )
    price = independent["price"]
    need(type(price["calls"]) is int and price["calls"] == 144, "call count")
    need(type(price["live"]) is int and price["live"] == 14336, "live families")
    need(mass(profile) == 72 * 14336 + 64 * 144, "selected coverage law")
    local = CORE | {8: 8}
    for rank in set(profile) | set(idle) | set(local):
        need(
            profile.get(rank, 0) - idle.get(rank, 0) == 144 * local.get(rank, 0),
            "local/core split",
        )
    need(mass(idle) == 16 * 14814, "idle mass per replica")
    return {
        "kappa": assembly["kappa"],
        "complex_a": assembly["complex_lower"],
        "bit_a": assembly["bit_lower"],
        "profile": assembly["complex_profile"],
        "live_families": 14336,
        "calls": 144,
        "replicas": 16,
    }


def budget(adapter_mass, added=472, credit=0):
    need(type(adapter_mass) is int and 0 <= adapter_mass <= 10000, "adapter mass")
    need(type(added) is int and 0 <= added <= 10000, "added mass")
    need(type(credit) is int and 0 <= credit <= 14814, "idle mass credit")
    total = 72 * 896 + added + adapter_mass - credit
    parent = 73 * 896
    return {
        "paid_mass": total,
        "parent_mass": parent,
        "mass_margin": parent - total,
        "moment_at_zero": str(Q(total, parent)),
        "conditional_fixed_credit_rejects_all_a_ge_zero": total >= parent,
        "hypothetical_credit": credit,
        "necessary_integer_credit_for_strict_mass_gate": max(
            0, added + adapter_mass - 896 + 1
        ),
    }


def report():
    loaded = sources()
    baseline = selected(parse(loaded[INPUTS[0]]), parse(loaded[INPUTS[1]]))
    produced = producer(loaded[INPUTS[3]])
    word = parse(loaded[INPUTS[7]])
    need(type(word) is list and len(word) == 3823, "decoder word shape")
    counted = dict(Counter(e[0] for e in word))
    need(counted["line"] == 336 and counted["map"] == 464, "decoder native invoice")
    tariff = parse(loaded[INPUTS[5]])
    rows = {}
    for label, key, expected in (
        ("common_FL", "common_F_L", 1792),
        ("F0_gauges", "F0", 1904),
        ("entry_gauges", "entry", 3696),
    ):
        profile = histogram(tariff[key + "_adapter_histogram"])
        need(
            mass(profile) == expected and sum(profile.values()) == 224, "adapter tariff"
        )
        rows[label] = {
            "adapter_profile": {str(r): n for r, n in profile.items()},
            "adapter_mass": expected,
            **budget(expected),
        }
    need(produced["native_line"] == 136, "nine-stage added lines")
    need(
        all(row["mass_margin"] < 0 for row in rows.values()),
        "expected strict rejection",
    )
    return {
        "status": "PASS_QQ16_SEPARATE_CONSUMER_ADMISSION_GAP_NO_NEW_KAPPA",
        "baseline": baseline,
        "core_profile": {str(r): n for r, n in CORE.items()},
        "core_mass_per_call": mass(CORE),
        "producer_added_events": produced,
        "decoder_events": counted,
        "one_decoder_optimistic_delta": {"1": 472, "8": -72},
        "conditional_unchanged_idle_before_adapter": budget(0),
        "conditional_unchanged_idle_endpoints": rows,
        "free_producer_decoder_common_FL": budget(1792, added=0),
        "mass_gate_boundary_controls": {
            "equality": budget(1792, credit=1368),
            "strict_mass_only": budget(1792, credit=1369),
        },
        "actual_idle_credit": None,
        "actual_complete_moment": None,
        "global_obstruction_proved": False,
        "global_closure": (
            "unknown; one decoder and all first-pair cut availability granted"
        ),
        "physical_bill": (
            "unknown; no actual source/owner continuation or displaced-idle receipt"
        ),
        "kappa_status": "no new kappa; actual admissible a interval unknown",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = report()
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        expected = parse(regular(HERE / "RESULT.json", 100000))
        need(canonical(result) == canonical(expected), "typed receipt mismatch")
        print(result["status"])


if __name__ == "__main__":
    main()
