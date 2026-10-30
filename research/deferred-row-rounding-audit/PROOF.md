# Completed-row projection and internal rounding are different operations

Scoped audit of the deferred-row boundary in selected PR6030's inherited
support-local supplier, and of the precision obligation retained by PR6115.
No new kappa or physical supplier is claimed.

## 1. Actual source boundary

The selected copy of PR1673 `SUPPLIER-SUPPORT-AUDIT.md` §3 deletes added zero
rows after a completed phase, restores exposure, and starts the next phase
at the original volume. Section 7 supplies the normalized real tensor
`H0 = (1/2)[[1,1],[1,-1]]`, followed by the exact scaling `2^g` to obtain the
raw H tensor. `OUTER-TRANSFER-AUDIT.md` §5 has the same completed-row boundary.

`FINITE-TEMPLATE-CLOSURE.md` explicitly keeps a fixed fine grid: a child is
never rounded, compressed or re-encoded at return. This audit does **not**
claim to find a rounding bug in that source or in PR6030. Its object is the
following conditional implication for a future implementation with declared
rounding defects, which cannot be inferred just from an exact endpoint.

Use the coordinate sup norm on real arrays; real and imaginary components
can be treated separately for this real H0 map. Coefficient overflow is
excluded by premise. Range/precision guards and physical erasure are separate.

## 2. Projection theorem

Let E append zero rows, P select the original rows, and Q be an exact exposure
permutation. Their induced sup norms are one, and PE=I. Let U be the exact
completed phase, with `U E = E T`, where T acts on the original array and the
added rows return to zero. Suppose an implementation F, possibly nonlinear,
obeys, for every admitted computed input z,

    ||F(E Q z) - U E Q z||_infinity <= delta(z).

The implemented phase is `Q^-1 P F(E Q z)`. Its error relative to
`Q^-1 T Q z` is at most delta(z), by applying the norm-one projection and
permutation. **No test that the computed added rows are exactly zero is
necessary for this numerical conclusion.** Deleting their nonzero residuals
after the completed phase is a projection, not a new additive error.

This statement presupposes that deletion leaves retained coefficients
unchanged. It provides no free machine operation, reversible erasure protocol,
zero-scratch premise, or permission to delete a row still read by the program.
One may also use a bound on the projected defect directly; a full padded-array
error bound is sufficient but can be unnecessarily large.

For numerical retained-output correctness alone, the weaker condition PUE=T
would suffice. It does not imply clean return. Indeed omitting the last
cleanup shear in §4 preserves retained x exactly while leaving z+Mx in the
added row. The checker therefore verifies the entire padded-phase endpoint,
separately from the retained endpoint. Neither norm bounds nor retained-column
tests alone discharge the source's owned-erasure/return contract.

## 3. Exact sharp coefficient for an internal-error contract

Write an exact linear straight-line program as maps A_1,...,A_m. Dimensions
may change: padding and projection are allowed. Suppose after designated
steps t a defect e_t is added in specified coordinates via an injection B_t,
with `||e_t||_infinity <= u_t`. There is no probabilistic assumption. Define

    S_t = A_m ... A_(t+1) B_t.

Unrolling the actual computed recurrence, even when each e_t depends on the
computed state, gives the exact endpoint error

    error = sum_t S_t e_t.

Thus the following input-independent coefficient is an exact worst-case
bound for the independent defect-box contract:

    D = max_output_row i sum_t u_t sum_j |(S_t)_(i,j)|.       (1)

The upper bound is the triangle inequality in each output row. It is sharp
for real arrays: choose a maximizing row i and set each defect coordinate
to `u_t sign((S_t)_(i,j))`. All terms in that row then have the same sign and
sum to D. This also proves sharpness when dimensions change. If some defects
have additional correlations, such as those from a specific quantizer, (1)
remains an upper bound but need not be attainable. We make no optimality
claim for nearest-even rounding.

The terminal projection is inside every suffix S_t. Dropping padded columns
from B_t before their final read is generally invalid. Conversely, keeping
discarded *output* rows in the maximum can overestimate the required precision.

## 4. Two-row counterexample, with arbitrarily large amplification

Let x be retained and z be an added row, initially z=0. For positive rational
M,a execute, in this order,

    z <- z + M x
    x <- x + a z
    x <- x - a z
    z <- z - M x.

The exact endpoint is identity on **both arbitrary inputs** x,z. Now add a
defect epsilon to z immediately after step 2. The endpoint becomes

    retained x: x - a epsilon,
    padded z:   z + (1 + M a) epsilon.

Deletion after step 4 leaves retained error `-a epsilon`. Thus the claim
"this error is in a row that will be deleted, so it has no output effect"
is false. Taking a arbitrarily large also falsifies an endpoint-norm-only
rounding allowance: the exact endpoint norm is one, but the relevant internal
error amplification is a.

This can be a literal rounding event. Choose M=1/2, a=4, x=1, z=0. After
step 2 the state is (3,1/2). Round z to the nearest integer, with ties to even,
giving epsilon=-1/2. The completed state is (3,-3/2), and retained x has error
2 although the sole rounding error was 1/2. This is a counterexample to the
shortcut, **not** to the selected fixed-grid algorithm.

The opposite distinction is equally important. With a=1 and M=2^k, a defect
epsilon only in z at that cut leaves retained error `-epsilon`, while the
discarded output error is `(1+2^k)epsilon`. For this particular defect channel,
the full padded-output norm overstates retained error by exactly `1+2^k`.
Equation (1) accounts for both examples without treating any internal error
as free. It does not assert this factor for every defect in a complete word.

## 5. Deferred phases and the actual H0 recovery scale

For the source H0 kernel, the row-sum sup norm is one. Tensor products on
disjoint selected coordinates and exposure conjugations also have norm one.
Let T_j be such an exact completed phase, and let its computed phase satisfy

    z_(j+1) = T_j z_j + d_j,    ||d_j|| <= Delta_j

on the actual computed input. Then induction gives

    ||z_J - T_(J-1)...T_0 z_0|| <= sum_j Delta_j.            (2)

The phase may include a direct small-width tail. No equal phase sizes or
zero reserved inputs are required. Padding/deletion introduces no extra
multiplicative factor. If the input itself has error E_0, add E_0 to (2).

The caller's raw H recovery multiplies by `2^g`. If that shift is exact and
has sufficient range, the final error is bounded by

    2^g (E_0 + sum_j Delta_j).                             (3)

In particular a sufficient common phase budget for desired raw error eps
and exact input is `Delta_j <= eps/(J 2^g)`. For nonlinear rounded phases,
each Delta_j must hold on the reached input domain; checking only ideal
inputs or only input basis columns is insufficient. For general phase norms
L_j, replace (2) by `sum_j Delta_j product_(k>j) L_k`; the no-amplification
claim is specific to the normalized H0 endpoint. This does not remove the
source's magnitude guard or its O(g) recovery-scale allowance.

## 6. Concrete complete finite check

The checker builds an eight-coordinate-data input (three address bits),
exposes selected bits 1 and 2, and pads two four-entry rows to three. Inside
the first phase it uses the four shears above between the first original row
and the added row, followed by H0 on the active bit. It deletes the added row,
undoes exposure, then applies H0 to the deferred selected bit. The exact
complete matrix is checked against the closed two-bit Walsh formula, with
arbitrary values in both original rows and the spectator factor.

This is a small explicit surrogate for the **numerical interface**. It is
not an emitted PR6030 child, a legal native construction, or a paid compact
router. It intentionally allows temporary cross-row mixing before exact
return. No physical running-time or precision improvement is inferred.

The verifier computes (1) from exact rational suffix matrices and separately
constructs attaining defects by forward execution. It also enumerates every
input in a stated finite ternary cube through nonlinear nearest-even rounding
and checks its error against (1). This is stronger than testing basis vectors
for that nonlinear question, but remains a finite corroboration. The proof
above carries the quantified implication. Private-copy mutations test failure
detection, including premature row deletion and an omitted recovery scale.

## 7. Scope and attribution

This resolves a numerical projection implication conditional on supplied
gate-defect or completed-phase bounds. It supplies neither the actual
PR6030 bounds nor physical deletion/owned-erasure costs. All five framework
assumptions remain. No new kappa, native replay, rounded multiplier, proof
kernel, or independent human acceptance is claimed.

Credit Vlado Vojdanovski's PR1673 support-local construction, the selected
finite-template/outer-transfer authors, DreamingOfClouds and the P104 lineage,
JosieElliston's PR6110 question, and DLamdata's concurrent PR6115 cost audit.
The telescoping-error and induced-norm tools are standard; the scoped result
is this row-boundary audit, sharp channels, and independently checkable finite
package. Prepared by @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0.
