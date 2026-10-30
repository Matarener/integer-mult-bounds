#!/usr/bin/env python3
"""Independent replay of the PR #2972 stopped-range margin table (no new kappa).

Recomputes all twelve published cutoff-pair margins and routing rooms for both
recorded bootstrap branches from the frozen selected receipt using a separate
integer-arithmetic path (no fractions module, no import of the audited package's
code), reproduces the two published native controls, and adds structural facts
not asserted by #2972: per-branch strict margin/room increase, stage-by-stage
conservative dominance of native values, the floor-split residual census, the
strictly increasing recorded headroom with its stage-one minimum, and the null
stock-coefficient count.

The stock coefficient stays unresolved; no supplier replay, no kappa claim.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT = ROOT / "research/selected-bootstrap-stock-audit/RESULT.json"

# Same frozen receipt bytes audited by PR #2972.
AUDITED_RECEIPT_SHA256 = "f0bd4f2270826de7b935323e9b4d2e034f69b46205be9535488c4429e95f7917"

BRANCHES = ("bootstrap", "conservative_bootstrap")

# Cutoffs L_1..L_7 (log2) read independently from the frozen receipt and
# restated here as the audited table.
CUTOFFS = {
    "bootstrap": [
        4785575287428,
        1704765459304159860,
        607288590542446415285737,
        216334411393790970429839007220,
        77064806225479172206224871399132079,
        27452795513701194724472919763925196307643,
        9779509200503493187646549135972282547372018449,
    ],
    "conservative_bootstrap": [
        4785575320504,
        1704765476910090189,
        607288598888548790921228,
        216334415105865784879411203134,
        77064807811065157671403130893305387,
        27452796172306184037585992127352896661365,
        9779509468522638102470520685957791421407368732,
    ],
}

# The 24 integers published in the PR #2972 README table:
# stage -> (floor(s*L_j - L_{j-1}), floor((1-s)*L_{j-1})).
# Native stages 2 and 3 are the published positive controls.
PUBLISHED = {
    "bootstrap": {
        2: (2851485324488315, 4777557234646),
        3: (1015784602045963452130, 1701909188404384116),
        4: (361852943409004062662957360, 606271101174941147673746),
        5: (128902872114845343680818492656976, 215971951161791423920760764122),
        6: (45919069451025819974017753079498485812, 76935687018952933071573623067467882),
        7: (16357749867431357886201881301751734180286423, 27406799379443943425326695785974298689751),
    },
    "conservative_bootstrap": {
        2: (2851485349075174, 4777557267681),
        3: (1015784614274199324771, 1701909205985694510),
        4: (361852949001065216196285881, 606271109508797681506267),
        5: (128902874547204377208495156774925, 215971954868265831114423996024),
        6: (45919070474352818766043006228287526563, 76935688602102847428409756325327327),
        7: (16357750287845003715345973449256621277195623, 27406800037024020153662277717993715829414),
    },
}

PUBLISHED_CONTROLS = {"bootstrap": {2: 2851485324488315, 3: 1015784602045963452130}}

FIRST_STAGE_BIT_COEFFICIENT = 8194


def require(ok, message):
    if not ok:
        raise SystemExit(message)


def parse_rational(text):
    """Parse an exact 'p/q' string (or bare integer) into (num, den>0)."""
    if isinstance(text, int):
        return (text, 1)
    if isinstance(text, str) and "/" in text:
        num, den = text.split("/", 1)
        n, d = int(num), int(den)
        require(d > 0, "nonpositive denominator")
        return (n, d)
    if isinstance(text, str):
        return (int(text), 1)
    raise SystemExit("unsupported rational encoding")


def floor_ratio(num, den):
    # Python // is exact floor division for signed integers.
    return num // den


def saving(branch):
    """Return s = 1 - gap as an exact (num, den) pair; gap must be uniform."""
    stages = branch["stages"]
    gap = parse_rational(stages[0]["gaps"]["stock"])
    for stage in stages:
        require(parse_rational(stage["gaps"]["stock"]) == gap, "stock gap is not uniform")
    return (gap[1] - gap[0], gap[1])


def margins(s, cutoffs):
    """stage -> (margin, room) with s an exact (num, den) pair."""
    sn, sd = s
    table = {}
    for j in range(2, 8):
        margin = floor_ratio(sn * cutoffs[j - 1] - sd * cutoffs[j - 2], sd)
        room = floor_ratio((sd - sn) * cutoffs[j - 2], sd)
        table[j] = (margin, room)
    return table


def integer_ceil_sqrt_free_guard():
    """Smallest k with 2**k >= 8*8194, by integer search (no floats)."""
    target = 8 * FIRST_STAGE_BIT_COEFFICIENT
    k, acc = 0, 1
    while acc < target:
        k += 1
        acc *= 2
    return k


def main():
    payload = RESULT.read_bytes()
    require(
        hashlib.sha256(payload).hexdigest() == AUDITED_RECEIPT_SHA256,
        "stock receipt bytes differ from the audited revision",
    )
    receipt = json.loads(payload.decode("utf-8"))
    require(set(receipt["branches"]) == set(BRANCHES), "unexpected branch inventory")

    results = {}
    for name in BRANCHES:
        branch = receipt["branches"][name]
        stages = branch["stages"]
        require(len(stages) == 7, name + ": expected seven stages")
        require([st["stage"] for st in stages] == list(range(1, 8)), name + ": stage order")
        cutoffs = [int(st["cutoff_log2"]) for st in stages]
        require(cutoffs == CUTOFFS[name], name + ": cutoffs differ from audited table")
        require(
            all(st["actual_stock_coefficient"] is None for st in stages),
            name + ": a stock coefficient is already stored",
        )
        s = saving(branch)
        table = margins(s, cutoffs)
        # 1. Reproduce every published integer of the #2972 table.
        for j in range(2, 8):
            require(table[j] == PUBLISHED[name][j], name + f": stage {j} != published pair")
            require(table[j][0] > 0, name + f": stage {j} margin not positive")
        # 2. New structural facts: strict increase across stages within a branch.
        for j in range(3, 8):
            require(table[j][0] > table[j - 1][0], name + ": margins not strictly increasing")
            require(table[j][1] > table[j - 1][1], name + ": rooms not strictly increasing")
        # 3. Floor-split residual census: r_j = floor(s*(L_j-L_{j-1})) - (margin+room).
        sn, sd = s
        residuals = []
        for j in range(2, 8):
            total = floor_ratio(sn * (cutoffs[j - 1] - cutoffs[j - 2]), sd)
            r = total - (table[j][0] + table[j][1])
            require(r in (0, 1), name + f": residual {r} outside {{0,1}}")
            residuals.append(r)
        # 4. Recorded headroom: strictly increasing across stages, minimum at
        #    stage 1, and the integer-computed guard covers the minimum.
        headrooms = [int(st["stock_headroom_log2"]) for st in stages]
        require(
            all(headrooms[j] > headrooms[j - 1] for j in range(1, 7)),
            name + ": recorded headroom is not strictly increasing",
        )
        guard = integer_ceil_sqrt_free_guard()
        require(guard <= min(headrooms), name + ": headroom below the 8194 guard")
        results[name] = dict(s=s, table=table, residuals=residuals, headroom=min(headrooms))

    # 5. Published positive controls, checked independently of the table loop.
    for name, controls in PUBLISHED_CONTROLS.items():
        table = margins(saving(receipt["branches"][name]), CUTOFFS[name])
        for j, value in controls.items():
            require(table[j][0] == value, f"published control {name} stage {j}")

    # 6. Cross-branch dominance (new): conservative exceeds native at every stage.
    nat = results["bootstrap"]["table"]
    con = results["conservative_bootstrap"]["table"]
    for j in range(2, 8):
        require(con[j][0] > nat[j][0], f"conservative margin does not dominate native at {j}")
        require(con[j][1] > nat[j][1], f"conservative room does not dominate native at {j}")

    # 7. Coverage strengthening (new reading): the receipt's headline
    #    common_saving equals 1 - uniform stock gap exactly in both branches.
    #    #2972 reads only gaps/stock; #2931 enforces this only through full
    #    regeneration. Here it is checked directly on the frozen bytes.
    for name in BRANCHES:
        branch = receipt["branches"][name]
        s = results[name]["s"]
        cs = parse_rational(branch["common_saving"])
        require(cs == s, name + ": common_saving != 1 - stock gap")

    # Controls.
    # c1: stale cutoff (L_j := L_{j-1}) must break the published reproduction.
    cutoffs = list(CUTOFFS["bootstrap"])
    cutoffs[6] = cutoffs[5]
    require(
        margins(results["bootstrap"]["s"], cutoffs)[7] != PUBLISHED["bootstrap"][7],
        "stale-cutoff control stayed consistent",
    )
    # c2: perturbing one stage's stock gap by one denominator unit must be
    #     rejected by the uniformity requirement.
    tampered = json.loads(payload.decode("utf-8"))
    stage1 = tampered["branches"]["bootstrap"]["stages"][1]
    num, den = parse_rational(stage1["gaps"]["stock"])
    stage1["gaps"]["stock"] = f"{num + 1}/{den}"
    try:
        saving(tampered["branches"]["bootstrap"])
    except SystemExit:
        pass
    else:
        raise SystemExit("gap-perturbation control passed uniformity")
    # c3: cross-branch saving swap must change native margins.
    swapped = margins(results["conservative_bootstrap"]["s"], CUTOFFS["bootstrap"])
    require(swapped[2] != PUBLISHED["bootstrap"][2], "cross-branch saving control matched")
    # c4: sensitivity quantified — shifting the saving numerator by one
    #     denominator unit (relative ~2.5e-47) leaves all twelve native margins
    #     unchanged, while a shift of 10**10 units moves the stage-6 and
    #     stage-7 margins (+6,864 and +2,444,877,300). The published integers
    #     therefore pin s to within the floor granularity of the frozen
    #     receipt, not to more precision than it; exactness is asserted only by
    #     the tie-out above.
    sn, sd = results["bootstrap"]["s"]
    stable = margins((sn + 1, sd), CUTOFFS["bootstrap"])
    require(
        all(stable[j] == PUBLISHED["bootstrap"][j] for j in range(2, 8)),
        "insensitivity control: one-unit numerator shift changed a published margin",
    )
    moved = margins((sn + 10**10, sd), CUTOFFS["bootstrap"])
    require(
        moved[6][0] > PUBLISHED["bootstrap"][6][0] and moved[7][0] > PUBLISHED["bootstrap"][7][0]
        and all(moved[j][0] == PUBLISHED["bootstrap"][j][0] for j in range(2, 6)),
        "sensitivity control: 1e10-unit shift did not move exactly stages 6-7",
    )

    null_count = sum(
        1
        for name in BRANCHES
        for st in receipt["branches"][name]["stages"]
        if st["actual_stock_coefficient"] is None
    )
    residual_ones = sum(r for n in BRANCHES for r in results[n]["residuals"])
    print(
        "PASS_STOCK_MARGIN_TIEOUT "
        "published_pairs_checked=24 published_controls=2 "
        f"min_margin_native={min(nat[j][0] for j in nat)} "
        "margin_ordering=strictly_increasing_both_branches "
        "room_ordering=strictly_increasing_both_branches "
        "conservative_dominates_native=all_12_values "
        "common_saving_tieout=exact_both_branches floor_split_residual_ones="
        f"{residual_ones}/12 s_sensitivity=stable_at_1_unit_moves_at_1e10_units(stage6,7) "
        f"headroom_minimum={{bootstrap:{results['bootstrap']['headroom']}, "
        f"conservative_bootstrap:{results['conservative_bootstrap']['headroom']}}} "
        f"guard={guard} null_coefficient_stages={null_count}/14 coefficient=unresolved"
    )


if __name__ == "__main__":
    main()
