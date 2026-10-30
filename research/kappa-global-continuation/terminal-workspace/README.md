# Terminal workspace and conservative native tariff

The direct residual inverse can use **72 existing private zero fields** at the
terminal boundary. This finite lifetime statement removes an unnecessary
denominator penalty. It does not make the physical gather and scatter cheap.
The conservative implementation below costs **896 rank-one children** and
already fails the raw invoice. The recorded 72 query coordinates imply neither
72 rank-eight children nor nine rank-eight children.

This work was substantially assisted by OpenAI under the user's direction.
It does not claim an improved multiplication exponent.

## Reproduce

From the repository root:

```sh
python3 -B research/kappa-global-continuation/terminal-workspace/check_workspace.py \
  --followup /path/to/kappa-consumer-followup \
  --out research/kappa-global-continuation/terminal-workspace/RESULT.json
python3 -B research/kappa-global-continuation/terminal-workspace/screen_padding.py
```

`check_workspace.py` binds the original native receipt, both canonical words,
and the freshly emitted alternating programs. It checks allocation and release
events independently. Exact zero values at local release are inherited from
the source-bound alternating local replay on all 632 live input columns; this
checker does not repeat that numerical replay.
The owned-clear check separately calls the retained native interpreter's
`core_frame_check` and `replay`: it fills 72 C labels with an arbitrary live
input column, erases all 72 in a common FULL frame, and verifies that the
borrowed live input is preserved and no recursive child is introduced.

## Explicit query lifetime and family map

The m73 allocation already counts 368,640 productive families, 376 retained
helper families, eight other private families, 91 private zero families, and
two coefficient families. Thus the total remains 369,117. Its private zero
bank is the inclusive interval 369,024 through 369,114.

For stage \(j\in\{0,\ldots,8\}\) and query coordinate
\(k\in\{0,\ldots,7\}\), assign

\[
Q_{j,k}\longmapsto 369024+8j+k.
\]

This is an injection into families 369,024 through 369,095. The receipt also
gives the corresponding actual canonical zero-buffer roles. Both native
orientations allocate and release all 91 roles. After all local and idle child
work, run the 360 terminal replicas serially, releasing the 72 query fields
after each replica. This schedule needs no concurrent local scratch and no
extra physical family. The receipt emits every terminal epoch.

The retained scalar grammar admits `clear` on owned query scratch in the FULL
frame. The receipt emits 72 such logical operations and the injective map of
their query labels onto the released physical zero bank. These are owned
temporaries; no arbitrary borrowed data are erased. The optional second
gather in the helper consumer gives a reversible erasure alternative, but it
is not necessary for the stated retained grammar.

This proves finite capacity and lifetime compatibility with the existing
private bank. It is not an emitted all-size recursive field-hosting ledger.
The inherited size, precision and tape obligations still apply.

## What a complete conservative physical implementation costs

The helper consumer proves the operator identity

\[
M^{-1}=I+U(I-G_{\rm upper})^{-1}V.
\]

Its 72 intermediate fields are a storage count. The entries of \(V\), \(U\),
and \(G\) involve actual owner permutations, not just scalar coefficients.
At the terminal boundary 448 ordinary X fields have gauge
\(C_{\rm FULL73}C_q^{-1}\). The remaining fields already have the common FULL73
gauge. A conservative implementation is:

1. Apply \(C_q\) to those 448 fields, charging 448 rank-one children.
2. Gather, solve, scatter, and clear the queries while all fields remain FULL73.
3. Apply \(C_q^{-1}\) to the same 448 fields, charging another 448 rank-one
   children and restoring the required output holes.

In the middle, implement each summand by an actual rank-zero source view,
Gaussian addition, and inverse source view. A gather summand temporarily
applies the appropriate owner map to its data source, adds it to the query,
then undoes the view. A scatter summand temporarily views its query source,
adds it to the data destination, and undoes the view. A Gram summand with
\(i<j\) applies \(P_{j,p}^{-1}\) followed by \(P_{i,p}\) to source query
\(Q_j\), adds the coefficient multiple into \(Q_i\), then undoes those source
views in reverse order. The source and destination do not alias.
Here the displayed \(P\) products describe the normalized-coordinate
operator. The physical word must use their correctly conjugated owner maps
in the FULL basis, following the retained native dual/inverse-transpose
convention. An unconjugated normalized route label is not automatically a
legal physical map in another gauge.

The inherited terminal native proof establishes that the affine owner views
commute with the owner-independent common FULL gauge. Gaussian field
operations also preserve that common gauge. Therefore this lowering uses
actual allowed native maps; it does not infer native eligibility from a scalar
route identity. Even a reversible cleanup pass can stay inside the same FULL
normalization. The receipt specifies this finite lowering, rather than
emitting every expanded rank-zero term of the inverse.

The complete m73 preconsumer invoice has raw rank mass 74,368 per replica,
against normalizer \(73\cdot1024=74,752\). The 896 rank-one fallback raises the
mass to 75,264, an excess of 512. Every child rank is below 73, so increasing
the exponent above zero only worsens this failed invoice. This upper
construction establishes a concrete remaining target: a cheaper native
gather/scatter interface must account for the X holes without paying these
896 line transforms. This is not a lower bound on every possible decoder.

## Why whole-replica padding does not rescue the m81 screens

`screen_padding.py` reads the frozen source-bound invoice and reproduces exact
outward rational signs for 256 cases: two normalization alternatives, two
terminal tariffs, and padding dimensions 1 through 64. Both 72 rank-eight
children and eight rank-72 children fail in every case, even granting the
native common-padding geometry and optimal fractional inherited idle packing.

There is also a proof for **every positive padding dimension** in this scoped
family. Put \(p=1-a\in(0,1)\), \(m_0=81\), and

\[
A=\frac{1}{W}\sum_r n_r r^p.
\]

The exact m81 rejection says \(A>m_0^p\). Appending one rank-\(d\) child on each
of the \(W\) productive fields, and increasing ambient dimension to
\(m_0+d\), gives moment

\[
\frac{A+d^p}{(m_0+d)^p}.
\]

For positive \(m_0,d\), strict subadditivity gives
\((m_0+d)^p<m_0^p+d^p<A+d^p\), so the new moment remains greater than one.
Charging the whole-bank padding is essential to this conclusion. The scope
retains the original m81 profile, including its optimistic rank-57 idle mass,
and the proposed terminal tariff. A redesigned supplier, altered idle
geometry, or different terminal interface is outside this rejection.
