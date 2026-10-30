# Exact circuit and substitution proof

Produced by Nick Petalas. Apache-2.0.

## 1. Declared local map

Let W be the decompressed source word pinned in SOURCES.json and let
`B = W.program[17461:20431]`. All 2,970 events of B are ADD or SCALE at
chart 127. Let R be the sorted union of all its source and destination
roles. There are 545 roles. At entry, assign an independent formal value
to every role in R, regardless of any additional relations that the full
word might happen to impose. All other roles are left alone.

An ADD `r <- r + q s` is an elementary matrix with inverse obtained by
negating q. A SCALE `r <- q r` is invertible over Z[1/2] exactly when
q is a signed power of two; its inverse uses 1/q. The replacement obeys
these conditions. This proves invertibility of each operation without
assuming any initial helper is zero.

## 2. Construction and finite equality

The constructor starts with the exact matrix M of B. It greedily subtracts
one current row from another at a dyadic coefficient when this removes at
least two nonzero entries. There are 245 such steps in this instance.
It then chooses sparse dyadic-unit pivots, normalizes each pivot, and
eliminates its column from every other row. Pivots outside Z[1/2]'s units
are rejected. The resulting permutation matrix is returned to the literal
identity by 218 exchanges. Each exchange is the charged four-operation word

```text
r += s; s -= r; r += s; s = -s.
```

No external zero cell or free role permutation is used. All operations are
on the original role set. If the chronological elimination matrices are
E_1,...,E_k, the checked invariant at completion is

`E_k ... E_1 M = I`.

Hence `M = E_1^-1 ... E_k^-1`. The emitted chronological replacement is
`E_k^-1,...,E_1^-1`. Its 2,851 operations are authenticated by the fixed
canonical JSON digest in verify.py.

The mathematical claim is finite and has a separate direct check. The
verifier initializes a dense integer identity matrix, retaining one binary
denominator exponent per row. For an ADD it aligns the two denominator
exponents, performs the integer row addition, and cancels common powers of
two; SCALE is analogous. This engine does not call the sparse row routines.
It computes every coefficient of the original and emitted matrices and
requires equality of their canonical normalized integer representations.
All 297,025 coefficients agree. Role 758 is explicitly retained even though
it appears in no emitted operation. Thus the equality includes its identity
row and column, rather than silently shrinking the interface.

Equality over the rational dyadic coefficients proves equality on every
module over Z[1/2], in particular arbitrary real or complex payload arrays.
The finite integer certificate proves this named matrix identity; it does
not prove a universal synthesis algorithm or an optimality bound.

## 3. Legal substitution in the full word

Replace B in W by the emitted circuit B'. All preceding and subsequent
events remain identical. The source-authenticated complete-word interpreter
checks that every new source/destination is available at chart 127 and
that all chronological transports, owned lifetimes, COPY preconditions
and final frames hold. The new interval contains no MOVE, INIT, CLEAR or
COPY. All original non-scalar events retain their order and literal values.

Because B and B' agree on arbitrary entry values of all touched roles,
they agree on the actual state reached by any prefix of W. They also agree
on the unchanged roles. Applying the identical continuation therefore
preserves every whole-word endpoint. The explicit ADD at ordinal 20431
is not crossed: it remains the first event after the replacement and
uses chart 245. The full replay confirms every one of 799 squared endpoint
coefficients and the original storage inventory.

Recursive paid calls are determined by the unchanged MOVE events. Productive
helper ranks use the unchanged public entry/exit frames and main-role set.
Their histograms therefore remain identical. This is why the local scalar
gain supplies no new exponent saving.

## 4. Complete scalar charge

Use the tariff in the pinned complete-word checker. For q=n/d in reduced
form, with n positive after taking the absolute value, an ADD costs

`2 (3 + bitlength(n)-1 + popcount(n) + bitlength(d)-1)`.

A signed power-of-two SCALE costs

`2 (abs(bitlength(n)-bitlength(d)) + [q<0])`.

There are no uncharged exchanges, scales or access changes inside this
abstract scalar tariff. Summing over the entire original interval gives
25,988; summing over the emitted interval gives 23,478. The improvement is
2,510, and event count improves by 119. All other events are unchanged,
so the full-word allowance is 189,428 - 2,510 = 186,918 and the event count
is 22,803 - 119 = 22,684. The new complete-word interpreter independently
recounts that allowance from the emitted word.

The dense engine also tracks the l1 norm of every intermediate local row.
Both maxima equal 67. This supports a local absolute-magnitude comparison
from identical entry values. It establishes no rounded error accumulation,
physical memory traffic, native runtime or supplier integration theorem.
