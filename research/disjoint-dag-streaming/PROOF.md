# Exact streaming serialization and retained checks

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract

The encoder accepts a finite set of active integer node indices, an argument
array and a support array of the same length. The arrays have at most
1,000,000 entries. Each argument is either `None` or a two-tuple of valid
nonnegative integer indices. Each support is a nonnegative integer of at
most 10,000 bits. Boolean indices and supports are rejected. The measured
`h=26` instance lies within these limits.

These bounds are explicit limits of this opt-in encoder. The support-bit bound
covers the default input-width budget; the node bound is an additional limit.
They do not assert that every possible expansion fits. The unchanged
checker still decides support, topology, recurrence and embedding validity.
The encoder is not an alternative mathematical admission test.

## Canonical bytes

The old expression is

```python
json.dumps([[i, args[i], str(support[i])] for i in sorted(active)],
           separators=(',', ':')).encode()
```

For a valid row, compact JSON encodes an index by its decimal digits, `None`
by `null`, and a two-tuple by its two decimal entries inside square brackets.
The support has already been converted to a string. It contains only decimal
digits, so neither escaping nor character-set selection changes it. The
resulting row is exactly `[i,null,"s"]` or `[i,[a,b],"s"]`.

The new encoder emits the same initial square bracket, those same rows in
the same sorted order, one comma between successive rows, and the same final
square bracket. The empty set emits `[]`. Its concatenated chunks therefore
equal the old byte string, including tuple/null distinction and digit order.
This statement is byte equality, stronger than matching two SHA256 digests.
Incremental SHA256 consumes the concatenation in order, so it returns the
same digest. There is no omitted lazy computation: `stream_digest` exhausts
the generator before returning.

## Buffer bound

At most six decimal digits encode an index. A pair uses at most fifteen
characters. A 10,000-bit nonnegative integer uses at most 3,011 decimal
digits, since `2**10000 < 10**3011`. Including brackets, commas and quotes,
one row has at most 3,038 bytes. Its preceding separator adds at most one.

The buffer is flushed after the row that reaches the configured threshold
`B`, where `1 <= B <= 65536`. Before that row its length is below `B`,
except for the initial single bracket when `B=1`.
Thus every emitted chunk has at most `B + 3039` bytes, a conservative bound
also covering the final bracket and the empty case. No allocation grows
with the sum of the serialized row lengths. Sorting still retains `O(n)`
node references, and Python retains a constant number of chunk/row copies.
The additional serialization space is `O(n + B + d)`, where `d <= 3011` is
the largest decimal support length. This is not a claim of constant space,
process RSS reduction, or a bound on the circuit's existing storage.

The historical encoder retains all row strings, a complete JSON string and
its encoded bytes. The new encoder eliminates those whole-document copies.
The allocation experiment starts after construction, and separately measures
the digest and the complete verification call with `tracemalloc`.

## Check conservation and invalidation

`accelerator.verify` is a static copy of the pinned method with exactly two
changes: remove its final `encoded = ...` assignment, and replace its
`dag_sha256` expression by `stream_digest(self)`. The registered verifier
compares the entire function AST after exactly those substitutions. Any other
statement or expression change fails that comparison. Thus the support,
acyclicity, disjointness, recurrence, physical embedding, fanout freshness and
output checks, and every other receipt field, are retained. No checks are
replaced by cached success.

The adapter authenticates its declared live input bytes before importing the
checker and its dependencies. Direct invocations select an absent bytecode
namespace and prohibit bytecode writes. The sources must remain stable during
an invocation. Five changed-input controls reject drift; a future source
change requires an explicit new adapter comparison, not silent reuse.

Finite corroboration includes every support choice in `{0,1,2,3}`, every
argument choice and every active subset on arrays of length zero through
two. There are 1,617 such schemas. Six large-integer fixtures bring the total
to 1,623. Four chunk thresholds exercise delimiter and flush boundaries.
Six actual circuits include singleton inputs, pairs, triples and `h=26`.
Both complete receipts and actual bytes agree. Controls also remove each
nondigest top-level statement and corrupt four actual circuits. The same
checks run under optimized Python.

This proves a scoped serialization equivalence and checks its application to
the retained verifier. It adds no supplier, multiplication theorem, native
cost model, formal proof-kernel result or new kappa.

## Code constraints

The new encoder uses no recursion, dynamic evaluation, subprocess or global
mutation of the original checker. Its loops are bounded by one million nodes,
two argument entries, and a fixed chunk budget. The benchmark uses five to
ten pairs of serial subprocesses, each with a 120-second timeout. All new
functions fit within sixty lines. Boundary guards use explicit exceptions
and remain active under `-O`.

Python requires managed allocations. The deviation from Power of Ten's
fixed-allocation rule is limited to these bounded arrays, strings and chunks;
the buffer bound above and explicit input limits provide the control.
The unchanged constructor and compiler retain their original recursion,
allocation and assertion contracts. Rewriting them would expand this task
beyond serialization. Their exact bytes, the AST guard, full receipt checks
and direct corruption controls prevent this adapter from changing them.
A separate streamed compiler would need its own ownership and iteration
proof before replacing that dependency.

No project Python linter is configured for this package, and Ruff is absent
from the local interpreter. Registered normal and optimized runs use
`-W error`; the exact-AST comparison also parses both checker implementations.
