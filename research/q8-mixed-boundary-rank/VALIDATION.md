# Verification scope and implementation decisions

The author-written proof is in PROOF.md. The exact finite receipt is
RESULT.json. verify.py uses no external runtime source. It authenticates
all four unchanged mathematical-premise files through RETENTION.json and
binds the proof hash in its receipt. Registered-package checks validate
the catalogue and selected-record provenance; committed-byte/source-history
checks are separate. A receipt does not certify the universal theorem.

## What is checked

The verifier compares all 64 group products against a separate signed
Hamilton table. It reconstructs both 256-element algebra-coordinate
bijections and checks every one- through five-increment product in both
label orientations. The quadratic table, cubic sum, absence of fourth
contributions and fifth nilpotence support the coefficient derivation.

A fixed pseudorandom fixture seed 2026101804 generates 216 legal words,
three per role/length pair for roles 1 through 6 and lengths 1 through 12. Both exact
chronological identities are checked on full group-algebra matrices. A
separate Hamilton permutation action checks all 6,048 independent dirty
basis columns. The target result is not inferred from those generic words.

The boundary-rank lemma is checked on every rectangular binary X,Y pair
with target dimension 1 or 2 and call dimension 1 through 3, exactly 4,452 pairs.
Their product ranks are computed, including 3,770 nonzero products. The
I2/I2 control shows why the homogeneous zero-product bound cannot be
reused without the t_g term. Separately, 578 invertible K fixtures exhaust
the upper-left-zero matrices in dimensions 2 and 4 for target dimensions 1
and 2. They attain the cubic subspace rank lower bound. These fixtures
are rank-lemma checks, not realizable Q8 endpoint certificates.

For t from 1 through 16, all target splits and paid count pairs with total at most 3t
are screened by the inherited parity/count conditions and the two new
inequalities. Every one of the 6,157 admitted pairs satisfies 5n>=11t.
The balanced eight-call pair passes the predecessor inequality and fails
the new one. A ten-call pair passes necessary counts only. Forty-two
explicit three-calls-per-target words check the upper bound, all target
splits through t=4 and zero, one or two restored dirty spectators.

Eight unittest controls run with -O. They reject an abelianized group
law, omitted cubic correction, broken independent action, absent cubic
hypotheses, illegal inputs/capacities, changed retained source and changed
receipt. They also check the nonzero-product rank term and distinguish
necessary ten-call counts from eight-call exclusion. All scientific
contracts use require/ValueError and remain active under -O.

## Engineering constraints

Build the Lever led to the deterministic exact verifier rather than a
manual calculation receipt. Prove It Works requires actual committed
bytes to run from a Git-free export. Separate Before Serializing Shared
State led to this worker's own package/branch/output directory and
process-held ownership, with advisory serialization only for shared Git
and task reservation mutations.

Power of Ten applies to verify.py and test_package.py. Control flow is
nonrecursive. Loops are bounded by group order 8, algebra size 256,
MAX_DIM=16, validated roles<=8, fixed fixture ranges, at most 16 count
targets and eight tests. No solver, child process or background worker is
started by the package. Every function is below 60 physical lines in
normal formatting. Matrix shapes, idempotence, capacities, rank hypotheses,
source integrity and exact receipt equality use checked contracts.
Mutable state is local except immutable module constants. Runtime calls
are direct; only the bounded test framework has dynamic substitution.
Warnings are errors. Scoped Ruff 0.14.0 E/F/B/UP diagnostics are required
alongside the registered checks. The initial 14 E501 line-length findings
were corrected by formatting, without suppression; original diagnostics
are retained in the external session evidence.

Rule 3 deviation, verify.py and test_package.py: CPython allocates managed
integers/tuples/dictionaries during exact arithmetic. Fixed-capacity
allocation cannot be imposed without replacing the runtime. The enforced
16-dimensional matrices and fixed finite fixtures bound live data; no
unbounded output or queue grows. Test temporary directories have context
owners and are removed on every normal/exceptional exit. Verification
runs normal and optimized CPython 3.12. Follow-up for a native port is an
explicit fixed-capacity matrix representation with the same receipt.

Rules 8/9 deviation, test_package.py only: runpy and unittest/patch use
runtime dispatch to load the one explicit local verifier and inject
faults. The source path and eight test targets are fixed. They do not
alter production dispatch or run unbounded discovery. Context managers
restore patches and owned temporary paths on failure. Optimized tests
exercise all substitutions. Follow-up if this code gains a production
plugin boundary is an explicit immutable dispatch table and boundary test.

No claim is made that Ruff, finite tests or source hashing replace
independent mathematical review. Published exact-HEAD replay receipts,
export hashes and environment belong to the contribution evidence;
precommit executions are not relabelled as final-HEAD executions.
