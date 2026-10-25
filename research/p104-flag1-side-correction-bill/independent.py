#!/usr/bin/env python3
"""Independent replay of the flag-1 side-correction bill.

Imports neither verify.py nor check_native.py. Frames are XOR-closed sets of
compressed labels. #3532's R0 and R1 and every corrected word are replayed with
exact rational rows under the channel rules (common-chart ADD and copy, nested
transports paying their frame gap, owned private lifetimes, endpoint frames).
The committed new-edge recipes are checked directly with the pinned
independent Gaussian interpreter. The forced-frame obstruction, the forcing
chain and the order-preserving joint census are recomputed by a separate
forward sweep over closure sets. Key receipts are compared with CERTIFICATE.json.
"""

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
    f"{NATIVE}/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "research/p104-joint-unit-flags/CERTIFICATE.json": "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
    f"{PR3532}/CERTIFICATE.json": "5f29955e692d3fdb628ab0562c87defd21318c31cc2a8cafd6693f8004404359",
}
MARKER = (
    "PASS_P104_FLAG1_SIDE_CORRECTION_BILL_INDEPENDENT entry=(7,0) coefficient=+1/2 "
    "strict_classes_obstructed=18/18(delivery_dropped)+19/19(published_order) early_private_obstructed=5/5 "
    "forcing_head=387(X7) R0:T,S,Trow=+2rank P=+1rank R1:E,Erow=+0rank Tend=+2rank "
    "joint_order_preserving_single_rescue=none rows_changed=Y7_only row7=identity new_recipes=3 no_new_kappa"
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def strict(pairs):
    out = {}
    for k, v in pairs:
        need(k not in out, "duplicate JSON key: " + str(k))
        out[k] = v
    return out


def read(root, rel, gz=False):
    raw = (root / rel).read_bytes()
    if rel in PINS:
        need(hashlib.sha256(raw).hexdigest() == PINS[rel], "pin: " + rel)
    return json.loads(gzip.decompress(raw) if gz else raw, object_pairs_hook=strict)


def closure(vectors):
    s = {0}
    for v in vectors:
        if v not in s:
            s |= {x ^ v for x in s}
    return frozenset(s)


def grow(s, vectors):
    s = set(s)
    for v in vectors:
        if v not in s:
            s |= {x ^ v for x in s}
    return frozenset(s)


def dim(s):
    return len(s).bit_length() - 1


def splice(program, rows):
    out = list(program)
    for row in sorted(rows, key=lambda r: -r["published_range"][0]):
        a, b = row["published_range"]
        need(out[a:b] == row["published"], "splice anchor")
        out[a:b] = row["events"]
    return out


def gram_rows(fixture):
    lines = set()
    for i, j in itertools.combinations(range(8), 2):
        for s in (-1, 1):
            v = [0] * 8
            v[i], v[j] = 2, 2 * s
            lines.add(tuple(v))
    for s in itertools.product((-1, 1), repeat=7):
        if s.count(-1) % 2 == 0:
            lines.add((1,) + s)
    gone = {tuple(r) for r in fixture["F0"] + fixture["C"]}
    ps = [r for r in sorted(lines) if r not in gone]
    need(len(ps) == 104, "104 ports")
    return lambda t, s: sum(x * y for x, y in zip(ps[t], ps[s])) // 4


def replay(witness, program, watch=None):
    frames = {n: closure(f) for n, f in witness["initial_frames"].items()}
    rows = {n: {n: Fraction(1)} for n in witness["initial_frames"]}
    paid, adds, private = {}, 0, {"zero": 0, "copy": 0, "erase": 0}
    mass = {}
    shared = []
    for i, e in enumerate(program):
        op = e[0]
        if op == "transport":
            _, r, a, b, k = e
            fa, fb = closure(a), closure(b)
            need(frames[r] == fa, "transport starts at live frame")
            need(fa <= fb or fb <= fa, "nested transport")
            need(abs(dim(fb) - dim(fa)) == k and k > 0, "rank equals frame gap")
            frames[r] = fb
            paid[k] = paid.get(k, 0) + 1
            mass[r] = mass.get(r, 0) + k
        elif op == "zero":
            need(e[1] == "C" and "C" not in frames, "owned private zero")
            frames["C"], rows["C"] = closure(e[2]), {}
            private["zero"] += 1
        elif op == "erase":
            need(frames.get("C") == closure(e[2]), "owned private erase")
            frames.pop("C")
            rows.pop("C")
            private["erase"] += 1
        elif op == "copy":
            need(not rows["C"] and frames["C"] == frames[e[2]] == closure(e[3]), "common-chart copy")
            rows["C"] = dict(rows[e[2]])
            private["copy"] += 1
        else:
            need(op == "add", "known opcode")
            _, dst, src, a, f = e
            need(dst != src and frames[dst] == frames[src] == closure(f), "common-chart add")
            if watch and dst == watch[0] and src == watch[1]:
                shared.append((i, dim(frames[dst])))
            for k, v in rows[src].items():
                z = rows[dst].get(k, Fraction(0)) + Fraction(a) * v
                if z:
                    rows[dst][k] = z
                else:
                    rows[dst].pop(k, None)
            adds += 1
    need("C" not in frames, "private storage closed")
    for n, f in witness["final_frames"].items():
        need(frames[n] == closure(f), "endpoint frame " + n)
    return rows, {"events": len(program), "adds": adds, "transports": sum(paid.values()),
                  "rank_mass": sum(k * v for k, v in paid.items()), "profile": paid,
                  "private": private, "mass": mass, "shared": shared}


def lower_sweep(witness, program, inject=(), skip=(), free=()):
    free = {"C"} | set(free)
    cur = {n: closure(f) for n, f in witness["initial_frames"].items()}
    fin = {n: closure(f) for n, f in witness["final_frames"].items()}
    plan = {}
    for u, regs, extra in inject:
        plan.setdefault(u, []).append(([r for r in regs if r not in free], extra))
    for i in range(len(program) + 1):
        for regs, extra in plan.get(i, ()):
            m = closure(extra)
            for r in regs:
                m = grow(m, cur[r])
            for r in regs:
                cur[r] = m
                if not m <= fin[r]:
                    return i, r
        if i == len(program):
            return None
        e = program[i]
        if i in skip or e[0] != "add" or free & {e[1], e[2]}:
            continue
        a, b = e[1], e[2]
        m = cur[a] if cur[b] <= cur[a] else cur[b] if cur[a] <= cur[b] else grow(cur[a], cur[b])
        cur[a] = cur[b] = m
        for r in (a, b):
            if not m <= fin[r]:
                return i, r


def main(root=ROOT):
    witness = read(root, f"{NATIVE}/inputs/LOWRANK-WITNESS.json")
    fixture = read(root, f"{NATIVE}/inputs/P104-FIXTURE.json")["section4_explicit_P104"]
    recipes = read(root, f"{NATIVE}/NATIVE-RECIPES.json.gz", gz=True)
    flags = read(root, "research/p104-joint-unit-flags/CERTIFICATE.json")
    repair = read(root, f"{PR3532}/CERTIFICATE.json")
    cert = json.loads((HERE / "CERTIFICATE.json").read_bytes(), object_pairs_hook=strict)
    new = json.loads((HERE / "CORRECTION-RECIPES.json").read_bytes(), object_pairs_hook=strict)["recipes"]
    raw = (root / NATIVE / "vendor/native_verify.py").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[f"{NATIVE}/vendor/native_verify.py"], "interpreter pin")
    spec = importlib.util.spec_from_file_location("flag1_side_independent_native", root / NATIVE / "vendor/native_verify.py")
    N = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(N)

    flag = flags["helpers"][1]
    need((flag["source"], flag["target"], flag["basis"][0]) == (0, 7, 232), "flag 1")
    G = gram_rows(fixture)
    need(G(7, 0) == -1 and G(7, 7) == 2, "Gram entries")
    program = witness["program"]
    f7 = closure(witness["final_frames"]["Y7"])
    need(232 in f7, "head inside F7")
    bases = {"published": program}
    for name in ("R0", "R1"):
        bases[name] = splice(program, repair["repairs"][name]["splices"])
    rows_b, bill_b = {}, {}
    for name, prog in bases.items():
        rows_b[name], bill_b[name] = replay(witness, prog)
    for t in range(104):
        want = {"Y%d" % t: Fraction(1)}
        want.update({"X%d" % s: Fraction(G(t, s), 2) for s in range(104) if G(t, s)})
        need(all(rows_b[n]["Y%d" % t] == want for n in bases), "base target rows G/2")
    need([bill_b[n]["rank_mass"] for n in ("published", "R0", "R1")] == [2368, 2370, 2370], "base rank mass")

    iso = recipes["label_isometry"]
    dual, orth = iso["compressed_dual_gram"], iso["orthonormal_basis_compressed"]

    def to_phys(x):
        dx = sum((((row & x).bit_count()) & 1) << i for i, row in enumerate(dual))
        return sum((((v & dx).bit_count()) & 1) << j for j, v in enumerate(orth))

    phys = lambda f: closure(to_phys(x) for x in f)
    for rec in new:
        need(rec["rank"] == abs(len(rec["old"]) - len(rec["new"])) == rec["recipe"]["rank"], "recipe rank")
        N.equal(N.recipe(rec["recipe"]), N.adjoint(N.frame(tuple(rec["old"]), 9)) + N.frame(tuple(rec["new"]), 9), "new native edge")
    full = [1 << k for k in range(9)]
    keys = {(closure(r["old"]), closure(r["new"])) for r in new}
    want_keys = {(phys(witness["final_frames"]["Y7"]), phys(full)), (phys([95, 486, 232]), phys(full)), (phys([95, 486]), phys(full))}
    need(keys == want_keys, "new edges are F7->FULL, A3->FULL and A2->FULL")

    want = {"T": ("R0", (2, 1, 1, 2)), "S": ("R0", (3, 1, 2, 2)), "P": ("R0", (5, 1, 1, 1)),
            "Trow": ("R0", (49, 48, 1, 2)), "E": ("R1", (1, 1, 0, 0)), "Erow": ("R1", (48, 48, 0, 0)),
            "Tend": ("published", (2, 1, 1, 2))}
    for name, (base, (ev, ad, tr, rm)) in want.items():
        item = cert["corrections"][base][name]
        prog = splice(bases[base], item["splices"])
        rows, b = replay(witness, prog, watch=("Y7", "X0"))
        b0 = bill_b[base]
        got = (b["events"] - b0["events"], b["adds"] - b0["adds"], b["transports"] - b0["transports"], b["rank_mass"] - b0["rank_mass"])
        need(got == (ev, ad, tr, rm), name + " added bill")
        changed = sorted(k for k in rows_b[base] if rows[k] != rows_b[base][k])
        need(changed == ["Y7"], name + " changes only Y7")
        if name.endswith("row"):
            need(rows["Y7"] == {"Y7": Fraction(1), "X7": Fraction(1)}, name + " row 7 identity")
        else:
            need("X0" not in rows["Y7"], name + " entry applied")
            diff = {k: rows["Y7"].get(k, 0) - rows_b[base]["Y7"].get(k, 0) for k in set(rows["Y7"]) | set(rows_b[base]["Y7"])}
            need({k: v for k, v in diff.items() if v} == {"X0": Fraction(1, 2)}, name + " exact entry")
        c = cert["bill"][name]
        need([c["added_vs_base"][k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")] == [ev, ad, tr, rm], name + " certificate bill")
        dm = {r: b["mass"].get(r, 0) - b0["mass"].get(r, 0) for r in set(b["mass"]) | set(b0["mass"])}
        dm = {r: v for r, v in dm.items() if v}
        need(all(v % 2 == 0 for r, v in dm.items() if r != "C"), name + " even non-private mass")
        need(c["added_rank_by_register"] == dm, name + " per-register mass")
        if name in ("E", "Erow"):
            need(b["shared"] and all(d == 9 for _i, d in b["shared"]), name + " Y7 and X0 share the full chart")
            need(not dm, name + " no added rank")
    need(cert["bill"]["P"]["private_events"] == {"zero": 9, "copy": 9, "erase": 9}, "P lifetime")

    need(all(lower_sweep(witness, p) is None for p in bases.values()), "bases feasible")
    d = 2797
    need(program[d] == ["add", "Y7", "D17", "1/4", [95, 486]], "published delivering ADD")
    touch = lambda regs, skip: sorted({0} | {i + 1 for i, e in enumerate(program)
                                            if i not in skip and e[0] in ("add", "copy") and set(regs) & {e[1], e[2]}})
    cuts = touch(("X0", "Y7"), {d})
    need(len(cuts) == 18, "18 classes without the delivering ADD")
    blocked = [lower_sweep(witness, program, [(u, ("X0", "Y7"), ())], skip={d}) for u in cuts]
    need(all(blocked), "no zero-mass correction for any delivery placement")
    need([[u, list(x)] for u, x in zip(cuts, blocked)] == cert["obstruction"]["strict_first_obstruction"], "strict table")
    pub_cuts = touch(("X0", "Y7"), set())
    pub_blocked = [lower_sweep(witness, program, [(u, ("X0", "Y7"), ())]) for u in pub_cuts]
    need(len(pub_cuts) == 19 and all(pub_blocked), "published-order classes obstructed")
    early = [u for u in touch(("Y7",), {d}) if u < 2461]
    pblocked = [lower_sweep(witness, program, [(u, ("Y7",), (232,))], skip={d}) for u in early]
    need(len(early) == 5 and all(pblocked), "early private deliveries obstructed")

    cur = {n: closure(f) for n, f in witness["initial_frames"].items()}
    carriers = {"X7"}
    for i, e in enumerate(program[:1075]):
        if e[0] == "add" and "C" not in (e[1], e[2]):
            if {e[1], e[2]} & carriers:
                carriers |= {e[1], e[2]}
            cur[e[1]] = cur[e[2]] = grow(cur[e[1]], cur[e[2]])
        if i == 1073:
            need(cur["X0"] <= f7, "X0 inside F7 before 1074")
    need(witness["initial_frames"]["X7"] == [387] and 387 not in f7, "X7 head outside F7")
    need("X0" in carriers and 387 in cur["X0"] and not cur["X0"] <= f7, "387 reaches X0 by 1074")
    ob = cert["obstruction"]
    need(ob["forcing_source_head"] == [387] and ob["source_leaves_target_final_at"][0] == 1074, "certificate forcing")

    force = (d, ("Y7", "D17"), (232,))
    rescue = [r for r in sorted(witness["initial_frames"]) if lower_sweep(witness, program, [force], free=(r,)) is None]
    need(rescue == ["D17"] == ob["order_preserving_cohost_single_register_rescues"], "only D17 rescues co-hosting")
    for r in ((), ("D17",)):
        need(all(lower_sweep(witness, program, [force, (u, ("X0", "Y7"), ())], free=r) for u in pub_cuts),
             "joint order-preserving obstructed with %s free" % (r or "nothing"))
    ec = cert["end_cut_comparison"]
    need((ec["cohost_discount_R0"], ec["cohost_discount_R1"]) == (0, 2), "co-host discounts")
    need(cert["selected_kappa"] == "0.001672660197076918" and cert["no_new_kappa"] is True, "kappa")
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
