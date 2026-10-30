#!/usr/bin/env python3
"""Independent replay of the flag-43 side-correction bill.

Imports neither verify.py nor check_native.py. Frames are XOR-closed sets of
compressed labels. Every corrected word is replayed with exact rational rows
under the channel rules (common-chart ADD and copy, nested transports paying
their frame gap, owned private lifetimes, endpoint frames). The four
committed new-edge recipes are checked directly with the pinned independent
Gaussian interpreter. The forced-frame obstruction is recomputed by a forward
sweep over closure sets. Key receipts are compared with CERTIFICATE.json.
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
NATIVE = "research/p104-native-channel"
REPAIR = "research/p104-flag43-head-step-repair"
PINS = {
    f"{NATIVE}/inputs/LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    f"{NATIVE}/inputs/P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    f"{NATIVE}/NATIVE-RECIPES.json.gz": "a1c4d83d3d5fe1338e99b59272e8cf5d43244c33888597da340b2aa7fef5b3e8",
    f"{NATIVE}/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "research/p104-joint-unit-flags/CERTIFICATE.json": "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
    f"{REPAIR}/CERTIFICATE.json": "6ce05cee77b6641e9875a0fd07059fb2b41de7733b6e770dc673426f70f764b1",
    f"{REPAIR}/REPAIR-RECIPES.json": "d6dd5a7aade3206dcf7ccd9876dd143627b9d91ba8a41d7f71df26b437b988fd",
}
MARKER = (
    "PASS_P104_FLAG43_SIDE_CORRECTION_BILL_INDEPENDENT entry=(59,21) zero_mass_placements=0/28 "
    "early_private_deliveries_obstructed=11/11 T=+2rank S=+2rank P=+1rank T48=+2rank "
    "rows_changed=Y59_only row59=identity new_recipes=2 no_new_kappa"
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
    return lambda t, s: sum(x * y for x, y in zip(ps[t], ps[s])) // 4


def replay(witness, program):
    frames = {n: closure(f) for n, f in witness["initial_frames"].items()}
    rows = {n: {n: Fraction(1)} for n in witness["initial_frames"]}
    paid, adds, private = {}, 0, {"zero": 0, "copy": 0, "erase": 0}
    mass = {}
    for e in program:
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
                  "private": private, "mass": mass}


def lower_sweep(witness, program, inject=None):
    cur = {n: closure(f) for n, f in witness["initial_frames"].items()}
    fin = {n: closure(f) for n, f in witness["final_frames"].items()}
    for i in range(len(program) + 1):
        if inject is not None and i == inject[0]:
            regs = inject[1]
            m = frozenset().union(*[cur[r] for r in regs]) if len(regs) > 1 else cur[regs[0]]
            m = closure(set(m) | set(inject[2]))
            for r in regs:
                cur[r] = m
                if not m <= fin[r]:
                    return i, r
        if i == len(program):
            return None
        e = program[i]
        if e[0] == "add" and "C" not in (e[1], e[2]):
            m = closure(set(cur[e[1]]) | set(cur[e[2]]))
            cur[e[1]] = cur[e[2]] = m
            for r in (e[1], e[2]):
                if not m <= fin[r]:
                    return i, r


def main(root=ROOT):
    witness = read(root, f"{NATIVE}/inputs/LOWRANK-WITNESS.json")
    fixture = read(root, f"{NATIVE}/inputs/P104-FIXTURE.json")["section4_explicit_P104"]
    recipes = read(root, f"{NATIVE}/NATIVE-RECIPES.json.gz", gz=True)
    flags = read(root, "research/p104-joint-unit-flags/CERTIFICATE.json")
    repair = read(root, f"{REPAIR}/CERTIFICATE.json")
    cert = json.loads((HERE / "CERTIFICATE.json").read_bytes(), object_pairs_hook=strict)
    new = json.loads((HERE / "CORRECTION-RECIPES.json").read_bytes(), object_pairs_hook=strict)["recipes"]
    raw = (root / NATIVE / "vendor/native_verify.py").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[f"{NATIVE}/vendor/native_verify.py"], "interpreter pin")
    spec = importlib.util.spec_from_file_location("flag43_side_independent_native", root / NATIVE / "vendor/native_verify.py")
    N = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(N)

    flag = flags["helpers"][43]
    need((flag["source"], flag["target"], flag["basis"][0]) == (21, 59, 15), "flag 43")
    G = gram_rows(fixture)
    need(G(59, 21) == 1 and G(59, 59) == 2 and G(59, 12) == 0, "Gram entries")
    program = witness["program"]
    r0 = splice(program, repair["repairs"]["R0"]["splices"])
    rows0, b0 = replay(witness, r0)
    need((b0["events"], b0["adds"], b0["transports"], b0["rank_mass"]) == (4058, 2624, 1410, 2368), "R0 bill")
    for t in range(104):
        y = rows0["Y%d" % t]
        want = {"Y%d" % t: Fraction(1)}
        want.update({"X%d" % s: Fraction(G(t, s), 2) for s in range(104) if G(t, s)})
        need(y == want, "R0 target row G/2")

    iso = recipes["label_isometry"]
    dual, orth = iso["compressed_dual_gram"], iso["orthonormal_basis_compressed"]

    def to_phys(x):
        dx = sum((((row & x).bit_count()) & 1) << i for i, row in enumerate(dual))
        return sum((((v & dx).bit_count()) & 1) << j for j, v in enumerate(orth))

    for rec in new:
        need(rec["rank"] == abs(len(rec["old"]) - len(rec["new"])) == rec["recipe"]["rank"], "recipe rank")
        N.equal(N.recipe(rec["recipe"]), N.adjoint(N.frame(tuple(rec["old"]), 9)) + N.frame(tuple(rec["new"]), 9), "new native edge")
    f59 = witness["final_frames"]["Y59"]
    full = [1 << k for k in range(9)]
    phys = lambda f: closure(to_phys(x) for x in f)
    keys = {(closure(r["old"]), closure(r["new"])) for r in new}
    need(keys == {(phys(full), phys(f59)), (phys(f59), phys(full))}, "new edges are FULL<->F59")

    want_add = {"T": (2, 1, 1, 2), "S": (3, 1, 2, 2), "P": (5, 1, 1, 1), "T48": (49, 48, 1, 2)}
    for name, (ev, ad, tr, rm) in want_add.items():
        prog = splice(r0, cert["corrections"][name]["splices"])
        rows, b = replay(witness, prog)
        got = (b["events"] - 4058, b["adds"] - 2624, b["transports"] - 1410, b["rank_mass"] - 2368)
        need(got == (ev, ad, tr, rm), name + " added bill")
        changed = sorted(k for k in rows0 if rows[k] != rows0[k])
        need(changed == ["Y59"], name + " changes only Y59")
        if name == "T48":
            need(rows["Y59"] == {"Y59": Fraction(1), "X59": Fraction(1)}, "row 59 identity")
        else:
            need("X21" not in rows["Y59"], name + " entry applied")
            diff = {k: rows["Y59"].get(k, 0) - rows0["Y59"].get(k, 0) for k in set(rows["Y59"]) | set(rows0["Y59"])}
            need({k: v for k, v in diff.items() if v} == {"X21": Fraction(-1, 2)}, name + " exact entry")
        c = cert["bill"][name]
        need([c["added_vs_R0"][k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")] == [ev, ad, tr, rm], name + " certificate bill")
        dm = {r: b["mass"].get(r, 0) - b0["mass"].get(r, 0) for r in set(b["mass"]) | set(b0["mass"])}
        dm = {r: v for r, v in dm.items() if v}
        need(all(v % 2 == 0 for r, v in dm.items() if r != "C"), name + " even non-private mass")
        need(c["added_rank_by_register"] == dm, name + " per-register mass")
    need(cert["bill"]["P"]["private_events"] == {"zero": 9, "copy": 9, "erase": 9}, "P lifetime")

    need(lower_sweep(witness, program) is None and lower_sweep(witness, r0) is None, "base feasible")
    ev = sorted({i for i, e in enumerate(program) if e[0] in ("add", "copy") and {"X21", "Y59"} & {e[1], e[2]}})
    cuts = sorted({0} | {i + 1 for i in ev})
    need(len(cuts) == 28, "28 placement classes")
    blocked = [lower_sweep(witness, program, (u, ("X21", "Y59"), ())) for u in cuts]
    need(all(blocked), "no zero-mass direct placement")
    need([[u, list(x)] for u, x in zip(cuts, blocked)] == cert["obstruction"]["direct_first_obstruction"], "obstruction table")
    yev = sorted({i for i, e in enumerate(program) if e[0] in ("add", "copy") and "Y59" in (e[1], e[2])})
    early = [u for u in sorted({0} | {i + 1 for i in yev}) if u < 2461]
    pblocked = [lower_sweep(witness, program, (u, ("Y59",), (15,))) for u in early]
    need(len(early) == 11 and all(pblocked), "early private deliveries obstructed")
    cur = {n: closure(f) for n, f in witness["initial_frames"].items()}
    for i, e in enumerate(program[:885]):
        if e[0] == "add" and "C" not in (e[1], e[2]):
            cur[e[1]] = cur[e[2]] = closure(set(cur[e[1]]) | set(cur[e[2]]))
    need(131 in cur["X21"] and 15 in cur["X21"] and 131 not in closure(f59) and 15 in closure(f59), "131 forced into X21 by 884")
    need(witness["initial_frames"]["X12"] == [131], "X12 head")
    ob = cert["obstruction"]
    need(ob["partner_feeder"][0] == 625 and ob["source_first_read"][0] == 884, "certificate forcing events")
    need(ob["feeder_source_head"] == witness["initial_frames"]["X12"] and ob["feeder_source_gram_with_target"] == G(59, 12), "certificate feeder")
    need(ob["source_forced_full_from"] == 1708 and 9 not in [r for i, _p, r in ob["source_forced_rank_at_events"] if i < 1708], "certificate full-from")
    need(cert["selected_kappa"] == "0.001672660197076918" and cert["no_new_kappa"] is True, "kappa")
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
