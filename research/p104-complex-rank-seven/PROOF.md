# Complex rank seven beats the real quarter-error floor

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Nick Petalas's PR6183 retains the contractive Gram question and the real
omitted-root projector; Matarener's PR6166 retains the cited coordinate
identification and omitted lines. The real comparison theorem is credited
to apoursh's [PR6191](https://github.com/CrocSwap/integer-mult-bounds/blob/be3fc854aa380b3d81e134ce9a4282468e4fa999/research/p104-rank-seven-error-floor/PROOF.md).

## 1. Fixed matrix and statement

Use the 104 root lines retained by
`research/p104-contractive-gram-deflation/MISSING.json`: all 56 D8 lines
`e_i +/- e_j` and 48 odd-parity half-spin lines in eight coordinates.
Each row of R is a root of squared norm two, with its first nonzero
coordinate positive. Write S=2R and K=RR^T/2=SS^T/8. The sixteen omitted
half-spin lines are part of the pinned instance, not a search parameter.

There is a Hermitian orthogonal projector D over Q(i), of complex rank
seven, such that C=RDR^T/2 has complex rank seven, satisfies
`0 <= C <= K` in Hermitian positive-semidefinite order, and

```text
max_(j,k) |K_jk-C_jk| = 25/101 < 1/4.
```

The absolute value is the complex modulus. In contrast, every real
104-by-104 matrix of real rank at most seven has error at least 1/4
against this K (section 4). Thus extending the coefficient field changes
the approximation problem even with a positive contractive carrier filter.
The assertion `0<=D<=I` is about the eight-dimensional filter, not about
C being a contraction on the 104-dimensional ambient space.

## 2. Exact witness

Take

```text
z = (5-5i, 3+9i, 5-5i, 7, 5-5i, -1-4i, -7, -7),
N = z* z = 404,
D = I8 - z z*/N.
```

Here * denotes conjugate transpose. Since z is nonzero, `zz*/N` is a
rank-one Hermitian orthogonal projector. Consequently D is Hermitian,
`D^2=D`, `0<=D<=I`, and `rank_C D=7`. R has full column rank: the
eight retained roots `e_(2j)+e_(2j+1)` and `e_(2j)-e_(2j+1)` for
j=0,1,2,3 form an orthogonal basis. Thus

```text
C = (RD)(RD)*/2,     rank_C C = rank_C(RD) = 7,
K-C = (Rz)(Rz)*/(2N) = (Sz)(Sz)*/(8N).
```

Both C and K-C are positive semidefinite, proving `0<=C<=K`.
If `m=max_j |(Sz)_j|^2`, the last rank-one formula gives

```text
max_(j,k) |K_jk-C_jk| = m/(8N).
```

Indeed each product `|(Sz)_j| |(Sz)_k|` is at most m, and a diagonal
entry with maximal squared modulus attains m. Complete exact enumeration
of the fixed 104 rows gives m=800, in both the D8 and retained half-spin
parts. Therefore the error is `800/(8*404)=25/101`, whose gap below
1/4 is exactly `1/404`.

For a reproducible row ordering, enumerate pairs i<j lexicographically,
with D8 sign -1 then +1, followed by tails in `{-1,+1}^7` lexicographically,
first coordinate +1, odd negative parity, excluding the pinned omitted
lines. The attaining row indices, starting at zero, are

```text
0, 3, 7, 14, 18, 29, 70, 71, 72, 77, 78, 79.
```

The primary checker also verifies every entry of the literal product
`SDS^T/8` against the rank-one error identity. The independently written
checker reconstructs the instance and uses separate exact arithmetic.
Neither certificate uses floating point tolerances.

## 3. Secondary witness and coefficient field

A previously found second witness provides the stronger upper bound below,
with no optimality claim:

```text
z' = (14-10i, 6+23i, 14-10i, 17+3i,
      14-10i, -3-10i, -17-3i, -17-3i),
N' = 2456,      max_j |(Sz')_j|^2 = 4820,
error = 4820/(8*2456) = 1205/4912 < 1/4,
gap = 23/4912.
```

The same proof applies, and both checkers verify its full matrix too.
Attaining indices in the primary ordering are `17,22,24,62,69,85`.
The small witness is the principal example because its arithmetic is
simpler; neither witness is asserted globally optimal. No new search is
needed to reproduce them. Discovery used bounded numerical exploration
followed by exact integer rationalization; only the exact witnesses and
their complete certificates supply the result.

These coefficients are Gaussian-rational, not Gaussian-dyadic. For the
first D, `D_00=177/202`; for the second, `D'_00=270/307`. The odd
denominators cannot be called free native operations. This is an algebraic
field separation, with no circuit or physical cost claimed.

## 4. The real comparison and why real parts do not evade it

The following is the real proof from PR6191, included to state the exact
comparison without requiring its pending Git head at replay time.
Let F be any real 104-by-104 matrix of rank at most seven. Select the
eight columns J indexed by the orthogonal D8 basis above. There is a
nonzero real a with `F[:,J]a=0`. Let U have those eight roots as its
columns and set x=Ua. Then `K[:,J]a=Rx/2`.

For each coordinate pair, the inverse change of basis gives
`a_+=(x_i+x_j)/2`, `a_-=(x_i-x_j)/2`. The real identity

```text
(|s+t|+|s-t|)/2 = max(|s|,|t|)
```

implies that `||a||_1` is the sum of the larger coordinate modulus in
each of four pairs. If t1>=...>=t8 are the ordered moduli of x, then
`||a||_1 <= t1+t2+t3+t4 <= 2(t1+t2)`. The retained D8 rows give
`||Rx||_infinity=t1+t2` when restricted to that subsystem. For
`delta=max|K-F|`, therefore

```text
delta ||a||_1 >= ||(K-F)[:,J]a||_infinity
               = ||Rx||_infinity/2 >= (t1+t2)/2,
delta >= 1/4.
```

An omitted real half-spin root gives equality by PR6183's projection,
so the real floor is exactly 1/4. The displayed two-coordinate identity
is specific to real numbers: s=1,t=i already makes its left side sqrt(2)
and right side 1. It cannot be applied to the complex kernel vector.

There is also no contradiction obtained by taking real parts. Write
z=u+iv for the small witness. Then

```text
u^T u = 232,   v^T v = 172,   u^T v = -44,
det [[232,-44],[-44,172]] = 37968 > 0,
Re(D) = I8 - (uu^T+vv^T)/404.
```

The real matrix `uu^T+vv^T` has two strictly positive eigenvalues whose
sum is 404, so each is strictly less than 404. Thus Re(D) is positive
definite and `rank_R Re(C)=8`. The complex rank-seven construction does
not yield a seven-real-mode implementation; its usual realification has
rank fourteen.

## 5. Scope and proof obligations

The mathematical object is the fixed root Gram matrix with its specified
sixteen omitted lines. The physical identification with selected P104
ports remains a cited premise from Matarener's PR6166; its source code,
native operators and coordinate identification are not independently
replayed here. Nick Petalas's PR6183 retains the Gram convention and
contractive question, with Rohan Arun/Chafik Boukhalfa and the retained
root/frame/native/helper/compiler/BIT lineage credited in the README.

The complete finite root census proves the two stated errors for this
instance; the projection and rank arguments are written mathematics.
No universal complex optimum, asymptotically vanishing residual, native
Gaussian-dyadic implementation, source/consumer installation, residual
correction, dirty restoration, paid/target saving, new kappa or complete
multiplication theorem follows. The selected result and its five framework
assumptions retain their status.
