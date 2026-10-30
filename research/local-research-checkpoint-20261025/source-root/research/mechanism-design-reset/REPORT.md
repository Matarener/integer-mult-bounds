# Design reset: three mechanisms and one admission test

2026-10-09. Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.

**Follow-up:** the [terminal decoder admission pass](../terminal-decoder-admission/REPORT.md)
is complete. Actual routing leaves almost all four-bank summary dimension,
and common-frame terminal decoding exhausts rank capacity. No decoder was
admitted. Distributed realizations remain unresolved, without a selected
physical word or an automatic continuation to a frame search.

**Decision: give a coupled terminal decoder one bounded routing/cost test.**
Its scalar identity and arbitrary-workspace restoration have exact controls
over both relevant scalar fields, including unequal noncommuting stage maps.
No frame-compatible implementation or favorable recursive profile has been
supplied. The selected conditional κ remains `0.000661885549259598`.

The other two proposals below do not earn a construction round in their
stated forms. This comparison selects a specific missing-cost question;
it does not launch an open-ended search or claim a new route to `1/16`.

## Why reset the selection rule

The [residual readout test](../residual-shared-readout/REPORT.md) showed that
a one-rank address-discrepancy floor does not imply a one-transform array
implementation. The [budget audit](../../docs/research/kappa-sixteenth-domain-round.md)
also rejects the retained rank-one deficit and child cap at the target,
even with zero central loss and zero auxiliary stock. Therefore another
local readout improvement alone is not a sufficient `1/16` strategy.

Require a proposed operation identity, identify the paid work it might
remove, and charge its replacement before increasing the search scale.
An unclosed lower-bound gap is not enough. Both suppliers matter: the
selected complex supplier presently limits the assembled result.

| Proposal | Concrete change | Design disposition |
|---|---|---|
| Coupled terminal decoder | Execute side-only exchange stages, then correct their complete output through small summary maps | Select one routing/cost admission test |
| Rank-boosting tensor labels | Tensor the scalar central matrix while replacing intersection labels by union/parity labels | Reject these literal lifts: required annihilations fail |
| Packed permutation differences | Carry only one difference per involution orbit | Park: formation and final expansion require two opposite alignments |

## 1. Coupled terminal decoder

### Complete operation, rather than isolated readout

In a local scalar identity, write the central part as `C=BA`, with A
mapping v sources to k central summaries. Let `S=I-C` be the side part.
Ordinary source-to-target assembly supplies the central and side parts in
each of the three shears implementing the bank exchange.

Consider instead the chronological side-only word

\[
 y\mathrel{+}=S_1x,\qquad
 x\mathrel{-}=S_2y,\qquad
 y\mathrel{+}=S_3x.
\]

The minus is the same as plus for bit payloads. **Do not assume the stage
maps coincide:** cover routing may give different global maps. Their full
scalar transfer is

\[
 M=\begin{pmatrix}
 I-S_2S_1&-S_2\\
 S_1+S_3-S_3S_2S_1&I-S_3S_2
 \end{pmatrix}.
\]

For the desired signed exchange `J=[[0,-I],[I,0]]`, an exact terminal
decoder is

\[
 D=JM^{-1}=\begin{pmatrix}
 S_1+S_3-S_1S_2S_3&S_1S_2-I\\
 I-S_2S_3&S_2
 \end{pmatrix}.
\]

This identity holds without commutativity or a special characteristic.
It is only a change in where work is performed until D receives a cheaper
physical implementation.

### Aligned stages expose a small factorization

If all `S_i=I-BA`, put `Q=AB`, `A₂=diag(A,A)`, `B₂=diag(B,B)`, and

\[
 K=\begin{pmatrix}
 I-3Q+Q^2&Q-2I\\
 2I-Q&-I
 \end{pmatrix}.
\]

Then

\[
 D=I+B_2KA_2.
\]

Two banks of k summaries suffice algebraically. The possible payoff is
replacing central producer/readout work in three stages by one coupled
terminal correction. Neither two banks nor the smaller scalar rank means
two cheap physical calls. Their frames, dirty contents and independent
stock all have to be priced.

There is an instructive bit special case. For incidence V on all triples,
`C=V^T V` over F2 and

\[
 (VV^{\mathsf T})_{ii}=\binom{h-1}{2}\bmod2,
 \qquad (VV^{\mathsf T})_{ij}=h-2\bmod2\ (i\ne j).
\]

When `h=2 mod 4`, `VV^T=0`, hence `C²=0` and `S²=I`.
The side-only exchange has outputs `(Sy,Sx)` and needs S once on each
bank at the end. This is not a characteristic-zero shortcut: a nilpotent
matrix cannot have unit diagonal there, since its trace is zero.
More generally `S²=I` with `S=I-C` requires `C²=2C`, forcing
`rank C=v/2` in characteristic zero. In the conservative copied-source
model that gives `L>=vr/2`. Even granting zero auxiliary stock, the
zero-gauge moment at complex saving 0.075 exceeds one throughout
`0<=r/d<=1/2`: concavity reduces the test to endpoint values approximately
1.08589 and 1.06961. This excludes that simple shortcut under those
accounting hypotheses, **not the general coupled decoder**.

### Unequal routing enlarges the summary requirement

Let `C_i=B_i A_i`, with k channels per stage for notation. D−I factors
through the four input summaries

\[
 A_2x,\quad A_3x,\quad A_1y,\quad A_2y.
\]

For an explicit factor, write `Q_ij=A_i B_j` and set

\[
 A_* = \begin{pmatrix}A_2&0\\A_3&0\\0&A_1\\0&A_2\end{pmatrix},
 \quad B_* = \begin{pmatrix}B_1&B_2&0&0\\0&0&B_2&B_3\end{pmatrix},
\]

\[
 K_* = \begin{pmatrix}
 -Q_{12}&-Q_{13}+Q_{12}Q_{23}&-I&Q_{12}\\
 I&-Q_{23}&0&-I\\
 I&-Q_{23}&0&-I\\
 0&I&0&0
 \end{pmatrix}.
\]

Direct multiplication gives `D=I+B_*K_*A_*`. The dimension of these
input summaries is

\[
 \operatorname{rank}\begin{pmatrix}A_2\\A_3\end{pmatrix}
 +\operatorname{rank}\begin{pmatrix}A_1\\A_2\end{pmatrix}.
\]

This measures overlap in this factorization; it is not a universal minimum
decoder rank or a free frame-compatible compression. It ranges up to 4k.
In explicit noncommuting toy column-permutation controls it is 18 rather
than 12 for the bit example, and 15 rather than 10 for the rational example.
Those permutations are **not production cover routing**. The aligned-stage
decoder fails when wrongly applied to these unequal-stage examples.

### Arbitrary dirty workspace can be restored

For either factorization, abbreviate `D=I+EF` and `H=I+FE`.
H is invertible because D is invertible. For arbitrary data z and dirty
workspace w, execute

1. `w += F z`;
2. `z += E w`;
3. `w -= H⁻¹ F z`;
4. `w = H w`;
5. `z -= E w`.

After step 3 the workspace is `H⁻¹ w_original`; after step 4 it is restored.
The final data is `D z_original`. This supplies an exact **scalar** completion
without zero-initialized workspace. The scalar workspace mixing in steps
3–4 is not declared free in the physical frame geometry.

The audit executes every independent data and workspace column for:

- F2, full triples at `h=6`, including the nilpotent case;
- Q, full triples at `h=5`, using a dyadic rank-h factor of
  `C_ST=(|S intersect T|-1)/2`;
- unequal, noncommuting stage maps in both fields.

The rational factor uses the first `h-1` incidence rows plus the all-ones
row, replacing the last incidence row through `sum V_i=3·ones`. This uses
the existing rank-h factorization idea, not a new claim of priority for it.
Every tested scalar decoder coefficient is dyadic. No complex Clifford
phase, endpoint chart, frame transition, recursive moment or all-size
implementation has been validated by this scalar replay.

### Why select this for one test

Unlike the last readout experiment, the correction depends on the original
data through the central maps and is allowed to mix both output banks.
It is not an isolated broadcast from arbitrary independent center inputs
around an unchanged target bank. It also does not use the matched encoder
that the earlier rational-lift obstruction closed.

The algebra works in both scalar fields and accommodates the stage-routing
problem rather than assuming it away. Those are reasons for one bounded
cost test, not evidence of an eventual improvement. In the rational toy,
the unoptimized decoder has more nonzero phase coefficients than the three
old central routines. These counts include identities and dense maps;
they are neither optimized gate counts nor recursive costs.

**First admission test:** derive the actual routed stage maps and compute
or bound the joint summary spaces above. Reprice the required source,
target and workspace frames with their genuine outer cuts. Begin with the
complex side, since it binds the selected result. Give this factorization
favorable internal costs first: if even that complete lower bound loses,
stop before a frame search. If it leaves room, build one literal small
decoder and its inverse with every internal transition charged.

**Acceptance:** a lower complete normalized moment than its matched
baseline, after changed stock, side paths, both terminal banks, restoration,
entrance/exit gauges and dependent buffers are included. A scalar identity
or fewer center appearances alone is not a pass. Retain signs and exact
complex phases. If the tested factorization fails, end that round; a
different decoder proposal needs a fresh mechanism and budget assessment.

**Milestone limit:** this rewrite alone does not establish the block density
or child sizes needed for `1/16`. If it preserves the old rank-one gross
ledger and child cap, the existing exclusion still applies. Its value would
be a reusable paid mechanism for a later different core, or an incremental
improvement. That possibility must be demonstrated, not inferred.

## 2. Rank-boosting tensor lift: reject the literal proposal

A tempting construction tensors a cheap scalar central map `C tensor C`
while increasing address-block density using union or parity projectors:

\[
 P^{\lor}_{ij}=P_i\otimes I+I\otimes P_j-P_i\otimes P_j,
 \qquad
 P^{\oplus}_{ij}=P_i\otimes I+I\otimes P_j-2P_i\otimes P_j.
\]

Their relative ranks are `2t-t²` and `2t(1-t)` for original ratio t.
The cheap scalar factor has diagonal one, so whenever `C_jl!=0` the lifted
pair `(i,j),(i,l)` still requires annihilating labels. Union labels share
`image P_i tensor whole_space`, so they fail immediately. Parity labels
also fail in the explicit dimension-three rank-one control: required-edge
product rank is one. The ordinary tensor-intersection labels do annihilate
but reduce the rank ratio to `t²`.

The audit records exact commuting coordinate counterexamples, with ranks
1, 5, 4 in dimension 9 for intersection, union, parity respectively.
This rejects these recipes with unchanged tensor scalar support. It does
not reject all tensor constructions or new interaction graphs. Altering
the support would require a new paid central factorization and encounters
the [joint support/producer screens](../interaction-family-design/REPORT.md).
No broad tensor-label search is selected.

## 3. Packed orbit differences: park without a shared-consumer identity

For an involutive address permutation P, `(P-I)x` has only one independent
difference per two-cycle. That suggests carrying roughly half as much data.
But the two halves are generally in different tape orders.

For matrix transposition, let a be the strict upper triangle in row order,
b the lower triangle in row order, and T align lower entries to matching
upper entries. Form `delta=a-Tb`. The complete transpose is

\[
 a'=a-\delta=Tb,\qquad b'=b+T^{-1}\delta=T^{-1}a.
\]

This requires both T and its inverse, each acting on half the movable
data. Their total aligned volume is the original movable volume, not
half. The script checks every independent input coefficient and rejects
omitting inverse alignment. Diagonal fixed points require no movement in
either version; they are not an additional saving of this rewrite.

A useful typed primitive would need several consumers that can retain the
packed difference and share the final expansion, plus a closed recurrence
and a paid fixed-tape packing procedure. None is supplied here. Merely
counting the independent difference values does not establish a speedup.
This route is parked rather than selected for construction.

## Research checkpoint and reproduction

The design session is complete. The sole selected successor is the coupled
decoder's routed-summary and frame-cost admission test. This is a research
priority decision; no goal loop, broad search, publication, or production
verifier change was launched.

```sh
python3 -B research/mechanism-design-reset/audit.py --check research/mechanism-design-reset/certificate.json
python3 -B -m unittest discover -s research/mechanism-design-reset -p 'test_*.py'
make selected-record-check
```

The selected construction retains Dugongue #186, chafreaky #181, eumemic
#168 and the cumulative community lineage. These diagnostics concern
separate toy families and algebraic rewrites; no contribution to the
selected κ is claimed.
