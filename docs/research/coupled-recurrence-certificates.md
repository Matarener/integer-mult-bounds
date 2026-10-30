# Check a complete nonnegative coupling matrix

Separate type checks can miss a cycle that consumes the whole margin. This
tool constructs an exact certificate for a declared nonnegative rational
matrix A, with nonnegative forcing b. It produces one of two alternatives:

- Positive weights w and a rational q<1 with Aw<=qw. It also gives the exact
  total u=sum A^k b, characterized by u=Au+b.
- A nonzero nonnegative vector v with Av>=v. No positive strict contraction
  weights exist for this matrix.

```sh
python3 -B scripts/certify_coupled_recurrence.py \
  tests/fixtures/coupled-recurrence/barrier.json > certificate.json
python3 -B scripts/certify_coupled_recurrence.py \
  tests/fixtures/coupled-recurrence/barrier.json --check certificate.json
```

The fixture source is pinned to main `de5ec2e7a6074068452f45b1a191b5c72832df4a`.
The window-barrier README SHA-256 is
`9fd738d926741f8691120aa91b342c5eb9f2f05b227858ba1eeda1a3ee5bc9f0`.

The fixture normalizes the explicit retained matrix in
[the window barrier](../../research/window-comparison-barrier/README.md) by its
diagonal (4,5,3). Its total is (49/156,10/39,83/234), the same published least
barrier. The [coupled-update example](../../research/coupled-comparison-barrier/README.md)
changes entries A01 to 9/4 and A10 to 7/15. Each change alone is safe; together
they produce the exact witness v=(9/4,1,0). This interface adds a constructive
alternative for arbitrary bounded matrix dimensions and standalone receipts.
It does not claim a new M-matrix theorem or repeat source admission.

## Why the producer always supplies an alternative

Set M=I-A. Its off-diagonal entries are nonpositive. Eliminate columns in order
without row swaps while the diagonal pivots are positive. Each Schur complement
still has nonpositive off-diagonal entries. At the first nonpositive pivot k,
set v_k=1, later entries to zero, and solve the earlier triangular equations
for v. Their positive diagonal and nonpositive upper entries give v>=0. Earlier
rows of Mv are zero; row k is nonpositive; later rows are nonpositive because
their relevant original off-diagonal entries are nonpositive. Thus Av>=v.

If every pivot is positive, forward and backward substitution preserve
nonnegativity. Solving Mw=1 gives w>0 and Aw=w-1<w. Solving Mu=b gives u>=0.
The weighted maximum norm contracts by q=max_i (Aw)_i/w_i<1, so the geometric
series converges to the unique u. The separate checker only multiplies matrices
and vectors. It checks these inequalities and the fixed-point equation; it
does not trust elimination pivots or recompute the solve.

For the negative alternative, choose an index maximizing v_i/w_i for any
proposed w>0. Monotonicity of A contradicts Aw<w if Av>=v. This also covers
singular and reducible matrices, without a floating eigenvalue calculation.

## Scope and next use

Input fields are `schema: coupled-recurrence/v1`, square `matrix` and `forcing`.
Use integers or rational strings. Limits: 64 types, coefficient numerator and
denominator at most 10^12, and 2 MiB input. Arithmetic is exact; rational growth
can increase runtime. Each certificate numerator and denominator is limited
to 6000 bits. Larger exact outputs fail before serialization and emit no
certificate. This is not a bit-complexity claim.

If A bounds actual costs from above, a positive certificate transfers to those
costs. Failure of that upper bound does not prove failure of the actual costs.
A negative certificate for a lower bound can rule out strict contraction.
Even Av>=v does not show that every forcing vector causes divergent work: a
zero or unreachable forcing can miss the bad component.

## Open next questions

Bind the matrix, forcing and reachable types to one complete source recurrence.
Include every child, adapter and restoration cost. For numerical recovery,
bind each normalized row to its actual comparison matrix. Neither use alone
discharges all-size compiler, precision, native or outer assumptions.

Credit classical M-matrix and Perron-Frobenius theory; Nick Petalas's least
barrier, Ali Romman's coupled-update proof, David Ganz / Dugongue's inverse
interface and Jose Manuel's retained setup fixture, with their predecessor
lineage. Prepared for Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. No new kappa or selected-frontier change.
