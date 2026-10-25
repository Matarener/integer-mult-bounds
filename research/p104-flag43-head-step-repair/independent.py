#!/usr/bin/env python3
"""Second, separately written scanner for the flag-43 head-step repair bill.

Does not import verify.py, check_native.py or the compiler. Frames are explicit
XOR-closure sets; the repaired words are replayed with exact rational rows and
compared register by register with the published word's final rows and frames.
The forced-hosting closure is recomputed by a single forward sweep. The new
native recipes are checked directly with the vendored independent interpreter.
Admission uses need() and stays active under python -O.
"""

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
    f"{NATIVE}/NATIVE-RECIPES.json.gz": "a1c4d83d3d5fe1338e99b59272e8cf5d43244c33888597da340b2aa7fef5b3e8",
    f"{NATIVE}/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "research/p104-joint-unit-flags/CERTIFICATE.json": "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
}
MARKER = (
    "PASS_P104_FLAG43_HEAD_STEP_REPAIR_INDEPENDENT flag=43 head=15 repaired_update=3364 "
    "added_events=0 added_adds=0 added_transports=0 added_rank_mass=0 "
    "retargeted_transports=9 forced_registers=4 profile_delta=-3H1+5H2-H3-H4 "
    "rows_equal=280/280 earlier_updates_obstructed=14/14 no_new_kappa"
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def strict(pairs):
    seen = {}
    for k, v in pairs:
        need(k not in seen, "duplicate JSON key: " + str(k))
        seen[k] = v
    return seen


def read(root, rel, gz=False):
    raw = (root / rel).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[rel], "source hash: " + rel)
    return json.loads(gzip.decompress(raw) if gz else raw, object_pairs_hook=strict)


def closure(vectors):
    out = frozenset([0])
    for v in vectors:
        out = out | frozenset(x ^ v for x in out)
    return out


def dim(s):
    n = len(s)
    need(n & (n - 1) == 0, "closure size is a power of two")
    return n.bit_length() - 1


def splice(program, rows):
    out = list(program)
    edits = sorted(((r["published_range"][0], r["published_range"][1], r) for r in rows), reverse=True)
    prev = len(program)
    for a, b, r in edits:
        need(b <= prev and a < b, "disjoint splices")
        need(program[a:b] == r["published"], "splice binding at %d" % a)
        out[a:b] = [list(e) for e in r["events"]]
        prev = a
    return out


def replay(witness, program):
    rows = {n: {n: Fraction(1)} for n in witness["initial_frames"]}
    frames = {n: closure(f) for n, f in witness["initial_frames"].items()}
    profile = {}
    adds = 0
    for i, e in enumerate(program):
        op = e[0]
        if op == "transport":
            _, r, old, new, k = e
            a, b = closure(old), closure(new)
            need(frames[r] == a, "transport before-frame continuity at %d" % i)
            need(a <= b or b <= a, "nested transport at %d" % i)
            need(k == abs(dim(b) - dim(a)) and k > 0, "paid rank equals frame gap at %d" % i)
            need(len(new) == dim(b) and len(old) == dim(a), "independent frame lists at %d" % i)
            frames[r] = b
            profile[k] = profile.get(k, 0) + 1
        elif op == "zero":
            need(e[1] not in frames, "fresh private")
            rows[e[1]] = {}
            frames[e[1]] = closure(e[2])
        elif op == "erase":
            need(frames[e[1]] == closure(e[2]), "erase chart")
            rows.pop(e[1])
            frames.pop(e[1])
        elif op == "copy":
            need(not rows[e[1]] and frames[e[1]] == frames[e[2]] == closure(e[3]), "copy chart")
            rows[e[1]] = dict(rows[e[2]])
        else:
            need(op == "add", "opcode")
            _, d, s, c, f = e
            need(d != s and frames[d] == frames[s] == closure(f), "common chart at %d" % i)
            adds += 1
            for n, v in rows[s].items():
                z = rows[d].get(n, Fraction(0)) + Fraction(c) * v
                if z:
                    rows[d][n] = z
                else:
                    rows[d].pop(n, None)
    for n, f in witness["final_frames"].items():
        need(frames[n] == closure(f), "final frame " + n)
    return rows, frames, profile, adds


def frames_over_time(witness, program, reg):
    out = [(-1, closure(witness["initial_frames"][reg]))]
    for i, e in enumerate(program):
        if e[0] == "transport" and e[1] == reg:
            out.append((i, closure(e[3])))
    return out


def frame_before(seq, t):
    cur = seq[0][1]
    for i, f in seq:
        if i < t:
            cur = f
    return cur


def sweep(witness, program, target, start, head):
    hosting = {target: start}
    for j in range(start, len(program)):
        e = program[j]
        if e[0] not in ("add", "copy"):
            continue
        a, b = e[1], e[2]
        if a in hosting or b in hosting:
            for r in (a, b):
                hosting.setdefault(r, j)
    seqs = {}
    change = {}
    for r, t in hosting.items():
        if r == "C":
            frames = [f for i, f in private_frames(program) if i < t]
            if not frames or head not in frames[-1]:
                change[r] = t
            continue
        seqs[r] = frames_over_time(witness, program, r)
        if head not in frame_before(seqs[r], t):
            change[r] = t
    return change, seqs


def private_frames(program):
    out = []
    for i, e in enumerate(program):
        if e[1:2] == ["C"]:
            if e[0] == "zero":
                out.append((i, closure(e[2])))
            elif e[0] == "transport":
                out.append((i, closure(e[3])))
    return out


def main(root=ROOT):
    cert = json.loads((HERE / "CERTIFICATE.json").read_bytes(), object_pairs_hook=strict)
    recipes_new = json.loads((HERE / "REPAIR-RECIPES.json").read_bytes(), object_pairs_hook=strict)["recipes"]
    witness = read(root, f"{NATIVE}/inputs/LOWRANK-WITNESS.json")
    published_recipes = read(root, f"{NATIVE}/NATIVE-RECIPES.json.gz", gz=True)
    flags = read(root, "research/p104-joint-unit-flags/CERTIFICATE.json")
    raw = (root / NATIVE / "vendor/native_verify.py").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[f"{NATIVE}/vendor/native_verify.py"], "native interpreter pin")
    spec = importlib.util.spec_from_file_location("flag43_independent_native", root / NATIVE / "vendor/native_verify.py")
    N = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(N)

    h = flags["helpers"][43]
    head, src, tgt = h["basis"][0], "X%d" % h["source"], "Y%d" % h["target"]
    need((head, src, tgt) == (15, "X21", "Y59"), "flag 43")
    need(cert["basis_head"] == head and cert["source_register"] == src and cert["target_register"] == tgt, "certificate flag")
    P = witness["program"]
    base_rows, _, base_profile, base_adds = replay(witness, P)
    bill = cert["bill"]
    need(sum(base_profile.values()) == bill["published"]["transport_occurrences"] == 1410, "published transports")
    need(sum(k * v for k, v in base_profile.items()) == bill["published"]["rank_mass"] == 2368, "published rank mass")
    need(base_adds == bill["published"]["scalar_adds"] == 2624, "published adds")

    # Physical canonical images of the repaired frames, for the native recipe check.
    iso = published_recipes["label_isometry"]
    dual, orth = iso["compressed_dual_gram"], iso["orthonormal_basis_compressed"]

    def to_phys(x):
        bx = sum(((((row & x).bit_count()) & 1) << i) for i, row in enumerate(dual))
        return sum((((v & bx).bit_count()) & 1) << j for j, v in enumerate(orth))

    pub_edges = {(closure(r["old"]), closure(r["new"])) for r in published_recipes["transports"]}
    new_edges = {}
    for rec in recipes_new:
        key = (closure(rec["old"]), closure(rec["new"]))
        need(key not in pub_edges and key not in new_edges, "new edge is new and unique")
        need(rec["rank"] == rec["recipe"]["rank"] == abs(dim(key[1]) - dim(key[0])), "new recipe rank")
        N.equal(N.recipe(rec["recipe"]), N.adjoint(N.frame(tuple(rec["old"]), 9)) + N.frame(tuple(rec["new"]), 9), "new native edge")
        new_edges[key] = rec

    used = set()
    out = {}
    for name in ("R0", "R1"):
        prog = splice(P, cert["repairs"][name]["splices"])
        rows, _, profile, adds = replay(witness, prog)
        same = sum(1 for n in base_rows if rows[n] == base_rows[n])
        need(same == len(base_rows) == 280, "every final row equals the published row")
        for e in prog:
            if e[0] == "transport":
                key = (closure(to_phys(x) for x in e[2]), closure(to_phys(x) for x in e[3]))
                if key not in pub_edges:
                    need(key in new_edges, "repaired edge has a committed recipe")
                    used.add(key)
        b = bill[name]
        need(b["events"] == len(prog) and b["scalar_adds"] == adds, name + " counts")
        need(b["transport_occurrences"] == sum(profile.values()), name + " transports")
        need(b["rank_mass"] == sum(k * v for k, v in profile.items()), name + " rank mass")
        need(b["paid_profile"] == {str(k): v for k, v in sorted(profile.items())}, name + " profile")
        delta = {str(k): profile.get(k, 0) - base_profile.get(k, 0) for k in sorted(set(profile) | set(base_profile)) if profile.get(k, 0) != base_profile.get(k, 0)}
        need(b["profile_delta"] == delta, name + " delta")
        out[name] = (prog, b)
    need(used == set(new_edges), "every committed recipe used")

    prog0, b0 = out["R0"]
    need((b0["added_events"], b0["added_scalar_adds"], b0["added_transport_occurrences"], b0["added_rank_mass"]) == (0, 0, 0, 0), "R0 adds nothing counted")
    need(b0["profile_delta"] == {"1": -3, "2": 5, "3": -1, "4": -1}, "R0 delta")
    moved = [i for i in range(len(P)) if P[i] != prog0[i] and P[i][0] == "transport"]
    need(moved == b0["retargeted_transports"] and len(moved) == 9, "nine retargeted transports")
    old_r = sorted((P[i][4] for i in moved), reverse=True)
    new_r = sorted((prog0[i][4] for i in moved), reverse=True)
    need(sum(old_r) == sum(new_r) and all(sum(new_r[:k]) <= sum(old_r[:k]) for k in range(1, 10)), "majorization")
    need(sorted({P[i][1] for i in moved}) == b0["registers_changed"] == ["D17", "D28", "Y103", "Y59"], "changed registers")
    need((b["added_events"], b["added_transport_occurrences"], b["added_rank_mass"]) == (1, 1, 0) and b["profile_delta"] == {"2": 2, "4": -1}, "R1 bill")

    hc = cert["head_cohosting"]
    tseq, sseq = frames_over_time(witness, prog0, tgt), frames_over_time(witness, prog0, src)
    pseq = frames_over_time(witness, P, tgt)
    upd = [i for i, e in enumerate(prog0) if e[0] == "add" and e[1] == tgt]
    need([i for i in upd if head in frame_before(pseq, i)] == hc["published_head_hosting_target_updates"] == [], "published head-free updates")
    co = [i for i in upd if head in frame_before(tseq, i) and head in frame_before(sseq, i)]
    need(co == hc["R0_cohosted_target_updates"] == [3364] and upd[-1] == 3364, "R0 co-hosted last update")
    need(closure(prog0[3364][4]) == closure([95, 447, 6, 32, 20, 15]) and prog0[3364][2] == "D17", "R0 update chart")
    need(dim(frame_before(sseq, 3364)) == 9 and [i for i, e in enumerate(prog0) if i > 3364 and src in e[1:3]] == [3705, 3760, 3811, 3863], "source live and full")
    coef = Fraction(0)
    carried = []
    rows = {n: {n: Fraction(1)} for n in witness["initial_frames"]}
    for i, e in enumerate(prog0):
        if e[0] == "zero":
            rows[e[1]] = {}
        elif e[0] == "erase":
            rows.pop(e[1])
        elif e[0] == "copy":
            rows[e[1]] = dict(rows[e[2]])
        elif e[0] == "add":
            if e[1] == tgt and rows[e[2]].get(src):
                coef += Fraction(e[3]) * rows[e[2]][src]
                carried.append([i, e[2], str(Fraction(e[3]) * rows[e[2]][src]), str(coef)])
            for n, v in rows[e[2]].items():
                z = rows[e[1]].get(n, Fraction(0)) + Fraction(e[3]) * v
                if z:
                    rows[e[1]][n] = z
                else:
                    rows[e[1]].pop(n, None)
    need(carried == hc["R0_source_delivery_into_target"] and carried[-1] == [3364, "D17", "1/2", "1/2"], "delivery chronology")

    finals = {n: closure(f) for n, f in witness["final_frames"].items()}
    table = {row["event"]: row for row in cert["forced_hosting"]["table"]}
    need(sorted(table) == [i for i, e in enumerate(P) if e[0] == "add" and e[1] == tgt], "every target update tabulated")
    obstructed = 0
    for t0, row in table.items():
        change, seqs = sweep(witness, P, tgt, t0, head)
        hard = sorted([[r, t] for r, t in change.items() if r != "C" and r in finals and head not in finals[r]], key=lambda x: (x[1], x[0]))
        private = sorted([[r, t] for r, t in change.items() if r == "C"], key=lambda x: (x[1], x[0]))
        slot = [r for r, t in change.items() if r != "C" and not any(-1 < i < t for i, _ in seqs[r]) and [r, t] not in hard and head not in seqs[r][0][1]]
        need(row["must_change"] == len(change), "must-change count at %d" % t0)
        need(row["slot_independent_obstructions"] == len(hard), "obstruction count at %d" % t0)
        need(row["first_obstruction"] == (hard[0] + ["final frame excludes head"] if hard else None), "first obstruction at %d" % t0)
        need(row["private_registers_forced"] == private, "private forcing at %d" % t0)
        need(row["registers_without_prior_transport"] == len(slot), "slot count at %d" % t0)
        need(row["admissible"] == (not hard and not slot and not private), "admissible at %d" % t0)
        if hard:
            obstructed += 1
        else:
            need(row["forced"] == change, "forced set at %d" % t0)
    need(obstructed == 14 and table[3364]["forced"] == {"Y59": 3364, "D17": 3364, "Y103": 3366, "D28": 3462}, "closure verdict")
    need(cert["selected_kappa"] == "0.001672660197076918" and cert["no_new_kappa"] is True, "kappa")
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
