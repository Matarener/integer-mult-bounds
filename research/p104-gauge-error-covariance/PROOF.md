# Complete gauge covariance and causal precision admission

Fix the exact PR5830 word and its retained frame implementation. Fields are
vectors in a finite-dimensional complex Hilbert space. Decoded native frame
changes are exact isometries before their stated completed defects. Initial
actual and ideal fields agree and each initial field has norm at most B.
The bit length of B and the conversion from a coordinate bound to this field
norm remain separate interface data.

COPY, including its displayed dyadic coefficient, INIT and CLEAR are exact in
this contract. MOVE, ADD and each emitted SCALE can add one defect after the
completed operation. At unit roundoff u the defect norm is bounded by u times:

| Operation | Local bound |
| --- | --- |
| MOVE | norm of its actual input |
| ADD d+=q*s | norm of actual d plus abs(q) times norm of actual s |
| SCALE d*=q | abs(q) times norm of its actual input |

This contract is different from a reset-residual contract. It does not implement
the exact primitives, the completed native child or their physical tape costs.
The source's local cost, ownership, frames and native proof dependencies stay
in force. No bound is transferred from another word without replay.

## Covariance under a time-dependent scalar representation

Let the physical representation of role r at cut c be g_(r,c) times its
normalized value. Each g is a nonzero signed power of two, constant on the
whole field. Native linear maps commute with that scalar. An ADD has physical
coefficient q*g_d/g_s; a SCALE has physical coefficient q*g_after/g_before.
The source word checks these identities at every event and preserves every
public boundary conversion. A diagonal depending on entries within the field
need not commute with a native unitary map; a rational unitary counterexample
is a control.

Divide a physical error by its current g. A physical local defect divided by
its output g obeys exactly the normalized local allowance. For example, ADD's
allowance becomes

`u*(norm(normalized d)+abs(q)*norm(normalized s))`.

The statement holds for arbitrary prior errors, not only the ideal trajectory.
For SCALE the same calculation uses its different input and output gauges.
Exact COPY and resets preserve the state relation without a new defect.
Thus the complete admissible defect sets correspond after normalization.

A public entry or exit conversion is a noisy identity in the normalized word.
It must remain a defect site. If a source SCALE becomes physical coefficient1
and is omitted, the normalized word still makes the source SCALE transition,
but that event has no defect. The reference timeline contains that physical
identity only as an exact virtual event. Deleting all such virtual events gives
the emitted physical word byte-for-byte as canonical data. They incur no new
physical cost, and no omitted physical operation is assigned a defect.

At event j, inject g_j times a formal normalized defect into the physical
word. The final public gauges are1, so every final signed coefficient must equal
the corresponding normalized coefficient. At an intermediate destination,
division by its current g gives the same signed response and score. This proves
the relation by induction, including arbitrary signs and all owned lifetimes.
The checker validates the local identities and source word, every prefix score,
all final signed coefficient hashes, peak witnesses and a separate transpose.
Literal aligned defects attain the independent normalized defect gain.

## Uniform score bounds

Let p_i be the exact ideal input row norm. At each physical defect site write
its allowance as `u*(B*a_j+c_j*E)`, where E is the largest error over all cuts
in the chosen field norm. Exact signed transfer gives coefficients C_(r,c),j.
Set J_(r,c)=sum(abs(C)*a), K_(r,c)=sum(abs(C)*c), and take separate maxima J,K.
If u*K<1, then

`E <= B*u*J/(1-u*K)`.

A final role r has bound

`B*u*(J_r+K_r*u*J/(1-u*K))`.

A strict bound below B at u=2^-g gives a bound below B*2^-t when u is replaced
by2^(-g-t), for every t>=0. In the normalized calculation E is measured after
division by the current g. In the ordinary calculation it is measured in the
physical representation. Neither bound is automatically better. At the final
public boundary both describe the same actual error.

The local ideal defect weight scales by abs(g_j), so the exact first-order
final J score is invariant between the two calculations with the same actual
defect sites. The feedback K and the all-prefix maxima can differ. This explains
why a direct physical calculation can beat the normalized uniform estimate.
These are sufficient bounds, not optimal physical precision.

## A stronger finite causal bound

A global E can overcharge feedback. The complete word permits a chronological
calculation. Maintain the exact signed coefficient row C_r for each field and
an upper bound d_k on each earlier defect divided by B. Then

`E_r = sum(abs(C_r,k)*d_k)`

bounds that field's error divided by B. Before a MOVE use feedback E_d; before
ADD use E_d+abs(q)*E_s; before SCALE use abs(q)*E_d. Set

`d_j >= u*(a_j+feedback_j)`.

Apply the exact linear row transition and insert the new unit defect column.
This induction is finite and triangular. It needs no stability denominator.
It retains signed cancellations within C; it does not propagate an absolute
matrix product through the word.

The implementation stores exact coefficient numerators at a proved common
power-of-two scale. It rounds each d_j upwards to a2^-96 grid. Every division
of a coefficient is exact, and every rounded defect is checked to be at least
its exact rational expression with excess less than one grid unit. The bound
is therefore rigorous; the grid is a checker representation, not machine
precision or an extra physical error. A separate direct rational oracle checks
36 small cancellation/scaling/reset examples. Controls reject omitted actual-
input feedback and downward rounding.

For t>=0, the same recorded d_j at u0 bounds the defects at u0*2^-t after
multiplication by2^-t. Inductively, prior field errors also shrink by2^-t;
substitution in the nonnegative local formula proves the assertion. Thus a
strict final bound below1 gives final error below B*2^-t at every t. The checker
finds the first passing integer guard and the adjacent failing upper-bound
certificate. Failure of an upper bound is not a lower bound on physical precision.
Monotonicity follows from the nonnegative causal formulas and upward rounding.

The complete bound includes all entry/exit conversions and the actual set of
omitted physical SCALEs. A separate field-norm headroom check adds the exact
ideal peak to the causal error peak. It is a bound relative to B, not a
dimension-free conversion from individual input record magnitudes.

## Scope and remaining work

The precise numbers, source pins and complete output coefficients are in
`RESULT.json`. The source's scalar optimum and norm/cost tradeoff belong to its
construction owner. This package does not optimize or emit another gauge word.
The physical reset/COPY implementation, native unitary and completed-child
contracts, final compiler execution, fixed tapes and analytic recovery remain
unadmitted. All five project assumptions keep their status. No new kappa follows.

## Sharp contract guard and a representation-invariant obstruction

`ADVERSARY.json` gives unit-bounded scalar initial fields. For target205, a
separate reverse row gives each completed defect's final response coefficient.
A literal forward run chooses its sign to agree with that coefficient and its
magnitude by rounding the actual permitted local budget down to a2^-96 grid.
Each scalar state lifts to a field vector by choosing one common decoded unit
vector and applying its current unitary frame. MOVE transports that vector;
ADD combines fields in the same frame. Thus the scalar trace is permitted by
the stated frame contract, including arbitrary-input initialization.
Every step checks the allowance on the actual perturbed inputs. The final error
also equals the separate adjoint sum. At19 guard bits the final error exceeds
1.79B for t=0, and1.79B*2^-32 for t=32. These are admissible traces, not just
failures of an upper-bound calculation. An over-budget defect is rejected.

Together with the20-bit causal theorem, the t=0 counterexample proves that20
is the least integer guard which guarantees the stated final error for all
t>=0 and every allowed defect trace of this exact completed-operation contract.
Any smaller guard allows the same19-bit trace. This is not a lower bound for a
particular hardware rounding rule, whose errors may obey stronger correlations.

There is a stronger obstruction to a pure representation search.
`FAMILY-ADVERSARY.json` uses defects only after source MOVE and ADD events.
Every SCALE, COPY, INIT and CLEAR is exact in this trace. Its final error exceeds
1.70B at19 guard bits, and1.70B*2^-32 with32 additional bits. Each defect uses
its actual input budget and passes the independent adjoint sum.

For any nonzero signed scalar gauge constant on each field, multiply each such
source defect by the gauge at its destination. The local covariance identity
preserves its relative allowance on the actual perturbed inputs. Set defects
on every boundary conversion and other SCALE to zero. Those are permitted
choices. Retain all native and ADD sites, and retain the exact normalized
transition when a physical unit SCALE is omitted. Induction preserves the
complete state relation, and unit public exit gauges give the same final error.
Thus this19-bit obstruction holds for every such representation of the same
source word, regardless of the scalar cost or ideal peak norm. It excludes a
better worst-case guard by pure gauges within this precise contract; it does
not exclude changed words, exact ADD/native implementations or stronger
rounding correlations. The verifier also transports both family traces
literally through the actual PR5830 word and checks every nonzero physical
defect allowance and final error.
