# Full monomial two-FULL routing still fails with identity scratch

This note closes the simultaneous extension left open by
`research/two-full-central-obstruction/PROOF.md` and
`research/two-full-central-obstruction/grade/PROOF.md`. Those theorems grant
either arbitrary restored identity scratch, or full monomial routing on
exactly two owners, and they say the two grants are not the same theorem.
The argument below grants both at once for every finite scratch count.
It is an algebra obstruction. It is not a new word, a caller, or a kappa.

## Setup

Let G be the finite one-column Clifford group used by the predecessor,
including absolute phases, and let H be its monomial subgroup. Let A be the
twisted group algebra of G and B the twisted group algebra of H, over a
field of characteristic zero. A nonzero scalar cocycle does not affect the
argument: left multiplication by a group unit still permutes the basis up
to nonzero scalars. Fourier rank is subadditive, every element of H has
rank 0, and left multiplication by H preserves rank.

Label owners `0,...,n-1` with `n>=2`. Owners 0 and 1 are the two main
owners. Owners `2,...,n-1` are identity scratch. Each main transverse
factor `a0,a1,b0,b1` is a pure group unit of rank at most `t`. The source
case is `t=8`. Write `pi` for the projection onto the span of group
elements of rank at most `2t`. It is a B-bimodule map. In the source case
`2t=16`, which is the cutoff in the grade note, because two rank-8 factors
multiply to rank at most 16.

Each FULL factor is diagonal transverse multiplication after one elementary
shear on the two main owners. For an arbitrary central element `c` in A,
an upper shear is `I + e0 c e1^T` and a lower shear is `I + e1 c e0^T`.
The square of that off-diagonal term is zero, so every such shear is
invertible on `A^n`, with inverse given by the minus sign. The two FULL
factors may use different central elements, different orientations, and
different transverse units. Neither shear reads or writes a scratch owner.

The interstage matrix `W` and the outer matrices `L,R` lie in `GL_n(B)`.
The same matrix inverse over B remains an inverse over A, because the
product that gives the identity only multiplies elements of B. Thus `W`,
`L` and `R` are K-linear automorphisms of `A^n`.

The forbidden target is `diag(g0,g1,I,...,I)`, where `g0` and `g1` are pure
group elements of rank greater than `2t`, so `pi(g0)=pi(g1)=0`, and each
scratch coordinate is returned as the identity.

## The free input subspace

Let `r` be the main owner read by the first shear, and let `f` be the other
main owner. Let S be the coordinate subspace of `B^n` on which owner `r`
is zero and owner `f` together with every scratch owner is free. Then
`dim_K S = (n-1) dim_K B`.

On S the first shear acts as the identity, because its only added term
contains the zero coordinate. The first transverse diagonal then multiplies
owner `f` by the unit `a_f` and each scratch owner by 1. That map is
injective, so the first FULL factor is injective on S.

The image of S has a rigid rank bound. Owner `r` is zero. Owner `f` is
`a_f` times a B-element, hence Fourier rank at most `t`. Each scratch
coordinate is a B-element, hence rank 0. Applying `W`, whose entries have
rank 0, keeps every coordinate at rank at most `t`. Call this intermediate
vector `u`. Every coordinate of `u` is kept by `pi`, and in fact by the
stronger projection onto rank at most `t`.

## The clean output kills the second shear

Let `z` be the second FULL factor applied to `u`. Exactly one main output
is untouched by the second shear. That output equals its transverse unit
times the corresponding coordinate of `u`, with no central factor. The
product of a rank-at-most-`t` unit with a rank-at-most-`t` element has rank
at most `2t`, so `pi` keeps it. Vanishing of that projected output is
therefore vanishing of the algebra element, and the transverse unit forces
the corresponding coordinate of `u` to vanish.

That coordinate is the one the second shear reads. After it vanishes, the
central term is multiplied by zero. The other main output collapses to its
own transverse unit times the remaining main coordinate of `u`, which `pi`
likewise keeps, so that coordinate vanishes too. Each scratch output equals
the corresponding scratch coordinate of `u`. Those coordinates already have
rank at most `t`, so `pi` keeps them and they vanish as well.

Thus `pi(z)=0` implies `u=0`. Combined with injectivity of `W` and of the
first FULL factor on S, `pi` of the whole product is injective on S.
Therefore

```text
rank pi(T2 W T1) >= (n-1) dim B.
```

The central elements never need a rank bound. They are multiplied only
after the coordinate they read has already been forced to zero.

## Comparison with the identity-scratch target

The projected target is `diag(0,0,I,...,I)`. Its image is the scratch
coordinates, so its rank is exactly `(n-2) dim B`. For `n=2` that rank is
zero. Because `pi` is a B-bimodule map and `L,R` are invertible over B,

```text
rank pi(L T2 W T1 R) = rank pi(T2 W T1) >= (n-1) dim B
                     > (n-2) dim B = rank pi(diag(g0,g1,I,...,I)).
```

The two maps cannot be equal. No choice of orientations, central elements,
rank-at-most-`t` transverse units, monomial interstage, or monomial outer
change removes the gap. The gap is exactly one copy of B, coming from the
main input the first shear does not read.

For `n=2` the same bound says the projected product has rank at least
`dim B`, while two pure high-rank targets project to zero. That recovers
the two-owner shear obstruction under these hypotheses. It does not replace
the predecessor's separated-address nullity theorem, which allows scratch
but only one nonmonomial update in each FULL factor.

## All large widths

The predecessor's separating-polynomial argument says that, for every
sufficiently large tensor width, distinct projective classes remain linearly
independent after the central-character specialization. An identity of
operators at every such width therefore implies the same identity in the
twisted group algebra. The rank gap above is an identity failure in that
algebra, so it forbids an all-width completion. A single small width can
still have an accidental numerical relation. This note does not compute
that width and does not change the predecessor's sufficient bound.

## What remains out of scope

A FULL shear that reads a scratch owner is a different macro. The
intermediate rank bound uses that the first shear does not. Transformed
helper states are not identity scratch; the separated-address note already
records that they cannot be absorbed into `L,W,R`. Rank of a transverse
factor above `t`, or a cutoff below `2t`, can drop the clean output and
the proof stops applying. Finite movement, precision, compiler reserve and
outer transfer are not reached, because the endpoint identity already
fails. No conditional kappa is claimed.
