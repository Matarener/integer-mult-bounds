# Carrier source and scope audit

This review concerns one fixed twelve-port D4 construction in the explicit
seven-dimensional chart, and its four-helper version on 28 arbitrary entering
fields. It does not admit a uniform P112 construction, a chronological owner
schedule, rounded recursion, a physical tape implementation or a kappa change.
The historical scientific pin is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## Exact source closure

`SOURCE-CLOSURE.json` records the actual bytes read during this review and the
role of each file. All 20 files and four external inputs named by the historical
`FINAL-FREEZE.json` match its digests. That historical manifest is a provenance
record, not the complete executable dependency closure of every retained script.

The old `source_carrier.py` and `reverse_carrier.py` import `need` from
`d4_geometry.py`; the former also imports an unused `dot`. `bus_word.py` imports
the elementary matrix/subspace helpers from that module. The manifest omits
`d4_geometry.py`. Its current SHA256 is
`c394a816306605124f662df5751fdf51f8a664e04222fcf63cb648b74630e06a`.
Importing its definitions does not call its separate P112 geometry generation,
but executing that generation would add substantial upstream dependencies.
Those dependencies are not needed to replay the fixed twelve-port geometry.

The historical executable closures, excluding Python's standard library, are:

| Historical program | Read or imported inputs |
| --- | --- |
| `source_carrier.py`, `reverse_carrier.py` | `d4_geometry.py` elementary guard; `D4-BUS-INPUT.json`; pinned `clifford_exact.py` |
| `common_frame_normalizer.py` | `D4-BUS-INPUT.json`; pinned `clifford_exact.py` |
| `common_frame_inverse_search.py` | `D4-BUS-INPUT.json`; `COMMON-FRAME-NORMALIZER.json`; pinned `clifford_exact.py`; its own bytes for a receipt digest |
| `verify_factor.py` | `D4-BUS-INPUT.json`; pinned `clifford_exact.py`; fixed `FACTOR.json` in comparison mode |
| `bus_width3_compiler.py` | `D4-BUS-INPUT.json`; pinned `clifford_exact.py`; its own bytes for a receipt digest |

Their corresponding historical JSON outputs and proof documents are additional
evidence inputs when the claims or exact historical results are cited.

The final package executes newly reviewed checkers. Retained historical
programs are attribution and provenance; they are not run through their
path-dependent main functions. The new normalizer replays the four fixed winners,
not the historical bounded random search. Its runtime inputs are the geometry,
the exact compiler and `COMMON-FRAME-INVERSE-SEARCH.json`. The new native
and eight-star checkers read only the fixed geometry and compiler.
`SOURCE-CLOSURE.json` records all three exact runtime stages and the complete
45-entry authenticated
package input inventory. `REVIEW-VERIFICATION.md` covers the integrated
checkers and wrapper; the larger ancestry list is explicitly review-only.
The independent 96-identity `REVIEW-STARS.md` is review evidence with a
separate byte pin, not an additional executable input or registered stage.

## Source-control findings

The historical runners load the compiler through `importlib` after reading a
digest; the inverse search even executes the module before checking that digest.
This does not bind execution to the previously captured source bytes.
`sys.dont_write_bytecode=True` suppresses cache writes, not cache reads. The
compiler contains substantive assertions, so an ordinary optimized import also
removes mathematical checks.

The new loaders execute the authenticated byte buffer with
`compile(..., dont_inherit=True, optimize=0)`, without a subsequent path reopen
or module-cache lookup. Ordinary and optimized outer invocations must retain the
same checks and compare entire typed receipts. JSON duplicate keys and
Boolean/integer substitutions must not be accepted. Source authentication and
scientific defect rejection are separate controls; their final executed
results are in `CONTROLS.json` and `CONTROL-VALIDATION.json`.

The historical factor check's `before != expected` and
`bad != expected` statements only establish a difference between arrays. They do
not run the production all-column acceptance gate on the altered word. The
replacement must reject an omitted cleanup, dirty-helper leakage and an actual
sign/frame defect through the same mathematical acceptance predicates as the
valid word. Unexpected acceptance must raise outside the rejection handler, and
the handler must match the intended failure.

## Retained-point and phase boundaries

The geometry's `source_factor_sha256` agrees with the existing
`D4-P112-FACTORS.json`; that factor's geometry digest also agrees with the existing
`D4-GEOMETRY.json`. Selected block 1 is exactly the twelve labels in the bus
input. All twelve belong to the factor's retained 112 labels. Its seven
orthonormal basis vectors in dimension nine map the twelve labels exactly to
the declared `groups7`.

The full historical tiling has 120 labels, of which eight are absent from P112.
The fixed intact block proves no uniform seven-dimensional implementation for
the other retained points. The package may use the fixed geometry as an
authenticated premise; it must not silently inherit full tiling or supplier
coverage from its ancestry.

The actual current invariant gauge is `F = X_33 F_7`, with the explicit `-i`
phase in the two-radical Walsh contact. C14's earlier width-three compiler uses
`F_7` and basis-sensitive canonical contacts. Its exact wrapper records cannot
be reused unchanged as current invariant-gauge wrappers. Native identities must
retain the signed Pauli images and global phase. The helper's fixed-slot
entrance-to-exit rank one and the moved-value helper-to-source-A rank three
describe different channels.

Raw family cleanup carries the physical value and its native frame together.
It restores family IDs while retaining changed source endpoints. It does not
restore the old source caps. The four-helper factor's twelve cleanup swaps cost
36 signed complex ADDs and twelve negations. The zero-helper carrier's eight
cleanup swaps cost 24 signed complex ADDs and eight negations. Monomial scans and
all remaining native/scalar operations are additional paid work.

## Contributions that remain separate

**C02:** `PAIRED-COMPLEX.md` concerns the nine-dimensional P112 paired endpoint,
its literal/canonical monomial gauges, the signed B4 identity, individual
dirty-helper contacts, and a restricted source-batched scheduling certificate.
Its individual-contact proof does not assemble the simultaneous helper word.
Those bounded results deserve their own completion and review. They are not
proved by the twelve-port carrier package.

**C14:** the 28-field moving-owner factor and local width-three monomial helper
interface are relevant ancestry. The one-N encoded-input contract, the generic
past/future free-group invariant, retained three-call words, zero-residual
borrowing and BIT projector-transfer questions are separate mathematical
claims. In particular a clean generic group-algebra invariant is not an
obstruction for the actual R429 representation, and consuming an encoded input
does not provide a caller that supplies that encoding. Those claims remain
queued independently.

## Attribution

Preserve the exact compiler's kernel92/PR531 lineage and the repository's
applicable Apache-2.0 license and notices. The local histories identify the
preceding D4 bus, source-carrier, common-frame normalizer and width-three-helper
constructions, and substantial OpenAI Codex assistance. New independent
verification must be attributed as such rather than represented as a formal
kernel proof or a fresh derivation of every historical source result.
