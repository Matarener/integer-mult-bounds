# Dyadic normalizer words and a declared address kernel

The source is the 111 port interfaces in PR #5798 at
`eaa9cc8c15d8e994d7b81b0cda3f6dd63b0db826`. Frozen PORTS, CONTROLLER and CALLS
data bind the matrices and the ordered list of 18 thick stages. This package
constructs finite elementary words and a chosen address layout. It does not
identify that layout with the complete retained physical ROW route.

## Exact matrix and operator conventions

For distinct indices i,j define `E(i,j,a) = I + a e_i e_j^T`, and let D(i,u)
scale coordinate i by u. A published word is a **right product**:

```
I E1 E2 ... Em = W.
```

Consequently a row value v is updated chronologically by `v <- v E1`, then
`v <- v E2`, and so on. An ADD factor E(i,j,a) means
`v[j] <- v[j] + a*v[i]`; its destination is j and its source is i. A SCALE
D(i,u) means `v[i] <- u*v[i]`. The inverse word reverses the factor list and
inverts each factor: `E(i,j,a)^-1 = E(i,j,-a)` and `D(i,u)^-1 = D(i,1/u)`.

The source W has a different, column-vector interpretation: `x -> W x` maps
axis data to line data, and `x -> W^-1 x` maps line data to axis data. The
address kernel here computes `v -> v W` on row values. On columnized row data
that is `v^T -> W^T v^T`, not `v^T -> W v^T`. Equality of the matrix products
does not make these two operator conventions interchangeable. Binding this
row kernel to the final physical head-map convention remains an obligation.

## Existence using only dyadic ADDs and unit SCALEs

Let `D = Z[1/2]`. For every n and every matrix A whose entries and inverse
entries lie in D, there is a finite factorization into E(i,j,a), a in D, and
D(i,u), where `u = +/- 2^k`, k an integer. This is classical elementary
elimination over the dyadic ring; no new general theorem is claimed.

Indeed `det(A)*det(A^-1)=1` in D, so det(A) is a unit of D, hence a signed
power of two. At an elimination stage the remaining nonsingular block has
unit determinant. Clear its row denominators by multiplying rows by suitable
powers of two, which are permitted unit scalings. The resulting integer block
still has determinant a signed power of two. The gcd g of its first column
divides that determinant, by expansion along the column, so g is a power of
two. Integer Euclidean row additions and row swaps reduce that column to a
single nonzero pivot +/-g. They terminate by the usual decreasing nonnegative
integer remainder. Scale the pivot to one using a signed power of two.
The remaining block again has unit determinant; repeat. Clear the entries
above pivots by dyadic row additions. Every operation and its inverse stays
in the permitted class, and the reduction ends at I.

If the chronological left row operations are R1,...,Rm, then

```
Rm ... R2 R1 A = I, hence A = R1^-1 R2^-1 ... Rm^-1.
```

Thus the forward **right** word consists of the inverses in the same order
as the recorded left reduction operations. Reversing that order would in
general be wrong. Only construction of the inverse word reverses the
already-correct right factor list.

A swap is lowered to three ADDs and one negation SCALE. With the conventions
above its right-factor identity is

```
S(i,j) = E(i,j,1) E(j,i,-1) E(i,j,1) D(i,-1).
```

On row values (a,b), the successive pairs are `(a,a+b)`, `(-b,a+b)`,
`(-b,a)`, `(b,a)`. No SWAP primitive is silently left uncharged. For every
admitted odd q, dyadic coefficients reduce modulo the required power of q,
and each signed power-of-two SCALE is a unit. This algebra does not supply
the physical implementation or time tariff of a named P2 primitive.

## Chosen stage layout and all-row address lift

Number the retained 18 thick stages by their **ordinal** j=0,...,17 in the
authenticated CALLS order. Their controller stage identifiers need not equal
j. For that ordinal choose the eight active coordinates

```
active_j = [0, 1+7*j, 2+7*j, ..., 7+7*j]
```

inside ambient dimension 127. The other 119 coordinates are spectators for
this stage kernel. Different stages share coordinate zero; this construction
does not assert that their kernels commute or can run concurrently.

For every integer f>=1 put N=127*f. For every row r=0,...,N-1 and lane
l=0,...,f-1, the local active coordinate i has flattened address

```
address(r,i,l) = r*N + active_j[i]*f + l.
```

Within the two-half namespace, half b=0 or 1 adds the disjoint offset
`b*N^2` to this address. Thus no factor crosses the paired-half boundary.

Lower E(i,j,a) to
`ordered_shift(dst=address(r,j,l), src=address(r,i,l), coefficient=a)` and
D(i,u) to `unit_scale(address(r,i,l), coefficient=u)`. These are precisely
the destination/source conventions of JoyboyBrian's retained
`bit-row-route-generator` ABI. No predecessor generator is imported.

For a fixed row and lane, induction on the chronological factors proves the
row action vW on the eight active coordinates. Addresses for distinct rows
or lanes are disjoint, so the same induction proves the lift on all N rows
and all f lanes. Every spectator address is untouched, including arbitrary
dirty spectator values. The inverse word restores every active address as
well. This is a claim about this explicit logical address kernel under its
named primitive semantics, not a claim that an arbitrary physical ROW can
be accessed or borrowed at no cost.

## Positive counts and remaining obligations

Each coefficient-specific ADD or SCALE occurrence in one local word produces
exactly `N*f = 127*f^2` addressed primitive calls. Keep ADD and SCALE histograms
separate, including negative coefficients and all lowered swap factors.
The declared cross product of 111 ports, both words, 18 stages and two paired
halves contains `111*2*18*2 = 7,992` catalogue kernels. It is not the source's
physical paid-route incidence list or a complete caller allowance. An exact
incidence map is required before assigning those counts to the full source
schedule.

The operation counts are positive named counts. Their physical P2 unit prices
and movement/precision tariffs remain unknown; unknown costs are not zero.
Summing symbolic tariffs over the emitted address calls is legitimate, but
assuming a common unit tariff or absorbing these kernels into a retained
fee near `9.5*10^11` is not established here.

The complete ROW borrow/cache schedule, N-squared low-cache COPYs and CLEARs,
carry corrections, low-type commit, padding, return/restoration, physical
head-map correspondence, compiler and admission remain open. No new kappa
or selected-frontier change follows from this finite certificate.

Credit: Ali Romman with substantial OpenAI Codex assistance for the G20 source
port interfaces and controller/caller data; JoyboyBrian with OpenAI Codex
assistance for the retained row-route address ABI and ROW obligations.
This scoped construction/proof/audit was prepared by ToikY with substantial
OpenAI Codex assistance in separate primary, oracle and review contexts.
All retained predecessor credit is in NOTICE. Apache-2.0.
