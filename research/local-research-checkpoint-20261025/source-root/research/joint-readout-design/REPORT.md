# Joint readout: two failed encoders and a residual contract

2026-10-09. Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.

**No improved supplier or multiplication exponent is certified.** Two explicit
encoding words are correct on arbitrary inputs but cost more than ordinary
copied readout. A joint endpoint calculation leaves a smaller, concrete open
problem: two rank-one residual center copies whose rational discrepancy has
only one rank of excess. Realizing that gap, with a favorable child profile,
is still missing.

This is a mechanism-selection pass following the
[boundary-readout diagnostic](../boundary-readout-sixteenth/REPORT.md).
It changes the proposed readout graph, rather than relabeling an invocation
inside the already optimized grouped-gate model. It does not reopen the
retired clean-aggregate producer model.

The subsequent [residual shared-readout diagnostic](../residual-shared-readout/REPORT.md)
closes the single-parallel-target-bank implementation and the direct
unconverted-center schedules. The residual contract remains open only
beyond those scoped models; the lower-bound gap is still not a construction.

## Interface and exact checks

Work first in the plain triple geometry, for `h>=5`, `h!=9`, with
`H=I-J/9`. For a triple `T`, let `q_T` be its indicator vector and

\[
 P_T=q_T\phi_T,\qquad
 \phi_T=(q_T^{\mathsf T}-\tfrac13\mathbf1^{\mathsf T})/2,
 \qquad K_T=I-P_T.
\]

The center projector `R_j` is onto the span of the `q_T` with `j in T`.
Its image is the hyperplane `sum_l z_l=3z_j`, of dimension `h-1`.
For `j in T`, `P_T R_j=R_j P_T=P_T`.

Targets enter at frame zero and leave at `K_T`. Centers enter and leave at
`R_j`. The isolated scalar operation is

\[
 y_T\leftarrow y_T+\sum_j U_{Tj}z_j,
 \qquad U_{Tj}=\mathbf1_{j\in T},\qquad z\leftarrow z.
\]

Every target and center input is arbitrary. Copies are dependent scratch,
not additional independent roles or recurrence volume. This interface is
not yet a replacement for the full supplier's side corrections, dirty
workspace schedule, shared-core gauges, or endpoint permutation.

`audit.py` tracks symbolic linear combinations of independent input arrays
under exact rational address transformations. Each key includes both the
original input role and its complete address matrix. In particular, a sum
of permuted arrays is not replaced by a permutation with a summed matrix.
The two words are checked over both rational scalar payloads and F2 scalar
payloads, including mandatory decoders and restoration. Rational payload
checks establish local scalar lifts; they are not complex-supplier checks.

## Candidate 1: encode targets against a pivot

For one center, at frame zero replace each nonpivot target by `y_T-y_0`.
Move the pivot to `R`, add the center, and transform one dependent copy of
the updated pivot back to zero to decode the other targets. Move all
targets to their prescribed final frames.

This word is exact. It pays the same children as the original copied
broadcast, **plus one width-two child** for the pivot's exit from `R` to
`I-P_0`. At `h=5`, on six incident targets, the rank bill rises from 28 to 30.
Omitting the decoder fails on arbitrary target values.

There is also a sharp rank obstruction for this isolated interface. For
any gate graph realizing this same scalar broadcast over Q, the endpoint
discrepancy gives the lower bound

\[
 \sum_e\operatorname{rank}(M_v-M_u)
 \ge \sum_T\operatorname{rank}K_T
       +\operatorname{rank}\begin{bmatrix}P_T R\end{bmatrix}_T.
\]

The stacked block has rank `h-1`, because the incident target lines span
`R`. Existing copied readout attains that rank bound. This does not by
itself establish optimality of every nonlinear recurrence moment or cover
a characteristic-two-only scalar realization with no such rational lift.

## Candidate 2: encode two centers at a common frame

Move two centers to a common frame `M`, encode them as `w0=z0+z1`, `w1=z1`,
transform one copy of each encoded stream to zero, and read out using
`U L^-1`. Decode the originals at `M` and restore them to `R0,R1`.
Both encoded streams remain necessary: the scalar incidence matrix has
rank two.

The center rank charge, including copies and restoration, is

\[
 2\bigl(\operatorname{rank}M+
         \operatorname{rank}(M-R_0)+
         \operatorname{rank}(M-R_1)\bigr).
\]

The three pairwise distances among `0,R0,R1` are `h-1,h-1,2`.
Adding the three rank triangle inequalities shows that the bracket is
at least `h`. The projector onto `R0 intersect R1` attains it. Thus this
template costs at least `2h`, versus `2(h-1)` for ordinary copies.
This rank bound allows arbitrary rational `M`; the physical replay checks
five projector choices at `h=5,6`, including noncommuting center projectors
at `h=6`. Omitting center decoding corrupts arbitrary inputs.

This excludes the one-common-frame encoding template. It does not exclude
a distributed word combining several center and target frames.

## Joint endpoint discrepancy leaves room

For all centers together, the target rows of the rational endpoint
discrepancy have diagonal blocks `K_T` and center blocks
`U_Tj(K_T-R_j)`. Quotienting each target output by `image K_T` gives

\[
 Q_{Tj}=U_{Tj}P_T R_j,\qquad
 \operatorname{rank}D=\binom h3(h-1)+\operatorname{rank}Q.
\]

Rank telescoping bounds the charged edge ranks below by `rank D` whenever
the proposed gate graph has the specified rational scalar realization.
This is a lower bound, not a circuit synthesis theorem.

Compress each target block to its one-dimensional image and multiply by
six. The resulting row is

\[
 q_{T,(j,l)}=\mathbf1_{j\in T}(3\mathbf1_{l\in T}-1).
\]

Its rank is exactly `binom(h,2)`, half the separate-copy rank `h(h-1)`.
Indeed its column span equals that of pair incidence on triples:
singletons satisfy `x_j=(1/2) sum_{l!=j} x_j x_l` on weight-three vectors,
and `q_(j,l)+q_(j,j)/2=3x_jx_l` for `j!=l`.

Pair incidence has full column rank for `h>=5`. To see this directly,
suppose pair weights `a_ij` sum to zero on every triple. Comparing triples
`(i,j,k)` and `(i,j,l)` gives `d_i+d_j=0`, where
`d_i=a_ik-a_il`. There are at least three points outside `k,l`, so all
these differences vanish over Q. Every weight incident to a fixed point
is therefore equal; symmetry makes all weights equal, and a triple forces
their common value to zero.

The exact script checks compressed ranks at `h=5,6,7,8` and the full
discrepancy at `h=5`. At `h=23`, the proved formula gives separate-copy
rank 506 versus joint excess 253. **Neither 253 nor the difference is an
implemented readout cost.** This is the plain triple model, not the
selected supplier's complete ledger. No substitution into its loss count
or multiplication assembly is justified.

## A smaller open contract: two residual lines

For centers 0 and 1 choose

\[
 a=e_0+2e_1,\qquad b=2e_0+e_1,
\]

and let `L0,L1` be the H-orthogonal projectors onto these lines. Both
lines have H-norm four, and `L_j` is nested in `R_j`.

Make a dependent copy of each center and transform it from `R_j` to `L_j`.
These are **two paid width-(h-2) children**. Keep the original arbitrary
centers unchanged. The residual readout takes these two copied streams,
updates the arbitrary targets as before, and must finish targets at `K_T`.
The dependent copies may be discarded after use; borrowed original inputs
must still be restored.

Ordinary readout now transforms both residual copies to zero, paying two
width-one children. But the residual quotient `U_Tj P_T L_j` has rank only
one:

- Targets containing only 0 have `P_T L0=0`.
- Targets containing only 1 have `P_T L1=0`.
- Targets containing both see the same quotient row. Their final caps
  contain `a-b`, and the quotient kills the explicit vector `(a,-b)`.

The two actual scalar streams are still independent (`rank U=2`). The
kernel above is a relation between address labels, not permission to
delete an input array or add arrays in different frames for free.

This gives a precise synthesis question:

> Can a distributed target/center word realize this residual readout with
> one width-one child beyond the prescribed target paths, rather than two,
> while preserving arbitrary target values and charging every alignment,
> decoder and restoration?

At `h=5`, the complete pair-readout rank would drop from 48 to 47 if such
a word existed with unchanged target paths. At `h=6`, it would drop from
110 to 109. The script certifies the residual contract and rank lower
bound, **not the missing word**. This formulation avoids insisting that
every target visit a full center frame, which was the earlier excursion
obstruction's hypothesis.

## The child profile is a strict acceptance test

A rank improvement alone does not guarantee a useful recurrence. At the
illustrative coarse-bit saving `s=0.08`, ambient dimension `3h`, compare

\[
 2\left(\frac{h-1}{3h}\right)^{1-s}
 \quad\text{with}\quad
 2\left(\frac{h-2}{3h}\right)^{1-s}
 +\left(\frac1{3h}\right)^{1-s}.
\]

The ideal residual word has positive moment gain, but less than the cost
of one additional width-one child. Splitting a target's width-(h-1) move
into widths 1 and h-2 consumes some of that gain, even though its rank sum
is unchanged.

Exact rational enclosures give the following budget, omitting the common
role normalization on both sides:

| h | Ideal moment gain, approximately | Maximum such target splits | Exclusive targets |
|---|---:|---:|---:|
| 5 | 0.0550597 | 3 | 6 |
| 6 | 0.0442237 | 3 | 12 |
| 23 | 0.00893851 | 1 | 420 |

Thus moving every exclusive target through its residual line loses even
if the one-child residual readout is granted. A useful word needs shared
alignment or a different paid profile. These are conditional local
budgets, not an admitted new supplier or an extension of the analytic
assembly domain.

## Next bounded experiment and stop rule

Use the explicit two-line contract at `h=5` as the next construction test.
Search for shared alignment across the target classes (only 0, only 1,
both), keeping all input arrays arbitrary. Before scaling, require a
literal word, exact address-operator replay, and its complete child
histogram. Reject candidates that merely remove scalar additions,
identify independent streams, omit decoders, or exceed the split budget.

A successful small word must then extend to general h, survive the real
side-correction and dirty-workspace schedule, and improve the complete
normalized moment. A bounded failure should close the tested template;
the discrepancy gap alone is not grounds for a broad topology search.

## Reproduction

```sh
python3 -B research/joint-readout-design/audit.py --check research/joint-readout-design/certificate.json
python3 -B -m unittest discover -s research/joint-readout-design -p 'test_*.py'
make selected-record-check
```

`certificate.json` records exact ranks, child histograms and rational
moment enclosures. The adverse controls check missing decoders, an
incomplete single-center span, genuinely noncommuting center frames,
generic residual lines that lose the rank-one gap, independent scalar
channels, and target splitting that erases the optimistic gain.
