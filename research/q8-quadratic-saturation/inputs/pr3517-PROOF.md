# The scalar core and call Gram matrix

Work over the full formal group algebra F2[G]. A chronological paid sequence
has factors `D_l=I+([a_l]+1)u_l v_l^T`, with binary vectors and `v_l^T u_l=1`.
Only binary scalar GL mixing is free. Every role has arbitrary independent
dirty input. A diagonal identity-target role must restore that input.
Interleaved scalar mixing normalizes by conjugation; augmentation forces
the final scalar factor to be identity at a diagonal group endpoint.

Let X have the n columns u_l, Y have the n rows v_l^T, and `A=YX`.
Factor order is part of the data. In code, gate zero acts first, so the
endpoint is `D_(n-1) ... D_0`. The theorem uses this same convention.

## Exact simultaneous reduction

Put `U=im X` and `K=ker Y`. Every paid projector preserves U and kills K.
It therefore descends to

```text
C = U / (U intersect K),       dim C = rank(YX).
```

The induced projector is still rank one and idempotent. Indeed u_l belongs
to U and cannot belong to K, since its l-th Y coordinate is `v_l^T u_l=1`.
The quotient map commutes with every ordered factor and every formal group
coefficient. This argument does not transpose noncommutative matrices.

Suppose the original endpoint is diagonal, with active coordinate space E
for nonidentity targets and restored dirty coordinate space D. Expanding
the product shows that the image of each coefficient of `T-I` lies in U.
The coefficient at any nonidentity group element is its target-coordinate
projector. Thus `E subset U`. Every factor fixes K, so the same projectors
kill K and `K subset D`. Consequently

```text
C = E direct_sum ((U intersect D) / (U intersect K)).
```

The induced endpoint retains the identical active targets and identity on
the remaining dirty roles. No clean initialization or discarded dirty
output is used. Restriction and quotient may discard intermediate traffic,
but their legitimacy follows from full restoration at the endpoint.

This combines PR3487's two separate reductions. It can be strictly smaller
than both. With three roles, repeat the chronological pair
`(i,e1,(1,1,0))`, `(i,e2,(1,1,1))` four times. Here a tuple names label,u,v.
The eight-call endpoint is identity in full F2[Q8]. Both X and Y have rank
two, while A is the eight-by-eight all-ones matrix of rank one. The core
retains all eight calls on one dirty role. The endpoint itself also has an
empty implementation; this example compares reductions of the fixed call
sequence, not shortest implementations.

## A complete invariant for the reduced ordered sequence

The map `x -> Yx` identifies C with `im A` in F2^n. On that space the l-th
projector is exactly

```text
Q_l = A e_l e_l^T restricted to im A.
```

Its image vector is `A e_l`; its covector reads coordinate l. The diagonal
condition `A_ll=1` makes it a legal rank-one idempotent.

Conversely, every binary n-by-n A with diagonal one realizes such a reduced
sequence, for any ordered labels. Choose any rank factorization `A=BC`,
where B is injective and C is onto, of inner dimension `r=rank A`.
Take X=C, Y=B. The l-th paid gate uses column l of C and row l of B.
Its Gram matrix is A, and its scalar space has dimension r.

Any two such rank factorizations differ by a unique scalar GL_r change.
Indeed `ker C=ker A`; hence `SC=C'` defines an invertible S uniquely, and
`B'=BS^-1` follows from `BC=B'C'` and surjectivity of C'. Thus A together
with the ordered labels classifies reduced gate sequences up to scalar
basis change. Rank A is the smallest dimension of a factorization with
this same Gram matrix. This does not claim that endpoint-equivalent words
have the same A, nor that rank A is their minimum possible workspace.

The reachable/observable quotient and rank-factorization uniqueness are
standard linear algebra. The contribution here is this ordered-call
application, its strict reduction, and the exact Q8 endpoint criterion below.

## Character and essential dirty roles

Suppose a binary character chi sends every paid label to one. The ring map
`[g] -> 1+chi(g)*epsilon`, with epsilon squared zero, gives `XY=P`, where
P is the odd-target coordinate projector of rank t. Therefore

```text
A^3 = Y P^2 X = Y P X = A^2,       rank(A^2)=t.
```

Taking binary traces of `XY=P` also gives `n=t mod 2`, since every paid
rank-one idempotent has trace one.

For the rank claim, PX maps onto the odd active coordinates, and Y is
injective there because `XY e=e`. The matrix A squared is a projection.
On its image A is identity. On its kernel A squared is zero. If the latter
restriction has rank b, choose a basis of its image, preimages of that
basis, and remaining kernel vectors. This gives t identity blocks, b
nilpotent blocks of size two, and c zero blocks of size one. Hence

```text
rank A = t+b,        n=t+2b+c,        b,c nonnegative integers.
```

At Q8 diagonal endpoints consisting of generator targets and identities,
t is the active target count. The core has exactly b remaining dirty roles.
The inherited bound `rank A <= floor((n+t)/2)` follows. This restatement
does not strengthen PR3487's uniform numerical bound, but identifies the
actual core and its nilpotent dirty part without choosing a role basis.

## Exact all-negative Q8 candidate criterion

Set `G=Q8`, with central `z=i^2=j^2`, and positive paid labels i,j only.
The group symbols z and 1 remain distinct. Fix n, an ordered label list,
and desired negative-target counts s_i,s_j. Let A be binary with diagonal
one, let `V=im A`, and form the ambient n-role gates

```text
Q_l = A e_l e_l^T,
L_i = sum_(a_l=i) Q_l = A E_i,    L_j=A E_j,
Z_i=L_i A,                       Z_j=L_j A.
```

Here E_i,E_j are the complementary diagonal selectors of call indices.
Let T be the full formal endpoint of these ambient gates, in chronological
order. The following binary and full-group-coefficient equations are
necessary and sufficient for an n-call word with exactly s_i targets zi,
s_j targets zj and any finite number of restored dirty roles:

```text
rank Z_i=s_i,       rank Z_j=s_j,
L_i Z_i=Z_i,       L_j Z_j=Z_j,
L_i Z_j=0,         L_j Z_i=0,
T A = A + ([zi]+1) Z_i + ([zj]+1) Z_j.
```

Necessity follows by reducing any such word to its core. The separate
first-order i,j characters identify `L_i|V` and `L_j|V` with the two target
projectors. Every equation above is their equality tested on `V=im A`.

For sufficiency, the four binary equations make `L_i|V,L_j|V` orthogonal
projections with the stated ranks. Their images and their common kernel
give a direct-sum basis of V. The formal equation makes T multiplication
by zi and zj on the respective images and identity on that common kernel.
The ambient gates restrict legally to V. Conjugating by this binary basis
therefore gives the required diagonal endpoint on rank A roles. All dirt
is restored. The equations test all eight formal coefficients, including
central and mixed coefficients which first-order tests would miss.

`gram.py` checks a concrete candidate. `system.py` exports the same equations
as QF_BV SMT-LIB with variable ordered labels and a symbolic binary-rank
elimination circuit. It imports no solver. At n=7 there are 42 free Gram
entries after the diagonal constraints and seven binary label choices.
That is a parameter count before the endpoint equations, not a census or
an execution-time claim.

## What remains unsolved

For three negative targets, generator interchange and target permutation
leave shapes `(s_i,s_j)=(3,0)` and `(2,1)`. A direct construction takes nine
calls. Trace parity and the first-order rank floor leave possible cheaper
lengths 3,5,7. The exporter describes each exact length, without padding
one length into another. Excluding only seven calls would not itself
exclude five. At seven calls the spectral decomposition permits core
dimensions three, four or five; the two dirty nilpotent blocks in the
five-role case remain a concrete open obligation.

Both bounded seven-call Z3 probes returned unknown because of timeout.
They supply no exclusion and no evidence of optimality. No three-negative
arbitrary-workspace minimum, physical conversion, caller, complete supplier
invoice, multiplication theorem, kappa improvement or selected-frontier
change is claimed. Independent human and formal proof-kernel review are
unclaimed.

Credit Tuafo/PR2900 for image restriction, ywz65/PR2587 for coefficient
support and Sylvester, and Nick Petalas/PR3487 for the common-kernel
quotient and two-sided bound. The exact predecessor proof is retained
unchanged with source identities in inputs/RETENTION.json. PR3471 and
PR3499 retain finite-minimum and weighted-frontier credit. Aaron Wang/PR2318,
PR3450/3460, Cinna Davis, steph4n-gh and the register-model lineage retain
their attribution recorded there. Arham Tahir/PR3137's physical compiler
and PR3461's scalar preparation have separate costs.
