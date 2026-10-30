#!/usr/bin/env python3
"""Read-only replay of the flag-9 head-step repair bill.

Applies two changed schedules to the published 4,058-event P104 witness in
memory, assembles their native recipe sets from the published recipes plus
the committed new-edge recipes, and runs the published native checker's
complete validate() on each. It then recomputes the bill, the head
co-hosting facts, the X4 span correction, and the forced-hosting closure of
every Y23 update, and compares the receipt with CERTIFICATE.json. Admission
uses need() and stays active under python -O. Nothing is written.
"""

import bisect
import copy
import gzip
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = "research/p104-native-channel"
PINS = {
    f"{NATIVE}/inputs/LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    f"{NATIVE}/inputs/P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    f"{NATIVE}/NATIVE-RECIPES.json.gz": "a1c4d83d3d5fe1338e99b59272e8cf5d43244c33888597da340b2aa7fef5b3e8",
    f"{NATIVE}/check_native.py": "e67b874a061a4a28007b9a0fabaf30c8db4a587b1e1c7dd9396c77ff1e3a9fe6",
    f"{NATIVE}/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "research/p104-joint-unit-flags/CERTIFICATE.json": "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
}
FLAG_INDEX = 9
HEAD = 196
SOURCE = "X4"
TARGET = "Y23"
SELECTED_KAPPA = "0.001672660197076918"
MARKER = (
    "PASS_P104_FLAG9_HEAD_STEP_REPAIR flag=9 head=196 delivering_update=3124 "
    "R0_added_events=1 R0_added_rank_mass=2 R0_mass_register=D28 "
    "R1_added_events=0 R1_added_rank_mass=2 R1_mass_register=Y23 "
    "profile_R0=-H1+2H2+H4-H5 profile_R1=H7-H5 "
    "native_validate=PASS updates_obstructed=9/9 source_events_keep_head=21/21 "
    "no_new_kappa"
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key: " + str(key))
        out[key] = value
    return out


def loads(raw):
    return json.loads(raw, object_pairs_hook=pairs_unique)


def pinned_bytes(root, rel):
    raw = (root / rel).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[rel], "pinned input changed: " + rel)
    return raw


def load_checker(root):
    pinned_bytes(root, f"{NATIVE}/check_native.py")
    pinned_bytes(root, f"{NATIVE}/vendor/native_verify.py")
    name = "flag9_repair_check_native"
    spec = importlib.util.spec_from_file_location(name, root / NATIVE / "check_native.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_inputs(root):
    witness = loads(pinned_bytes(root, f"{NATIVE}/inputs/LOWRANK-WITNESS.json"))
    fixture = loads(pinned_bytes(root, f"{NATIVE}/inputs/P104-FIXTURE.json"))["section4_explicit_P104"]
    recipes = loads(gzip.decompress(pinned_bytes(root, f"{NATIVE}/NATIVE-RECIPES.json.gz")))
    flags = loads(pinned_bytes(root, "research/p104-joint-unit-flags/CERTIFICATE.json"))
    return witness, fixture, recipes, flags


def span(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


def dim(vectors):
    n = len(span(vectors))
    need(n and n & (n - 1) == 0, "frame span is not a subspace")
    return n.bit_length() - 1


def rank_of_independent(vectors):
    piv = {}
    for x in vectors:
        while x:
            j = x.bit_length() - 1
            if j in piv:
                x ^= piv[j]
            else:
                piv[j] = x
                break
    return len(piv)


def canon(values):
    piv = {}
    for x in values:
        while x:
            j = x.bit_length() - 1
            if j in piv:
                x ^= piv[j]
            else:
                piv[j] = x
                break
    for j in sorted(piv):
        for k in piv:
            if k > j and piv[k] >> j & 1:
                piv[k] ^= piv[j]
    return tuple(piv[j] for j in sorted(piv, reverse=True))


def physical_map(recipes):
    iso = recipes["label_isometry"]
    dual = iso["compressed_dual_gram"]
    orth = iso["orthonormal_basis_compressed"]

    def mv(rows, x):
        return sum((((row & x).bit_count()) & 1) << i for i, row in enumerate(rows))

    def convert(x):
        return sum(((x & mv(dual, v)).bit_count() & 1) << j for j, v in enumerate(orth))

    return lambda frame: canon(convert(x) for x in frame)


def apply_splices(program, splices):
    out = list(program)
    last = len(program) + 1
    for row in sorted(splices, key=lambda r: -r["published_range"][0]):
        start, stop = row["published_range"]
        need(0 <= start < stop <= len(program) and stop <= last, "ordered disjoint splices")
        for k, old in enumerate(row["published"]):
            need(program[start + k] == old, "splice binds published event %d" % (start + k))
        need(len(row["published"]) == stop - start, "splice covers its range")
        out[start:stop] = copy.deepcopy(row["events"])
        last = start
    return out


def check_program_frames(witness, program):
    frames = {n: span(f) for n, f in witness["initial_frames"].items()}
    profile = {}
    adds = 0
    for i, e in enumerate(program):
        op = e[0]
        if op == "transport":
            _, reg, old, new, k = e
            a, b = span(old), span(new)
            need(frames[reg] == a, "transport before-frame continuity at %d" % i)
            need(a <= b or b <= a, "nested transport at %d" % i)
            need(k == abs(dim(new) - dim(old)) and k > 0, "paid rank equals frame gap at %d" % i)
            frames[reg] = b
            profile[k] = profile.get(k, 0) + 1
        elif op == "zero":
            frames[e[1]] = span(e[2])
        elif op == "erase":
            frames.pop(e[1])
        elif op == "copy":
            need(frames[e[1]] == frames[e[2]] == span(e[3]), "copy chart at %d" % i)
        elif op == "add":
            _, dst, src, _a, fr = e
            need(frames[dst] == frames[src] == span(fr), "common chart at %d" % i)
            adds += 1
        else:
            need(False, "opcode at %d" % i)
    for name, final in witness["final_frames"].items():
        need(frames[name] == span(final), "final frame " + name)
    return profile, adds


def assemble(recipes, program, new_recipes, physical):
    pub = {(tuple(r["old"]), tuple(r["new"])): r for r in recipes["transports"]}
    extra = {(tuple(r["old"]), tuple(r["new"])): r for r in new_recipes}
    need(len(extra) == len(new_recipes), "unique new-edge recipes")
    need(not (set(pub) & set(extra)), "new recipes are new edges")
    edges = {}
    for i, e in enumerate(program):
        if e[0] == "transport":
            edges.setdefault((physical(e[2]), physical(e[3])), []).append(i)
    used_new = set()
    out = []
    for key in sorted(edges):
        if key in pub:
            rec = dict(pub[key])
        else:
            need(key in extra, "missing native recipe for new edge")
            rec = dict(extra[key])
            used_new.add(key)
        rec["events"] = edges[key]
        out.append(rec)
    profile = {}
    for rec in out:
        profile[rec["rank"]] = profile.get(rec["rank"], 0) + len(rec["events"])
    c = dict(recipes)
    c["transports"] = out
    c["paid_profile"] = {str(k): v for k, v in sorted(profile.items())}
    return c, used_new, len(set(pub) - set(edges))


def bill(result, program, n_edges):
    profile = {str(k): v for k, v in sorted(result["paid_profile"].items())}
    return {
        "events": len(program),
        "scalar_adds": result["scalar_events"]["add"],
        "private_events": {k: result["scalar_events"][k] for k in ("zero", "copy", "erase")},
        "transport_occurrences": sum(int(v) for v in profile.values()),
        "rank_mass": result["rank_mass"],
        "paid_profile": profile,
        "distinct_native_edges": n_edges,
        "endpoint_adapters": result["intrinsic_endpoint_adapters"],
        "formal_boundary_columns": result["formal_boundary_columns"],
    }


def profile_delta(a, b):
    keys = sorted({int(k) for k in a["paid_profile"]} | {int(k) for k in b["paid_profile"]})
    out = {}
    for k in keys:
        d = b["paid_profile"].get(str(k), 0) - a["paid_profile"].get(str(k), 0)
        if d:
            out[str(k)] = d
    return out


def frame_history(witness, program):
    hist = {n: [(-1, span(f))] for n, f in witness["initial_frames"].items()}
    for i, e in enumerate(program):
        if e[0] == "transport":
            hist[e[1]].append((i, span(e[3])))
        elif e[0] == "zero":
            hist.setdefault(e[1], []).append((i, span(e[2])))
    return hist


def frame_at(hist, reg, t):
    h = hist[reg]
    k = bisect.bisect_left([x[0] for x in h], t) - 1
    return h[k][1]


def register_mass(program):
    mass = {}
    for e in program:
        if e[0] == "transport":
            mass[e[1]] = mass.get(e[1], 0) + e[4]
    return mass


def deliveries(witness, program):
    state = {n: {n: Fraction(1)} for n in witness["initial_frames"]}
    seen = []
    for i, e in enumerate(program):
        op = e[0]
        if op == "zero":
            state[e[1]] = {}
        elif op == "erase":
            state.pop(e[1])
        elif op == "copy":
            state[e[1]] = dict(state[e[2]])
        elif op == "add":
            _, dst, src, a, _f = e
            if dst == TARGET:
                carried = Fraction(a) * state[src].get(SOURCE, Fraction(0))
                before = state[TARGET].get(SOURCE, Fraction(0))
                if carried:
                    seen.append([i, src, str(carried), str(before + carried)])
            for name, v in list(state[src].items()):
                z = state[dst].get(name, Fraction(0)) + Fraction(a) * v
                if z:
                    state[dst][name] = z
                else:
                    state[dst].pop(name, None)
    return state, seen


def closure_table(witness, program, target, head):
    hist = frame_history(witness, program)
    finals = {n: span(f) for n, f in witness["final_frames"].items()}
    monotone = {r: r != "C" and all(a[1] <= b[1] for a, b in zip(h, h[1:])) for r, h in hist.items()}
    touch = {}
    for i, e in enumerate(program):
        if e[0] in ("add", "copy"):
            for r in (e[1], e[2]):
                touch.setdefault(r, []).append(i)
    rows = []
    for i, e in enumerate(program):
        if e[0] != "add" or e[1] != target:
            continue
        host = {target: i}
        work = [target]
        while work:
            r = work.pop()
            t = host[r]
            for j in touch.get(r, []):
                if j < t:
                    continue
                other = program[j][2] if program[j][1] == r else program[j][1]
                if other not in host or host[other] > j:
                    host[other] = j
                    work.append(other)
        change = {r: t for r, t in host.items() if head not in frame_at(hist, r, t)}
        hard, slot, private = [], [], []
        for r, t in sorted(change.items(), key=lambda x: (x[1], x[0])):
            if not monotone.get(r, False):
                private.append([r, t])
            elif r in finals and head not in finals[r]:
                hard.append([r, t, "final frame excludes head"])
            elif not any(-1 < j < t for j, _ in hist[r]):
                slot.append([r, t])
        rows.append({
            "event": i,
            "partner": e[2],
            "must_change": len(change),
            "slot_independent_obstructions": len(hard),
            "first_obstruction": hard[0] if hard else None,
            "registers_without_prior_transport": len(slot),
            "private_registers_forced": private,
            "admissible": not hard and not slot and not private,
            "forced": {r: t for r, t in sorted(change.items(), key=lambda x: (x[1], x[0]))} if not hard else None,
        })
    return rows


def cohost_facts(witness, program, published_hist_target):
    hist = frame_history(witness, program)
    adds = [i for i, e in enumerate(program) if e[0] == "add" and e[1] == TARGET]
    hosting = [i for i in adds if HEAD in frame_at(hist, TARGET, i) and HEAD in frame_at(hist, SOURCE, i)]
    need(len(hosting) == 1, "one co-hosted target update")
    last = hosting[0]
    later = [i for i, e in enumerate(program) if i > last and SOURCE in e[1:3]]
    _state, seen = deliveries(witness, program)
    return {
        "cohosted_target_updates": hosting,
        "update": last,
        "partner": program[last][2],
        "chart": program[last][4],
        "chart_rank": dim(program[last][4]),
        "source_frame_rank": rank_of_independent(frame_at(hist, SOURCE, last) - {0}),
        "source_spans_head": HEAD in frame_at(hist, SOURCE, last),
        "source_events_after_update": later,
        "source_delivery_into_target": seen,
        "published_head_hosting_target_updates": [
            i for i, e in enumerate(witness["program"])
            if e[0] == "add" and e[1] == TARGET and HEAD in frame_at(published_hist_target, TARGET, i)
        ],
    }


def receipt(root, cert, new_recipes):
    ck = load_checker(root)
    witness, fixture, recipes, flags = load_inputs(root)
    helper = flags["helpers"][FLAG_INDEX]
    head = helper["basis"][0]
    source, target = "X%d" % helper["source"], "Y%d" % helper["target"]
    need((source, target, head) == (SOURCE, TARGET, HEAD), "flag 9 identity")
    physical = physical_map(recipes)
    program = witness["program"]
    published = ck.validate(recipes, witness, fixture, False)
    need(published["transports"] == len(recipes["transports"]) == 740, "published native edges")
    out = {"published": bill(published, program, published["transports"])}
    pub_hist = frame_history(witness, program)
    repaired = {}
    used = set()
    for name in ("R0", "R1"):
        prog = apply_splices(program, cert["repairs"][name]["splices"])
        check_program_frames(witness, prog)
        w2 = dict(witness)
        w2["program"] = prog
        c2, used_new, dropped = assemble(recipes, prog, new_recipes, physical)
        used |= used_new
        result = ck.validate(c2, w2, fixture, False)
        out[name] = bill(result, prog, result["transports"])
        out[name]["new_native_edges"] = len(used_new)
        out[name]["dropped_native_edges"] = dropped
        repaired[name] = prog
    need(len(used) == len(new_recipes), "every committed recipe is used")
    pub_mass = register_mass(program)
    for name in ("R0", "R1"):
        out[name]["profile_delta"] = profile_delta(out["published"], out[name])
        for key in ("events", "scalar_adds", "transport_occurrences", "rank_mass"):
            out[name]["added_" + key] = out[name][key] - out["published"][key]
        mass = register_mass(repaired[name])
        out[name]["register_rank_mass_delta"] = {
            r: mass.get(r, 0) - pub_mass.get(r, 0)
            for r in sorted(set(mass) | set(pub_mass))
            if mass.get(r, 0) != pub_mass.get(r, 0)
        }
        facts = cohost_facts(witness, repaired[name], pub_hist)
        out[name]["cohosting"] = facts

    # Literal generator drop versus span. 196 = 64 XOR 132.
    drop = program[500]
    need(drop[:2] == ["transport", SOURCE], "event 500 is the X4 transport")
    after = drop[3]
    need(HEAD not in after and 64 in after and 132 in after and (64 ^ 132) == HEAD, "literal drop keeps 196 in span")
    source_frames = pub_hist[SOURCE]
    source_events = [
        i for i, e in enumerate(program)
        if SOURCE in (e[1:3] if e[0] in ("add", "copy") else e[1:2])
    ]
    need(all(HEAD in sp for _t, sp in source_frames), "X4 spans 196 in every source frame")
    need(all(HEAD in frame_at(pub_hist, SOURCE, i) for i in source_events), "X4 spans 196 at every source event")
    need(len(source_events) == 21 and len(source_frames) == 7, "source event and frame counts")
    target_final = span(witness["final_frames"][TARGET])
    partner_final = span(witness["final_frames"]["Y28"])
    need(HEAD in target_final and HEAD not in partner_final, "Y23 final hosts 196 and Y28 final does not")
    between = [e for e in program[3125:3126]]
    need(all("D28" not in e[1:3] for e in between), "no D28 event between the delivering ADD and Y28")

    gain = register_mass(program)
    floor = [r for r in witness["initial_frames"]
             if gain.get(r, 0) == dim(witness["final_frames"][r]) - dim(witness["initial_frames"][r])]
    need(len(floor) == len(witness["initial_frames"]) == 280, "every non-private register at its rank floor")
    table = closure_table(witness, program, TARGET, HEAD)
    return {
        "schema_version": 1,
        "claim_id": "p104-flag9-head-step-repair",
        "pinned_main": "bb4bccbf42844d2801487450727c2f63e10d1d0f",
        "flag_index": FLAG_INDEX,
        "source_register": SOURCE,
        "target_register": TARGET,
        "basis_head": HEAD,
        "source_span": {
            "head_in_every_source_frame": True,
            "source_frame_count": len(source_frames),
            "source_event_count": len(source_events),
            "literal_drop_event": 500,
            "literal_drop_after_lists_head": False,
            "span_relation": "196 = 64 XOR 132",
        },
        "repairs": cert["repairs"],
        "bill": {k: {kk: vv for kk, vv in out[k].items() if kk != "cohosting"} for k in ("published", "R0", "R1")},
        "head_cohosting": {
            "published_head_hosting_target_updates": out["R0"]["cohosting"]["published_head_hosting_target_updates"],
            "R0": {k: v for k, v in out["R0"]["cohosting"].items() if k != "published_head_hosting_target_updates"},
            "R1": {k: v for k, v in out["R1"]["cohosting"].items() if k != "published_head_hosting_target_updates"},
        },
        "forced_hosting": {
            "non_private_registers_at_rank_floor": len(floor),
            "table": table,
            "admissible_updates": [row["event"] for row in table if row["admissible"]],
            "slot_independently_obstructed_updates": [row["event"] for row in table if row["slot_independent_obstructions"]],
        },
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }


def admit(root, cert, new_recipes):
    got = json.loads(json.dumps(receipt(root, cert, new_recipes)))
    need(got == cert, "receipt differs from committed certificate")
    b, hc, fh = cert["bill"], cert["head_cohosting"], cert["forced_hosting"]
    pub, r0, r1 = b["published"], b["R0"], b["R1"]
    need(pub["events"] == 4058 and pub["scalar_adds"] == 2624, "published counts")
    need(pub["transport_occurrences"] == 1410 and pub["rank_mass"] == 2368, "published mass")
    need(pub["distinct_native_edges"] == 740, "published edges")
    need([r0["added_" + k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")] == [1, 0, 1, 2], "R0 bill")
    need(r0["profile_delta"] == {"1": -1, "2": 2, "4": 1, "5": -1}, "R0 profile delta")
    need(r0["register_rank_mass_delta"] == {"D28": 2}, "R0 mass sits on D28")
    need(r0["distinct_native_edges"] == 742, "R0 edges")
    need([r1["added_" + k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")] == [0, 0, 0, 2], "R1 bill")
    need(r1["profile_delta"] == {"5": -1, "7": 1}, "R1 profile delta")
    need(r1["register_rank_mass_delta"] == {"Y23": 2}, "R1 mass sits on Y23")
    need(r1["distinct_native_edges"] == 741, "R1 edges")
    need(hc["published_head_hosting_target_updates"] == [], "published updates are head-free")
    r0h, r1h = hc["R0"], hc["R1"]
    need(r0h["cohosted_target_updates"] == [3124] and r0h["partner"] == "D28", "R0 co-hosts at 3124")
    need(r0h["chart"] == [447, 127, 192, 196] and r0h["chart_rank"] == 4, "R0 chart")
    need(r0h["source_spans_head"] and r0h["source_frame_rank"] == 9, "R0 source still spans the head at full rank")
    need(r0h["source_events_after_update"] == [3696, 3803, 3855, 3959, 4010], "R0 source still live")
    need(r0h["source_delivery_into_target"] == [[3124, "D28", "-1/2", "-1/2"]], "R0 delivers -1/2 once")
    need(r1h["update"] == 3633 and r1h["partner"] == "D28" and r1h["chart_rank"] == 9, "R1 co-hosts in the full chart")
    need(r1h["source_spans_head"] and r1h["source_delivery_into_target"] == [[3633, "D28", "-1/2", "-1/2"]], "R1 delivery")
    need(r1h["source_events_after_update"] == [3695, 3802, 3854, 3958, 4009], "R1 source still live")
    need(fh["admissible_updates"] == [], "no zero-mass admissible update")
    need(len(fh["slot_independently_obstructed_updates"]) == 9, "all nine updates obstructed")
    row = [r for r in fh["table"] if r["event"] == 3124][0]
    need(row["first_obstruction"] == ["Y28", 3126, "final frame excludes head"], "3124 forces Y28")
    need(row["slot_independent_obstructions"] == 5, "3124 has five final-excluding registers")
    need(cert["source_span"]["source_frame_count"] == 7 and cert["source_span"]["source_event_count"] == 21, "span counts")
    need(cert["source_span"]["span_relation"] == "196 = 64 XOR 132", "span correction")
    need(fh["non_private_registers_at_rank_floor"] == 280, "rank floor")
    need(cert["selected_kappa"] == SELECTED_KAPPA and cert["no_new_kappa"] is True, "kappa unchanged")
    return got


def main(root=ROOT):
    cert = loads((HERE / "CERTIFICATE.json").read_bytes())
    new_recipes = loads((HERE / "REPAIR-RECIPES.json").read_bytes())["recipes"]
    admit(root, cert, new_recipes)
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
