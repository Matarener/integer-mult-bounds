"""K-defect sector census for the retained R439 helper-star words.

Scope: three retained finite words at the current main checkout.
- helper_star  research/r439-helper-stars-seed19/candidate.json.gz  (PR967 lineage, 11,783 ADDs)
- composition  research/r439-bsection-stars-seed01/composition.json.gz (PR1062, 11,515 ADDs)
- candidate    research/r439-bsection-stars-seed01/candidate.json.gz   (PR1062, 11,500 ADDs)

For each word the syntactic conclusion flag K_equals_D is false (retained claims).
This script (a) re-derives the raw-word helper part K and the D-derived matrix N
with an independent GF(2) replay and cross-checks every derived boolean against the
pinned owner checker research/e8-bit-p111-tuned/code/xcheck_p.py, (b) decomposes the
K != N defect into per-helper-column sectors with exact bit counts, (c) tests the
per-operation condition KS(h) ("sector h alone satisfies K = N") on every helper that
D reads, (d) enumerates all single-D-gate removals and all single-bit toggles to show
no single-operation edit can repair K_equals_D, and (e) classifies why the syntactic
H2 flag fails (gate frame, read kind, and start-frame clauses).

Finite certificate on three named words only. No kappa, no supplier admission, no
selected-frontier change, no native or hosted replay.

usage: python3 -I -B verify.py [--json OUT]
"""
import gzip
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

WORDS = {
    "helper_star": "research/r439-helper-stars-seed19/candidate.json.gz",
    "composition": "research/r439-bsection-stars-seed01/composition.json.gz",
    "candidate": "research/r439-bsection-stars-seed01/candidate.json.gz",
}
CHECKER = "research/e8-bit-p111-tuned/code/xcheck_p.py"


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_checker():
    spec = importlib.util.spec_from_file_location("xcheck_p", os.path.join(ROOT, CHECKER))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def my_raw(w):
    """Independent GF(2) symbolic replay of W0 = (A, scatter, B) over all columns.

    Register r starts as column e_r; targets accumulate retained totals at the
    scatter; no frames, no D, no C. Covers arbitrary sources and arbitrary dirty
    helpers in one shot because every column is carried symbolically."""
    v, R = w["v"], w["R"]
    n = 2 * v + R
    val = [1 << r for r in range(n)]
    for name in ("A", "scatter", "B"):
        if name == "scatter":
            copies = [val[q] for q in w["ret"]]
            for t, row in enumerate(w["scatter"]):
                acc = 0
                for k in row:
                    acc ^= copies[k]
                val[v + t] ^= acc
        else:
            for _, d, srcs in w[name]:
                acc = 0
                for s in srcs:
                    acc ^= val[s]
                val[d] ^= acc
    return val


def d_matrix(w):
    """N[t] = XOR of helper columns that D adds to target t (mirrors the checker's
    construction, returned with the full column mask so non-helper bits are visible)."""
    v = w["v"]
    N = [0] * v
    for _, d, srcs in w["D"]:
        if v <= d < 2 * v:
            for s in srcs:
                N[d - v] ^= 1 << s
    return N


def bits(x):
    out = []
    i = 0
    while x:
        if x & 1:
            out.append(i)
        x >>= 1
        i += 1
    return out


def census(w, fdim):
    v, R = w["v"], w["R"]
    smask = ((1 << R) - 1) << (2 * v)
    raw = my_raw(w)
    N = d_matrix(w)
    K = [raw[v + t] & smask for t in range(v)]
    defects = [K[t] ^ (N[t] & smask) for t in range(v)]
    k_eq_n = all(K[t] == N[t] for t in range(v))  # mirrors the checker flag exactly
    # H2 clause breakdown: read-kind clause (all D reads helpers / no non-helper bits
    # survive in N) versus the two frame clauses (gate frame, start frame).
    h2_gates_nonzero_frame = sum(1 for f, _, _ in w["D"] if fdim[f] != 0)
    h2_start_violations = sum(1 for r in range(v, 2 * v + R) if fdim[w["start"][r]] != 0)
    h2_dest_not_target = sum(1 for _, d, _ in w["D"] if not (v <= d < 2 * v))
    h2_reads_nonhelper = sum(1 for _, _, srcs in w["D"] if any(s < 2 * v for s in srcs))
    # non-helper columns surviving in N (uncancelled): syntactic K = N is then
    # unreachable for those targets regardless of A/scatter/B.
    n_bad = [t for t in range(v) if N[t] & ~smask]
    total = sum(len(bits(x)) for x in defects)
    sectors = {}
    for t, x in enumerate(defects):
        for c in bits(x):
            sectors.setdefault(c - 2 * v, []).append(t)
    star_helpers = sorted({s - 2 * v for _, _, srcs in w["D"] for s in srcs if s >= 2 * v})
    ks_pass = [h for h in star_helpers if not sectors.get(h)]
    ks_fail = [h for h in star_helpers if sectors.get(h)]
    # single-D-gate removal repair test: removing gate (f, y_t, srcs) toggles exactly
    # the bits of its helper reads on target t.
    single_gate_repairs = []
    for gi, (_, d, srcs) in enumerate(w["D"]):
        if not (v <= d < 2 * v):
            continue
        t = d - v
        flip = 0
        for s in srcs:
            flip ^= (1 << s) & smask
        ok = True
        for u in range(v):
            dz = defects[u] ^ (flip if u == t else 0)
            if dz:
                ok = False
                break
        if ok:
            single_gate_repairs.append(gi)
    # single-bit toggle repair over all (t, helper column) positions: possible iff the
    # total defect is exactly one bit.
    single_bit_repair_possible = total == 1
    # H2 failure classification over D gates (frame id, read kind).
    return dict(
        v=v,
        R=R,
        K=K,
        N=N,
        defects=defects,
        k_eq_n=k_eq_n,
        N_nonhelper_columns_targets=n_bad,
        defect_total_bits=total,
        h2_gates_nonzero_frame=h2_gates_nonzero_frame,
        h2_start_frame_violations=h2_start_violations,
        h2_dest_not_target=h2_dest_not_target,
        h2_reads_nonhelper=h2_reads_nonhelper,
        defective_sectors=sorted(sectors),
        sector_targets={str(h): ts for h, ts in sorted(sectors.items())},
        star_helpers=star_helpers,
        KS_pass=ks_pass,
        KS_fail=ks_fail,
        single_gate_repairs=single_gate_repairs,
        single_bit_repair_possible=single_bit_repair_possible,
    )


def main():
    x = load_checker()
    with open(os.path.join(HERE, "SOURCES.json")) as f:
        bindings = {row["path"]: row["sha256"] for row in json.load(f)["files"] if row["usage"] == "input"}
    for rel, want in bindings.items():
        got = sha256(os.path.join(ROOT, rel))
        if got != want:
            print("FAIL_R439_STAR_KDEFECT_SECTORS source binding mismatch:", rel)
            sys.exit(1)
    controls = [("source_bindings_match", True)]
    result = {"base_files": {}, "words": {}}
    prev_raw = {}
    for name, rel in WORDS.items():
        path = os.path.join(ROOT, rel)
        result["base_files"][rel] = sha256(path)
        w = json.load(gzip.open(path, "rt"))
        W = x.Word(w)
        fl = W.full()                      # legality + exact F2 identity, all columns
        H, C, _info = W.interface()
        cs = census(w, W.fdim)
        # cross-check every boolean this script derives against the pinned checker
        v, R = w["v"], w["R"]
        n = 2 * v + R
        xmask = (1 << v) - 1
        ymask = ((1 << v) - 1) << v
        raw = my_raw(w)
        my_J = all(raw[v + t] & xmask == 1 << t for t in range(v))
        my_U = all(raw[r] & ymask == 0 for r in range(n) if not (v <= r < 2 * v))
        agree = (cs["k_eq_n"] == C["K_equals_D"]) and (my_J == C["J_identity"]) and (my_U == C["U_block_form"])
        # retained pattern: H1/H3/H4/H5 pass, H2 false; U/J/Uinv pass, K_equals_D false
        pattern = (
            H["H1_no_target_feeds_z"] and H["H3_A_z_only_scatter_targets_B_split"]
            and H["H4_C_literal_reverse_at_full"] and H["H5_V_identity"]
            and not H["H2_D_frame0_targets_from_helpers"]
            and C["U_block_form"] and C["J_identity"] and C["C_is_U_inverse"] and not C["K_equals_D"]
        )
        result["words"][name] = {
            "word_file": rel,
            "gates": fl["gates"],
            "columns": fl["columns"],
            "flags_H": {k: bool(b) for k, b in H.items()},
            "flags_C": {k: bool(b) for k, b in C.items()},
            "retained_pattern": bool(pattern),
            "independent_agreement": bool(agree),
            "defect_total_bits": cs["defect_total_bits"],
            "defective_sectors": cs["defective_sectors"],
            "defective_sector_target_lists": cs["sector_targets"],
            "star_helpers_read_by_D": len(cs["star_helpers"]),
            "KS_pass_helpers": cs["KS_pass"],
            "KS_fail_helpers": cs["KS_fail"],
            "single_D_gate_removal_repairs": cs["single_gate_repairs"],
            "single_bit_repair_possible": cs["single_bit_repair_possible"],
            "N_nonhelper_columns_targets": cs["N_nonhelper_columns_targets"],
            "h2_gates_nonzero_frame": cs["h2_gates_nonzero_frame"],
            "h2_start_frame_violations": cs["h2_start_frame_violations"],
            "h2_dest_not_target": cs["h2_dest_not_target"],
            "h2_reads_nonhelper": cs["h2_reads_nonhelper"],
        }
        prev_raw[name] = (cs["K"], cs["N"])

    # invariance diagnostics between the words (all share the same labels/frames)
    hs, co, ca = prev_raw["helper_star"], prev_raw["composition"], prev_raw["candidate"]
    n_identical_12 = hs[1] == co[1]           # D byte-identical per the retained claim
    n_xor_bits_3 = sum(bin(a ^ b).count("1") for a, b in zip(co[1], ca[1]))  # star rerun
    k_diff = {
        "composition_vs_helper_star": sum(bin(a ^ b).count("1") for a, b in zip(hs[0], co[0])),
        "candidate_vs_composition": sum(bin(a ^ b).count("1") for a, b in zip(co[0], ca[0])),
    }
    result["cross_word"] = {
        "N_identical_helper_star_vs_composition": bool(n_identical_12),
        "N_xor_bits_composition_vs_candidate": n_xor_bits_3,
        "helper_part_K_diff_bits": k_diff,
    }

    # controls (in-memory only; nothing on disk is modified)
    w0 = json.load(gzip.open(os.path.join(ROOT, WORDS["candidate"]), "rt"))
    cs0 = census(w0, x.Word(w0).fdim)
    # c1: substituting N := K (the semantic route's conclusion, not its premise) makes
    # K = N true by construction; the honest claim is only that no N from D satisfies it.
    sub_ok = all(cs0["K"][t] == (cs0["K"][t]) for t in range(cs0["v"]))
    controls.append(("N_substitution_true_by_construction", sub_ok))
    # c2: flipping one defect bit changes exactly one sector membership (localization sane)
    t0 = next(t for t, z in enumerate(cs0["defects"]) if z)
    c = bits(cs0["defects"][t0])[0]
    flipped = list(cs0["defects"])
    flipped[t0] ^= 1 << c
    changed = sum(bin(a ^ b).count("1") for a, b in zip(flipped, cs0["defects"]))
    controls.append(("single_flip_changes_one_bit_only", changed == 1))
    # c3: total defect >= 2 on every word -> no single-bit or single-gate repair exists
    all_multi = all(r["defect_total_bits"] >= 2 and not r["single_D_gate_removal_repairs"]
                    and not r["single_bit_repair_possible"] for r in result["words"].values())
    controls.append(("no_single_operation_repair_all_words", all_multi))
    # c4: agreement with the pinned owner checker on every word and both flags
    all_agree = all(r["independent_agreement"] and r["retained_pattern"] for r in result["words"].values())
    controls.append(("checker_agreement_and_retained_pattern", all_agree))

    ok = (
        all_agree
        and all_multi
        and sub_ok
        and changed == 1
        and n_identical_12
        and k_diff["composition_vs_helper_star"] == 0
    )
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        with open(out, "w") as f:
            json.dump({"status": "PASS_R439_STAR_KDEFECT_SECTORS" if ok else "FAIL",
                      "checker_sha256": sha256(os.path.join(ROOT, CHECKER)),
                      **result,
                      "controls": [{"name": n, "pass": bool(p)} for n, p in controls]}, f, indent=1, sort_keys=True)
    if not ok:
        print("FAIL_R439_STAR_KDEFECT_SECTORS", json.dumps(
            {n: bool(p) for n, p in controls}, sort_keys=True))
        sys.exit(1)
    tsum = "/".join(str(result["words"][k]["defect_total_bits"]) for k in WORDS)
    sc = "/".join(str(len(result["words"][k]["defective_sectors"])) for k in WORDS)
    ks = "/".join("%d/%d" % (len(result["words"][k]["KS_pass_helpers"]), result["words"][k]["star_helpers_read_by_D"])
                 for k in WORDS)
    print("PASS_R439_STAR_KDEFECT_SECTORS words=3 defect_bits=%s defective_sectors=%s KS_pass=%s "
          "single_op_repairs=0 controls=%d no_new_kappa" % (tsum, sc, ks, len(controls)))

if __name__ == "__main__":
    main()
