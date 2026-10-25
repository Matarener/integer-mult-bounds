#!/usr/bin/env python3
"""Read-only replay of the flag-43 head-step repair bill.

Applies two changed schedules to the published 4,058-event P104 witness in
memory, assembles their native recipe sets from the published recipes plus
the committed new-edge recipes, and runs the published native checker's
complete validate() on each: every native edge, every endpoint adapter, all
280 framed rows and the 72 dirty-helper restorations. It then recomputes the
bill, the head co-hosting facts and the forced-hosting closure of every Y59
update, and compares the receipt with CERTIFICATE.json. Admission uses need()
and stays active under python -O. Nothing is written.
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
FLAG_INDEX = 43
SELECTED_KAPPA = "0.001672660197076918"
MARKER = (
    "PASS_P104_FLAG43_HEAD_STEP_REPAIR flag=43 head=15 repaired_update=3364 "
    "added_events=0 added_adds=0 added_transports=0 added_rank_mass=0 "
    "retargeted_transports=9 forced_registers=4 profile_delta=-3H1+5H2-H3-H4 "
    "native_validate=PASS earlier_updates_obstructed=14/14 no_new_kappa"
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
    name = "flag43_repair_check_native"
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


# --- GF(2) frames -----------------------------------------------------------

def span(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


def rank(vectors):
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
    mv = lambda rows, x: sum((((row & x).bit_count()) & 1) << i for i, row in enumerate(rows))
    dot = lambda a, b: (a & mv(dual, b)).bit_count() & 1
    convert = lambda x: sum(dot(x, v) << j for j, v in enumerate(orth))
    return lambda frame: canon(convert(x) for x in frame)


# --- schedules ---------------------------------------------------------------

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
        "transport_occurrences": sum(profile.values()),
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


def majorized(small, big):
    """True when `small` is majorized by `big` (same length and sum)."""
    s, b = sorted(small, reverse=True), sorted(big, reverse=True)
    if len(s) != len(b) or sum(s) != sum(b):
        return False
    ps = pb = 0
    for x, y in zip(s, b):
        ps += x
        pb += y
        if ps > pb:
            return False
    return True


# --- frame chronology --------------------------------------------------------

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


def row_replay(witness, program, watch):
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
            if dst == watch[0]:
                carried = Fraction(a) * state[src].get(watch[1], Fraction(0))
                before = state[dst].get(watch[1], Fraction(0))
                seen.append((i, src, carried, before + carried))
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


# --- receipt -----------------------------------------------------------------

def receipt(root, cert, new_recipes):
    ck = load_checker(root)
    witness, fixture, recipes, flags = load_inputs(root)
    helper = flags["helpers"][FLAG_INDEX]
    head = helper["basis"][0]
    source, target = "X%d" % helper["source"], "Y%d" % helper["target"]
    need((source, target, head) == ("X21", "Y59", 15), "flag 43 identity")
    physical = physical_map(recipes)
    program = witness["program"]
    published = ck.validate(recipes, witness, fixture, False)
    need(published["transports"] == len(recipes["transports"]) == 740, "published native edges")
    out = {"published": bill(published, program, published["transports"])}
    repaired = {}
    used = set()
    for name in ("R0", "R1"):
        prog = apply_splices(program, cert["repairs"][name]["splices"])
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
    for name in ("R0", "R1"):
        out[name]["profile_delta"] = profile_delta(out["published"], out[name])
        for key in ("events", "scalar_adds", "transport_occurrences", "rank_mass"):
            out[name]["added_" + key] = out[name][key] - out["published"][key]

    # Retargeted transports and the head co-hosting update.
    r0 = repaired["R0"]
    changed = [i for i, (a, b) in enumerate(zip(program, r0)) if a != b]
    retargeted = [i for i in changed if program[i][0] == "transport"]
    relabelled = [i for i in changed if program[i][0] == "add"]
    for i in relabelled:
        need(program[i][:4] == r0[i][:4], "add registers and coefficient unchanged")
    for i in retargeted:
        a, b = program[i], r0[i]
        need(a[1] == b[1], "same register")
        need(span(b[3]) == span(list(a[3]) + [head]) or span(b[3]) == span(a[3]), "after-frame is published plus head")
        need(span(b[2]) == span(a[2]) or span(b[2]) == span(list(a[2]) + [head]), "before-frame is published plus head")
    pub_ranks = [program[i][4] for i in retargeted]
    new_ranks = [r0[i][4] for i in retargeted]
    hist = frame_history(witness, r0)
    adds = [i for i, e in enumerate(r0) if e[0] == "add" and e[1] == target]
    last = adds[-1]
    chart = r0[last][4]
    src_frame = frame_at(hist, source, last)
    later_source = [i for i, e in enumerate(r0) if i > last and source in e[1:3]]
    _, seen = row_replay(witness, r0, (target, source))
    delivery = [[i, src, str(c), str(after)] for i, src, c, after in seen if c]
    pub_hist = frame_history(witness, program)
    pub_hosting_updates = [i for i in adds if head in frame_at(pub_hist, target, i)]
    hosting_updates = [i for i in adds if head in frame_at(hist, target, i) and head in frame_at(hist, source, i)]
    r1 = repaired["R1"]
    h1 = frame_history(witness, r1)
    adds1 = [i for i, e in enumerate(r1) if e[0] == "add" and e[1] == target]
    out["R0"]["retargeted_transports"] = retargeted
    out["R0"]["relabelled_add_charts"] = relabelled
    out["R0"]["retargeted_ranks_published"] = pub_ranks
    out["R0"]["retargeted_ranks_repaired"] = new_ranks
    out["R0"]["majorized_by_published"] = majorized(new_ranks, pub_ranks)
    out["R0"]["registers_changed"] = sorted({program[i][1] for i in retargeted})
    out["head_cohosting"] = {
        "published_head_hosting_target_updates": pub_hosting_updates,
        "R0_cohosted_target_updates": hosting_updates,
        "R0_last_target_update": last,
        "R0_update_partner": r0[last][2],
        "R0_update_chart": chart,
        "R0_update_chart_rank": rank(chart),
        "R0_source_frame_rank_at_update": rank(sorted(src_frame - {0})),
        "R0_source_spans_head_at_update": head in src_frame,
        "R0_source_events_after_update": later_source,
        "R0_source_delivery_into_target": delivery,
        "R1_cohosted_target_updates": [i for i in adds1 if head in frame_at(h1, target, i) and head in frame_at(h1, source, i)],
        "R1_last_target_update": adds1[-1],
    }
    table = closure_table(witness, program, target, head)
    admissible = [row["event"] for row in table if row["admissible"]]
    obstructed = [row["event"] for row in table if row["slot_independent_obstructions"]]
    gain = {}
    for e in program:
        if e[0] == "transport":
            gain[e[1]] = gain.get(e[1], 0) + e[4]
    floor = [r for r in witness["initial_frames"]
             if gain.get(r, 0) == rank(witness["final_frames"][r]) - rank(witness["initial_frames"][r])]
    need(len(floor) == len(witness["initial_frames"]) == 280, "every non-private register at its rank floor")
    out["forced_hosting"] = {
        "non_private_registers_at_rank_floor": len(floor),
        "table": table,
        "admissible_updates": admissible,
        "slot_independently_obstructed_updates": obstructed,
    }
    return {
        "schema_version": 1,
        "claim_id": "p104-flag43-head-step-repair",
        "pinned_main": "6f100d4bb5083f8c35d96fd95a539811c62f245c",
        "flag_index": FLAG_INDEX,
        "source_register": source,
        "target_register": target,
        "basis_head": head,
        "repairs": cert["repairs"],
        "bill": {k: out[k] for k in ("published", "R0", "R1")},
        "head_cohosting": out["head_cohosting"],
        "forced_hosting": out["forced_hosting"],
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }


def admit(root, cert, new_recipes):
    got = json.loads(json.dumps(receipt(root, cert, new_recipes)))
    need(got == cert, "receipt differs from committed certificate")
    b = cert["bill"]
    r0, r1, hc, fh = b["R0"], b["R1"], cert["head_cohosting"], cert["forced_hosting"]
    need([r0["added_" + k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")] == [0, 0, 0, 0], "R0 adds nothing to the counted bill")
    need(r0["profile_delta"] == {"1": -3, "2": 5, "3": -1, "4": -1}, "R0 profile delta")
    need(len(r0["retargeted_transports"]) == 9 and r0["majorized_by_published"], "R0 retargets nine transports by majorization")
    need(r0["registers_changed"] == ["D17", "D28", "Y103", "Y59"], "R0 changed registers")
    need(r1["added_events"] == 1 and r1["added_transport_occurrences"] == 1 and r1["added_rank_mass"] == 0, "R1 bill")
    need(r1["profile_delta"] == {"2": 2, "4": -1}, "R1 profile delta")
    need(hc["published_head_hosting_target_updates"] == [], "published word has no head-hosting update")
    need(hc["R0_cohosted_target_updates"] == [3364] and hc["R0_source_spans_head_at_update"], "R0 co-hosts the head at 3364")
    need(hc["R0_source_events_after_update"] == [3705, 3760, 3811, 3863], "source still live")
    need(hc["R0_source_delivery_into_target"][-1] == [3364, "D17", "1/2", "1/2"], "3364 settles the source coefficient")
    need(hc["R1_cohosted_target_updates"] == [hc["R1_last_target_update"]], "R1 co-hosts at its last update")
    need(fh["admissible_updates"] == [3364], "3364 is the only admissible update")
    need(len(fh["slot_independently_obstructed_updates"]) == 14, "every earlier update obstructed")
    forced = [row for row in fh["table"] if row["event"] == 3364][0]["forced"]
    need(forced == {"D17": 3364, "Y59": 3364, "Y103": 3366, "D28": 3462}, "forced register set")
    need(cert["selected_kappa"] == SELECTED_KAPPA and cert["no_new_kappa"] is True, "kappa unchanged")
    return got


def main(root=ROOT):
    cert = loads((HERE / "CERTIFICATE.json").read_bytes())
    new_recipes = loads((HERE / "REPAIR-RECIPES.json").read_bytes())["recipes"]
    admit(root, cert, new_recipes)
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
