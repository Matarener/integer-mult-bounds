# Completed-operation precision contract

Fix the exact word in `inputs/WORD.json.gz`. Let each decoded field be a vector
in one finite-dimensional complex Hilbert space. Assume that the native maps
and frame gauges preserve this norm and implement decoded identity. This is a
premise. This package does not implement or admit that native supplier.

Let every initial coordinate, including an owned coordinate before its first
reset, have norm at most B. The ideal operations have the published semantics.
Every ideal COPY destination is zero. The actual completed COPY performs
`d += q*s`, so a destination error survives. Each INIT and CLEAR resets to zero,
then adds a residual. Each other completed operation can also add a defect.
The actual and ideal initial vectors are equal. Errors at the initial boundary
would need a separate term.

For unit roundoff u, impose these local bounds on the norm of the defect:

| Operation | Bound divided by u |
| --- | --- |
| MOVE | norm of its actual input |
| ADD or additive COPY | norm of actual d plus abs(q) times norm of actual s |
| SCALE | abs(q) times norm of its actual input |
| INIT or CLEAR | norm of its actual input before reset |

These are mathematical allowances. They do not supply a reset implementation,
a cost, a tape schedule, or a bound for a child operation which is not complete.
In particular, bounded final residuals do not imply exact owned zero return.

Let p_i be the exact sum of the absolute ideal input coefficients in role i.
The verifier computes these coefficients with rational arithmetic over every
input column. At each event j define a_j and c_j as follows. For MOVE and reset,
they are p_d and 1. For ADD they are p_d+abs(q)p_s and 1+abs(q). For SCALE they
are abs(q)p_d and abs(q). For COPY they are abs(q)p_s and 1+abs(q), since its
ideal destination is zero. Thus the defect at j is at most u(B*a_j+c_j*E),
where E is the largest error at any cut and role.

The error transition for COPY is ADD. For reset it is zero before the new
residual. Let C_(r,c),j be the exact signed coefficient of defect j at role r
and cut c. Define J_(r,c)=sum(abs(C)*a), K_(r,c)=sum(abs(C)*c), and
G_(r,c)=sum(abs(C)). Let J and K be their separate maxima over all cuts and
roles. The triangle inequality gives E <= u(B*J+K*E). If u*K<1, then

`E <= B*u*J/(1-u*K)`.

For any final role with scores (J_r,K_r), its error is at most

`B*u*(J_r+K_r*u*J/(1-u*K))`.

The verifier finds the least integer guard for these sufficient formulas.
A prefix guard g must satisfy J+K<2^g. A final guard must satisfy u*K<1 and the
strict final bound divided by B must be less than 1 at u=2^-g. With t additional
bits, monotonicity makes the respective error less than B*2^-t for all t>=0.
These guards need not be the least precision of a physical implementation.
The separate maxima and the relative defect allowances can be conservative.

The signed forward trace retains cancellations. A separate transposed program
checks every final coefficient for all 799 roles and the three prefix maxima.
Literal scalar execution with aligned defect signs attains the independent
unit-defect gain G. This proves sharpness for independently bounded defects;
it does not assert that all relative local allowances can be attained together.
Literal input signs also attain the largest ideal input norm.

A residual injected immediately after an actual INIT remains in the next
additive COPY. The old overwrite transition deletes it. This is a counterexample
to extending that transition to the new contract. PR5819 assumes exact COPY
and reset; its stated theorem does not have this defect.

The full word has 31 CLEAR events, and 30 erase nonzero ideal data. Neither an
exact-zero cancellation lemma nor this residual estimate implements those
operations. Their physical implementation and bill remain open.
