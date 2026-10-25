"""Reconstruct neutral buffer routes, a concentration, and causal augmenting paths.

Retains PR3354/3359/3366/3375/3381 reconstruction by Nick Petalas and Pierre (hexapode)."""

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
BLOCKS = (7,)
FINAL_SHA256 = "8e5940efdf9026ec41200e6dc7132e3736f2d63f84d5e4e24d82d8db03967f4e"
PREDECESSOR_KAPPA = Fraction("0.001673636244951726")
EXPECTED_KAPPA = Fraction("0.001673648366462479")
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
    need(len(export["retained_files"]) <= 16, "retained source count")
    for name, expected in export["retained_files"].items():
        need(replay.sha(PACKAGE / name) == expected, "changed retained source")
    prior = read(PACKAGE / "predecessor/RESULT.json")
    need(
        export["predecessor_canonical_sha256"] == prior["owner_canonical_sha256"],
        "retained PR3381 payload binding",
    )
    need(Fraction(prior["kappa"]) == PREDECESSOR_KAPPA, "retained PR3381 price binding")
    return export


def predecessor(main, export):
    retained = load("retained_3381", PACKAGE / "predecessor/verify.py")
    retained.PACKAGE = PACKAGE / "predecessor"
    retained.ROOT = main
    binding = retained.read(retained.PACKAGE / "SOURCE-EXPORT.json")
    old = retained.predecessor(main, binding)
    rows, _before, _after, plan = retained.construct(old, retained.context(main))
    need(digest(rows) == export["predecessor_canonical_sha256"], "retained PR3381 owner payload")
    return rows, plan


def bin_key(row):
    return row["owner_replica"], row["child"], row["port"]


def rotate(rows, indices):
    need(len(rows) == ROWS, "role count")
    need(
        len(indices) in (2, 3) and len(set(indices)) == len(indices),
        "two or three distinct roles",
    )
    need(all(type(i) is int and 0 <= i < ROWS for i in indices), "cycle indices")  # noqa: E721 - reject bool
    affected = {bin_key(rows[i]) for i in indices}
    need(len(affected) == len(indices), "distinct bins")
    result = [dict(row) for row in rows]
    for position, index in enumerate(indices):
        target = rows[indices[(position + 1) % len(indices)]]
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
        "rotation changes logical role",
    )
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
    old, new = json.loads(json.dumps(old)), json.loads(json.dumps(new))
    for invoice in (old, new):
        calls = invoice.get("selected_calls")
        need(isinstance(calls, list) and len(calls) == 144, "invoice call count")
        need(all(type(c["stage"]) is int and type(c["replica"]) is int for c in calls), "invoice integer calls")  # noqa: E721
        need({(c["stage"], c["replica"]) for c in calls} == {(s, r) for s in range(9) for r in range(16)}, "invoice call inventory")
        invoice["selected_calls"] = sorted(calls, key=lambda call: (call["stage"], call["replica"]))
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


def write_data(main, target, rows, audit, native, conservative, final_plan):
    data = target / "data"
    data.mkdir(parents=True)
    container = gzip.compress(canonical(rows), mtime=0)
    need(json.loads(gzip.decompress(container)) == rows, "container round trip")
    (data / "OWNERS.json.gz").write_bytes(container)
    owner_hash = replay.sha(data / "OWNERS.json.gz")
    profile = {str(k): v for k, v in sorted(audit["profile"].items())}
    plan = json.loads(json.dumps(final_plan))
    plan.update(
        profile=profile,
        assignment_sha256=owner_hash,
        assignment_content_sha256=digest(rows),
    )
    plan["replica_lift"]["owners_file_sha256"] = owner_hash
    at = {tuple(call): time for time, call in enumerate(plan["order"])}
    for field in ("provider_calls", "per_call_widths"):
        for call in plan[field]:
            if "time" in call:
                call["time"] = at[call["stage"], call["replica"]]
        plan[field].sort(key=lambda call: at[call["stage"], call["replica"]])
    with tempfile.TemporaryDirectory(prefix="reordered-parent-") as directory:
        source = replay.extract_source(main, Path(directory))
        builder = load("reordered_parent", source / "t16/build_parent.py")
        auditor = context(main)[0]
        parent = builder.lift_parent(read(main / auditor.TEMPLATE))
        windows, schedule = builder.actual_windows(parent, plan["order"])
        need(windows == plan["windows"], "independent changed-order windows")
        plan["replica_lift"]["schedule_content_sha256"] = digest(schedule)
    (data / "PLAN.json").write_text(json.dumps(plan, indent=2) + "\n")
    spec = read(main / SELECTED / "SPEC.json")
    spec["call_order"] = plan["order"]
    spec["dispatch"].sort(key=lambda call: at[tuple(call[:2])])
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
        actual_73column_sigmas=10017,
    )
    (data / "SPEC.json").write_text(json.dumps(spec, indent=2) + "\n")


def validate_order(order):
    need(len(order) == 144, "order length")
    need(all(len(call) == 2 and all(type(x) is int for x in call) for call in order), "integer call labels")  # noqa: E721
    need({tuple(call) for call in order} == {(s, r) for s in range(9) for r in range(16)}, "complete call inventory")
    need(all([s for s, r in order if r == replica] == list(range(9)) for replica in range(16)), "replica causal order")
    need(all(order[2*k+1] == [order[2*k][0], order[2*k][1]+8] and order[2*k][1] < 8 for k in range(72)), "paired order")


def change_order(rows, ctx, block):
    need(type(block) is int and 0 <= block < 71, "block index")  # noqa: E721
    auditor, geometry, widths, local, plan = ctx
    order = [list(call) for call in plan["order"]]
    start = 2 * block
    order[start:start+4] = order[start+2:start+4] + order[start:start+2]
    validate_order(order)
    spans, positions = auditor.windows(geometry, [tuple(call) for call in order])
    at = {tuple(call): time for time, call in enumerate(order)}
    result = [dict(row, time=at[row["stage"], row["replica"]]) for row in rows]
    updated = dict(plan, order=order, windows={
        f"{owner},{child}": [geometry["rank"][child], [time for time, call in enumerate(order)
            if lo < positions[tuple(call)] < hi]]
        for (owner, child), (lo, hi) in spans.items()
    })
    return result, (auditor, geometry, widths, local, updated)


def apply_moves(rows, moves, geometry, sort_after):
    need(type(sort_after) is bool, "sort flag")  # noqa: E721 - exact protocol type
    parsed = {}
    for raw, destination in moves.items():
        index = int(raw)
        need(str(index) == raw and 0 <= index < ROWS, "move index")
        need(len(destination) == 3 and all(type(x) is int for x in destination), "move coordinates")  # noqa: E721
        owner, child, port = destination
        need(0 <= owner < 16 and child in geometry["rank"] and 0 <= port < 112, "move range")
        parsed[index] = tuple(destination)
    result = [dict(row) for row in rows]
    affected = set()
    for index, destination in parsed.items():
        owner, child, port = destination
        affected.update((bin_key(rows[index]), destination))
        pair, side = geometry["place"][child]
        result[index].update(owner_replica=owner, child=child, port=port,
                             copy=owner*112+port, family=owner*896+(2*pair+side)*112+port)
    members = defaultdict(list)
    for index, row in enumerate(result):
        if bin_key(row) in affected:
            members[bin_key(row)].append(index)
    for indices in members.values():
        offset = 0
        for index in sorted(indices, key=lambda i: (result[i]["offset"], i)):
            result[index]["offset"] = offset
            offset += result[index]["width"]
    need(all(all(a[key] == b[key] for key in ROLE_KEYS) for a, b in zip(rows, result)), "moves change logical role")
    if sort_after:
        result.sort(key=lambda row: (row["time"], row["helper"]))
    return result


def construct(old, ctx, steps=None):
    steps = read(PACKAGE / "REPAIRS.json")["steps"] if steps is None else steps
    need(len(steps) == 16, "sixteen reconstruction stages")
    before = audit_map(old, ctx)
    rows, previous = old, before
    for number, step in enumerate(steps):
        need(digest(rows) == step["source_canonical_sha256"], "stage source payload")
        need(step["paired_block"] == (7 if number == 12 else None), "reconstruction block")
        if step["paired_block"] is not None:
            rows, ctx = change_order(rows, ctx, step["paired_block"])
        identities = {(r["stage"], r["replica"], r["helper"]): i for i, r in enumerate(rows)}
        need(len(identities) == ROWS, "logical role inventory")
        moves = {}
        for action in step["actions"]:
            identity = action["identity"]
            need(set(identity) == {"stage", "replica", "helper"}, "identity fields")
            need(all(type(value) is int for value in identity.values()), "integer identity")  # noqa: E721
            key = tuple(identity[field] for field in ("stage", "replica", "helper"))
            need(key in identities, "unknown logical role")
            index = identities[key]
            need(str(index) not in moves, "repeated logical role")
            need(type(action["width"]) is int and rows[index]["width"] == action["width"], "action width")  # noqa: E721
            need(canonical(list(bin_key(rows[index]))) == canonical(action["from"]), "action preimage")
            moves[str(index)] = action["to"]
        need(0 < len(moves) <= 256, "stage action budget")
        rows = apply_moves(rows, moves, ctx[1], True)
        current = audit_map(rows, ctx)
        delta = Counter(current["idle"])
        delta.subtract(previous["idle"])
        actual = {str(k): v for k, v in delta.items() if v}
        need(canonical(actual) == canonical(step["idle_delta"]), "stage idle delta")
        if number < 9 or number in (11, 12):
            need(not actual, "neutral stage changed profile")
        need(current["rank_mass"] == before["rank_mass"] == 1041408, "rank mass")
        need(digest(rows) == step["target_canonical_sha256"], "stage target payload")
        previous = current
    delta = Counter(previous["idle"])
    delta.subtract(before["idle"])
    need({k: v for k, v in delta.items() if v} == {16: -2, 32: 1}, "complete concentration delta")
    need(digest(rows) == FINAL_SHA256, "final owner payload")
    return rows, before, previous, ctx[4]


def prepare(main, work):
    export = check_sources(main)
    old, old_plan = predecessor(main, export)
    ctx = (*context(main)[:4], old_plan)
    new, before, after, final_plan = construct(old, ctx)
    old_native, _ = prices(main, before["profile"])
    need(
        Fraction(old_native["kappa"]) == PREDECESSOR_KAPPA,
        "predecessor exact price differs",
    )
    native, conservative = prices(main, after["profile"])
    need(
        Fraction(native["kappa"]) == EXPECTED_KAPPA > PREDECESSOR_KAPPA,
        "exact kappa gain",
    )
    target = work / "candidate"
    write_data(main, target, new, after, native, conservative, final_plan)
    auditor, geometry, widths, local, _plan = ctx
    plan = final_plan
    controls = auditor.controls(
        geometry, widths, local, new, plan, Counter(after["idle"]), 16
    )
    need(len(controls) == 11, "owner controls")
    return new, after, native, conservative, local, target


def result_record(main, new, audit, native, conservative, local, strict, invoice):
    profile = {str(k): v for k, v in sorted(audit["profile"].items())}
    need(
        strict["complex_profile"] == profile and strict["kappa"] == native["kappa"],
        "strict score/profile differs",
    )
    need(strict["actual_73_axis_charts"] == 10017, "actual chart count")
    ceiling = load(
        "three_cycle_ceiling", main / "research/complex-local-word-ceiling/ceiling.py"
    )
    _, high = ceiling.ceiling(local, 73, 896, 9, 64)
    cap = high / (1 + high)
    return {
        "status": "PASS_T16_BUFFER_CONCENTRATION",
        "paired_block_swaps": list(BLOCKS),
        "owner_canonical_sha256": digest(new),
        "profile": profile,
        "idle": audit["idle"],
        "kappa": native["kappa"],
        "complex_lower": native["endpoint"],
        "bit_lower": strict["bit_lower"],
        "conservative": conservative,
        "gain_vs_pr3381": str(Fraction(native["kappa"]) - PREDECESSOR_KAPPA),
        "gain_vs_selected": str(
            Fraction(native["kappa"]) - Fraction("0.001672660197076918")
        ),
        "roles": audit["roles"],
        "rank_mass": audit["rank_mass"],
        "deficit": audit["deficit"],
        "actual_charts": 10017,
        "owner_controls": 11,
        "strict_controls": strict["controls"],
        "complete_invoice_unchanged": True,
        "prefix_bits": invoice["global_prefix_bits"],
        "row_coefficient": invoice["finite"]["physical_row_coefficient"],
        "packing_kappa_cap": str(cap),
        "fraction_of_kappa_cap": str(Fraction(native["kappa"]) / cap),
        "scope": "Conditional selected-word finite composition; all inherited selected assumptions remain.",
    }


def run(main, work, write=False):
    new, audit, native, conservative, local, target = prepare(main, work)
    admission = work / "admission"
    admission.mkdir()
    strict, invoice = replay.run(main, target, admission)
    check_typed_invoice(main, invoice)
    result = result_record(
        main, new, audit, native, conservative, local, strict, invoice
    )
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
        with tempfile.TemporaryDirectory(prefix="t16-buffer-concentration-") as directory:
            run(args.main.resolve(), Path(directory), args.write)


if __name__ == "__main__":
    main()
