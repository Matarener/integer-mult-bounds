# Staged544 width-unit prices: the exact staging break-even in the fixed-T360 ideal

**Scoped exact result about the clock-free fixed-bin ideal. It makes no kappa
claim, is not a construction and is not a complete multiplication theorem.**

## Statement

The model is PR3815's fixed-inventory ideal of the staged544 T360 template
(PR3734). Per owner replica there are 9 calls of 408 helpers with hosted widths
`{4:26,5:2,6:18,7:53,8:96,9:213}`, idle bins `{8:672,16:448,32:448,48:448}`,
local profile `{1:2440,2:725,3:224,4:102,5:20,8:8}` and 896 live rank-73
families. Packings may be fractional and any clock is allowed. Details are in
[PROOF.md](PROOF.md). A "width unit" is one helper-call (one helper in one of
the nine calls) moved one width step; prices are in `F` units per replica at
`a_hi = 0.001730578437266246818741`, the upper end of the staged544 ceiling
bracket `[0.001730578437266246818740, ...741]` (this bracket reproduces PR3815).

1. **Exact width-unit prices, within basis ranges.** PR3815's basis dual
   `(pi_4..pi_9, mu)`, evaluated exactly at `a_hi`, gives:

   | move | price per width unit | exact for up to (helper-calls per replica) |
   |---|---|---|
   | 9->8, 8->7, 7->6, 6->5 | `(h(48)-h(3)-5h(5))/20` = 0.987736781185353068089966 | 28 / 30 / 28 / 28 |
   | 5->4 | `h(1)-h(0)` = 1 | 18 |
   | 4->3 | `h(5)-h(3)-1` = 0.991791369039984911721564 | 324/5 = 64.8 |

   The 6..9 closed form is PR3682's 8->7 width shadow (zxv, `price.py`); the
   new content is that the same price holds for every step on 6..9 (the dual
   is affine on widths 5..9), the exact 5->4 and 4->3 prices and all the
   ranges. The 4->3 price is exact because the column `[3,9^5]` in a 48-bin
   is tight under the tight extension of `pi_1..pi_3`, which is dual feasible
   on all 318,840 width-1..9 patterns; `verify.py` checks the four-column
   move and its range exactly. Outside a range the price is a lower bound
   for every further unit (convexity of the LP value).
2. **Staging screens (exact arithmetic, per width unit).** Under the observed
   conservation (item 4), a literal staging move must also change the local
   profile. Its net change in `F` is (local saving) minus (price):
   - **Documented signature.** All three observed staging units (644 and 660
     in PR3605, 544 in PR3734) change the local profile by `{1:+3,2:+1,3:-2}`
     per unit (PR3605 PROOF: `3H1 + H2 - 2H3`), saving
     0.991001081580029037511288. Gain: **+0.003264300394675969421322** for
     6..9, **-0.008998918419970962488711** for 5->4 and
     **-0.000790287459955874210276** for 4->3. All three observed units are 8->7 moves; for the other widths the screen assumes the same signature.
     So with this signature only width-6..9 staging pays, and 5->4 and 4->3
     staging lose; a candidate's own local saving should be priced with (*).
   - **Hypothetical rank-1 deletion** (single-child compensation, saving
     `h(1) = 1`, the most any single-child decrement `r -> r-1` saves). Gain at
     most **0.012263218814646931910033** for 6..9, **0** for 5->4 (in any
     amount) and **0.008208630960015088278435** for 4->3. No staging with this
     compensation is known, and its realization cost is not priced; these are
     upper references, not leads. A local rewrite that also merges children
     can save more than 1 and is priced by the local term of (*) below.
   - The gap between the two is 0.008998918419970962488711 per unit. Whether
     any literal staging achieves a smaller gap is open.
3. **General screen (*).** By weak duality with the same `(pi, mu)`, any
   changed inventory `s'` over widths 1..9 with these bins and any local
   profile `n'` satisfies

   `F(a_hi) >= 9 sum n'_r h(r) + 9 sum pi_w s'_w + sum mu_c B_c - 896 h(73)`   (*)

   This is the screen PR3815's open question 1 suggests; here it is extended
   to widths 1..9. The staged544 inventory gives `F(a_hi) >= 5.28e-20 > 0`.
   `mu` (`mu_48 = 47.679502755263063473958379`) gives subgradient bin prices
   only: no bin-row ranging was done.
4. **Per-call conservation (observed).** Local paid rank minus hosted helper
   width is 1856 per call on both pinned (inventory, local) pairs, PR3682 and
   staged544, so the total paid rank is `9*1856 + sum c B_c = 896*73 - 320`
   per replica. PR3605 states the same conservation for its staging ("the
   local rank mass falls by 2, exactly matching the owned-width decrease").
   The PR3734 finite and PR3815 clock-fill profiles share one pair, so their
   total of 23,431,680 at `T = 360` is implied, not independent. The
   conservation is observed, not derived. Where it holds, a width reduction
   with an unchanged local profile is not realizable, which is why item 2
   prices staging with a local change.
5. **Monotone-price lemma (free reductions).** With `pi_1 = pi_2 = pi_3 =
   pi_4`, the helper duals `pi_w` are nonincreasing in `w`, nonpositive and still dual feasible
   on all width-1..9 patterns. This follows from PR3815's 2,551-pattern dual
   and `pi_4 <= -3` by a two-line slack lemma (PROOF section 3); `verify.py`
   also checks it on all 318,840 patterns. Hence a width reduction (to any
   width `>= 1`, or unhosting) with an unchanged local profile keeps the
   ideal ceiling below `a_hi = 0.001730578437266246818741`. Under item 4 such a move is not realizable, so this is a
   consistency statement about the model, not a staging closure.
6. **PR3682 -> staged544 split at `a_hi`.** `F` is additively separable in
   inventory and local profile at fixed `a`, so the 2x2 interaction is
   identically 0. Width part (one 8->7 per call, inside the range 30):
   `+8.889631030668177612809695088162` = 9 x the price. Local part:
   `-8.919009734220261337601597266358`. Net
   `-0.029378703552083724791902178195`, i.e. the documented-signature gain
   0.003264300394675969421322 per call. Either change alone breaks the
   conservation: width-only moves the ideal root to about 0.0016821,
   local-only to about 0.0017788 (HiGHS, float).

To first order, `dF/da ~ 184132` at the ceiling (floating point). One more
width-6..9 staging in all nine calls with the documented signature would raise
the ideal ceiling by about 1.6e-7 (9 x 0.003264 / 184132); a hypothetical
rank-1 deletion would give about 6.0e-7. For comparison, the staged544
inventory's ideal gain over PR3682 is about 1.6e-7 (realized on a literal clock
by PR3815 and PR3802); PR3734's own finite fill realized about 2.9e-8.

## Decision informed

This informs expansion-gate point 4 for the staged-entrance family (#3606), the
engine of #3605 and #3734, and partly answers PR3815's open question 1. The
family is tracked in #3606; it is not a revision-6 lead.

- With the documented staging signature, only width-6..9 staging pays
  (+0.003264 per width unit); 5->4 and 4->3 staging lose. The signature was
  observed only on 8->7 units; for other widths it is an assumption.
- By weak duality (*), `k` width-6..9 units with the documented signature, in
  any number and mix and also outside the ranges, leave
  `F(a_hi) >= 5.28e-20 - k x 0.003264300394675969421322`. To first order this
  is at most about 1.6e-7 of ideal ceiling per fully staged helper (nine
  units), before clock and admission costs.
- A candidate staging is decided by one exact inequality: its local saving per
  width unit must exceed the price in item 1 (within the ranges).
- Even a hypothetical rank-1-deletion compensation cannot make 5->4 staging
  pay.
- The gap between the documented signature and a hypothetical rank-1 deletion
  is 0.008999 per unit; whether a literal staging can narrow it is open.
- Free width reduction is not a lever (item 5).

## Reproduce

```
python3.12 -B scripts/research_package.py --package research/staged544-width-lever-screen
```

The verifier is standard-library only and runs in about 6 s. It can also be run
directly as `python3 -B research/staged544-width-lever-screen/verify.py`. The
expected last line is `PASS_STAGED544_WIDTH_LEVER_SCREEN`, preceded by a JSON
report with every exact number above. The output was identical under Python 3.12.15
and 3.14.4.

**Negative controls (each must fail; the verifier asserts they do):**

- `pi_9 + 1e-30` makes the dual infeasible.
- Raising the tight `pi_3` by 1e-30 makes the pattern `[3,9^5]` infeasible
  (the tight extension, and so the exact 4->3 price, is tight).
- A non-monotone extension is rejected by the same `monotone` check the lemma
  uses.
- One 8->9 widening per call drops the bound to `<= 0` (widening is priced as a
  gain).
- A +1 change to the PR3734 histogram fails the same `paid_rank_ok` check the
  profiles pass.

One consistency check (not a mutation): the dual bound at `a_lo` is not
positive, as implied by `F_upper(a_lo) < 0` and weak duality. The `pi_9`
control and this check reproduce PR3815's two controls.

**Second, independent method (floating point):** `crosscheck_highs.py` used
Python 3.14.4, numpy 2.5.4 and scipy 1.18.1 HiGHS. It generates patterns as
integer partitions, uses explicit reduction columns instead of dual
monotonicity, and bisects the root. Its recorded output is
`evidence/HIGHS.json`:

- Fixed staged544 root 0.0017305784372662612.
- Free reductions over 318,840 patterns: 0.0017305784372661503. This is not
  higher; the 1.1e-16 difference is float noise.
- PR3682 ideal root 0.0017304188997660508.
- Single-unit prices 0.9877367811860 (8->7), 1.0 (5->4) and 0.9917913690369
  (4->3), agreeing with the exact values to about 3e-12.
- The `stage` variant (`s544_stage_w1`) charges each move `h(2)-h(1)`. That
  is the superseded task-card model, which adds local rank; it is not the
  staging accounting used here and is kept only as recorded output.

It is not part of the registered replay.

## What is new

Prior art, credited: PR3815 (ChaloupeMusic) solves the basis dual
`(pi_4..pi_9, mu)` in `ceiling_certificate.py` and suggests pricing changed
inventories with it (open question 1). PR3682's `price.py` (zxv) has the
closed-form 8->7 width shadow `(h(48)-h(3)-5h(5))/20` and the "staged net =
local delta + width shadow" calibration of PR3605. PR3605's PROOF
(RossRichardson) derives the per-helper staging delta `3H1 + H2 - 2H3` and
states that local rank mass falls with the owned width. The async505 inventory
wall, PR3630 and PR3638 priced other inventories with fixed widths.

New here:

- reading PR3815's `a_hi` dual (which PR3815 already solves exactly at
  `a_hi`) as width-unit prices: the common 6..9 price (affine dual on widths
  5..9), `5->4 = 1` and the exact `4->3 = h(5)-h(3)-1`;
- the basis ranges (18 to 30, and 324/5 for 4->3);
- the extension of the dual to widths 1..9 (cheapest and tight), with the slack
  lemma;
- the two staging screens per width (documented signature and rank-1
  reference), including that 5->4 and 4->3 staging lose under the documented
  signature;
- the per-call conservation 1856 checked on both pinned pairs;
- the exact PR3682 -> staged544 split with the per-width break-even.

## Sources

The base is canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The
inputs are numbers transcribed into `verify.py` and `CERTIFICATE.json` from
unmerged PR heads. These heads are not reachable from main, so they are recorded
here by sha256 and not as `SOURCES.json` pins. The verifier cannot byte-check
them. This is a stated gap.

| PR | head | file | sha256 |
|---|---|---|---|
| #3734 (dataisfire) | `fa041037a3374eaa08feeca0b26a5d6893194147` | `research/staged544-producer-return/PROOF.md` (inventory, local profile) | `be5fa8e381da957d52d02b154e2420f4459d7c8b30e23e82e245c11c978e3b62` |
| #3734 | same | `research/staged544-producer-return/inputs/PROFILE.json` | `06b4e2abe8d56b49bad3bdc8f8504082404b40609d548fa8de2618eb7373fd48` |
| #3815 (ChaloupeMusic) | `77ffbf287b6ca198b4a31e3835db3bae60718b93` | `research/staged544-clock-ceiling/ceiling_certificate.py` (model, bins, bracket) | `2276f1c5d341db63dcf511f6398733b1efbe9d09e2e9aa86b50d7a160a0f7d03` |
| #3815 | same | `research/staged544-clock-ceiling/inputs/PROFILE.json` | `9686df0d8e710c2e94aef3887f4bf130a05b64215faeae702cccb59e95a469d5` |
| #3682 (zxv) | `431e6c6023ef352c41696469de7fb614cd4ded8c` | `research/staged-donor-release/PROOF.md` (inventory, local profile) | `89ce2b0aa2dcf84ebcab04aedc451420815bc48af25c69998594910e9976a31b` |
| #3682 | same | `research/staged-donor-release/LEAD1-PRICE.json` (finite profile) | `217dfc6b0c243d5387f50b23d0a5a389754df702ea1d810aea46a6f3d81617bc` |

## Scope, inherited assumptions and unresolved obligations

- **Model.** This is the clock-free fractional ideal with fixed idle bins and
  PR3815's payment rule (one rank-`l` child per remainder). Template, stock and
  clock effects are out of scope. PR3815 traced PR3734's shortfall from its
  ideal to the clock.
- **Per-call conservation.** Observed on two pinned (inventory, local) pairs
  and stated by PR3605 for its staging; not derived. The non-realizability of
  free reductions depends on it.
- **Staging signature.** The documented signature is what the three observed
  staging units use; all three are 8->7 moves, so for other widths it is an
  assumption. It is not proved to be forced. The rank-1-deletion
  reference has no known realization.
- **Admission costs not priced.** All admission costs of a changed inventory are
  unknown and are not zero. These include physical stock, coverage law and
  template checks, literal staging identities and clock feasibility.
- **Ranges.** Exact prices hold within the stated ranges. Outside them they are
  lower bounds. `mu` is a subgradient (lower-bound) bin price only.
- **Floating-point values.** `dF/da`, the ceiling conversions and the HiGHS
  values are floating point.
- **No kappa.** No kappa, frontier or selected-result change is claimed.

## Open next questions

- **Is the staging signature `{1:+3,2:+1,3:-2}` forced?** A literal width-6..9
  staging with a smaller gap to a rank-1 deletion would gain up to 0.008999 per
  width unit more. The PR3682 -> staged544 local delta equals the signature,
  which suggests PR3682's delayed donor release (`{1:-2,2:-2,3:+2}`, worth
  about 0.0066 per call) survives in PR3734. First step: check in PR3734's
  frames whether that release survives, or whether an analogous release applies
  to helper 544's donors; then price the result with (*).
- **Does the per-call conservation (local paid rank minus hosted width = 1856)
  hold for every literal construction of this template?** First step: derive it
  from the owner and frame accounting in PR3734's `owner_audit.py`, or find a
  construction that violates it.
- **What do bin-count changes offer?** `mu` gives subgradient bin prices. First
  step: write a candidate template's bin counts and evaluate (*), re-solving the
  LP outside the (unknown) bin ranges. New bin ranks are constrained by
  concurrent PR3836 (Matarener, unmerged), which reports, by a census within
  its class, that the idle alphabet is forced within bridge-based nine-stage
  schedules; changing bin counts stays open.

## Credit

The model, bins, payment rule, basis and basis dual are from PR3815
(ChaloupeMusic, head `77ffbf28`). The staged544 inventory and local profile are
from PR3734 (dataisfire, head `fa041037`). The predecessor inventory, the
closed-form 8->7 width shadow and the staged-net calibration are from PR3682
(zxv, head `431e6c60`, `price.py`). The staged-entrance mechanism, the
per-helper staging delta `3H1 + H2 - 2H3` and the rank-mass/width statement are
from PR3605 (RossRichardson, head `3efbb5de`, PROOF lines 146-164), with lineage
through PR3795/PR3802 (hexapode). The width-price method follows
`research/experiment-log/negative-searches/async505-inventory-wall` (Rohan
Arun), PR3630 (RossRichardson) and PR3638 (zxv). PR3836 (Matarener) is cited
for the idle alphabet. No predecessor code is copied. `verify.py`'s
enclosures, enumeration, knapsack check and LP algebra are new.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from
Claude (Anthropic, Claude Opus 5.5). Reviewed by four AI review passes in the
same loop (reproducibility, mathematical audit, provenance, referee), then one
revision, a re-verification round by two of them (mathematical audit, referee)
and a second, text-level revision; no human or formal-kernel verification is
claimed.
Apache-2.0.
