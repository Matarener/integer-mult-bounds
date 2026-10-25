#!/usr/bin/env python3
"""Read-only replay of the flag-1 side-correction bill at #3532's co-hosted charts.

Builds #3532's repairs R0 (order-preserving, Y7 += D17/4 in [95,486,232]) and
R1 (relocated, the same ADD in the full chart) from the vendored, hash-pinned
splices, then adds the (7, 0) entry of I - G/2 (Y7 += +1/2 X0) and, for the
row variants, the whole Y7 row. For each corrected word it runs the published
check_native.validate() unchanged on the coefficient-0 copy (chart legality,
native edges, endpoint adapters and all 280 framed rows do not depend on the
inserted coefficient), replays the real word with exact rational rows, and
confirms that validate() rejects the real word only at Y7's endpoint. It then
recomputes the bills, the X7 -> X20 -> G18 -> X0 forcing chain, the least-frame
sweep that rules out a zero-added-mass correction at every insertion class and
every placement of the delivering ADD, and the single-register census that
rules out an order-preserving co-hosted correction at +2. Admission uses need()
and stays active under python -O. Nothing is written.
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
PKG = HERE.relative_to(ROOT).as_posix()
NATIVE = "research/p104-native-channel"
PR3532 = f"{PKG}/inputs/pr3532"
PINS = {
    f"{NATIVE}/inputs/LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    f"{NATIVE}/inputs/P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    f"{NATIVE}/NATIVE-RECIPES.json.gz": "a1c4d83d3d5fe1338e99b59272e8cf5d43244c33888597da340b2aa7fef5b3e8",
    f"{NATIVE}/check_native.py": "e67b874a061a4a28007b9a0fabaf30c8db4a587b1e1c7dd9396c77ff1e3a9fe6",
    f"{NATIVE}/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "research/p104-joint-unit-flags/CERTIFICATE.json": "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
    f"{PR3532}/CERTIFICATE.json": "5f29955e692d3fdb628ab0562c87defd21318c31cc2a8cafd6693f8004404359",
    f"{PR3532}/REPAIR-RECIPES.json": "13d2b2f45d75697d137aca1baf953b2bdf482bc8b02da6887ebb492f18470209",
}
FLAG_INDEX = 1
DELIVERY = 2797
SELECTED_KAPPA = "0.001672660197076918"
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]
A2 = [95, 486]
A3 = [95, 486, 232]
PRIVATE_SPAN = (2461, 2524)
MARKER = (
    "PASS_P104_FLAG1_SIDE_CORRECTION_BILL flag=1 entry=(7,0) gram=-1 coefficient=+1/2 "
    "zero_mass_placements=0/18(delivery_anywhere_in_1116_slots) forcing=X7(387)-616-G11-679-X20-1070-G18-1074-X0 "
    "strict_min_added_rank=2 "
    "R0:T=+1transport+1add+2rank S=+2transport+1add+2rank P=+1rank+1private_lifetime Trow=+48add+2rank "
    "R1:E=+0transport+1add+0rank Erow=+48add+0rank row7=identity "
    "cohost_discount_R0=0 cohost_discount_R1=2 joint_min_relocated=2 joint_min_order_preserving_strict=4 "
    "native_validate=7/7 no_new_kappa"
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
    name = "flag1_side_check_native"
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
    repair = loads(pinned_bytes(root, f"{PR3532}/CERTIFICATE.json"))
    repair_recipes = loads(pinned_bytes(root, f"{PR3532}/REPAIR-RECIPES.json"))["recipes"]
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


def is_correction(e):
    return e[0] == "add" and e[1] == "Y7" and (e[2].startswith("X") or e[2] == "C")


def last_transport(program, reg):
    return max(i for i, e in enumerate(program) if e[0] == "transport" and e[1] == reg)


def delivering_add(program):
    hits = [i for i, e in enumerate(program) if e[0] == "add" and e[1] == "Y7" and e[2] == "D17" and e[3] == "1/4"]
    need(len(hits) == 1, "one delivering Y7 += D17/4")
    return hits[0]


def corrections(program, r0, r1, final, ps):
    f7 = final["Y7"]
    row = [["add", "Y7", "X%d" % s, str(Fraction(-gram(ps, 7, s), 2)), FULL]
           for s in range(104) if s != 7 and gram(ps, 7, s)]
    entry = ["add", "Y7", "X0", str(Fraction(-gram(ps, 7, 0), 2)), FULL]

    def one(base, at, events):
        return [{"published_range": [at, at + 1], "published": [base[at]], "events": events}]

    c0 = last_transport(r0, "Y7")
    need(r0[c0] == ["transport", "Y7", A3, r0[c0][3], 5], "R0 terminal Y7 transport leaves the rank-3 co-hosted chart")
    t7 = r0[c0][3]
    need(canon(t7) == canon(f7), "terminal chart is Y7's final frame")
    d1 = delivering_add(r1)
    need(r1[d1] == ["add", "Y7", "D17", "1/4", FULL], "R1 delivers in the full chart")
    cp = last_transport(program, "Y7")
    need(program[cp] == ["transport", "Y7", A2, t7, 6], "published terminal Y7 transport")
    lift0 = [["transport", "Y7", A3, FULL, 6]]
    drop = [["transport", "Y7", FULL, t7, 1]]
    return {
        "R0": {
            "T": {
                "route": "target lift at R0's cut: Y7 leaves the co-hosted chart [95,486,232] for the full chart, takes the entry from X0 there, then descends to its final hyperplane",
                "splices": one(r0, c0, lift0 + [entry] + drop),
            },
            "S": {
                "route": "source detour: Y7 takes R0's terminal transport, X0 descends to Y7's final hyperplane for one ADD and returns to the full chart before its next read",
                "splices": one(r0, c0, [r0[c0], ["transport", "X0", FULL, t7, 1],
                                        ["add", "Y7", "X0", entry[3], t7], ["transport", "X0", t7, FULL, 1]]),
            },
            "P": {
                "route": "one added private lifetime under the inherited private-copy contract: copy X0 into C at the full chart, descend C to Y7's final hyperplane, deliver, discard",
                "splices": one(r0, c0, [r0[c0], ["zero", "C", FULL], ["copy", "C", "X0", FULL],
                                        ["transport", "C", FULL, t7, 1], ["add", "Y7", "C", entry[3], t7],
                                        ["erase", "C", t7]]),
            },
            "Trow": {
                "route": "whole Y7 row of I - G/2 on T's lift: every off-diagonal source entry -G[7,s]/2 is added while Y7 sits in the full chart",
                "splices": one(r0, c0, lift0 + row + drop),
            },
        },
        "R1": {
            "E": {
                "route": "in-chart entry at R1's co-hosted update: Y7 and X0 already share the full chart at the relocated delivering ADD, so the entry is one extra ADD there",
                "splices": one(r1, d1, [r1[d1], entry]),
            },
            "Erow": {
                "route": "whole Y7 row of I - G/2 at R1's co-hosted update: all 48 off-diagonal entries are added in the full chart right after the delivering ADD",
                "splices": one(r1, d1, [r1[d1]] + row),
            },
        },
        "published": {
            "Tend": {
                "route": "end-cut control on the published word: Y7 leaves [95,486] for the full chart at its terminal transport, takes the entry there, then descends",
                "splices": one(program, cp, [["transport", "Y7", A2, FULL, 7], entry] + drop),
            },
        },
    }


def zeroed(program):
    out = copy.deepcopy(program)
    for e in out:
        if is_correction(e):
            e[3] = "0"
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


def added(a, b):
    return {k: b[k] - a[k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")}


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


def frames_before(witness, program, at, regs):
    hist = {}
    for e in program[:at]:
        if e[0] == "transport":
            hist[e[1]] = e[3]
    return {r: list(canon(hist.get(r, witness["initial_frames"][r]))) for r in regs}


# --- least monotone lower bounds ---------------------------------------------

def sweep(witness, program, inject=(), skip=(), relax=()):
    """Least frames of a repair in which every non-relaxed non-private path is monotone.

    The private register C and every register in `relax` are left unconstrained
    (their ADDs impose nothing), which only removes constraints. Events in `skip`
    are dropped, which also only removes constraints. inject = [(u, regs, extra)]:
    just before event u the listed registers share one frame that also contains
    `extra`. Returns [event, register] for the first forced frame that leaves the
    register's final frame, or None.
    """
    free = {"C"} | set(relax)
    init = {k: canon(v) for k, v in witness["initial_frames"].items()}
    final = {k: canon(v) for k, v in witness["final_frames"].items()}
    cur = dict(init)
    at = {}
    for u, regs, extra in inject:
        at.setdefault(u, []).append(([r for r in regs if r not in free], tuple(extra)))
    for i in range(len(program) + 1):
        for regs, extra in at.get(i, ()):
            m = canon(extra + tuple(x for r in regs for x in cur[r]))
            for r in regs:
                cur[r] = m
            for r in regs:
                if not inside(m, final[r]):
                    return [i, r]
        if i == len(program):
            break
        e = program[i]
        if i in skip or e[0] != "add" or free & {e[1], e[2]}:
            continue
        m = join(cur[e[1]], cur[e[2]])
        cur[e[1]] = cur[e[2]] = m
        for r in e[1:3]:
            if not inside(m, final[r]):
                return [i, r]
    return None


def forced_frames(witness, program, reg):
    cur = {k: canon(v) for k, v in witness["initial_frames"].items()}
    out = []
    for i, e in enumerate(program):
        if e[0] == "add" and "C" not in e[1:3]:
            m = join(cur[e[1]], cur[e[2]])
            cur[e[1]] = cur[e[2]] = m
            if reg in e[1:3]:
                out.append([i, e[1] if e[2] == reg else e[2], len(m)])
    return out


def head_chain(witness, program, source, stop):
    """Earliest time-respecting ADD chain carrying `source`'s head into each register before `stop`."""
    came = {source: None}
    for i, e in enumerate(program[:stop]):
        if e[0] != "add" or "C" in e[1:3]:
            continue
        a, b = e[1], e[2]
        if (a in came) != (b in came):
            new, old = (a, b) if b in came else (b, a)
            came[new] = (i, old)
    return came


def trace(came, reg):
    out = []
    while came.get(reg) is not None:
        i, prev = came[reg]
        out.append([i, prev, reg])
        reg = prev
    return out[::-1]


def classes(program, regs, skip=()):
    ev = [i for i, e in enumerate(program)
          if i not in skip and e[0] in ("add", "copy") and set(regs) & {e[1], e[2]}]
    return sorted({0} | {i + 1 for i in ev})


# --- receipt -----------------------------------------------------------------

def receipt(root, cert, new_recipes):
    ck = load_checker(root)
    witness, fixture, recipes, flags, repair, repair_recipes = load_inputs(root)
    helper = flags["helpers"][FLAG_INDEX]
    head = helper["basis"][0]
    need(("X%d" % helper["source"], "Y%d" % helper["target"], head) == ("X0", "Y7", 232), "flag 1 identity")
    need(repair["claim_id"] == "p104-flag1-head-step-repair", "R0/R1 source is #3532")
    ps = ports(fixture)
    physical = physical_map(recipes)
    program = witness["program"]
    final = witness["final_frames"]
    f7 = canon(final["Y7"])
    bases = {"published": program}
    for name in ("R0", "R1"):
        bases[name] = apply_splices(program, repair["repairs"][name]["splices"])
    base_bill = {"published": bill(ck.validate(recipes, witness, fixture, False), program)}
    for name in ("R0", "R1"):
        w = dict(witness)
        w["program"] = bases[name]
        c, _ = assemble(recipes, bases[name], repair_recipes, physical)
        base_bill[name] = bill(ck.validate(c, w, fixture, False), bases[name])
    spec = corrections(program, bases["R0"], bases["R1"], final, ps)
    need(cert.get("corrections") == spec, "committed corrections equal the generated ones")
    need(all(not (e[0] in ("add", "copy") and e[2] == "Y7") for b in bases.values() for e in b), "Y7 is never read")
    extra = list(repair_recipes) + list(new_recipes)
    new_keys = {(tuple(r["old"]), tuple(r["new"])) for r in new_recipes}
    need(len(new_keys) == len(new_recipes), "unique correction recipes")
    used_all = set()
    out = {}
    for base_name, group in spec.items():
        base = bases[base_name]
        expected = rows(witness, base)
        mass0 = register_mass(base)
        for name, item in group.items():
            prog = apply_splices(base, item["splices"])
            zero = zeroed(prog)
            wz = dict(witness)
            wz["program"] = zero
            cz, used = assemble(recipes, zero, extra, physical)
            used_all |= used & new_keys
            b = bill(ck.validate(cz, wz, fixture, False), prog)
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
            y = got["Y7"]
            mass1 = register_mass(prog)
            added_mass = {r: mass1.get(r, 0) - mass0.get(r, 0) for r in sorted(set(mass0) | set(mass1))
                          if mass1.get(r, 0) != mass0.get(r, 0)}
            at = item["splices"][0]["published_range"][0]
            fb = frames_before(witness, prog, at, ("Y7", "X0"))
            corr = [e for e in prog if is_correction(e)]
            hist = {}
            for i, e in enumerate(prog):
                if e[0] == "transport":
                    hist[e[1]] = e[3]
                if e[0] == "add" and e[1] == "Y7" and e[2] == "D17" and e[3] == "1/4":
                    deliver_chart = canon(e[4])
            r = dict(b)
            r.update({
                "base": base_name,
                "native_validate_coefficient_zero": "PASS",
                "real_word_rejected_by_unchanged_checker_at": rejection,
                "changed_final_rows": changed,
                "Y7_final_X0": str(y.get("X0", Fraction(0))),
                "Y7_final_row_is_identity": y == {"Y7": Fraction(1), "X7": Fraction(1)},
                "correction_adds": len(corr),
                "correction_chart_ranks": sorted({len(canon(e[4])) for e in corr}),
                "head_in_correction_charts": all(inside([head], e[4]) for e in corr),
                "delivering_update_chart_rank": len(deliver_chart),
                "head_in_delivering_update_chart": inside([head], deliver_chart),
                "added_rank_by_register": added_mass,
                "Y7_frame_rank_before_correction": len(fb["Y7"]),
                "X0_frame_rank_before_correction": len(fb["X0"]),
                "added_vs_base": added(base_bill[base_name], b),
                "added_vs_published": added(base_bill["published"], b),
                "profile_delta_vs_base": delta(base_bill[base_name], b),
            })
            out[name] = r
    need(len(used_all) == len(new_recipes), "every committed correction recipe is used")

    # Forcing chain and the zero-added-mass obstruction.
    init = witness["initial_frames"]
    lb = forced_frames(witness, program, "X0")
    leave = [i for i, e in enumerate(program) if e[0] == "add" and "X0" in e[1:3]]
    cur = {k: canon(v) for k, v in init.items()}
    leave_at = None
    for i, e in enumerate(program):
        if e[0] == "add" and "C" not in e[1:3]:
            m = join(cur[e[1]], cur[e[2]])
            cur[e[1]] = cur[e[2]] = m
            if "X0" in e[1:3] and not inside(m, f7):
                leave_at = i
                leave_frame = m
                break
    need(leave_at is not None and leave_at in leave, "X0's forced frame leaves final(Y7) at an X0 read")
    partner = program[leave_at][1]
    outside = sorted(s for s in range(104) if not inside(canon(init["X%d" % s]), f7))
    reach = {}
    for s in outside:
        came = head_chain(witness, program, "X%d" % s, leave_at + 1)
        if "X0" in came:
            reach["X%d" % s] = trace(came, "X0")
    need(len(reach) == 1, "one outside head reaches X0 at its exit")
    (witness_source, chain), = reach.items()
    dskip = {DELIVERY}
    cls = classes(program, ("X0", "Y7"), skip=dskip)
    strict = [[u, sweep(witness, program, inject=[(u, ("X0", "Y7"), ())], skip=dskip)] for u in cls]
    need(all(x[1] for x in strict), "every strict placement is obstructed")
    strict_pub = [[u, sweep(witness, program, inject=[(u, ("X0", "Y7"), ())])] for u in classes(program, ("X0", "Y7"))]
    early = [u for u in classes(program, ("Y7",), skip=dskip) if u < PRIVATE_SPAN[0]]
    private = [[u, sweep(witness, program, inject=[(u, ("Y7",), (head,))], skip=dskip)] for u in early]
    need(all(x[1] for x in private), "every early private delivery is obstructed")
    need(all(sweep(witness, b) is None for b in bases.values()), "published, R0 and R1 feasible")
    need(sweep(witness, program, skip=dskip) is None, "published feasible without the delivering ADD")
    force = (DELIVERY, ("Y7", "D17"), (head,))
    regs = sorted(init)
    cohost_rescue = [r for r in regs if sweep(witness, program, inject=[force], relax=(r,)) is None]
    need(sweep(witness, program, inject=[force]) is not None, "order-preserving co-hosting needs added mass")
    joint = {}
    for r in [None] + cohost_rescue:
        rel = () if r is None else (r,)
        joint["none" if r is None else r] = [
            [u, sweep(witness, program, inject=[force, (u, ("X0", "Y7"), ())], relax=rel)]
            for u in classes(program, ("X0", "Y7"))]
    need(all(x[1] for v in joint.values() for x in v), "no single-register order-preserving joint repair")
    nz = [s for s in range(104) if s != 7 and gram(ps, 7, s)]
    obstruction = {
        "entry": {"target": "Y7", "source": "X0", "gram": gram(ps, 7, 0),
                  "correction_coefficient": str(Fraction(-gram(ps, 7, 0), 2)), "diagonal_gram": gram(ps, 7, 7)},
        "row_7_offdiagonal_nonzero": len(nz),
        "target_final_frame": list(f7),
        "flag_head_in_target_final": inside([head], f7),
        "sources_with_head_outside_target_final": len(outside),
        "outside_heads_have_even_gram": all(gram(ps, 7, s) % 2 == 0 for s in outside),
        "source_first_read": [leave[0], program[leave[0]][:4]],
        "source_leaves_target_final_at": [leave_at, program[leave_at][:4]],
        "source_forced_frame_at_exit": list(leave_frame),
        "exit_partner": partner,
        "forcing_source": witness_source,
        "forcing_source_head": list(canon(init[witness_source])),
        "forcing_source_gram_with_target": gram(ps, 7, int(witness_source[1:])),
        "forcing_chain": chain,
        "source_forced_rank_at_events": lb,
        "source_forced_full_from": [i for i, _p, r in lb if r == 9][0],
        "delivering_add_dropped_in_sweeps": DELIVERY,
        "delivering_add_window_slots": 1116,
        "strict_cut_classes": len(cls),
        "strict_first_obstruction": strict,
        "strict_published_order_first_obstruction": strict_pub,
        "private_early_delivery_cuts": len(private),
        "private_early_first_obstruction": private,
        "published_private_lifetimes": list(PRIVATE_SPAN),
        "non_private_registers_at_rank_floor": sum(
            1 for r in init if register_mass(program).get(r, 0) == len(canon(final[r])) - len(canon(init[r]))),
        "order_preserving_cohost_single_register_rescues": cohost_rescue,
        "order_preserving_joint_first_obstruction": joint,
    }
    pub_cut = program[last_transport(program, "Y7")]
    r0_cut = bases["R0"][last_transport(bases["R0"], "Y7")]
    end_cut = {
        "published_terminal_transport": [last_transport(program, "Y7"), pub_cut[4]],
        "published_detour_added_rank": out["Tend"]["added_vs_base"]["rank_mass"],
        "R0_terminal_transport": [last_transport(bases["R0"], "Y7"), r0_cut[4]],
        "R0_correction_added_rank": out["T"]["added_vs_base"]["rank_mass"],
        "R1_correction_added_rank": out["E"]["added_vs_base"]["rank_mass"],
        "cohost_discount_R0": out["Tend"]["added_vs_base"]["rank_mass"] - out["T"]["added_vs_base"]["rank_mass"],
        "cohost_discount_R1": out["Tend"]["added_vs_base"]["rank_mass"] - out["E"]["added_vs_base"]["rank_mass"],
        "joint_cohosted_and_corrected_vs_published": {
            "R0+T": out["T"]["added_vs_published"]["rank_mass"],
            "R0+S": out["S"]["added_vs_published"]["rank_mass"],
            "R0+P": out["P"]["added_vs_published"]["rank_mass"],
            "R1+E": out["E"]["added_vs_published"]["rank_mass"],
            "published+Tend_not_cohosted": out["Tend"]["added_vs_published"]["rank_mass"],
        },
    }
    return {
        "schema_version": 1,
        "claim_id": "p104-flag1-side-correction-bill",
        "pinned_main": "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "requested_pin": "6f100d4bb5083f8c35d96fd95a539811c62f245c",
        "repair_source": {"pr": 3532, "head": "8fecbf7df7b48c9004bd10a0da6a81f33d455737",
                          "vendored": [f"{PR3532}/CERTIFICATE.json", f"{PR3532}/REPAIR-RECIPES.json"]},
        "flag_index": FLAG_INDEX,
        "basis_head": head,
        "corrections": spec,
        "bill": {"published": base_bill["published"], "R0": base_bill["R0"], "R1": base_bill["R1"], **out},
        "obstruction": obstruction,
        "end_cut_comparison": end_cut,
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }


def admit(root, cert, new_recipes):
    got = json.loads(json.dumps(receipt(root, cert, new_recipes)))
    need(got == cert, "receipt differs from committed certificate")
    b, ob, ec = cert["bill"], cert["obstruction"], cert["end_cut_comparison"]
    need(ob["entry"] == {"target": "Y7", "source": "X0", "gram": -1, "correction_coefficient": "1/2", "diagonal_gram": 2}, "entry")
    need(ob["row_7_offdiagonal_nonzero"] == 48 and ob["flag_head_in_target_final"], "row 7 and head inside F7")
    need(ob["source_first_read"][0] == 840 and ob["source_leaves_target_final_at"][0] == 1074 and ob["exit_partner"] == "G18", "exit event")
    need(ob["forcing_source"] == "X7" and ob["forcing_source_head"] == [387] and ob["forcing_source_gram_with_target"] == 2, "X7 head 387 forces the exit")
    need(ob["forcing_chain"][-2:] == [[1070, "X20", "G18"], [1074, "G18", "X0"]], "chain ends X20 -> G18 -> X0")
    need(ob["source_forced_full_from"] == 1690, "X0 forced full from 1690")
    need(ob["strict_cut_classes"] == 18 and all(x[1] for x in ob["strict_first_obstruction"]), "18/18 strict classes obstructed")
    need(len(ob["strict_published_order_first_obstruction"]) == 19 and all(x[1] for x in ob["strict_published_order_first_obstruction"]), "19/19 published-order classes obstructed")
    need(ob["forcing_chain"][0] == [616, "X7", "G11"], "chain starts at X7")
    need(ob["private_early_delivery_cuts"] == 5 and all(x[1] for x in ob["private_early_first_obstruction"]), "5/5 early private deliveries obstructed")
    need(ob["non_private_registers_at_rank_floor"] == 280, "rank floor")
    need(ob["order_preserving_cohost_single_register_rescues"] == ["D17"], "only D17 rescues order-preserving co-hosting")
    for name, base, want in (("T", "R0", [2, 1, 1, 2]), ("S", "R0", [3, 1, 2, 2]), ("P", "R0", [5, 1, 1, 1]),
                             ("Trow", "R0", [49, 48, 1, 2]), ("E", "R1", [1, 1, 0, 0]), ("Erow", "R1", [48, 48, 0, 0]),
                             ("Tend", "published", [2, 1, 1, 2])):
        r = b[name]
        need(r["base"] == base, name + " base")
        need([r["added_vs_base"][k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")] == want, name + " bill")
        need(r["native_validate_coefficient_zero"] == "PASS", name + " native")
        need(r["real_word_rejected_by_unchanged_checker_at"] == "full physical boundary endpoint Y7", name + " rejection site")
        need(r["changed_final_rows"] == ["Y7"], name + " only Y7 changes")
        need(r["X0_frame_rank_before_correction"] == 9, name + " source in the full chart")
        if name in ("Trow", "Erow"):
            need(r["Y7_final_row_is_identity"] and r["correction_adds"] == 48, name + " row 7 becomes y + x")
        else:
            need(r["Y7_final_X0"] == "0" and r["correction_adds"] == 1, name + " entry applied")
    for name in ("T", "S", "P", "Trow", "E", "Erow"):
        need(b[name]["head_in_delivering_update_chart"], name + " delivering update co-hosts the head")
    need(not b["Tend"]["head_in_delivering_update_chart"], "published delivering update does not co-host")
    need(b["E"]["added_rank_by_register"] == {} and b["Erow"]["added_rank_by_register"] == {}, "E rides free on R1")
    need(b["E"]["correction_chart_ranks"] == [9] and b["E"]["delivering_update_chart_rank"] == 9, "E in R1's full chart")
    need(b["T"]["added_rank_by_register"] == {"Y7": 2} and b["S"]["added_rank_by_register"] == {"X0": 2}, "even per-register mass")
    need(b["P"]["added_rank_by_register"] == {"C": 1} and b["P"]["private_events"] == {"zero": 9, "copy": 9, "erase": 9}, "P private lifetime")
    need(b["T"]["profile_delta_vs_base"] == {"1": 1, "5": -1, "6": 1}, "T profile")
    need(b["S"]["profile_delta_vs_base"] == {"1": 2}, "S profile")
    need(b["E"]["profile_delta_vs_base"] == {} and b["Erow"]["profile_delta_vs_base"] == {}, "E profile unchanged")
    need((ec["cohost_discount_R0"], ec["cohost_discount_R1"]) == (0, 2), "co-host discounts")
    need(ec["joint_cohosted_and_corrected_vs_published"] == {"R0+T": 4, "R0+S": 4, "R0+P": 3, "R1+E": 2,
                                                             "published+Tend_not_cohosted": 2}, "joint bills")
    need(cert["selected_kappa"] == SELECTED_KAPPA and cert["no_new_kappa"] is True, "kappa unchanged")
    return got


def main(root=ROOT):
    cert = loads((HERE / "CERTIFICATE.json").read_bytes())
    new_recipes = loads((HERE / "CORRECTION-RECIPES.json").read_bytes())["recipes"]
    admit(root, cert, new_recipes)
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
