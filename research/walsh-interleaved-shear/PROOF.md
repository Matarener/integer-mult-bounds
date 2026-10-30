# A sharp error bound for one interleaved integer shear

Jerry Chen (@CubeJerry), with substantial OpenAI Codex assistance. Apache-2.0.

## Exact statement and conventions

Let h > 0, m be any integer, and t,s be distinct elements of {0,1,2,3}.
Let R round a real number to its nearest integer, with ties to the even integer,
and apply it componentwise. Coordinates are numbered by their binary indices.
Define the two **normalized** real Walsh factors

```
A = (1/2) [[1, 1, 0, 0],       B = (1/2) [[1, 0, 1, 0],
           [1,-1, 0, 0],                  [0, 1, 0, 1],
           [0, 0, 1, 1],                  [1, 0,-1, 0],
           [0, 0, 1,-1]]                  [0, 1, 0,-1]].
```

Let S = I + m e_t e_s^T. In grid units the literal program is

```
y = R(Ax);  z = S y;  F_m(x) = R(Bz),       x in Z^4.
```

The shear is exact on this integer grid. Rounding after it would be the
identity. Both values in each butterfly are read before either is written.
The **exact comparison operator includes the same shear**: T_m = B S A.
Then, for each of the twelve ordered pairs (t,s),

```
sup_(x in Z^4) ||F_m(x) - T_m x||_infinity = (|m|+3)/4.       (1)
```

For inputs on h Z, multiply the right side by h. Reversing the two axes
preserves (1), by conjugating all coordinates and the shear by the permutation
(1 2). Independent spectator fibers preserve the bound when the shear is
within a fiber. Cross-fiber shears are not asserted here.

For m=0, (1) recovers Nick Petalas's PR6129 value a_2=3/4. For every nonzero
integer m, that unsheared value is exceeded. This answers the two-stage,
integer-shear instance of Josie Elliston's explicit PR6140 open question.
Neither predecessor claimed that its theorem covered interleaved gates.

## Upper bound for all inputs and all integer coefficients

Scale h to one. Put delta = y - Ax. Every component of Ax is a half integer,
so each delta_i belongs to {-1/2,0,1/2}. A crucial implication is

```
delta_i != 0  =>  y_i is even.                            (2)
```

This is the nearest-even tie rule. Let eta = R(B S y) - B S y.
Every component of S y is an integer, so eta_i is again 0 or +/-1/2.
The error is exactly

```
F_m(x) - T_m x = B S delta + eta.                       (3)
```

An unaffected output combines the first errors of one second-stage pair
with signs and a factor 1/2. If eta_i=0, its absolute error is at most 1/2.
If eta_i!=0, the two stored inputs have odd sum/difference. They cannot both
be even, so (2) implies that at least one of their first errors is zero.
The error is then at most 1/4+1/2=3/4.

For an affected output let p=t xor 2 be t's partner in B. Its propagated
first error has the form

```
(alpha delta_t + beta delta_p + alpha m delta_s)/2,
alpha,beta in {+1,-1}.
```

The two signs are the actual row signs of B; no independence of delta terms
is assumed. The source may equal p, in which case terms refer to the same
error and the triangle inequality remains valid.

First suppose |m|>=1. If eta_i=0, the absolute total error is at most
(|m|+2)/4, which is smaller than (1). If eta_i!=0, at least one of
**delta_t, delta_p, delta_s is zero**. Otherwise (2) would make all of
 y_t, y_p, y_s even; y_t+m y_s and y_p would be even, forcing eta_i=0.
Removing any one of these three terms decreases the triangle bound by at
least 1/2 before the outer division: its weight is either 1 or |m|>=1.
Therefore

```
|error_i| <= (|m|+1)/4 + 1/2 = (|m|+3)/4.
```

If the same variable appears twice, its vanishing removes both terms and
only strengthens this estimate. For m=0 there are just two relevant terms;
the unaffected-output argument gives 3/4. This proves the upper bound
without a bounded search, residue assumption or inherited Walsh recurrence.

## Attainment by fixed small inputs

[WITNESSES.json](WITNESSES.json) has two rows per (t,s), one for each
c in {-1,+1}. A row records (t,s,c,j,x0,x1,x2,x3), with x in {-1,0,1}^4.
Each row satisfies three exact identities:

```
(R(Ax))_s = 0,
4(F_0(x)_j - (T_0 x)_j) = 3,
4((T_0 - T_1)x)_j = c.                                (4)
```

Because the stored shear source is zero, **F_m(x)=F_0(x) for every m**.
The exact operator is affine in m. Hence (4) proves the identity

```
4(F_m(x)_j - (T_m x)_j) = 3 + c m                    (all integer m).
```

For nonzero m choose c=sign(m); either sign works for m=0. This attains (1).
The 24 finite identities in (4), combined with this algebraic argument,
prove attainment for the unbounded coefficient domain. They are checked
using explicit dense matrices and exact Fraction rounding, independently of
the loop-based integer butterfly interpreter. The certificate is not a claim
that a finite coefficient sweep alone proves (1).

For example, take t=0, s=1, m=-1 and x=(0,-1,-1,-1). The first stored vector
is (0,0,-1,0), so the shear leaves it unchanged and F_m(x)=(0,0,0,0).
The exact output is (-1,1/4,0,1/4), giving error exactly 1. Removing the
shear yields exact output (-3/4,1/4,1/4,1/4) and error 3/4.
At h=1/4 the input is (0,-1/4,-1/4,-1/4), and the two sharp errors are
1/4 and 3/16 respectively. This is a changed four-coordinate program;
it is not a defect in CubeJerry's unchanged PR6119 surrogate.

## Why the finite corroboration is complete in its stated domain

Two elementary reductions make the secondary census meaningful:

1. **Input period eight.** Replace x by x+8v with arbitrary integer v.
   The first exact displacement 8Av has coordinates divisible by four.
   Since R(u+2k)=R(u)+2k, the stored displacement is exactly 8Av.
   The integer shear preserves divisibility by four. After B the displacement
   has even coordinates, so the second rounding also commutes with it.
   Thus F_m(x+8v)-T_m(x+8v)=F_m(x)-T_m x for every integer m.
2. **Coefficient residues modulo four.** At fixed x, replace m=r by r+4q.
   The pre-final-round displacement is 4q B e_t y_s, whose components are
   even integers. The rounded output shifts by this exact displacement.
   Consequently four-times the error in output j changes by 4q c_j, where
   c_j = 4 B[j,t] delta_s is in {-1,0,1}. Thus it is an affine function
   c_j m + a_j within each coefficient residue class.

The verifier compares **both complete output vectors and the first stored
vector** between its two engines for all 8^4 inputs, all twelve directed
shears and r=0,1,2,3: 196,608 cases, 786,432 final coordinates. For each
pair/residue and slope -1,0,+1, the intercept minimum and maximum are -3,+3.
This independently corroborates the formula under the two proved reductions.
It does not replace the universal upper-bound argument above.

Large signed period/coefficient tests and the reverse-axis checks are finite
controls. The unrestricted h and spectator statements follow by scaling and
fiberwise application, not numerical testing of every grid or dimension.

## Scope, inherited obligations and credit

The theorem assumes real arithmetic, grid inputs, exactly two distinct axes,
one integral off-diagonal shear, exact pre-rounding arithmetic, and sufficient
range. It supplies no finite-width implementation, overflow bound, bit/tape
cost, reversible history, clean-scratch service or accelerated recursive child.
More stages, nonintegral shears, complex Gaussian mixing, multiple interleaved
gates and cross-fiber shears need their own analysis.

This is a source-context-bound mathematical side result. It does not discharge
the selected PR6030 assumptions native_all_columns, owned_erasure, compiler,
precision_tape or analytic_recovery, and gives **No new κ**. No selected cold
replay, Lean kernel proof or independent human review is claimed.

The pure-stage sharp bound and its proof are Nick Petalas's PR6129. The
independent audit and interleaved-shear question are Josie Elliston's PR6140.
The two-phase numerical surrogate is CubeJerry's PR6119; the deferred-row/H0
context is Vlado Vojdanovski's PR1673, with the retained native/BIT/analytic
lineage credited by those packages. The exact-history result PR5912 and
Sricharan Vagvala's PR1631 shear-equivariance obstruction address different
contracts: neither is a two-stage Walsh error classification. No predecessor
code is imported or modified. The verbatim context documents retain their
notices and exact source pins in SOURCES.json.
