# complex-halving-degree-invoice: halving degree of the selected complex invoice under the inherited degree-t ledger

**Scoped finite statement, conditional on inherited hypotheses; an optimistic opening only.
No new κ, no supplier, no frontier change.**

## Answer in three lines

- **Question.** Every complex ceiling screen caps child ranks (idle and paid) at 51, from the
  halving guard 73^t > 2R^t at halving degree t = 2. Does the selected #1094 finite
  invoice force t = 2, and what is a larger t worth?
- **Bound that does not depend on the invoice.** R = 73 never meets the guard, so every
  child rank, paid or idle, is ≤ 72 for every t. Its idle-cap component (the selected
  word's paid children held fixed, only idle mass repacked) is worth at most
  **+2.76469%** in Colkitt's ideal relaxation, whatever the row contract is. The same
  guard also caps the paid ranks; that rank-shape lever above 51 is not priced here.
- **Under the inherited degree-t ledger (H1–H4 in [PROOF.md](PROOF.md)).** If only the
  outer bridge binds (reading B, favoured by the inherited bridge text), t_max = 181
  (152 with a 512·t prefix) and every child rank up to 72 is admissible (from t = 51). If
  the retained row 20161 binds (reading A, the fallback), t_max = 3 and every child rank
  is ≤ 57 (+0.875558% from idle repacking under the integer-degree ledger).

## Statement

At t = 2 the selected invoice charges the row coefficient 2·2642 + 9909 + 252 + 1024 =
16469, where S = 2642 is its stock bits. Under H1 the charge at halving degree t is

Row(t, S) = t·S + 9909 + 252 + prefix(t),

and under H1–H4 the halving degree is limited only by this row contract:

| Row contract | prefix(t) | t_max | Largest admissible R | Rank-56 idle bin¹ | R = 72 |
|---|---|---|---|---|---|
| B, bridge-only: Row < 490196 | 1024 (fixed) | **181** (row 489387) | **72** | admissible | yes (t ≥ 51) |
| B | 512·t | **152** (row 489569) | **72** | admissible | yes |
| A, retained-binding: Row < 20161 | 1024 | **3** (row 19111) | **57** | admissible | no |
| A | 512·t | **3** (row 19623) | **57** | admissible | no |

¹ 56 = 8 + 16 + 32, a merge of the nine-stage route's smaller idle bins. Open #3836
(Matarener) reports that bridge-based nine-stage schedules force the 16/32/48 alphabet,
so this bin is guard-admissible here but not realized in that schedule class.

Reading B keeps the bridge reserve 10^6 and the factor 51/25 fixed and re-chooses the
retained coefficient up to ⌊(25·10^6 − 1)/51⌋ = 490196, where the bridge gap is 4/25 > 0.

**Why source favours B.** The lineage bridge text that derives 20161 calls it an
overcharge: "The complex child maximum below m/2 gives halving degree1, while
log2 W<5208<10000 … A=10000+9909+252=20161 … Increasing these finite overcharges changes
constants and the all-size bridge, not the selected exponent saving"
(`research/five-stage-gen4-banks/inputs/complex/retained/FINITE_BRIDGE.txt`, section 4;
lineage evidence, outside the selected manifest). The 10000 slot is exactly where
t·S + prefix(t) must fit under A, and it was sized at halving degree 1. The
selected-manifest lineage assembler `research/direct-delivery504-global/code/assemble.py:29`
certifies the bridge at `row=max(20161, bit row, physical row)`, treating 20161 as a
floor. Counter-evidence for A: the selected assembler also asserts the bit row
`<20161` (`assemble.py:204`), the invoice emits `retained_row_coefficient=20161`
(`invoice_allcold.py:307`), and the lineage invoices keep a strict `row<20161`; under B
these stay satisfied because K ≥ 20161. The outer engine consumes the bridge only as
the positivity slack `row_product_gap=bridge['rows']['degree_gap']`
(`research/contextual-provider-pooling/engines/outer.py:45`), not as a κ margin. The
lineage calls 20161 a "retained … allowance"
(`research/contextual-provider-pooling/docs/PRIOR-TN27-README.md:21`). An earlier assembly
in the same bridge lineage charges row 20445 at halving degree 4 against its own reserve
70000 (`notes/paired-cube-assembly.tex`), so reserves and allowances are chosen per
assembly. And 51/25 is derived independently of t
(`notes/structured-bulk-assembly.tex`). Reading A keeps this replay's pinned constant.
Reading A admits t = 3 for any prefix(3) ≤ 2073, so its t_max = 3 holds for every prefix
form with that property (a superlinear form such as 256·t² would give 2).

A child rank R is admissible exactly when t_min(R) ≤ t_max, where t_min(R) is the least
t with 73^t > 2R^t: t_min(51) = 2, t_min(57) = 3, t_min(58) = 4, t_min(71) = 25,
t_min(72) = 51. For general stock, (R, S) is admissible exactly when
S ≤ ⌊(cap − 1 − 10161 − prefix(t))/t⌋ with t = t_min(R); RESULT.json tabulates this for
R ∈ {48, 51, 52, 56, 57, 58, 64, 68, 71, 72}.

**Ideal ceilings.** Colkitt's packing relaxation of the selected local word, with idle
ranks allowed up to R:

| R | t_min | a_ceiling (certified to a 10^−15 grid cell) | κ ≤ a/(1+a) | κ cap with the bit endpoint | gain over R = 51 |
|---|---|---|---|---|---|
| 51 | 2 | 0.001690054109089 (published value, reproduced) | 0.001687202645325402 | same | — |
| 57 | 3 | 0.001704851516268 | 0.001701949944324806 | same | +0.875558% |
| 72 | 51 | 0.001736778936705 | 0.001733767765368969 | 0.001730427469823603 | +2.76469% |

a/(1+a) is an upper bound in all cases. For R ≥ 71 it is no longer the binding one: the
selected bit endpoint b = 0.001733427039589844234749 caps any conversion at
b/(1+b) = 0.001730427469823603. The full table for R = 51..72 is in RESULT.json and
increases strictly with R. **R = 71 (t_min = 25) is the least rank whose ceiling cell lies
above b**; the ceiling at R = 70 is 0.001732866531911.

**Conditional what-if under reading A.** Reading A's R ≤ 57 uses the integer halving
degree as the multiplier of S (H1). `research/selected-coarse-depth-stock` prices the same
depth component more sharply (43/26 instead of 2 at R = 48; sharp asymptotic coefficient
1/log2(73/R)) and calls this "not an adopted complete row bound". Repricing the t·S term
at the sharp coefficient, other terms kept, would admit R ≤ 59 under A with the fixed
prefix (row 19786; +1.1501%, ceiling 0.001709491591784) and R ≤ 58 with the prefix scaled
likewise (row 19666; +1.0138%). So reading A's cap depends on the ledger; it is not an
upper bound on every repricing.

What this decides:

- R = 51 is not forced by the invoice under either reading (given H1–H4).
- Under B (or C, below), R = 72 is admissible. The ideal lever is +2.76469%, and from
  R = 71 this relaxation no longer forces the complex side to bind.
- Under A, the integer-degree ledger gives +0.875558% (R ≤ 57), or up to +1.1501% with the
  conditional sharper depth pricing. The complex ceiling stays below b.
- The guard caps every child rank, not only idle ones. The rank-shape screens of open
  #3701 and #3811 stop at paid cap s = 51 because of this same t = 2 guard; under H1–H4
  the cap becomes 57 (A) or 72 (B). In their relaxation (all local and idle mass at rank
  s) a same-loop AI review computation (not asserted by verify.py) gives 0.013675 at s = 51, 0.019823 at s = 57 and an
  uninformative 0.3556 at s = 72, where physical hosting, not the guard, binds. That
  paid-rank lever is not priced or claimed here (open question 5); the +2.76469% above is
  only the idle-cap component.

## What is new compared with predecessors

- **philippeVV**, Discussion #2278 ([comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/2278#discussioncomment-18960261),
  2026-10-15, local-only and unreviewed), stated that the guard is a convention, that
  "the retained bridge degree 10^6 already admits t ≤ 181", and that the effect on this
  word's ceiling is "≤ +2.8%". This package confirms his ≤ +2.8% bound exactly
  (+2.76469%) under every reading, and his t ≤ 181 under reading B with a fixed prefix
  (152 with a 512·t prefix). The t = 2 ledger terms were traced concurrently (below);
  new here are the t-dependence of the ledger bound to the selected assembler and invoice
  bytes; reading A (t_max = 3) and the source evidence for B; the exact (R, S) region; certified ceilings at every
  R = 51..72; and the bit-endpoint crossing at R = 71.
- **Gonzalo-Mier**, `research/kappa010-rank-cap-floor`, open question 3, asks whether
  depth six fits the row invoice. For the complex invoice: halving degree 6 gives row
  6·2642 + 11185 = 27037, which fits under B (< 490196) and fails under A (≥ 20161).
  Every degree 4 ≤ t ≤ 152 fits under B, including the 17 that their complex rank-70 row
  needs. The bit invoice is not evaluated here.
- **Douglas Colkitt**, `research/complex-local-word-ceiling`: the relaxation and its
  rational enclosure primitives are reused unmodified, as a cross-check. Its guard check
  (`ceiling.py:111`) is not called for R > 51.
- **petalas**, open #3701/#3729/#3754/#3805/#3811: ceilings and integer packings for caps
  up to the guard cap 51. This package prices only the idle cap past 51.
- **Concurrent (open PRs):** #3768 (jwr404) records the same degree-gap arithmetic
  (23971789/25, 141461/5, 20249.8) that this package re-asserts as precedent. #3667
  (Mainzu) traces 9909, 252 and 1024 as w-free degrees of the fixed external reserve
  (support for H4) and claims, conditionally, that the 9909/252 slots are slack (lean row
  6308 at t = 2). If that were adopted, reading A would admit t = 7 with the fixed prefix
  (row 19518, R ≤ 66) or t = 6 with the 512·t prefix (row 18924, R ≤ 65), still below the
  R = 71 bit crossing; verify.py asserts these (`lean_row_what_if_A_3667`). #3670 and
  #3766 (jwr404) record the t = 2 rows 16469 and 15555; #3766's "two selected row
  readings" are row values, not this package's contract readings A/B.

## Reproduce

From the repository root, with the standard library only. Tested locally with Python
3.14 only. `VERIFY.json` targets 3.12, which was not available locally, so the runner's
3.12 replay was not run here.

```sh
python3 -I -B research/complex-halving-degree-invoice/verify.py
```

Expected output, in under 10 s:

```
PASS_COMPLEX_HALVING_DEGREE_INVOICE_SCOPED {'A_retained/fixed': 3, 'A_retained/per_level': 3, 'B_bridge/fixed': 181, 'B_bridge/per_level': 152} {'51': '0.001690054109089', '57': '0.001704851516268', '72': '0.001736778936705'} 11 controls
```

The verifier recomputes everything and requires byte equality with
[RESULT.json](RESULT.json). `--write` regenerates the file. The six checks and the 11
negative controls (each must fail with its stated assertion message; each did) are
listed in [PROOF.md](PROOF.md#verifier-checks-and-negative-controls).

Outside the verifier: `-O` exits non-zero (the assertions are the checks), an unknown
argument is rejected, and a one-digit edit of RESULT.json fails the byte comparison.
The invoice binds only bit lengths, so a change that keeps every bit length (for example
`conservative_pervertex_used + 1`) is not detected.

## Scope, inherited assumptions and unresolved obligations

These hypotheses are inherited (see PROOF.md). They are evidenced from source but not
proved here:

- **H1.** The finite-cover transfer can be instantiated at halving degree t with ledger
  t·S + 10161 + prefix(t). The lineage's notes do this at t = 4 and t = 24 with the same
  9909 + 252, and #3421 (VictorLiwentao) proves the per-level stock shape A = 0 with
  B_bits = 2642 for the m = 73 divisor, so S is the per-level allowance. The
  degree-genericity of the written transfer proof is not re-proved.
- **H2.** prefix(t) is fixed (1024) or 512·t; source does not settle which.
- **H3.** Reading B (bridge-only, favoured by source) or reading A (retained-binding).
  A third reading, C, is recorded but not used for any number: the reserve exponent is
  itself chosen per assembly (70000, 108000, 160000 in the notes; 10^6 here), and then
  the row invoice gives no finite cap.
- **H4.** The other finite checks do not depend on t. The square in router and literal
  is the W² exchange count of a W-role permutation, kept at degree 24; C0 = 32·m_c·B² is
  kept at degree 4; the bootstrap cutoff max(⌈36/gap²⌉, ⌈2(4+512)/gap⌉) is
  self-adjusting.

The following costs are unknown, not zero:

- physical hosting of idle children of rank > 48 (#3805 leaves 49–51 open);
- the per-level divisor and stock for higher-rank children: #3421 binds A = 0 and
  B_bits = 2642 for the selected m = 73 divisor, and the leaf constant ρ stays unbound
  (#3113; selected-coarse-depth-stock open question 1). Coarse depth itself is not an
  extra cost: H1 already charges it, conservatively, as t·S;
- native admission, including the hard-coded t = 2 guards at
  `complex-sw4-frame8/code/assemble.py:175` and `:191` and `ceiling.py:111`;
- any change to the staged544 template.

The ceilings are relaxations: they bound what repacking this local word could reach,
and they are not achievable values. This package admits nothing and does not change the
selected frontier.

## Open next questions

1. **Does the retained row coefficient 20161 bind, or only the bridge (reading A versus
   B or C)?** Source favours B (above): the derivation of 20161 as a degree-1 overcharge
   is known (FINITE_BRIDGE section 4), and lineage assemblers certify the bridge at
   max(20161, rows). What remains is whether the selected transfer proof inherits the
   section-4 "overcharge" clause, or the invoices' strict `row<20161` is a contract.
   Blocker: a contract decision.
2. **Is `row_prefix_extra` fixed or proportional to t?** It changes t_max under B from
   181 to 152, but not the R = 72 conclusion. Weak evidence for 512·t: the selected
   assembler names the bit side's 512 charge `charged_two_level_coefficient_bits`
   (`assemble.py:204`). First step: trace `2*payload` to the PR582 plain-joint-prefix
   construction.
3. **Can idle children of rank 71 or 72 be hosted, and what do ρ and the per-level
   divisor cost there?** This is where the bit side could start to bind. A sharper depth
   coefficient would be a row saving (it could raise reading A's cap to 58–59), not a
   cost. Blocked by #3805 (physical hosting) and ρ (#3113 / #3421).
4. **Bit-side analogue.** Does the bit invoice (m = 64) admit the halving degrees that
   the kappa010 bit rows need (t = 15 for rank 61)? First step: bind the bit row ledger
   the same way.
5. **Paid caps 52–72.** The same guard limits paid child ranks. What do the rank-shape
   screens of #3701/#3811 (open) give at paid caps s = 52..72, with physical hosting
   (#3805) and stock/depth repricing charged? First step: rerun their screens with the
   cap lifted to 57 (A) and to 72 (B).

## Sources and credit

- Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6. Exact Git
  blobs and SHA256 values of every input are in [SOURCES.json](SOURCES.json).
- The selected invoice is the tar member `candidate/strict/global/audit/PREFIX-AND-INVOICE.json`
  of the #1094 replay (rohanarun), SHA256 `212cf4ee3b16081bf66f300fa18b4070d25c17210c21c78c2967892c91870d12`.
- The ledger formula and contracts are in the selected assembler
  `research/complex-sw4-frame8/code/` (PR741 by chafreaky; inherited authors credited
  in its PROVENANCE.md): `invoice_allcold.py:263,271-283,297` and
  `assemble.py:159,173,175,191,210,213`. The selected record's source chain includes
  PR1087 by jeremykothe2.
- Precedents: `notes/paired-cube-assembly.tex`, `notes/three-stage-cover-assembly.tex`,
  `notes/three-stage-cover-rows.tex`, `notes/structured-bulk-assembly.tex`, all by
  icekylinx. DaysSky's closed PR375 (halving degree two, raised from one) is the earliest
  explicit statement of the degree-t ledger (row term t·log2 W, recursion depth
  t·⌈log2 n⌉) that H1 relies on. `FINITE_BRIDGE.txt` (five-stage-gen4-banks lineage) and
  `research/direct-delivery504-global` are cited as lineage evidence for reading B.
- Predecessors:
  - philippeVV: the halving-guard note in Discussion #2278.
  - Gonzalo-Mier: kappa010-rank-cap-floor, open question 3.
  - Sricharan Vagvala (@theon199): selected-coarse-depth-stock.
  - VictorLiwentao: #3421, selected-stock-shape-a-zero.
  - Douglas Colkitt: complex-local-word-ceiling.
  - Dugongue: contextual-provider-pooling (PR563; `outer.py` and the PRIOR-TN27 README,
    from the PR552 lineage), integrated by Douglas Colkitt.
  - DaysSky: closed PR375 (degree-t ledger generalization).
  - navinor: #3113.
  - petalas: #3701/#3729/#3754/#3805/#3811.
  - Concurrent (open PRs): jwr404 (#3768, #3670, #3766), Mainzu (#3667), Matarener
    (#3836).

No predecessor file was modified.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5). Claude chose the method, wrote verify.py and drafted this
README and PROOF.md. Reviewed by seven independent AI review passes (two rounds) in the same
loop; no human has reviewed it. Apache-2.0.
