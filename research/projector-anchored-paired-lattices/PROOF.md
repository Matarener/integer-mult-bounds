# Complete paired-lattice feasibility with projector anchors

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof, with finite executable corroboration.
No multiplication theorem or new kappa is claimed.

## Interface and theorem

Put R=Z_(2)={a/b in Q : b is odd}, and v2(2)=1. A full R-lattice Lambda
in Q^m is the R-span of a rational basis. A paired lattice is Lambda direct-sum
Lambda, with H before D. Supply a finite list of rational 2m by 2m applied
matrices G_k. Include every inverse actually applied. Stability means inclusion,
not equality; an unapplied inverse need not preserve the lattice.

The additional hypothesis is an explicit complete family of anchors:

```text
rank(P_i)=1,     P_i^2=P_i,
P_i P_j=0 for i != j,     sum_(i=1..m) P_i=I.
```

Every P_i must occur as one of the four m by m blocks of an actually applied
G_k. For example, an actual paid label n_(P_i) supplies such an upper-right
block. An unapplied projector is not an anchor.

Choose a nonzero rational c_i in image(P_i) and form C=[c_1 ... c_m].
The identities imply C is invertible and C^-1 P_i C=E_ii. For every nonzero
entry t at row r, column s of diag(C,C)^-1 G_k diag(C,C), retain the edge

```text
s mod m -> r mod m,     weight v2(t).
```

Parallel edges and self loops are allowed. The following are equivalent:

1. Some full common paired R-lattice is stable under every G_k.
2. Integers a_i satisfy a_(r mod m)-a_(s mod m)<=v2(t) on every edge.
3. The graph has no negative directed cycle.

A feasible potential supplies Lambda=C diag(2^a_i) R^m. A negative cycle
excludes every full common paired rational lattice under the anchor hypothesis,
including non-diagonal lattices. This strengthens rejection of diagonal gauges
in the original coordinates.

## Proof of completeness

Stability of Lambda^2 under a block matrix implies stability of Lambda under
each block: apply it to (x,0) and (0,x). Hence every P_i preserves Lambda, and

```text
Lambda = direct-sum_i P_i Lambda.
```

Each summand is finitely generated over R on the line Q c_i. Write its
generators as q_j c_i. The minimum valuation a_i of the nonzero q_j exists.
A generator attaining it is 2^a_i u c_i with u and u^-1 in R. Thus the
module contains 2^a_i c_i, and every generator belongs to 2^a_i R c_i.
Consequently P_i Lambda=2^a_i R c_i. Every possible invariant lattice
therefore has the displayed form. This is the new completeness step.

In that basis the entry t becomes t*2^(a_s-a_r), with indices reduced
modulo m. It is in R exactly when its edge inequality holds, proving 1 iff 2.
Summing inequalities around a negative cycle is impossible. Conversely, add
a source with zero-weight edges to every vertex. Without negative cycles,
minimum paths can be chosen simple by removing repeated-vertex cycles.
Their integer distances satisfy every edge inequality, proving 2 iff 3.
Subtracting a_1 from all a_i preserves the inequalities.

The graph argument is the classical difference-constraint argument already
used by ywz65's [PR #2671](https://github.com/CrocSwap/integer-mult-bounds/pull/2671).
The contribution here is completeness over all common paired lattices in the
anchored class. Decomposition by orthogonal idempotents and the rank-one
ideal calculation are classical ingredients, not new general invariants.
Bellman-Ford takes O(m E) relaxations for E nonzero entries, in addition to
exact rational basis construction and conjugation. This is an arithmetic
operation bound, not a bit-time or fixed-tape tariff.

## An unbounded separation from original-coordinate diagonal gauges

For m=2^k, k>=1, let H be the Sylvester Walsh matrix:

```text
H[x,y]=(-1)^(binary_dot(x,y)),     H^-1=H/m,
P_i=H E_ii H^-1,                 G_i=n_(P_i)=[[I,P_i],[0,I]].
```

For distinct column labels, pairing summands differing in a bit where the
labels differ proves H^T H=mI. Thus the P_i are complete orthogonal rank-one
projectors. Every diagonal entry of every P_i is 1/m. A diagonal similarity
leaves these entries unchanged. No original-coordinate paired-diagonal basis
can therefore make all G_i 2-integral: every projector gives negative self
loops of weight -k.

The non-diagonal paired basis diag(H,H) sends G_i to n_(E_ii), an integral
matrix. The anchored test accepts. This holds in unbounded dimension, beyond
the checked m=2,4,8 examples.

There is no paid-rank saving in this family. The exact rational group-label
identity is

```text
n_(P_m) ... n_(P_1) = n_(sum_i P_i) = n_I.
```

Each paid upper block has rank one. Running this independently on W data
roles costs mW paid rank, with no auxiliary scalar role. This is a literal
rational group-label identity, not an inference from a finite representation
of a formal group algebra. A failed diagonal filter can miss an applicable
obstruction; it is not itself evidence of a saving.

## Existing Borel bound and its boundaries

Only after the source-model premises of
[PR #2613](https://github.com/CrocSwap/integer-mult-bounds/pull/2613) and
[PR #2671](https://github.com/CrocSwap/integer-mult-bounds/pull/2671) are supplied,
the certified basis may be used in their existing rank-functional argument.
Apply the same paired basis to every scalar role. It commutes with scalar
mixing, preserves block-lower free maps, and preserves paid rational ranks.
Unit labels n_I remain exactly n_I. The source's reduction then gives
total paid rank >=mW for W such unit targets, including its permitted finite
scalar workspace. The rank functional, auxiliary allowance and allowance
for singular reductions of free maps retain the source authors' credit.
This package proves the common-lattice premise on a larger decidable class;
it does not re-audit that rank bound or its predecessors.

For a general target, integrality of its transformed HD block does not imply
invertibility modulo two. For example n_(2I) is integral with zero HD block
modulo two. Rational invertibility of an applied matrix likewise does not
imply integrality of its inverse.

The theorem requires one paired lattice shared across scalar roles and a
complete actual rank-one anchor family. Different H/D lattices, role-specific
lattices, non-lattice representations and unanchored inputs are outside its
completeness claim. A failed anchor premise is an unsupported input, not an
impossibility certificate. The complete applied list, legal native/model
operations and a formal word's full endpoint are separate caller obligations.

This analytic basis is not executed or declared free. Physical conversion,
stock, precision, tape movement, native lowering, recursive compiler closure
and analytic recovery remain implementation obligations. No selected supplier
is mapped into this class, and no complete supplier invoice is supplied.
