# A half-call scalar-core bound for negative Q8 endpoints

Work over the full formal group algebra F2[Q8], with
`Q8={1,i,j,k,z,zi,zj,zk}`, `i^2=j^2=z`, `z^2=1`, and `ji=z ij`.
The symbols z and 1 are distinct. Paid factors have the form

```text
D_l = I + ([g_l]+1) u_l v_l^T,    g_l in {i,j},    v_l^T u_l=1.
```

The vectors are binary. Binary scalar GL mixing is free. Every role has
arbitrary independent dirty input, and identity-target roles must restore it.
Suppose the diagonal endpoint has t targets in {zi,zj} and identity elsewhere.
Let X have columns u_l, let Y have rows v_l^T, and set A=YX for n paid calls.
Call zero acts first, so the endpoint is D_(n-1)...D_0.

**Theorem.** Every such normalized word satisfies `2 rank(A)<=n`. Its
simultaneous scalar core therefore has at most `floor(n/2)` roles, including
the t active targets. In particular its essential dirty dimension is at most
`floor(n/2)-t`. This is a written all-finite-workspace theorem. The executable
controls have explicit finite bounds and do not replace its proof.

**Computer-assisted corollary.** Exactly three negative targets require
exactly nine positive i/j calls with any finite restored dirty workspace.
The new theorem transports the retained PR3471 three-role exclusion through
seven calls to arbitrary workspace. The finite premise is replayed here with
its original implementation and a separate complete Hamilton implementation.
No physical supplier or multiplication-exponent improvement follows.

## 1. Normalization, first-order coefficient and scalar core

The normalization and simultaneous core are Nick Petalas's PR3517 results,
retained unchanged in `inputs/pr3517-PROOF.md`. We restate the needed proof.
Conjugate each paid projector by its accumulated binary scalar mixing.
Augmentation sends every paid factor and the diagonal group endpoint to I,
so the final residual scalar factor is I. This preserves all ordered labels.

In the first-order quotient, write `[i]=1+x`, `[j]=1+y`, and discard all
degree-two monomials. The negative generators have the same first-order
coefficients as their positive counterparts. Equating the x and y coefficients
gives the active coordinate projectors P_i and P_j. In particular

```text
XY=P=P_i+P_j,    rank(P)=t,    tr(P)=t mod 2.
```

Every projector has trace one. Taking the trace of `XY=sum_l u_l v_l^T`
gives `n=t mod 2`. This uses arbitrary dirty inputs, without setting them zero.

Put `U=im X`, `K=ker Y`. Every factor preserves U and fixes K pointwise.
The coefficient of zi or zj in the endpoint minus I is the corresponding
coordinate projector. Its image lies in U, and it kills K. Thus the active
coordinate subspace E lies in U, and K lies in the restored coordinate subspace D.
Consequently

```text
C=U/(U intersect K)
```

retains every active target and only restored dirty directions besides them.
Its dimension is rank(YX), since Y maps U onto im(YX) with kernel U intersect K.
The induced rank-one projector remains nonzero and idempotent because
`v_l^T u_l=1`. Hence the ordered paid word is legal on C. A binary basis
separates E from its dirty quotient and restores every remaining input.
No transpose of a noncommutative coefficient matrix is used. This establishes
the core statement and `rank(A)>=t`.

## 2. A five-dimensional algebra that distinguishes the negative sign

Define a binary algebra B with basis `1,x,y,tau,q`. The element 1 is its unit.
The nonzero products of positive-degree basis elements are exactly

```text
x*x=tau,    y*y=tau,    x*y=q,    y*x=q+tau.
```

All products involving tau or q and a positive-degree element vanish. Every
product of three positive-degree elements is zero, so these rules are
associative. The elements `1+x` and `1+y` square to `1+tau`, whose square is 1.
Also `(1+y)(1+x)=(1+tau)(1+x)(1+y)`. These relations define a homomorphism
from F2[Q8] to B by `[i] -> 1+x`, `[j] -> 1+y`, `[z] -> 1+tau`.
Equivalently this is the degree-two augmentation quotient. Only the explicit
homomorphism is needed, so no assertion about the augmentation ideal's
complete associated graded algebra is required.

In particular

```text
[zi] -> 1+x+tau,       [zj] -> 1+y+tau.
```

The tau coefficient of the target is therefore P. The same coefficient would
be zero on a positive generator. This is the sign-sensitive step absent from
the earlier first-order core bound.

## 3. Chronology makes the central coefficient strictly triangular

Let H be the n-by-n binary matrix defined by

```text
H[b,a] = A[b,a] * c(g_b,g_a)  if b>a, and 0 otherwise,
c(i,i)=c(j,j)=c(j,i)=1,       c(i,j)=0.
```

The table c is the tau coefficient of the product of the corresponding
increments x or y in B. There is no quadratic contribution from a single
paid factor, and every triple product vanishes. The tau coefficient of the
chronological word is therefore

```text
sum_(b>a) c(g_b,g_a) u_b (v_b^T u_a) v_a^T = X H Y.
```

Equating this with the negative endpoint gives `XHY=P=XY`. Multiplying on
the left by Y and on the right by X gives

```text
A H A = A^2,        A (I+H) A = 0.
```

H is strictly lower triangular, so H^n=0 and I+H is invertible. The image
of `(I+H)A` is contained in ker A, and has dimension rank A. Rank-nullity
therefore gives `rank A <= n-rank A`, proving the theorem. This implication
requires no enumeration, solver assumption or restriction on n or workspace.

## 4. Resolving the three-negative handoff

For t=3, the rank bound gives n>=6 and trace parity makes n odd. A hypothetical
word with fewer than nine calls must therefore have n=7. Its core has at least
three and at most floor(7/2)=3 roles. There is no essential dirty direction.
Permutation of the targets and the automorphism interchanging i and j reduce
all eight ordered target lists to shapes `(3,0)` and `(2,1)`.

PR3471 certifies that neither `diag(zi,zi,zi)` nor `diag(zi,zi,zj)` has a
three-role word through seven paid calls. Here the retained source runs only
that query, with a separate positive query. The three-role alphabet contains
all 56 positive i/j rank-one idempotent factors. Every scalar mixing is already
absorbed into those projectors. Build the inverse ball through three calls and
the positive prefix ball through three calls. Each has 91,955 distinct matrices.
For each prefix test it and every one-factor extension, giving 5,241,435
candidate occurrences. Test membership in each inverse-ball-times-target set.
Any word of length at most seven has a split with a left part through three
calls and a right part through four calls, so zero hits excludes every such
word. Duplicate candidates do not remove coverage. Both targets have zero hits.

The retained implementation uses full formal group packets and right matrix
multiplication. The independent implementation uses fixed Hamilton left/right
permutations and imports none of its algebra. It regenerates both complete
balls byte for byte after explicit encoding conversion, then repeats the full
5,241,435-occurrence membership query. This adds an independent full query to
the earlier finite premise; it does not expand its role or length domain.

Three repetitions of each target's underlying positive generator on its own
coordinate attain zi or zj. Applying these nine factors to the three active
coordinates and leaving all other coordinates untouched gives the matching
uniform upper bound. Every identity-target input stays arbitrary and restored.

## Limits and credit

The written half-call bound is uniform in n and finite workspace. The exact
triple minimum combines it with a complete finite computation. Independent
human and formal proof-kernel review are unclaimed. No four-negative minimum,
full signed-label tariff, native bit conversion, actual physical caller, scalar
preparation invoice, complete supplier, new kappa or selected-frontier update
is established.

Nick Petalas/PR3517 retains the simultaneous core and ordered-call Gram method;
PR3471 retains the exact three-role exclusion, and PR3525 the independent n3/n5
censuses and explicit seven-call handoff. The new result is the sign-sensitive
triangular coefficient and its stronger core bound. The degree-two quotient
uses the standard Q8 relations, also considered in the earlier central-minus-one
discussion. Tuafo/PR2900 retains image restriction, ywz65/PR2587 coefficient
support/Sylvester and first-order methods, and PR3487 the common-kernel quotient.
Aaron Wang/PR2318, Cinna Davis, steph4n-gh and the retained register-model lineage
keep their original credit. Arham Tahir/PR3137 and PR3461 address separate
physical/scalar costs. All retained source notices are unchanged.
