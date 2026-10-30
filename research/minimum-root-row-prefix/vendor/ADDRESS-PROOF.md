# The original root's reserved axes and padded core rectangle

Copyright 2026 Sagar Thakrar. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.

This is a conditional address refinement of `reserved_leaves` and `fast_core`
in Jose Manuel's original PR3385 `root_layer.py`, at
`7e5a187214126d31afc241a8f89f4a652352b58c`. It explains how the three source
calls cover exactly the selected tensor axes and why the temporary row
padding can be removed. It does not independently prove the recursive
machine, its numerical precision, the normalized root, or its cost bound.
The source and its predecessors already claim the tensor decomposition;
the contribution here is an independent derivation at these literal
descriptor and serialization boundaries.

## 1. Domain and endpoint contracts

Let $D,q_0,q_F,q_B,H,l,r$ be nonnegative integers, and let $K,O,F,w$
be positive integers. Here $l,r$ are the left and right spectator widths,
$O$ is the outer-row count, $F$ is the number of Gaussian coefficients per
address, and $w$ is a signed component width. Let $0\le\rho<K$ and put

\[
 a=q_0+q_F,\qquad c=D-a-q_B>0,
 \qquad f=q_FK-2H\ge0,\qquad b=q_BK-H+r\ge0.
\]

The fast branch has the strict inequality $D>Q_0=q_0+q_F+q_B$.
The two nonnegative-width conditions hold for the production choices
$q_F=\lceil2H/K\rceil$ and $q_B=\lceil H/K\rceil$.

Within each outer row the payload is ordered by increasing binary address
of width $l+DK+r$. Within each address the $F$ Gaussian coefficients occur
in order, each with a real and imaginary component of width $w$.
Address bit positions are counted from the least significant bit. The
selected positions are

\[
 S=\{r+\rho+jK:0\le j<D\}.
\]

The other address bits are spectators. Component-bit order is irrelevant
to the address argument, provided all callees preserve the same component
serialization. No conversion between inner and outer coefficient formats
is asserted here.

We retain the following contracts explicitly.

1. An exact leaf with widths `(left, selected*K, right)` applies its
   declared tensor factor $C$ on positions `right+rho+j*K`, independently
   for every outer row and coefficient, and is the identity on every other
   address factor at its completed endpoint. It preserves the complete
   rectangle and returns in the source's required tape state. This remains
   true for arbitrary correlations among the fields.
2. The completed recursive machine with the supplied descriptors applies
   $C^{\otimes c}$ on its active spaced positions independently for each
   prefix, row, coefficient and choice of spectator bits. It restores the
   entire rectangle, including the three compact fields, at its endpoint.
   Its implementation may temporarily move or mix rows or use compact
   fields; the completed endpoint must have this rowwise action.
3. These operators are linear, hence send a zero row to a zero row.
   Numerical headroom, exact divisions, physical ownership, source/target
   separation and closed scratch needed to realize their endpoints are
   inherited contracts. This address proof supplies none of those bounds.
4. The plan fields denote the integers specified here, the input packet is
   complete, and the unchanged transfer and encoded-count routines realize
   their declared copy/move and arithmetic operations. Count cursor and
   tape cleanup guarantees are retained with those physical routines.

The conclusion below is an implication from these contracts. A finite
coordinate-routing witness is not a substitute for them.

## 2. The two reserved leaves

The source first computes `prefix=q0+qF`, `tail=selected-prefix`, and
`suffix=tail*K+right`. Its first `apply_leaf` call therefore has widths

\[
 (l,\ aK,\ (D-a)K+r).
\]

By the leaf contract it acts on positions

\[
 r+(D-a)K+\rho+tK,\qquad 0\le t<a.
\]

These are exactly the original selected indices $j=D-a,\ldots,D-1$.
The widths sum to $l+DK+r$; no spectator or component is discarded.

The source next computes `left=(selected-qB)*K+left` and calls the leaf
with widths

\[
 (l+(D-q_B)K,\ q_BK,\ r).
\]

This acts exactly on original selected indices $j=0,\ldots,q_B-1$.
If either reserved width is zero, the source's zero-width return implements
the empty tensor product. Both leaves operate separately on all $O$ outer
rows and all $F$ coefficients. They may create correlations between the
eventual row labels and other fields; no product-state assumption is used.

## 3. Reinterpreting the complete packet as rows

After the reserved leaves, divide each address into the following fields,
written from most significant to least significant:

\[
 [\text{left}:l]\ [\text{row}:q_0K]\
 [\text{front reserve}:q_FK]\ [\text{core}:cK]\
 [\text{back reserve}:q_BK]\ [\text{right}:r].
\]

This is a reinterpretation of the existing serialization, not a movement
of selected coordinates. The original outer-row index together with the
left field gives

\[
 P=O2^l\quad\text{prefixes},\qquad R=2^{q_0K}\quad\text{rows per prefix}.
\]

Each row has $A=(D-q_0)K+r$ address bits and

\[
 B=2^A\,F\,(2w)
\]

serialized component bits. These are exactly the source's `prefixes`,
`original_rows`, and `row_bits`. The identity

\[
 PRB=O\,2^{l+DK+r}\,F\,(2w)
\]

accounts for the entire packet, including all spectators and coefficients.

For any positive stock $T$, set $R'=T\lceil R/T\rceil$. The source's
`RowPadding.run` consumes $RB$ bits for each of the $P$ prefixes and then
appends $(R'-R)B$ zeros. Consequently the old coordinate
$(p,u,x,k)$, where $0\le u<R$, is retained as $(p,u,x,k)$ in the padded
rectangle; $k$ denotes the within-address coefficient/component bit.
The only change to a serialized offset is the larger stride between
prefixes. Rows $R\le u<R'$ are complete zero rows. Appending one zero block
only at the end of the whole packet would not have this property when
$P>1$; the source loops over prefixes.

## 4. The recursive descriptor selects the middle axes

The source passes `before=after=0`, `width=c`, `spacing=K`, `residue=rho`,
`compact_bits=H`, `front=f`, and `back=b` to the recursive machine. Its
row geometry is therefore

\[
 [f]\ [H]\ [H]\ [cK]\ [H]\ [b].
\]

The source identifies this with the preceding rectangle because

\[
 f+2H=q_FK,\qquad H+b=q_BK+r,
\]

and hence

\[
 f+3H+cK+b=(D-q_0)K+r=A.
\]

Thus its selected position $t$ is

\[
 b+H+\rho+tK=r+\rho+(q_B+t)K,\qquad0\le t<c.
\]

The recursive call acts exactly on original selected indices
$j=q_B,\ldots,D-a-1$. It preserves the other bits by the retained endpoint
contract, including compact-field bits on which an earlier reserved leaf
may already have acted. The row and prefix descriptors are respectively
$R'$ and $P$; `component_bits`, `coefficients`, `guard`, and `root_width`
are passed from the plan without changing their meanings.

## 5. Unpadding and the tensor implication

By the rowwise homogeneous recursive endpoint, an appended zero row is
still zero when the recursive call returns. `RowPadding.run(remove=True)`
copies each original $RB$-bit block and checks every bit in that prefix's
appended block is zero before skipping it. It therefore restores the
original $P\times R$ rectangle exactly. A nonzero appended bit is rejected;
this is an explicit check, not silent truncation. The zero claim relies
on the completed endpoint, not on intermediate rows staying zero.

The three selected-index intervals are pairwise disjoint and satisfy

\[
 \{0,\ldots,q_B-1\}\ \dot\cup\
 \{q_B,\ldots,D-a-1\}\ \dot\cup\
 \{D-a,\ldots,D-1\}=\{0,\ldots,D-1\}.
\]

Operators on these distinct tensor factors commute. Therefore the source's
chronological sequence of first reserved leaf, second reserved leaf and
padded recursive core has endpoint $C^{\otimes D}$ on exactly $S$, with
the identity on all remaining address factors and with every coefficient
and outer row retained. This is the middle unnormalized transform only.
It does not prove the surrounding phase sweeps, multiplication by $((1-i)/2)^D$,
signed truncation, the unit-disk/error conclusion, or the full root theorem.

## 6. Production stock and the padding factor

For the source's fixed level divisor $L>1$ and coarse depth $h\ge0$, the
plan sets

\[
 q_0=h\lceil\log_2 L\rceil,\qquad T=L^h.
\]

Since $K\ge1$, $R=2^{q_0K}\ge L^h=T$. For positive $R,T$,

\[
 R\le R'=T\lceil R/T\rceil<R+T\le2R.
\]

This proves the strict less-than-two volume enlargement at this padding
boundary, with all other fields unchanged. The depth-zero case has
$q_0=0$, $R=T=R'=1$. This does not prove the child stock induction,
descriptor setup cost, or the global running-time invoice.

The address theorem itself only needs $R'\ge R$ and complete row padding;
the stock law is an additional premise for the factor bound and production
admission. Reduced fixtures with injected plan fields are labelled as such
and do not establish the production parameter law.

## 7. Evidence, prior coverage and attribution

The original `check_root.py` tests a complete reduced fast root with
$K=1$, $\rho=0$, zero left/right spectators, one coefficient and one outer
row. Its original and padded row counts are both eight. The original
`check_root_streams.py` separately checks a phase sweep at $K=2,\rho=1$
and prefix padding with unequal row counts. These are useful prior checks;
they do not jointly exercise the nontrivial fast-root descriptor boundary.

The finite checks in this package use explicitly declared routing endpoints
to inspect literal call descriptors and complete packet coordinates, with
real source padding and transfer routines. Such a routing endpoint is not
the numerical operator $C$. Its role is to distinguish address mistakes
and expose padding or spectator loss. The universal tensor conclusion is
the conditional argument above, not an inference from those finite maps.

Jose Manuel (`jmbarrancoml`) supplied PR3385's root, planner, physical
cohort and credited PR2287 construction, retaining the numerical, native,
hosting, ordinary-backend and normalization lineage. His later T74 layer
retains the reduced fast fixture; no T74 production execution is claimed
here. Nick Petalas's `t74-outer-format-plan` already supplies the outer
dimension and signed component-order adapter and reduced direct-root tests
with nonzero spectators and multiple coefficients/rows. Its proof explicitly
retains root correctness. This package does not reclaim that adapter or a
new tensor identity. Exact predecessor pins and original notices are in
the accompanying source manifest.

This is a written source-relative implication with finite layout controls,
not a proof-assistant certificate, complete source-to-machine refinement,
fixed-prime factory admission, outer multiplication theorem, or a change
to the selected frontier.
