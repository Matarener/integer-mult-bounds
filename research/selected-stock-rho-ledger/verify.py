#!/usr/bin/env python3
"""Source-bound audit of the selected m=73 row-ledger terms behind `rho`.

Standard library only. Reads the pinned live inputs named in SOURCES.json
(and three members of the pinned PR1087 tarball, in memory); nothing from the
repository is imported or executed. Every proof-relevant constant is parsed
from source text, then checked by exact integer/rational arithmetic. Sixteen
mutation controls must each be rejected.

Mainzu, with substantial Claude Code assistance. Apache-2.0.
"""
import copy
import hashlib
import io
import json
import re
import sys
import tarfile
from fractions import Fraction as F
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
TARBALL = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
MEMBERS = {  # member -> sha256 (the assemble.py pin matches selected-bootstrap-stock-audit)
    "code/assemble.py": "15f6986a476bac76bcdc0bfcf51da115389b46f1950d2766b6822f757888b13a",
    "code/invoice_allcold.py": "71eb57514e28ced97251e0507105f654f59885ec4d40486a780bf166098858a8",
    "inputs/PR589-EXPECTED.json": "b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4",
}
MARKER = "PASS_SELECTED_STOCK_RHO_LEDGER"
DEFAULTS = dict(sp_half=36, bit_record="nine", rho_b=None, h1_override=None)


class Reject(Exception):
    pass


def need(cond, what):
    if not cond:
        raise Reject(what)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def flat(text):
    return " ".join(text.split())


def load_raw():
    sources = json.loads((PKG / "SOURCES.json").read_text(encoding="utf-8"))
    pins = {r["path"]: r["sha256"] for r in sources["files"] if r["usage"] == "input"}
    return pins, {p: (ROOT / p).read_bytes() for p in pins}


def authenticate(pins, raw):
    for path, digest in pins.items():
        need(sha(raw[path]) == digest, "pin mismatch: " + path)
    with tarfile.open(fileobj=io.BytesIO(raw[TARBALL])) as tar:
        names = {m.name.lstrip("./"): m for m in tar.getmembers() if m.isfile()}
        members = {k: tar.extractfile(names[k]).read() for k in MEMBERS}
    for k, digest in MEMBERS.items():
        need(sha(members[k]) == digest, "member mismatch: " + k)
    texts = {p: b.decode("utf-8") for p, b in raw.items() if p != TARBALL}
    texts.update({"tar:" + k: b.decode("utf-8") for k, b in members.items()})
    return texts


def ceil_log2(x):
    """Least integer g with 2**g >= x, for rational x > 0."""
    g = max(x.numerator.bit_length() - x.denominator.bit_length() - 1, 0)
    while F(2) ** g < x:
        g += 1
    return g


def analyse(t, p):
    n = [0]

    def ok(cond, what):
        need(cond, what)
        n[0] += 1

    asm, inv = t["tar:code/assemble.py"], t["tar:code/invoice_allcold.py"]

    # 1. The selected complex ledger as the frozen assembler states it.
    m = re.search(r"finite\['physical_row_coefficient'\]==2\*stock\.bit_length\(\)\+(\d+)\+(\d+)\+(\d+)", asm)
    ok(m is not None, "selected ledger formula")
    c_bit, c_leaf, c_prefix = map(int, m.groups())
    ok("finite['retained_row_coefficient']==20161" in asm, "retained row cap 20161")
    ok("'degree_gap':Q(10**6)-Q(51*20161,25)" in asm, "external p^(10^6) degree gap")
    gap = json.loads(t["research/community-frontier1094-audit/ASSEMBLY.json"])["outer"]["row_product_gap"]
    ok(F(gap) == F(10 ** 6) - F(51 * 20161, 25), "selected ASSEMBLY row_product_gap")

    # 2. Prefix term = twice the charged prefix payload.
    pay = re.search(r"invoice\['charged_prefix_bits'\]==(\d+)", asm)
    extra = re.search(r"invoice\['row_prefix_extra'\]==(\d+)", asm)
    ok(pay is not None and extra is not None, "prefix fields")
    ok("row=2*stock.bit_length()+9909+252+2*payload" in inv, "invoice ledger uses 2*payload")
    ok("charged_prefix_bits=payload" in inv and "row_prefix_extra=2*payload" in inv, "invoice prefix binding")
    ok(c_prefix == int(extra.group(1)) == 2 * int(pay.group(1)), "prefix term = 2*payload")

    # 3. B = bit length of |Sp(2h,2)| times the 14,826 physical families.
    h = p["sp_half"]
    order = 2 ** (h * h)
    for j in range(1, h + 1):
        order *= 2 ** (2 * j) - 1
    fam = re.search(r"data_and_owner_families=(\d+),local_helpers=R,private_centres=(\d+),coefficient_work=(\d+)", asm)
    ok(fam is not None, "physical stock identity")
    families = int(fam.group(1)) + 480 + int(fam.group(2)) + int(fam.group(3))
    ok("families=14826" in t["research/selected-stock-envelope-m73/README.md"] and families == 14826, "14826 families")
    b_bits = (order * families).bit_length()
    ok(b_bits == 2642, "B = 2642 bits")
    ledger = 2 * b_bits + c_bit + c_leaf + c_prefix
    ok(ledger == 16469 < 20161, "physical ledger 16469 < 20161")

    # 4. Origin of 9909 and 252: historical (halving degree, wire bits) families.
    pg = flat(t["notes/partial-gauge-assembly.tex"])
    ok("The coarse bit, ordinary leaf and complex families" in pg, "family sentence")
    pairs = re.search(r"\$\((\d+),(\d+)\),\((\d+),(\d+)\),\((\d+),(\d+)\)\$", pg)
    ok(pairs is not None, "family pairs")
    (hb, wb, hl, wl, hc, wc) = map(int, pairs.groups())
    ok(f"{hb}\\cdot{wb}+{hl}\\cdot{wl}+{hc}\\cdot{wc}={hb*wb+hl*wl+hc*wc}" in pg, "family sum as printed")
    ok(c_bit == hb * wb, "9909 = coarse-bit family degree x wire bits")
    ok(c_leaf == hl * wl, "252 = ordinary-leaf family degree x wire bits")
    tsc = flat(t["notes/three-stage-cover-assembly.tex"])
    ok("conservative previous bit and ordinary-leaf reserves" in tsc, "carried as conservative reserves")
    ok(f"58344+{c_bit}+{c_leaf}=68505" in tsc, "carried forward (three-stage)")
    ok(f"10284+{c_bit}+{c_leaf}=20445" in flat(t["notes/paired-cube-assembly.tex"]), "carried forward (paired-cube)")

    # 5. Units: external polynomial reserve degree vs internal q-adic borrowing.
    ok("width-dependent q-adic selectors are supplied by the separate internal borrowing proof, "
       "rather than multiplied into this external polynomial stock" in tsc, "selectors internal (three-stage)")
    ok("selector stock is borrowed and restored internally, not multiplied into this external "
       "polynomial reserve" in flat(t["notes/paired-cube-assembly.tex"]), "selectors internal (paired-cube)")
    sb = flat(t["notes/structured-bulk-assembly.tex"])
    ok("\\log_2Q\\le\\frac{51}{25}K\\log_2p" in sb, "row coefficient is a log2 Q / log2 p degree")
    ok("Both factors are reserved simultaneously" in sb, "bit-adapter factor reserved with complex factor")

    # 6. Selected BIT (PR589) ledger stacks the same constants (PR2084's reading).
    ok("bit=bit_record['nine']" in asm, "assembler consumes the nine-stage BIT record")
    rec = json.loads(t["tar:inputs/PR589-EXPECTED.json"])[p["bit_record"]]["bit"]
    ok(rec["maxchild"] == 42 and rec["physical"] == 28425, "PR589 m=64 producer identity")
    a9 = t["research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/code/assemble9.py"]
    f9 = re.search(r"row = DEPTH \* \(m \* m \+ 1\) \+ (\d+) \+ (\d+); assert row == (\d+)", a9)
    ok(f9 is not None, "PR510 assemble9 row formula")
    ok((int(f9.group(1)), int(f9.group(2))) == (c_bit, c_leaf), "BIT ledger reuses 9909 and 252")
    hd = rec["halving_depth"]
    ok(64 ** hd > 2 * rec["maxchild"] ** hd and 64 ** (hd - 1) <= 2 * rec["maxchild"] ** (hd - 1), "least halving depth")
    sigma_bit = hd * (64 * 64 + 1)
    ok(rec["row_coefficient"] == int(f9.group(3)) == sigma_bit + c_bit + c_leaf, "BIT row = HD(m^2+1)+9909+252")
    pr2084 = flat(t["research/selected-bit-parent-reserve/README.md"])
    ok(f"2*(64^2+1)={sigma_bit}" in pr2084, "PR2084 sigma_BIT")
    ok("needs **no additional externally supplied row factor**" in pr2084, "PR2084 hypothesis 4")

    # 7. Predecessor statements this package composes.
    cd = flat(t["research/selected-coarse-depth-stock/PROOF.md"])
    ok("one may take S_leaf=1" in cd, "coarse-depth: S_leaf=1 admissible under completed leaves")
    ok("sigma <= (43/26)*(1-s)*(A+B) + rho." in cd, "coarse-depth composition formula")
    ok("**A = 0** and **B = 2642**" in t["research/selected-stock-shape-a-zero/PROOF.md"], "PR3421 A=0, B=2642")
    m73 = t["research/selected-stock-envelope-m73/README.md"]
    ok("ledger=16469->15555" in m73 and "Under either conditional ledger reading" in m73, "#3113 ledger readings")
    implicit = 15555 - -(-43 * b_bits // 26)
    ok(implicit == c_bit + c_leaf + c_prefix == 11185, "#3113's 15555 reading carries 11185 as rho")

    # 8. Native stage 1 from the audited receipt.
    br = json.loads(t["research/selected-bootstrap-stock-audit/RESULT.json"])["branches"]["bootstrap"]
    s = F(br["common_saving"])
    st1 = br["stages"][0]
    ok(st1["stage"] in (1, "1") and st1["actual_stock_coefficient"] is None, "stage-1 record, coefficient null")
    h1 = int(st1["stock_headroom_log2"]) if p["h1_override"] is None else p["h1_override"]
    ok(0 < s < 1, "0 < s < 1")

    # 9. The two readings of rho, and why the ledger constant is not one.
    base = F(43, 26) * (1 - s) * b_bits  # complex part with A = 0
    # A candidate is (coefficient, shape): "w" multiplies w*(1+log2 e) as in H3;
    # "free" multiplies only ceil(log2 e), as every external-ledger degree does.
    rho_b, shape = (sigma_bit, "w") if p["rho_b"] is None else p["rho_b"]
    if shape == "w":
        ok(rho_b >= sigma_bit, "reading (b) rho must dominate the w-shaped BIT coefficient")
    else:
        ok(all(rho_b >= sigma_bit * w for w in range(1, 4097)), "w-free rho must dominate 8194*w at every w")
    ok(all(c_bit < sigma_bit * w for w in range(2, 4097)), "9909 < 8194*w for every w >= 2 probed")
    sigma_a, sigma_b = base, base + rho_b
    g_a, g_b = ceil_log2(8 * sigma_a), ceil_log2(8 * sigma_b)
    ok(g_a <= h1 and g_b <= h1, "sufficient guard ceil(log2(8 sigma)) <= H_1")

    # 10. Mode of the BIT callee inside selected complex nodes (open question 1).
    # The "reserved simultaneously" factor is a fixed-wire external one ...
    ok("W_b,W_c<2^{43}" in sb and "Nested bit adapters require \\[ Q=W_c^{D_c(e)}W_b^{D_b(e)}. \\]" in sb
       and "The sufficient stock is $p^{108000}$" in sb, "simultaneous factor is fixed-wire external")
    # ... while the selected adapters' callee gets no external row stock (PR2250) ...
    ca = flat(t["research/selected-complex-compact-adapters/PROOF.md"])
    ok("bind its tensor interpretation to the selected R480/T16 complex supplier" in ca, "PR2250 is selected-bound")
    ok("It may borrow internally; we grant it no external row stock or ancestor access." in ca,
       "PR2250: adapter callee has no external row stock")
    # ... and that callee, PR2234's selected BIT, borrows its own 4097w-per-level stock.
    rc = flat(t["research/selected-bit-recursive-closure/PROOF.md"])
    tau = re.search(r"tau=1-(\d+)/(\d+)\. Its review status remains separate", ca)
    a_ = re.search(r"a = (\d+)/(\d+) = ", rc)
    ok(tau is not None and a_ is not None and tau.groups() == a_.groups(), "PR2250's callee is PR2234's interchange")
    ok("The machine restores spectators and clears its work." in rc
       and "Choose the sufficient stock S=K(w)^D(e) from the original width e" in rc, "PR2234 completed contract")
    kb = re.search(r"log_q K < 4096w\+1 <=(\d+)w\. Borrow k=ceil\(log_q S\)=O\(w log e\) leading digits "
                   r"from the earlier chunk\. Eventually k<e/2\.", rc)
    ok(kb is not None and hd * int(kb.group(1)) == sigma_bit, "self-borrowed BIT stock is the 8194 coefficient")
    # The selected complex layer (PR2287): its only row stock is its own level divisor
    # L^D0(d); peeled axes and stopped leaves use the elementary C kernel; and its ordinary
    # callee is the completed interchange above. So S_leaf = 1, which is reading (a). The
    # root also reserves three H-bit compact fields, but they are not row stock.
    cl = flat(t["research/selected-complex-layer-closure/PROOF.md"])
    wm = re.search(r"The selected archive binds m=73, W=(\d+) live families", cl)
    ok(wm is not None and "Let Gamma=|O(73,2)| and L=W Gamma." in cl
       and "Gamma = 2^1296 product_(i=1)^36 (2^(2i)-1)," in cl, "PR2287 level divisor L = W*Gamma")
    l_bits = ceil_log2(F(int(wm.group(1)) * order))
    ok(l_bits == b_bits, "ceil(log2 L) = B")
    ok("q0=ceil(log2 L) D0(d)," in cl
       and "q0 whole chunks supply a preceding row range of size 2^(q0K)>=L^D0(d)." in cl
       and "For a child e', L^D0(e') divides U. A completed child restores its own row labels, so all "
           "subsequent siblings reuse the same stock." in cl, "complex row stock is L^D0(d)")
    ok("The next qF chunks supply two H-bit front compact fields; the last qB chunks supply one H-bit "
       "back field." in cl and "No compact-field bit enters this selector." in cl,
       "compact fields are reserved but are not row stock")
    ok("First process the delta leftmost selected axes individually and retain their chunks as completed "
       "spectators." in cl and "The leaves require only the elementary C kernel." in cl, "peeled axes, leaves elementary")
    ok("The bound uses an ordinary binary chunk interchange with cost O(V b^tau), complete spectators and "
       "restored work. PR2234 proposes that contract" in cl, "PR2287's ordinary callee is PR2234's contract")

    # 11. Every recorded stage, each with its branch's own s and its own headroom.
    branches = json.loads(t["research/selected-bootstrap-stock-audit/RESULT.json"])["branches"]
    rows = [(F(branches[k]["common_saving"]), int(st["cutoff_log2"]), F(st["gap"]), int(st["stock_headroom_log2"]),
             {g: F(v) for g, v in st["gaps"].items()})
            for k in ("bootstrap", "conservative_bootstrap") for st in branches[k]["stages"]]
    ok(len(rows) == 14 and all(0 < r[0] < 1 for r in rows), "fourteen stage records")
    ok(all(g == min(gs.values()) and gs["stock"] == 1 - s_ for s_, _, g, _, gs in rows), "gap = least gap; stock gap = 1-s")
    ok(all(cl_ >= 2 and cl_ * g * g >= 36 and 0 < g <= 1 - s_ for s_, cl_, g, _, _ in rows), "PR1965 premises, every stage")
    ok(all(h == (cl_ * g) // 2 - 4 for _, cl_, g, h, _ in rows), "headroom = floor(L*gap/2)-4, every stage")
    stage_g = [(ceil_log2(8 * F(43, 26) * (1 - s_) * b_bits), ceil_log2(8 * (F(43, 26) * (1 - s_) * b_bits + rho_b)), h)
               for s_, _, _, h, _ in rows]
    ok(all(ga <= h and gb <= h for ga, gb, h in stage_g), "both values pass every stage guard")
    h_min = min(h for _, _, h in stage_g)

    # 12. What the 9909 and 252 slots pay for (open question 3). In the selected layer they pay
    # for nothing: without them the complex row is 2B+1024. The BIT the adapters call is PR2234's
    # q-adic one: its level divisor has at least 4096*80-2 bits, since |GL_64(F_q)| >= q^4096/2
    # with q > 2^80. In the certificate's row convention (halving depth x bits per level) that
    # exceeds the cap even at w = 1, so the row ledger cannot be holding that BIT's stock; it is
    # borrowed inside the call instead.
    cap = int(re.search(r"finite\['retained_row_coefficient'\]==(\d+)", asm).group(1))
    lean = 2 * b_bits + c_prefix
    ok(lean < ledger < cap, "the 9909 and 252 slots are slack in the selected layer")
    qm = re.search(r"We fix one odd prime q>2\^(\d+) throughout;", rc)
    km = re.search(r"log_q K < (\d+)w\+1 <=", rc)
    ok(qm is not None and km is not None and int(km.group(1)) == 64 * 64, "PR2234 prime size and level exponent")
    qadic = hd * (int(km.group(1)) * int(qm.group(1)) - 2)
    ok(qadic > cap, "one q-adic BIT level exceeds the external row cap")
    return dict(checks=n[0], b=b_bits, ledger=ledger, c=(c_bit, c_leaf, c_prefix), fam=(hb, wb, hl, wl),
                bit_row=rec["row_coefficient"], sigma_bit=sigma_bit, implicit=implicit,
                sigma_a=sigma_a, sigma_b=sigma_b, g=(g_a, g_b), h1=h1, l_bits=l_bits, stages=len(rows), h_min=h_min, lean=lean, qadic=qadic, cap=cap)


def controls(pins, raw, texts):
    def text_edit(key, old, new):
        def run():
            t = dict(texts)
            need(old in t[key], "control precondition: " + old)
            t[key] = t[key].replace(old, new)
            analyse(t, DEFAULTS)
        return run

    def param(**kw):
        return lambda: analyse(texts, {**DEFAULTS, **kw})

    def tamper():
        r = copy.copy(raw)
        k = "notes/partial-gauge-assembly.tex"
        r[k] = r[k][:-1] + bytes([r[k][-1] ^ 1])
        authenticate(pins, r)

    asm, pg = "tar:code/assemble.py", "notes/partial-gauge-assembly.tex"
    cases = {
        "tampered_input_byte": tamper,
        "ledger_constant_9908": text_edit(asm, "+9909+252+1024", "+9908+252+1024"),
        "family_wire_bits_28": text_edit(pg, "(367,27)", "(367,28)"),
        "sp70_instead_of_sp72": param(sp_half=35),
        "prefix_extra_2048": text_edit(asm, "invoice['row_prefix_extra']==1024", "invoice['row_prefix_extra']==2048"),
        "eleven_stage_bit_record": param(bit_record="eleven"),
        "row_gap_tampered": text_edit("research/community-frontier1094-audit/ASSEMBLY.json",
                                      '"row_product_gap": "23971789/25"', '"row_product_gap": "23971790/25"'),
        "ledger_constant_as_rho": param(rho_b=(9909, "free")),
        "missing_s_leaf_premise": text_edit("research/selected-coarse-depth-stock/PROOF.md",
                                            "one may take S_leaf=1", "one may take S_leaf=2"),
        "guard_below_sigma": param(h1_override=15),
        "adapter_callee_external_stock": text_edit("research/selected-complex-compact-adapters/PROOF.md",
                                                   "it no external row stock", "it an external row stock"),
        "bit_stock_coefficient_4098": text_edit("research/selected-bit-recursive-closure/PROOF.md",
                                                "<=4097w.", "<=4098w."),
        "leaves_given_bit_reserve": text_edit("research/selected-complex-layer-closure/PROOF.md",
                                              "The leaves require only the", "The leaves require a BIT reserve and the"),
        "divisor_families_doubled": text_edit("research/selected-complex-layer-closure/PROOF.md",
                                              "W=14336 live families", "W=28672 live families"),
        "bit_prime_two_bits": text_edit("research/selected-bit-recursive-closure/PROOF.md",
                                        "q>2^80 throughout", "q>2^2 throughout"),
        "late_stage_headroom_tampered": text_edit("research/selected-bootstrap-stock-audit/RESULT.json",
                                                  '"stock_headroom_log2": 296674207198239164557594',
                                                  '"stock_headroom_log2": 296674207198239164557595'),
    }
    for name, run in cases.items():
        try:
            run()
        except Reject:
            continue
        raise SystemExit("CONTROL ACCEPTED (must reject): " + name)
    return len(cases)


def main():
    pins, raw = load_raw()
    texts = authenticate(pins, raw)
    r = analyse(texts, DEFAULTS)
    k = controls(pins, raw, texts)
    print(f"{MARKER} B={r['b']} ledger={r['ledger']} "
          f"{r['c'][0]}={r['fam'][0]}*{r['fam'][1]} {r['c'][1]}={r['fam'][2]}*{r['fam'][3]} "
          f"{r['c'][2]}=2*{r['c'][2] // 2} bit_row={r['bit_row']}={r['sigma_bit']}+{r['c'][0]}+{r['c'][1]} "
          f"implicit_rho_3113={r['implicit']} rho_a=0 sigma_a<={float(r['sigma_a']):.2f} "
          f"rho_b={r['sigma_bit']} sigma_b<={float(r['sigma_b']):.2f} L_bits={r['l_bits']} S_leaf=1 "
          f"guard={r['g'][0]},{r['g'][1]}<={r['h1']} stages={r['stages']} H_min={r['h_min']} "
          f"lean_row={r['lean']} qadic_bit_row>={r['qadic']}>{r['cap']} "
          f"controls={k} checks={r['checks']}")


if __name__ == "__main__":
    try:
        main()
    except Reject as exc:
        sys.exit("FAIL: " + str(exc))
