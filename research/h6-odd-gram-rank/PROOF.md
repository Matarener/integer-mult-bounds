# Odd-Gram rank theorem and its precise cost consequence

Work over any characteristic-zero field F. All displayed rational constants
embed in F; in particular the argument covers real and complex coefficients.
Let E be the 240 signed E8 roots, represented by doubled integer coordinates:
two nonzero entries ±2, or eight entries ±1 with an even number of negatives.
Divide ordinary doubled-coordinate dot products by 4. Roots have norm 2 and
pairings in {-2,-1,0,1,2}.

The pinned primary `e8_cubed.py` constructs these roots in `e8_shells`, retains
120 representatives whose first nonzero coordinate is positive, and constructs
each two-block product in `construct_shell` as those 120 first roots times both
signs of each second representative. Thus one H6 two-block shell contains the
canonical 28,800 root-product ports, plus 2,160 single-block norm-four ports.
This is a written binding to the exact pinned primary functions; the registered
checks independently enumerate the roots, not the entire NumPy shell generator.

Let K_f have entries f(a·c+b·d) on the canonical root-product ports. An odd
extension to {-4,...,4} of the attainable Gram values is determined by its
values at 1,2,3,4. The canonical Gram set excludes -4; its extension value
f(-4)=-f(4) is determined by oddness, not an extra assumption. The Vandermonde matrix in their distinct nonzero squares is invertible
in characteristic zero, so its unique odd interpolant has degree at most 7.
Imposing f(2)=0 and f(4)=1 leaves

```
f(t)=(-1/12+64u+1280v)t +(1/48-20u-336v)t^3 +u t^5+v t^7.
```

Any odd formula with those same attainable values is covered, irrespective of
how it is originally written. No claim is made about values outside this finite
Gram set, even kernels, different normalization or characteristic two.

## Exact root algebra

On the 240 signed roots let S be the Gram matrix, R its entrywise square, B
the antipodal permutation and J the all-ones matrix. Direct exact enumeration
checks the second moment and every one of the 57,600 entries of R². They give

```
S²=60S, R²=24R+48J, SR=0, BS=-S, BR=R, SJ=0, RJ=120J.
```

Here SR=0 follows by pairing the intermediate root with its antipode; the
other omitted products follow from B²=I and J²=240J. The five orthogonal
idempotents summing to I are

```
P0=J/240                     rank 1
P1=S/60                      rank 8
P2=R/24-J/48                 rank 35
P3=(I-B)/2-S/60              rank 112
P4=(I+B)/2-R/24+J/60         rank 84.
```

Their ranks follow from traces and idempotence, which is valid over F.
For positive odd j, the entrywise power S^[j] is
`S+(2^j-2)(I-B)`; for positive even j it is
`R+(2^j-4)(I+B)`. The zeroth entrywise power is J, including its diagonal.
The binomial expansion of `(a·c+b·d)^j` is therefore diagonal on all tensor
products of the P_i.

An odd f is supported on the odd simultaneous-antipode subspace of the signed
240×240 product. Restricting to one representative of each simultaneous
antipodal pair divides its nonzero eigenvalues by 2. It preserves rank, and
produces exactly the canonical 120×240 matrix above. Its six eigenspaces are
the indicated tensor sector and its swap:

| sectors | dimension | eigenvalue |
|---|---:|---|
| (1,0) and (0,1) |16| -195+151200u+3104640v |
| (3,0) and (0,3) |224| 30-14400u-347760v |
| (1,2) and (2,1) |560| 45-27360u-604800v |
| (3,2) and (2,3) |7840| 1440u+25200v |
| (1,4) and (4,1) |1344| 3600u+55440v |
| (3,4) and (4,3) |18816| 5040v |

The dimensions sum to 28,800. Both checkers derive these forms from the exact
root algebra. Each also checks 18 actual 28,800-column operator actions at the
cubic and two attaining parameters. The direct actions detect an omitted
quotient factor and corrupted new-sector coefficients; they supplement the
algebraic derivation rather than replacing its universal proof.

## Exhaustive parameter cases and sharpness

At u=v=0 only the first three sectors survive, giving rank 800.

If v=0 and u≠0, the two new sectors of dimensions 7,840 and 1,344 survive.
The three old sectors have distinct zero parameters, so at most the largest
old sector, of dimension 560, can vanish. Hence
`rank K_f >= 7840+1344+800-560 = 9424`.
Equality holds at u=1/608, v=0.

If v≠0, the 18,816 sector survives. When the 7,840 sector also survives their
sum alone is 26,656, greater than 20,400. Otherwise u=-35v/2. The 1,344
sector then has eigenvalue -7560v and survives. On that line the three old
zeros occur at the distinct values v=13/30576, 1/3192, 1/2800. At most 560 old
dimensions vanish, so
`rank K_f >= 18816+1344+800-560 = 20400`.
Equality holds at u=-1/160, v=1/2800. These alternatives exhaust F²; no real
ordering, floating calculation or finite-sample extrapolation is used.

These are sharp ranks of the root-product principal block. The whole H6
matrix has rank at least that of its principal block. Attainment here does
not assert the entire H6 matrix has that same rank.

## Conditional full-width scalar-factor invoice

Assume a realization expresses the full scalar K as a sum of scalar rank-one
terms, each delivered by a paid FULL-to-zero return episode of width 17.
Rank subadditivity forces at least rank(K) such terms/episodes and each pays
17 rank units. Thus a genuinely quintic member forces at least
`17*9424=160208`; a member with v≠0 forces at least `17*20400=346800`.
Both exceed N=30960 before compensation. In the inherited deficit expression,
for every positive replica count L and nonnegative other costs,
`(L-1)N-L*C_K < 0`.

The count is of rank-one return episodes, not simultaneous physical centres:
reusing one centre repeatedly still counts its episodes. This implication is
conditional on the stated scalar factorization and full-width return price.
It does not bound arbitrary dirty helpers, nonisotropic kernels, operator
factors, partial-frame networks, changed geometry or a different coverage law.
No physical supplier, rounding/precision, owners/access/tape, joint outer
transfer, new kappa or formal-kernel theorem is established here.
