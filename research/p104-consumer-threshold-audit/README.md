# Conditional audit of PR3620's P104 all-pair deletion threshold

Independent verification. No kappa, supplier or frontier change.

**Result.** Take PR3609's changed full dual and the named paired-chain coverage
law (both inherited; the law is optimistic and unrealised). Under those
conditions, PR3620's threshold is correct: deleting at most **425** rank units
per dual call fails for every pair count `p >= 1` and every finite number of
fully paid banks, at `a = κ` and hence at every `a >= κ`, including every
admissible `a > a_req`. Deleting **426** rank-one children in every dual call
passes, at `p = 6..10` for
PR3620's test value `a = 1/596` and at `p = 6..11` for `a = a_req = κ/(1-κ)`.
The rejection is proved twice with exact arithmetic. The passing points (426
at `p = 7`, 428 at `p = 4`, `a = 1/596`) are checked by both methods; the
passing ranges and slack comparisons use method A plus convexity. The coverage
grant is favourable and nothing is counted twice. The excess depends only on
the total deletion over the `p` dual calls, so 426 is the least *uniform*
per-call deletion. Uneven calls can pass with a smaller average: at `p = 7` a
total of `7·425+3 = 2978` passes at both `a_req` and `1/596` (2977 fails).
Some call must still delete more than 425.

Which saving to test: under the repository's retained limiting conversion
`κ = a/(1+a)` ([bottleneck brief](../../docs/research/bottleneck-brief.md);
PR3620's "outer ratio"), an improvement needs `a > a_req = κ/(1-κ) ≈ 0.00167546`.
`E` increases in `a`, so the sharp slack ceilings are the values at `a_req`
(suprema, not attained). PR3620's `1/596 > a_req` gives slightly smaller
figures. Values at `a = κ` are looser and suit rejection proofs only, as in the
all-pair package; they are in [RESULT.json](RESULT.json). All slack figures are
optimistic ceilings under the named law (necessary conditions), not realised
allowances, are for 426 rank-one deletions in every dual call, and are
truncated toward zero.

- **Cost proportional to the number of dual calls** (for example a deletion
  network in every dual call): seven pairs is best, at 0.710094 per dual call
  (`a_req`) or 0.651010 (`1/596`). Per call of either kind (`2p+1` calls),
  seven pairs is also best: 0.331377 and 0.303804.
- **Purely fixed extra cost**: the total slack is largest at eight pairs,
  5.524500 (`a_req`) or 5.040108 (`1/596`).
- **Mixed cost `c0 + c1·p`**: it passes iff `c0 + c1·p < -E_426(p,a)` for some
  `p`, so a large fixed part can make eight pairs the only passing count (at
  `a_req`, `5 + 0.05p` passes only at `p = 8`; at `1/596`, `4 + 0.1p` passes
  only at `p = 8`).

PR3620's slack sentences ("four additional normalized cost units still pass;
five already fail" and "leaves less than 4.558 units") are correct as written:
PR3620 scopes them to seven pairs and `a = 1/596`, the binding pair count for
per-call costs. At seven pairs the ceiling at `a_req` is 4.970660. The 426
threshold and the qualitative stop decision are unchanged. [REVIEW.md](REVIEW.md)
marks every step valid, confirmed, or valid as scoped and clarified (3.11,
3.12). No step is invalid.

## Object and conditions

- Audited claim: [PR #3620](https://github.com/CrocSwap/integer-mult-bounds/pull/3620)
  (Clear1nsight), head `5a4354c669dc05a9368f58321b1951ebac36d80d`,
  `research/p104-caller-feasibility/consumer/PROOF.md` sections 1 and 3
  (lines 1-7, 18-165).
- Changed dual D: [PR #3609](https://github.com/CrocSwap/integer-mult-bounds/pull/3609)
  (Clear1nsight), head `13f974dae4af66027afb01f3ab42df9e830c2e90`,
  `research/p104-inplace-entrance/RECEIPT.json`. It is vendored byte for byte as
  [inputs/PR3609_RECEIPT.json](inputs/PR3609_RECEIPT.json) (git blob
  `6faa5157f2274a5bb85da4d5e44b1b1ff39eb32c`, sha256
  `6d06db043316af94377653a8e3fbfa1dcd686e20760af943b08e7060896ccf8b`). The pin
  is outside this repository's pin forms, so `verify.py` checks both digests.
  PR3609 is open and unreviewed.
- Forward profile F and the per-call progress cap: `research/p104-consumer-budget-audit/RESULT.json`
  on main (PR2744), sha256 `08705a91912d937a782696cd3e0905a9a5b63e60ce7daf9ff9618968f32eaae5`.
- Base: canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
  revision 6.
- Model: as stated in PR3620 PROOF.md section 1 and in
  `research/p104-all-pair-consumer-budget/README.md` on main. For pair count
  `p`: `m = 16p+9`, `W = 208p`, `P = 3014`, `p+1` forward calls and `p` dual
  calls, residual children of rank `m`, and fully paid banks `B`.
- Test: with `d` rank-one children deleted from every dual call
  (`D_d = D - d·H1`), the relaxation passes iff
  `E_d(p,a) = (16p+9)^a (p·U_d + V) - 6236p - 3014 < 0`, where
  `U_d = Σ_r (F_r + D_{d,r}) r^(1-a)` and `V = Σ_r F_r r^(1-a)`. Here `a` is
  the primitive saving tested (`a_req = κ/(1-κ)`, PR3620's test value
  `1/596`, or `κ` on the rejection side), and the slack is `-E_d` in normalised cost units. REVIEW.md 3.3-3.4
  derives this from the clamped model.

Coverage-grant check (REVIEW.md 1.3-1.5): the grant is favourable for PR3609's
dual, and the completion's children are not counted twice.

- Per-call persistent progress is `Σ (len(final) - len(initial))` over the 358
  role fields, so it is fixed by the boundary frame dimensions: X `(1,9)`, Y
  `(0,8)`, dirty `(0,9)`, giving `3014 = 104·8 + 104·8 + 150·9` (PR2744's
  checker). PR3609 states, and its receipt records a check of, the original
  word's complete endpoint map and all 358 final frames. If that claim holds,
  PR3609's per-call progress is exactly 3014, so granting 3014 to every call
  is exact for the dual and an over-credit after deletion. This audit did not
  re-run the frame check.
- `W = 208p` is the inherited law, unchanged by PR3609 (no new banks or
  families). The excess decreases in `W`, so extra families would only help a
  candidate; `W` itself is not shown favourable here.
- The 145 completion calls (`52 H1 + 93 H9`, mass 889) are inside D and are
  charged once. Their progress lies inside the capped credit.

Not checked here: whether the law can be realised (owners, idle packing), and
PR3609's endpoint and native proofs. PR3620 itself calls the law optimistic.

## What is new

- An independent re-derivation of the arithmetic and reductions. It confirms
  the threshold and stated enclosures, including a second all-p proof that
  does not use convexity: exact values for `p = 1..23` and a linear tail bound
  from `p = 24`.
- The slack clarification above: the sharp ceilings at `a_req` under the
  retained conversion, which pair count binds for per-call versus fixed extra
  costs, and the passing pair counts for `d = 426` (6-10 at `1/596`, 6-11 at
  `a_req`).
- Source binding of D to PR3609's receipt, including the split into projection
  (1597 calls, mass 2653) plus entrance completion (145 calls, mass 889).

Predecessors on main screened the older PR2712 dual
([p104-all-pair-consumer-budget](../p104-all-pair-consumer-budget/README.md),
[p104-consumer-budget-audit](../p104-consumer-budget-audit/README.md)). This
package targets PR3609's changed dual, the grant/double-count question and the
general deletion lemma.

Concurrent: jwr404's open [PR #3654](https://github.com/CrocSwap/integer-mult-bounds/pull/3654)
(head `4068c58d`, same task card, oriented at PR3620's 425/426 comparison)
proves that rank-one deletions maximise the power-sum drop and a positive lower
bound for the pair-count convexity bracket. REVIEW.md 3.1, 3.2 and 3.5 cover the
same reductions. They were written independently and do not rely on PR3654.

## Reproduce

From the repository root, Python 3.12 or later, standard library only:

```sh
python3 -I -B research/p104-consumer-threshold-audit/verify.py
python3 -I -B research/p104-consumer-threshold-audit/controls.py
python3 scripts/research_package.py --package research/p104-consumer-threshold-audit
```

Expected markers:

```
PASS_P104_CONSUMER_THRESHOLD_AUDIT d425_rejects_every_p>=1 d426_passes(a596:p6..10,a_req:p6..11) total_slack_p7(a596=4.557071,a_req=4.970660)(best_p_for_per_call_costs) fixed_cost_slack_best_p8(a596=5.040108,a_req=5.524500) a_req=kappa/(1-kappa) conditional_on_PR3609_D_and_named_law
PASS_P104_CONSUMER_THRESHOLD_CONTROLS rejected=14 positive=1
```

`verify.py` reads only. It recomputes all 31 claims and compares the full
receipt with [RESULT.json](RESULT.json). Only `--write` replaces that receipt.
Every check is an explicit raise, not an `assert`, so it also runs under
`python3 -O`.

The two methods are:

- **A.** Fraction interval arithmetic on the model numerator, with the clamp,
  capacity and banks explicit. Logarithms use an atanh series and exponentials
  a Taylor series, both with rigorous tails, rounded outward to `10^-50`.
- **B.** The closed form `E_d` in Python `Decimal` at 70 digits, using
  correctly rounded `ln`/`exp`, padded outward by `10^-55`.

Method A is an independent implementation of the same series technique that
PR3620's PROOF.md describes for its `budget.py` (range reduction, atanh series,
Taylor exponential with geometric tails). Method B is the methodologically
distinct check. The PASS marker is formatted from the recomputed values.

Run time is about 2 s for the verifier and 10-25 s for the controls.

## Negative controls

`controls.py` sends 13 parameter mutations through `verify.audit` and one
corrupted source byte through `verify.load_sources`. Each must break a named
claim: the rejection proof (`B_finite_p1_to_p23_positive`), the passing point
(`E426_p7_kappa_negative`), the matching `p = 4` claim, or a stated enclosure:

- `P` set to 3015 or 3013.
- `D_9 = 92`, `D_1 = 1317`, the rank-9 stratum dropped, or the old PR2712 dual.
- `F_7 = 76`.
- `m = 16p+8` (value binding: the 425/426 threshold survives it; the stated
  enclosures and passing ranges break).
- `W = 209p`.
- The rejection claim evaluated at 426, or the passing claim at 425.
- `p = 4` with the two thresholds swapped.
- One byte of the vendored receipt changed.

The positive control (no mutation) must pass. The control code was frozen
before the sweep. Limit: removing the clamp from `model_excess_A` is not
detected, because the clamp is active only at `p = 1` and method B proves
`p = 1` without it (`E_425(1,κ) >= 40.7565`). `clamp_only_raises_p1` checks a
model property, not the code.

## Scope, inherited assumptions and unresolved obligations

- This is a conditional statement about one relaxation. It is not a P104
  barrier, a supplier and not a multiplication theorem.
- Inherited and not checked: the named coverage law; the per-role progress
  caps; full credit retained after deletion; PR3609's endpoint, native and
  module proofs; and PR2744's forward recount.
- D is bound to PR3609's receipt. It was not recounted from `PROGRAM.json` and
  `NATIVE.json`.
- The threshold covers corrections that delete rank units from PR3609's dual
  children with the forward calls fixed. Coarsening (`H1+H1 -> H2`), added
  children and other replacement networks must pass PR3620 section 2's general
  criterion instead.
- For the passing direction only, these costs are unpriced and must fit inside
  the slack ceilings above: temporarily writable Y sources, ownership, routing, scalar
  work, the 102 missing forward corrections, and any physical deletion network.
- PR3620's `physical/` format half, its section 4 (the PR3605 T740 bracket),
  PR3623 and the PR3259 support cut are outside this audit. PR3605's staged
  words are audited separately in open PR #3687.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. *Which ceiling form should P104 gates quote?* The requirement is already
   fixed by the retained conversion (`a > κ/(1-κ)`); only the form is open.
   Per-call costs bind at seven pairs and fixed costs at eight. First step:
   quote both sharp ceilings at `a_req` in the family status file (0.710094
   per dual call and 5.524500 fixed, for exactly 426 deletions), and label
   tests at `κ` as rejection-side and at `1/596` as point checks. No computation
   needed.
2. *Can any realised deletion network remove at least 426 rank units per dual
   call from PR3609's dual (or, with uneven calls, meet the total threshold
   above)?* With exactly 426 rank-one deletions, a purely
   per-call extra cost must stay below the optimistic ceiling of about 0.71
   units per dual call (`a_req`, seven pairs). Each further rank-one deletion
   per dual call adds `121^a ≈ 1.008` units per dual call at seven pairs.
   First step: name 426 removable rank-one children and their endpoint
   contracts before pricing. Blocked by the absence of any candidate network.
3. *Is D's receipt reproducible from PR3609's program artifacts?* First step:
   recount native ranks from `PROGRAM.json`/`NATIVE.json` and the PR3446
   projection events, without the author's `invoice.py`.

## Credit and provenance

- Clear1nsight: PR3620 (threshold, convex all-p argument) and PR3609 (changed
  dual and in-place completion).
- Vasek (`flyingviper`): the PR2744 consumer-budget audit and its recount.
- Ross Richardson (`RossRichardson`): the PR2458 forward profile.
- Nick Petalas: the all-pair consumer model in `research/p104-all-pair-consumer-budget`.
- Jose Manuel (`jmbarrancoml`): the original four-pair screen and the
  deletion-discount argument
  ([Discussion 2619](https://github.com/CrocSwap/integer-mult-bounds/discussions/2619#discussioncomment-18955566)).
- ywz65: PR2712, used in a control.
- Hiroki Kumazaki (`kumagi`): the PR3446 projection inside D.
- Dominik Scholz: the larger-gain stage template, as credited in the all-pair
  package.
- Sagar Thakrar (`thakrarsagar`), PR1012: the coverage context, as credited in
  the all-pair package.
- Concurrent: jwr404, open PR #3654 (rank-one deletion order and convexity
  bracket), see above.

The vendored receipt is Clear1nsight's Apache-2.0 work, unchanged. PR3609's
own credits (Nick Petalas's PR3462/PR3469, Hiroki Kumazaki's PR3446 projection,
ywz65's PR2586 WORD, Dumas and Grenet, Jose Manuel, Vasek and Ross Richardson)
remain in force for it.

The verifier was cross-checked by two exact methods in this session. The
package was reviewed in three rounds of independent AI review passes in the
same loop (reproducibility, mathematics, provenance, referee), with a revision
after each round.
It is not human-reviewed and is not a proof-assistant check.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from
Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
