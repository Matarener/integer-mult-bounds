# Exact inverse refinement and its resource boundary

This scoped proof and implementation were produced by Nick Petalas.
The Gauss-Jordan algorithm and its identity-column invariant are classical.
Jose Manuel / jmbarrancoml, PR3851, supplies the exact encoded implementation
to which this refinement applies. Its Gaussian construction is a cited
premise, not a result audited here. New work is Apache-2.0.

## Contract

Take a positive-dimensional square exact rational `Matrix` accepted by the
retained no-pivot inverse. Each successive pivot must be positive. Matrix
entries are canonical reduced rational records. Numerical payloads and
indices use the retained encoded tape operations; fixture construction and
final checking are separate host boundaries. Sufficient scratch leases for
the stated extra counts are required; a pool sized only for the original
peak is not promised to suffice.

The candidate starts from the same `[A | I]`, uses the same normalization
and elimination arithmetic, checks each pivot at the same point, and copies
the same final right block. It changes only the column iterator in the two
row-operation loops from `[0,2n)` to `[k,2n)` at pivot `k`.

## Equality of states and accepted domain

Before pivot `k`, the first `k` columns of the augmented matrix equal the
first `k` columns of `I`. This holds vacuously at zero. In particular every
entry `(k,j)` with `j<k` is exactly zero.

Normalization in the retained implementation reads these entries, tests
zero, and skips them. The candidate omits exactly those reads. In every
other row, elimination first captures its factor from column `k`. For
`j<k` the source entry in row `k` is zero, so the retained implementation
again reads it and skips every multiplication and write. The candidate
omits exactly those source reads. Both implementations perform identical
arithmetic and writes for every `j>=k`, in identical order. Column `k`
becomes the `k`th identity column. Induction proves both the invariant and
bit-identical augmented matrix contents after every completed pivot.

The next pivot is therefore identical, including its sign and reduced
representation. A nonpositive pivot rejects in both implementations. A
nonsquare matrix rejects before augmentation in both. The iterator's
extra order guard always holds, since `0<=k<n<2n`. The accepted numerical
domain is unchanged. After the last pivot, both return the same encoded
inverse matrix. Suppressing reads of known zeros cannot change borrowed
input data or exterior state. The cursor owns and closes its two added
`Count` values; the retained augmented matrix remains closed in `finally`.

## Exact matrix-read reduction

Let `m_k` be the number of nonzero off-diagonal elimination factors at
pivot `k`. Both algorithms have the same `m_k` by the state induction.
Normalization omits `k` matrix reads. Each of those `m_k` row eliminations
omits another `k` source reads. All remaining matrix reads and all matrix
writes agree, including augmentation and result construction. Thus

```text
saved Matrix.get calls = sum(k * (1 + m_k), k=0,...,n-1).
```

Since `0<=m_k<=n-1`, the sharp general interval is

```text
n(n-1)/2 <= saved reads <= n^2(n-1)/2.
```

An identity matrix attains the lower bound. For the upper bound use
`A=nI+J`, where `J` is the all-ones matrix. After eliminating `k` columns,
the unprocessed Schur block has the form `nI+c_k J` with `c_k>0`, because
eliminating one pivot changes `c` to `nc/(n+c)>0`. The already processed
rows have the same nonzero coefficient on every unprocessed column;
their common coefficient begins positive and updates by multiplication
by `n/(n+c)>0`. Thus every off-diagonal factor is nonzero and `m_k=n-1`.
Every pivot is positive. This proves attainment in every dimension.

For `n=4`, this is the literal fixture `4I+J`. The physical checker measures
236 versus 212 matrix reads and 80 writes on each side. Its separate
rational trace derives the 24 omitted reads rather than assuming density.

## Costs not hidden by the read count

The suffix iterator additionally owns a cursor and a length while the
retained iterator owns its own index and remaining counter. These are
encoded `O(log n)`-bit counts, closed after each finite traversal. The
candidate does not claim a universal reduction in every tape operation,
wall time or scratch capacity.

For the complete `4I+J` fixture, including input construction, decoding,
and final pool cleanup, the retained pool's own meters report

```text
                 baseline   candidate
record reads       947301      922401
record writes      187399      182739
unit head moves    869032      846336
peak pool leases       34          36
```

These are actual finite pooled-record-tape counters. They are not a
complete machine instruction count or a supplier invoice. In particular
the two extra peak leases are paid explicitly. Both runs execute under
`sealed_constructors` and disallow host payload decoding during inversion.
All returned source records agree and all pool tapes are blank at return.

Cold-process measurements include source hash authentication, extraction,
imports, input construction, inversion, output consumption and cleanup.
They do not establish a runtime improvement. The written theorem is the
all-dimension semantics and matrix-read refinement; finite checks alone
do not prove it universally. Native all-column validity, numerical
Gaussian admission, production pages and a complete multiplication caller
remain outside this result.
