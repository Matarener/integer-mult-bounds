#!/usr/bin/env python3
"""One-role cap-two bill against the direct ordinary-swap recipe.

The arithmetic is exact. It does not execute a native program, compiler,
Lean build, or selected cold replay, and it does not claim a new kappa.

Apache-2.0. Prepared by unpaidmoon with substantial Cursor Grok assistance.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise SystemExit(why)


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = []
    for row in manifest["files"]:
        path = ROOT / row["path"]
        actual = sha(path)
        need(actual == row["sha256"], "source byte mismatch: " + row["path"])
        pinned.append(row["path"])
    text = {
        "rows": (ROOT / "notes/batched-bit-rows.tex").read_text(encoding="utf-8"),
        "cover": (ROOT / "notes/three-stage-cover-bit.tex").read_text(encoding="utf-8"),
        "ceiling": (ROOT / "research/three-swap-cap2-physical-ceiling/README.md").read_text(encoding="utf-8"),
    }
    need("operates on exactly\n$1/W$ of the parent's logical volume." in text["rows"],
         "missing one-role volume sentence")
    need("Repetitions in the list represent\nseparate calls." in text["rows"],
         "missing separate-call sentence")
    need("Every call preserves all complete spectator fields" in text["cover"],
         "missing spectator sentence")
    need(r"J_A=R_{\rm tail}F_AR_{\rm tail}" in text["cover"], "missing direct J recipe")
    need(r"costs at most three children of widths $f,\lfloor f/2\rfloor," in text["cover"],
         "missing three-child upper recipe")
    need("B < (2F + 6Q - Delta)/4" in text["ceiling"], "missing #5099 threshold")
    need("increases volume to `2V/W`" in text["ceiling"], "missing two-owner volume sentence")
    need("No eligible chronological occurrence" in text["ceiling"], "missing open-caller sentence")
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    need(selected["kappa"] == "605457647/200000000000", "selected kappa moved")
    return pinned, selected["kappa"]


def gap_over_f(b_over_f, q_over_f, delta_over_f=0):
    """(F+4B+Delta - (3F+6Q)) / F for nonnegative rational ratios."""
    return 4 * b_over_f - 2 - 6 * q_over_f + delta_over_f


def main():
    pinned, kappa = authenticate()
    # #5099 screen: 0<=C<=17/5000 implies 2^(1-C) > 399/200.
    need(399 ** 5000 < 2 ** 4983 * 200 ** 5000, "power-screen integer bound")
    boundary = Fraction(399, 200)
    half_ratio_cap = Fraction(200, 399)  # strict upper bound on (1/2)^(1-C)
    need(Fraction(1, 2) + Fraction(3, 2) / boundary == Fraction(333, 266),
         "nominal break-even cap")
    # One-role service: B = 2F and Delta = 0. Strict success needs Q > F.
    need(gap_over_f(2, 1, 0) == 0, "Q=F is break-even, not a strict win")
    need(not (Fraction(2) < (2 + 6 * Fraction(1)) / 4), "B=2F and Q=F fails the strict test")
    # On the screen, Q/F <= 2^(C-1) < 200/399 < 1.
    need(half_ratio_cap < 1, "half-width ratio cap")
    screen_gap = gap_over_f(2, half_ratio_cap, 0)
    need(screen_gap == Fraction(398, 133), "screen gap at the unattained ratio cap")
    need(screen_gap > 0, "one-role bill loses against the direct upper recipe")
    # g(x)=6(x-1)/x increases for x>0, and the legal gap is strictly above g(boundary).
    def g(x):
        return 6 * (x - 1) / x
    need(g(boundary) == Fraction(398, 133), "boundary gap identity")
    need(g(boundary + Fraction(1, 10**6)) > g(boundary), "gap increases with the power")
    # Every integer width: floor(f/2)/f <= 1/2, so the screen ratio is <= 1/2^(1-C).
    width_cases = 0
    for f in range(1, 129):
        half = f // 2
        need(half * 2 <= f, "floor half")
        if f == 1:
            q_over_f = Fraction(0, 1)
        else:
            q_over_f = Fraction(half, f)  # tau=1, the most expensive half call inside C=0
            need(q_over_f <= Fraction(1, 2), "tau=1 half ratio")
        difference = gap_over_f(2, q_over_f, 0)
        need(difference > 0, "tau=1 one-role bill must lose")
        if f % 2 == 0:
            need(difference == 3, "even tau=1 gap is 3F")
        elif f == 1:
            need(difference == 6, "width-one gap is 6F")
        else:
            need(difference == 6 - 6 * q_over_f > 3, "odd tau=1 gap exceeds the even case")
        width_cases += 1
    # Positive control: a multi-owner price below the threshold can pass.
    # F=1, Q=1/2, Delta=0 => threshold = 5/4. B=1 is outside the one-role service.
    threshold = (2 + 6 * Fraction(1, 2)) / 4
    need(threshold == Fraction(5, 4), "control threshold")
    need(1 < threshold and gap_over_f(1, Fraction(1, 2), 0) < 0, "cheaper primitive can pass")
    need(not (2 < threshold), "one-role price fails the same control")
    # Positive outside cost cannot create a one-role win.
    need(gap_over_f(2, half_ratio_cap, Fraction(1, 100)) > screen_gap, "positive Delta widens the loss")
    # A negative Delta large enough can change the decision; it is not proved.
    rescue = gap_over_f(2, half_ratio_cap, -screen_gap - 1)
    need(rescue < 0, "unproved negative Delta is not a universal loss")
    receipt = {
        "status": "PASS_CAP2_ONE_ROLE_DIRECT_BILL",
        "caller": "one-role compilation of the #5083 five-call schedule",
        "bill": {"F": "F", "Q": "Q", "B": "2F", "wNew": "0", "wDirect": "0", "Delta": "0"},
        "strict_test": "B<(2F+6Q-Delta)/4",
        "screen": {"C": "[0,17/5000]", "Q_over_F_strict_cap": "200/399",
                   "gap_over_F_strict_lower": "398/133"},
        "width_cases": width_cases,
        "selected_kappa_unchanged": kappa,
        "new_kappa": None,
        "sources": pinned,
    }
    print("PASS_CAP2_ONE_ROLE_DIRECT_BILL")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
