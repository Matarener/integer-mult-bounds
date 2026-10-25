# Current-cut endpoint debt and its precise boundary

This package presents the corrected endpoint theorem for a unary simultaneous
current-cut insertion model, together with source-bound exact operator checks
and an actual full-native coefficient path outside its deficient path class.
It proves no complete clearing caller, native physical schedule, rounded
supplier, or stronger multiplication bound. The support library
`full_stabilizer_bound.py` was already reused by later packages; this standalone
theorem, its counterexample boundary, and its complete retained receipts are
the scope here. It does not republish any later changed caller.

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Original sources and receipts are preserved unchanged. `ORIGINS.json` records
their authorship lineage and the explicit loader/output adaptations. Substantial
OpenAI Codex assistance; Apache-2.0 ancestry. This is written mathematics and
finite exact computation, not a formal-kernel proof.

## 1. Operator model and quantifiers

Let L>=1 and split the binary address space orthogonally as

```
C direct-sum F_0 direct-sum ... direct-sum F_(L-1),
dim C=2, dim F_s=5, m=2+5L.
```

The common plane has orthogonal norm-one basis p,q. The actual positive
Gaussian Clifford in translation direction v is

```
C_v = ((1+i)I+(1-i)X_v)/2,
C_v^2=X_v,       C_v^-1=C_v X_v.
```

These identities retain the global phase. Let F_s denote the product of the
five positive coordinate C gates on fresh block s and let
`F_<=s=F_s ... F_0`. The chosen chart maps p,q to the two common coordinates.
The third odd orbit root maps to the characteristic vector of all five fresh
coordinates, not one fresh axis.

For each local source normalizer write `P_s=pre_s^-1`. It is monomial and acts
only on C plus its own fresh block. The exact source-bound common-F relation
is `post_s S_s pre_s=T_s`, with monomial post_s and `T_s=F_s` in the stated
chart, retaining any actual Pauli decorations. Those decorations are paid
monomials; their phase is not discarded. Put `R=C_p C_q^-1`.

At cut s use the physical fronts

```
D_X,s=C_p F_<=s,       D_Y,s=C_q F_<=s.
```

A simultaneous unary logical insertion H_s is admitted when both physical
pullbacks are monomial. In particular, write
`M_s=D_X,s H_s D_X,s^-1`. The theorem only uses that this X pullback is an
invertible monomial. M_s may have an arbitrary address permutation and
arbitrary nonzero diagonal factors; it need not be Clifford, affine,
quadratic, local, or a tensor product. Requiring the Y pullback to be
monomial only restricts this larger class. All its address and phase work
remains paid.

Define the chart insertion and ordered relay expression by

```
J_s=C_p H_s C_p^-1=F_<=s^-1 M_s F_<=s,
Q=P_(L-1) J_(L-2) P_(L-2) ... J_0 P_0,
Y_out=F_<=L-1 Q R.
```

The theorem is conditional on this displayed ordered endpoint expression for
every L>=1. The independently replayed free noncommutative two-column word
establishes the B1 expression only at L=3:

`E=A_2^-1 Z A_1^-1 H A_0^-1` on both arbitrary input columns after the signed
exchange. It does not require A_s,H,Z to commute or be involutions, but it
does not construct an L-stage caller for general L. In particular the L=1
operator fixture is not a zero-bank caller construction.

## 2. Exact telescoping; no absorbing-past premise

For s>=1, P_s acts on C plus fresh block s and therefore commutes with every
earlier fresh Fourier factor. Thus

`F_<=s P_s F_<=s-1^-1=F_s P_s`.

Substitute each exact J_s into Y_out and cancel only adjacent actual inverse
factors. This gives

```
Y_out=(F_(L-1) P_(L-1)) M_(L-2) ... (F_1 P_1) M_0 (F_0 P_0 R).  (1)
```

No M_s is commuted through a fresh Fourier operator. It can freely mix past
and future fresh directions. Every cancellation uses the actual adjoint,
including its sign and phase, rather than replacing it by a positive C gate.
Equation (1) is consequently an exact operator identity on arbitrary arrays.

The dressed-swap counterexample in the companion counterexample package
explains why this argument is needed. With one completed fresh direction u
and one future direction v, let physical M swap u,v and let
`H=D_X^-1 M D_X`. Both cut pullbacks are monomial, but H transfers the
completed-past phase-space direction `(u,u)` to the future direction `(0,v)`.
Preservation of the complete current-cut intersection therefore does not
preserve its past and future summands. The older common-corner product
argument without insertions cannot be extended using that false absorption
premise. Equation (1) makes no such inference.

The companion chirped GL2 example also shows that admitted common-coordinate
mixing need not be an orthogonal address map. The common quadratic chirp is
essential to its simultaneous admission. An undressed logical past/future
swap, by contrast, has a hidden rank-two query at the cut. Native rank zero
for a correctly dressed map still leaves its literal scans paid.

## 3. Source-bound first factor and row-support theorem

For a matrix U let s(U) be its maximum number of nonzero entries in a row.
For every compatible pair, `s(UV)<=s(U)s(V)`. An invertible monomial has
row support one. Every later factor F_s P_s has row support exactly 2^5,
because right multiplication by a monomial only permutes and scales columns.

The actual first factor is smaller:

| Port family | Number | native rank of F_0 P_0 R | row support |
| --- | ---: | ---: | ---: |
| A/B | 8 | 5 | 2^5 |
| C | 4 | 3 | 2^3 |

This is not an extrapolation from a finite search of normalizers. From
`post S pre=T`, one has `T pre^-1 R=post S R`. Left monomial multiplication
preserves each row-support count. The fixed source operators S R have the
displayed ranks, so every normalizer satisfying this source identity has the
same first-factor support. The checker reconstructs all twelve actual saved
normalizers, their exact first factors, and their literal native lowerings.
Signed Pauli images and complete Gaussian zero columns are compared.

For the Clifford specialization, a rank-r Clifford has exactly 2^r nonzero
entries in every row: it is a rank-r coordinate child between monomials.
One independent source derivation uses the common-F form

```
P = [[G, 0], [G+G^-T, G^-T]],
B(F_fresh P R)=diag(G_CC,(G^-T)_FF).
```

Complementary principal nullity gives
`nullity((G^-T)_FF)=nullity(G_CC)`, hence the local native rank is
`7-4+2 rank(G_CC)`. The actual source identity forces common-corner rank one
on A/B and zero on C. These are corners of inverse(pre), not of pre.

Applying the elementary support inequality to (1) now gives, for all L>=1,

```
s(Y_out)<=2^(5(L-1)+3)=2^(m-4)    on C,
s(Y_out)<=2^(5(L-1)+5)=2^(m-2)    on A/B.                 (2)
```

The result does not require Y_out to be Clifford. If all insertions are
Clifford, it specializes to native B-rank at most m-4 or m-2. For arbitrary
monomial insertions the row-support statement itself is the theorem.

For the saved charts, identity insertions attain these bounds for every L.
Without inserted mixing, disjoint fresh supports make the inverse-pre common
corner of the product the product of the individual common corners. The saved
A/B corners are `diag(1,0)` and the C corners vanish. The same complementary
nullity formula at global dimension m gives exactly m-2 and m-4. The finite
baseline replay covers all twelve ports at L=1,3,5,7,9; the written corner
argument supplies its all-L assertion. No corresponding corner-product claim
is made after arbitrary current-cut insertions.

## 4. Tensor columns and separately paid unary completion

For every integer chunk parameter f>=1, tensor the local source identities
over f columns. Later factors have row support 2^(5f), and the first factor
has support 2^(3f) or 2^(5f). The admitted physical insertion can still be an
arbitrary monomial on the entire tensor address space. Equation (2) becomes

```
s(Y_out)<=2^((m-4)f) on C,       s(Y_out)<=2^((m-2)f) on A/B.
```

A full native mf-coordinate endpoint, even with arbitrary monomial adapters,
has 2^(mf) entries in every row. Thus neither endpoint can already be such a
native full endpoint. Requiring a full X endpoint does not change this Y
obstruction.

Suppose a separate unary completion consists of native children with total
positive rank R, with arbitrary monomials between them. Its row support is
at most 2^R. By support multiplication, completion of a deficit d requires
`2^R 2^((m-d)f)>=2^(mf)`, hence `R>=df`. This argument applies even when the
inserted monomials made Y_out non-Clifford; it does not assign a B-rank to a
non-Clifford matrix. Rank subadditivity is only an alternative proof in the
all-Clifford specialization.

Across one twelve-port Y bank, the separate unary floor is consequently
`4*4f+8*2f=32f`. This is a necessary paid rank sum, not an optimal repair
recipe, one-child realization, primitive count, or complete moment. Coupled
multi-field completion is outside this proof.

For the stipulated old paired schedule only, take odd L=2B+1>=3 with B>=1,
`m=2+5L`, stock `W=12(L-1)`, and inherited local-plus-idle zero-exponent
deficit `D=8L-24`. If its B Y banks are each completed by separate unary
repairs, the additional rank floor is `32B=16(L-1)` in pre-tensor units.
Its completed zero-exponent deficit is at most

`(8L-24)-16(L-1)=-8L-8<0`.

Under the stipulated strict child contraction, increasing a positive power
exponent increases the normalized moment above its already failing zero-
exponent value. This excludes a positive supplier exponent for that completed
stipulated profile. It does not establish the stock premise for a changed
caller, a universal completion lower bound, or a multiplication lower bound.
The L=1 fixture is deliberately excluded from this caller invoice.

The inherited OPEN local resource is `H1=8,H2=40,H3=16`, mass 136, with zero
ordinary/private helper fields. This endpoint package authenticates and
retains that source claim but does not rerun the full local OPEN word.
All native child occurrences, idle progress, monomial normalizers, insertions,
signs, address movements and phase scans remain part of a complete caller
bill. A local endpoint theorem does not make any of them free.

## 5. A full-native path outside the deficient relay class

The admitted normalized forward physical cross at stage zero is `T_0 K_0`,
where `T_0=F_0` and `K_0=C_q C_p^-1 pre_0`. Take that cross and then the
diagonal progress at every later stage. Its isolated coefficient path is

```
U_path=(product_s F_s) C_q C_p^-1 pre_0
      =F_global X_p pre_0.                               (3)
```

The equality is exact: all these translation C gates commute and
`C_p^-2=X_p`. Since pre_0 is monomial, the right side has full row support
2^m and native rank m, or rank mf after tensoring. All twelve actual ports
are replayed at L=1,3,5,9. Complete signed tableaus are compared in every
case, and independent complete Gaussian columns fix global phase for the
retained A and C witnesses at m=17. The written identity gives all L,f.

Equation (3) is one coefficient path, not a complete diagonal caller. A paid
bank exchange can put an original Y input on that source lineage only while
retaining the changed bank-dependent code. It does not establish clearance
of the other input coefficients, monotone global fronts, or favorable stock.
No analogous statement is inferred for the raw reverse-source boundary.
The old three-bank suggestion is preserved as historical context; later
changed callers are separate results, and no unfinished suggestion is
presented here as a newly established construction.

For comparison, if every path in a K-term coefficient sum has row support at
most 2^((m-d)f), the sum has support at most `K*2^((m-d)f)` and a full native
endpoint requires `K>=2^(df)`. Cancellations can only reduce that support.
Fixed or polynomial path counts cannot close a positive uniform deficit for
all f. Equation (3) prevents applying this lemma to every path in every OPEN
network. The heterogeneous refinement and its exact scope are developed
independently in the companion review.

## 6. Exact replay and negative controls

Run from any working directory with a fresh absolute output outside the code
directory and outside an overridden inputs directory:

```
python3 -I -B /path/to/check.py --output /external/new-receipt.json.gz
python3 -I -O -B /path/to/check.py --output /external/new-optimized.json.gz
```

`INPUTS.json` is itself pinned. Each input transport is captured once and
checked for byte length and SHA-256; compressed inputs are then decompressed
and checked against their independent raw pins. The historical mathematical
sources are immutable. The adaptations replace ambient path/import loaders,
preserve original source-digest provenance, and return the canonical endpoint
receipt rather than writing into its original directory. No mathematical
predicate or event is deleted. Captured adapted sources and the unchanged
compiler are compiled with `dont_inherit=True,optimize=0`; the receipt records
both raw and executed-source hashes. No historical bytecode cache, ambient
Git read, or third-party package is used.

The complete canonical endpoint, full-stabilizer and full-native-path outputs
are compared with all fields of their original receipts using type-sensitive
equality. There is no mathematical-field projection. The fresh receipt also
retains the twelve signed local native lowerings and every sparse Gaussian
phase evaluation. Each complete phase column stores every nonzero Gaussian
numerator and its common power-of-two denominator. Hash interning checks
exact data equality on reuse, so a hash is not substituted for phase
acceptance.

Fresh defect controls use the same production equality and admission gates:

* At each of twelve local first factors, right multiplication by an input Z
  fixes the zero column but changes signed Pauli images. The signed-image
  gate rejects; deleting precisely that gate admits the same defect.
* At those twelve factors and all four retained m=17 global identity pairs,
  multiplication by i preserves the signed tableau but changes the complete
  Gaussian column. The phase gate rejects; deleting precisely that gate
  admits the same defect.
* The undressed logical swap and the omitted common chirp fail the shared
  rank-zero cut-admission predicates. Deleting the corresponding predicate
  admits those actual operators.

There are 30 actual intended rejections and 30 executed named-guard deletions.
Each exception must have the intended message; deletion runs occur outside
the rejection handler. Original inequality-only diagnostics are preserved
and rerun but are not counted as these fresh controls. Normal and optimized
complete receipts are compared, and the final package inventory records
their exact raw and compressed hashes.

The finite global tableau checks do not enumerate all monomial insertions;
equation (1) and row support supply that quantifier. Complete m=17 phase
columns are not claimed for dimension 47; the written exact cancellation
supplies the all-L phase identity. Physical ownership, source scans, native
monomial implementations, coefficient precision, approximate children and
outer recursive admission remain distinct obligations.
