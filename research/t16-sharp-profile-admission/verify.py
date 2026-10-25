"""Admit PR3403's sharp near-selected T16 map through the unchanged controller."""

import argparse
import copy
import gzip
import hashlib
import importlib.util
import io
import json
import sys
import tarfile
import tempfile
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
import replay

SELECTED = "research/complex-t16-rare-pattern-exchanges/data/"
IDLE = {1: 2431, 17: 1, 48: 4887}
KAPPA = Fraction("0.001674088611862992")
MAX_FILE = 32 * 1024 * 1024


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    path = Path(path)
    need(path.is_file() and not path.is_symlink(), "regular input file")
    need(path.stat().st_size <= MAX_FILE, "input byte budget")
    data = path.read_bytes()
    if path.suffix == ".gz":
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
            data = stream.read(64 * 1024 * 1024 + 1)
    need(len(data) <= 64 * 1024 * 1024, "decoded byte budget")
    return json.loads(data, object_pairs_hook=unique_object)


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "module loader")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_sources(main, package):
    pins = read_json(package / "SOURCES.json")["files"]
    need(len(pins) <= 64, "source count bound")
    for pin in pins:
        if pin["usage"] != "input":
            continue
        relative = Path(pin["path"])
        need(not relative.is_absolute() and ".." not in relative.parts, "source path")
        path = main / relative
        need(not any(p.is_symlink() for p in (path, *path.parents)), "linked source")
        need(replay.sha(path) == pin["sha256"], "source bytes: " + pin["path"])
    export = read_json(package / "SOURCE-EXPORT.json")
    need(len(export["files"]) == 12, "retained source count")
    for pin in export["files"]:
        path = package / pin["path"]
        need(path.is_relative_to(package) and not path.is_symlink(), "export path")
        need(replay.sha(path) == pin["sha256"], "retained source bytes: " + pin["path"])


def nomination(main, package):
    source = load_module("sharp_t16_attainment", package / "predecessor/verify.py")
    model = source.source_model(*source.sources(main))
    certificate = source.read_json(package / "predecessor/CERTIFICATE.json")
    profile = certificate["profiles"]["old"]
    source.check_certificate(profile, model, IDLE)
    assignments = source.expand(profile, model)
    need(source.check_rows(assignments, model) == IDLE, "nominated idle inventory")
    roles = []
    for time, helper, owner, child, port, offset, width in assignments:
        stage, replica = model.calls[time]
        roles.append(
            {
                "time": time,
                "helper": helper,
                "stage": stage,
                "replica": replica,
                "owner_replica": owner,
                "child": child,
                "port": port,
                "offset": offset,
                "width": width,
                "copy": owner * 112 + port,
                "family": source.family(model, owner, child, port),
            }
        )
    need(
        roles == read_json(package / "data/OWNERS.json.gz"),
        "literal nomination differs",
    )
    return roles


def audit_nomination(main, roles):
    auditor = load_module(
        "sharp_t16_owner_audit", main / "research/t16-owner-audit-seed67/verify.py"
    )
    geometry = auditor.geometry(
        read_json(main / auditor.TEMPLATE), read_json(main / auditor.PHASES)
    )
    word = read_json(auditor.WORD)
    widths = auditor.word_widths(word)
    local = auditor.as_profile(word["report"]["local_profile"])
    plan = read_json(main / (SELECTED + "PLAN.json"))
    audit = auditor.audit(geometry, widths, local, roles, plan, IDLE, 16)
    controls = auditor.controls(geometry, widths, local, roles, plan, IDLE, 16)
    need(len(controls) == 11, "independent owner controls")
    return audit, local


def prices(main, profile):
    engine = load_module(
        "sharp_t16_price", main / "research/frontier1094-idle-star-ceiling/analyze.py"
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


def decimal(value):
    rational = Fraction(value)
    with localcontext() as context:
        context.prec = 70
        return str(Decimal(rational.numerator) / Decimal(rational.denominator))


def derive_data(
    roles, original_plan, original_spec, audit, native, conservative, owner_hash
):
    """PR3338's attributed three-file binding recipe, with this map's actual chart count."""
    plan, spec = copy.deepcopy(original_plan), copy.deepcopy(original_spec)
    profile = {str(rank): count for rank, count in sorted(audit["profile"].items())}
    plan.update(profile=profile, assignment_sha256=owner_hash)
    plan["replica_lift"]["owners_file_sha256"] = owner_hash
    plan["assignment_content_sha256"] = hashlib.sha256(canonical(roles)).hexdigest()
    spec["expected"].update(
        complex_lower=native["endpoint"],
        conservative_complex_lower=conservative["endpoint"],
        kappa=native["kappa"],
        kappa_decimal=decimal(native["kappa"]),
        conservative_kappa_decimal=decimal(conservative["kappa"]),
        cross_replica_helper_roles=audit["cross_replica_roles"],
        idle_remainders=sum(IDLE.values()),
        idle_remainder_profile={str(rank): count for rank, count in IDLE.items()},
        global_profile=profile,
        actual_73column_sigmas=9967,
    )
    return plan, spec


def reconstruct(main, package):
    check_sources(main, package)
    roles = nomination(main, package)
    audit, local = audit_nomination(main, roles)
    native, conservative = prices(main, audit["profile"])
    need(Fraction(native["kappa"]) == KAPPA, "conditional price differs")
    plan, spec = derive_data(
        roles,
        read_json(main / (SELECTED + "PLAN.json")),
        read_json(main / (SELECTED + "SPEC.json")),
        audit,
        native,
        conservative,
        replay.sha(package / "data/OWNERS.json.gz"),
    )
    need(plan == read_json(package / "data/PLAN.json"), "derived PLAN differs")
    spec["data"] = {
        "owners_sha256": replay.sha(package / "data/OWNERS.json.gz"),
        "plan_sha256": replay.sha(package / "data/PLAN.json"),
    }
    need(spec == read_json(package / "data/SPEC.json"), "derived SPEC differs")
    return audit, local, native, conservative


def paid_invoice(invoice):
    omitted = {"template_sha256", "owner_audit_sha256", "controller_audit_sha256"}
    return canonical(
        {key: value for key, value in invoice.items() if key not in omitted}
    )


def check_invoice(main, actual):
    with tarfile.open(main / replay.SELECTED) as archive:
        member = archive.getmember(replay.INVOICE)
        need(member.isfile() and member.size <= MAX_FILE, "invoice member budget")
        baseline = json.load(archive.extractfile(member))
    need(
        paid_invoice(baseline) == paid_invoice(actual),
        "complete typed paid invoice differs",
    )
    return hashlib.sha256(paid_invoice(actual)).hexdigest()


def summarize(main, reconstructed, strict, invoice):
    audit, local, native, conservative = reconstructed
    need(
        strict["kappa"] == native["kappa"]
        and strict["complex_lower"] == native["endpoint"],
        "strict/native price binding",
    )
    need(
        strict["complex_profile"] == {str(k): v for k, v in audit["profile"].items()},
        "strict profile binding",
    )
    need(strict["actual_73_axis_charts"] == 9967, "actual chart census")
    ceiling = load_module(
        "sharp_t16_ceiling", main / "research/complex-local-word-ceiling/ceiling.py"
    )
    low, high = ceiling.ceiling(local, 73, 896, 9, 64)
    cap = high / (1 + high)
    selected = Fraction("0.001672660197076918")
    return {
        "status": "PASS_T16_SHARP_PROFILE_ADMISSION",
        "kappa": native["kappa"],
        "kappa_decimal": native["kappa_decimal"],
        "conservative": conservative,
        "complex_lower": native["endpoint"],
        "bit_lower": strict["bit_lower"],
        "gain_vs_selected": str(KAPPA - selected),
        "profile": {str(rank): count for rank, count in audit["profile"].items()},
        "idle": {str(rank): count for rank, count in IDLE.items()},
        "rank_mass": audit["rank_mass"],
        "deficit": audit["deficit"],
        "roles": audit["roles"],
        "calls": audit["calls"],
        "cross_replica_roles": audit["cross_replica_roles"],
        "actual_charts": 9967,
        "prefix_bits": strict["prefix_bits"],
        "charged_prefix_bits": strict["charged_prefix_bits"],
        "row_coefficient": strict["physical_row_coefficient"],
        "strict_controls": strict["controls"],
        "independent_owner_controls": 11,
        "strict_stages": [s["name"] for s in strict["stages"]],
        "typed_paid_invoice_sha256": check_invoice(main, invoice),
        "packing_a_bracket": [str(low), str(high)],
        "packing_kappa_cap": str(cap),
        "fraction_of_kappa_cap": str(KAPPA / cap),
        "scope": "Conditional finite fixed-word T16 admission with authenticated native ancestry reuse; selected result unchanged.",
    }


def run(main, package, work):
    need(__debug__, "full admission requires unchanged predecessor assertions")
    reconstructed = reconstruct(main, package)
    strict, invoice = replay.run(main, package, work)
    result = summarize(main, reconstructed, strict, invoice)
    need(
        canonical(result) == canonical(read_json(package / "RESULT.json")),
        "complete result differs",
    )
    (work / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        result["status"],
        result["kappa_decimal"],
        "complete_typed_paid_invoice_unchanged",
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--work", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.work:
        work = args.work.resolve()
        need(not work.is_relative_to(root), "output must be outside source tree")
        work.mkdir(parents=True, exist_ok=False)
        run(root, PACKAGE, work)
    else:
        with tempfile.TemporaryDirectory(prefix="t16-sharp-admission-") as temporary:
            work = Path(temporary)
            need(not work.is_relative_to(root), "TMPDIR must be outside source tree")
            run(root, PACKAGE, work)


if __name__ == "__main__":
    main()
