#!/usr/bin/env python3
"""Compose six disjoint three-helper cycles on PR3354 and replay the full invoice.

Adapted from Nick Petalas's PR3354 reconstruction and admission; Apache-2.0.
New composition prepared with substantial OpenAI Codex assistance."""

import argparse
import gzip
import hashlib
import importlib.util
import json
import tarfile
import tempfile
from collections import Counter, defaultdict
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

import replay

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "research/complex-t16-two-stage-cycles/data/OWNERS.json.gz"
SELECTED = "research/complex-t16-rare-pattern-exchanges/data"
CYCLES = (
    (1813, 2979, 650),
    (1814, 2981, 861),
    (1815, 2986, 869),
    (1859, 2993, 1009),
    (1861, 2995, 231),
    (1862, 3002, 260),
)
CYCLE = CYCLES[0]
PREDECESSOR_KAPPA = Fraction("0.001673620586419375")
EXPECTED_KAPPA = Fraction("0.001673626873024029")
ROLE_KEYS = ("stage", "replica", "time", "helper", "width")
PLACE_KEYS = ("owner_replica", "child", "port", "copy", "family")
ROWS = 69120
MAX_BYTES = 32 * 1024 * 1024


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    path = Path(path)
    need(path.stat().st_size <= MAX_BYTES, "input byte budget")
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
    else:
        raw = path.read_bytes()
    need(len(raw) <= MAX_BYTES, "decompressed byte budget")
    return json.loads(raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_sources(main):
    sources = read(PACKAGE / "SOURCES.json")
    need(len(sources["files"]) <= 100, "source count budget")
    for item in sources["files"]:
        if item["usage"] == "input":
            need(
                replay.sha(main / item["path"]) == item["sha256"],
                "changed input: " + item["path"],
            )
    export = read(PACKAGE / "SOURCE-EXPORT.json")
    need(len(export["retained_files"]) <= 10, "retained source count")
    for name, expected in export["retained_files"].items():
        need(replay.sha(PACKAGE / name) == expected, "changed retained source")
    return export


def predecessor(main, export):
    rows = read(main / BASE)
    patch = read(PACKAGE / "predecessor.patch.json")
    need(len(rows) == ROWS and len(patch) <= 200, "predecessor dimensions")
    indices = [item["index"] for item in patch]
    need(indices == sorted(set(indices)), "patch indices")
    for item in patch:
        index = item["index"]
        need(type(index) is int and 0 <= index < ROWS, "patch index range")  # noqa: E721
        need(rows[index] == item["before"], "patch preimage")
        need(
            all(rows[index][key] == item["after"][key] for key in ROLE_KEYS),
            "patch changes logical role",
        )
        rows[index] = item["after"]
    need(
        digest(rows) == export["predecessor_canonical_sha256"],
        "PR3354 complete owner payload differs",
    )
    return rows


def bin_key(row):
    return row["owner_replica"], row["child"], row["port"]


def cycle(rows, indices=CYCLE):
    need(len(rows) == ROWS, "role count")
    need(len(indices) == 3 and len(set(indices)) == 3, "three distinct roles")
    need(all(type(i) is int and 0 <= i < ROWS for i in indices), "cycle indices")  # noqa: E721
    affected = {bin_key(rows[i]) for i in indices}
    need(len(affected) == 3, "three distinct bins")
    result = [dict(row) for row in rows]
    for position, index in enumerate(indices):
        target = rows[indices[(position + 1) % 3]]
        result[index].update({key: target[key] for key in PLACE_KEYS})
    members = defaultdict(list)
    for index, row in enumerate(result):
        if bin_key(row) in affected:
            members[bin_key(row)].append(index)
    for indices_in_bin in members.values():
        offset = 0
        for index in sorted(indices_in_bin, key=lambda i: (result[i]["offset"], i)):
            result[index]["offset"] = offset
            offset += result[index]["width"]
    need(
        all(all(a[key] == b[key] for key in ROLE_KEYS) for a, b in zip(rows, result)),
        "cycle changes logical role",
    )
    return result


def compose(rows, cycles=CYCLES):
    """Apply the declared disjoint cycles without touching PR3354's existing cycle."""
    need(len(cycles) == 6, "six cycles required")
    roles = [i for indices in cycles for i in indices]
    need(len(roles) == 18 and len(set(roles)) == 18, "disjoint cycle roles")
    need(all(type(i) is int and 0 <= i < ROWS for i in roles), "cycle indices")  # noqa: E721
    need(len({bin_key(rows[i]) for i in roles}) == 18, "disjoint cycle bins")
    result = rows
    for indices in cycles:
        result = cycle(result, indices)
    return result


def context(main):
    auditor = load(
        "three_cycle_owners", main / "research/t16-owner-audit-seed67/verify.py"
    )
    word = read(auditor.WORD)
    geometry = auditor.geometry(
        read(main / auditor.TEMPLATE), read(main / auditor.PHASES)
    )
    widths = auditor.word_widths(word)
    local = auditor.as_profile(word["report"]["local_profile"])
    plan = read(main / SELECTED / "PLAN.json")
    return auditor, geometry, widths, local, plan


def audit_map(rows, context_values):
    auditor, geometry, widths, local, plan = context_values
    used = Counter()
    for row in rows:
        used[bin_key(row)] += row["width"]
    spans, _ = auditor.windows(geometry, [tuple(item) for item in plan["order"]])
    idle = Counter()
    for owner, child in spans:
        for port in range(112):
            free = geometry["rank"][child] - used[owner, child, port]
            need(free >= 0, "overfilled bin")
            if free:
                idle[free] += 1
    return auditor.audit(geometry, widths, local, rows, plan, idle, 16)


def prices(main, profile):
    engine = load(
        "three_cycle_price", main / "research/frontier1094-idle-star-ceiling/analyze.py"
    )
    engine.ROOT = main
    engine.ENGINE_ROOT = (
        main / "research/complex-k492-owner-repair/vendor/multicold/engines"
    )
    engines = tuple(
        engine.load_engine(name) for name in ("moment", "base_two_moment", "outer")
    )
    baseline = read(main / "research/community-frontier1094-audit/ASSEMBLY.json")
    return tuple(
        engine.price(Counter(profile), bad, baseline, engines) for bad in (False, True)
    )


def decimal(value):
    rational = Fraction(value)
    with localcontext() as context_value:
        context_value.prec = 70
        return str(Decimal(rational.numerator) / Decimal(rational.denominator))


def same_invoice(old, new):
    need(isinstance(old, dict) and isinstance(new, dict), "invoice objects")
    identifiers = {"template_sha256", "owner_audit_sha256", "controller_audit_sha256"}
    before = {key: value for key, value in old.items() if key not in identifiers}
    after = {key: value for key, value in new.items() if key not in identifiers}
    need(canonical(before) == canonical(after), "complete typed invoice changed")


def check_typed_invoice(main, new):
    with tarfile.open(main / replay.SELECTED) as archive:
        member = archive.getmember(replay.INVOICE)
        need(member.isfile() and member.size <= MAX_BYTES, "invoice input budget")
        with archive.extractfile(member) as stream:
            old = json.load(stream)
    same_invoice(old, new)


def write_data(main, target, rows, audit, native, conservative):
    data = target / "data"
    data.mkdir(parents=True)
    container = gzip.compress(canonical(rows), mtime=0)
    need(json.loads(gzip.decompress(container)) == rows, "container round trip")
    (data / "OWNERS.json.gz").write_bytes(container)
    owner_hash = replay.sha(data / "OWNERS.json.gz")
    profile = {str(k): v for k, v in sorted(audit["profile"].items())}
    plan = read(main / SELECTED / "PLAN.json")
    plan.update(
        profile=profile,
        assignment_sha256=owner_hash,
        assignment_content_sha256=digest(rows),
    )
    plan["replica_lift"]["owners_file_sha256"] = owner_hash
    (data / "PLAN.json").write_text(json.dumps(plan, indent=2) + "\n")
    spec = read(main / SELECTED / "SPEC.json")
    spec["data"] = {
        "owners_sha256": owner_hash,
        "plan_sha256": replay.sha(data / "PLAN.json"),
    }
    spec["expected"].update(
        complex_lower=native["endpoint"],
        conservative_complex_lower=conservative["endpoint"],
        kappa=native["kappa"],
        kappa_decimal=decimal(native["kappa"]),
        conservative_kappa_decimal=decimal(conservative["kappa"]),
        cross_replica_helper_roles=audit["cross_replica_roles"],
        idle_remainders=sum(audit["idle"].values()),
        idle_remainder_profile={str(k): v for k, v in sorted(audit["idle"].items())},
        global_profile=profile,
        actual_73column_sigmas=10008,
    )
    (data / "SPEC.json").write_text(json.dumps(spec, indent=2) + "\n")


def prepare(main, work):
    export = check_sources(main)
    old = predecessor(main, export)
    new = compose(old)
    ctx = context(main)
    before, after = audit_map(old, ctx), audit_map(new, ctx)
    delta = Counter(after["idle"])
    delta.subtract(before["idle"])
    need({k: v for k, v in delta.items() if v} == {1: -6, 2: -6, 3: 6}, "idle delta")
    need(after["rank_mass"] == before["rank_mass"] == 1041408, "rank mass")
    need(sum(bin_key(a) != bin_key(b) for a, b in zip(old, new)) == 18, "relocations")
    native, conservative = prices(main, after["profile"])
    need(
        Fraction(native["kappa"]) == EXPECTED_KAPPA > PREDECESSOR_KAPPA,
        "exact kappa gain",
    )
    target = work / "candidate"
    write_data(main, target, new, after, native, conservative)
    auditor, geometry, widths, local, plan = ctx
    controls = auditor.controls(
        geometry, widths, local, new, plan, Counter(after["idle"]), 16
    )
    need(len(controls) == 11, "owner controls")
    return new, after, native, conservative, local, target


def run(main, work, write=False):
    new, audit, native, conservative, local, target = prepare(main, work)
    admission = work / "admission"
    admission.mkdir()
    strict, invoice = replay.run(main, target, admission)
    check_typed_invoice(main, invoice)
    profile = {str(k): v for k, v in sorted(audit["profile"].items())}
    need(
        strict["complex_profile"] == profile and strict["kappa"] == native["kappa"],
        "strict score/profile differs",
    )
    need(strict["actual_73_axis_charts"] == 10008, "actual chart count")
    ceiling = load(
        "three_cycle_ceiling", main / "research/complex-local-word-ceiling/ceiling.py"
    )
    _, high = ceiling.ceiling(local, 73, 896, 9, 64)
    cap = high / (1 + high)
    result = {
        "status": "PASS_T16_COMPOSED_CYCLES",
        "cycles": [list(indices) for indices in CYCLES],
        "owner_canonical_sha256": digest(new),
        "profile": profile,
        "idle": audit["idle"],
        "kappa": native["kappa"],
        "complex_lower": native["endpoint"],
        "bit_lower": strict["bit_lower"],
        "conservative": conservative,
        "gain_vs_pr3354": str(Fraction(native["kappa"]) - PREDECESSOR_KAPPA),
        "gain_vs_selected": str(
            Fraction(native["kappa"]) - Fraction("0.001672660197076918")
        ),
        "roles": audit["roles"],
        "rank_mass": audit["rank_mass"],
        "deficit": audit["deficit"],
        "actual_charts": 10008,
        "owner_controls": 11,
        "strict_controls": strict["controls"],
        "complete_invoice_unchanged": True,
        "prefix_bits": invoice["global_prefix_bits"],
        "row_coefficient": invoice["finite"]["physical_row_coefficient"],
        "packing_kappa_cap": str(cap),
        "fraction_of_kappa_cap": str(Fraction(native["kappa"]) / cap),
        "scope": "Conditional selected-word finite composition; all inherited selected assumptions remain.",
    }
    normalized = json.loads(json.dumps(result))
    if write:
        (PACKAGE / "RESULT.json").write_text(json.dumps(normalized, indent=2) + "\n")
    else:
        need(
            canonical(normalized) == canonical(read(PACKAGE / "RESULT.json")),
            "typed committed result differs",
        )
    print(result["status"], decimal(result["kappa"]), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", type=Path, default=ROOT)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.work:
        args.work.mkdir(parents=True, exist_ok=False)
        run(args.main.resolve(), args.work.resolve(), args.write)
    else:
        with tempfile.TemporaryDirectory(prefix="t16-composed-cycles-") as directory:
            run(args.main.resolve(), Path(directory), args.write)


if __name__ == "__main__":
    main()
