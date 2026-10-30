# Verification and bounded-code notes

The registered standard-library replay passes on CPython 3.12.15, macOS arm64.
The primary checker passes normally and under `-O`; the separate sparse/dense
checker and all seven behavioral groups pass. Four optimized CLI mutations
reject changed selected bytes, changed retained bytes, duplicate seeds and a
false 218 reader receipt. Failed commands leave the mutated input unchanged.
The tests build source-only disposable exports, without Git, using the caller's
TMPDIR. They never change file modes, symlinks, shared interpreters or sources.

Exact measured outputs are in RESULT.json. Every integer factor entry, forced
mask entry, expanded binary entry and term invoice is checked against the real
source, rather than inferred from a source hash alone. The independent checker
uses no primary imports. The formal all-field statement comes from PROOF.md,
with unimodular and characteristic-not-two half-integral cases separated.

The exploratory finite seed census is not needed for replay or the proof and
is not claimed as an independently certified exhaustive search. The direct
symbolic classification and rank argument cover all allowed seeds. The native
saving hypothesis failed at the actual-reader gate, even though the exact
38-query scalar construction passed.

## Engineering choices

Build the Lever produced the retained source-bound primary and separate
checkers. Prove It Works changed the acceptance test from the source self-Gram
sum to both actual term closures and a whole integer UQ=K check. Unslop was
applied to the proof, scope, handoff and publication prose.

Power of Ten inspection covers the three new Python files. Control flow is
iterative and uses bounded for loops. There is no recursion, eval, dynamic code
generation, registry or indirect application dispatch. Inputs are authenticated
and bounded before science loops. Main dimensions are 112 ports, 16 groups,
38 queries, 7 formal vectors, 35 triples, 496 pairs and 9 label coordinates.
The pairwise dense rank routine accepts at most 16 rows and 16 columns. The
primary binary rank routine accepts at most 224 rows and 112 bits, with at most
112 pivot iterations per row. Certificate parsing limits three replacements,
two group IDs and at most 16 seed ports. Files are limited to 32 KiB metadata,
16 KiB construction, 64 KiB receipt and 2 MiB selected payload. Exceptions fail the
check; meaningful contracts remain active under optimized Python.

The largest functions remain within sixty physical lines after formatting.
Files own no persistent resources beyond context-managed reads. Tests use
context-managed temporary directories and at most six sequential 30-second
child commands. Their executable is the current interpreter; no Git, network
or arbitrary child executable is used. Test exports are removed on exit.
Published scripts write no evidence. RESULT.json is a committed expected
receipt checked for exact equality, not a receipt regenerated on ordinary runs.

Rule 3, fixed memory, has a managed-runtime deviation in all three Python files.
Python JSON, integers, fractions and lists allocate during checks. Live sizes
are bounded by the authenticated input limits and fixed dimensions above,
with no concurrency or growing work queue. The largest dense operator has
112 by 112 entries. Valid, invalid and capacity controls pass; interpreter/library
allocation internals are not audited. Revisit only if dimensions or concurrency
are expanded, using explicit capacity analysis before that change.

Rule 10 uses warning-as-error registered commands and local Ruff 0.17.1 checks
with E/F/B/SIM/I/UP/PLW and formatting. The generic standard-library replay
workflow does not provide Ruff; local static lint is documented rather than
adding a dependency or changing shared workflow policy in this isolated package.
If a dedicated lint dependency contract is adopted, add the same pinned check
there. No diagnostic is suppressed in this package.

## Limits

No native source acquisition, physical frame transport, coefficient execution,
private-workspace restoration, hosting, storage, precision/tape, all-size
compilation, complete supplier, selected cold replay, Lean, Docker, independent
human review or formal-kernel check was run. Algebraic dirty-target preservation
is checked on all 224 source/target basis columns and has only that scope.
The actual source/reader 244 bill is not a complete physical execution bill.
No improved kappa or selected-frontier change is claimed.
