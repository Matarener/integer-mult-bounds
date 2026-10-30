# Reduce coupled tensor frames to one copy

This is a theorem about recursive rank moments on a fixed contact graph.
It does not give a new kappa, a minimum for the current P104 graph, or a
complete native implementation. All spaces below are over F2.

## 1. Contract and statement

Fix positive integers d and m. Put V = F2^d and H = V^m. Fix a finite graph
with nonnegative edge weights w_e. Each vertex has one Clifford preimage
Lagrangian in H plus H. Identify vertices which must have one common chart
at a scalar operation. All scalar operations, coefficients and fields stay
fixed. Each edge represents a paid transition. Its Fourier rank is

```math
r_e=dm-\dim(L_a\cap L_b).
```

At every fixed boundary vertex prescribe the canonical Lagrangian of
U_v^m, where U_v is a fixed subspace of V. This includes both ends of each
productive target. Internal Lagrangians can be arbitrary and can couple
the m copies. There is no fixed native operator equation across an edge.

Let phi be increasing and concave on [0,d], with phi(0)=0. Then there is
one assignment of subspaces A_v of V, with the same boundary spaces and
common-contact equalities, for which

```math
\sum_e w_e\,\phi\bigl(d_S(A_a,A_b)\bigr)
\ \leq\ \sum_e w_e\,\phi(r_e/m),
\qquad
d_S(A,B)=\dim A+\dim B-2\dim(A\cap B).
```

One assignment is used for the whole graph. A different choice for each
edge would not prove this statement. For phi(x)=x^t, 0<t<=1, the right
side is the coupled paid moment divided by m^t.

The boundary target ranks are m times their ranks in one copy. Thus their
power moment, divided by m^t, is the same constant for all assignments.
The same comparison holds after this fixed target credit is subtracted.
The optimum in this rank-moment model is therefore unchanged by tensor
coupling or general Clifford frames. The reverse inequality follows by
taking the direct sum of m copies of any assignment in V.

This equality of optima is for each stated tariff separately. The selected
assignment need not be the same at different exponents.

## 2. The inherited projection inequality

Use the convention from `notes/general-clifford-frames.tex`. The canonical
Lagrangian of a subspace S of H is

```math
\mathcal L_S=\{(u,u+z):u\in S,\ z\in S^\perp\}.
```

It has dimension dm and projects onto S in the first coordinate. Direct
intersection gives

```math
dm-\dim(\mathcal L_S\cap\mathcal L_T)=d_S(S,T).
```

The following projection inequality is prior work. Cinna Davis's
[PR5140 proof, exact head 1d1b593168a36ee524300752a5e33f6cd7a08314](https://github.com/1337isnot1337/integer-mult-bounds/blob/1d1b593168a36ee524300752a5e33f6cd7a08314/research/monotone-owned-centre-floor/PROOF.md)
uses it for an owned-wire floor. Its short argument is included to state
the conventions used by the new tensor reduction.

For any Lagrangian L, let S be its first-coordinate projection. Isotropy
and dimension give

```math
L\cap(0\oplus H)=0\oplus S^\perp.
```

For L and M with projections S and T, the projection of their intersection
is contained in S intersect T. Its vertical kernel is contained in
0 plus (S+T)-perp. Rank-nullity therefore gives

```math
\dim(L\cap M)\leq\dim(S\cap T)+dm-\dim(S+T).
```

Consequently r(L,M)>=d_S(S,T). Replacement by canonical projected charts
cannot increase any paid rank. It fixes every prescribed canonical boundary
and preserves common-contact equalities. This step does not use a new
phase identity or declare its adapters free.

## 3. Split the projected spaces with one coordinate flag

Let H_j contain the first j copies of V, with H_0=0. For each S in H put

```math
S_j=\pi_j(S\cap H_j)\ \subseteq V,
```

where pi_j is projection onto copy j. Its kernel on S intersect H_j is
S intersect H_(j-1). Thus

```math
\dim S=\sum_{j=1}^m\dim S_j.
```

Apply this construction to S intersect T. Its j-th image is contained in
S_j intersect T_j. Therefore

```math
\dim(S\cap T)\leq\sum_j\dim(S_j\cap T_j),
\qquad
\sum_j d_S(S_j,T_j)\leq d_S(S,T).
```

Both inequalities are in the required direction. Ordinary projection of
S onto each copy would be wrong: the line spanned by (1,1) has dimension
one, but both ordinary projections have dimension one. Intersection with
the coordinate prefix is required.

The same flag is used at every vertex. Equal spaces give equal images.
Containment is also preserved if a model imposes it on projected spaces.
For S=U^m each image S_j is exactly U. Thus every candidate copy has all
the prescribed boundaries. The images in this argument need not have
equal dimensions at internal vertices.

## 4. One copy for the complete moment

For edge e let r_(e,j) be the distance between its two j-th spaces. The
two preceding bounds give sum_j r_(e,j)<=r_e. Concavity and monotonicity
give

```math
\frac1m\sum_j\phi(r_{e,j})
\leq\phi\left(\frac1m\sum_j r_{e,j}\right)
\leq\phi(r_e/m).
```

Multiply by w_e and sum. At least one copy j has its entire graph cost
at most the average of the m graph costs. This proves the statement.
The proof applies to every finite d, every positive m, and every finite
graph. It is not an extrapolation from the finite checks.

For a power tariff, a productive boundary pair U,W has coupled rank
m*d_S(U,W). Its normalized credit is therefore d_S(U,W)^t. It is fixed
and can be subtracted after the paid-cost comparison. If productive
boundaries can vary, their negative terms need not satisfy the comparison.

## 5. Relation to a physical scalar word

The usual common-chart invariant writes each field as its chart operator
applied to a scalar row of logical inputs. The scalar rows do not change
when the chart assignment changes. Common-contact equalities are preserved
by both steps above. Choose identical exact chart representatives at each
contact and retain the prescribed representatives at the boundaries.

Under the repository's Clifford factorization premise, each new transition
can be represented by a child of its relative Fourier rank and two
rank-zero adapters. This explains the rank graph used in the statement.
It does not bound the added scalar, movement, precision or tape work. No
new native phases or all-column recipes are emitted by this package.

A fixed native operator relation, a prescribed phase form at an internal
vertex, or a restricted adapter alphabet can fail to survive projection.
Such a constraint is outside the graph contract unless it is separately
proved to survive. Likewise the proof does not permit a cross-frame ADD
to be counted as a common-chart scalar ADD.

## 6. Evidence and limits

The standard-library checker uses binary elimination and a separate
explicit-set oracle for the coordinate-flag construction and its distances.
It checks all subspace pairs in four small tensor layouts, all Lagrangian
pairs through dimension three, and a declared sample at dimension four.
It also checks exact concave hinge tariffs and a common-copy choice on
complete weighted graph fixtures. `RESULT.json` states the exact coverage.

Controls retain the failed ordinary-projection rule, incompatible boundary
copies, nonisotropic frames, different choices on different edges, convex
tariffs, variable negative target credits, and tensor normalization. These
are checks of the hypotheses and arithmetic. They are not a proof-kernel
verification or an independent scientific review.

The two-copy P104 discovery screens which led to this question are not
premises. Their floating cuts and optimizer statuses do not enter this
proof. No global optimum for P104 in one copy is claimed. Changed scalar
words, extra observations, productive splits, new geometry, changed native
constraints and complete caller construction remain separate questions.
