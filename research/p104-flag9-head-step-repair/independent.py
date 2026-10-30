#!/usr/bin/env python3
"""Second scanner for the flag-9 head-step repair bill.

Does not import verify.py, check_native.py or the compiler. Frames are
XOR-closure sets. Both repaired words are replayed with exact rational rows
and compared with the published final rows. Transport ranks are the frame
gaps. New native recipes are checked with the vendored interpreter. The
forced-hosting closure is a forward sweep. Admission uses need() and stays
active under python -O.
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
HEAD = 196
SOURCE = "X4"
TARGET = "Y23"
MARKER = (
    "PASS_P104_FLAG9_HEAD_STEP_REPAIR_INDEPENDENT flag=9 head=196 "
    "R0_added_rank_mass=2 R1_added_rank_mass=2 rows_equal=280/280 "
    "updates_obstructed=9/9 source_events_keep_head=21/21 no_new_kappa"
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
    need(n and n & (n - 1) == 0, "closure size is a power of two")
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
    change = {}
    seqs = {}
    for r, t in hosting.items():
        if r == "C":
            continue
        seqs[r] = frames_over_time(witness, program, r)
        if head not in frame_before(seqs[r], t):
            change[r] = t
    return change, seqs


def deliveries(witness, program):
    rows = {n: {n: Fraction(1)} for n in witness["initial_frames"]}
    seen = []
    coef = Fraction(0)
    for i, e in enumerate(program):
        if e[0] == "zero":
            rows[e[1]] = {}
        elif e[0] == "erase":
            rows.pop(e[1])
        elif e[0] == "copy":
            rows[e[1]] = dict(rows[e[2]])
        elif e[0] == "add":
            if e[1] == TARGET and rows[e[2]].get(SOURCE):
                carried = Fraction(e[3]) * rows[e[2]][SOURCE]
                coef += carried
                seen.append([i, e[2], str(carried), str(coef)])
            for n, v in rows[e[2]].items():
                z = rows[e[1]].get(n, Fraction(0)) + Fraction(e[3]) * v
                if z:
                    rows[e[1]][n] = z
                else:
                    rows[e[1]].pop(n, None)
    return seen


def main(root=ROOT):
    cert = json.loads((HERE / "CERTIFICATE.json").read_bytes(), object_pairs_hook=strict)
    recipes_new = json.loads((HERE / "REPAIR-RECIPES.json").read_bytes(), object_pairs_hook=strict)["recipes"]
    witness = read(root, f"{NATIVE}/inputs/LOWRANK-WITNESS.json")
    published_recipes = read(root, f"{NATIVE}/NATIVE-RECIPES.json.gz", gz=True)
    flags = read(root, "research/p104-joint-unit-flags/CERTIFICATE.json")
    raw = (root / NATIVE / "vendor/native_verify.py").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[f"{NATIVE}/vendor/native_verify.py"], "native interpreter pin")
    spec = importlib.util.spec_from_file_location("flag9_independent_native", root / NATIVE / "vendor/native_verify.py")
    N = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(N)

    h = flags["helpers"][9]
    need((h["basis"][0], "X%d" % h["source"], "Y%d" % h["target"]) == (HEAD, SOURCE, TARGET), "flag 9")
    need(cert["basis_head"] == HEAD and cert["source_register"] == SOURCE, "certificate flag")
    P = witness["program"]
    base_rows, _, base_profile, base_adds = replay(witness, P)
    bill = cert["bill"]
    need(sum(base_profile.values()) == bill["published"]["transport_occurrences"] == 1410, "published transports")
    need(sum(k * v for k, v in base_profile.items()) == bill["published"]["rank_mass"] == 2368, "published rank mass")
    need(base_adds == bill["published"]["scalar_adds"] == 2624, "published adds")

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

    drop = P[500]
    need(drop[0] == "transport" and drop[1] == SOURCE, "event 500")
    need(HEAD not in drop[3] and (64 ^ 132) == HEAD and 64 in drop[3] and 132 in drop[3], "196 = 64 XOR 132")
    source_events = [i for i, e in enumerate(P) if SOURCE in (e[1:3] if e[0] in ("add", "copy") else e[1:2])]
    sseq_pub = frames_over_time(witness, P, SOURCE)
    need(len(source_events) == 21 and all(HEAD in frame_before(sseq_pub, i) for i in source_events), "source span")
    need(HEAD in closure(witness["final_frames"][TARGET]) and HEAD not in closure(witness["final_frames"]["Y28"]), "finals")
    need(all("D28" not in e[1:3] for e in P[3125:3126]), "gap before Y28")

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
        delta = {str(k): profile.get(k, 0) - base_profile.get(k, 0)
                 for k in sorted(set(profile) | set(base_profile)) if profile.get(k, 0) != base_profile.get(k, 0)}
        need(b["profile_delta"] == delta, name + " delta")
        mass = {}
        for e in prog:
            if e[0] == "transport":
                mass[e[1]] = mass.get(e[1], 0) + e[4]
        base_mass = {}
        for e in P:
            if e[0] == "transport":
                base_mass[e[1]] = base_mass.get(e[1], 0) + e[4]
        reg_delta = {r: mass.get(r, 0) - base_mass.get(r, 0) for r in set(mass) | set(base_mass) if mass.get(r, 0) != base_mass.get(r, 0)}
        need(b["register_rank_mass_delta"] == reg_delta, name + " register mass")
        out[name] = prog
    need(used == set(new_edges), "every committed recipe used")

    need(bill["R0"]["added_rank_mass"] == 2 and bill["R0"]["added_events"] == 1, "R0 bill")
    need(bill["R0"]["register_rank_mass_delta"] == {"D28": 2}, "R0 register")
    need(bill["R0"]["profile_delta"] == {"1": -1, "2": 2, "4": 1, "5": -1}, "R0 profile")
    need(bill["R1"]["added_rank_mass"] == 2 and bill["R1"]["added_events"] == 0, "R1 bill")
    need(bill["R1"]["register_rank_mass_delta"] == {"Y23": 2}, "R1 register")
    need(bill["R1"]["profile_delta"] == {"5": -1, "7": 1}, "R1 profile")

    hc = cert["head_cohosting"]
    for name, prog, update in (("R0", out["R0"], 3124), ("R1", out["R1"], 3633)):
        tseq = frames_over_time(witness, prog, TARGET)
        sseq = frames_over_time(witness, prog, SOURCE)
        adds = [i for i, e in enumerate(prog) if e[0] == "add" and e[1] == TARGET]
        co = [i for i in adds if HEAD in frame_before(tseq, i) and HEAD in frame_before(sseq, i)]
        block = hc[name]
        need(co == block["cohosted_target_updates"] == [update], name + " co-host index")
        need(block["source_spans_head"] and dim(frame_before(sseq, update)) == 9, name + " source rank")
        need(deliveries(witness, prog) == block["source_delivery_into_target"], name + " delivery")
    need(hc["published_head_hosting_target_updates"] == [], "published head-free")
    need(hc["R0"]["source_delivery_into_target"] == [[3124, "D28", "-1/2", "-1/2"]], "R0 coefficient")

    finals = {n: closure(f) for n, f in witness["final_frames"].items()}
    table = {row["event"]: row for row in cert["forced_hosting"]["table"]}
    need(sorted(table) == [i for i, e in enumerate(P) if e[0] == "add" and e[1] == TARGET], "every target update")
    obstructed = 0
    for t0, row in table.items():
        change, seqs = sweep(witness, P, TARGET, t0, HEAD)
        hard = sorted([[r, t] for r, t in change.items() if r in finals and HEAD not in finals[r]], key=lambda x: (x[1], x[0]))
        need(row["slot_independent_obstructions"] == len(hard), "obstruction count at %d" % t0)
        need(row["first_obstruction"] == (hard[0] + ["final frame excludes head"] if hard else None), "first obstruction at %d" % t0)
        need(row["admissible"] is False, "not admissible at %d" % t0)
        if hard:
            obstructed += 1
    need(obstructed == 9 and table[3124]["first_obstruction"][0] == "Y28", "closure verdict")
    need(cert["selected_kappa"] == "0.001672660197076918" and cert["no_new_kappa"] is True, "kappa")
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
