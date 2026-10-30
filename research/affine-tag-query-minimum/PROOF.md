# Sharp oracle cost of affine native tag membership

This scoped proof was produced by Nick Petalas. Quadratic interpolation and
binary nullspace elimination are classical. The contribution is the exact
decision cost with unknown constant and even-linear tags, including an
adversary for arbitrary adaptive query choices.

## Statement and oracle model

Fix any positive integer n, a known invertible binary matrix A, and a known
binary offset b. The oracle returns exact values in Z/4 of a function promised
to have the form

```text
q(x) = q0 + sum_i a_i x_i + 2 sum_(i<j) h_ij x_i x_j modulo 4,
q0,a_i in Z/4, h_ij in F2, x in F2^n.
```

The matrix, offset and promise are available without oracle queries. Polynomial
coefficients are not available. A query specifies any binary address and returns
its phase exponent. Algorithms may choose later addresses from earlier answers.
The decision must be correct on every promised oracle. The complexity is the
worst-case number of queries of a deterministic algorithm. Neither arithmetic
cost nor tensor-width identity testing is the quantity being optimized.

Let `D|x> = i^wt(x)|x>`, `F(x)=Ax+b`, and `J_F=D P_F D^-1`. The question is
whether there are a constant `c in Z/4` and mask `t in F2^n` such that

```text
i^q(x)|F(x)> = i^c J_F Z_t |x>    for every x.
```

The answer can be decided, and the unique c,t recovered on acceptance, with
exactly

```text
d(n) = 1 + n + binom(n,2) = 1 + n(n+1)/2
```

queries in the worst case. Every deterministic adaptive decision algorithm
requires at least d(n) queries. In particular d(9)=46, whereas the cube has
512 points. This is a query count, not a measured speedup or a physical saving.

## Reduction to an even-linear residual

Write `r_A,b(x)=wt(Ax+b)-wt(x) modulo 4`. If row j of A has entries A_ji, then
the parity expansion modulo four gives

```text
(Ax+b)_j = b_j + (1-2b_j) sum_i A_ji x_i
                 - 2 sum_(i<k) A_ji A_jk x_i x_k modulo 4.
```

Terms of degree at least three have coefficients divisible by four. The sign
of the quadratic term is immaterial modulo four. Thus r_A,b belongs to the
same promised quadratic class. That class is closed under subtraction.

Set `R=q-r_A,b`. The requested identity is exactly

```text
R(x) = c + 2(t dot x) modulo 4.
```

Since twice binary parity equals twice the ordinary sum modulo four, these
are precisely the residual polynomials with even linear coefficients and
zero quadratic coefficients. Every coefficient in the promised class is
unique as a function: its constant is determined at zero, its linear
coefficients at the unit vectors, and its doubled quadratic coefficients by
the pair differences. The constant and mask c,t are therefore unique too.

## Upper bound

Query q, hence R, on zero, every unit vector e_i, and every e_i+e_j with i<j.
There are d(n) distinct addresses. Compute

```text
c = R(0),
delta_i = R(e_i)-c modulo 4,
gamma_ij = R(e_i+e_j)-R(e_i)-R(e_j)+c modulo 4.
```

Accept exactly when every delta_i is even and every gamma_ij is zero. These
are exactly the required coefficient conditions. On acceptance return
`t_i=delta_i/2`. The polynomial promise extends these conditions to every
address. The implementation uses equivalent pair comparisons after recovering
t; it queries each address once.

## Lower bound with arbitrary adaptive choices

Run any correct deterministic algorithm on the accepted oracle `q=r_A,b`,
whose residual R is identically zero. Suppose it stops after m<d(n) queries.
Let S be the set of queried addresses; repeated queries do not add information.
We construct a promised residual R* that vanishes on S but is outside the
accepted family. Then `q*=r_A,b+R*` supplies exactly the same transcript.
Determinism forces the same later queries and the same acceptance, which is
incorrect. This proves the worst-case lower bound once the construction is
given.

If S does not affinely span F2^n, choose a nonzero mask v whose binary linear
functional is constant, say k, on S. Empty S allows any nonzero v and k=0.
Take

```text
R*(x) = (v dot x as a bit) - k modulo 4.
```

This is a promised polynomial because binary parity has the expansion
`sum_i v_i x_i - 2 sum_(i<j) v_i v_j x_i x_j modulo 4`.
It vanishes on S. Its parity is nonconstant, whereas the parity of every
accepted `c+2(t dot x)` is constant. Hence it is outside the accepted family.

If S does affinely span F2^n, consider binary square-free polynomials of
degree at most two. They have dimension d(n), with basis 1, x_i, x_i x_j.
Evaluation on S has at most |S|<d(n) rows, so its kernel contains a nonzero
polynomial f. Full affine span implies that no nonzero affine polynomial
vanishes on S. Consequently f has a nonzero quadratic coefficient. Set

```text
R*(x) = 2 f(x) modulo 4.
```

Twice a binary polynomial equals twice its ordinary coefficient sum modulo
four. R* is promised, vanishes on S, and has a nonzero doubled quadratic
coefficient. Uniqueness of the square-free coefficient representation makes
it impossible for R* to be an accepted even-linear residual.

These cases cover every S and prove the lower bound. The executable
`adversary` constructs v or f by binary elimination, without searching
possible adaptive algorithms. The transcript argument handles adaptivity.

## Essential boundaries

The quadratic promise cannot be inferred from the d(n) samples. For n=3,
`q(x)=2 x1 x2 x3` with A=I,b=0 vanishes on every queried address but is nonzero
at 111. It is outside the promised class. The implementation intentionally
accepts its sampled values in a limitation control.

The theorem assumes that the affine permutation is known. It does not certify
the permutation, arbitrary serialized gate semantics, nonmonomial children,
general tensor linear combinations, or physical routing/restoration costs.
It does not give a lower bound for algorithms that inspect polynomial
coefficients directly, randomized bounded-error tests, or quantum queries.
It supplies no new kappa or complete multiplication theorem.

JoyboyBrian's [PR6106 at its exact head](https://github.com/CrocSwap/integer-mult-bounds/blob/9d0126c134720258cfe685b661ce288da01008fa/research/native-affine-phase-tags/README.md)
supplies the affine tag convention and explicitly warns that coordinate
evaluations alone cannot establish that a general quadratic residual is
linear. Its actual warp/inverse result is cited, not replayed here.
ToikY's [PR4002 proof](../native-lift-phase-tags/PROOF.md) supplies the normalized
linear lift and retains Chris R / Clear1nsight's PR3987 and the native lineage.
Ali Romman's [native tensor criterion](../native-tensor-cutoff/PROOF.md) concerns
fixed group-algebra identities across tensor widths, a different decision
problem. No predecessor result is claimed as a new theorem here.
