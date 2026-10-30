# Omit the three outer frequency reversals

This contribution is produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Contract and source premises

Fix any parameters admitted by the complete convolution caller of Jose Manuel's
PR3709, with its complete rounded Fourier endpoints from PR3640. Write
`a_i` for the address-bit lengths, `A=sum_i a_i`, `M=2^A`, and `r=2^ell`.
The coefficients belong to `C[X]/(X^r+1)`. All rows and coefficients within a
record retain their original order. Let B permute the M address records in
each outer row by reversing the bits within each axis. It fixes coefficients,
real/imaginary components, and outer rows, and satisfies B^2=I.

We use the predecessor endpoint and normalized-product theorems as premises.
We do not reprove native suppliers, exact-grid refinement, the physical word
multiplier, twiddle approximation, or the multiplication theorem.

Let Q denote the predecessor's component truncation to the specified grid.
Its complete natural-order forward and opposite endpoints are

    F(x) = Q(W_minus x / M),
    G(x) = Q(W_plus x / M).

Section 2 of PR3640's PROOF gives the raw round endpoints
`B W_minus/M` and `W_plus B/M`. Its execute method materializes B after forward
rounds and before opposite rounds. Section 3 proves that the lifted grid is
exact through all intermediate rounds. B permutes whole words without changing
them. Removing the forward reversal therefore gives exactly

    F_raw(x) = B F(x).

Removing the opposite reversal gives exactly

    G_raw(x) = G(B x).

These statements include the actual endpoint truncations: Q(Bx)=B Q(x).
They do not infer bitwise equality from an error estimate alone.

The physical RingProduct returns the same rounded polynomial operation on
each record. Define it as P(x,y). Its exact contract is
`Q_p(x_j y_j/r)` separately at every record j. The same parameters and
arithmetic apply at each record, so

    P(Bx, By) = B P(x,y).

This is equivariance under a permutation of complete polynomial records.
It uses no multiplicativity of component truncation. It does not permit B
to permute coefficients within a polynomial or different B on the two inputs.

## Complete equality

The changed caller uses the unchanged Convolution code with one private
Fourier subclass whose reversal method does no routing. Its intermediate
Fourier API deliberately has the raw convention above. No raw Fourier object
is returned by the adapter factory. The externally returned complete caller
retains the original natural-order convolution API.

Let S be the final exact M scale and width expansion in that caller. Then

    S G_raw(P(F_raw(x), F_raw(y)))
      = S G(B P(B F(x), B F(y)))
      = S G(B B P(F(x), F(y)))
      = S G(P(F(x), F(y))).

The equality is between complete rounded outputs, including their signed bit
encoding and unchanged width `p+2+A`. It holds for every input satisfying the
predecessor's disk-grid contract, every admitted row count, long/short axis
pattern and precision. It is a scoped program-refinement theorem, conditional
on those inherited contracts, rather than a claim that finite tests cover
all parameters.

The original reported error bound `4 sqrt(2) M 2^-p` from `(x*y)/(rM)` transfers
by equality. The same final disk-margin obligation remains before narrowing.
There is no new approximate arithmetic or guard allowance.

## Ownership and exact routing reduction

The skipped routine reads geometry and routes only the current owned payload.
It leaves flags and encoded counts at their required origins. Its completed
router and temporary descriptor are erased. Replacing it by the identity on
the current owned packet leaves the same ownership state at the next stage,
with fewer child invocations. Every retained root, product, grid conversion,
output width port, input rewind and cleanup is the inherited implementation.
The changed intermediate values obey the same coefficientwise disk and grid
bounds because B is a permutation. Thus the retained preconditions hold at
every subsequent call. Borrowed inputs and metadata remain preserved; all
owned scratch and both protected return ports retain the original lifecycle.
This argument does not erase arbitrary external dirt or introduce fresh state.

For P_precision=p+A, the source batches complete coordinate transpositions at
capacity

    b = 2^floor(997 floor(log2(P_precision))/1000).

One reversal emits exactly

    E = sum_i floor(a_i/2)

edges. The source's loop flushes each b edges and then the remainder. Hence
there are exactly `ceil(E/b)` nonempty sparse-router invocations per reversal,
with the convention ceil(0/b)=0. The three complete transforms use identical
parameters. The new program therefore removes exactly

    3 ceil(E/b)

of these outer sparse-router invocations, their descriptor generation/sorting
and materialized returns. All six root calls, three diagonal passes, three
lifts, three truncations, one polynomial product and final M scale in the
four-address fixture remain. No claim is made about router calls internal to
a root or the polynomial product, a measured speedup, or a recursive supplier
histogram change. For a_i=2 and p=3, E=1, b=2, so the reduction is exactly three
outer routing invocations. When E=0 the stated routing reduction is zero.

## Prior work and new scope

Matching DIF/DIT frequency order is classical FFT practice. The upstream
synthetic interface already has compatible raw endpoints. Androolloyd's
PR673 includes bit-reversed-order convolution in an indexed-read exact
reference. PR3709 also uses the same idea inside the polynomial product's
own coefficient FFT. These are credited precedents, not new general algebra.

PR3640's Open next question 2 asks for a complete product consumer retaining
the alternative convention. PR3709 subsequently supplies the required
physical record-local product, while its outer caller still uses three
natural-order Fourier endpoints. The new result is the source-bound adapter
for that actual fixed-tape caller, its bitwise refinement proof, exact batching
reduction, and a finite nonidentity-B execution. This does not extend the
indexed-read model by merely changing its group or target.

Production GL64/O73 execution, complete Gaussian/CRT/recovery joins, supplier
admission and all five selected framework assumptions remain outside this
contribution. The selected frontier is unchanged.
