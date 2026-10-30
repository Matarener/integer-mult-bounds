# Coordinate charts suffice for coordinate-terminal cache trees

This contribution was produced by Nick Petalas. Claim type: scoped proof
with exact finite corroboration. No new kappa is claimed.

If every required terminal chart selects one coordinate from each symplectic
pair in a common basis, arbitrary intermediate Clifford charts cannot lower
the rank-only cache-tree cost. Echelon pivots in a self-dual coordinate order
give an explicit retraction onto the 2^n coordinate charts that fixes every
terminal and never increases any edge rank.

The [proof](PROOF.md) covers every field and dimension. Any nonnegative
nondecreasing edge tariffs are allowed, including r^(1-kappa) for 0<kappa<1,
and different edges may have different tariffs. The same topology and number
of cache vertices are retained. Fixed terminal credits remain unchanged.

This reduces an abstract search over all intermediate Lagrangians to 2^n
candidates per variable vertex under the stated terminal hypothesis. For
example, the exhaustive F2 dimension-six domain contains 135 charts and
retracts to eight. This is a search reduction, not a measured runtime gain
or a physical supplier construction.

## Evidence and reproduction

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/coordinate-cache-retraction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/coordinate-cache-retraction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/coordinate-cache-retraction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/coordinate-cache-retraction --check-source-history
```

Another CPython 3.12 interpreter can replace the local absolute path. Direct
replay prints `PASS_COORDINATE_CACHE_RETRACTION` in its JSON result; registered
replay ends with `PASS_REGISTERED_RESEARCH_PACKAGE`. The checks remain active
under `-O`, write nothing and do not execute predecessor code.

The registered finite domains are F2, F3 and F5 for n=1,2, and F2 for n=3.
They enumerate 2,379 row-reduced planes, retain 359 Lagrangian charts, and
check all 44,447 ordered chart pairs. Literal vector-set intersections supply
the distances independently of the pivot calculation. The checker records
37,780 strict contractions and 416 monotone tariff/distance checks.

A separate fixed four-terminal census checks 675 labeled trees over all
three four-leaf binary topologies. With rank prices (0,1,3/2), the unrestricted
and coordinate-restricted minima agree in each topology at 3,3,7/2. Seven
malformed-chart rejections and four scope controls cover nonisotropic or
dependent inputs, unsupported domains, wrong coordinate order, non-coordinate
terminals and nonmonotone or negative edge prices.

`--emit-result` prints a generated receipt bound to SHA256 hashes of all six
package files. Redirect it outside the checkout if needed. No receipt is
handwritten or required as a mathematical premise.

## Scope and predecessors

zxv's [PR5283](https://github.com/CrocSwap/integer-mult-bounds/pull/5283)
supplies the typed-copy snapshot contract and actual Clifford rank distance
`n-dim(L intersect M)`. Its local cache construction, sharp three-terminal
example and selected-center obstruction are cited, not audited or replayed.
Credit Matarener's PR5060, Dugongue's PR4534 and the retained native, compiler,
helper and supplier lineage in the pinned predecessor notices.

The new step is a simultaneous coordinate retraction for an arbitrary finite
cache tree. Standard pivot and initial-subspace facts are background. No
literature-priority claim is intended. PR4866's separate three-contact rule
uses all subspaces and explicitly excludes transfer to Lagrangian charts;
it neither supplies nor is extended as this tree reduction.

The complex-rank-shape-decoder card has changed scope to this rank-only
search restriction. The selected source-binding orientation passed at base
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8. The package
does not claim to have found a common coordinate basis for a current caller.
Source pins and the original card are retained in the JSON metadata.

## Limitations

All terminals must lie in one common coordinate set. Intermediate feasibility
constraints need their own preservation proof. Negative variable-edge credits
and decreasing tariffs are outside the reduction. Ordinary monomial work,
absolute phases, native realization, physical movement, dirty restoration,
ownership, snapshot lifetime, precision/tape, compiler closure and the complete
signed caller bill are unpriced. The five selected framework assumptions
remain. Selected cold replay, Lean and Docker are unrun; independent human
and formal proof-kernel review are unclaimed.

The verifier uses bounded prime-field domains, with matrices at most six by
six, at most 4,096 row-reduced bases per census and 256 retained charts. Python
and the standard library allocate managed objects during the finite loops;
this is a bounded-runtime deviation from fixed allocation. There is no
recursion, network access or dynamic source import. Functions fit within
60 physical lines. Warning-strict normal and optimized runs supply interpreter
diagnostics; no new shared tooling is introduced.

## Open next questions

Can one actual repeated source snapshot in a current supplier meet the common
coordinate-terminal hypothesis and profit after every ordinary and restoration
charge? First pin its exact operator row and required read charts, construct
the common basis if one exists, and price one complete retracted tree.
The source-row lifetime and complete physical consumer remain blockers.
No further construction or search is reserved by this package.

Apache-2.0.
