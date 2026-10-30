# A sharp point-and-line cut obstruction

This scoped proof uses a finite exact certificate on two seven-element sets.
It does not establish the optimum of a multi-target formal word.

## Model

Let `G=GL_3(F_2)`, with `s_ij=I+E_ij`, `i!=j`, at unit price. Matrices act
on column vectors. The ordered generator list is
`(s_01,s_02,s_10,s_12,s_20,s_21)`. Let

```text
        [1 1 1]
g   =   [1 0 1]       binary columns (7,1,3).
        [1 0 0]
```

In `M_R(F_2[G])`, a paid call is `I+([s_ij]+[e])uv^T`, with binary
`v^T u=1`. Any invertible scalar register mixing is free. There are `t>=1`
active roles with targets `[g]` or `[g^-1]`; every other role is an arbitrary
dirty spectator with exact identity output. All off-diagonal outputs vanish.

Use the point set `P=F_2^3\{0}` with action `x -> A x`, or the line set
`L`, labelled by nonzero normal covectors, with action `a -> A^-T a`.
The latter convention makes incidence invariant. Modules may be arbitrary
finite direct sums of these permutation modules. A coordinate cut chooses
any subset of the basis in each summand, identically for every scalar role.

For an address permutation `A` and cut `H`, write

`c_H(A)=#{x in H : A x not in H}`.

This is the rank over `F_2` of the crossing block of the permutation matrix.
The number is unchanged on replacing `A` by `A^-1` or `H` by its complement.

## The finite certificate

On **each** of P and L, every one of the 128 subsets satisfies

`2 c_H(g) <= sum_(i!=j) c_H(s_ij)`.                         (1)

Here is the complete slack histogram for either module. The slack is the
right-hand side minus the left-hand side, without dividing by two.

| Slack | 0 | 2 | 4 | 6 | 8 |
|---|---:|---:|---:|---:|---:|
| Number of subsets | 34 | 46 | 34 | 10 | 4 |

`verify.py` enumerates all subsets and checks (1) with integer arithmetic.
It constructs both actions from all 168 invertible binary matrices, checks
all their composition pairs, and checks line incidence independently of
the inverse-transpose formula. This finite enumeration is the proof of
(1), not a sampled experiment or a numerical optimization claim.

Matching cuts make the upper bound sharp. Label points and covectors by
their binary integers 1 through 7, with coordinate zero the low bit. Take
`H_P={2,4,6}` and `H_L={2,4}`. Their exact profiles are

| Cut | s_01 | s_02 | s_10 | s_12 | s_20 | s_21 | g |
|---|---:|---:|---:|---:|---:|---:|---:|
| H_P on P | 2 | 2 | 0 | 0 | 0 | 0 | 2 |
| H_L on L | 0 | 0 | 1 | 1 | 1 | 1 | 2 |

Weight the first cut by 1/2 and the second by 1. Every paid generator
then has weight exactly 1, and g has weight exactly 3. Equivalently, use
one point copy and two line copies with a single coordinate cut, then
divide all ranks by two.

## Passage to every finite module sum and role count

For a fixed coordinate cut, crossing rank is subadditive under composition.
Indeed `(AB)_(out,in)=A_(out,in)B_(in,in)+A_(out,out)B_(out,in)`, so its
rank is at most the sum of the two crossing ranks. Free scalar register
mixing has zero crossing block. A paid factor has crossing block
`uv^T tensor (s_ij)_(out,in)`, up to the order of tensor factors. Its rank
is exactly `c_H(s_ij)`, since `uv^T` has rank one. At the required diagonal
endpoint the crossing rank is `t c_H(g)`. Every restored spectator adds zero.
This proves the inherited cut inequality for any finite dirty workspace.

Coordinate cuts on a direct sum split across the summands. Their crossing
ranks add, so (1) continues to hold for every allowed module sum. If a
nonnegative combination of these cut inequalities has paid-generator
coefficients `b_ij<=1`, its endpoint coefficient is at most

`(t/2) sum_(i!=j) b_ij <= 3t`.                             (2)

The two matching cuts attain `3t`. Thus the complete normalized cone of
the declared coordinate-cut inequalities has **exact value 3t**, for
every t and every choice of target orientations. Taking more copies,
more coordinate cuts, or more dirty roles cannot improve this value.
No linear-program solver is needed to verify the upper or lower certificate.

## Comparison with the direct bill

In chronological execution order, the four labels
`s_01,s_02,s_10,s_21` have product `s_21 s_10 s_02 s_01=g`. Direct execution
on each active coordinate therefore costs `4t`, restoring all spectators.
The full group-algebra verifier checks this endpoint for t=1,2,3, including
all omitted-call controls and dirty-coupling detours. The Cayley traversal
also finds that g has distance four. The inverse has the reversed word.

For a single target, every formal coefficient in a k-paid-call word is
supported on products of at most k paid address labels, even with free
scalar mixing and dirty roles. The coefficient `[g]` therefore requires
at least four calls. This standard support argument, already used in
JoyboyBrian's PR #4974, is not a new contribution here. The new certificate
shows that the specified point-and-line cut cone stops at three even in
this singleton case. For multiple targets, **4t is a direct upper bound**;
this package does not claim an all-workspace lower bound of 4t.

## Limits

Arbitrary subspace cuts, modules other than finite sums of P and L,
role-dependent cuts, nonlinear or integer-combined invariants and different
paid alphabets are outside (2). In particular the full regular module is
not a sum of these two modules as a permutation module. The theorem neither
constructs shared paid work nor excludes it. Native implementation,
compiler/hosting/precision invoices, recursive suppliers and the complete
multiplication theorem remain unproved here. No proof-kernel or independent
human review is claimed.
