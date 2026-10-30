# Integer idle counts must be imposed before normalization

**Source-bound counterexample in an aggregate cost model. No physical packing,
supplier admission, new multiplication kappa or selected-frontier change.**

[PR3729](https://github.com/CrocSwap/integer-mult-bounds/pull/3729), audited at
`c7c68f89e020f9e62f38514afdfc99dda01430d4`, computes a valid integer optimum
for **one call with idle mass exactly 1646**. Its claim that this tightens the
predecessor's ceiling for every selected-word repacking requires an additional
local-mass restriction. The selected source supplies an **aggregate** integer
invoice. Dividing that invoice by the call count gives rational averages.

## Decisive comparison

The retained selected invoice has `N=144` calls, `W=14336` live families,
width `m=73`, and rank guard `R=51`. Subtracting its actual idle histogram
from its full profile gives exactly `144` times the paid local profile
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, of mass 5586 per call.
The coverage identity gives

```text
total paid mass = 72 W + 64 N = 1041408
idle mass       = 1041408 - 144*5586 = 237024 = 144*1646.
```

The actual selected idle counts are `{1:2276, 3:377, 7:7, 48:4866}`.
Every one becomes nonintegral after division by 144. This fact does not refute
the stronger restricted model by itself: even equal integer mass per call
could produce nonintegral average counts. It does show why integrality cannot
simply be transported through normalization. The missing implication is the
**equal-mass local decomposition**, not the integrality of actual children.

The selected independent owner auditor, whose exact source is pinned as
provenance, recounts residuals by `(owner replica, idle child, port)` after
subtracting occupied helper slices. It then adds those residuals to the whole
`9*T`-call local profile. This source reading corroborates the aggregation
boundary; this package does not rerun or replace that auditor's physical rules.

At PR3729's claimed upper endpoint `a=0.001688603446527`, compare the
following **whole-invoice** idle histograms, including the same full paid local
profile in both moments:

| Idle constraint | Aggregate histogram | Certified moment |
|---|---|---|
| Each call separately has mass 1646 | `{51:4608, 14:144}` | greater than `1.0000000000000017` |
| Only aggregate mass and guard | `{51:4647, 27:1}` | less than `0.999995815381823334` |

All counts are nonnegative integers, both idle masses are 237024, and all ranks
obey `73^2 > 2*51^2`. The normalized complete moment is

```text
Phi(a) = [144 * sum_r local[r]*(r/73)^(1-a)
          + sum_r idle[r]*(r/73)^(1-a)] / 14336.
```

The pooled histogram is therefore a counterexample to the proposed ceiling
**inside the stated unrestricted aggregate relaxation**. It is not a physical
owner assignment. An additional physical restriction might exclude it and
justify a stronger ceiling, but that restriction must be stated and proved.
The DP's arithmetic for the narrower equal-mass-per-call problem is preserved.
This audit reproduces its strict upper sign and lower/upper grid bracket.

Even requiring that every integer child belong to some call does not supply
the missing equal-mass condition. The pooled histogram has the purely
arithmetic call allocation:

| Calls | Idle children per call | Mass per call |
|---:|---|---:|
| 39 | 33 of rank 51 | 1683 |
| 1 | 32 of rank 51 and one of rank 27 | 1659 |
| 104 | 32 of rank 51 | 1632 |

It averages to 1646. No hosting, chronology or per-family legality is asserted
for this allocation.

## Correct fixed-invoice ceiling and scaling diagnostic

[PR1685's retained package](../idle-packing-stability/README.md) already proves
the aggregate optimum `{51:4647,27:1}`. This audit does not claim that theorem
or histogram as new. Applying it at the actual aggregation unit gives the
strict two-sided root bracket

```text
0.001690044548222 < a_pooled < 0.001690044548223.
```

The proof used from PR1685 is short: for `0<a<1`, `f(r)=(r/73)^(1-a)`
is strictly concave with `f(0)=0`. Two interior ranks can be merged when
their sum is at most 51, or replaced by `51` and their sum minus 51
otherwise, strictly lowering cost. Repetition leaves only rank-51 children
and at most one residual child. Conservation gives `237024=4647*51+27`.
This is a combinatorial optimum, so its moment brackets the unrestricted
aggregate-model ceiling; no network realization is needed for that statement.
Every rank is strictly between zero and 73, so the complete moment is continuous
and strictly increasing in `a`; the two strict signs determine its unique root.

Under a model additionally permitting unrestricted pooling across replicated
invoices, the integrality gap can disappear entirely. Since
`51/gcd(237024,51)=17`, seventeen copies have integer histogram
`{51:79008}`. After normalization its cost is **exactly the predecessor's
fractional relaxation**, as an algebraic identity for every `a` in the pricing
domain. This diagnoses the aggregation assumption; it does not prove such
pooling is allowed by a physical compiler or the fixed selected layout.

The two-unpaid-coordinate lever also cannot be ruled out merely because its
average idle mass is `13918/9`: at 144 calls the total is the integer 222688,
with an aggregate arithmetic witness `{51:4366,22:1}`. This says nothing about
realizing the hypothetical changed coverage law or its complete cost bill.

## Evidence and independent arithmetic

[RESULT.json](RESULT.json) retains exact rational interval endpoints, outward
decimal displays, both root brackets, the source decomposition, the call
allocation and five deliberate rejections: rank above guard, wrong mass,
fractional actual child count, falsely integral normalized count, and wrong
whole-invoice normalization. Checks use explicit exceptions and survive `-O`.

The primary prices reuse Douglas Colkitt / Claude's authenticated, unchanged
`complex-local-word-ceiling/ceiling.py`. A separately written price engine
checks the decisive pooled/restricted signs and both corrected bracket ends:

```text
x^(1-a) = x * sum_{k>=0} (a)_k/k! * (1-x)^k,  x=r/73.
```

For `0<a<1` all terms are positive and successive ratios are at most
`z=1-x<1`. After a computed term `t_k`, the omitted tail is at most
`t_k*z/(1-z)`. Integer floor/ceiling recurrences at scale `2^192` enclose
every term and sum; an outward geometric tail closes the upper bound.
The verifier stops when that tail is at most `2^-140`, with a 20000-term
cap. This engine uses no predecessor logarithm, exponential or DP code.
At `a=1/2`, four additional checks square its bounds and enclose the exact
rationals `1/73`, `14/73`, `27/73` and `51/73`, calibrating it independently
of the predecessor's series.
The historical positive-binomial arithmetic in PR1052 is predecessor context;
this implementation is newly written. Independent arithmetic does not make
the physical packing admissible or constitute independent human review.

## Reproduce

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -I -B research/idle-integrality-aggregation-audit/verify.py
python3.12 scripts/research_package.py --package research/idle-integrality-aggregation-audit
```

The first command reads only package files and the live inputs declared in
[VERIFY.json](VERIFY.json); it works in a Git-free export retaining those paths.
The registered command additionally checks historical Git provenance and runs
both normal and optimized modes. `--write` explicitly regenerates only this
package's `RESULT.json`; default verification never rewrites it.

[AUDITED-SOURCE.json](AUDITED-SOURCE.json) records the exact PR3729 commit,
paths, Git blob IDs and SHA256 hashes for its unmodified README, result and
implementation. The direct verifier authenticates these retained bytes without
needing the foreign PR object or runtime network. [SOURCES.json](SOURCES.json)
pins the selected inputs, original task card and pricing engine at canonical
main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6.
No source archive, historical package or shared production code is changed.

Author validation passed the registered normal and optimized commands on
CPython 3.12.14 and an optimized Git-free export on CPython 3.14.7. All fourteen
exported files remained byte-identical. In disposable export copies, changes to
the retained audited result, live price engine, expected receipt and local-call
scaling were each rejected. TASK.json records these checks and their limits.

## Open next questions

Can the actual owner/controller contract impose a stronger local-mass or
legal-group restriction? This matters because physical constraints, rather
than normalized integrality alone, might support a stronger ceiling. Start
by extracting the selected per-family residual intervals and their cross-call
and cross-replica assignments, then prove a necessary inequality before pricing
it. The blocker is the missing legal-group characterization. The unrestricted
optimum is already known; another random packing seed does not close this gap.

Physical realization of the pooled witness, a complete supplier/consumer bill,
the full selected cold replay, all-size/compiler and analytic-transfer
obligations, hosted CI and independent human/formal acceptance are outside
this audit. The selected conditional result remains unchanged.

## Credit and coordination

Credit Nick Petalas for PR3729's DP, restricted-model bracket and clear published
claim; Penguin (OpenAI) for Maximus Putnam for PR1685's aggregate optimum and
stability theorem; Douglas Colkitt with Claude assistance for the exact ceiling
engine and model; PR1012's coverage identity; Ali Romman's catalogue-bound
lineage; and the selected work by Rohan Arun, Jeremy Kothe, Hao Yan and all
predecessors and independent auditors retained in
[the selected review](../../docs/research/community-batch1099-review.md).
In particular, Josie Elliston supplies the retained independent owner audit,
Sagar Thakrar its pricing counterpart, and Douglas Colkitt their composition.
The audited source's original notices are retained unchanged.

This is the changed `selected-packing` scope in [TASK.json](TASK.json).
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2278#discussioncomment-19022491);
[concrete feedback on the audited PR](https://github.com/CrocSwap/integer-mult-bounds/pull/3729#issuecomment-6254060645).
The live overlap snapshot covered 444 open PR bodies and 2495 Discussion
records with complete pagination and no warnings; this is bounded, non-atomic
coverage, not a novelty proof. Submission freshness belongs in TASK.json.

Prepared by OpenAI Codex at Arham Tahir's direction, with substantial AI
assistance throughout. New work is Apache-2.0; no independent human or
proof-kernel review is claimed.
