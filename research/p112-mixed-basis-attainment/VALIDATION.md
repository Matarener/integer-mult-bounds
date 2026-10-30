# Verification coverage and limits

## Scientific checks

The fixed 35-case corpus has 28,269 VVV ternary assignments and 2,200 MMM binary
assignments. It includes twelve matched mixed/coordinate pairs with private
pins, shared-block dimensions four/five/six, double blocks, crossing cells, an
eight-cell case and the explicit five-cell basis-change example. This is a
bounded regression corpus, not an exhaustive geometry classification.

`verify.py` computes column-span ranks blockwise. For every VVV assignment it
checks equivalence of the graph/count test and the actual floor, and verifies
that zeroing unpinned components preserves equality whenever equality holds.
It exhausts MMM choices and checks the explicit all-zero attaining choice.

`independent.py` derives reader supports from the actual doubled scalar factors,
forms the full rectangular binary Gram matrices and uses a separate row
elimination. It compares four-charge streams, their ordered SHA256 hashes,
complete histograms, minima, equality counts and first witnesses with RESULT.
The common code is only input byte/geometry validation. No criterion, support
mask, graph construction or rank function is shared between the calculations.

The scalar checker also verifies 17,032 doubled operator entries, 4,258 each
over integers and F3/F5/F7, with arbitrary nonconstant parameters, two external
coordinates and nontrivial finite-field term gauges. These entries check
algebraic exactness; they are not physical dirty-restoration executions.

Seven faults reject through each real optimized CLI: out-of-range basis label,
non-Gram-I basis, duplicated port, omitted port, Boolean dimension, forged
equality count and forged charge-stream hash. The five geometry faults update
the fixture authentication hash so hash rejection cannot conceal missing
contract validation. Fourteen rejected runs are each followed by a restored
success; both initial positives also pass. Controls use owned regular exclusive
inode-disjoint byte copies in a private temporary directory. Sources and
restored copies must retain their exact bytes. No chmod, copied modes, shared
runtime modification or source mutation is used.

The written PROOF supplies all-size quantifiers. It reproves every inherited
mathematical ingredient used here. The exact predecessor proofs are retained
only under COMPARISONS with commit/path/blob/SHA256, as handoff context. They
are not used to bypass source ancestry or as undeclared proof premises.

## Execution contract

VERIFY registers all three optimized scientific/control commands on CPython3.12,
with a 120-second bound each, no third-party dependencies and no external live
inputs. The source-history checker and metadata validator require repository
Git history. Scientific replay needs only package bytes and CPython3.12.

Publication verification must record actual executed HEAD independently for
registered replay, metadata and committed-byte/source-history checks. A later
byte-equivalence observation does not retroactively change the HEAD of an
execution. An actual committed Git-free export must run all three commands
with PATH=/nonexistent and an existing private TMPDIR. Export manifests must
compare source/export hashes, regular/owned status and disjoint device/inode
identities before and after replay. Required reports retain these receipts
outside the checkout. A Git-free pass does not establish hosted CI success.

## Power of Ten inspection

New scientific code has no recursion. Loops are bounded by at most 64 cases,
four blocks, block dimension six, 72 indexed labels, eight cells, 3^8 VVV
assignments and 2^8 MMM assignments per case. Column elimination has six bit
positions; raw elimination has 72. Component propagation takes at most eight
passes. Identity matrices have at most ten scalar coordinates and four fields.
Both JSON reads stop after 200,001 bytes and reject above 200,000. Every check
uses explicit exceptions and stays active under `-O`. Subprocess controls have
60-second bounds and checked return codes/diagnostics; registered commands have
separate timeouts. The longest function is the 50-line fixture replay.

Rule 3 deviation: CPython and JSON dynamically allocate. Fixed fixture/input
limits bound live data and the exhaustive generators stream assignments. The
interpreter/library allocation internals are not statically inspected. A future
fixed-capacity implementation would need allocation instrumentation; no memory
benchmark is claimed.

Rules 8/9 deviation: the independent checker uses importlib with one fixed
package-local `verify.py` target for input validation only. This avoids two
inconsistent boundary implementations. The scientific paths are direct local
functions. Fresh exports/control copies contain no bytecode, and registered
execution supplies a private cache namespace. No arbitrary module or function
name is accepted. If the boundary becomes a reusable API, replace the loader
atomically with an explicit bounded input module.

Rule 10 deviation: Ruff's complete optional rules report annotation/docstring,
magic-number, comma, package-layout, copyright-policy and intentional CLI-print
preferences, plus a fixed-argv subprocess warning. The subprocess uses the
current interpreter, a fixed local script, no shell, a timeout and explicit
status checks. Applicable E/F/I/B/UP/ASYNC/SIM diagnostics and formatting must
pass. No project-wide type-check/configuration expansion is made for this
isolated research script. Full optional diagnostics remain in the session
receipts, without blanket source suppressions. The source integer constants
are finite proof/corpus bounds and documented support masks. A future shared
library adoption would warrant a repository type/style policy and annotations.

Build the Lever shaped the rerunnable graph/raw-Gram checks and fault controls.
Prove It Works required real optimized CLIs and committed Git-free replay.
Separate Before Serializing Shared State kept owned outputs disjoint and used
process-held locks for shared Git/reservations. No extra thread or subagent was
created for this contribution.

## Unrun obligations

No Lean, Docker, selected full cold replay, hosted CI, independent human/formal
acceptance, nonreducing/partial-basis theorem, arbitrary-query classification or
complexity result is claimed. Native acquisition, coefficient delivery, frames,
physical dirty restoration, hosting, precision, stock, compiler/all-size
admission, complete supplier/consumer invoices and outer multiplication transfer
remain unrun. This scoped equality theorem does not authorize expanding a
physical construction without its complete boundary and cost ledger.
