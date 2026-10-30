# Validation and bounded implementation

This contribution was produced by Nick Petalas. Apache-2.0.

The written proof covers every n=4k+2>=2. The Python program is finite
corroboration and does not enumerate six-axis tuples or a large affine group.
It authenticates the cited source proof without importing predecessor code.
All mathematical checks use explicit exceptions and remain active under -O.

The registered normal and optimized commands run with warning-strict
CPython 3.12, using only the standard library. Each has a 120-second bound.
The receipt reports actual enumeration counts and file hashes. Direct,
registered, committed-byte/source-history and export checks are distinct;
local success does not claim hosted scientific certification.

## Capacities and control flow

The constructor accepts only n=2,6,...,130. Witness validation accepts at
most 130 coordinate rows and 265 bits per row. Its phase-pair loop has at
most 8,385 iterations. Binary elimination has at most 131 rows by 265
pivots. Each function is below 60 physical lines. There is no recursion,
dynamic evaluation, external command, network access or concurrent writer.

The family sweep has 33 dimensions and four pads. The independent literal
column check is called only through 18 axes and 41 columns. Its span has
at most 2^18 elements. Explicit codeword enumeration is capped at 2^10.
The complete two-axis census has sum_(f=0..6) 4^f=5,461 iterations and 32
phase choices per tuple. Its affine closure contains at most four values.
The Gaussian-integer check uses at most 262 binomial coefficients per
case. Input/domain failures raise ValueError and return a nonzero status.

## Managed-runtime deviations from Power of Ten

Rule: 3, fix memory capacity before steady operation.
Location: verify.py, especially literal_witness and two_axis_census.
Reason: Python's integer, list, set and JSON operations allocate dynamically.
Scope: this standalone finite verifier only.
Compensating control: fixed enumeration domains above; the largest explicit
set contains at most 2^18 bounded integers. Package hashing reads at most
ten package files and one source proof, whose byte sizes are source-bound.
Verification: direct and registered normal/optimized checks exercise every
stated finite domain. No persistent allocations or generated files remain.
Follow-up: if dimensions are raised, replace explicit span enumeration with
a separately checked bounded elimination before increasing these caps.

Rule: 10, maximum diagnostics.
Location: verify.py.
Reason: Python has no compiler warning level, and no optional static checker
is installed in this environment.
Scope: the new standalone standard-library verifier.
Compensating control: warning-strict normal/optimized execution, explicit
contracts, independent row/column arithmetic, exhaustive small cases and
rejection controls. Checks remain enabled under interpreter optimization.
Verification: the exact commands are in README.md and VERIFY.json.
Follow-up: run a project-adopted static checker when one is available; this
package adds no global tooling configuration.

## Unrun obligations

No Lean, Docker, selected cold replay, hardware rounding, physical native
execution or all-character upper certificate is needed for or supplied by
this scoped result. The source's Green-character lemma is a cited dependency,
not a new independent review claim. Hosted status belongs in the PR body.
