# Exact comparison with bounded auxiliary memory

The input contract is the existing validator contract. `relative_file` has
already checked the repository-relative path and produced a regular file.
The working checkout remains stable throughout validation. Write N for its
byte length and B for the retained pinned Git blob. This proof concerns the
new comparison, not the correctness of the blob reader or any mathematics in
an input package.

`file_equals_bytes` opens the file in binary mode, obtains N from the opened
file descriptor, and allocates a buffer of capacity

    q = min(1048576, max(1, N)).

It keeps memory views of that buffer and B. The loop has exactly ceil(N/q)
iterations, zero when N is zero. Its iteration at offset j*q reads into the
same buffer. For a stable regular file, the read count is
`min(q, N-j*q)`, and the buffer's first count bytes are precisely that part
of the file. The corresponding slice of B is compared without allocating
a second bytes object. A size mismatch, count mismatch, or unequal slice
sets `matches` false permanently. No mismatch exits the loop early.

If the comparison returns true, the lengths agree, every successive slice
agrees and the final one-byte read found EOF. Thus every byte agrees with B.
Conversely, if the file equals B, all lengths and slices agree, and the final
read finds EOF, so the comparison returns true. This includes an empty file,
embedded zero bytes and a final partial buffer. Therefore, under the stable
regular-file contract, the predicate is exactly the former
`B == path.read_bytes()` predicate.

The existing blob-ID and SHA256 checks still run first. The caller still
raises `ValueError("working source drift: " + name)` on a false result.
Open, fstat, readinto, final-read and close errors propagate through the
existing validator. The file context closes on every exit. Because the
whole initial extent is read even after a mismatch, an I/O error in a later
initial-extent chunk is not suppressed by an earlier unequal chunk. The
existing outer `closing(git_blobs(...))` still closes the source reader when
any comparison fails.

The comparison's additional data buffer is at most 1 MiB, independently of
N and len(B). Memory views and loop integers add constant-size interpreter
objects at the supported implementation sizes. The pinned blob itself is
still retained, and the Git reader can retain other objects. No bound on
total validator RSS or Python allocator internals follows from this claim.
The old comparison allocated N additional bytes for a matching working
file. The measured reduction in the full validator is smaller than that
local saving because the rest of validation still allocates memory.

Concurrent mutation is outside the existing stable-checkout contract. The
final read detects some growth and count checks detect some shrinkage; they
do not make validation an atomic filesystem snapshot. No stronger concurrent
mutation guarantee, universal speedup or fixed-allocation Python runtime is
claimed.
