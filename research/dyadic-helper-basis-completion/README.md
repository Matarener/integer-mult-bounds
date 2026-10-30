# Complete the dyadic helper-basis constructor

This enabling algorithm removes the unit-entry restriction in the
[PR5602](https://github.com/CrocSwap/integer-mult-bounds/pull/5602) helper
basis constructor. For every dyadic row a and column b with a b = 1,
[basis.py](basis.py) emits ADD and unit SCALE operations for R with
`a R = e_p^T` and `R e_p = b`. The pair `(3,5)` and `(2,-1)` is legal
but has no unit row entry. The old sufficient test rejects it.

The [proof](PROOF.md) gives the complete construction. The
[replay](verify.py) uses a separate dense matrix interpreter and checks all
18 basis interfaces from the source's nine handoffs. It also checks every
integer dual pair in `[-5,5]^2` at both pivots: 616 compilations, including
16 primitive pairs omitted by the old test. Another 96 presentations cover
dimensions 1 through 12 and dyadic fractions. Five invalid-input controls
and an operation-sign control reject their defects. [RESULT.json](RESULT.json)
is the exact receipt. [SOURCES.json](SOURCES.json) pins all consumed inputs.

This is a complete constructor for one algebraic interface. It does not
find a new physical helper channel. Complete kappa is unchanged. Consumers
must charge the emitted scalar operations and recheck growth, operation
count, native maps, ownership, the physical caller and the full invoice.
The complete selected replay was not run: orientation read the selected
record and its promotion proof; its sparse source closure is not present.

## Reproduce

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/dyadic-helper-basis-completion
```

Normal and optimized commands must print `PASS_DYADIC_HELPER_BASIS_COMPLETION`.
The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The scientific
checker does not call Git or the network. Export the package with its three
declared source files. A source hash mismatch fails before the checks.

## Scope and credit

Base: canonical main `d7633ce230196a1d5d061347de7a0fd8be512ed6`, priority 7.
The three source files equal PR5602 head
`6c224aa720203c4f4615e6538d8038a275387db8`. The
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5125#discussioncomment-19184390)
is separate from the active different-carrier and word-reassociation searches.
Remote overlap pagination was complete at 22:17 UTC; local notes are sparse.
No exhaustive novelty claim is made.

Ali Romman's [PR5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599)
and PR5602 supply the helper handoff, source witnesses and compiler interface.
Nick Petalas's [PR5115](https://github.com/CrocSwap/integer-mult-bounds/pull/5115)
already uses Euclidean row preparation for a different single-hub shear
contract. Its [proof](https://github.com/CrocSwap/integer-mult-bounds/blob/391355b8e537b82cedabd45af509177496e7a7a6/research/dyadic-rankone-borrowing/README.md)
is related prior work. The present interface prescribes both a row and a
column. It does not claim row preparation as new. The Euclidean method is standard. The P104/native/controller/compiler lineage
retains its source credit; it is not re-proved here. New implementation,
interface proof and checks: Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. No independent human or formal-kernel acceptance is claimed.

## Open next questions

Use the complete constructor in the current cut search only after checking
live overlap. First test whether a previously rejected dual pair gives a
new physical target. Then charge the emitted scalar work and growth and
rerun the complete caller. Feasibility over the dyadic ring is distinct
from feasibility over the rational field. An exact pairing-ideal test can
prevent searches from relying on an unavailable odd inverse.
