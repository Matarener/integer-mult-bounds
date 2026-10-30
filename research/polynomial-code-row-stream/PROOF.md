# Incremental XOR row equivalence

This contribution was produced by Nick Petalas. Apache-2.0.

## Domain and invariant

A packed row has n binary coordinates, where n is a power of two and
1 <= n <= 2^21. Define P_i by moving coordinate j to j xor i.
These permutations satisfy

```text
P_0 = I,   P_i P_j = P_(i xor j),   P_i^2 = I.
```

The new object retains the most recent base B, width n, index j and result
P_j B. For a request with that same B and n,

```text
P_(i xor j) (P_j B) = P_i B.
```

It can therefore start with either B or the preceding result. The code
chooses the preceding result only when popcount(i xor j) < popcount(i).
Otherwise it starts with B. Both paths produce the identical complete row.
Updating the retained tuple establishes the invariant for the next request.
The empty stream starts with base -1, outside the admitted row domain.

A changed width discards the masks and sets the retained base to -1.
A changed base takes the direct path, even if its index matches a prior
request. Equality of base integers is sufficient; object identity is not
assumed. Repeated indices, zero rows, zero indices and interleaved widths
are all covered. Invalid arguments are rejected before any state changes.

## Exact block swaps

Douglas Colkitt's original XOR operation and Ross Richardson's PR1075
cached implementation use, for stride s = 2^b,

```text
M = ((2^n - 1) // (2^(2s) - 1)) (2^s - 1).
```

Since 2s divides n, the quotient is an exact geometric sum. M selects the
lower s positions of each block of length 2s. The operation

```text
((row & M) << s) | ((row >> s) & M)
```

exchanges that block's halves. The destinations are disjoint, so the OR
does not discard information. Composing the selected swaps implements P_i.
The new code uses the same masks and swaps. Geometry-mask caching is the
credited predecessor step. The additional step is choosing the preceding
row as the starting point when its XOR difference is cheaper.

For an arbitrary admitted request sequence, the number of block swaps is
no greater than direct cached application in the same order. This statement
counts swaps, not elapsed time, and does not assert a globally optimal tour.
The finite production stream uses 5,501 swaps versus 12,949 direct swaps.

## Complete consumer

The adapter changes only the function reference used to construct the
four polynomial-code witness row lists in the retained complete
`audit_affine_vectors.certificate()` call. Each original index still
produces its full row, in its original position. Ordered binary elimination,
all independent-row tests, code generation, the Walsh witness, the five
Leech screens, upstream checks and certificate serialization still run.
The original function reference is restored in a finally block.

Consequently, substituting the equal rows preserves every retained
scientific result and the complete certificate. A fresh invocation owns
the adapter state; it does not memoize certificates or rank decisions.
This opt-in wrapper is for a standalone process. Its temporary module-level
substitution is not a concurrent public interface.

The written permutation identity establishes equivalence on the bounded
domain. The finite checker separately compares every one of the 3,074
production rows against both retained implementations and uses a literal
coordinate permutation oracle on small cases. Full certificate equality
alone would be weaker than those row comparisons.

## Resource and implementation limits

At one width, at most log2(n) masks are retained, together with one base
and one preceding result. Mask payload is at most n log2(n) bits, at most
5.25 MiB at the admitted maximum. Arithmetic temporaries and Python object
overheads are additional. Counters use O(log Q) bits after Q requests.
On a width change, the old mask dictionary is discarded. There is no
multi-width or multi-row result cache.

All new loops have finite domain bounds: at most 21 swap positions per
request, at most 64 declared source rows, five benchmark rounds with three
engines, and fixed verifier grids. Individual source reads are bounded
at 2 MiB. Functions remain below 60 physical lines. Explicit exceptions
keep checks enabled under optimized execution. There is no recursion.
The explicit source execution compiles one authenticated retained comparator;
it accepts no supplied code. Scientific source imports are authenticated
before execution. Direct source imports use an absent bytecode namespace
with writes disabled; registered replay supplies its own private namespace.

Power of Ten rules 3 and 8 have bounded Python-runtime deviations. Python
allocates arbitrary-precision integers and containers during each swap;
fixed-capacity arithmetic would change the implementation platform. The
enforced width, one-width mask state and fixed scientific grids bound live
data. The comparator loader executes exactly one pinned source file to
use PR1075 unchanged; its hash is checked first. A static vendored import
would duplicate that predecessor and would need its own source inventory.
The compensating checks are normal/optimized conformance, per-row equality,
capacity rejection, source corruption rejection and a Git-free export replay.
Any production adoption must revisit these bounds and the import contract.

No new support theorem, rank lower bound, decoder, supplier, paid invoice,
kappa or complete multiplication theorem is proved. The timing claim is
only a local measurement of the specified complete command.
