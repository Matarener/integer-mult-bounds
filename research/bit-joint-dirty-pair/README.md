# Joint dirty processing does not lower this pair's unary-query tariff

For the two independently dirty rank-two inputs identified in
[PR4068](https://github.com/CrocSwap/integer-mult-bounds/pull/4068), the original
two queries attain the minimum tariff in the uniform unary-query model below.
Arbitrary scalar mixing and any finite number of restored dirty or initially
zero registers are allowed for free. The exact minimum remains
`2 Phi_m(2)`, where `Phi_m(r)=m^b r^(1-b)` and `0 <= b <= 1`.
There is no recursive-query saving or new kappa from this local mechanism.

This is a written all-parameter proof with finite source and algebra controls,
not a proof-kernel certificate or a new native supplier. The substantive
premises are fixed rational address maps, one VALUE stream per query, scalar
mixing independent of the address, the same finite word for all sufficiently
large odd address primes, and restoration of the complete required state.
The price parameter `m` is independent of the address half-dimension `d`.

## Actual source and endpoint

The frozen input bytes are copied from PR4068 head
`5a34918402ae2c0c683d8820ad832970e77f6382` and independently pinned in
[INPUT-SOURCES.json](INPUT-SOURCES.json). This package starts from canonical
main `bb4bccbf42844d2801487450727c2f63e10d1d0f` and changes no predecessor.

| Helper | Original record | Frames | Query rank |
|---|---:|---|---:|
| 413 | 23405 | 509 to 390 | 2 |
| 444 | 23424 | 509 to 392 | 2 |

Both queries can be moved to the quiet cut before record23339, preserving the
remaining scalar word and frames. All660 ordinary rows at that cut are
independently arbitrary: a complete inverse-prefix replay returns their660
input columns. The existing private slot660 is inactive and zero. The proof
grants access to additional clean scratch as a favorable relaxation, so it
does not depend on treating that private slot as dirty or unavailable.

The two rank-two increment projectors `P,Q` satisfy `(PQ-QP)[0,1]=1/8`.
Their partial-swap address labels `p=S(P), q=S(Q)` are distinct. A nonzero
dyadic minor `1/256` also certifies `rank[P Q]=4`; the principal proof does
not require that stronger geometric fact or noncommutativity.

The required local operator is `diag(p,q,I,...)` on all arbitrary rows,
with initially zero auxiliary rows returned to zero. This is the necessary
endpoint for a replacement that rejoins the same injective suffix and
preserves the entire final state. Reversible ADD/MOVE operations and guarded
COPY/ERASE pairs make the frozen suffix injective on its valid states.
New auxiliary ports have identity continuation, or the same explicitly
injective continuation on both sides. Cleaning them later with new gates
changes the extended suffix even if every old record remains.
The earlier two-public-output minor alone would not justify this endpoint
for arbitrary perturbations to other source, helper or output rows.
A rewrite that changes later compensation has a different endpoint problem.

## Why all cheaper call profiles fail

[PROOF.md](PROOF.md) gives the full argument, including clean input columns.
Let `N=ell^(2d)`. A rank-r partial swap has Boolean operator defect rank
`D_r=N(1-ell^(-r))/2`. Scalar mixing fixes the constant-input normalization,
so query defects must supply the target's two independent defects `2D_2`.
This excludes one query of any rank and two queries with either rank equal
to one. In particular, replacing `(2,2)` by `(1,3)` is impossible.

For three rank-one queries, fixed uniform correctness lifts to the formal
group algebra: finitely many distinct rational address maps separate on a
generic integer address and remain separated modulo all sufficiently large
good primes. The address determinant character then maps odd queries to
`1+epsilon`, with `epsilon^2=0`, while both targets map to1. If `U` collects
the three query output directions and `VJ` their arbitrary-input directions,
this forces `UVJ=0`. The two required target coefficients force both ranks
to be at least two, contradicting Sylvester's inequality through a
three-dimensional intermediate space. This argument allows clean ancillas.

Writing `x=2^(1-b)`, with `1 <= x <= 2`, exhausts every call count:

| Calls | Necessary normalized tariff |
|---:|---|
| 0 or1 | Impossible |
| 2 | Both ranks at least2, hence at least `2x` |
| 3 | Not all rank1, hence at least `2+x >= 2x` |
| 4 or more | At least `4 >= 2x` |

The two original rank-two calls attain `2x`. Free workspace and scalar
operations only favor a proposed replacement; charging them cannot turn
this local result into a saving.

The uniform-prime hypothesis is essential to the argument. Our explicit
control sums all24 coordinate permutations of four coordinates. It is a
nonzero formal group-algebra element whose Boolean operator is zero on
all81 addresses over F3, yet is nonzero at a separating F5 address.
A single finite-address representation cannot silently replace the bridge.

## Packing proposals and their missing costs

The direct-product carrier `H(x,y)=f(x)+g(y)`, together with the anchor
`c=f(0)`, encodes both functions injectively. Applying the single address
map `diag(p,q)` to H and decoding its slices gives `pf` and `qg` because
linear maps fix zero. Its partial-swap rank is four after reordering
coordinates. But its address carrier has `N^2` cells, plus the anchor,
instead of the original `2N` cells. Encoding, access, scratch, restoration
and the query's changed payload volume are unpriced. It cannot be invoiced
as one original-sized `Phi_m(4)` call.

A tagged two-bank primitive could instead specify
`F(0,x)=f(x), F(1,x)=g(x)` and act by `(0,x)->(0,px)`,
`(1,x)->(1,qx)`. This is a precise functional interface, but it is a
tag-controlled choice between two address maps, not the admitted single
linear partial swap on the original carrier. Rank-two involutions can also
be conjugated to a common label, but encoding and decoding that conjugation
on one bank require address adapters and a justified enlarged-carrier tariff.
Neither construction supplies those missing native costs.

Even the hypothetical tariff `Phi_m(4)` leaves only
`m^b(2x-x^2)` of margin against `2 Phi_m(2)`. Since `x(2-x) <= 1`,
one extra ordinary rank-one query consumes that entire margin. A useful
tagged mechanism therefore needs both a genuinely admitted joint tariff
and a packing/consumer contract with no additional ordinary query overhead.
These are interface proposals, not positive query savings.

## Reproduction and evidence

From the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/bit-joint-dirty-pair
```

The self-contained package also runs without Git, predecessor checkouts,
network access or writable package files:

```sh
python3 -I -B /absolute/path/to/bit-joint-dirty-pair/verify.py
python3 -I -O -B /absolute/path/to/bit-joint-dirty-pair/verify.py
```

The verifier checks immutable input hashes, the focused source prefix and
local retiming, all660 independent columns, private-slot guards, exact
projector geometry, finite Boolean defect ranks, all32768 pairs of small
matrices in the stated Sylvester control, and the finite-field representation
counterexample. Complete canonical JSON receipts are compared, including
Boolean types. The code does not verify the all-parameter proof in a kernel.
Normal and optimized execution run the same checks.

[REVIEW.md](REVIEW.md) records separate AI mathematical and source reviews.
[SOURCE-NOTES.md](SOURCE-NOTES.md) retains attribution and overlap limits.
No physical controller, owner allocation, all-size precision/storage proof,
changed whole-word histogram, supplier admission or selected-frontier change
is claimed.

## Open next questions

The next concrete route is a larger joint helper/consumer rewrite that changes
the full rejoin state and cancels its effects later. Pin its earliest changed
reader and every borrowed row, then compare the entire output map and paid
query profile. No such downstream word is supplied here, and a public-output
projection alone does not establish restoration.

A second route is to implement the tagged two-bank interface with its true
payload volume, physical layout and full adapter/cleanup price. The first
test is whether an actual packet already supplies and consumes the needed
layout without paid conversion. Its joint recursive price remains unknown.
Structured relevance, first steps and blockers are in [TASK.json](TASK.json).

Ross Richardson, with substantial OpenAI Codex assistance in mathematics,
implementation and writing, and separate AI checks. Apache-2.0. No independent
human or formal-kernel review is claimed.
