#!/usr/bin/env python3
"""Locate the selected complex supplier's bootstrap cutoff sequence in source.

Answers stock-margin-chain's open question 2: the frozen PR1087 assembler
defines exactly two bootstrap cutoff sequences, both inside `outer_witness`,
and both are driven by the complex lower (the bit lower enters only through a
non-binding minimum and the 512-bit charged constant). The m=73 supplier is
priced inside those same witnesses, and the receipt's `bootstrap` /
`conservative_bootstrap` fields are the emitted sequences. All fourteen
recorded stage triples, both recorded kappas and the twelve published
membership margins are reproduced here in exact rational arithmetic from this
input path. The stock coefficient sigma stays uncomputed; that residual is
stated, not filled. No supplier replay and no kappa claim.

Standard library only. Python 3.10+ (registered launcher gates on 3.12).
"""
import hashlib
import io
import json
import tarfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent

ASSEMBLY = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
RESULT = ROOT / "research/selected-bootstrap-stock-audit/RESULT.json"
SELECTED = ROOT / "certificates/selected-result.json"
CATALOG = ROOT / "docs/research/agent-task-catalog.json"
TARBALL = ROOT / "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"

# Pinned byte bindings (sha256), recorded in SOURCES.json.
SHA = {
    "assembly": "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    "result": "f0bd4f2270826de7b935323e9b4d2e034f69b46205be9535488c4429e95f7917",
    "tarball": "d4acf04daef85d4514f80ec5fcd2492d0c60e5d6c49fa71b3e6523f8db2dea86",
    "selected": "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129",
    "catalog": "47b42433f5a85809a3aadd29c2c339da2c6ed728e4f7762df6b88bccb7874cf0",
}

# Exact assembler source facts (frozen PR1087, code/assemble.py member).
# Line numbers are positions in the retained member bytes.
SOURCE_FACTS = {
    206: "eta=beta=Q(1,10**24);s=min(c,(1-beta)*bb)-Q(1,10**27);assert 0<s<c and s<(1-beta)*bb",
    207: "chain=[Q(384599,10**10)];cuts=[]",
    210: "ceil=lambda x:-(-x.numerator//x.denominator);cut=max(ceil(36/gap**2),"
         "ceil(2*(4+512)/gap));assert cut*gap**2>=36 and cut*gap>=2*(4+512)",
    211: "cuts.append(dict(exponent=str(a),gap=str(gap),cutoff_log2=str(cut)));chain.append(a)",
    212: "q=chain[-1]*(1-2*eta);margin=(1-eta)*q/(1+q);ticks=margin*10**18;"
         "k=Q((ticks.numerator-1)//ticks.denominator,10**18)",
    214: "outer=A.assembly(chain[-1],bb,bridge,k,eta=eta,beta=beta);"
         "assert len(outer['strict_constraints'])==47 and all(v>0 for v in outer['strict_constraints'].values())",
    221: "conservative_k,conservative_cuts,conservative_outer,conservative_controls=outer_witness(conservative_b)",
    225: "native_moments=check_moment('complex',H,73,owner['live'],b,5120,False)",
    226: "k,cuts,outer,controls=outer_witness(b)",
}

# The twelve published membership margins and routing rooms (stock-margin-chain,
# PR #2972), recomputed here from the receipt's own recorded cutoffs.
PUBLISHED_MARGINS = {
    "bootstrap": {
        2: (2851485324488315, 4777557234646),
        3: (1015784602045963452130, 1701909188404384116),
        4: (361852943409004062662957360, 606271101174941147673746),
        5: (128902872114845343680818492656976, 215971951161791423920760764122),
        6: (45919069451025819974017753079498485812, 76935687018952933071573623067467882),
        7: (16357749867431357886201881301751734180286423,
            27406799379443943425326695785974298689751),
    },
    "conservative_bootstrap": {
        2: (2851485349075174, 4777557267681),
        3: (1015784614274199324771, 1701909205985694510),
        4: (361852949001065216196285881, 606271109508797681506267),
        5: (128902874547204377208495156774925, 215971954868265831114423996024),
        6: (45919070474352818766043006228287526563, 76935688602102847428409756325327327),
        7: (16357750287845003715345973449256621277195623,
            27406800037024020153662277717993715829414),
    },
}

STAGE_FIELDS = ("exponent", "gap", "cutoff_log2")


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL_COMPLEX_BRANCH_CUTOFF_LOCATION: " + message)


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tar_member(path, member):
    with tarfile.open(path) as archive:
        data = archive.extractfile(member).read()
    return data.decode("utf-8")


def floor_fraction(value):
    return value.numerator // value.denominator


def chain_and_cuts(bit_lower, complex_lower, beta=None, bit_driven=False):
    """The frozen assembler's own chain recurrence (code/assemble.py lines 205-212).

    bit_driven=True replaces the assembler's min() by the bit lower alone; used
    only as a negative control.
    """
    beta = Fraction(1, 10**24) if beta is None else beta
    if bit_driven:
        s = bit_lower - Fraction(1, 10**27)
    else:
        s = min(bit_lower, (1 - beta) * complex_lower) - Fraction(1, 10**27)
    chain = [Fraction(384599, 10**10)]
    cuts = []
    for _ in range(7):
        old = chain[-1]
        a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
        require(old < a < s < 1 - a and gap > 0, "chain invariant failed")
        ceil_int = lambda x: -(-x.numerator // x.denominator)
        cut = max(ceil_int(36 / gap**2), ceil_int(2 * (4 + 512) / gap))
        require(cut * gap**2 >= 36 and cut * gap >= 2 * (4 + 512),
                "assembler inline cutoff guard failed")
        cuts.append({"exponent": str(a), "gap": str(gap), "cutoff_log2": str(cut)})
        chain.append(a)
    q = chain[-1] * (1 - 2 * beta)
    margin = (1 - beta) * q / (1 + q)
    ticks = margin * 10**18
    k = Fraction((ticks.numerator - 1) // ticks.denominator, 10**18)
    return s, chain, cuts, k


def stage_headrooms(cuts):
    """H_j = floor(L_j * delta_j / 2) - 4 for the recorded stage triples."""
    heads = []
    for stage in cuts:
        L = int(stage["cutoff_log2"])
        delta = Fraction(stage["gap"])
        H = floor_fraction(Fraction(L) * delta / 2) - 4
        heads.append(int(H))
        # The stock audit's headroom identity: H is the largest integer log
        # bound the sufficient guard admits at this stage.
        require(2 * (H + 4) <= L * delta < 2 * (H + 5),
                f"headroom identity failed at cutoff {L}")
    return heads


def main():
    require(sha256_file(ASSEMBLY) == SHA["assembly"], "ASSEMBLY.json drift")
    require(sha256_file(RESULT) == SHA["result"], "stock-audit RESULT.json drift")
    require(sha256_file(TARBALL) == SHA["tarball"], "upstream1087.tar.gz drift")
    require(sha256_file(SELECTED) == SHA["selected"], "selected-result.json drift")
    require(sha256_file(CATALOG) == SHA["catalog"], "task-catalog drift")

    receipt = json.loads(ASSEMBLY.read_text())
    selected = json.loads(SELECTED.read_text())
    require(selected.get("decimal") == receipt["kappa_decimal"],
            "selected record disagrees with the receipt's kappa")
    stock = json.loads(RESULT.read_text())

    # --- Source facts: the location of the cutoff sequences in frozen source.
    member = load_tar_member(TARBALL, "code/assemble.py")
    lines = member.splitlines()
    for number, text in SOURCE_FACTS.items():
        require(lines[number - 1].strip() == text,
                f"source fact at line {number} does not match retained source")
    require(member.count("cuts.append") == 1,
            "more than one cuts.append site in the retained assembler")
    call_sites = [i + 1 for i, l in enumerate(lines)
                  if "outer_witness(" in l and "def outer_witness" not in l]
    require(call_sites == [221, 226],
            "outer_witness is not called exactly at the conservative and native sites")
    require(sum(1 for l in lines if "def outer_witness" in l) == 1,
            "more than one outer_witness definition")
    require("bootstrap=cuts" in member and "conservative_bootstrap=conservative_cuts" in member,
            "the output dict does not emit both sequences")
    require(member.count("check_moment('complex',H,73,") == 1
            and member.count("check_moment('conservative_complex',H,73,") == 1,
            "the m=73 supplier is not priced exactly once per branch")
    # No third sequence anywhere in the retained archive's Python sources.
    with tarfile.open(TARBALL) as archive:
        py_members = [m for m in archive.getmembers() if m.name.endswith(".py")]
        total_cut_sites = 0
        for m in py_members:
            text = archive.extractfile(m).read().decode("utf-8", "replace")
            total_cut_sites += text.count("cuts.append") + text.count("cutoff_log2")
    require(total_cut_sites == 2,
            "unexpected additional cutoff construction in retained sources")

    # --- Exact complex binding of both branch chains.
    b = Fraction(receipt["complex_lower"])
    c = Fraction(receipt["bit_lower"])
    conservative_b = Fraction(receipt["conservative_complex_lower"])
    beta = Fraction(1, 10**24)
    require((1 - beta) * b < c and (1 - beta) * conservative_b < c,
            "the complex side does not bind the assembler's min()")

    summary = {"branches": 2, "stages": 14, "controls_rejected": 0}
    for branch, lower, kappa_key in (
        ("bootstrap", b, "kappa"),
        ("conservative_bootstrap", conservative_b, "conservative_kappa"),
    ):
        recorded = receipt[branch]
        require(len(recorded) == 7, branch + ": expected seven recorded stages")
        require(receipt[kappa_key] is not None, branch + ": no recorded kappa")

        s, chain, cuts, k = chain_and_cuts(c, lower)
        require(s == (1 - beta) * lower - Fraction(1, 10**27),
                branch + ": saving is not the discounted complex lower")
        for i in range(7):
            for field in STAGE_FIELDS:
                require(recorded[i][field] == cuts[i][field],
                        f"{branch} stage {i+1} field {field} differs from the "
                        "recomputed assembler chain")
        require(k == Fraction(receipt[kappa_key]),
                branch + ": recomputed kappa differs from the recorded kappa")

        # The stock audit's recorded headrooms, recomputed from the receipt's
        # own triples rather than the audit's reconstruction.
        heads = stage_headrooms(cuts)
        audited = [int(st["stock_headroom_log2"])
                   for st in stock["branches"][branch]["stages"]]
        require(heads == audited,
                branch + ": recomputed headrooms differ from the audited ones")
        summary.setdefault(branch, {"stage1_headroom_log2": heads[0]})

        # --- Membership margins from this input path.
        L = [int(x["cutoff_log2"]) for x in cuts]
        for j in range(2, 8):
            margin = s * L[j - 1] - L[j - 2]
            room = (1 - s) * L[j - 2]
            published_margin, published_room = PUBLISHED_MARGINS[branch][j]
            require(floor_fraction(margin) == published_margin,
                    f"{branch} stage {j}: membership margin differs from the "
                    "published stock-margin-chain integer")
            require(floor_fraction(room) == published_room,
                    f"{branch} stage {j}: routing room differs from the "
                    "published stock-margin-chain integer")
            require(margin > 0,
                    f"{branch} stage {j}: membership margin not positive")

    # --- Controls (each must fail to reproduce / must be rejected).
    # 1. A bit-driven chain does not reproduce the recorded triples.
    s_bit, _, cuts_bit, _ = chain_and_cuts(c, b, bit_driven=True)
    require(not all(receipt["bootstrap"][i][f] == cuts_bit[i][f]
                    for i in range(7) for f in STAGE_FIELDS),
            "control 1: the bit-driven chain unexpectedly reproduced the receipt")
    summary["controls_rejected"] += 1

    # 2. Swapping the two branches' complex lowers does not reproduce either.
    _, _, cuts_swap, _ = chain_and_cuts(c, conservative_b)
    native_match = all(receipt["bootstrap"][i][f] == cuts_swap[i][f]
                       for i in range(7) for f in STAGE_FIELDS)
    _, _, cuts_swap2, _ = chain_and_cuts(c, b)
    cons_match = all(receipt["conservative_bootstrap"][i][f] == cuts_swap2[i][f]
                     for i in range(7) for f in STAGE_FIELDS)
    require(not (native_match or cons_match),
            "control 2: the branch-swapped chain unexpectedly reproduced a branch")
    summary["controls_rejected"] += 1

    # 3. A tampered recorded cutoff is rejected by the byte comparison.
    tampered = json.loads(ASSEMBLY.read_text())
    tampered["bootstrap"][3]["cutoff_log2"] = str(
        int(tampered["bootstrap"][3]["cutoff_log2"]) + 1)
    _, _, cuts_ref, _ = chain_and_cuts(c, b)
    require(not all(tampered["bootstrap"][i][f] == cuts_ref[i][f]
                    for i in range(7) for f in STAGE_FIELDS),
            "control 3: a tampered cutoff was not rejected")
    summary["controls_rejected"] += 1

    # 4. The stale-cutoff substitution must give a non-positive margin.
    s_native, _, _, _ = chain_and_cuts(c, b)
    L_native = [int(x["cutoff_log2"]) for x in cuts_ref]
    stale = s_native * L_native[5] - L_native[5]  # L_{j-1} in place of L_j, j=7
    require(stale <= 0,
            "control 4: the stale-cutoff substitution did not go non-positive")
    summary["controls_rejected"] += 1

    # 5. Cross-branch kappa: each chain reproduces exactly its own branch's
    #    recorded kappa and not the other branch's (the branches are distinct).
    _, _, _, k_con = chain_and_cuts(c, conservative_b)
    _, _, _, k_nat = chain_and_cuts(c, b)
    require(k_con != Fraction(receipt["kappa"])
            and k_nat != Fraction(receipt["conservative_kappa"]),
            "control 5: a cross-branch chain reproduced the other branch's kappa")
    summary["controls_rejected"] += 1

    # 6. A stock coefficient one bit above the stage-1 headroom fails the fit
    #    identity; the headroom itself passes (checked above via 2(H+4)<=...).
    H1 = int(stock["branches"]["bootstrap"]["stages"][0]["stock_headroom_log2"])
    require(H1 == 6562783,
            "control 6: the recorded stage-1 headroom is not the audited 6,562,783")
    L1 = int(receipt["bootstrap"][0]["cutoff_log2"])
    delta1 = Fraction(receipt["bootstrap"][0]["gap"])
    require(2 * (H1 + 4) <= L1 * delta1 < 2 * (H1 + 5),
            "control 6: the stage-1 headroom identity failed")
    summary["controls_rejected"] += 1

    # Every recorded coefficient stays null: the sigma obligation is open.
    for branch in ("bootstrap", "conservative_bootstrap"):
        require(all(st["actual_stock_coefficient"] is None
                    for st in stock["branches"][branch]["stages"]),
                branch + ": a stock coefficient is stored")

    summary["sigma_obligation"] = "uncomputed"
    summary["binding"] = receipt["binding"]
    print(json.dumps({"status": "PASS_COMPLEX_BRANCH_CUTOFF_LOCATION", **summary},
                     sort_keys=True))


if __name__ == "__main__":
    main()
