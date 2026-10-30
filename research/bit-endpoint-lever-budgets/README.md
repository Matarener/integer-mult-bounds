# The +10% centre-sharing route at c\* ≈ 0.0018433: complex need and bit-lever budgets on the actual histograms

**Planning bound and scoped proof (bit supplier). No construction, no κ claim, not a multiplication theorem.**
The selected record is unchanged: κ = 0.001672660197076918 (#1094), complex-bound.

- Track: bit (weight 20). Card: `bit-helper-contract`, scope **changed** to lever pricing (see [TASK.json](TASK.json)):
  the claim was filed on that card because its H2/K question is saturated; the consuming decision is
  `centre-path-sharing` (recursive interfaces).
- Base: canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (priority revision 6). Pins: [SOURCES.json](SOURCES.json).

## Statement

[centre-sharing-overhead-budget](../centre-sharing-overhead-budget/README.md) (PR1791) showed that two-call centre
sharing makes the complex side stop binding. A **+10%** whole-bound κ then needs **both** endpoints at
**c\* = 921658892752012102303/5·10²³ ≈ 0.0018433178** (1.0634× the selected bit endpoint). This package gives the
requirement map of that route on the actual histograms.

- **Complex side: PR1791's sufficient condition is too weak at c\*.** Its open question 1 says a complex saving of
  ≥ 1.33 units per call, together with a 649-unit bit mechanism, reaches +10%. The 1.33 figure is the complex need
  at the selected bit endpoint. With the bit side at c\*, the complex endpoint must itself reach c\*: κ(complex, bit) at
  (c\* − 10⁻²⁴, c\*) and even at (c\* − 10⁻²⁴, 3/1000) is below 1.1× selected (asserted). On the #1094 complex profile that is a net
  saving of **≥ 511 rank-1 children** (510 fails), **≈ 3.55 units per call** over 144 calls. Two-call centre sharing
  covers it with an additive rank-1 / rank-8 overhead of at most **4,079 rank-1 or 511 rank-8 children (≈ 28.3–28.4
  units per call)**, not the 30.5–30.8 PR1791 states for the selected bit endpoint.
- **Bit side: no admitted bit lever nets anything.** On the PR589 histogram (deficit 10,272, m = 64, W = 28,416,
  T = 32 replicas, 288 stage calls, nine rank-7 copies per call, halving depth HD = 2), c\* needs a net saving of
  **649 rank-1 children** (648 fails). Each bit lever in the table below (revision-3 catalogue) is changed one
  premise at a time on the actual histogram, with the surcharge recomputed from the child count. cst is the copy-rank
  sum per call (63 = 9 × 7). Every row below is a certified sign at c\* − 10⁻²⁴, c\* and c\* + 10⁻²⁴. The budgets
  are sharp integers in the stated model: the stated count passes and one less fails (one more, for budgets). The
  exceptions are marked: (c) is a necessary bound, (d) and (f) are sharp between an explicit hosting and the
  concavity bound, and the TEMPLATE and width-7 trimmed brackets have no boundary in range.

| Lever (one premise changed on the actual histogram) | Admitted today? | Net saving at c\* (rank-1 units) | Size that clears 649 |
|---|---|---:|---|
| (a) Halving depth 3 / 4 (idle cap 45 → 50 / 53) | admissible under the merged r740 elementary-cover row bound (invoice not redone) | **0 exactly** | none: the cap is slack |
| (a′) Width-8 re-hosting inside the actual idle windows | yes | **0 exactly** (record is optimal) | none |
| (b1) Rank-8 copy carriage, 9 copies per call (cst 63 → 72) | allowed by format-limits' copy cap (copies up to rank 8) | **−2,577.6** | none (makes things worse) |
| (b2) Fewer rank-7 copies | no (new decoder contract) | +2,008.8 for one fewer per call | threshold **93 copies** record-wide (92 fails); a uniform decoder change removes 288 (one per call) |
| (b3) Bit centre path shared by two calls (cst 31.5) | no (unconstructed) | **+9,039.5** | passes with overhead ≤ **8,391 rank-1 / 1,203 rank-7 / 201 rank-42** children (29.1–29.3 units per call) |
| (c) Second unpaid coordinate on F families, pure removal (one unit per family, no reshaping) | no (coverage-law change) | ≤ F | **F ≥ 649** of 28,416 (2.28%), necessary in this model |
| (d) Pure helper deletion, most favorable (8 rank-1 climbs each), optimal width-8 re-hosting | no (see PR1250 below) | +658.5 at d = 40 | **d = 40 per call** (39 fails for every hosting) |
| (d) Helper deletion, PR1043's measured delta | no | +169.8 (explicit hosting), ≤ +170.4 (concavity bound) | none: the model runs out of rank-7 climbs at d = 19 (d = 10 if the 9 copies are kept) |
| (f) Width-7 helper conversion, #1023's **window-free** placement, rank-1 child removed per helper | no (#1128: needs a changed prefix) | +656.0 at k = 71 (window-free) | window-free only: k = 71 per call (70 fails at the concavity bound). **Under replica-local windows no k ≤ 74 clears** (PR1736) |
| (f) Width-7 conversion, largest local child trimmed per helper (window-free) | no | +580.6 at k = 74 (explicit hosting), ≤ +581.2 (concavity bound) | none: fails at k = 74, when all 666 empty 7-slots per replica are used |
| (e) Ideal in-window local shapes (single rank-7 data climbs, single rank-8 helper climbs) | no (no such word) | +3,647.6 in all 288 calls | **52 of 288 calls** (51 fails) |

(e) uses PR1334's ideal in-window shapes (rank-7 data climbs, rank-8 helper climbs). PR1334's cruder "rank-8 children (window h = 8)" row, which ignores the 7-level data climb, and its
"rank-16 children (beyond the window)" row are not priced here. A same-loop float estimate, not certified, puts them
at about 50 and 34 calls; the rank-16 row needs longer windows, hence a different recipe.

**Conclusion.** No admitted bit lever nets anything at c\*. The admitted levers are the halving-depth cap raise,
width-8 re-hosting and rank-8 copy carriage. Their nets are 0, 0 and −2,578, so any combination of them also fails.
Every lever that clears 649 changes the word, the decoder or the coverage law. The stated sizes are: one fewer
rank-7 copy per call (93 of the 2,592 copies record-wide), 40 pure helper deletions per call (9.3% of the 430
helpers; a stage-relaxed pass), the ideal local shapes in 52 calls, ≥ 649 doubly-unpaid families, or
bit-side two-call sharing within ≈ 29.1 units of overhead per call. Partial width-7 conversion (f) clears only in
#1023's window-free relaxation (k = 71); our merged PR1736 shows that under replica-local windows on the frozen
recipe no partial conversion k ≤ 74 reaches c\* (certified maximum 0.0018099 at k = 74), so width-7 clears only by
the full all-439 conversion (#1023, window-feasible per PR1736), which needs a changed prefix (#1128).

**Consequence for `centre-path-sharing`.** At c\* the route needs a complex saving of ≥ 511 net rank-1 units
(≈ 3.55 per call), not PR1791's 1.33, plus one of the bit-side mechanisms above. Rows b3 and f both have
constructed complex-side analogues: the PR1708/PR1748 two-call centre phase (scalar-macro level, not admitted) and
the PR601/PR593/PR569 width-7 helpers (per #1023). Each is blocked on the bit side, by the analogue of PR1748's
ownership/sink blocker and by #1128's changed prefix respectively. Bit-side sharing (b3) has about 14× the needed
saving, with an overhead budget of ≈ 29.1–29.3 paid-mass units per call. Rows b2, c, d and e (and f
only in the window-free relaxation) also clear 649, each with a new decoder, coverage law or word of the stated size. With the complex side at
c\* + 10⁻²⁴ and the bit side at c\*, κ is still ≥ 1.1× selected (asserted). The complex overhead figure is an
additive rank-1 / rank-8 budget in PR1791's treatment. Mixed ranks allow more added mass: PR1888's mixed-rank
maxima reach 30.87 units per call at the selected bit endpoint, with rank-51 children. PR3075 charges the named
k = 2 costs (per call: 4 ADD, 4 scratch CLEAR and 4 precision rank-1 children) inside this budget, and reports that eligibility and demand coupling, not
the named costs, are the blocker. Without a bit-side mechanism of one of the stated sizes, the card's stop rule
holds for the catalogued lever set.

## Why the admitted levers give exactly zero (proof)

**Windows.** The nine-stage recipe (`global_k.py`, PR #463/#510 lineage, K = 4 pairs) creates nine idle events per
replica: ranks 14, 28, 42 for s = 1, 3, 5, then 7, 7, 7 for s = 2, 4, 6, then 42, 28, 14 (and one rank-0 event) at
s = 8. Each event covers 2v = 222 coordinates. Per replica that gives windows {7: 666, 14: 444, 28: 444, 42: 444}.
`verify.py` derives this from the recipe rules and checks that the record's idle part (profile minus 288 shipped
words) equals T × {2: 435, 4: 444, 6: 444, 7: 666, 42: 9}, the remainder left after hosting 9 × 439 width-8 residuals
per replica (439 = 430 helpers + 9 retained totals).

**(a) The cap is slack.** HD = 2 caps children at 45, since 2r² < 64² ⇔ r ≤ 45. HD = 3 and 4 raise the cap to 50
and 53. But every idle child is a window remainder, at most the largest window 7(2K − 2) = 42, and every local
child has rank ≤ 7. No idle child can span two consecutive windows of the same pair: the windows are delimited by
the recipe's bridges, each of which needs both pairs at a common level, reading the source pair's side-0
coordinates and writing its side-1 coordinates there, so every coordinate of the source pair must be materialized
at that level. The
record already keeps pair 1's 14 and 7 windows (21 < 45) and pair 2's 28 and 7 windows (35 < 45) as separate
children at HD 2, so the split is structural, not a cap effect; pair 3's 42 + 7 = 49 likewise cannot merge under
the HD-3 cap of 50. So the record's max child is 42 < 45, and raising the halving depth admits no histogram the
fixed windows can produce. Its net saving is exactly 0. Longer windows need a different recipe. In
[bit589-recipe-floor](../bit589-recipe-floor/README.md) (PR1487)'s whole class of nine-stage recipes, that package
reports the longest advance as 2(K − 1) = 6 levels, i.e. a window of 42, so the cap is slack there too. In
particular, PR1334's cap-50/53 columns and its halving-depth-4 escape (145 ≥ 138) cannot be reached by any
recipe in that class.

**(a′) Width-8 re-hosting cannot help.** A rank-r window holds at most ⌊r/8⌋ width-8 helpers. 8 divides no window
rank, so every window keeps exactly one nonzero remainder child, and the child count (hence the surcharge) is fixed.
Write φ(x) = x(m/x)^a, which is concave. A window with base remainder ρ = r − 8⌊r/8⌋ and u unused slots costs
φ(ρ + 8u), so its extra cost g_ρ(u) = φ(ρ + 8u) − φ(ρ) is concave in u with g_ρ(0) = 0. Hence
g_ρ(u) ≥ u·g_ρ(cap)/cap. Each replica has exactly 3,996 − 3,951 = 45 unused slots. So the total extra cost is
at least 45·min over ρ of g_ρ(cap)/cap.

At c\* the per-slot costs are certified as 7.94284 (rank-42 window) < 7.94625 (rank 28) < 7.95184 (rank 14) rank-1
units. So the minimum is 45·g_2(5)/5, which the record attains by leaving 9 rank-42 windows empty. The record's
hosting therefore minimizes the bill over all width-8 hostings of the actual windows, even with the per-stage window
constraints relaxed. The same bound holds record-wide (1,440 unused slots), so pooling across replicas does not
help either. This re-certifies, at c\*, what our merged
[bit589-width-packing](../bit589-width-packing/README.md) (#1023) proved at the selected endpoint.

**(b1) Copy carriage.** cst is the sum of the copy ranks (63), entering the deficit D = T(2Kv − L·cst). With whole
copies, rank-8 carriage of the nine copies raises cst to 72 and the paid mass by 2,592. That increases the bill.
PR1334's receipt instead keeps cst = 63 as 63/8 rank-8 copies per call. That mass-preserving reshaping nets only
about +4.45 rank-1 units here (same-loop review check, not shipped) and fails.

**(c) One unit of rank mass is worth at most one rank-1 child.** Trimming a rank-r child to r − 1 saves
φ(r) − φ(r − 1) < φ(1), certified for r = 2..42 at c\*. Removing a rank-1 child also removes its surcharge. So F
doubly-unpaid families save at most F rank-1 children, and F ≥ 649 is necessary, when each unpaid coordinate is a
pure removal of one unit of mass. Reshaping or merges that accompany the unpaid coordinate are outside this model. JosieElliston's PR1808
(`plane-port-copy-budgets`) priced this lever earlier at the +10% target as an all-families ideal-packing
relaxation; (c) instead gives a necessary pure-removal count on the actual histogram, and the two do not conflict.

**(d) Deletion bounds.** For d deletions per call, the 45 + 9d unused slots per replica are priced two ways:
- from below, by the concavity bound (all at the rank-42 per-slot cost, fractional);
- from above, by an explicit hosting (⌊(45 + 9d)/5⌋ empty rank-42 windows plus one partly used rank-42 window).

In the most favorable pure-deletion model each deleted helper removes 8 rank-1 climbs, the most a mass-8 removal can
save. There the lower bound fails at d = 39 and the explicit hosting passes at d = 40. So 40 is sharp in the
stage-relaxed slot model, and d ≤ 39 fails for every pure-deletion word. Deltas that also merge other climbs belong
to lever (e); the [bit-deletion-ladder](../bit-deletion-ladder/README.md) (PR2465) notes that they can beat RANK1
at equal mass. PR1043's measured TEMPLATE delta consumes one rank-7 climb per deletion; the word's 19 rank-7 climbs
include its 9 rank-7 copies, so with the copies kept that model is exhausted at d = 10, and even consuming all 19 it
nets at most +170.4 (concavity bound; +169.8 with the explicit hosting).

**(f) Width-7 conversion.** [bit589-width-packing](../bit589-width-packing/README.md) (#1023) prices helpers of
width 7 in a **window-free** placement: the 9k width-7 residuals per replica fill 9k of the 666 empty 7-slots exactly,
and the freed width-8 slack goes to emptied rank-42 windows. Its bracket removes one unit per converted helper either
as a rank-1 child (optimistic) or by trimming the largest local child (pessimistic). Here the slack is hosted as in
(d). In the optimistic bracket k = 71 per call passes with the explicit hosting and k = 70 fails at the concavity
bound. The pessimistic bracket fails at k = 74, when every empty 7-slot is used; beyond that, this placement does not
apply (#1023's all-439 slot-exact optimum is a different placement). Within the slot model, mightyOil's #1281 (step-1
subadditivity lemma) shows an optimum puts each width-7 role alone in a 7-slot, so the k = 70 fail holds for every
slot-model placement and +656.0 is the slot-model optimum. But the slot model ignores stage windows: our merged
[bit589-width7-windows-seed72](../bit589-width7-windows-seed72/README.md) (PR1736, head `b4fd72163234`) proves
that each capacity-7 idle child admits exactly one stage, so at most 3k of the 9k residuals per replica fit, and its
certified window-respecting optimum stays below c\* for every k ≤ 74 (maximum 0.0018099 at k = 74). So under
replica-local windows on the frozen recipe no partial width-7 conversion clears; cross-replica owner maps and other
recipes are open. The lever is not admitted either:
[bit-width-seven-boundary](../bit-width-seven-boundary/README.md) (#1128, Ali Romman, head `df29b159239b`) shows that the selected PR589 word
cannot obtain width-7 helpers by replacing its cleanup alone; a changed prefix is needed.

Linearity makes every budget sharp. f(a) = (1/(mW)) Σ n_r r (m/r)^a + c_s m^a with c_s = 32mN/(10¹⁶W) is affine in
the counts, so each one-parameter family is monotone and the boundary is a single integer.

## Second method

[independent.py](independent.py) rebuilds every boundary histogram from the pinned PR589 and #1094 records with its
own code, requires byte-identical histograms, and recomputes all **75 signs**: 19 bit rows, 4 complex budget rows and
the 2 complex need rows, each at c\* − 10⁻²⁴, c\* and c\* + 10⁻²⁴. It uses the separate interval arithmetic of our merged
[bit-revision3-levers-seed03/levers.py](../bit-revision3-levers-seed03/levers.py) (PR1334): ln by atanh prime chains,
exp by Taylor with a remainder bound, outward dyadic rounding. It also re-checks the re-hosting order and the
trimming lemma. The primary [verify.py](verify.py) uses the D/E-diagnostic engine (PR1293, Navinor). The two
methods agree on every sign. Only the histogram code and the arithmetic are independent: the lever definitions, the
hosting model and the boundary integers (read from RESULT.json) are shared with verify.py.

## Reproduce

From the repository root (standard library and `git`; under a minute, about 55 s for `verify.py` on a shared host):

```sh
python3 -I -B research/bit-endpoint-lever-budgets/verify.py && python3 -I -B research/bit-endpoint-lever-budgets/independent.py
```

Expected output:

```text
PASS_BIT_ENDPOINT_LEVER_BUDGETS need_rank1=649 admitted_levers_max_net=0 copies_sharp=93 deletions_per_call=RANK1:40/TEMPLATE:None width7_windowfree_per_call=71 ideal_shape_calls=52 complex_need_rank1=511 no_new_kappa
PASS_BIT_ENDPOINT_LEVER_BUDGETS_INDEPENDENT signs=75 at c*-1e-24, c* and c*+1e-24 (levers.py interval arithmetic)
```

`verify.py` regenerates [RESULT.json](RESULT.json) and requires byte equality (`--write` rewrites it). It refuses
to run under `-O`.

**Controls in `verify.py`:**
- its bill equals the pinned engine's on the record;
- the selected bit endpoint is accepted and its next grid point rejected;
- the selected κ is recomputed;
- c\* is the least grid point with κ ≥ 1.1× selected (and c\* − 10⁻²⁴ is not);
- the complex endpoint c\* is necessary: κ(c\* − 10⁻²⁴, c\*) and κ(c\* − 10⁻²⁴, 3/1000) are below the target;
- the admitted-lever maximum net (0) is computed from rows (a), (a′) and (b1), and (b1) is asserted negative;
- the record fails at c\*;
- the 649/648 rank-1 and 16 rank-42 requirements are re-derived.

**Negative controls that must fail:** every "one less" boundary row (648 rank-1, 92 copies, 39 deletions,
70 width-7 helpers, 51 reshaped calls, 510 complex rank-1) and every "one more" overhead row. Fail rows are checked at
c\* − 10⁻²⁴ as well, where monotonicity does not make the check automatic. [test_package.py](test_package.py) checks
that tampering is rejected by the independent method:
- off-by-one counts, including one consistent shift (requirement 648 with its rows rebuilt) that only the sign
  arithmetic can catch;
- a flipped verdict;
- an edited histogram;
- an edited complex verdict.

```sh
python3 -I -B -m unittest discover -s research/bit-endpoint-lever-budgets -p test_package.py
```

## Scope, inherited assumptions and unresolved obligations

- **Inherited:**
  - the fixed-histogram bill and surcharge law of the selected record;
  - the coverage identity D = T(2Kv − L·cst) at fixed m, W;
  - PR1791's endpoint model, with the complex side at 3/1000 under two-call sharing;
  - the PR589 H1–H5, all-size/compiler, precision and analytic obligations, unchanged.
- **Scope of each row:**
  - (a) and (a′) hold for the PR589 nine-stage windows and width-8 helpers. (a′) also holds with stage windows
    relaxed. No banks are used.
  - (b2), (b3), (c), (d), (e) and (f) are pricing passes for hypothetical words or decoders.
    - (d)'s d = 40 pass is in the stage-relaxed slot model; its d ≤ 39 fail holds for every hosting.
    - (e) is the in-window ideal relaxation of PR1334, applied call by call.
    - (f) is #1023's window-free slot model; with #1281's lemma its k = 70 fail holds for every slot-model
      placement, but under replica-local windows no k ≤ 74 clears at all (PR1736).
- **Unpaid obligations of every passing row:** the word or decoder itself, then:
  - the dirty-input endpoint and restoration;
  - hosting under the real stage windows;
  - the row-coefficient invoice;
  - the recomputed surcharge (included here);
  - the native precision/tape;
  - admission.

  For (b3) add the bit analogue of PR1748's ownership/sink blocker. Overhead that changes the windows, the coverage
  law or the outer recipe is outside the model.
- Run on Linux with CPython 3.14.4. The registered replay
  (`python3.12 scripts/research_package.py --package research/bit-endpoint-lever-budgets`) also passed with CPython
  3.12.15: `PASS_REGISTERED_RESEARCH_PACKAGE`.

## Open next questions

1. **Can the bit centre path be shared by two calls within ≈ 29 units of overhead per call?**
   - *Why it matters:* it has the largest margin of the clearing rows (about 14× the need) and a constructed
     complex-side analogue (PR1708/PR1748, scalar-macro level, not admitted).
     The complex half must then deliver ≥ 511 net rank-1 units at c\*, i.e. keep its additive rank-1/rank-8 overhead
     within ≈ 28.3 units per call.
   - *First step:* write the bit analogue of PR1748's two-call reverse phase for the nine rank-7 copies of one
     replica, and price its restoration/hosting children.
   - *Blocked by:* no bit sharing word exists, and PR1748's ownership/sink blocker has no bit analogue yet.
     [r439-copy-path-sharing-barrier](../r439-copy-path-sharing-barrier/README.md) (section T) records that the
     nine retained totals read pairwise-disjoint source sets, which a sharing word must respect.
2. **Is there a decoder contract with eight retained totals (cst ≤ 56)?**
   - *Why it matters:* one fewer copy per call nets ≈ 2,009 units, 3.1× the requirement.
   - *First step:* test whether one of the nine retained totals of the v = 111 word can be recomputed instead of
     copied, and price the extra climbs.
   - *Blocked by:* a replacement contract for the decoder's copied totals (the `centre-path-sharing` card's
     scope-change trigger); r439-copy-path-sharing-barrier section T shows the totals' source sets are disjoint.
3. **Which bit word reaches the 52-call reshaping, the 40-deletion size or a window-feasible width-7 conversion?**
   - *Why it matters:* these are the non-sharing alternatives.
   - *First step:* measure the best per-call delta of PR1043-style deletions combined with climb merges, or test the
     six width-7 survivors of #1128 with a B/C rewrite (prefix through scatter fixed); the other 433 need a changed
     prefix, and partial conversion must also beat PR1736's window bound.
   - *Blocked by:* PR1250 found no further single deletion beyond PR1043 within arbitrary source XOR masks on the
     fixed R439 word (sole survivor helper 470); it does not exclude simultaneous deletions. Width-7 helpers need a
     changed prefix.

## Credit and provenance

- **Requirement, endpoint and sharp-removal method:** rtyu193-rgb, `centre-sharing-overhead-budget` (PR1791, head
  `00d05a648985`).
- **Moment enclosures:** Navinor, `selected-suppliers-de-diagnostic` (PR1293, head `85a361233431`).
- **Bootstrap/outer formulas:** Wronskode, `frontier1042-invoice-audit-seed81` (PR #1112).
- **Independent arithmetic:** our merged `bit-revision3-levers-seed03` (PR1334, head `5ad74a4a04d1`).
- **Re-hosting optimality at the selected endpoint, the slot model and the width-7 placement/bracket:** our merged
  `bit589-width-packing` (#1023, head `babca68167d8`); exact partial width-7 slot optima by mightyOil (#1281). Window-respecting width-7 bound: our merged
  `bit589-width7-windows-seed72` (PR1736, head `b4fd72163234`).
- **Width-7 admission boundary:** Ali Romman, `bit-width-seven-boundary` (#1128, head `df29b159239b`).
- **Bit second-unpaid-coordinate pricing at +10% (all-families relaxation, predecessor of row c):** JosieElliston,
  `plane-port-copy-budgets` (PR1808, head `b3d9b9813e0f`).
- **Deletion models:** our merged `bit-deletion-ladder` (PR2465, head `9494fc4e2ecd`), from Ali Romman's PR1043 delta
  (head `e309e17f83f5`); single-deletion scope from PR1250 (bbMisk, head `67667b11049e`).
- **Recipe class:** ianlibanio, `bit589-recipe-floor` (PR1487, head `cfd97ca1e9d3`).
- **Halving-depth admission:** the merged r740 elementary-cover row bound,
  `research/e8-bit-carrier-skeleton/code/hub/r740-hosted-eleven/code/row_bound.py` (as cited by PR1334).
- **Complex overhead context:** RossRichardson, `centre-sharing-mixed-overhead` (PR1888, head `9c0fd1d20d33`);
  navinor / Aaron Wang, `centre-shared-kcall-charged-seed615415` (PR3075, head `378b8e47fc01`); the two-call
  mechanism PR1708 (1337isnot1337) / PR1748 (ToikY; PR1748 head `ea14f191752c`); `r439-copy-path-sharing-barrier`.
- **Bit supplier:** DreamingOfClouds (PR589, head `a5afc8c6169e`) and eumemic (PR555, head `65a6bc19f820`), with the
  PR510/PR463/PR442 template and hosting lineage.
- **Selected construction:** Rohan Arun (#1094).

All are loaded unchanged as pinned Git blobs. Predecessor code is reused without modification.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). The
question was scoped, and the code and prose written, in one session of an automated research loop. Before submission
it is checked only by AI review passes in the same loop; there is no independent human review. Apache-2.0.
