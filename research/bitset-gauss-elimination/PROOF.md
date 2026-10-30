# Equivalence of adjacency-bitset elimination

This implementation is produced by Nick Petalas. Quadratic Gauss-sum
elimination is classical. Ali Romman's PR5727 retains its contraction,
phase, state and finite-span contracts. The contribution here is this
implementation and its consumer and performance evidence.

The admitted input is a canonical polynomial on at most 256 Boolean variables,

```text
q(x) = c + sum a_i x_i + 2 sum_(i<j) b_ij x_i x_j  (mod 4),
c,a_i in Z/4; b_ij in F2.
```

Dictionary mask zero represents c. A one-bit mask represents a linear term;
a two-bit mask must have coefficient two. Zero dictionary coefficients,
other masks and nonintegral or Boolean parameters are rejected.

`unpack` retains the diagonal coefficients and the symmetric adjacency
rows as integer bitsets. `active` names the variables not yet summed.
The invariant is that the original sum equals the current Gaussian-integer
scalar times the sum of the remaining polynomial. Indices never change.
Inactive adjacency entries have no effect because every neighborhood is
intersected with `active` before use.

## One odd diagonal

Write the eliminated variable as x and its neighbor parity as L. Its terms
are `a*x + 2*x*L`, with a odd. Pointwise on the remaining variables,

```text
sum_(x=0,1) i^(a*x+2*x*L) = (1+i^a) i^(-a*L).
```

For any Boolean parity `L = XOR_(j in S) x_j`, its residue modulo four is

```text
L = sum_(j in S) x_j - 2 sum_(j<k in S) x_j x_k  (mod 4).
```

Terms involving at least three distinct variables have coefficient divisible
by four. Thus `-a*L` subtracts a from every neighbor diagonal and toggles
every edge inside S. `odd_step` performs those updates. The real/imaginary
update multiplies the scalar by `1+i` for a=1 and by `1-i` for a=3.

## One even diagonal with a neighbor

Choose a neighbor y. Write the remaining terms involving x or y as

```text
a*x + b*y + 2*x*y + 2*x*L + 2*y*M,
```

where a is even and L,M are parities excluding both x and y. Summing x
gives two when `y=t XOR L`, where `t=a/2`, and zero otherwise. Substitute
this value for y. Modulo four, the new contribution is

```text
b*t + b*(1-2*t)*L + 2*t*M + 2*L*M.
```

The constant increases by b*t. Each vertex in L receives the diagonal
increment `b*(1-2*t)`, and its internal edges toggle exactly when b is odd.
Each vertex in M receives diagonal increment 2*t. Expanding `2*L*M`
gives diagonal increment two on `L intersection M` and toggles each cross
edge once per ordered membership in L times M. A pair counted twice cancels.

For the row at vertex k, those cross-edge toggles are precisely

```text
(M if k in L else empty) XOR (L if k in M else empty),
```

with the self bit removed. These are `pair_step`'s updates, including the
intersection diagonal. The scalar doubles, and both x and y leave `active`.
This step does not divide by a polynomial coefficient.

## Isolated variable and termination

An isolated variable with diagonal two makes the entire sum zero. One with
diagonal zero multiplies it by two. These and the odd case exhaust isolated
variables. Each nonterminal iteration removes one or two variables. At most
n iterations suffice. The final constant rotates the scalar by its exact
quarter phase. The invariant proves that `gauss` returns `sum_x i^q(x)`.

The argument holds in every finite dimension. The supplied implementation
accepts only dimensions 0 through 256. It performs O(n squared) bounded
row or coefficient updates, counting a bitset operation as one operation;
this is not a constant-time bit-complexity assertion for unbounded n.

## Consumer boundary

`run_replay.py` authenticates the unchanged PR5727 package and substitutes
only its `gauss` function. Differential mode compares every result with the
original function, including each valid call inside the complete replay.
The replay still compares its whole result with its committed RESULT.json.
The original scientific theorem and its literal and signed-Pauli checks are
cited inherited contracts, not new research claims of this package.

`run_projection.py` generates five fixed 64-axis Clifford circuits. Each is
a full coordinate C layer followed by a symmetric quadratic diagonal, with
diagonal coefficients of the required parity. It uses the original Choi
constructor and original exact finite-span solver on four sources and one
target. Its kernel has 25 entries. Differential mode compares every Gauss
sum in this complete calculation. All other computations remain unchanged.
The fixed seeded fixture and algorithm are a computation benchmark, not a
new scientific approximation optimum or an admitted physical caller.
