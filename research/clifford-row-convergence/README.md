# Finite-dimension convergence of the Clifford absolute Gram row sum

This scoped proof was produced by Nick Petalas. It adds strict dimension
monotonicity and an explicit convergence rate to Javier Vera / GosuBoy's
[PR #5714](https://github.com/CrocSwap/integer-mult-bounds/pull/5714).
The predecessor limit, residual correspondence and trace-lift identity are
cited inputs, not results audited by this contribution.

Let `N=2n`, `Q=2^N`, and let `c_(N,k)` count binary symplectic maps with
`rank(S-I)=k`. At tensor width `4n+4`, write

```text
R_N = sum_(k=1..N) c_(N,k) 2^(-k(N+1)),
T   = sum_(k>=1) 2^(-k(k+1)/2).
```

PR #5714 proves `R_N -> T`. The new finite-dimension result is

```text
R_(N+2) > R_N,
1/(2Q) <= T-R_N <= (4+T)/(3Q),             n >= 1.       (1)
```

Thus the convergence has the sharp order `4^(-n)`. The constants in the
two-sided envelope are not claimed optimal. This determines the rate for
the absolute row sum, not the optimal Gram eigenvalue or its convergence
rate. It gives no physical supplier, paid invoice or new kappa.

## Exact embedding product

For integers `l>=0`, define

```text
P_(N,l) = product_(j=0..l-1) (1-4^j/Q)   if l <= n,
P_(N,l) = 0                             if l > n.
```

The empty product is one. For every `k>=1`, including `k>N` with
`c_(N,k)=0`, the following residual-form average holds:

```text
p_(N,k) := c_(N,k) / 2^(Nk-k(k-1)/2)
         = (1/|GL(k,2)|) sum_(B in GL(k,2)) P_(N,k-r(B)),       (2)
r(B)    := rank(B+B^T)/2.
```

Powers with negative integer exponents are exact rationals. The average
in (2) is a mathematical formula, not a proposal to enumerate `GL(k,2)`
at large k.

To prove it, use the residual correspondence in kumagi's
[PR #5694](https://github.com/CrocSwap/integer-mult-bounds/pull/5694),
building on Ali Romman's
[PR #5526](https://github.com/CrocSwap/integer-mult-bounds/pull/5526).
It identifies symplectic maps of displacement rank k, with an ordered basis
of their residual space, with pairs `(E,B)` satisfying

```text
E injective, B invertible, E^T J E = B+B^T.
```

Every symplectic map has exactly `|GL(k,2)|` such bases. We retain that
correspondence without re-proving or independently certifying it here.

Fix B, put `r=r(B)` and `s=k-2r`. A change of basis makes its alternating
symmetrization a direct sum of r hyperbolic planes and an s-dimensional
radical. Count embeddings in this basis. Each hyperbolic pair in a
nondegenerate ambient space of dimension D has exactly
`(2^D-1) 2^(D-1)` ordered choices. Its orthogonal complement has dimension
`D-2`. After all r pairs, the s ordered radical vectors must be independent
and mutually orthogonal in a nondegenerate space of dimension `N-2r`.
After i of these vectors, their orthogonality equations leave
`2^(N-2r-i)` choices, of which exactly `2^i` are in the preceding span.

Consequently the embedding count is

```text
product_(j=0..r-1) [(2^(N-2j)-1) 2^(N-2j-1)]
  * product_(i=0..s-1) [2^(N-2r-i)-2^i]
= 2^(Nk-k(k-1)/2) P_(N,k-r).                         (3)
```

This calculation applies when `r+s=k-r<=n`. Otherwise such an embedding
is impossible: the remaining nondegenerate space has isotropic dimension
at most `n-r`. This explains the zero branch in P. Summing (3) over B and
dividing by `|GL(k,2)|` proves (2).

## Monotonicity and the rate

For fixed `l>=1`, `P_(N,l)` is nondecreasing when N increases by two. It
is initially zero if its dimension is unavailable. At the first available
dimension it becomes positive, and afterward every factor increases.
Equation (2) therefore makes every `p_(N,k)` nondecreasing. Also

```text
p_(N,1) = 1-1/Q,
R_N = sum_(k>=1) w_k p_(N,k),
w_k = 2^(-k(k+1)/2).
```

The sums for each N have finite support. The k=1 term increases strictly,
which proves `R_(N+2)>R_N`. The same term gives
`T-R_N >= w_1/Q = 1/(2Q)`, since every other deficit is nonnegative.

For the upper bound use the elementary product inequality
`1-product(1-x_j)<=sum x_j` for `0<=x_j<=1`. When `l<=n`, it gives

```text
0 <= 1-P_(N,l) <= (4^l-1)/(3Q).
```

When `l>n`, the left side is one and the right side is at least one,
so the same inequality holds. Since `k-r(B)<=k`, (2) implies

```text
0 <= 1-p_(N,k) <= (4^k-1)/(3Q).
```

This also covers `k>N`. Multiply by w_k and sum the nonnegative,
absolutely convergent series. Reindexing k by k-2 gives

```text
sum_(k>=1) w_k 4^k = 4+2T,
T-R_N <= (1/(3Q)) sum_(k>=1) w_k(4^k-1) = (4+T)/(3Q).
```

This proves (1) for every positive n. The two positive constants establish
the sharp order without asserting a leading coefficient.

## Evidence and reproduction

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/clifford-row-convergence/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/clifford-row-convergence/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/clifford-row-convergence
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/clifford-row-convergence --check-source-history
```

The standalone verifier enumerates literal ordered embeddings in dimensions
two and four and compares every alternating Gram type with (3), including
impossible types. It separately enumerates invertible forms through k=4.
For a distinct finite corroboration it implements the classical fixed-space
distribution of Rudvalis and Shinoda, as recorded in Fulman and Stanton,
[*On the distribution of the number of fixed vectors for the finite classical
groups*, Theorem 2.3](https://dornsife.usc.edu/jason-fulman/wp-content/uploads/sites/224/2023/06/fulman-stantonfinal.pdf).
That formula is prior art. No originality is claimed for the distribution.
It checks the new normalized-count identity through k=4 and the new rate
and monotonicity for n=1..32, using rational enclosures for T.

The verifier prints `PASS_CLIFFORD_ROW_CONVERGENCE` and a generated JSON
receipt binding all five package files by SHA256. It writes no files and
imports no predecessor code. The registered normal and optimized checks
each have a 120-second timeout. Python-managed allocation is a documented
Power of Ten deviation; finite domains bound every loop and collection.
All claim checks use explicit exceptions and remain active under `-O`.
The only indirect-call helper has four fixed rejection-test targets. Every
function is at most 33 physical lines. No separate Python linter or type
checker was installed; warning-strict normal and optimized execution are
the available runtime diagnostics.

Local checks enumerate 22,914 ordered embeddings and 78 alternating Gram
types, 20,336 invertible forms, and 128 residual-average comparisons.
They check 32 row sums, their 31 strict increases, and both gap bounds.
Twelve invalid-input or false-bound fixtures reject; two omitted-factor
controls distinguish the wrong product, and an unavailable-dimension
boundary control confirms the zero branch.

The written proof supplies the all-dimension statement. Finite checks are
corroboration, not formal proof-kernel or independent human acceptance.
Hosted CI status belongs in the PR body. It is not implied by a local pass.

## Sources, scope and credit

Canonical base is `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority
revision 8. SOURCES.json binds the retained predecessor text as provenance;
no external file or network access is a runtime dependency. The selected
baseline binding control passed. Its full scientific replay is outside
this algebraic side result and was not run.

GosuBoy / Javier Vera retains credit for #5714's lower product and limiting
absolute row sum. kumagi / Hiroki KUMAZAKI retains #5694's nonsingular-form
count and Gram envelope. Ali Romman retains #5526's residual-form,
trace-lift and tensor framework. Classical symplectic embeddings,
alternating-form classification and product inequalities retain their
prior-art status. The new contribution is the dimension-monotone residual
average and the explicit two-sided convergence-rate deduction in this
repository. No claim of global literature priority is made. Apache-2.0.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19219082)
changes the coverage-law card to this conditioning question. Live PR and
Discussion searches, merged-PR searches, main-tree keyword searches and
batch locks were checked. Sparse local note coverage, unpublished work
and arbitrary historical code diffs remain limitations of overlap search.
The account's separate odd-axis spectral result #5883 is not extended;
this package studies the phase-insensitive absolute row sum from #5714.

## Open next questions

What is the exact leading coefficient of `4^n(T-R_(2n))`? Start with (2),
justify a summable first-order expansion, and evaluate the resulting
symmetrization-rank average over nonsingular binary forms. This would
sharpen the error term rather than settle the spectral optimum. The
necessary average has not been evaluated here. TASK.json records the
structured question. No follow-up is reserved.
