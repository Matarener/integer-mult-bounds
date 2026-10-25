#!/usr/bin/env python3
"""Rebind a complete R437 word to the retained T35 physical owners and bill.

All source/target/helper endpoints, captured SOURCE rows, physical owners,
idle axes, and global controller are checked. Changed D and B graphs are
allowed and explicitly repriced. No complex supplier is inferred from this
BIT certificate. The retained physical/all-size interfaces remain conditional.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = HERE.parent / "kappa-next-regime"
PARENT = OLD / "geometry-search/pool35-word"
BASE = OLD / "sources/PR3647/research/bit-p111-r437-gl464-470-20261018"


def need(value, reason):
    if not value:
        raise ValueError(reason)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def capture(word):
    rows = [1 << r if r < 111 else 0 for r in range(659)]
    frames = list(word["start"])
    for frame, d, sources in word["A"]:
        for s in sources:
            rows[d] ^= rows[s]
        for r in [d] + sources:
            frames[r] = frame
    return [(r, word["frames"][frames[r]], rows[r]) for r in word["ret"]]


def run(word_path, records_path, output):
    need(not output.exists(), "fresh output directory")
    old_word_path = OLD / "word-search/candidate/WORD.json.gz"
    word, original = read(word_path), read(old_word_path)
    for key in ("v", "R", "h", "form", "lines", "start", "final", "ret", "scatter"):
        need(word[key] == original[key], "unchanged R437 boundary: " + key)
    need(capture(word) == capture(original), "all nine captured SOURCE rows and frames")
    word_sha = sha256(gzip.decompress(word_path.read_bytes())).hexdigest()
    checker = module("bit1745_independent_xcheck", BASE / "vendor/xcheck_p.py")
    local_check = checker.Word(word)
    all_columns = local_check.full()
    hypotheses, conclusion, _ = local_check.interface()
    need(all(hypotheses.values()) and all(conclusion.values()), "complete local native interface")
    builder = module("bit1745_retained_record_converter", OLD / "geometry-search/build_word_pool35.py")
    adapter = module("bit1745_native_adapter", OLD / "native-catalogue/adapter.py")
    dimensions = [builder.dimension(word["lines"], frame) for frame in word["frames"]]
    programs, local, information = adapter.lower_word(word, dimensions)
    need(programs == builder.from_records(records_path.read_bytes(), dimensions), "independent native export and lowering agree")
    need(information["forward"]["source_record_sha256"] == sha256(records_path.read_bytes()).hexdigest(), "actual native record pin")
    need(sum(r*n for r, n in local.items()) == 5113, "complete local rank mass")

    parent = read(PARENT / "GLOBAL-TEMPLATE.json.gz")
    parent_result = read(PARENT / "RESULT.json")
    need(sha256(canonical(parent)).hexdigest() == parent_result["template_content_sha256"], "retained physical template pin")
    template = deepcopy(parent)
    template["local_programs"] = programs
    template["source_record_sha256"] = information["forward"]["source_record_sha256"]
    template["version"] = "r437-T35-source-projection-DC-resynthesis"
    template["local_word_override"] = {"word_content_sha256": word_sha,
                                       "parent_template_content_sha256": parent_result["template_content_sha256"],
                                       "local_programs": information,
                                       "scope": "Complete changed A/B/C/D word with unchanged endpoints, captures, global controller, ordered helper widths and every absolute owner."}
    profile, owners = Counter(), []
    for old_call, call in zip(parent["calls"], template["calls"]):
        call["local_hash"] = information[call["orientation"]]["sha256"]
        need(call["owners"] == old_call["owners"], "every absolute owner retained")
        profile.update(local)
        for helper, (family, route) in enumerate(call["owners"][222:]):
            _, child, offset, width = route
            need(width == 8, "all 437 native helper widths remain eight")
            owners.append([call["stage"], call["replica"], helper, family, child, offset, width])
    need(owners == read(PARENT / "OWNER-INVENTORY.json.gz"), "all 137655 physical helper roles")
    idles = read(PARENT / "IDLE-INVENTORY.json.gz")
    profile.update(row[-1] for row in idles)
    need(len(idles) == 69930, "all absolute idle children")
    m, W, T, R, V, L, depth = 64, 31080, 35, 437, 111, 9, 2
    E, physical = sum(profile.values()), W + 9
    need(sum(r*n for r, n in profile.items()) == 1977885, "complete rank mass")
    need(m*W - sum(r*n for r, n in profile.items()) == 11235, "raw deficit")
    need(2*max(profile)**2 < m*m, "halving guard")

    invoice = module("bit1745_retained_local_counter", OLD / "complete_invoice.py")
    block = module("bit1745_retained_block_audit", OLD / "geometry-search/block_prefix.py")
    details = invoice.local_details(template, word)
    _, bridge_events, idle_count, bridge_adds = block.block_audit(template)
    forward, forward_copies = block.local_bound(programs["forward"])
    backward, backward_copies = block.local_bound(programs["reverse"])
    need(forward_copies == backward_copies == 9, "clean private COPY/ERASE episodes")
    need(backward == details["reverse"]["prefix_l1"], "independent reverse norm")
    # local_details permits a looser forward convention; choose the larger
    # of independently valid bounds, and pay it consistently in the invoice.
    forward = max(forward, details["forward"]["prefix_l1"])
    prefix = (1 << 90) * forward**25 * backward**20
    unit = L*T*details["forward"]["adds"] + 18*V*T
    episodes = 9*L*T
    J = 8*T*L*(2*V+R) + 8*(8*V*T) + 2*L*T*R + 2*episodes
    d, N = m*m, 2*m
    geometry = read(BASE / "data/GEOMETRY.json")
    selectors = 2*L*T*((W-1)+R*m*(geometry["max_route_factors"]+144+2+(m-1)+m))
    components = {"unit": unit, "J_times_high": J*16*(d+1)**2, "J_times_physical": J*physical,
                  "E_times_good": E*(8*m*m+8), "E_times_compiler": E*128*N**3,
                  "matrix_test": 16*m**3, "copy_erase_episodes": episodes,
                  "selectors": selectors, "one": 1}
    coefficient = prefix + sum(components.values())
    two = (coefficient+1)**2 * (E+1)**2
    prefix_charge = 64*((prefix.bit_length()+63)//64)
    two_charge = max(512, 64*((two.bit_length()+63)//64))
    need(prefix < 2**prefix_charge and two < 2**two_charge < 2**210000, "complete charged coefficient envelope")
    ROW = 2*(m*m+1) + 9909 + 252
    need(ROW == 18355 < 20161, "row guard")
    first, second = invoice.load_engine("moment"), invoice.load_engine("base_two_moment")
    price = first.certify(dict(profile), m, W, True)
    lower, upper = Q(price["lower"]), Q(price["upper"])
    need(lower > Q(parent_result["bit_endpoint_upper"]), "strict extra BIT gain over previous bracket")
    signs = []
    for label, endpoint in (("lower", lower), ("upper", upper)):
        lo, hi = second.moment(m, W, list(profile.items()), endpoint)
        fl, fh = second.moment(m, W, [(1, 32*m*m*E)], endpoint)
        lo, hi = lo + fl/10**16, hi + fh/10**16
        need(hi < 1 if label == "lower" else lo > 1, "second exact full-price sign")
        signs.append({"endpoint": str(endpoint), "moment_lower": str(lo), "moment_upper": str(hi)})
    output.mkdir(parents=True)
    payload = canonical(template)
    (output / "GLOBAL-TEMPLATE.json.gz").write_bytes(gzip.compress(payload, mtime=0))
    for name in ("OWNER-INVENTORY.json.gz", "IDLE-INVENTORY.json.gz", "POOL-MOVES.json"):
        (output / name).write_bytes((PARENT / name).read_bytes())
    paths = [word_path, old_word_path, records_path, PARENT / "GLOBAL-TEMPLATE.json.gz", PARENT / "RESULT.json",
             PARENT / "OWNER-INVENTORY.json.gz", PARENT / "IDLE-INVENTORY.json.gz", Path(__file__),
             BASE / "vendor/xcheck_p.py", OLD / "native-catalogue/adapter.py", OLD / "complete_invoice.py",
             OLD / "geometry-search/block_prefix.py", OLD / "geometry-search/build_word_pool35.py",
             BASE / "vendor/engines/moment.py", BASE / "vendor/engines/base_two_moment.py", BASE / "data/GEOMETRY.json"]
    result = {"status": "PASS_T35_SOURCE_RESYNTHESIS_COMPLETE_BIT_INVOICE", "new_combined_kappa": False,
              "m": m, "productive_families": W, "physical_families": physical, "replicas": T,
              "local_calls": L*T, "helper_roles": len(owners), "absolute_idle_children": len(idles),
              "local_profile": dict(sorted(local.items())), "profile": dict(sorted(profile.items())),
              "paid_requests": E, "rank_mass": 1977885, "raw_deficit": 11235,
              "bit_endpoint_lower": str(lower), "bit_endpoint_upper": str(upper),
              "bit_endpoint_lower_decimal": first.decimal(lower), "bit_endpoint_upper_decimal": first.decimal(upper),
              "gain_over_previous_upper": str(lower-Q(parent_result["bit_endpoint_upper"])),
              "gain_over_previous_lower": str(lower-Q(parent_result["bit_endpoint_lower"])),
              "gap_to_requested_target": str(Q("0.001745")-lower),
              "strict_rational_price": price, "second_engine_signs": signs,
              "word_content_sha256": word_sha, "template_content_sha256": sha256(payload).hexdigest(),
              "source_record_sha256": sha256(records_path.read_bytes()).hexdigest(), "local_programs": information,
              "local_details": details, "all_columns": all_columns, "hypotheses": hypotheses, "conclusion": conclusion,
              "block_proof": {"blocks": 7, "replicas_per_block": 5, "bridge_events": bridge_events,
                              "bridge_adds": bridge_adds, "private_payload_carry": False,
                              "forward_norm": forward, "reverse_norm": backward},
              "coefficient_invoice": {"components_without_prefix": {k: str(v) for k, v in components.items()},
                                      "five_replica_prefix": str(prefix), "prefix_bits": prefix.bit_length(),
                                      "charged_prefix_bits": prefix_charge, "coefficient": str(coefficient),
                                      "two_level_coefficient": str(two), "two_level_bits": two.bit_length(),
                                      "charged_two_level_bits": two_charge, "semantic_umbrella_bits": 210000,
                                      "ROW": ROW, "ROW_cap": 20161},
              "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths},
              "scope": "Complete finite BIT word and inherited-formula invoice on unchanged T35 physical owners. General packet/source, recursive-D, physical primitive, precision and all-size assumptions remain inherited. The disputed high complex endpoint is not used. No combined kappa gain or attainment of0.001745 is claimed."}
    (output / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "bit_endpoint_lower_decimal", "bit_endpoint_upper_decimal", "paid_requests", "profile")}), flush=True)
    return result


if __name__ == "__main__":
    sys.set_int_max_str_digits(0)
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--word", type=Path, required=True)
    ap.add_argument("--records", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    run(args.word.resolve(), args.records.resolve(), args.out.resolve())
