#!/usr/bin/env python3.12
"""Independent transfer audit of the PR4091 pooled ceiling against the
retained PR4088 head.

Checks, all on committed evidence under the repository root:

A. Word equivalence: the four shared scalar-word inputs frozen in
   research/staged-fourth-mixture-ceiling/source4088/inputs/ (PR4088 head
   76088d49e3ed4142a958659aa996b0ca4da5e88e) versus the retained head
   research/staged544-mixed-fourth-entry/inputs/ (72d7efc181edb21806a878f1
   74847c96dd410ab0), compared as sha256 of each gzip payload and of the
   canonical JSON re-serialisation (per CONTRIBUTING, compressed containers
   are not compared byte-wise).
B. Word-profile anchors: the exact per-call profiles appear verbatim in both
   packages' written proofs.
C. Bin-inventory equivalence: capacity-8/16/32/48 inventory of the ceiling
   model versus the later fill's published totals; constant residual mass.
D. Word-law identity: each package's published paid profile must decompose
   as calls x three-entry word + x x (four minus three) + idle residual, with
   x derived independently from rank-1, rank-3 and rank-4 coordinates and
   equal to each package's published fourth-call count.
E. Independent moment recomputation: solve sum_r n_r (r/73)^(1-a) / (896*360)
   = 1 by interval bisection in Decimal (precision 60) for both published
   profiles and contain the result in each package's own published bracket.
F. Transfer verdict: recomputed roots lie strictly below the PR4091 pooled
   ceiling bracket; exact remaining headroom with decimal and ratio.

This is a finite source-bound audit. It is not a replay of PR4091's
841-pattern coverage proof, not supplier admission, not a new kappa, and it
does not change the selected record. Assumptions that this audit does not
re-derive are listed in RESULT.json under "assumptions_not_rederived".
"""
import gzip
import hashlib
import json
import os
import sys
from decimal import Decimal, getcontext
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CEIL = os.path.join(ROOT, "research", "staged-fourth-mixture-ceiling")
MIX4 = os.path.join(ROOT, "research", "staged544-mixed-fourth-entry")

CEIL_HEAD_PR4088 = "76088d49e3ed4142a958659aa996b0ca4da5e88e"
MIX4_HEAD = "72d7efc181edb21806a878f174847c96dd410ab0"

WORD_FILES = ["THREE-base.json.gz", "THREE-extra.json.gz",
              "FOUR-base.json.gz", "FOUR-extra.json.gz"]

# Per-call local words, PR4085 three-entry receiver-sharing word and the
# PR4088 four-entry variant, as published identically in both packages
# (anchor-checked in check_word_anchors below).
WORDS3 = {1: 2487, 2: 713, 3: 224, 4: 102, 5: 20, 8: 8}
WORDS4 = {1: 2489, 2: 713, 3: 227, 4: 99, 5: 20, 8: 8}

CALLS = 3240
WIDTH_M = 73
STOCK_W = 896 * 360
BIN_COUNTS = {8: 241920, 16: 161280, 32: 161280, 48: 161280}
BIN_TOTAL = 725760
ROLE_TOTAL = 1321920
REPLICAS = 360
IDLE_TOTAL = 162900


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def load_json(path):
    with open(path, "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def check_word_files():
    """A. Byte-for-byte payload equivalence of the four shared word files."""
    rows = []
    for name in WORD_FILES:
        old_p = os.path.join(CEIL, "source4088", "inputs", name)
        new_p = os.path.join(MIX4, "inputs", name)
        if not (os.path.isfile(old_p) and os.path.isfile(new_p)):
            rows.append({"file": name, "present": False})
            continue
        with open(old_p, "rb") as fh:
            old_raw = fh.read()
        with open(new_p, "rb") as fh:
            new_raw = fh.read()
        old_payload = gzip.decompress(old_raw)
        new_payload = gzip.decompress(new_raw)
        rows.append({
            "file": name,
            "present": True,
            "payload_equal": old_payload == new_payload,
            "canonical_equal": canonical(json.loads(old_payload)) ==
                             canonical(json.loads(new_payload)),
            "payload_sha256": sha(new_payload),
            "container_sha256_old": sha(old_raw),
            "container_sha256_new": sha(new_raw),
        })
    return rows


def check_word_anchors():
    """B. Per-call word profiles and the word delta appear in both packages.

    PR4091 PROOF.md publishes L3 and the delta d = L4 - L3; PR4088 README
    publishes both full profiles. Deriving WORDS4 = WORDS3 + d from the
    ceiling package and comparing against the fill package ties the two
    packages to the same word law without trusting either table alone.
    """
    with open(os.path.join(CEIL, "PROOF.md"), encoding="utf-8") as fh:
        ceil_proof = fh.read()
    with open(os.path.join(MIX4, "README.md"), encoding="utf-8") as fh:
        mix_readme = fh.read()
    l3 = "L3 = 2487 H1 + 713 H2 + 224 H3 + 102 H4 + 20 H5 + 8 H8"
    delta = "L4-L3 = 2 H1 + 3 H3 - 3 H4"
    t3 = "{1:2487,2:713,3:224,4:102,5:20,8:8}"
    t4 = "{1:2489,2:713,3:227,4:99,5:20,8:8}"
    derived4 = dict(WORDS3)
    derived4[1] += 2
    derived4[3] += 3
    derived4[4] -= 3
    return {
        "ceil_proof_has_L3": l3 in ceil_proof,
        "ceil_proof_has_delta": delta in ceil_proof,
        "derived_L4_matches": derived4 == WORDS4,
        "mix_readme_has_three": t3 in mix_readme,
        "mix_readme_has_four": t4 in mix_readme,
    }


def check_bins(ceil_res, mix_task_text):
    """C. Bin-inventory equivalence and constant residual mass."""
    idle_c = {int(k): v for k, v in ceil_res["idle"].items()}
    idle_m = {int(k): v for k, v in mix_task_text["idle"].items()}
    return {
        "ceil_bin_counts_match": dict(ceil_res["bin_counts"]) ==
                               {str(k): v for k, v in BIN_COUNTS.items()},
        "ceil_bin_total": sum(BIN_COUNTS.values()) == BIN_TOTAL,
        "ceil_bins_divide_replicas": BIN_TOTAL % REPLICAS == 0,
        "mix_publishes_bin_total": str(BIN_TOTAL) in mix_task_text["raw"],
        "mix_publishes_role_total": str(ROLE_TOTAL) in mix_task_text["raw"],
        "idle_total_ceiling": sum(idle_c.values()),
        "idle_total_mixed": sum(idle_m.values()),
        "idle_total_constant": sum(idle_c.values()) ==
                              sum(idle_m.values()) == IDLE_TOTAL,
    }


def derive_x(profile, idle):
    """D. Independent derivations of the fourth-call count from the profile."""
    prof = {int(k): v for k, v in profile.items()}
    idl = {int(k): v for k, v in idle.items()}
    base = {r: CALLS * w for r, w in WORDS3.items()}
    delta = {r: WORDS4[r] - WORDS3[r] for r in WORDS4}
    x1 = None
    if delta[1]:
        x1 = Fraction(prof[1] - base[1], delta[1])
    x4 = None
    if delta[4]:
        x4 = Fraction(base[4] - prof[4], -delta[4])
    x3 = None
    if delta[3]:
        x3 = Fraction(prof[3] - base[3] - idl.get(3, 0), delta[3])
    ok = (x1 == x3 == x4) and x1.denominator == 1
    residuals_ok = (prof[2] == base[2] and prof[8] == base[8]
                    and prof[5] == base[5] + idl.get(5, 0)
                    and prof[48] == idl.get(48, 0))
    return {
        "x_rank1": str(x1), "x_rank3": str(x3), "x_rank4": str(x4),
        "x_consistent": ok,
        "rank2_constant": prof[2] == base[2],
        "rank8_constant": prof[8] == base[8],
        "rank5_is_word_plus_idle5": prof[5] == base[5] + idl.get(5, 0),
        "rank48_is_idle48": prof[48] == idl.get(48, 0),
        "residuals_ok": residuals_ok,
        "x": int(x1) if ok else None,
    }


def bill(a, profile):
    total = Decimal(0)
    one = Decimal(1)
    for r, n in profile.items():
        ratio = Decimal(r) / Decimal(WIDTH_M)
        total += Decimal(n) * ((one - a) * ratio.ln()).exp()
    return total / Decimal(STOCK_W)


def solve_root(profile):
    """E. Bisection on the strictly increasing complete-moment bill."""
    getcontext().prec = 60
    lo, hi = Decimal("0.0010"), Decimal("0.0025")
    for _ in range(420):
        mid = (lo + hi) / 2
        if bill(mid, profile) < 1:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def frac_to_dec(s):
    num, den = s.split("/")
    getcontext().prec = 60
    return Decimal(num) / Decimal(den)


def literal_profile_from_proof(ceil_res):
    """Rebuild the pinned literal fill from the published pooled optimum plus
    the residual-bin delta recorded in PR4091 PROOF.md
    ("profile is `22785 H3+1625 H5+H16+2H32+138490 H48`")."""
    import re
    with open(os.path.join(CEIL, "PROOF.md"), encoding="utf-8") as fh:
        proof = fh.read()
    m = re.search(r"profile is `(\d+) H3\+(\d+) H5\+H16\+2H32\+(\d+) H48`",
                 proof)
    if m is None:
        return None, False
    h3, h5, h48 = (int(g) for g in m.groups())
    prof = {int(k): v for k, v in ceil_res["complete_profile"].items()}
    # pooled optimum residual multiset {3:22788,5:1620,48:138492} is replaced
    # by the literal one; delta paid = literal - pooled residuals.
    prof[3] += h3 - ceil_res["idle"]["3"]
    prof[5] += h5 - ceil_res["idle"]["5"]
    prof[16] = prof.get(16, 0) + 1
    prof[32] = prof.get(32, 0) + 2
    prof[48] += h48 - ceil_res["idle"]["48"]
    return prof, True


def check_roots(ceil_res, mix_res):
    prof_pool = {int(k): v for k, v in ceil_res["complete_profile"].items()}
    prof_m = {int(k): v for k, v in mix_res["profile"].items()}
    prof_lit, lit_parsed = literal_profile_from_proof(ceil_res)
    root_pool = solve_root(prof_pool)
    root_m = solve_root(prof_m)
    lit_lo = frac_to_dec(ceil_res["literal_root_bracket"][0])
    lit_hi = frac_to_dec(ceil_res["literal_root_bracket"][1])
    mix_lo = frac_to_dec(mix_res["root_lower"])
    mix_hi = frac_to_dec(mix_res["root_upper"])
    ceil_lo = Decimal(ceil_res["root_decimal_bracket"][0])
    ceil_hi = Decimal(ceil_res["root_decimal_bracket"][1])
    out = {
        "ceiling_profile_root_reproduced": ceil_lo <= root_pool <= ceil_hi,
        "root_pooled_optimum": str(root_pool),
        "root_later_head": str(root_m),
        "later_root_in_own_bracket": mix_lo <= root_m <= mix_hi,
        "later_root_below_ceiling": root_m < ceil_lo,
        "ceil_minus_later_upper_decimal": f"{ceil_hi - mix_hi:.30e}",
        "pinned_literal_profile_parsed_from_proof": lit_parsed,
    }
    if lit_parsed:
        root_lit = solve_root(prof_lit)
        out["root_pinned_literal"] = str(root_lit)
        out["pinned_literal_root_reproduced"] = lit_lo <= root_lit <= lit_hi
        out["pinned_headroom_decimal"] = f"{ceil_hi - lit_hi:.30e}"
        prev_up = frac_to_dec(mix_res["previous_revision_upper"])
        out["pinned_root_matches_later_packages_pin"] = (
            ceil_res["literal_root_bracket"][1]
            == mix_res["previous_revision_upper"]
            and lit_hi <= prev_up + Decimal(0))
        consumed = mix_hi - lit_hi
        out["margin_consumed_decimal"] = f"{consumed:.30e}"
        out["margin_consumed_ge_published_gain"] = consumed >= frac_to_dec(
            mix_res["gain_over_previous_revision"])
    return out


def run_audit():
    """Full audit; returns (verdict_bool, result_dict)."""
    ceil_res = load_json(os.path.join(CEIL, "RESULT.json"))
    mix_res = load_json(os.path.join(MIX4, "RESULT.json"))
    with open(os.path.join(MIX4, "TASK.json"), encoding="utf-8") as fh:
        mix_task = fh.read()

    words = check_word_files()
    anchors = check_word_anchors()
    bins = check_bins(ceil_res, {"raw": mix_task,
                                 "idle": mix_res.get("idle",
                                                 mix_res.get("idle_profile"))})
    law_c = derive_x(ceil_res["complete_profile"], ceil_res["idle"])
    law_m = derive_x(mix_res["profile"], mix_res["idle"])
    roots = check_roots(ceil_res, mix_res)

    checks_ok = (
        all(r.get("present") and r["payload_equal"] and r["canonical_equal"]
            for r in words)
        and all(anchors.values())
        and bins["ceil_bin_counts_match"] and bins["ceil_bin_total"]
        and bins["ceil_bins_divide_replicas"]
        and bins["mix_publishes_bin_total"] and bins["mix_publishes_role_total"]
        and bins["idle_total_constant"]
        and law_c["x_consistent"] and law_c["residuals_ok"]
        and law_m["x_consistent"] and law_m["residuals_ok"]
        and law_c["x"] == ceil_res["optimum_fourth_calls"] == 1080
        and law_m["x"] == mix_res["fourth_calls"] == 1090
        and roots["ceiling_profile_root_reproduced"]
        and roots["pinned_literal_profile_parsed_from_proof"]
        and roots.get("pinned_literal_root_reproduced") is True
        and roots.get("pinned_root_matches_later_packages_pin") is True
        and roots["later_root_in_own_bracket"]
        and roots["later_root_below_ceiling"]
        and roots.get("margin_consumed_ge_published_gain") is True
        and Decimal(roots["ceil_minus_later_upper_decimal"]) > 0
    )
    if checks_ok:
        roots["remaining_over_original_ratio"] = str(
            (Fraction(Decimal(roots["ceil_minus_later_upper_decimal"]))
             / Fraction(Decimal(roots["pinned_headroom_decimal"]))
             ).limit_denominator(10**9))
        roots["remaining_over_original_float"] = float(Decimal(
            roots["ceil_minus_later_upper_decimal"])
            / Decimal(roots["pinned_headroom_decimal"]))
    verdict = ("TRANSFER_SUPPORTED_AT_MODEL_PREMISES" if checks_ok
               else "AUDIT_FAILED")
    result = {
        "schema_version": 1,
        "status": verdict,
        "card": "independent-moment",
        "question": ("Does PR4091's fixed-inventory pooled ceiling transfer to "
                     "the retained later PR4088 head?"),
        "pinned_head_pr4088": CEIL_HEAD_PR4088,
        "retained_head_pr4088": MIX4_HEAD,
        "ceiling_bracket": ceil_res["root_decimal_bracket"],
        "word_file_payload_equal": sum(1 for r in words
                                      if r.get("payload_equal")),
        "word_files": words,
        "word_profile_anchors": anchors,
        "bin_inventory": bins,
        "word_law_pinned": law_c,
        "word_law_later": law_m,
        "moments": roots,
        "bill": {
            "form": "sum_r n_r (r/m)^(1-a) / W",
            "m": WIDTH_M,
            "W": STOCK_W,
        },
        "assumptions_not_rederived": [
            ("PR4091's 841 whole-helper pattern coverage and three dual "
             "certificates are not replayed here; the ceiling is taken as "
             "published by its own package."),
            ("Whether every literal exchange may reach an arbitrary idle "
             "multiset with the same residual total (PR4091 open question 1) "
             "is not settled by this audit."),
            ("Native, owner/phase, chronology, precision, tape, BIT and outer "
             "transfer obligations are inherited from the pinned packages and "
             "are not re-verified."),
        ],
    }
    return checks_ok, result


def main():
    out = None
    if "--output" in sys.argv:
        out = sys.argv[sys.argv.index("--output") + 1]
    ok, result = run_audit()
    if out:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print("wrote " + out)
    if not ok:
        print("AUDIT_FAILED")
        for name, val in sorted(result.items()):
            if isinstance(val, dict):
                for k, v in sorted(val.items()):
                    if v is False:
                        print("failed:", name, k)
        return 1
    print("PASS_CEILING_TRANSFER_AT_MODEL_PREMISES")
    print("word payload equal files: %d/4" % result["word_file_payload_equal"])
    print("x pinned=%d later=%d" % (result["word_law_pinned"]["x"],
                                    result["word_law_later"]["x"]))
    print("ceiling minus later root: %s"
          % result["moments"]["ceil_minus_later_upper_decimal"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
