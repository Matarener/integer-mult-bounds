# Shorter G20 boundaries from equal target pairs

The complete G20 caller now has **76 boundary ADDs per port**, down from 160.
This saves **9,324 ADDs** over all 111 ports, a 52.5% reduction in boundary
work. The emitted full stream has 301,920 events. Its positive majorant bit
length falls from 379 to 375, and its coarse positive primitive bound falls
from 952,838,302,881 to 952,838,284,233.

The physical core, all 18 local words, paid ranks, productive targets and
48-slot private contract stay fixed. Actual query values change with the
boundary basis. Every new source record is generated and checked. This is a
complete source-bound circuit construction, not a new kappa or an admitted
physical tape implementation.

## The larger construction

The original left and right boundary matrices L and R are exact inverses.
Their words cost 101 and 59 ADDs per port. Reversing the cheaper word already
reduces the combined cost from 160 to 118. Exact four-role and dependency
synthesis finds no shorter word at that fixed point.

The physical core P has the exact diagonalization L P R = D. The 32 entries
of D form 16 pairs of identical target polynomials. Let S exchange the two
coordinates in any chosen pairs. Then S commutes with D, and

```
(S^-1 L) P (R S) = S^-1 D S = D.
```

Choose the new right boundary R S and its inverse as the new left boundary.
All original labeled target jobs stay exact. No physical exchange is free:
the emitted words implement the new matrices and charge every operation.
The choice of a basis is part of the construction, not an omitted route.

Move the source word's permutations to the end by relabeling each ADD. This
keeps 14 ADDs and leaves a permutation on 32 banks. A cycle decomposition
implements that permutation with the minimum number of transpositions;
each transposition is expanded into three ADDs. The checker enumerates all
65,536 pair orientations and checks every complete matrix. A separate census
uses permutation cycle counts and matches the full cost histogram. The best
normal form has 14 ADDs and eight swaps,
for a cost of 38. There are 16 attaining orientations. The retained mask is
254. Its reverse gives the other 38-ADD boundary.

This is an exact minimum among these 65,536 normal forms. It is not a global
minimum over all linear bases, CNOT words or rescheduled callers. Both emitted
orientations are also fixed points of the retained exact four-role window,
dependency-closure and commutation reductions. These fixed points do not
exclude a different synthesis strategy.

## Complete physical and source checks

CONTROLLER.json contains both new programs and their exact 32 by 32 matrices.
The checker verifies both inverse products and the relation to the original
matrices. It also checks that each exchanged pair has the same exact target
polynomial. The physical interpreter executes every core event and compares
all resulting polynomial coefficients with the original labeled diagonal.
Only boundary programs and their derived matrix/cost fields change.

The full caller is emitted with fresh query event indices, prefix hashes,
owner versions and erasure epochs. A separate global interpreter checks all
11,070 arbitrary input axes and all 122,544,900 Boolean matrix coefficients.
A reverse sweep checks the full transpose. The exact native source relation
is checked for every one of the 56,223 paid queries: the new RAW input equals
the old RAW input after the declared permutation of the initial main inputs.
Helper and dirty-private coordinates are not permuted. The native jobs and
frame pairs remain fixed, so the retained arbitrary-input contracts apply.

All 2,529 private lifetimes and all 18 call intervals move with the unchanged
physical core. The whole core stream is compared literally after boundary
operations are removed. The productive-owner list and full signed invoice
are unchanged. The fresh positive majorant remains inside the original
1,024-bit envelope. It is not a sharp rounded-error bound.

Every saved ADD removes one field scan and one raw event from the retained
positive finite fee. Thus the bound falls by 18,648. Parking, routes, matrix
work, matchers, initialization and erasure all remain charged. The recursive
moment is unchanged, so no new ordinary exponent or multiplication kappa is
inferred from the finite fee improvement.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/g20-target-pair-boundaries
```

Python 3.12 and the standard library suffice. The exact official PR5834 export
is retained in inputs/, including all nested sources. Its complete replay
runs before this construction. The compiler adds one explicit controller
argument; ADAPTATION.json and a byte comparison require every other source
check to remain. There is no runtime patch or external pending-PR dependency.

Normal and optimized checks regenerate the complete artifacts and compare
all payloads. Controls reject an omitted boundary operation and unequal target
jobs. The parent replay retains its source-epoch and construction controls.
The direct verifier writes only to a fresh temporary directory and works
without Git or network. Hosted CI and independent admission remain separate.

## Open next questions and limits

A general GL2 basis within each equal-target pair may improve the result.
A new candidate must give a cheaper emitted pair, the exact commutation proof,
all changed source values and a full caller fee. The present census does not
exclude that possibility. TASK.json records the scope and next check.

Physical ROW head placement, cache, carry, low-type commit, padding, borrowed
storage, restoration and rounded primitive costs remain open. The inherited
native, compiler, precision/tape and analytic premises retain their status;
all five framework assumptions remain. No large uniform multiplier or new
selected result is claimed.

## Credit

Ali Romman with substantial OpenAI Codex assistance; no subagents. Keep the
complete notices in the PR5834 export and its PR5708/5828 source archives.
PR5834 supplies the global integration, and PR5807/5828 supply exact synthesis.
The controller/native lineage includes PR5708/5671, ai-nanachi PR5512,
Dugongue and every retained predecessor. The conjugation identity is standard
linear algebra. New work is this source-wide basis choice and its complete
caller construction. Apache-2.0.
Coordination: https://github.com/CrocSwap/integer-mult-bounds/discussions/5804.
