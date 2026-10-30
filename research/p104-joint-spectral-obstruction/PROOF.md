# A persistent joint code cannot spectrally normalize the Gram pair

This contribution was produced by Nick Petalas. It is a scoped written proof
with finite exact corroboration. It gives no new kappa or physical call tariff.

## Contract and cited premises

Let R = Z[i,1/2]. Chris R / Clear1nsight's
[PR #3979](https://github.com/CrocSwap/integer-mult-bounds/pull/3979), at
`a8a1d744811cd7d1f9c43ec7ccbae85ef9695b61`, supplies the P104 Gram matrix A,
of size n = 104, and the premises

```
A² = 13A,       rank(A modulo 13, i -> 5) = r = 8.
```

The exact cited text is pinned in SOURCES.json at the canonical base. These
premises, the original code and its invoice are not rechecked here. The new
argument begins with the complete two-stage operator. The predecessor excludes
bank-separate codes for the same spectral target. Its proof explicitly leaves
general bank mixing outside that obstruction.

Put B = A tensor I_n and C = I_n tensor A. On the two banks define

```
F = upper(-C) lower(B) = [ I-CB  -C ].
                           [ B      I ]
```

Let P be the coordinate rank-r projector, P_r = P tensor I_n and
P_c = I_n tensor P. The proposed spectral endpoint is

```
T = upper(-alpha P_c) lower(beta P_r),     alpha,beta in R,
alpha beta = 169.
```

The allowed code is one arbitrary Q in GL_(2n²+h)(R), for any finite h >= 0.
It may mix both data banks and all scratch coordinates. The same code is used
at entry and exit. Scratch has arbitrary initial data and must return exactly,
so the endpoints compared are F direct-sum I_h and T direct-sum I_h. Different
entry and exit codes, interleaved new operations, and a changed scratch return
are outside this contract.

## Complete-pair invariant

Reduce through the ring map R -> F_13 given by i -> 5 and 1/2 -> 7. An
R-invertible code stays invertible after reduction. Bars are omitted in this
section. Now A² = 0 and rank A = r. Hence B² = C² = 0, BC = CB, and

```
rank B = rank C = nr,       D = BC = A tensor A,       rank D = r².
N = F-I = [ -D  -C ],       N² = [ -D   0 ],           N³ = 0.
          [  B   0 ]            [  0  -D ]
```

To compute the first rank without an inequality, N(x,y) = 0 implies Bx = 0.
Then Dx = CBx = 0, so also Cy = 0. The converse holds. Thus
ker N = ker B direct-sum ker C, and

```
rank N = 2nr,       rank N² = 2r²,       rank N³ = 0.
```

These identities hold over every field for a square-zero A. In particular,
r <= n/2. The nilpotent Jordan multiplicities are

```
size 3: 2r²;       size 2: 2r(n-2r);       size 1: 2(n-r)².
```

For the cited P104 premises, the new complete-pair invariants are

```
dimension 21632;       ranks 1664, 128, 0;
Jordan multiplicities 128 blocks of size 3,
                      1408 blocks of size 2,
                      18432 blocks of size 1.
```

The Jordan facts used here are standard nilpotent linear algebra. Their
application to this complete Gram pair and the following stable obstruction
are the new step.

## Joint codes and restored scratch still fail

Since alpha beta reduces to zero in a field, at least one coefficient reduces
to zero. Therefore T-I reduces to a single off-diagonal square-zero block,
or to zero. Its rank is nr if exactly one coefficient survives, and zero if
both vanish. In particular its rank is at most nr, strictly below 2nr when
r > 0.

Conjugacy preserves rank after subtracting the identity. Adding I_h adds
only zero blocks to that difference. Consequently

```
Q (F direct-sum I_h) Q^-1 != T direct-sum I_h
```

for every code and finite restored scratch allowed by the contract. This
removes the bank-separate restriction from this particular free-normalization
exclusion. It does not exclude arbitrary joint programs or every decoder.

## The correction rank and its precise sharpness

Write E = Q(F direct-sum I_h)Q^-1 - (T direct-sum I_h). The rank inequality
rank(X-Y) >= rank X - rank Y, applied after subtracting the identity, gives

```
rank_F13 E >= nr = 832,
rank_F13 E >= 2nr = 1664 if both coefficients vanish modulo 13.
```

The second case includes alpha = beta = 13. A nonzero minor over F_13 comes
from a nonzero minor over Q(i). Thus the same lower bounds hold for the
characteristic-zero rank of any R-valued E. Rank is an endpoint matrix rank,
not a number of native children or a complete paid invoice.

The bounds are exact in the modular relaxation, even without scratch. In
Jordan coordinates N has 2r(n-r) nontrivial chains. This is at least nr.
Select one arrow in each of nr different chains, and let M retain just these
arrows. Then M² = 0, rank M = nr, and rank(N-M) = 2nr-nr = nr. Distinct
Jordan arrows have distinct row and column indices, so the last equality
follows by counting the remaining arrows.

Every square-zero matrix of this dimension and rank nr is similar over the
field to M. Hence this construction attains the lower bound for every modular
target with exactly one surviving coefficient. When neither survives, the
target is the identity and rank N = 2nr attains the other bound. The verifier
enumerates all 21632 Jordan coordinates and an explicit permutation matching
the 832 projector arrows to the selected arrows. Existence of the Jordan
basis follows from the written argument, not a reconstruction of the original
P104 matrix.

This is sharpness over F_13. No exact dyadic rank-832 correction or lift of
the entire corrected endpoint is constructed or claimed.

## Finite corroboration and boundaries

The verifier multiplies the literal two shears for each tensor pair of a
size-two nilpotent block or a size-one zero block. Exact elimination checks
their ranks and cubes in five prime fields. It enumerates the direct-sum
components and all Jordan coordinates for n = 104, r = 8. Small stable
fixtures mix data and restored scratch and cover every coefficient residue
pair whose product is zero. They are finite checks of the new formulas,
not independent verification of the predecessor's Gram premises.

An exact rational control uses A = [[13,1],[0,0]] and
S = [[1,1/13],[0,1]]. Here SAS^-1 = diag(13,0). The two-axis code built from
S tensor S does perform the spectral normalization. Its forbidden denominator
shows why the coefficient-ring hypothesis matters. A separate scratch control
can move the nontrivial endpoint entirely into an unreturned scratch bank.
That is why an identity return on the whole scratch space is required.

No selected native, caller, compiler, precision, stock, tape or analytic replay
is needed for this algebraic side result, and none is claimed. Independent
human and formal proof-kernel review are unclaimed.

## Open next questions

Can an exact R-valued correction attain rank 832 for this spectral target?
Start with n = 2, r = 1 and the displayed integral A; require one common
R-invertible code and an exact endpoint. A modular witness alone cannot
answer this lifting question. A useful physical implementation must then price
access, native maps and complete restoration. A different producer/consumer
boundary must state which common-code hypothesis it changes.
