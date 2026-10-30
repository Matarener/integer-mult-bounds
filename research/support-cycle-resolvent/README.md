# Sharp inverse bounds with forbidden diagonal entries

This contribution was produced by Nick Petalas. Apache-2.0.

The exact inverse envelope under unequal row contraction budgets remains
computable when arbitrary diagonal entries are forbidden. A maximum-product
return cycle replaces the root self-loop in the denominator. In a two-vertex
example the sharp bound is **14/5**, whereas allowing the diagonals gives **6**.

This is a scoped algebraic proof with exact finite corroboration. It claims
neither a new multiplication exponent nor a Gaussian-specific bound. The new
step removes the all-diagonals-allowed hypothesis of Ali Romman's
[PR #5306](https://github.com/CrocSwap/integer-mult-bounds/pull/5306) and
[PR #5255](https://github.com/CrocSwap/integer-mult-bounds/pull/5255).
Those predecessor theorems are cited, not audited or replayed.

## Statement

Let G be any finite directed graph on n >= 1 vertices, with self-loops
optional. Fix real row budgets 0 < r_i < 1. Admit all complex n by n matrices
E satisfying

```text
E_ik = 0 unless i -> k is an edge of G,
sum_k |E_ik| <= r_i.
```

An allowed entry may be zero. The matrix norm below is the induced 1-norm,
the largest absolute column sum.

For each root j, put w_jj = 1. For i != j, let w_ij be the largest product of
row budgets along a simple directed path from i to j, excluding the terminal
vertex j. If there is no path, put w_ij = 0. Let q_j be the largest product of
row budgets around a simple directed cycle containing j. A self-loop at j
counts as a cycle of length one. If no such cycle exists, put q_j = 0.

Then every inverse exists and

```text
max_E sum_i |((I-E)^-1)_ij| = sum_i w_ij / (1-q_j),

max_E ||(I-E)^-1||_1 = max_j [sum_i w_ij / (1-q_j)].
```

For every root, one nonnegative real matrix attains the entire displayed
column entry by entry. Each row of an attaining matrix has at most one
nonzero entry, equal to that row's budget. The attaining matrix can depend
on the root; simultaneous attainment of all columns is not asserted.

## Proof

Fix j and abbreviate w_i = w_ij. The weight of every nonempty directed cycle
is strictly less than one. Removing a cycle from a walk therefore increases
its weight. Maximum-product walks from i to j can be taken simple, stopping
at their first arrival at j. In particular 0 <= w_i < 1 for i != j.

With the maximum of an empty set defined as zero, these weights satisfy

```text
w_i = r_i max_(i -> k) w_k                 for i != j,
q_j = r_j max_(j -> k) w_k.
```

For the first identity, prefixing an edge to a maximizing path gives a walk;
removing any repeated cycle can only improve it. Conversely every maximizing
nonempty simple path begins with an allowed edge. For the second identity,
an edge out of j followed by a simple path back to j is a simple cycle
through j. The self-loop case uses w_j = 1. A cycle elsewhere cannot replace
this root-specific return cycle. All factors are below one, so 0 <= q_j < 1.

Set h_i = w_i/(1-q_j). The preceding identities give

```text
h_i = r_i max_(i -> k) h_k                for i != j,
h_j = 1 + r_j max_(j -> k) h_k.
```

For any admitted E, put B = |E| entrywise. The row budgets imply
B h <= h-e_j, where e_j is the j-th coordinate vector. Because the graph is
finite, rho = max_i r_i < 1. Thus ||B||_infinity <= rho < 1, and its Neumann
inverse is nonnegative. Multiplying the last inequality by that inverse gives

```text
(I-B)^-1 e_j <= h.
```

The absolutely convergent Neumann series also gives
`|(I-E)^-1| <= (I-B)^-1` entrywise. This proves the claimed upper bound for
every entry in column j, including arbitrary complex phases and diffuse rows.

For attainment, at every i != j with w_i > 0, choose one allowed successor
k satisfying w_i = r_i w_k and set E_ik = r_i. Put zero in all other entries
of that row. When w_i = 0 use the zero row. At the root, if q_j > 0 choose a
successor satisfying q_j = r_j w_k and set E_jk = r_j; when q_j = 0 use the
zero row. Every choice exists by the finite maximum identities.

This matrix is nonnegative, obeys the support and row budgets, and satisfies
`(I-E)h = e_j` exactly. Since ||E||_infinity < 1, its inverse exists, and its
j-th column equals h. This proves full-column attainment. Choosing a root
maximizing the finite column formula proves the matrix norm formula.

## Strict improvement and examples

Adding self-loops does not change any maximum-product path weight, because
loops only reduce walk weights. If the loop at j is allowed, q_j = r_j. If it
is forbidden, q_j < r_j: every possible return cycle has at least one
additional factor strictly below one, and there are finitely many simple
cycles. Consequently, forbidding that loop strictly lowers the sharp bound
for column j relative to diagonal completion. If G has no self-loops, the
sharp matrix 1-norm is strictly below its diagonal-completed counterpart.
This is a comparison of two admitted matrix classes, not a source mutation.

For edges 0 -> 1 and 1 -> 0 with budgets 1/2 and 3/4, the attaining matrix is

```text
E = [[0, 1/2], [3/4, 0]],
(I-E)^-1 = [[8/5, 4/5], [6/5, 8/5]].
```

Both return factors are 3/8. The column sums are 14/5 and 12/5, so the exact
norm envelope is 14/5. Allowing both diagonals gives the larger envelope 6.

For the acyclic path 0 -> 1 -> 2 with budgets 1/2, 3/4, 1/4, every q_j is
zero. The sharp norm is 17/8, the sum 1 + 3/4 + 3/8 in the final column.

With unequal budgets, the maximizing return cycle need not be the shortest.
For edges 0 -> 1 -> 0 and 0 -> 2 -> 3 -> 0, with budgets
1/2, 1/10, 9/10, 9/10, the longer return product 81/200 exceeds 1/20. The
root-0 column envelope is 562/119. This fixture rejects a shortest-cycle
substitution in the unequal-budget formula.

## Exact finite evidence

The standalone [verifier](verify.py) uses maximum-product dynamic programming
for the formula and separate rational Gauss-Jordan inversion for observations.
It enumerates every directed support on one through three vertices with at
least one forbidden diagonal, and every row-budget assignment from {1/3,2/3}.
Thus it spends its main enumeration on the changed hypothesis.

The complete run checks 3,634 support/budget cases, 50,334 zero-or-saturated
single-successor policy matrices, 10,850 constructed attaining columns, and
10,902 diffuse signed or nonnegative matrix evaluations. Counts are evaluations
in their declared graph/budget domains, not counts of distinct matrices after
deduplication. The policy oracle compares every entry maximum with the proposed
full column, and a single constructed witness is inverted to check simultaneous
attainment within that column. The continuum upper bound is the written proof,
not an inference that policy enumeration covers arbitrary diffuse matrices.

The explicit examples above and a root-disconnected cycle fixture distinguish
self-loop, zero-return, unequal-cycle and root-specific behavior. Ten rejection
controls cover invalid dimensions/budgets/neighbors/root, forbidden diagonal
entries and overspent rows. Checks use explicit exceptions and remain enabled
under optimized Python. No predecessor verifier is imported or executed.

From the repository root, using CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/support-cycle-resolvent/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/support-cycle-resolvent/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/support-cycle-resolvent
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/support-cycle-resolvent --check-source-history
```

Any CPython 3.12 executable can replace the displayed path. Each direct run
prints `PASS_SUPPORT_CYCLE_RESOLVENT` inside a generated JSON receipt binding
all five package files by SHA256. Optional `--receipt /absolute/external/path`
exclusively creates that receipt outside the checkout. Normal replay writes
no files. The registered runner prints `PASS_REGISTERED_RESEARCH_PACKAGE`.
The standalone checker also works from a Git-free package export.

## Scope and credit

This is a changed conditioning side question under `uniform-transfer-audit`,
not discharge of a selected framework assumption. Base main is
`de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8. The card's
selected source-binding orientation passed after sparse inputs were materialized.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19213524)
records the optional-diagonal premise and overlap coverage. Current scientific
sources remain governed by `certificates/selected-result.json`.

Credit Ali Romman for #5255's common-row support optimum and #5306's unequal-row
extension with diagonal entries allowed. Credit Cinna Davis #4100 for the
conditioning context and James Reed #4282 for periodic sections. William
Lawyer #852 treats different bounded weighted cycles. Their results and all
retained source notices remain unchanged. Neumann comparison, discounted-path
and maximum-principle methods are classical; general literature priority is
unclaimed. [SOURCES.json](SOURCES.json) pins the two cited predecessor READMEs
as provenance, with no runtime dependency or imported scientific evidence.

The theorem is finite-dimensional with every r_i strictly between zero and
one. It permits arbitrary complex coefficients and arbitrary support, but does
not settle row budgets equal to or above one, mandatory nonzero edges, a
Gaussian-specific class, operator 2-norm optima or infinite graphs. Source-bound
row estimates and physical preparation, native operations, compiler, ownership,
precision/tape, stock and analytic recovery remain outside scope. No selected
cold replay, native replay, Lean, Docker or predecessor scientific suite was
run. Independent human and formal proof-kernel review are unclaimed.

Power-of-ten inspection: no recursion or dynamic code generation; loops have
fixed finite fixture bounds, graph dimension is capped at six in internal
helpers, exhaustive graph tests use n <= 3, and the policy oracle uses n <= 4.
Every function is below 60 lines. Python Fraction arithmetic and collection
allocation are a managed-runtime deviation from fixed allocation. Fixed fixture
dimensions and fixed rational budgets bound live data and coefficient sizes;
there is no externally supplied graph. The ten failure controls use a bounded
list of local callables, a deviation from avoiding indirect calls that keeps
rejection cases explicit. Warning-strict normal and optimized replay provide
the available standard-library diagnostics. A larger public solver would need
new input/resource contracts and dedicated static analysis.

## Open next questions

- Can one emitted rounded coefficient matrix provide both a proven sparse
  support with missing diagonal entries and heterogeneous row budgets? Extract
  the exact support and rational budgets, then apply the return-cycle formula
  and charge their preparation. Actual source binding and physical costs are
  missing; this abstract improvement alone does not admit a supplier.
- Which additional entrywise constraints prevent the concentrating attaining
  policies? Begin with one actual matrix class and its per-entry bounds.
  The current envelope permits each row to concentrate its entire budget on
  one allowed edge, so it cannot price a restriction that forbids concentration.
