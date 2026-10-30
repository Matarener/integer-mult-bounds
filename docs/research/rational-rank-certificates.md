# Export a linear interface with exact rank and kernels

Use this tool when an interface search needs independent coordinates, a
factorization through them, or all linear relations among ports. Floating
rank thresholds can lose an exact dependency. This tool uses rational data
and emits witnesses that a separate multiplication-only checker can replay.

```json
{"schema":"rational-rank-problem/v1","matrix":[[1,0,1],[0,1,1],[1,1,2]]}
```

```sh
python3 -B scripts/certify_rational_rank.py problem.json > certificate.json
python3 -B scripts/certify_rational_rank.py problem.json --check certificate.json
```

The example has rank 2. Both kernel bases contain (-1,-1,1). The returned
pivot row and column lists identify a nonsingular minor D of order r. Its
explicit inverse proves rank(A)>=r. The coefficient matrix C satisfies
A=A[:,columns] C, proving rank(A)<=r. These two witnesses establish exact rank.

Each right-kernel vector has an identity coordinate on one nonpivot column
and zero coordinates on the other nonpivot columns. The checker verifies
A v=0 and that identity block. There are n-r such independent vectors, so they
form the whole kernel. The left-kernel certificate uses the same argument on
nonpivot rows. The producer uses elimination; the checker only uses products,
coordinate identities and the rank factorization. Empty kernels and rank zero
have explicit valid certificates.

The CLI binds the exact problem bytes by SHA-256. It accepts integers and
rational strings, rejects duplicate JSON keys and floats, and uses the Python
standard library. Limits are 64 rows and columns, input numerator/denominator
magnitudes at most 10^9, 1 MiB input and 32 MiB saved certificate. Exact rational
growth can increase runtime and certificate size. Each output numerator and
denominator is limited to 6000 bits. Larger exact outputs fail before
serialization and emit no partial certificate.

## Open next questions

Bind rows, columns and coefficients to actual source ports. Use the explicit
kernel basis to test the next proposed interface, then replay its native word.
Rational coordinates do not establish an integral or dyadic basis completion.
A rank factorization does not supply legal delivery, independent productive
targets, arbitrary-input restoration, physical storage or a complete invoice.

Credit classical Gaussian elimination and rank factorization, and the many
source-specific rank and kernel audits retained in this repository. This is
a reusable certificate interface, not a new rank theorem. Prepared for Ali
Romman with substantial OpenAI Codex assistance. Apache-2.0. No new kappa or
selected-frontier change.
