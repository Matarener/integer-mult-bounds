# A paid pivoted fallback for BIT projector packets

This contribution is a **scoped construction proof with finite corroboration**.
It supplies a new local fallback algorithm, not an audit of an existing word.
It was produced by Nick Petalas. No new kappa or complete multiplication theorem
is claimed. The selected frontier is unchanged.

For every split rank-r projector P over Z/q^w, where q is an odd prime,
1 <= r < m, and w >= 1, the partial interchange N(P) can be implemented with
later-target ADDs and the following paid reversed children:

- One weighted child of width rf.
- At most 4r weighted children of width f.
- At most 8r unit-weight children of width floor(f/2), omitted when f = 1.

Each of the m head and m tail atoms has f columns. Every input may be
arbitrarily dirty. There is no clean data ancilla. Arbitrary diagonal unit
head weights may depend on frozen ancestor fields and on the column. All
spectators are fixed, and the inverse adapter is paid and executed.

Thus there are at most 1+12r children, or 1+4r when f=1. At the retained
m=64, r<=42 boundary this is at most 505 children, including the width-42f
child. Their widths differ from those in the predecessor's 49,911-child
fallback envelope, so these are not equal-tariff runtime estimates.
At the linear width moment the new total is at most 9rf, and all recursive
widths are at most 42f < 64f. The extra-child bound is attained by this
compiler on explicit diagonal suffix projectors. No claim is made that
the bound is minimal among all algorithms.

The change is paid pivoting in the rank-r normal form. The old generic
fallback eliminates the entire 2m-coordinate involution. The new algorithm
pivots only its rank-r cross block and retains one rank-r child. It is a
construction alternative to the fallback-cost handoff in
[#4215](https://github.com/CrocSwap/integer-mult-bounds/pull/4215), rather
than a recount of that predecessor's Gaussian-elimination program.

## Boundary and pivot construction

Let C reverse m coordinates, E=diag(I_r,0), and

```text
N(P) = [[I-P, PC], [CP, I-CPC]].
```

The input is a split projector, not an arbitrary low-rank matrix. On each
column the weighted target is B N(P) B^-1, where B=diag(A,I) and A is
diagonal with unit entries. A completed reversed-child oracle accepts two
ordered equal-width fields, arbitrary complete intervening spectators,
and an ancestor-only unit weight on each paired coordinate. Ordered ADDs
allow any ring coefficient independent of their active inputs. This is
a local construction under those explicit oracle contracts.

For k=0,...,r-1, select the first unit in rows k,...,m-1 and columns
0,...,m-1-k of the current PC. Swap its row into k and its column into
m-1-k, omitting identity swaps. Clear the entries below it by row additions
and to its left by column additions. Keep every ADD slot, including zero
coefficients. Record the permutations and full-ring coefficients. Then

```text
T = L P C R0 = E D C,
D[k,k] = delta_k for k<r, D[k,k] = 1 otherwise.
```

Each stage needs at most one head swap and one tail swap. Row additions
have target i>k. The inverse of a column addition to j from column m-1-k
acts on tail values as an ADD with target m-1-k>j. Swaps are paid; they
are not free renamings.

Pivoting cannot fail over the full ring. PC has a free split image of
rank r. After k unit pivots, its eliminated matrix is the direct sum of
an invertible k-block and a residual whose image is a free split summand
of rank r-k. A finitely generated projective module over a local ring is
free. For k<r the residual therefore has positive residue-field rank,
so a nonzero residue entry lifts to a unit. At k=r its image is zero and
the residual is exactly zero over Z/q^w. Vanishing modulo q alone would
not prove that final assertion. Equivalently, the selected r image columns
form a basis by their unit row minor, and every remaining image column
has the unique combination determined by those rows.

The pivot itinerary depends only on the residue modulo q. Elimination
commutes with reduction at unit pivots. Induction therefore gives identical
swaps and ADD slots on every high lift of a low class. Coefficients and
pivot values still use the full ring. The whole high packet is preserved;
there is no high-prefix deduplication.

## Extending the inherited block identity

The following block identity comes from Cinna Davis's
[NORMAL-FORM.md](../unconditional-batched-crt/NORMAL-FORM.md), and its
credited source527/commdata2338 normalizer lineage. The new observation is
that it requires invertible L,R0 with T=EDC, not triangular L,R0. Paid
pivoting supplies those matrices for every split projector. Put

```text
U = L P L^-1,        S0 = R0^-1 C L^-1,
J = C D^-1 E,        X = S0 E - J U,
Q = [[I,0],[X,I]] diag(L,R0^-1).
```

The inherited identity gives

```text
Q N(P) Q^-1 = [[I-E, T], [J, I-JT]] = W.
```

Its algebra uses TS0=U, TJ=E, UT=T, ET=T and im(U)=im(E), hence EU=U
and UE=E. These imply TX=E-U. The first conjugation gives blocks
I-U,T,S0U,I-S0T. Conjugating by the cross shear gives upper blocks I-E,T
and lower-right block I-JT. The lower-left block simplifies as

```text
S0 U - X(U+TX) + S0 TX = S0 E - X E = J.
```

None of these equalities uses triangularity. W exchanges head k with
tail m-1-k, with weights delta_k and delta_k^-1 for k<r, fixing every
other coordinate. On f columns this is one contiguous reversed rf-child.
Chronologically execute Q, then W, then Q^-1. The total matrix is
Q^-1 W Q=N(P). Both adapters are included. The identity holds on the
whole 2mf-coordinate module, including arbitrary correlated dirty inputs.

## Weights, physical orientations and the bill

Conjugate the whole word by B=diag(A,I), independently on each column.
An ADD i <- i+c k obtains coefficient c B_i/B_k. A swap of i,k becomes
the weighted swap with weights B_i/B_k and B_k/B_i. The central child
weights are A_(k,j) delta_k. All denominators are units, and all
coefficients depend only on frozen ancestor/header data.

A same-bank swap has equal physical orientations. Reverse the later
f-atom field, use one weighted reversed f-child, then reverse the later
field again. Each field reversal uses one unit reversed child on its
floor(f/2)-atom halves, fixing its middle atom when f is odd. For weights
c_j these operations put c_j y_j in the earlier field and c_j^-1 x_j
in the later field, so varying column weights survive. Tail logical
columns have reversed physical indices; the compiler retains them.

If s<=2r is the actual number of pivot swaps in Q, Q and Q^-1 together
use exactly 2s children of width f and 4s half-width children for f>=2.
For f=1 they use exactly 2s width-one children. Cross-bank ADDs need no
swap because every tail position is later than every head position.
This proves the stated 4r/8r bounds. A diagonal projector onto the final
r coordinates gives s=2r under the declared first-unit policy, attaining
this compiler's extra-child bound. This is not a lower bound for every
possible implementation.

For any exponent t>0 the local child moment is at most

```text
(rf)^t + 4r f^t + 8r floor(f/2)^t,
```

with the last term omitted for f=1. This priced local construction has
not been installed in BIT.md's physical recursion or used to claim a
revised global saving.

The adapters also use exactly
`f [4r(m-1)-2r(r-1)+2m^2]` scalar ordered-ADD slots, including zero
coefficients. There are `r(m-1)-r(r-1)/2` row slots and the same number
of column slots in Q, plus m^2 cross slots; Q^-1 repeats them in reverse.
At m=64,r=42 this is 15,332f slots. Coefficient preparation and physical
scans are still caller obligations, rather than zero-cost assumptions.

## Evidence and reproduction

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bit-pivoted-fallback
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/bit-pivoted-fallback/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/bit-pivoted-fallback/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bit-pivoted-fallback --check-source-history
```

`verify.py` prints `PASS_BIT_PIVOTED_FALLBACK` and a generated JSON report
binding the enumeration to SHA256 of every package file and all four live
inputs. Optional `--receipt /absolute/path/outside/checkout.json` writes
the generated report, refusing to overwrite an existing file.

The replay enumerates 417,575 matrix candidates and all 1,134 nontrivial
idempotents at m=2 over Z/3, Z/5, Z/9 and Z/25, and m=3 over F3.
It adds 128 invertible charts at m=3,4,5,8 over Z/9, Z/25 and Z/27,
with f=1,...,5. It checks 1,263 plans, of which 1,074 need paid swaps.
There are 11,490 basis/dirty vector endpoint comparisons and 11,490
involution roundtrips against a separate direct B N(P) B^-1 oracle.
All 128 low/high itinerary comparisons agree. Sixteen literal m=64
fixtures cover all eight retained paid ranks at f=1 and f=3, including
rank 42 and the attained 12r extra-child count.

Four semantic controls detect omitted pivot swaps, omitted return adapters,
discarded ancestor weights and residue-only coefficients. Four invalid-input
controls reject a nonprojector, an invalid rank, an even modulus and a
nonunit ancestor weight. Explicit exceptions keep all checks active under
Python optimization. These finite facts corroborate the written proof.

## Scope and remaining obligations

The local construction proves the endpoint, dirty-state identity, ordered
ADD directions, complete high-lift itinerary, child widths and local bill.
It does not implement a finite-tape machine or certify a supplier.
Numerical preparation has a bounded reference implementation, not a new
physical cost proof. A caller must supply the completed-child contract and
pay preparation, routing, storage, parking and ancestor-weight evaluation.

The code's replay domain is m<=64, f<=8 and modulus bit length<=4096.
The written construction has no such upper limits. Tests use only the
listed prime-power rings. No formal proof-kernel or independent human
review, full selected cold replay, physical stock admission or downstream
multiplication theorem is claimed.

The next decision is to implement the caller. All pivot children have
width <=f and the rank-r child has width <=42f. The existing depth bound
may therefore be reusable, but fresh-row divisibility, descriptors, high
packet scans and physical restoration remain separate obligations.
Unknown physical costs are not zero.

## Open next questions

1. Bind the pivoted word to one complete physical recursive caller, with
   descriptors for ratio weights and the low-class pivot schedule. This
   decides whether the local bill replaces the old fallback allowance.
   Start with one m=64 rank-42 packet, odd f and frozen ancestors. Blocked
   by the physical compiler/stock/restoration proof.
2. Can another pivot policy reduce paid swaps without increasing other
   work? First compare the suffix fixture with a policy preferring an
   already positioned unit. The bound is sharp only for this compiler.
   No further search is required for the current endpoint theorem.

Structured questions are in [TASK.json](TASK.json).

## Sources, overlap and credit

Scientific base: canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`,
priority revision 7. [SOURCES.json](SOURCES.json) pins the inherited identity,
old fallback context, BIT caller and retained notice, all unchanged. The
scope changed from `uniform-transfer-audit` to an original construction.
The card's first working command passed with
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`, not a full circuit replay.

- [#4215](https://github.com/CrocSwap/integer-mult-bounds/pull/4215) checks
  the good-packet identity. This extends it with paid pivots, without
  rechecking that submission or optimizing its old fallback word.
- [#4227](https://github.com/CrocSwap/integer-mult-bounds/pull/4227) and
  [#4228](https://github.com/CrocSwap/integer-mult-bounds/pull/4228) count
  unpivoted good headers. This covers every projector packet and shares
  no density number.
- The concurrent [sharp-count claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19080592)
  retains the old fallback program. It is a different algorithm and bill.

Cinna Davis supplies #4100's written normal-form identity and fallback
context. The source527 contributors and commdata2338 supply the normalizer;
Jose Manuel supplies the recursive-closure and physical continuation
lineage; Ross Richardson supplies the full-ring fallback, covariance and
orientation accounting. Their original notices remain unchanged. The new
paid-pivot extension, compiler and proof were produced by Nick Petalas.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.

## Implementation bounds

The reference implementation uses no recursion or mutable global state.
Elimination has at most r<64 stages. Matrices have dimension at most 128,
fiber width at most 8, and every loop traverses bounded ranges or collections
derived from them. Every function is below 60 physical lines. Explicit
contracts check idempotence, units, the exact zero remainder, ordered ADDs,
paid-child counts and endpoint equality.

Python's dynamic allocation and arbitrary-precision integers are managed
runtime deviations from Power of Ten's fixed-allocation rule, bounded by
the enforced dimensions and modulus bit length. File reads use this
package and its four pinned inputs. There is no network, subprocess,
dynamic import or code generation. Both modes run with `-W error`.
A formal interpreter memory bound and a project-wide diagnostics change
are outside this package.
