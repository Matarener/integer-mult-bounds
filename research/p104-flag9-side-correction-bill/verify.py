#!/usr/bin/env python3
"""Read-only replay of the flag-9 I-G/2 end-cut side-correction bill.

On the published native-channel word, replaces Y23's terminal transport at
event 3489 with four concrete corrections that apply the (23, 4) entry of
I - G/2 (and, for T48, the whole Y23 row). For each corrected word it runs the
published check_native.validate() unchanged on the coefficient-0 copy, replays
the real word with exact rational rows, and confirms that validate() rejects
the real word only at Y23's endpoint. It then recomputes the bills, the
X58:333 forcing leave at event 745 and the least-lower-bound frame sweep that
rules out a zero-added-mass placement (25/25 classes), and compares the
receipt with CERTIFICATE.json. Admission uses need() and stays active under
python -O. Nothing is written. Does not reopen the deferred flag-9 head-step
repair; cites open #3614's feeder/obstruction as leave-alone.
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
PINS = {
    f"{NATIVE}/inputs/LOWRANK-WITNESS.json": "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    f"{NATIVE}/inputs/P104-FIXTURE.json": "516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4",
    f"{NATIVE}/NATIVE-RECIPES.json.gz": "a1c4d83d3d5fe1338e99b59272e8cf5d43244c33888597da340b2aa7fef5b3e8",
    f"{NATIVE}/check_native.py": "e67b874a061a4a28007b9a0fabaf30c8db4a587b1e1c7dd9396c77ff1e3a9fe6",
    f"{NATIVE}/vendor/native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    "research/p104-joint-unit-flags/CERTIFICATE.json": "a98126428a8da6eae91c50afcc42e014a284c82b554ef77e5b3a34fc6d228128",
}
FLAG_INDEX = 9
CUT = 3489
SELECTED_KAPPA = "0.001672660197076918"
FULL = [1, 2, 4, 8, 16, 32, 64, 128, 256]
A3 = [447, 127, 192]
PRIVATE_SPAN = (2461, 2524)
MARKER = (
    "PASS_P104_FLAG9_SIDE_CORRECTION_BILL flag=9 entry=(23,4) gram=-1 coefficient=+1/2 "
    "zero_mass_placements=0/25 forcing=X58(333)@leave745 strict_min_added_rank=2 "
    "T=+1transport+1add+2rank(H1-H5+H6) S=+2transport+1add+2rank(2H1) "
    "P=+1transport+1add+1rank(H1)+1private_lifetime T48=+1transport+48add+2rank row23=identity "
    "native_validate=4/4 published_end_cut no_new_kappa"
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
    name = "flag9_side_check_native"
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


def corrections(program, final, ps):
    f23 = final["Y23"]
    cut = program[CUT]
    need(cut == ["transport", "Y23", A3, f23, 5], "published terminal Y23 transport at the cut")
    coeff = str(Fraction(-gram(ps, 23, 4), 2))
    need(coeff == "1/2", "flag-9 entry coefficient")
    row = [["add", "Y23", "X%d" % s, str(Fraction(-gram(ps, 23, s), 2)), FULL]
           for s in range(104) if s != 23 and gram(ps, 23, s)]
    entry = ["add", "Y23", "X4", coeff, FULL]

    def one(events):
        return [{"published_range": [CUT, CUT + 1], "published": [cut], "events": events}]

    return {
        "T": {
            "route": "end-cut target lift on the published word: Y23 leaves [447,127,192] for the full chart, takes the entry from X4 there, then descends to its final hyperplane",
            "splices": one([
                ["transport", "Y23", A3, FULL, 6],
                entry,
                ["transport", "Y23", FULL, f23, 1],
            ]),
        },
        "S": {
            "route": "source detour: Y23 takes its published terminal transport, X4 descends to Y23's final hyperplane for one ADD and returns to the full chart before its next read at 3695",
            "splices": one([
                cut,
                ["transport", "X4", FULL, f23, 1],
                ["add", "Y23", "X4", coeff, f23],
                ["transport", "X4", f23, FULL, 1],
            ]),
        },
        "P": {
            "route": "one added private lifetime under the inherited private-copy contract: copy X4 into C at the full chart, descend C to Y23's final hyperplane, deliver, discard",
            "splices": one([
                cut,
                ["zero", "C", FULL],
                ["copy", "C", "X4", FULL],
                ["transport", "C", FULL, f23, 1],
                ["add", "Y23", "C", coeff, f23],
                ["erase", "C", f23],
            ]),
        },
        "T48": {
            "route": "whole Y23 row of I - G/2 on the same end-cut lift: every off-diagonal source entry -G[23,s]/2 is added while Y23 sits in the full chart",
            "splices": one([["transport", "Y23", A3, FULL, 6]] + row + [["transport", "Y23", FULL, f23, 1]]),
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


def sweep(witness, program, inject=None):
    """Least frames of a zero-added-mass repair; C is left unconstrained."""
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


def closure(vectors):
    span = {0}
    for v in vectors:
        if v not in span:
            span |= {x ^ v for x in span}
    return frozenset(span)


def grow(span, vectors):
    span = set(span)
    for v in vectors:
        if v not in span:
            span |= {x ^ v for x in span}
    return frozenset(span)


def forcing_leave(witness, program, src, tgt):
    """First ADD that forces src outside tgt's final; list outside X-heads."""
    final = closure(witness["final_frames"][tgt])
    cur = {n: closure(f) for n, f in witness["initial_frames"].items()}
    head_of = {
        f[0]: n
        for n, f in witness["initial_frames"].items()
        if n.startswith("X") and len(f) == 1
    }
    holders = {head: {n} for head, n in head_of.items()}
    for index, event in enumerate(program):
        if event[0] != "add" or "C" in (event[1], event[2]):
            continue
        left, right = event[1], event[2]
        for head, regs in list(holders.items()):
            if left in regs or right in regs:
                holders[head] = regs | {left, right}
        merged = grow(cur[left], cur[right])
        cur[left] = cur[right] = merged
        if src in (left, right) and not cur[src] <= final:
            outside = []
            for head, name in sorted(head_of.items()):
                if head in cur[src] and head not in final:
                    seen = {name}
                    path = []
                    for step, prior in enumerate(program[: index + 1]):
                        if prior[0] != "add" or "C" in (prior[1], prior[2]):
                            continue
                        if set(prior[1:3]) & seen:
                            seen |= {prior[1], prior[2]}
                            path.append([step, prior[1], prior[2]])
                            if src in seen:
                                break
                    outside.append({
                        "head": head,
                        "from_register": name,
                        "carrier_path": path,
                    })
            return {
                "source_leaves_target_final_at": index,
                "source_rank_at_leave": len(cur[src]).bit_length() - 1,
                "add_event": event,
                "outside_heads": outside,
            }
    return None


def receipt(root, cert, new_recipes):
    ck = load_checker(root)
    witness, fixture, recipes, flags = load_inputs(root)
    helper = flags["helpers"][FLAG_INDEX]
    head = helper["basis"][0]
    need(("X%d" % helper["source"], "Y%d" % helper["target"], head) == ("X4", "Y23", 196), "flag 9 identity")
    ps = ports(fixture)
    physical = physical_map(recipes)
    program = witness["program"]
    final = witness["final_frames"]
    need(len(program) == 4058, "published word length")
    base = bill(ck.validate(recipes, witness, fixture, False), program)
    spec = corrections(program, final, ps)
    need(cert.get("corrections") == spec, "committed corrections equal the generated ones")
    expected = rows(witness, program)
    need(all(not (e[0] in ("add", "copy") and e[2] == "Y23") for e in program), "Y23 is never read")
    new_keys = {(tuple(r["old"]), tuple(r["new"])) for r in new_recipes}
    need(len(new_keys) == len(new_recipes), "unique correction recipes")
    used_all = set()
    out = {}
    for name in ("T", "S", "P", "T48"):
        prog = apply_splices(program, spec[name]["splices"])
        zero = zeroed(prog, len(program), spec[name]["splices"])
        wz = dict(witness)
        wz["program"] = zero
        cz, used = assemble(recipes, zero, new_recipes, physical)
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
        y = got["Y23"]
        mass0, mass1 = register_mass(program), register_mass(prog)
        added_mass = {r: mass1.get(r, 0) - mass0.get(r, 0) for r in sorted(set(mass0) | set(mass1))
                      if mass1.get(r, 0) != mass0.get(r, 0)}
        start = CUT
        stop = CUT + len(prog) - len(program) + 1
        hist = {}
        for i, e in enumerate(prog[:start]):
            if e[0] == "transport":
                hist[e[1]] = e[3]
        frames_before = {}
        for reg in ("Y23", "X4"):
            frames_before[reg] = list(canon(hist.get(reg, witness["initial_frames"][reg])))
        corr_adds = [e for e in prog[start:stop] if e[0] == "add"]
        out[name] = dict(b)
        out[name].update({
            "native_validate_coefficient_zero": "PASS",
            "real_word_rejected_by_unchanged_checker_at": rejection,
            "changed_final_rows": changed,
            "Y23_final_X4": str(y.get("X4", Fraction(0))),
            "Y23_final_row_is_identity": y == {"Y23": Fraction(1), "X23": Fraction(1)},
            "correction_adds": len(corr_adds),
            "correction_charts": sorted({len(canon(e[4])) for e in corr_adds}),
            "head_in_correction_charts": all(inside([head], e[4]) for e in corr_adds),
            "added_rank_by_register": added_mass,
            "head_in_target_frame_before_correction": inside([head], frames_before["Y23"]),
            "head_in_source_frame_before_correction": inside([head], frames_before["X4"]),
            "target_frame_before_correction_rank": len(frames_before["Y23"]),
            "added_vs_published": {k: b[k] - base[k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")},
            "profile_delta_vs_published": delta(base, b),
        })
    need(len(used_all) == len(new_recipes), "every committed correction recipe is used")

    f23 = canon(final["Y23"])
    leave = forcing_leave(witness, program, "X4", "Y23")
    need(leave is not None, "X4 leaves Y23 final")
    zero_gram = [h for h in leave["outside_heads"] if gram(ps, 23, int(h["from_register"][1:])) == 0]
    need(zero_gram, "orthogonal feeder head exists")
    feeder = next((h for h in zero_gram if h["from_register"] == "X58" and h["head"] == 333), zero_gram[0])
    lb = forced_frames(witness, program, "X4")
    full_from = [i for i, _p, r in lb if r == 9][0]
    cuts = cut_classes(program, ("X4", "Y23"))
    direct = [[u, sweep(witness, program, (u, "X4", "Y23"))] for u in cuts]
    need(all(x[1] for x in direct), "every direct placement is obstructed")
    early = [u for u in cut_classes(program, ("Y23",)) if u < PRIVATE_SPAN[0]]
    private = [[u, sweep(witness, program, (u, None, "Y23", canon([head])))] for u in early]
    need(all(x[1] for x in private), "every early private delivery is obstructed")
    need(sweep(witness, program) is None, "published feasible")
    nz = [s for s in range(104) if s != 23 and gram(ps, 23, s)]
    pub_cut = program[CUT]
    next_x4 = [i for i, e in enumerate(program) if i > CUT and e[0] == "add" and e[2] == "X4"][0]
    obstruction = {
        "entry": {
            "target": "Y23",
            "source": "X4",
            "gram": gram(ps, 23, 4),
            "correction_coefficient": str(Fraction(-gram(ps, 23, 4), 2)),
            "diagonal_gram": gram(ps, 23, 23),
        },
        "row_23_offdiagonal_nonzero": len(nz),
        "flag_head_in_target_final": inside([head], f23),
        "source_leaves_target_final_at": leave["source_leaves_target_final_at"],
        "source_rank_at_leave": leave["source_rank_at_leave"],
        "leave_add_event": leave["add_event"][:4],
        "selected_feeder": {
            "from_register": feeder["from_register"],
            "head": feeder["head"],
            "gram_with_target": gram(ps, 23, int(feeder["from_register"][1:])),
            "head_in_target_final": inside([feeder["head"]], f23),
            "carrier_path": feeder["carrier_path"],
        },
        "outside_head_count": len(leave["outside_heads"]),
        "source_forced_rank_at_events": lb,
        "source_forced_full_from": full_from,
        "direct_cut_classes": len(cuts),
        "direct_first_obstruction": direct,
        "private_early_delivery_cuts": len(private),
        "private_early_first_obstruction": private,
        "published_private_lifetimes": list(PRIVATE_SPAN),
        "source_next_read_after_cut": [next_x4, program[next_x4][:4]],
        "non_private_registers_at_rank_floor": sum(
            1 for r in witness["initial_frames"]
            if register_mass(program).get(r, 0) == len(canon(final[r])) - len(canon(witness["initial_frames"][r]))
        ),
        "leave_alone_forcing_census": {
            "package": "research/p104-present-head-side-correction-forcing-census",
            "open_pr": 3614,
            "cited_primary_feeder": "X58:333@leave745",
            "cited_insertion_classes": 25,
            "note": "recomputed on the published word; deferred flag-9 head-step repair not reopened",
        },
    }
    end_cut = {
        "published_terminal_transport": [CUT, pub_cut[4]],
        "published_before_chart": list(canon(pub_cut[2])),
        "published_detour_via_full_rank": (9 - len(canon(pub_cut[2]))) + (9 - len(f23)),
        "published_detour_added_rank": (9 - len(canon(pub_cut[2]))) + (9 - len(f23)) - pub_cut[4],
        "attaining_words": ["T", "S", "T48"],
        "private_discount_word": "P",
    }
    return {
        "schema_version": 1,
        "claim_id": "p104-flag9-side-correction-bill",
        "pinned_main": "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "flag_index": FLAG_INDEX,
        "basis_head": head,
        "cut_event": CUT,
        "corrections": spec,
        "bill": {"published": base, **out},
        "obstruction": obstruction,
        "end_cut": end_cut,
        "selected_kappa": SELECTED_KAPPA,
        "no_new_kappa": True,
    }


def admit(root, cert, new_recipes):
    got = json.loads(json.dumps(receipt(root, cert, new_recipes)))
    need(got == cert, "receipt differs from committed certificate")
    b, ob = cert["bill"], cert["obstruction"]
    need(ob["entry"] == {
        "target": "Y23", "source": "X4", "gram": -1,
        "correction_coefficient": "1/2", "diagonal_gram": 2,
    }, "entry")
    need(ob["source_leaves_target_final_at"] == 745, "leave event")
    need(ob["selected_feeder"]["from_register"] == "X58" and ob["selected_feeder"]["head"] == 333, "X58 feeder")
    need(ob["selected_feeder"]["gram_with_target"] == 0 and not ob["selected_feeder"]["head_in_target_final"], "333 orthogonal")
    need(ob["flag_head_in_target_final"] and not b["T"]["head_in_target_frame_before_correction"], "head arrives only at terminal after-frame")
    need(ob["source_forced_full_from"] == 1613, "X4 forced full from 1613")
    need(ob["direct_cut_classes"] == 25 and all(x[1] for x in ob["direct_first_obstruction"]), "25/25 obstructed")
    need(ob["private_early_delivery_cuts"] == 7 and all(x[1] for x in ob["private_early_first_obstruction"]), "7/7 early private")
    need(ob["non_private_registers_at_rank_floor"] == 280, "rank floor")
    need(ob["leave_alone_forcing_census"]["open_pr"] == 3614, "cite #3614")
    for name, want in (("T", [2, 1, 1, 2]), ("S", [3, 1, 2, 2]), ("P", [5, 1, 1, 1]), ("T48", [49, 48, 1, 2])):
        r = b[name]
        need([r["added_vs_published"][k] for k in ("events", "scalar_adds", "transport_occurrences", "rank_mass")] == want, name + " bill")
        need(r["native_validate_coefficient_zero"] == "PASS", name + " native")
        need(r["real_word_rejected_by_unchanged_checker_at"] == "full physical boundary endpoint Y23", name + " rejection site")
        need(r["changed_final_rows"] == ["Y23"], name + " only Y23 changes")
        need(r["head_in_correction_charts"], name + " head in correction charts")
    need(b["T"]["profile_delta_vs_published"] == {"1": 1, "5": -1, "6": 1}, "T profile")
    need(b["S"]["profile_delta_vs_published"] == {"1": 2}, "S profile")
    need(b["P"]["profile_delta_vs_published"] == {"1": 1}, "P profile")
    need(b["P"]["private_events"] == {"zero": 9, "copy": 9, "erase": 9}, "P private lifetime")
    need(b["T"]["Y23_final_X4"] == b["S"]["Y23_final_X4"] == b["P"]["Y23_final_X4"] == "0", "entry applied")
    need(b["T48"]["Y23_final_row_is_identity"], "row 23 becomes y + x")
    need(b["T"]["added_rank_by_register"] == {"Y23": 2} and b["S"]["added_rank_by_register"] == {"X4": 2}, "even per-register mass")
    need(b["T"]["target_frame_before_correction_rank"] == 3, "correction leaves the rank-3 before-chart")
    need(cert["end_cut"]["published_detour_added_rank"] == 2, "end-cut +2")
    need(cert["selected_kappa"] == SELECTED_KAPPA and cert["no_new_kappa"] is True, "kappa unchanged")
    return got


def main(root=ROOT):
    cert = loads((HERE / "CERTIFICATE.json").read_bytes())
    new_recipes = loads((HERE / "CORRECTION-RECIPES.json").read_bytes())["recipes"]
    admit(root, cert, new_recipes)
    print(MARKER)


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT)
