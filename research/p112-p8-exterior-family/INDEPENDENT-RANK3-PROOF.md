# Independent verification of the rank-three family

This companion closes the rank-three case excluded from the original
rank-four argument. It concerns the same six fixed query formulas and the
same three ordinary target pairs in physical groups 17,18,29,30,31,32.
It proves that every rational `h` in the span of those three marks, with
arbitrary actual readers realizing their exact endpoint, has invoice at
least 18. Equality occurs for `h=0`. It does not claim that every parameter
has minimum exactly 18, or that every three-target dictionary has this floor.

Write the coefficient query columns as

`h, e1+e2+2h, e0+e2+h, e0+e1+h, 2e0+e1+e2, e0+h`,

where `h` ranges over `Q^3`. Adjoining the marked unit vectors gives nine
columns of constant total rank three. Every maximal minor is affine in `h`:
multilinearity leaves the constant determinant and the three single-update
terms; any term using two updated columns vanishes because both are
proportional to `h`. The independent replay computes these coefficients
directly. There are 84 minors: three identically zero, four constant nonzero,
and 77 nonconstant, defining 25 distinct primitive affine planes.

The exact stratum of a point is determined by which planes contain it.
Intersect those planes, then remove all remaining planes. Any consistent
system of affine equations in three variables has a basis of at most three
equations. The independent replay therefore intersects every subset of at
most three planes, using exact rational RREF and rejecting inconsistent
systems. This differs from the primary iterative-flat construction. It
produces exactly 443 flats: 250 points,167 lines,25 planes and the ambient
space. Empty intersections, redundant equations and parallel distinct
planes are explicitly handled.

Every resulting stratum has a rational point. Parametrize its flat by free
coordinates, and substitute distinct powers `t,t^2,t^3` as appropriate. Any
excluded plane remains a nonzero univariate polynomial, so only finitely
many rational values are forbidden. The replay uses a degree-based finite
bound and verifies its chosen point against all 25 planes. It also checks
all 84 literal determinants at that point. These are certified generic
representatives of proved strata, not coefficient samples.

The maximal-basis pattern determines every subset rank: for a subset `S`,
its rank is the maximum of `|S intersect B|` over all maximal bases `B`.
The replay independently recomputes each of the 512 ranks directly from
literal rational columns, using cross products and determinants, for all
443 strata. All 226,816 comparisons pass. This includes source-coordinate
zeros, loops, parallel queries and every marked recovery request.

The physical target columns have disjoint supports, so their coefficient
embedding is injective. Exact recovery requires a target unit vector at
each of the six marked output ports and zero at every other output port.
All outside reader columns may therefore be set to zero without increasing
any charge. The two copies of a target choose readers independently; no
symmetrization premise is used.

Each feasible reader support contains an inclusion-minimal feasible subset.
Such a subset is independent: any dependence permits eliminating one
nonzero coefficient while retaining the recovered target. Its unique
recovery has every selected coefficient nonzero. Replacing a reader by
such a recovery can only delete physical group incidences. Thus the exact
finite objective is determined by the three complete minimal-support lists,
used independently at the six actual reader ports. Query group supports
are fixed throughout each stratum because their coordinate zero patterns
are maximal-minor data.

The checker authenticates the same two foundational inputs as the original
package, reconstructs all 4,096 tariffs on the six physical groups, and
checks monotonicity in each source and reader group. It uses whole-triad
binary pairing ranks, never scalar-coordinate tariffs. Each tariff lies
between zero and nine.

The independent threshold algorithm splits the reader ports into triples
`(0,2,4)` and `(1,3,5)`. It lists every support choice on each half and
deletes a half only when its already incurred invoice is at least 18.
Verified tariff monotonicity proves that no completion of such a half can
have cost below 18. Every surviving left/right pair is evaluated exactly.
For efficiency, costs for different right halves occupy separate byte
lanes of a Python integer. There are only six term charges, each at most
nine, so their sum is at most 54 and cannot carry between lanes. Adding
110 tests whether a lane is below 18 through its high bit; this addition
also cannot carry. The checker additionally unpacks every retained lane
and compares it to an ordinary six-term integer sum, so acceptance does
not rely solely on the packed computation.

Across the 443 strata this covers 2,785,849,439 Cartesian support cells.
Only 123,990 survive the valid partial-invoice deletion, and all have
invoice at least 18. The checker does not claim larger per-stratum minima.
Boundary controls distinguish 17,18 and54; six-term high-cost controls check
carry behavior. A literal `h=0` positive control uses only queries 2,3,5:

`c0=q5`, `c1=q3-q5`, `c2=q2-q5`.

Their complete physical charges are `6,6,6`. All 12,544 entries of the
112-port endpoint are checked exactly. A changed recovery coefficient is
rejected. Hence the family minimum is exactly 18.

`independent_rank3.py` is standard-library-only and imports no primary
verifier, scratch module or generated classification. It directly reads
only the two authenticated scientific inputs and, in default mode, compares
its result with `INDEPENDENT-RANK3-RESULT.json` without writing. The receipt
contains canonical hashes of all 443 reconstructed classification records
and all 443 threshold records, alongside counts and the equality witness.
All records are recomputed before their compact hashes are compared.
Only explicit `--write-receipt` creates or replaces the receipt. The same
guards remain active under Python optimization.
