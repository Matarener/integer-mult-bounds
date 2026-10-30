# Stochastic precision on the first selected scalar block

This proof and its source-bound certificate were produced by Nick Petalas.
New work is Apache-2.0. The source word and its endpoint theorem are credited
premises. This proof neither re-establishes that endpoint nor changes it.

## The changed arithmetic contract

Read `research/p104-helper-subspace-splits/WORD.json.gz` at the base pinned in
SOURCES.json. Take the half-open program interval `[0,9589)`, stopping before
its first MOVE. All 9,589 events are ADD or SCALE at frame 3, the empty frame.
There are 9,358 ADDs and 231 SCALEs, on 748 public roles. The block touches
501 roles. No native frame change, initialization or erasure occurs inside it.
At a fixed stream sample, each real component is consequently a scalar linear
straight-line program with fixed rational coefficients.

Fix a grid spacing h > 0. All incoming scalar components, including every
dirty helper component, belong to h Z. An ADD computes x_r + q x_s exactly
before rounding once; a SCALE computes q x_r exactly before rounding once.
This is a macro arithmetic contract, not a claim about the source's scalar
bit implementation. There is no overflow or saturation. Integer-coefficient
updates remain exactly on the grid and do not round. For a noninteger dyadic
coefficient, write the exact updated scalar as h(a + theta), with integer a
and 0 <= theta < 1. Return ha with probability 1-theta, or h(a+1) with
probability theta, using a fresh draw conditional on the entire past. Exact
grid values remain exact. Both negative numbers and arbitrary dirty values
are included in this definition.

The source coefficients have denominator 1, 2 or 4. Since the current values
are on h Z, each noninteger update needs at most one or two fresh fair bits
for exact sampling. There are 7,421 such updates, with total denominator
logarithm 11,713. This bounds random bits per real sample for the literal
fixed-draw sampler. It does not price integer operations, random-bit access,
storage, routing or a full native implementation.

## Exact output influences

Let A_t be the exact update matrix for event t, and let d_t be its destination.
Let R be the set of the 7,421 potentially rounded events. Number events from
zero. Define the fixed output vector

    b_t = A_(L-1) ... A_(t+1) e_(d_t),    L = 9589,

where an empty product is the identity. For output j put

    S_j = sum_(t in R) b_t[j]^2,
    L_j = sum_(t in R) |b_t[j]|.

These quantities concern propagation of newly injected errors, independently
of the source's claimed endpoint map. The generated certificate computes
all 748 pairs exactly. Two separate algorithms agree. The reverse engine
starts from identity output columns, records each destination column before
transposing that event, and uses integer vectors with binary denominators.
The forward engine starts from zero formal errors, executes updates in their
original order and injects a new independent formal variable after every
event in R. It uses sparse Fraction dictionaries. Its final coefficients
supply S_j and L_j directly.

The resulting exact values are

    max S_j = 733/8, attained only at role 217;
    max L_j = 90, attained only at role 184;
    sum S_j = 32269/4;
    #{j : S_j > 0} = 282.

The complete outputwise list is emitted by verify.py, with source/package
hashes. There are 8,493 nonzero formal error coefficients at exit, with at
most 98 in any output row. These are coefficient occurrences, not distinct
program events. S_j is a sum over possible rounding sites, so it can be
conservative when some sites happen to lie exactly on the grid. No equality
claim for the worst actual stochastic variance is made.

## Conditional variance and tails

Let epsilon_t be the additive rounding error after event t. Conditional on
the past, it has mean zero, variance at most h^2/4, and two possible values
in an interval of length h. Set epsilon_t = 0 outside R. Because every
update is linear, the exact difference from the unrounded block is

    E_j = sum_(t in R) b_t[j] epsilon_t.

The weights are deterministic. Cross terms have zero expectation by
conditioning the later error on its past. Hence, for every allowed input,

    E[E_j] = 0,
    E[E_j^2] = sum_t b_t[j]^2 E[epsilon_t^2]
             <= h^2 S_j/4,
    E[sum_j E_j^2] <= 32269 h^2/16.

Errors generally are not independent. Their distributions can depend on
previous rounded states. Conditional zero mean is the property used here.

For completeness, a centered random variable in an interval of length h
satisfies E exp(lambda X) <= exp(lambda^2 h^2/8). Indeed, the second derivative
of its log moment generating function is a variance under exponential tilt.
Every tilted distribution has the same support interval. If a <= Y <= b,
E[(Y-a)(b-Y)] >= 0 gives Var Y <= (b-a)^2/4 after completing the square.
Integrating the derivative bound twice from zero proves the displayed
inequality for positive and negative lambda. Apply it conditionally at each
event, with lambda replaced by lambda b_t[j], then iterate conditional
expectation. Chernoff's bound, optimized at lambda = 4u/(h^2 S_j), gives

    Pr(|E_j| >= u) <= 2 exp(-2u^2/(h^2 S_j))    if S_j > 0.

An output with S_j = 0 has zero error. A union bound, requiring no independence
between outputs, therefore gives

    Pr(max_j |E_j| >= u) <= 564 exp(-16u^2/(733 h^2)).

This is an absolute-error statement. It has no input-magnitude factor,
first-order truncation or asymptotic remainder.

## A one-bit certificate improvement on this block

For h = 2^-6 and u = 1/2, the preceding failure bound is

    564 exp(-16384/733) < 2^-23.

The strict inequality has an exact rational certificate. Put x = 16384/733.
The verifier evaluates P = sum_(k=0)^64 x^k/k! and checks

    P > 564 * 2^23.

Since exp(x) > P, the claimed probability follows without a floating-point
exponential or logarithm. For complex scalars at one stream sample, apply
the same reasoning to both real and imaginary components. The simultaneous
componentwise failure probability is below 2^-22. At M samples, a union
bound multiplies these bounds by M; there is no all-stream assertion at
fixed failure probability. Independence between samples is not needed for
that union bound, provided each scalar update satisfies its own conditional
rounding contract.

For deterministic nearest rounding on the same block, the local error is
at most h/2. The exact absolute-influence certificate gives

    max_j |E_j| <= 45h.

To certify a strict error below 1/2 with h = 2^-g, this bound needs g >= 7.
At g = 6 it gives 45/64; at g = 7 it gives 45/128. Thus the stochastic
certificate uses one fewer fractional bit for a stated failure probability.
This is a comparison of sufficient certificates. It does not prove that
nearest rounding at six bits fails, or that stochastic six-bit precision is
optimal. The allowed initial 2^-6-grid inputs also belong to the 2^-7 grid.
The exact prefix endpoint need not be integral, so this observation does not
by itself imply integer recovery.

## Essential boundaries and rejection controls

Fresh conditional randomness is essential. For two updates y += x/2 with
x = 1 and y = 0 on the unit grid, reusing the same fair bit makes the final
error -1 or +1. Its variance is 1, while S_y/4 = 1/2. Each individual rounding
has the right unconditional marginal, which is insufficient. Always rounding
both ties down instead has bias -1. The verifier enumerates the fresh-draw
versions and checks their genuine conditional probabilities.

A later inverse word with fresh rounding need not restore the dirty inputs
exactly, even if its exact linear endpoint is the identity. For example,
y += x/2 followed by y -= x/2 can leave error -1 or +1 with positive
probability. The finite fixtures include this word. We do not claim exact
restoration from small expected error or a high-probability enclosure.

No MOVE is rounded or executed here. Initial off-grid conversion, native
frame operators, later scalar blocks, overflow headroom, correlated physical
error, bit-level sampling/costs, exact cleanup, compiler/stock admission,
analytic recovery and whole-multiplier error remain separate obligations.
The full selected source theorem is reused only as provenance, not audited.
The five selected framework assumptions are unchanged. Independent human
and formal proof-kernel review are unclaimed.

The rounding method and bounded-martingale argument are classical. See
Connolly, Higham and Mary, *Stochastic Rounding and Its Probabilistic Backward
Error Analysis*, SIAM J. Sci. Comput. 43 (2021), A566-A585,
https://doi.org/10.1137/20M1334796, for mean-independent stochastic rounding.
The fixed-grid proof above is self-contained. The contribution is the new
exact selected-block influence certificate and its explicit precision/failure
specialization, not a new general concentration theorem.
