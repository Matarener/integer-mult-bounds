# Terminal decoder admission: routing erases almost all summary overlap

2026-10-09. Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.

**No terminal decoder is admitted, and κ is unchanged.** The selected complex
cover forces this four-summary factorization to retain at least `119/120`
of its uncompressed summary dimension. A common-frame terminal implementation
also consumes full rank capacity, even with free internal mixing. Neither
finding excludes every distributed realization of the scalar decoder.

This completes the bounded admission pass from the
[design reset](../mechanism-design-reset/REPORT.md). No frame search or
production-verifier change was launched.

## Selected inputs and routing

The audit reads frozen `selected/complex/graph.json.gz`. It checks all 1,320
ports at `h=22`, selecting one coordinate from each of three coordinate
pairs. It reconstructs the signed ancestors of all 22 center roots and
checks that they produce the incidence sums `sum_(S contains i) x_S`.
Every scatter coefficient is checked against `1/2·1_(i in T)−1/6`.
Thus the central map is `C_TS=(|T intersect S|-1)/2`, factored through
the full-rank, 22-row incidence matrix V.

The remaining side map is `I-C`, including both the paired-cube side
producer and original-source involution. It is not just the local Hadamard
block. See the [retained construction](../../notes/paired-cube-construction.tex).
The receipt pins the graph and cover/frame notes. It does not assume that
deleting center roots preserves old dirty-response corrections or rerun
the entire physical word.

Write `G=O(66,2)`, `g=|G|`. The retained cover places data port `(a,S)` at
vertices `aR_12,S`, `a`, `aR_23,S` in the three stages. Its exchanges satisfy

\[
 R_{12,S}A=B\oplus\langle q_S\rangle,\qquad
 R_{23,S}A=C\oplus\langle q_S\rangle.
\]

Distinct ports give distinct exchanges within either family: the image of
A determines the source line. This holds for every permitted exchange-basis
choice. The script constructs one canonical choice for all 2,640 maps and
checks orthogonality, involution, fixed source, active image and fixed padding.

Let `A₂=I_g tensor V`. The other summary maps are this block incidence map
after the respective data-column permutations. Auxiliary routing only
permutes rows and does not change row spaces. Each has rank `gh`.
The specified decoder needs `A₂x,A₃x,A₁y,A₂y`, with joint dimension

\[
 r_* = \operatorname{rank}\begin{pmatrix}A_2\\A_3\end{pmatrix}
       +\operatorname{rank}\begin{pmatrix}A_1\\A_2\end{pmatrix}.
\]

This concerns these input summaries, not the minimum workspace of every
possible decoder. Output-side cancellations, different factorizations and
sequential recomputation are not ruled out by this dimension count.

## A projection trace bound on the full cover

Use ordinary rational/real orthogonal projections onto scalar row spaces,
not binary address frames. Set `L=V^T(VV^T)^−1 V`. The actual Gram matrix
has diagonal 180, partner-coordinate entries zero, and other entries 18.
Exact inversion and all port checks give `L_SS=h/v=1/60`.

Let P_j project onto the row space of A_j. Their intersection dimension
is at most `tr(P_i P_j)`: the trace contributes one on the intersection
and nonnegative terms on its orthogonal complement.

The untwisted projector connects `(a,S)` to `(a,T)`. A neighboring stage
connects these same positions only when `aR_j,S=aR_j,T`. Distinct routes
therefore leave only `S=T` in the trace expansion. Consequently

\[
 \operatorname{tr}(P_2P_j)=g\sum_S L_{SS}^2
 =g\frac{h^2}{v}=\frac{11g}{30}\quad(j=1,3),
\]

and

\[
 r_*\ge g\left(4h-\frac{2h^2}{v}\right)
       =\frac{1309g}{15}\approx87.2667g.
\]

This is a full regular-cover identity, not a sampled group calculation.

| Summary accounting | Dimension |
|---|---:|
| Identical, aligned stage maps | `44g` |
| Actual routing: lower bound for these summaries | `87.2667g` |
| Four separate banks | `88g` |

At most `1/120` of the separate dimension can disappear through row-space
overlap. The lower bound is `119/60` times the aligned budget. It exceeds
the `66g` stage-indexed center values in three separate invocations, but
that is **not** a recursive cost comparison: old stock is reused, and
widths, chronology and restoration differ.

A dense rational control over the cyclic group of order three checks the
trace formula independently. A collided-routing control gives trace six
rather than four, rejecting use of the diagonal-only formula without its
distinct-route premise.

## Common-frame decoding exhausts rank capacity

Keep the old data cuts and full-volume child rule. Align all updated data
to common exact Clifford frames for terminal decoding, allowing different
common input/output frames and granting internal mixing for free. Retained
controls with converted copies are allowed.

After the old complement tails, data gauges are `X:F`, `Y:FT_(aq_S)^−1`,
with the actual source Pauli/sign normalizations retained. For norm-one
sources the Y preimage frames are `L_((aq_S)^perp)`. Distinct normals have
Lagrangian distance two. The
[arbitrary-frame metric](../../notes/general-clifford-frames.tex) gives,
for any common Clifford frame M,

\[
 d(L_{q^\perp},M)+d(M,L_{r^\perp})\ge2\quad(q\ne r).
\]

At each fixed a there are v distinct port normals. Summing over unordered
pairs gives total one-way distance at least v. Over the cover this is
`N=gv`; returning the updated Y outputs costs another N. The same bound
allows a different common frame for every fixed-a group. Normal-specific
frames with paid interactions instead constitute a distributed model
outside this screen.

The old prefix costs at least `2N(m−1)` on data: source lines reach the
full frame and zero-frame targets reach complementary hyperplanes. Thus

\[
 2N(m-1)+2N=2Nm.
\]

Per group element at m=66 this is 171,600 prefix rank plus 2,640 alignment
rank, equal to data capacity 174,240. Under the retained restored
full-transform endpoint, each independent dirty role adds at least m
along its physical chain. Changing their count does not rescue this model.

For `0<s<1`, `(t/m)^(1-s)>=t/m`. Rank at least capacity therefore prevents
a contracting moment. This grants zero internal decoder cost, free X
alignment and no extra fallback or precision cost. Pauli/phase adapters
cannot improve this lower bound; no equality of symplectic labels is used
to claim an exact implementation.

The small control tests all 67 subspace frames in binary dimension four
against eight distinct norm-one caps; the best one-way sum is eight.
The all-frame statement follows from the metric proof, not the catalog.

## Disposition and scope

Stage summaries scarcely overlap, and common-frame terminal decoding loses
even with free internal work. No new complete child histogram or better
moment results. Do not start a large common-frame or summary-compression
search on this factorization.

The scalar decoder remains valid. A distributed implementation might
interleave summaries with differently framed data, change cuts, or avoid
these summaries. **Its cost remains unresolved.** The routing bound alone
does not exclude it, and the common-frame bound must not be generalized
to it. This is not a proof that all coupled decoders are impossible.

A successor needs a concrete distributed word identifying paid work that
is shared or removed. Another optimistic rank factorization is insufficient.
Stop this bounded round with the conditional witness unchanged at
`330942774629799/500000000000000000`.

## Reproduction and attribution

```sh
python3 -B research/terminal-decoder-admission/audit.py --check research/terminal-decoder-admission/certificate.json
python3 -B -m unittest discover -s research/terminal-decoder-admission -p 'test_*.py'
make selected-record-check
```

The graph is Dugongue #186 on chafreaky #181 and eumemic #168. The paired-cube
construction and orthogonal cover retain icekylinx's and cumulative community
attribution, including an664's completed-core sharing. These diagnostics
neither modify the frozen supplier nor establish its inherited all-size
interfaces independently.
