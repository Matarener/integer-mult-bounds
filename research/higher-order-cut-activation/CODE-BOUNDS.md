# Executable bounds and implementation inspection

Produced by Nick Petalas. Apache-2.0.

The executable is calibration software. Its two modules have no recursion,
dynamic evaluation, subprocesses, network use, background work or file writes.
All functions are under 60 physical lines. Scalar words contain only signed
ADDs on distinct valid coordinates. Scientific checks use explicit exceptions
and remain active under optimized Python; internal assertions are additional
checks, not the only mathematical acceptance conditions.

The public constructors limit banks to eight, entries to 10^9 and scalar
fixtures to d <= 49. The Euclidean loop has 64 iterations, exceeding its
worst-case bound for two positive integers at most 10^9. At most eight Bezout
steps are used. Literal words have at most 816 signed ADDs and 24 scalar
coordinates. The registered verifier uses 57 families on at most six banks,
602 proper subpools and 25 three-coordinate scalar words. Its largest minor
oracle has 2^6-1 = 63 nonempty diagonal minors. No scientific loop grows its
own input collection. Source/package hashing is bounded by the fixed committed
file list; changing that list changes the authenticated payload.

Rule 3, fixed memory capacity: CPython integers, tuples, lists and JSON require
managed allocations. The code does not claim fixed allocation after startup.
The input and loop bounds above limit live collections. Bezout coefficients
are bounded by eight products of input-sized coefficients; scalar coordinates
in the actual finite checks are fixed small integers. Follow-up, if this code
becomes a physical execution engine, is a separately specified fixed-width
representation with capacity/exhaustion checks. This diagnostic program is
not that engine.

Rule 9, indirect calls: rejecting controls pass bounded, explicit lambdas to
one local helper. These targets are visible in verify_controls and live only
for one call; there is no registry or external dispatch. The finite verifier
also uses ordinary Python library iterators. Replacing the callbacks is only
needed if this checker is ported to a runtime forbidding indirect calls.

Rule 10, diagnostics: registered normal and optimized commands run with
`-I -W error -B`; the direct syntax inspection uses ast.parse and compile with
warnings treated as errors. No third-party linter or static type checker is
required by this standalone standard-library package. Repository package
metadata, source pins, whitespace, committed-byte/history and scientific
replay checks supply the recurring verification boundary.
