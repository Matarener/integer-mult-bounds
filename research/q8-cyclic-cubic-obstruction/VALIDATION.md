# Validation boundaries and engineering decisions

PROOF.md proves the uniform homogeneous cyclic tariff 3t and separately
the compressed cubic-defect lemma. Finite execution corroborates their
identities and detects representative faults. It is not a formal proof
kernel or an independent human audit. The all-t strengthening changes
the written argument, without enlarging the finite experiment.

## Bounded verification

The executable uses integer bit rows and exact arithmetic. It supports
at most eight roles, sixteen calls and 64-bit row widths. Its actual
generic fixtures use at most two roles and four calls. The block check
enumerates 8 and 4,096 matrices for t=1,2, respectively. The attaining
fixtures use t=1..4 and zero, one or three restored spectators, with each
of the two homogeneous paid labels. Every loop is bounded by those
constants, validated inputs or the 32-entry source-inventory limit.

The independent formal action evaluates full Q8 group basis inputs;
the coefficient implementation uses chronological binary polynomial
products modulo x^4. Their common Q8 coordinate convention is
`i^a j^b` encoded as `a+4b`. The retained PR3551 witness uses its original
encoding, whose target label five denotes zi; the verifier explicitly
checks that metadata and evaluates the same inverse target as i^3 in
its own encoding. The paid witness label one is i in both conventions.

The five behavioral groups inject actual producer faults and test the
critical rank/projection/invertibility/dimension hypotheses. They also
test invalid and excessive inputs, source and deterministic-receipt
corruption, and refusal to overwrite a receipt. Tests remain active
under optimized Python. No assertion essential to acceptance uses the
`assert` statement.

No new solver search or historical census is part of this package.
No full selected cold replay, Lean, Docker, mixed-label minimum,
physical caller, complete supplier or kappa update is claimed.

## Principle decisions

Build the Lever led to a small deterministic verifier, rather than
another uncheckable solver timeout. Prove It Works requires checks of
the actual committed package and its Git-free export before publication.
Separate Before Serializing Shared State led to this worker's own
branch, package, output directory and process-held ownership lock;
shared Git mutations and peer claims use the campaign advisory locks.

The Power of Ten inspection finds no recursion, dynamic evaluation,
unbounded scientific loop, detached process or mutable scientific global
state. All functions are below the 60-line ceiling. Failure checks use
explicit ValueError and remain enabled under optimization. Source and
receipt reads are bounded by package-owned files; exceptions propagate.
The only writes are an explicitly requested exclusive receipt, or
owned temporary files in the behavioral tests.

Rule 3 deviation, verify.py and test_package.py: CPython allocates
integers, tuples and library objects during evaluation. The interpreter
cannot provide fixed allocation after initialization. Enforced capacities
bound scientific rows, words and simultaneous state; the largest finite
census streams its matrices rather than retaining them. Tests own and
remove their temporary directories. A larger accepted input domain would
require a new capacity and allocation review.

Rules 8 and 9 deviation, test_package.py only: unittest, mock and the
standard importlib loader use bounded dynamic dispatch. They load exactly
the local verifier and five named test methods. No runtime network or
arbitrary module path is accepted. Optimized execution exercises these
same targets. A future test-framework change must recheck those targets.

Rule 10 diagnostics use CPython warnings as errors and scoped Ruff
E/F/B/UP checks. The repository-wide diagnostics configuration is outside
this isolated research change. Exact invocations and results are kept in
the session's command receipts; a passing lint is not mathematical evidence.

## Source closure and publication

SOURCE_HASHES.json authenticates the scientific runtime, written proof,
behavioral controls and unchanged retained source bytes. The publication
gate additionally checks all package working bytes against the actual
commit and canonical ancestry pins. Exact origin identities for pending
predecessor bytes are in inputs/RETENTION.json, so scientific replay does
not need their foreign Git objects.

The final session report records committed HEAD, exact argv, environment,
stdout/stderr/exit receipts and per-file export/source identities. Exports
must be exclusive owned regular byte copies with disjoint source and
destination inodes, using no copied modes or metadata. Their before/after
hashes are measured before disposal. The shared interpreter is neither
modified nor chmodded. Only proven-owned disposable files are removed.
