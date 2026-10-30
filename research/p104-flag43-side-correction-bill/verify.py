#!/usr/bin/env python3
"""Read-only replay of the flag-43 side-correction bill at R0's co-hosted cut.

Builds #3508's repair R0 from its committed splices, then applies four
corrections that add the (59, 21) entry of I - G/2 (and, for T48, the whole
Y59 row) after R0's last Y59 update. For each corrected word it runs the
published check_native.validate() unchanged on the coefficient-0 copy (chart
legality, native edges, endpoint adapters and all 280 framed rows do not
depend on the inserted coefficient), replays the real word with exact rational
rows, and confirms that validate() rejects the real word only at Y59's
endpoint. It then recomputes the bills, the forcing chain and the
least-lower-bound frame sweep that rules out a zero-added-mass placement, and
compares the receipt with CERTIFICATE.json. Admission uses need() and stays
active under python -O. Nothing is written.
"""

import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = "research/p104-native-channel"
REPAIR = "research/p104-flag43-head-step-repair"
PINS = {
    f"{NATIVE}/inputs/LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    f"{NATIVE}/inputs/P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    f"{NATIVE}/NATIVE-RECIPES.json.gz": "a1c4d83d3d5fe1338e99b59272e8cf5d43244c33888597da340b2aa7fef5b3e8",
    f"{NATIVE}/check_native.py": "e67b874a061a4a28007b9a0fabaf30c8db4a587b1e1c7dd9396c77ff1e3a9fe6",
    f"{NATIVE}/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "research/p104-joint-unit-flags/CERTIFICATE.json": "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
    f"{REPAIR}/CERTIFICATE.json": "6ce05cee77b6641e9875a0fd07059fb2b41de7733b6e770dc673426f70f764b1",
    f"{REPAIR}/REPAIR-RECIPES.json": "d6dd5a7aade3206dcf7ccd9876dd143627b9d91ba8a41d7f71df26b437b988fd",
}
FLAG_INDEX = 43
CUT = 3525
SELECTED_KAPPA = "0.001672660197076918"
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]
W6 = [95, 447, 6, 32, 20, 15]
PRIVATE_SPAN = (2461, 2524)
MARKER = (
    "PASS_P104_FLAG43_SIDE_CORRECTION_BILL flag=43 entry=(59,21) coefficient=-1/2 "
    "zero_mass_placements=0/28 forcing=625:X12(131)->884:G9->X21 strict_min_added_rank=2 "
    "T=+1transport+1add+2rank(H1-H2+H3) S=+2transport+1add+2rank(2H1) "
    "P=+1transport+1add+1rank(H1)+1private_lifetime T48=+1transport+48add+2rank row59=identity "
    "cohost_discount=0 native_validate=4/4 no_new_kappa"
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
    name = "flag43_side_check_native"
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
    repair = loads(pinned_bytes(root, f"{REPAIR}/CERTIFICATE.json"))
    repair_recipes = loads(pinned_bytes(root, f"{REPAIR}/REPAIR-RECIPES.json"))["recipes"]
    return witness, fixture, recipes, flags, repair, repair_recipes


# --- GF(2) frames -----------------------------------------------------------

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


def join(a, b):
    return canon(tuple(a) + tuple(b))


def inside(a, b):
    return len(join(a, b)) == len(canon(b))


def physical_map(recipes):
    iso = recipes["label_isometry"]
    dual = iso["compressed_dual_gram"]
    orth = iso["orthonormal_basis_compressed"]
    mv = lambda rows, x: sum((((row & x).bit_count()) & 1) << i for i, row in enumerate(rows))
    dot = lambda a, b: (a & mv(dual, b)).bit_count() & 1
    convert = lambda x: sum(dot(x, v) << j for j, v in enumerate(orth))
    return lambda frame: canon(convert(x) for x in frame)


# --- roots -------------------------------------------------------------------

def ports(fixture):
    lines = set()
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            v = [0] * 8
            v[i], v[j] = 2, 2 * sign
            lines.add(tuple(v))
    for signs in itertools.product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            lines.add((1, *signs))
    removed = {tuple(r) for r in fixture["F0"] + fixture["C"]}
    out = [r for r in sorted(lines) if r not in removed]
    need(len(out) == 104, "P104 ports")
    return out


def gram(ps, t, s):
    return sum(x * y for x, y in zip(ps[t], ps[s])) // 4


# --- schedules ---------------------------------------------------------------

def apply_splices(program, splices):
    out = list(program)
    last = len(program) + 1
    for row in sorted(splices, key=lambda r: -r["published_range"][0]):
        start, stop = row["published_range"]
        need(0 <= start < stop <= len(program) and stop <= last, "ordered disjoint splices")
        need(len(row["published"]) == stop - start, "splice covers its range")
        for k, old in enumerate(row["published"]):
            need(program[start + k] == old, "splice binds event %d" % (start + k))
        out[start:stop] = copy.deepcopy(row["events"])
        last = start
    return out


def corrections(r0, final, ps):
    f59 = final["Y59"]
    cut = r0[CUT]
    need(cut == ["transport", "Y59", W6, f59, 2], "R0 terminal Y59 transport at the cut")
    row = [["add", "Y59", "X%d" % s, str(Fraction(-gram(ps, 59, s), 2)), FULL]
           for s in range(104) if s != 59 and gram(ps, 59, s)]

    def one(events):
        return [{"published_range": [CUT, CUT + 1], "published": [cut], "events": events}]
    return {
        "T": {
            "route": "target lift at the co-hosted cut: Y59 leaves the head chart W6 for the full chart, takes the entry from X21 there, then descends to its final hyperplane",
            "splices": one([
                ["transport", "Y59", W6, FULL, 3],
                ["add", "Y59", "X21", "-1/2", FULL],
                ["transport", "Y59", FULL, f59, 1],
            ]),
        },
        "S": {
            "route": "source detour: Y59 takes R0's terminal transport, X21 descends to Y59's final hyperplane for one ADD and returns to the full chart before its next read at 3705",
            "splices": one([
                cut,
                ["transport", "X21", FULL, f59, 1],
                ["add", "Y59", "X21", "-1/2", f59],
                ["transport", "X21", f59, FULL, 1],
            ]),
        },
        "P": {
            "route": "one added private lifetime under the inherited private-copy contract: copy X21 into C at the full chart, descend C to Y59's final hyperplane, deliver, discard",
            "splices": one([
                cut,
                ["zero", "C", FULL],
                ["copy", "C", "X21", FULL],
                ["transport", "C", FULL, f59, 1],
                ["add", "Y59", "C", "-1/2", f59],
                ["erase", "C", f59],
            ]),
        },
        "T48": {
            "route": "whole Y59 row of I - G/2 on the same lift: every off-diagonal source entry -G[59,s]/2 is added while Y59 sits in the full chart",
            "splices": one([["transport", "Y59", W6, FULL, 3]] + row + [["transport", "Y59", FULL, f59, 1]]),
        },
    }


def zeroed(program, base_len, splices):
    out = copy.deepcopy(program)
    start = splices[0]["published_range"][0]
    stop = start + len(out) - base_len + 1
    for i in range(start, stop):
        if out[i][0] == "add":
            out[i][3] = "0"
    return out


def assemble(recipes, program, extra, physical):
    pub = {(tuple(r["old"]), tuple(r["new"])): r for r in recipes["transports"]}
    more = {}
    for r in extra:
        key = (tuple(r["old"]), tuple(r["new"]))
        need(key not in more and key not in pub, "extra recipes are unique new edges")
        more[key] = r
    edges = {}
    for i, e in enumerate(program):
        if e[0] == "transport":
            edges.setdefault((physical(e[2]), physical(e[3])), []).append(i)
    used = set()
    out = []
    for key in sorted(edges):
        if key in pub:
            rec = dict(pub[key])
        else:
            need(key in more, "missing native recipe for edge")
            rec = dict(more[key])
            used.add(key)
        rec["events"] = edges[key]
        out.append(rec)
    profile = {}
    for rec in out:
        profile[rec["rank"]] = profile.get(rec["rank"], 0) + len(rec["events"])
    c = dict(recipes)
    c["transports"] = out
    c["paid_profile"] = {str(k): v for k, v in sorted(profile.items())}
    return c, used


def bill(result, program):
    profile = {str(k): v for k, v in sorted(result["paid_profile"].items())}
    return {
        "events": len(program),
        "scalar_adds": result["scalar_events"]["add"],
        "private_events": {k: result["scalar_events"].get(k, 0) for k in ("zero", "copy", "erase")},
        "transport_occurrences": sum(profile.values()),
        "rank_mass": result["rank_mass"],
        "paid_profile": profile,
        "distinct_native_edges": result["transports"],
        "endpoint_adapters": result["intrinsic_endpoint_adapters"],
    }


def delta(a, b):
    out = {}
    for k in sorted({int(x) for x in a["paid_profile"]} | {int(x) for x in b["paid_profile"]}):
        d = b["paid_profile"].get(str(k), 0) - a["paid_profile"].get(str(k), 0)
        if d:
            out[str(k)] = d
    return out


def rows(witness, program):
    state = {n: {n: Fraction(1)} for n in witness["initial_frames"]}
    for e in program:
        if e[0] == "zero":
            state[e[1]] = {}
        elif e[0] == "erase":
            state.pop(e[1])
        elif e[0] == "copy":
            state[e[1]] = dict(state[e[2]])
        elif e[0] == "add":
            _, dst, src, a, _f = e
            for name, v in list(state[src].items()):
                z = state[dst].get(name, Fraction(0)) + Fraction(a) * v
                if z:
                    state[dst][name] = z
                else:
                    state[dst].pop(name, None)
    return state


def register_mass(program):
    out = {}
    for e in program:
        if e[0] == "transport":
            out[e[1]] = out.get(e[1], 0) + e[4]
    return out


# --- least monotone lower bounds ---------------------------------------------

def sweep(witness, program, inject=None):
    """Least frames of a zero-added-mass repair; C is left unconstrained.

    inject = (u, a, b): registers a and b share one frame just before event u.
    inject = (u, None, b, frame): register b contains `frame` from event u on.
    Returns the first event/register whose forced frame leaves its final frame.
    """
    init = {k: canon(v) for k, v in witness["initial_frames"].items()}
    final = {k: canon(v) for k, v in witness["final_frames"].items()}
    cur = dict(init)
    for i in range(len(program) + 1):
        if inject and i == inject[0]:
            if inject[1] is None:
                cur[inject[2]] = join(cur[inject[2]], inject[3])
                touched = (inject[2],)
            else:
                m = join(cur[inject[1]], cur[inject[2]])
                cur[inject[1]] = cur[inject[2]] = m
                touched = inject[1:3]
            for r in touched:
                if not inside(cur[r], final[r]):
                    return [i, r]
        if i == len(program):
            break
        e = program[i]
        if e[0] == "add" and "C" not in e[1:3]:
            m = join(cur[e[1]], cur[e[2]])
            cur[e[1]] = cur[e[2]] = m
            for r in e[1:3]:
                if not inside(m, final[r]):
                    return [i, r]
    return None


def forced_frames(witness, program, reg):
    init = {k: canon(v) for k, v in witness["initial_frames"].items()}
    cur = dict(init)
    out = []
    for i, e in enumerate(program):
        if e[0] == "add" and "C" not in e[1:3]:
            m = join(cur[e[1]], cur[e[2]])
            cur[e[1]] = cur[e[2]] = m
            if reg in e[1:3]:
                out.append([i, e[1] if e[2] == reg else e[2], len(m)])
    return out


def cut_classes(program, regs):
    ev = [i for i, e in enumerate(program) if e[0] in ("add", "copy") and set(regs) & {e[1], e[2]}]
    return sorted({0} | {i + 1 for i in ev})


# --- receipt -----------------------------------------------------------------

def receipt(root, cert, new_recipes):
    ck = load_checker(root)
    witness, fixture, recipes, flags, repair, repair_recipes = load_inputs(root)
    helper = flags["helpers"][FLAG_INDEX]
    head = helper["basis"][0]
    need(("X%d" % helper["source"], "Y%d" % helper["target"], head) == ("X21", "Y59", 15), "flag 43 identity")
    need(repair["claim_id"] == "p104-flag43-head-step-repair", "R0 source")
    ps = ports(fixture)
    physical = physical_map(recipes)
    program = witness["program"]
    final = witness["final_frames"]
    r0 = apply_splices(program, repair["repairs"]["R0"]["splices"])
    need(len(r0) == len(program), "R0 keeps the event count")
    w0 = dict(witness)
    w0["program"] = r0
    c0, _ = assemble(recipes, r0, repair_recipes, physical)
    base = bill(ck.validate(c0, w0, fixture, False), r0)
    pub = bill(ck.validate(recipes, witness, fixture, False), program)
    spec = corrections(r0, final, ps)
    need(cert.get("corrections") == spec, "committed corrections equal the generated ones")
    expected = rows(witness, r0)
    need(all(not (e[0] in ("add", "copy") and e[2] == "Y59") for e in r0), "Y59 is never read")
    extra = list(repair_recipes) + list(new_recipes)
    new_keys = {(tuple(r["old"]), tuple(r["new"])) for r in new_recipes}
    need(len(new_keys) == len(new_recipes), "unique correction recipes")
    used_all = set()
    out = {}
    for name in ("T", "S", "P", "T48"):
        prog = apply_splices(r0, spec[name]["splices"])
        zero = zeroed(prog, len(r0), spec[name]["splices"])
        wz = dict(witness)
        wz["program"] = zero
        cz, used = assemble(recipes, zero, extra, physical)
        used_all |= used & new_keys
        res = ck.validate(cz, wz, fixture, False)
        b = bill(res, prog)
        wr = dict(witness)
        wr["program"] = prog
        try:
            ck.validate(cz, wr, fixture, False)
        except ValueError as exc:
            rejection = str(exc)
        else:
            rejection = None
        got = rows(witness, prog)
        changed = sorted(k for k in expected if got.get(k) != expected[k])
        y = got["Y59"]
        mass0, mass1 = register_mass(r0), register_mass(prog)
        added_mass = {r: mass1.get(r, 0) - mass0.get(r, 0) for r in sorted(set(mass0) | set(mass1))
                      if mass1.get(r, 0) != mass0.get(r, 0)}
        start = CUT
        stop = CUT + len(prog) - len(r0) + 1
        frames_before = {}
        hist = {}
        for i, e in enumerate(prog[:start]):
            if e[0] == "transport":
                hist[e[1]] = e[3]
        for reg in ("Y59", "X21"):
            frames_before[reg] = list(canon(hist.get(reg, witness["initial_frames"][reg])))
        corr_adds = [e for e in prog[start:stop] if e[0] == "add"]
        out[name] = dict(b)
        out[name].update({
            "native_validate_coefficient_zero": "PASS",
            "real_word_rejected_by_unchanged_checker_at": rejection,
            "changed_final_rows": changed,
            "Y59_final_X21": str(y.get("X21", Fraction(0))),
            "Y59_final_row_is_identity": y == {"Y59": Fraction(1), "X59": Fraction(1)},
            "correction_adds": len(corr_adds),
            "correction_charts": sorted({len(canon(e[4])) for e in corr_adds}),
            "head_in_correction_charts": all(inside([head], e[4]) for e in corr_adds),
            "added_rank_by_register": added_mass,
            "head_in_target_frame_before_correction": inside([head], frames_before["Y59"]),
            "head_in_source_frame_before_correction": inside([head], frames_before["X21"]),
            "target_frame_before_correction_rank": len(frames_before["Y59"]),
            "added_vs_R0": {k: b[k] - base[k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")},
            "profile_delta_vs_R0": delta(base, b),
            "profile_delta_vs_published": delta(pub, b),
        })
    need(len(used_all) == len(new_recipes), "every committed correction recipe is used")

    # Forcing chain and the zero-added-mass obstruction.
    init = witness["initial_frames"]
    f59 = canon(final["Y59"])
    first_read = [i for i, e in enumerate(program) if e[0] == "add" and e[2] == "X21"][0]
    partner = program[first_read][1]
    feeders = [i for i, e in enumerate(program[:first_read])
               if e[0] == "add" and e[1] == partner and e[2].startswith("X")]
    need(len(feeders) == 1, "one source feeds the partner before the first read")
    feeder = feeders[0]
    src12 = program[feeder][2]
    head12 = canon(init[src12])
    lb = forced_frames(witness, program, "X21")
    full_from = [i for i, _p, r in lb if r == 9][0]
    cuts = cut_classes(program, ("X21", "Y59"))
    direct = [[u, sweep(witness, program, (u, "X21", "Y59"))] for u in cuts]
    need(all(x[1] for x in direct), "every direct placement is obstructed")
    early = [u for u in cut_classes(program, ("Y59",)) if u < PRIVATE_SPAN[0]]
    private = [[u, sweep(witness, program, (u, None, "Y59", canon([head])))] for u in early]
    need(all(x[1] for x in private), "every early private delivery is obstructed")
    need(sweep(witness, program) is None and sweep(witness, r0) is None, "published and R0 feasible")
    nz = [s for s in range(104) if s != 59 and gram(ps, 59, s)]
    pub_cut = program[CUT]
    obstruction = {
        "entry": {"target": "Y59", "source": "X21", "gram": gram(ps, 59, 21), "correction_coefficient": str(Fraction(-gram(ps, 59, 21), 2)), "diagonal_gram": gram(ps, 59, 59)},
        "row_59_offdiagonal_nonzero": len(nz),
        "source_first_read": [first_read, program[first_read][:4]],
        "partner_feeder": [feeder, program[feeder][:4]],
        "feeder_source_head": list(head12),
        "feeder_source_gram_with_target": gram(ps, 59, int(src12[1:])),
        "feeder_head_in_target_final": inside(head12, f59),
        "flag_head_in_target_final": inside([head], f59),
        "source_forced_rank_at_events": lb,
        "source_forced_full_from": full_from,
        "direct_cut_classes": len(cuts),
        "direct_first_obstruction": direct,
        "private_early_delivery_cuts": len(private),
        "private_early_first_obstruction": private,
        "published_private_lifetimes": list(PRIVATE_SPAN),
        "non_private_registers_at_rank_floor": sum(
            1 for r in init if register_mass(program).get(r, 0) == len(canon(final[r])) - len(canon(init[r]))),
    }
    end_cut_detour = {
        "published_terminal_transport": [CUT, pub_cut[4]],
        "published_detour_via_full_rank": (9 - len(canon(pub_cut[2]))) + (9 - len(f59)),
        "published_detour_added_rank": (9 - len(canon(pub_cut[2]))) + (9 - len(f59)) - pub_cut[4],
        "R0_detour_added_rank": out["T"]["added_vs_R0"]["rank_mass"],
    }
    return {
        "schema_version": 1,
        "claim_id": "p104-flag43-side-correction-bill",
        "pinned_main": "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "requested_pin": "6f100d4bb5083f8c35d96fd95a539811c62f245c",
        "flag_index": FLAG_INDEX,
        "basis_head": head,
        "cut_event": CUT,
        "corrections": spec,
        "bill": {"published": pub, "R0": base, **out},
        "obstruction": obstruction,
        "end_cut_detour": end_cut_detour,
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }


def admit(root, cert, new_recipes):
    got = json.loads(json.dumps(receipt(root, cert, new_recipes)))
    need(got == cert, "receipt differs from committed certificate")
    b, ob = cert["bill"], cert["obstruction"]
    need(ob["entry"] == {"target": "Y59", "source": "X21", "gram": 1, "correction_coefficient": "-1/2", "diagonal_gram": 2}, "entry")
    need(ob["source_first_read"][0] == 884 and ob["partner_feeder"][0] == 625, "forcing chain events")
    need(ob["feeder_source_head"] == [131] and ob["feeder_source_gram_with_target"] == 0, "X12 head orthogonal to r59")
    need(not ob["feeder_head_in_target_final"] and ob["flag_head_in_target_final"], "131 outside, 15 inside F59")
    need(ob["source_forced_full_from"] == 1708, "X21 forced full from 1708")
    need(ob["direct_cut_classes"] == 28 and all(x[1] for x in ob["direct_first_obstruction"]), "28/28 obstructed")
    need(ob["non_private_registers_at_rank_floor"] == 280, "rank floor")
    for name, want in (("T", [2, 1, 1, 2]), ("S", [3, 1, 2, 2]), ("P", [5, 1, 1, 1]), ("T48", [49, 48, 1, 2])):
        r = b[name]
        need([r["added_vs_R0"][k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")] == want, name + " bill")
        need(r["native_validate_coefficient_zero"] == "PASS", name + " native")
        need(r["real_word_rejected_by_unchanged_checker_at"] == "full physical boundary endpoint Y59", name + " rejection site")
        need(r["changed_final_rows"] == ["Y59"], name + " only Y59 changes")
        need(r["head_in_target_frame_before_correction"] and r["head_in_source_frame_before_correction"], name + " co-hosted")
    need(b["T"]["profile_delta_vs_R0"] == {"1": 1, "2": -1, "3": 1}, "T profile")
    need(b["S"]["profile_delta_vs_R0"] == {"1": 2}, "S profile")
    need(b["P"]["profile_delta_vs_R0"] == {"1": 1}, "P profile")
    need(b["P"]["private_events"] == {"zero": 9, "copy": 9, "erase": 9}, "P private lifetime")
    need(b["T"]["Y59_final_X21"] == b["S"]["Y59_final_X21"] == b["P"]["Y59_final_X21"] == "0", "entry applied")
    need(b["T48"]["Y59_final_row_is_identity"], "row 59 becomes y + x")
    need(b["T"]["added_rank_by_register"] == {"Y59": 2} and b["S"]["added_rank_by_register"] == {"X21": 2}, "even per-register mass")
    need(b["T"]["target_frame_before_correction_rank"] == 6, "correction leaves the rank-6 head chart")
    need(cert["end_cut_detour"]["published_detour_added_rank"] == cert["end_cut_detour"]["R0_detour_added_rank"] == 2, "co-host discount zero")
    need(cert["selected_kappa"] == SELECTED_KAPPA and cert["no_new_kappa"] is True, "kappa unchanged")
    return got


def main(root=ROOT):
    cert = loads((HERE / "CERTIFICATE.json").read_bytes())
    new_recipes = loads((HERE / "CORRECTION-RECIPES.json").read_bytes())["recipes"]
    admit(root, cert, new_recipes)
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
