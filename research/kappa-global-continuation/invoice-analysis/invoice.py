#!/usr/bin/env python3
"""Source-bound complete invoice screens and a literal inherited allocation.

This certifies finite arithmetic and physical slot reuse, not a new supplier.
The symmetric endpoint's global residual inverse remains an unpaid obligation.
Apache-2.0. Substantial OpenAI Codex assistance, October 2026.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as F
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ENGINE_PATH = REPO / "research/complex-local-word-ceiling/ceiling.py"
TARGET = F("0.001730578437266246818740")
BASE_ROOT = F("0.001730448360207635461740")
BIT_ROOT = F("0.001733427039589844234749")
LOCAL = {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20, 8: 8}
BASE = {1: 7990332, 2: 2349000, 3: 748971, 4: 330480,
        5: 69479, 8: 25920, 32: 1, 48: 137911}
T = 360
CALLS = 9 * T
ZERO_PORT_FIRST_IDLE = {0, 2, 4, 6, 8, 10}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


C = module(ENGINE_PATH, "invoice_exact_ceiling")


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decimal(value, digits=65):
    with localcontext() as ctx:
        ctx.prec = digits
        return str(Decimal(value.numerator) / Decimal(value.denominator))


def interval(lo, hi):
    need(lo <= hi, "interval order")
    return {"rational": [str(lo), str(hi)],
            "decimal": [decimal(lo), decimal(hi)]}


@lru_cache(None)
def cost(rank, dimension, endpoint):
    return C.child_cost(rank, dimension, endpoint)


def weighted(profile, dimension, endpoint):
    lo = hi = F(0)
    for rank, count in profile.items():
        a, b = cost(rank, dimension, endpoint)
        lo += count * (a if count >= 0 else b)
        hi += count * (b if count >= 0 else a)
    return C.down(lo), C.up(hi)


def moment(profile, dimension, productive, endpoint):
    lo, hi = weighted(profile, dimension, endpoint)
    return C.down(lo / productive), C.up(hi / productive)


def root(profile, dimension, productive):
    """Decimal nominates two adjacent decimals; rational arithmetic proves signs."""
    need(sum(r*n for r, n in profile.items()) < dimension*productive,
         "a positive root requires a strict raw deficit")
    with localcontext() as ctx:
        ctx.prec = 85
        terms = []
        for rank, count in profile.items():
            q = F(rank*count, dimension*productive)
            terms.append((Decimal(q.numerator)/q.denominator,
                          (Decimal(dimension)/rank).ln()))
        lo, hi = Decimal(0), Decimal("0.05")
        for _ in range(230):
            x = (lo + hi) / 2
            if sum(p*(x*l).exp() for p, l in terms) < 1:
                lo = x
            else:
                hi = x
        grid = int(lo * 10**24)
    a, b = F(grid, 10**24), F(grid+1, 10**24)
    ma, mb = moment(profile, dimension, productive, a), moment(profile, dimension, productive, b)
    need(ma[1] < 1 < mb[0], "exact root sign bracket")
    return {"decimal": [decimal(a), decimal(b)],
            "rational": [str(a), str(b)],
            "lower_residual": interval(ma[0]-1, ma[1]-1),
            "upper_residual": interval(mb[0]-1, mb[1]-1)}


def tariffs(profile, dimension, productive, endpoint):
    lo, hi = weighted(profile, dimension, endpoint)
    allowance = productive-hi, productive-lo
    result = {"normalized_allowance": interval(*allowance), "by_rank": {}}
    for rank in (1, 8, 9, 16, 48, 64, 72):
        if rank >= dimension:
            continue
        c = cost(rank, dimension, endpoint)
        if allowance[0] >= 0:
            q = allowance[0]/c[1], allowance[1]/c[0]
        else:
            q = allowance[0]/c[0], allowance[1]/c[1]
        result["by_rank"][str(rank)] = interval(*q)
    return result


def test_added(profile, dimension, productive, added, endpoint=TARGET):
    changed = Counter(profile)
    changed.update(added)
    m = moment(changed, dimension, productive, endpoint)
    return {"added": {str(k): str(v) for k, v in added.items()},
            "residual": interval(m[0]-1, m[1]-1),
            "passes_price": m[1] < 1}


def original_screen():
    base = {r: F(n, T) for r, n in BASE.items()}
    need(sum(r*n for r, n in base.items()) == 65088, "baseline raw rank mass")
    got = root(BASE, 73, 896*T)
    need(got["rational"][0] == str(BASE_ROOT), "actual PR3734 root")
    zero = dict(base)
    zero[8] -= 72
    v = moment(BASE, 73, 896*T, TARGET)
    return {"status": "PASS_EXACT_SOURCE_BOUND_BASELINE",
            "root": got, "target_residual": interval(v[0]-1, v[1]-1),
            "zero_repair_tariffs": tariffs(zero, 73, 896, TARGET),
            "zero_repair_controls": {
                "71_H8": test_added(zero, 73, 896, {8: 71}),
                "72_H8": test_added(zero, 73, 896, {8: 72}),
                "8_H72": test_added(zero, 73, 896, {72: 8})},
            "scope": "Unchanged productive denominator and every inherited cost. Batched H72 controls are numerical hypotheses, not emitted native consumers."}


def boundary_family_screen(extra_ports=16):
    """An optimistic lower bound, including unavoidable stated boundary children.

    Each of eight gaps uses either 2z inverse H1 on the active zero-port pair,
    or 224 forward H1 on the original active pair to carry one additional axis.
    The latter option requires further native construction; this is a relaxation.
    """
    need(extra_ports in (8, 16), "specified zero-port normalization alternatives")
    productive = 896 + 8*extra_ports
    result = {}
    for expanded in range(9):
        dimension = 73 + expanded
        inverse_gaps = 8 - expanded
        conversion = 2*extra_ports*inverse_gaps + 224*expanded
        deficit = 896 - 4*extra_ports*inverse_gaps
        idle_mass = dimension*productive - deficit - 9*5070 - conversion
        idle_cap = dimension - 24
        need(conversion == 16*extra_ports+(224-2*extra_ports)*expanded, "boundary conversion count")
        need(idle_mass == (23682+720*expanded if extra_ports == 8 else 28482+768*expanded),
             "remaining idle mass")
        profile = {r: 9*n for r, n in LOCAL.items() if r != 8}
        profile[1] += conversion
        profile[idle_cap] = F(idle_mass, idle_cap)
        need(sum(r*n for r, n in profile.items()) == dimension*productive-deficit,
             "complete optimistic raw invoice")
        controls = {f"{n}_H{r}": test_added(profile, dimension, productive, {r: n})
                    for n, r in ((68, 8), (69, 8), (70, 8), (71, 8), (72, 8), (8, 72))}
        for key in ("70_H8", "71_H8", "72_H8", "8_H72"):
            need(not controls[key]["passes_price"], "large consumer rejection")
        result[str(dimension)] = {
            "dimension": dimension, "productive_per_replica": productive,
            "extra_zero_ports_per_bank": extra_ports,
            "inverse_gaps": inverse_gaps, "expanded_gaps": expanded,
            "boundary_H1": conversion, "idle_mass": idle_mass,
            "idle_rank_cap": idle_cap, "raw_deficit": deficit,
            "optimistic_profile": {str(r): str(n) for r, n in profile.items()},
            "tariffs_at_target": tariffs(profile, dimension, productive, TARGET),
            "tariffs_at_bit_cap": tariffs(profile, dimension, productive, BIT_ROOT),
            "controls": controls,
        }
        if dimension == 81:
            for count in (68, 69, 70):
                p = Counter(profile)
                p[8] += count
                result[str(dimension)][f"optimistic_root_with_{count}_H8"] = root(p, dimension, productive)
    return {"status": "PASS_EXACT_SCOPED_BOUNDARY_FAMILY_SCREEN", "cases": result,
            "bound_direction": "All remaining idle rank mass is fractionally priced at the maximum allowed rank. Since r^(1-a)/r = r^(-a) decreases in r for a>0, this is a lower bound on the stated complete invoice. A failing screen excludes that boundary/tariff family; a passing screen does not supply packing or a native program.",
            "geometry_scope": "Only the16-extra-port m73 virtual-unit construction is natively checked separately. The other cases assume the corresponding mixed gap geometry exists and rank cap m-24 applies. The8-extra-port normalization requires division by3 and has no emitted120-port native word. This is not a theorem excluding different boundary contracts, endpoint fusions, or helper/terminal consumers.",
            "correction_to_prior_m81_screen": "The older optimistic screen assigned 1,792 rank units required for original-port boundary conversions to the favorable fractional rank57 idle tariff. Here those 1,792 operations are explicit H1 children. Thus 70H8 fails even before packing and terminal implementation costs."}


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length()
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def inherited_allocation(followup, out, emit_fill):
    supplier = followup / "artifact/live-source/research/staged544-producer-return"
    data = supplier / "inputs"
    sym_path = (followup / "artifact/integer-mult-bounds/research/kappa-consumer-followup"
                / "baseline/symmetric-extended-results/RESULT.json")
    sym = read(sym_path)
    source_roles = sym["providers"]["base"]["source_helper_ports"]
    target_roles = sym["providers"]["base"]["target_helper_ports"]
    promoted = set(source_roles+target_roles)
    need(len(promoted) == 32, "distinct promoted source and target roles")
    for p in sym["providers"].values():
        need(p["source_helper_ports"] == source_roles and p["target_helper_ports"] == target_roles,
             "both providers use the same promoted roles")
    retained = [h for h in range(408) if 224+h not in promoted]
    renumber = {h: i for i, h in enumerate(retained)}
    widths = {}
    source_hashes = {}
    for tag, provider in (("base", "gauge44"), ("extra", "extra")):
        path = data / f"NATIVE-{tag}.json.gz"
        w = read(path)
        v = [binary_rank(w["frames"][w["final"][r]])
             - binary_rank(w["frames"][w["start"][r]]) for r in range(224, 632)]
        need(all(v[r-224] == 9 for r in promoted), "every promoted helper has paid width9")
        need(sum(v[h] for h in retained) == 2990, "remaining helper width sum")
        widths[provider] = v
        source_hashes[str(path.relative_to(followup))] = digest(path)
    original_audit = module(supplier / "owner_audit.py", "invoice_original_owner_audit").audit()
    need(original_audit["profile"] == BASE, "independent complete original owner audit")
    order = read(data / "ORDER.json")
    dispatch = {(s, r): pid for s, r, pid in read(data / "DISPATCH.json")}
    template, plan = read(data / "TEMPLATE.json.gz"), read(data / "PLAN.json.gz")
    caps = {c["child"]: c["rank"] for c in template["idle_children"]}
    need(len(caps) == 18 and sum(caps.values()) == 432, "retained idle capacity")
    zero_caps = {child: cap + int(child in ZERO_PORT_FIRST_IDLE) for child, cap in caps.items()}
    need(sum(zero_caps.values()) == 438, "zero-port exact idle capacity")
    fill = read(data / "FILL.json.gz")
    used = Counter()
    emitted = [] if emit_fill else None
    previous = -1
    in_call = set()
    count = 0
    for time, helper, owner, child, port, old_offset in fill["rows"]:
        if helper not in renumber:
            continue
        if time != previous:
            need(previous == -1 or len(in_call) == 376, "complete retained helper call")
            in_call = set()
            previous = time
        new_helper = renumber[helper]
        family = owner*1024 + (2*plan["pairs"][str(child)] + plan["sides"][str(child)])*128 + port
        need(family not in in_call, "same-call family injection")
        in_call.add(family)
        key = owner, child, port
        offset = used[key]
        width = widths[dispatch[tuple(order[time])]][helper]
        need(offset <= old_offset, "deleting positive-width roles cannot advance a prefix")
        need(offset + width <= caps[child], "retained role capacity")
        used[key] += width
        if emitted is not None:
            emitted.append([time, new_helper, owner, child, port, offset])
        count += 1
    need(len(in_call) == 376 and count == CALLS*376, "literal retained role coverage")
    idle = Counter()
    for owner in range(T):
        for child, cap in caps.items():
            for port in range(112):
                remaining = cap-used[owner, child, port]
                if remaining:
                    idle[remaining] += 1
            idle[zero_caps[child]] += 16
    need(sum(r*n for r, n in idle.items()) == 28482*T, "complete changed idle rank mass")
    profile = Counter({r: CALLS*n for r, n in LOCAL.items() if r != 8})
    profile.update(idle)
    profile[1] += 256*T
    need(sum(r*n for r, n in profile.items()) == 74368*T, "finite full preconsumer invoice")
    per_replica = {r: F(n, T) for r, n in profile.items()}
    payload_record = None
    if emitted is not None:
        payload = {
            "columns": ["time", "helper", "owner_replica", "child", "port", "offset"],
            "helper_native_registers": [224+h for h in retained],
            "promoted_source_native_registers": source_roles,
            "promoted_target_native_registers": target_roles,
            "physical_family_formula": "1024*owner +128*(2*pair+side)+port",
            "zero_port_indices": list(range(112, 128)),
            "zero_port_helper_contacts": 0,
            "dispatch_overrides": [], "rows": emitted,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        path = out / "FILL-RETAINED376.json.gz"
        path.write_bytes(gzip.compress(raw, mtime=0))
        payload_record = {"path": path.name, "decompressed_sha256": hashlib.sha256(raw).hexdigest(),
                          "rows": count}
    for path in (sym_path, supplier/"owner_audit.py", data/"ORDER.json", data/"DISPATCH.json",
                 data/"TEMPLATE.json.gz", data/"PLAN.json.gz", data/"FILL.json.gz", data/"PROFILE.json"):
        source_hashes[str(path.relative_to(followup))] = digest(path)
    result = {
        "status": "PASS_LITERAL_SLOT_REUSE_AND_COMPLETE_PRECONSUMER_INVOICE",
        "original_owner_audit": original_audit,
        "replicas": T, "calls": CALLS, "productive_candidate": 1024*T,
        "helpers_per_call": 376, "roles": count,
        "promoted_native_roles": sorted(promoted),
        "remaining_width_inventory": dict(Counter(widths["gauge44"][h] for h in retained)),
        "remaining_width_per_call": 2990,
        "zero_port_idle_caps": zero_caps,
        "global_idle_profile": dict(sorted(idle.items())),
        "complete_preconsumer_profile": dict(sorted(profile.items())),
        "rank_mass": 74368*T,
        "raw_normalizer": 73*1024*T,
        "physical_family_upper": 1024*T+376+8+91+2,
        "tariffs_at_target": tariffs(per_replica, 73, 1024, TARGET),
        "tariffs_at_bit_cap": tariffs(per_replica, 73, 1024, BIT_ROOT),
        "preconsumer_root": root(profile, 73, 1024*T),
        "controls": {f"{n}_H8": test_added(per_replica, 73, 1024, {8: n}) for n in (7, 8, 70, 72)},
        "fill_payload": payload_record,
        "input_sha256": source_hashes,
        "scope": "The original physical windows are independently replayed; deletion of the32 promoted width9 roles preserves every remaining assignment, window, and same-call uniqueness. Every prefix is compacted. Added zero-port idle families host no borrowed helpers. The m73 geometry and native phase proof are separate. Productive1024 per replica requires a complete residual inverse, which this allocation does not construct or treat as free.",
        "excluded_claims": ["No completed residual inverse.", "No new kappa.",
                            "No new all-size, precision/tape or recursive-hosting theorem."]}
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--followup", type=Path, required=True,
                    help="Extracted kappa-consumer-followup attached package")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--emit-fill", action="store_true")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    result = {"status": "PASS_EXACT_INVOICE_CONTINUATION_NOT_SUPPLIER_ADMISSION",
              "target": str(TARGET), "retained_bit_cap": str(BIT_ROOT),
              "script_sha256": digest(Path(__file__)),
              "arithmetic_engine": str(ENGINE_PATH.relative_to(REPO)),
              "arithmetic_engine_sha256": digest(ENGINE_PATH),
              "baseline": original_screen(),
              "boundary_family": boundary_family_screen(),
              "rational_eight_port_boundary_family": boundary_family_screen(8),
              "m73_literal_allocation": inherited_allocation(args.followup.resolve(), args.out, args.emit_fill)}
    (args.out/"RESULT.json").write_text(json.dumps(result, indent=2)+"\n")
    print(result["status"])
    print("m73 literal additional H8 allowance:",
          result["m73_literal_allocation"]["tariffs_at_target"]["by_rank"]["8"]["decimal"][0])
    print("m81 corrected optimistic H8 allowance:",
          result["boundary_family"]["cases"]["81"]["tariffs_at_target"]["by_rank"]["8"]["decimal"][0])
    print("m81 rational8 optimistic H8 allowance:",
          result["rational_eight_port_boundary_family"]["cases"]["81"]["tariffs_at_target"]["by_rank"]["8"]["decimal"][0])
    print("all m73..81 tested boundary invoices reject 70H8,71H8,72H8 and8H72")


if __name__ == "__main__":
    main()
