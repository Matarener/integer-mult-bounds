# Sharp depth limit for bare Pascal lane iteration

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped proof with an exact finite numerical certificate.
Independent human and formal proof-kernel review are unclaimed.

At height 65, **no starting population passes the declared C=.0034 local
ledger after 111 bare Pascal steps**. The bound is sharp: a pure lowest-grade
start passes through step 110 in this algebraic relaxation. The original
66-grade equal-population start already fails after its first bare reuse,
with signed surplus in `[-17.553090674, -17.553090235]`.

Yiyang / Lyy-iiis's [PR5037](https://github.com/CrocSwap/integer-mult-bounds/pull/5037)
gives the reduced-domain border core, its one-shot local invoice and the
recurrence `d'_h=d_h+d_(h-1)`. It already observes eventual top-grade
domination. The new theorem optimizes every nonnegative starting population
and gives an exact first-failure depth. The source operator and native counts
are cited premises, not newly audited results.

For every fixed height H and integer depth e, the sharp minimum top-grade
fraction is

```text
q_H(e) = binom(e,H) / sum_(k=0)^H binom(e,k).
```

The surplus per unit final population is at most `A-B q_H(e)`, where A is
the cited base target-minus-paid moment and B is its top-grade target debit.
The pure lowest-grade vector attains this upper bound at every depth. For
e>=H>=1 it is the unique attaining direction. See [PROOF.md](PROOF.md) for
the weighted-average argument, equality cases and strict monotonicity.

## Scope and relevance

This is a partial answer to PR5037's whole-job matching question. It rules
out keeping a favorable homogeneous local bill through unchanged fixed-height
Pascal iteration by choosing better initial populations alone. The next
construction needs changed matching, a priced reset or a changed per-grade
invoice. It gives no new kappa or selected-frontier change.

The accounting extension is an explicit hypothesis: each population unit
has the same T/P ledger and each top-grade unit loses 112 rank-17 targets.
PR5037 does not establish that actual graded main/helper inventories realize
this extension. The theorem concerns that scalar relaxation. Depth counts
applications of the population recurrence, not actual multiplication recursion.
It excludes no different graded caller, replenishment or increasing height.
Native shears, all-size source/exit/complement matching, ownership, routing,
precision, stock, BIT transfer and outer admission remain open or inherited.
No complete multiplication theorem or formal-kernel proof is claimed.

## Evidence and reproduction

CPython 3.12 and its standard library suffice. Local replay used CPython
3.12.15 on macOS 27.0.1 arm64. From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/pascal-lane-depth/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/pascal-lane-depth/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/pascal-lane-depth
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/pascal-lane-depth --check-source-history
```

A portable Python 3.12 interpreter can replace the absolute path. Both direct
modes print `PASS_PASCAL_LANE_DEPTH` in a generated JSON receipt binding all
six package files and both cited inputs by SHA256. Direct replay needs only
these relative paths, without Git or network access. It writes nothing;
redirect stdout outside the checkout to retain a receipt. There is no
handwritten or frozen result receipt.

The certificate uses integer powers to bound all eight rank powers. It proves
strict signs at depths 110 and 111 and for the equal-start first reuse.
Literal iteration and the binomial formula agree in 4,654 population/depth
cases. The checks also cover 65 pure-grade attainers, 3,360 equality-case
fixtures, optimal-fraction monotonicity through depth 256, eight invalid
inputs and four false extrapolation controls. Finite checks corroborate the
written universal proof. Predecessor scientific verifiers are never executed.

## Sources and overlap

Canonical base is `721c03822c421b7f7fcbb2598993b947c4d88419`, priority
revision 8. [TASK.json](TASK.json) records the changed scope from
`complex-rank-shape-decoder`; [SOURCES.json](SOURCES.json) pins the exact
predecessor README and proof. The card's current first command,
`research_selected_baseline.py`, passes source bindings only. The selected
conditional frontier is unchanged.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19247035)
records this question. The initial overlap cache included 407 open PR bodies and
5,828 Discussion records with complete reported remote pagination. Sparse
local overlap covered 78 of 8,348 tracked note paths; separate Git searches
covered main's README corpus and merged/all-state PR searches covered Pascal,
border, lane and grade terms. This is bounded overlap evidence, not proof of
novelty or coverage of unpublished work. PR5117's root-only sign extraction
is a different question and is not extended here.

Credit Yiyang / Lyy-iiis for PR5037 and its bounded-lane core/recurrence/invoice;
Cao Yifan for the round-three native source; Dillon for border recovery;
Jacob Alan Sussman and the finite-precompiler contributors; and the retained
native, Clifford, helper, precision and outer lineage. The binomial theorem
and weighted-average method are classical. The new contribution is the sharp
population optimization and its source-specific exact depth consequence.
Predecessor files and their credit lines are unchanged.

## Implementation bounds

The checker uses direct calls, no recursion, subprocesses, external imports
or network access. Population entry points enforce height <=65, depth <=256,
and initial entries below 2^256. The exhaustive small domain has height <=4
and depth <=12. Each rank-power root uses at most 48 iterations, with integers
below 2^220000. Inputs and package files are each bounded below 1 MiB; the
source manifest has exactly four declarations and two fixed input paths.
All functions fit within sixty physical lines. Invariants use explicit
exceptions and remain active with optimization. Both registered modes enable
warning errors; no external static analyzer is claimed.

Power of Ten rule 3 deviation: CPython allocates arithmetic objects and bounded
collections dynamically. This one-shot exact checker cannot prohibit those
runtime allocations. Enforced inputs bound live data, and only one small
population or rank-power bisection is live at a time. Normal and optimized
replay exercise the maximum height/depth and invalid-input limits. A future
steady-operation native implementation would need fixed-capacity arithmetic
storage before removing this deviation.

## Open next questions

1. Can a paid grade-reset or replenishment operation keep the complete bill
   favorable? Start with one explicit reset, retained independent inputs,
   restored helpers and its full signed invoice. Legal native transport,
   ownership and reset costs are blockers. A reset is not free in this result.
2. Can a literal whole-job caller use nonhomogeneous per-grade profiles to
   escape the scalar ledger? Export one matched parent/child slice with
   source, exit and complement identities, then compute its full per-grade
   T/P profiles. Actual native shears and constructed graded adapters remain
   prerequisites. The present theorem does not supply that caller.
