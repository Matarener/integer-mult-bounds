#!/usr/bin/env python3
"""Reconstruct a two-role T16 packing improvement and run unchanged full admission."""

import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path

import replay
import support_checks
import swap

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "research/complex-t16-two-stage-cycles/data/OWNERS.json.gz"
SELECTED = "research/complex-t16-rare-pattern-exchanges/data/"
MAX_FILE = 32 * 1024 * 1024
MAX_JSON = 64 * 1024 * 1024
SELECTED_KAPPA = Fraction("0.001672660197076918")
PREDECESSOR_KAPPA = Fraction("0.001673618490895016")
EXPECTED_KAPPA = Fraction("0.001673619538656538")


def read_json(path):
    path = Path(path)
    swap.need(path.stat().st_size <= MAX_FILE, "input byte budget: " + str(path))
    data = path.read_bytes()
    if path.suffix == ".gz":
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
            data = stream.read(MAX_JSON + 1)
    swap.need(len(data) <= MAX_JSON, "JSON byte budget")
    return json.loads(data)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_sources(main, package):
    sources = read_json(package / "SOURCES.json")
    swap.need(len(sources["files"]) <= 400, "source count budget")
    for item in sources["files"]:
        if item["usage"] == "input":
            swap.need(
                replay.sha(main / item["path"]) == item["sha256"],
                "changed source input: " + item["path"],
            )
    export = read_json(package / "SOURCE-EXPORT.json")
    for item in export["files"]:
        swap.need(
            replay.sha(package / item["path"]) == item["sha256"],
            "changed predecessor export",
        )
    return export


def predecessor(main, package, export):
    rows = read_json(main / BASE)
    diff = read_json(package / "predecessor/DIFF-vs-predecessor.json")
    swap.need(len(diff) == 163, "wrong predecessor delta size")
    indices = [item["index"] for item in diff]
    swap.need(indices == sorted(set(indices)), "predecessor delta order")
    for item in diff:
        index = item["index"]
        swap.need(
            0 <= index < swap.ROWS and rows[index] == item["before"],
            "predecessor delta preimage",
        )
        rows[index] = item["after"]
    swap.validate_rows(rows)
    swap.need(
        hashlib.sha256(canonical(rows)).hexdigest()
        == export["predecessor_canonical_sha256"],
        "PR3308 complete payload differs",
    )
    return rows


def geometry(main):
    auditor = load_module(
        "t16_swap_source_auditor", main / "research/t16-owner-audit-seed67/verify.py"
    )
    word = read_json(auditor.WORD)
    geo = auditor.geometry(
        read_json(main / auditor.TEMPLATE), read_json(main / auditor.PHASES)
    )
    widths = auditor.word_widths(word)
    local = auditor.as_profile(word["report"]["local_profile"])
    return auditor, geo, widths, local


def prices(main, profile):
    engine = load_module(
        "t16_swap_price", main / "research/frontier1094-idle-star-ceiling/analyze.py"
    )
    engine.ROOT = main
    engine.ENGINE_ROOT = (
        main / "research/complex-k492-owner-repair/vendor/multicold/engines"
    )
    engines = tuple(
        engine.load_engine(name) for name in ("moment", "base_two_moment", "outer")
    )
    baseline = read_json(main / "research/community-frontier1094-audit/ASSEMBLY.json")
    return (
        engine.price(Counter(profile), False, baseline, engines),
        engine.price(Counter(profile), True, baseline, engines),
    )


def reconstruct(main, package):
    export = check_sources(main, package)
    old = predecessor(main, package, export)
    auditor, geo, widths, local = geometry(main)
    selected_plan = read_json(main / (SELECTED + "PLAN.json"))
    enumeration = swap.census(old, geo, selected_plan, auditor)
    swap.need(
        enumeration["winners"] and enumeration["winners"][-1] == [1863, 1514],
        "swap nomination changed",
    )
    new = swap.exchange(old, 1863, 1514)
    swap.need(
        new == read_json(package / "data/OWNERS.json.gz"),
        "candidate map differs from two-role construction",
    )
    plan, spec = (
        read_json(package / "data/PLAN.json"),
        read_json(package / "data/SPEC.json"),
    )
    idle = swap.idle_profile(new, geo, plan, auditor)
    audit = auditor.audit(geo, widths, local, new, plan, idle, 16)
    controls = auditor.controls(geo, widths, local, new, plan, idle, 16)
    swap.need(len(controls) == 11, "missing independent owner controls")
    native, conservative = prices(main, audit["profile"])
    swap.need(
        Fraction(native["kappa"])
        == EXPECTED_KAPPA
        > PREDECESSOR_KAPPA
        > SELECTED_KAPPA,
        "no strict exact headline gain",
    )
    expected_plan, expected_spec = swap.derive_data(
        new,
        selected_plan,
        read_json(main / (SELECTED + "SPEC.json")),
        audit,
        native,
        conservative,
        replay.sha(package / "data/OWNERS.json.gz"),
        10008,
    )
    swap.need(expected_plan == plan, "regenerated PLAN differs")
    expected_spec["data"] = {
        "owners_sha256": replay.sha(package / "data/OWNERS.json.gz"),
        "plan_sha256": replay.sha(package / "data/PLAN.json"),
    }
    swap.need(expected_spec == spec, "regenerated SPEC differs")
    return audit, enumeration, native, conservative, local


def summarize(main, package, reconstructed, strict, invoice):
    audit, enumeration, native, conservative, local = reconstructed
    swap.need(
        strict["complex_profile"] == {str(k): v for k, v in audit["profile"].items()},
        "strict profile mismatch",
    )
    swap.need(
        strict["kappa"] == native["kappa"]
        and strict["complex_lower"] == native["endpoint"],
        "strict score mismatch",
    )
    swap.need(strict["actual_73_axis_charts"] == 10008, "actual chart count changed")
    ceiling = load_module(
        "t16_swap_ceiling", main / "research/complex-local-word-ceiling/ceiling.py"
    )
    low, high = ceiling.ceiling(local, 73, 896, 9, 64)
    swap.need(high == Fraction(1690054109089, 10**15), "fixed-word ceiling differs")
    cap = high / (1 + high)
    return {
        "status": "PASS_T16_TWO_ROLE_MOMENT_SWAP",
        "kappa": native["kappa"],
        "kappa_decimal": native["kappa_decimal"],
        "complex_lower": native["endpoint"],
        "bit_lower": strict["bit_lower"],
        "gain_vs_selected": str(EXPECTED_KAPPA - SELECTED_KAPPA),
        "gain_vs_pr3308": str(EXPECTED_KAPPA - PREDECESSOR_KAPPA),
        "conservative_kappa": conservative["kappa"],
        "profile": audit["profile"],
        "idle": audit["idle"],
        "census": enumeration,
        "roles": audit["roles"],
        "rank_mass": audit["rank_mass"],
        "deficit": audit["deficit"],
        "independent_controls": 11,
        "strict_controls": strict["controls"],
        "actual_charts": 10008,
        "complete_invoice_unchanged": True,
        "prefix_bits": invoice["global_prefix_bits"],
        "row_coefficient": invoice["finite"]["physical_row_coefficient"],
        "packing_a_bracket": [str(low), str(high)],
        "packing_kappa_cap": str(cap),
        "fraction_of_kappa_cap": str(EXPECTED_KAPPA / cap),
        "source_overlay": {
            name: replay.sha(package / "data" / name)
            for name in ("OWNERS.json.gz", "PLAN.json", "SPEC.json")
        },
        "scope": "Conditional finite selected-word T16 admission with source-bound native ancestry reuse; inherited selected assumptions remain.",
    }


def run(main, package, work, write=False):
    reconstructed = reconstruct(main, package)
    strict, invoice = replay.run(main, package, work)
    support_checks.run(main, package, work)
    result = summarize(main, package, reconstructed, strict, invoice)
    normalized = json.loads(json.dumps(result))
    if write:
        (package / "RESULT.json").write_text(json.dumps(normalized, indent=2) + "\n")
    else:
        swap.need(
            normalized == read_json(package / "RESULT.json"),
            "result differs from committed certificate",
        )
    print(
        result["status"],
        result["kappa_decimal"],
        "complete_invoice_unchanged",
        flush=True,
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", type=Path, default=ROOT)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.work:
        args.work.mkdir(parents=True, exist_ok=False)
        run(args.main.resolve(), PACKAGE, args.work.resolve(), args.write)
    else:
        with tempfile.TemporaryDirectory(prefix="t16-two-role-") as directory:
            run(args.main.resolve(), PACKAGE, Path(directory), args.write)


if __name__ == "__main__":
    main()
