# Cubic caller: constant scalar bank directions

The positive quadratic continuation is in [QUADRATIC.md](QUADRATIC.md): an exact n+1-query scalar caller for every even n when N^2=-I, with native source-code transport still open.

This package also proves scoped lower bounds for a proposed exact common operator
`N` with `N^3=I`, over characteristic zero. There is no positive caller or new
κ claim. The actual rank-two Clifford lead and its native source-code deposits
belong to the stabilizer lane. None of the scalar arguments removes those
deposits or changes their charge.

The scientific checkout pin is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. This is local work in the originally
clocked round `kappa-changed-endpoints-20261019T0153Z`. The primary checkout and
the predecessor `mixed-carrier-caller/` and `coded-bit-boundary/` packages are
not modified.

The written results are:

* Three banks require at least five paid queries, even if the coefficient of
  each rank-one query is any scalar polynomial in `N`, provided its bank
  direction is constant rational.
* In `n` banks, using the actual mixed alphabet `E_ij(±N)` and `E_ij(±N^2)` with
  arbitrary constant rational scalar bridges requires
  `k >= n + ceil((n+1)/3)` paid queries.
* Three matching layers cannot give `N I_n`, even before restricting the
  directions to be rational.
* Four layers cannot give `N I_n` if every layer is pure: its nonconstant
  coefficient is all `N-1` or all `N^2-1`. A layer mixing both coefficients is
  outside this last obstruction.

These are all-word written proofs. The scripts supply exact finite identity
checks and negative controls; they are not exhaustive searches or kernel
formalizations. The independent review is recorded in
[INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md).

## Exact model and normalization

All `n` public inputs are independent. The desired word equals `N I_n`, or a
constant bank permutation times `N I_n`, over the **full** ring
`Q[N]/(N^3-1)`. A positive construction would therefore have to retain the
eigenvalue-one component. Allowing rational constants relaxes the requested
integer scalar bridge model, so a lower bound in this model also holds for
constant integral ADD/swap/sign words.

A paid query is `E_ij(s N^e)`, `i != j`, `s=±1`, `e=1 or 2`. Constant
`GL_n(Q)` operations may appear anywhere between paid queries. Normalize a
word `W(N)` by its full augmentation `B=W(1)`: `B^-1 W(N)`. If the word achieves
the desired output, this normalization gives `N I_n`, including when the
original target has a final bank permutation. Pulling the constant operations
through one query yields

```
I + (N^e-1) u_i v_i^T,
u_i,v_i in Q^n,  v_i^T u_i=0.
```

The sign is absorbed into either vector. For example, immediately before a
query the augmentation is `B_0`; its normalized direction is
`s B_0^-1 e_i e_j^T B_0`. The updated augmentation is
`E_ij(s) B_0`. This proves the normal form for arbitrary bridges, without a
commutation assumption. The saved fixtures check this statement on the full
cubic ring for both query powers.

Every factor has the literal inverse obtained by negating its nilpotent
perturbation. Its determinant is one. Thus `3 | n` is a further necessary
condition for the target, independent of the lower bounds below.

A full-ring identity necessarily holds after the specialization `N=ζ`, where
`ζ^2+ζ+1=0`. The lower bounds may use this necessary condition. They do not
infer a positive full-ring identity from a primitive-component identity.

## Three banks, four queries: arbitrary polynomial coefficients

Suppose `C_4 C_3 C_2 C_1 = ζ I_3`, where
`C_i=I+α_i u_i v_i^T`, the direction vectors are rational, and `v_i^T u_i=0`.
Here `α_i` may be any element of `Q(ζ)`; in particular the proof includes
mixed `ζ-1` and `ζ^2-1` queries.

The image of the product minus identity is contained in the span of the four
column directions. Since `ζ I_3-I_3` has rank three, some three of them are
independent over `Q`. Any three-element subset of four cyclic positions is
consecutive in cyclic order. Cyclically rotating invertible factors preserves
a central product: if `AB=ζI`, then `BA=A^-1(AB)A=ζI`. Rotate the application
order so that the independent directions occur first. A constant rational
change of basis then makes those directions `e_1,e_2,e_3` respectively.

Set `P=C_3 C_2 C_1`, with factors acting from right to left. `C_1` changes only
row one and has first diagonal entry one. `C_2` changes only row two and has
second diagonal entry one. `C_3` changes only row three. Consequently

```
P_11=1,       det P[{1,2},{1,2}]=1.
```

For clarity, before row three is changed the leading block is
`[[1,a],[b,1+ab]]`; its determinant is one regardless of the other entries.
But `P=ζ C_4^-1=ζ(I-α_4 u v^T)`. Write `c_i=u_i v_i`, which is rational. The
two principal minors force

```
α_4 c_1       = 1-ζ^-1,
α_4(c_1+c_2) = 1-ζ^-2.
```

The first right side is nonzero. Taking the ratio gives
`(c_1+c_2)/c_1 = -ζ`, contradicting rationality. This also covers three factors
by padding an identity; fewer than three already fail the image-rank test.

The constant-direction hypothesis is essential. `cubic_gate.py` checks an
explicit four-factor identity `N I_3` on the full cubic ring whose directions
depend on `N`. It checks all three independent columns and the literal
inverse, and verifies that each perturbation has coefficient-span dimension
greater than one, so it is outside the one-query constant-direction model.
Another negative control agrees with `N` at primitive roots but has value four
at `N=1`; the full-ring checker rejects it.

## General mixed-alphabet rank bound

Let `k` queries act on `n` banks, and specialize to `N=ζ`. Put `t=ζ-1` and
`t_2=ζ^2-1`. The normalized factors are
`I+α_i u_i v_i^T`, `α_i in {t,t_2}`. All vector entries are rational. Define

```
U=[u_1 ... u_k],       V=[v_1^T; ...; v_k^T],
B=VU,                 D=diag(α_1,...,α_k),
B=L_0+U_0,            G=(D^-1-L_0)^-1,
```

where `L_0,U_0` are the strict lower and upper triangular parts of `B`.
The diagonal of `B` vanishes. Expanding in chronological order gives the exact
resolvent identity

```
W = I + U G V.
```

For the desired central target, `UGV=tI_n`, so `U,V` both have rank `n` and
`k>=n`. Moreover `G V U/t` is a rank-`n` idempotent. It follows that

```
C = B-tG^-1 = U_0+ζL_0-diag(t/α_i)
```

has rank exactly `r=k-n` over `Q(ζ)`. The identities
`t/t=1` and `t/t_2=-ζ` give `C=A+ζH`, with rational matrices

```
A=U_0-diag(1 on N-query positions),
H=L_0+diag(1 on N^2-query positions).
```

Thus `A` is upper triangular, `H` is lower triangular, and their nonzero
diagonal supports partition all `k` positions. Complex conjugation preserves
the rank of `C`. Each of `A,H` is a linear combination of `C` and its conjugate,
so each has rank at most `2r`. If there are `a` first-power and `b` second-power
queries, their triangular principal minors give

```
a<=rank A<=2r,       b<=rank H<=2r,       k=a+b<=4r.
```

Equality `k=4r` is impossible. It would force both `A,H` to have rank `2r` and
to share the joint row space and the joint column space of `C` and its
conjugate; each joint space has dimension at most `2r`. Hence `A,H` have the
same image and kernel. Their ranks equal their nonzero-diagonal counts, so
zero is a semisimple eigenvalue of each. The unique projection onto the image
along the kernel is

```
P_A=I-(I+A)^k,       P_H=I-(I-H)^k.
```

The formulas annihilate the generalized nonzero eigenspaces and preserve the
zero eigenspaces before subtraction from identity; the exponent `k` suffices
for every possible Jordan block. Both therefore have the same image and
kernel, and uniqueness gives `P_A=P_H`. But their diagonals are respectively
the indicator of first-power positions and its complement, an immediate
contradiction. This proves

```
k < 4(k-n),       k >= n+ceil((n+1)/3).
```

The separate inequalities `a,b<=2(k-n)` are also useful for any prescribed
alphabet balance. In particular, a homogeneous alphabet requires `k>=2n`.
This general theorem is narrower than the three-bank theorem: unrelated
polynomial query coefficients need not have the displayed complementary
triangular split.

| Banks `n` | Necessary calls `k` | Favorable mass deficit `24n-16k` |
|---:|---:|---:|
| 3 | 5 | -8 |
| 6 | 9 | 0 |
| 9 | 13 | 8 |
| 12 | 17 | 16 |
| 24 | 33 | 48 |
| 48 | 65 | 112 |

In particular, six-bank/eight-call and nine-bank/eleven-call proposals fail
before any native bank-code transport is considered. Four-layer wider models
are not eliminated merely by this table.

## Three matching layers

Assume a layer consists of disjoint pair queries, and scalar bridges occur
only between complete layers. All pair perturbations within a layer annihilate
one another in both orders. The augmented-normalized layer is `I+A_l` with
`A_l^2=0`, also when its pair queries mix the two powers. Constant conjugation
by a bridge preserves this square-zero property.

For `P=(I+A_2)(I+A_1)`, direct multiplication gives

```
tr P = n+tr(A_2 A_1) = tr P^-1.
```

If `(I+A_3)P=ζI`, then `P=ζ(I-A_3)`, forcing the two traces to be `nζ` and
`nζ^-1`. They cannot agree in characteristic zero. This gate even allows
operator-dependent square-zero perturbations. It does not cover arbitrary
scalar mixing inside a nominal layer: that mixing may invalidate the
square-zero layer premise and the claimed reuse of a fresh block.

## Four pure layers

Suppose four normalized square-zero layers give `ζI`. For either adjacent pair
`P`, the complementary two-layer product is `ζP^-1`. Both products have equal
trace to their own inverse, so `(ζ-ζ^-1) tr P=0`, and `tr P=0`.

If two neighboring layers have the same pure coefficient, their pair trace is
`n-3ζ s` or `n-3ζ^2 s` for rational `s`. Neither can vanish for positive `n`.
The layer types must therefore alternate. By cyclic rotation and generator
conjugation, write the putative word as

```
(I+t_2 D)(I+t C)(I+t_2 B)(I+t A) = ζI,
A^2=B^2=C^2=D^2=0,
```

with all four matrices rational. Compare the rational and `ζ` coefficients of
`(I+t_2D)(I+tC)=ζ(I-tA)(I-t_2B)`. Using `tt_2=3` gives

```
C-D = I+2A+B+3AB,
D(2A+B+3AB) = A+AB.
```

Multiply the second equation on the right by `B`: `2DAB=AB`. Applying `D` and
using `D^2=0` forces `DAB=0` and then `AB=0`. The first two-layer product now
has trace `n+3tr BA=n`, contradicting its required trace zero. This proves the
four-pure-layer obstruction for every positive `n`, without a rank assumption.

The finite certificate checks both coefficient formulas and their explicit
target-defect remainder, rather than pretending an arbitrary fixture solves
the central target. Layers that mix `t` and `t_2` retain additional coefficient
matrices, so this proof does not apply to them.

## Complete optimistic invoice and native scope

For `n` banks of twelve independent fields and `k` OPEN calls in `s` legal
matching layers, the optimistic parameters are

```
W=12n, m=2+5s,
H_1=8k, H_2=40k, H_3=16k,
H_5=12(ns-2k),
mass=60ns+16k,       D=mW-mass=24n-16k.
```

Every inactive bank at each layer pays a fresh-rank-five idle. This is the
per-layer invoice; adjacent idle blocks have not been coalesced. Nonnegative
`H_5` requires actual disjoint query pairs in each layer. A scalar bridge must
also have an actual native admission/charge before the optimistic invoice can
be promoted to a construction.

For three banks and five sequential calls this is `m=27,W=36`,
`H={1:40,2:200,3:80,5:60}`, mass `980`, stock rank mass `972`, so `D=-8`.
It fails already at exponent zero; every positive exponent makes each
contracting-child contribution strictly larger. Source diagonal-code,
native-gauge, private/helper/owner, scalar/address, precision and tape costs
have all been omitted favorably. The six-bank lower bound gives `D=0`, also
failing every positive exponent irrespective of layering.

The root lane owns the wider positive-exponent budget screen. The remaining
four-layer mixed-coefficient scalar problem is mathematically distinct from
actual supplier admission: even a factorization there would still require
source-code transport, full arbitrary-input native endpoints, restoration,
literal inverse and all added costs.

## Reproduce

From this directory run:

```
python3 cubic_gate.py
python3 -O cubic_gate.py
python3 wide_gate.py
python3 -O wide_gate.py
```

The scripts compare newly computed results to the saved JSON receipts; ordinary
readback does not overwrite them. `--write` explicitly regenerates a receipt.
No external package, network access, PR, hosted CI, or publication is involved.
