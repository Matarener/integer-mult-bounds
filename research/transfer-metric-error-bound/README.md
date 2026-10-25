# Uniform operator error from a physical transfer metric

This package gives a finite exact certificate for a uniform operator-norm bound
on the complete fixed-transfer endpoint of PR5441. It checks the full local
input/output block operator. It has no factor from the growing payload dimension.
It is a sufficient contract, not a characterization of all bounded families.
The complete kappa calculation is unchanged.

## Contract and theorem

Use the predecessor's fixed table T[y,x], D virtual states, local dimension d,
left boundary F with p output roles and right boundary B with q input roles.
The complete physical endpoint E_f has entries

```
E_f[i,y_1...y_f ; j,x_1...x_f] = (F T[y_1,x_1] ... T[y_f,x_f] B)[i,j].
```

Let P be positive definite. Supply nonnegative real a,b,c with c<=1 and prove

```
F* F <= a P,
B* P B <= b I_q,
[sum_y T[y,x]* P T[y,x']]_(x,x') <= c (I_d tensor P).
```

The order is the positive-semidefinite order, and star is conjugate transpose.
The third inequality includes all off-diagonal x,x' blocks. Then, for every
positive integer f,

```
||E_f||_op^2 <= a b c^f <= a b c.
```

Here the norm is the full physical operator norm, with all input and output
roles. The bound applies to an error if the supplied table represents the
complete residual between an implementation and its exact target. It does not
follow from separately bounded entries or a few tested widths.

## Proof

Give the virtual space the norm from P. The local operator maps
`virtual tensor input-column` to `virtual tensor output-column`; its block
from x to y is T[y,x]. The third inequality bounds its squared norm by c.
First apply B to the input role, with squared norm at most b. Apply the local
operator to columns f,f-1,...,1, with identities on all other columns. This
order gives exactly T[y_1,x_1] ... T[y_f,x_f]. Tensoring by identities preserves
operator norm. Finally apply F, with squared norm at most a. Submultiplicativity
proves the displayed result. This reasoning sums coherently over the virtual
state and physical inputs; it never replaces operator norm by entrywise or
Frobenius norm. Thus it has no dimension factor. All p and q role blocks remain
in the two boundary inequalities.

The checker supports rational real tables and metrics. Rational Schur elimination
checks positive definiteness of P and positive semidefiniteness of the three
residual matrices. At a zero pivot, a nonzero remaining off-diagonal entry
rejects the matrix. Otherwise it removes the zero row or takes the exact Schur
complement. This is the standard PSD criterion; no eigenvalue tolerance is used.
The proof also holds over C, but complex certificate parsing is not implemented.

## Examples and limits

A two-state table with T[0,0]=I, T[1,1]=diag(1,-1), and other blocks zero has
F=(epsilon/2,-epsilon/2), B=(1,1)^T and P=I. Take a=epsilon squared/2,
b=2 and c=1. Its endpoint is epsilon times the odd-parity projector. Its norm
is exactly |epsilon| at every positive width. This gives a sharp certificate
without paying a factor 2 to the width from a Frobenius estimate.

Noncommuting rational virtual rotations and reflections give further exact
examples. A nonidentity metric checks invariance under a rational similarity
change; scaling each local operator by r gives the exact decay r to the width.
The source's slow-phase example is also checked in its real two-coordinate
representation. It has the safe uniform error bound two. Small early errors do
not make that bound small. No improved native recovery tolerance is inferred.

Per-input or per-entry checks are insufficient. The one-state local matrix
[[1,1],[0,0]] has unit-norm columns but operator norm sqrt(2). The full block
certificate rejects c=1. The transpose gives a second rejected coherent sum.
Singular/indefinite metrics, understated boundaries, understated rates, floats
and incomplete tables also reject.

A stable family can fail this certificate for the supplied representation.
Failure is not an instability proof. Finding P is a separate search. A change
of layout, varying table, unrepresented width schedule, or omitted dirty role
needs a new contract. Physical synthesis, bit precision, input conditioning,
tape access, recursive stock and exact recovery remain separate obligations.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/transfer-metric-error-bound
python3.12 -B research/transfer-metric-error-bound/certificate.py /path/to/certificate.json
```

Use the standard library. The JSON keys are `transfer_dimension`, `local_dimension`,
`metric`, `left`, `right`, `transitions`, `left_bound`, `right_bound` and
`squared_rate`. Integers and rational strings are accepted. The table is a full
d by d array of D by D matrices, including explicit zero blocks.

Registered normal and optimized checks use explicit exceptions. Literal complete
endpoint matrices corroborate the parity, noncommuting and slow-phase examples.
A separate determinant routine checks all principal minors for 125 symmetric
2-by-2 matrices and agrees with the PSD routine. The finite checks do not replace
the written all-width proof or establish independent human acceptance.

## Source and distinction

This answers Open next question 4 of zxv's
[PR #5441](https://github.com/CrocSwap/integer-mult-bounds/pull/5441), using its
[exact physical-table contract](https://github.com/zxv/integer-mult-bounds/blob/11fedb46fa199283f78282187c10aea432d8b0bb/research/finite-memory-lifting/PROOF.md).
Its exact endpoint theorem and slow-phase counterexample remain intact. The
new contribution is an exact sufficient approximation certificate in that same
contract. No predecessor executable is imported. The repository's Perron weight
work concerns recursive cost systems; this certificate concerns the physical
operator norm of a transfer table and includes coherent cross-input blocks.
Canonical base and proof-source objects are recorded in SOURCES.json. The overlap
search covered current open PRs, Discussions and all tracked in-scope notes;
unposted work and arbitrary historical diffs remain outside coverage.

## Open next questions

Extract a complete residual table from one real consumer and find a rational
metric that passes this test. Start with a numerical metric proposal, then
verify the rational inequalities exactly. Table size, a suitable metric, and
the source's complete role/version binding are the blockers. The resulting
operator bound must still fit a separately proved exact-recovery budget.

## Credit

zxv supplies the finite-memory physical contract, examples and approximation
handoff. The source retains the weighted-automata, matrix-product, native and
phase predecessors. Weighted operator norms, Schur complements and contractive
composition are classical. Ali Romman with substantial OpenAI Codex assistance;
Apache-2.0. No new general stability algorithm, physical supplier or kappa is
claimed. No independent human or proof-kernel acceptance is claimed.
