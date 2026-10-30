# Verification boundaries and implementation constraints

The direct verifier authenticates both live inputs before loading the retained
normalizer. It accepts only its exact `nongeneric low class` rejection as an
ordinary bad-header result. Any other exception fails the replay. It does not
invoke Git or fetch sources. The registered metadata/source-history commands
separately authenticate provenance and publication availability.

The finite domains are fixed constants in `counts.py`. Matrix scanning has at
most 27^4 candidates in one domain. Header scanning has at most 25^4 candidates
in one domain. Matrix dimensions are at most five; the largest retained set of
canonical projectors has 19,500 entries, each with at most 25 field entries.
Every loop ranges over these fixed finite domains, a bounded matrix dimension,
or the finite package manifest/file inventory. No recursive call occurs.
No performance speedup or memory benchmark is claimed.

The formulas are checked by a canonical factorization census, a separate
all-matrix idempotent census, complete GL header scans and scalar pair-product
paths. The same minor function is used for projector and header classification;
the actual source's elimination independently checks every GL3(F3) header
at both extreme ranks and every header in domains of modulus at most nine.
The modulus-25 domain uses a deterministic index-mod-97 sample. Source checks
are samples where the receipt says so.
No source endpoint/conjugation or complete physical machine is recertified.

The code uses explicit failure checks, which remain active with `-O`. No test
replaces a failed check with an assertion. There is no repository-wide linter
configuration for this isolated package. Both registered runs enable Python
warnings as errors. A source/receipt mismatch fails closed.

## Power of Ten deviations

Rule 3, fixed allocation: CPython allocates tuples, integers and sets during
enumeration. This is a managed-runtime deviation. The fixed domains above bound
live collections; the matrix/header scans stream candidates and discard them.
The canonical seen-set is released after each domain. Static inspection of
these lifetimes is the evidence; no allocation instrumentation is claimed.
A native implementation with fixed arrays is outside this mathematical task.

Rules 8 and 9, dynamic loading and dispatch: `verify.py:load_source` loads one
SHA256-authenticated, fixed Python source, which imports only standard-library
modules. Dataclass construction and importlib dispatch are CPython mechanisms.
The only variable callback target is that pinned normalizer's `prepare`.
The direct/cold source-bound replays check this exact path. Inlining the source
would duplicate its provenance and weaken the actual-program comparison.

The other new functions are below the approximately 60-line review ceiling.
All file writes are confined to the explicit exclusive-create receipt command;
the ordinary verifier and registered commands are read-only. The receipt output
must be a new path outside the repository. Files close through a context manager.
