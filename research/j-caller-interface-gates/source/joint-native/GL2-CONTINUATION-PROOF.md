# Any scalar GL2 at the q3 retained continuation

The changed physical cut mixes the two current carriers `(U,V)` by any
invertible scalar matrix `M=[[a,b],[c,d]]` before the retained J query.
The existing diagonal handoff then has homogeneous update

    (u2,v2)^T = P diag(B4,B5J) (u1,v1)^T,
    P=diag(1,-1) M.

The affine public-reader terms remain in the caller's actual prefix.
They do not alter the two pivot coefficients of its unique joint inverse.
The actual target is `F7 J`, not `N0 F7`.

Write column2 of `P^-1` as `(beta,delta)^T`. The exact original-t/current-V
inverse coefficient is

    C=F7 [beta A+delta B] (B7J)^-1 F7^-1,
    A=J Q1^-1(I-B2^-1)(B3J)^-1 B4^-1,
    B=J Q1^-1 B2^-1(B5J)^-1.

Here `Q1=J^-1B1J` and each actual source code is
`B_s=P_s N0^-1 J`; the base factor `B3J=P3N0` remains present.
This follows by inverting the homogeneous product

    diag(B6,B7J) P diag(B4,B5J) [[0,B3J],[I,0]] K.

Expand C as `beta V1-beta V2+delta V3`. The three phase-exact Clifford
operators Vj all have native arity `10f`. They are distinct up to scalar
phase. Their one-coordinate definitions are saved, and their all-f lift
is `Vj,f=i^(f-1) Vj,1^tensor(f)` after bit regrouping. The literal global
unit is retained in every coefficient group.

The producer independently replays the original-t inverse row from the
physical circuits of the upper, lower and balanced saved candidates.
It imports no caller X-character algebra and checks the complete
coefficient at all four chunk residues. Every source/fresh/continuation
native event has actual rank2 and the prefix has exactly61 H2 children.

## Cancellation is controlled by a uniform Gram bound

Normalize proportional one-coordinate rays into one group before using
a tensor argument. The exact one-coordinate normalized Hilbert-Schmidt
overlap moduli of V1,V2,V3 are `1/16,0,1/256`. The producer enumerates
the X-character trace exactly as Gaussian integers; changing to that
basis preserves the physical trace. Tensoring makes these moduli their
fth powers. Therefore their normalized Gram matrix has

    lambda_min >= 1-2*(1/16)^f >= 7/8

for **every f>=1**. This bound is uniform in all coefficient vectors.
It does not require bounded coefficients, periodic coefficients, or an
M independent of f.

For any invertible M, `(beta,delta)` is nonzero. Thus
`c=(beta,-beta,delta)` is a nonzero coefficient vector at every f.
Let `D=2^(16f)` be the physical dimension. Each Vj has entries of
magnitude either0 or `2^(-5f)`. Consequently

    ||C||_F^2 >= (7/8) D ||c||_2^2,
    maximum_entry_magnitude(C)^2 <= 3 ||c||_2^2 2^(-10f).

It follows that C has at least `(7/24) D 2^(10f)` nonzero entries in
total. Hence **some row** has at least `(7/24)2^(10f)` nonzeros. This is
a global/max-row statement, not an every-row assertion.

The full bank-circuit support induction now yields

    total actual native arity + binary ADD count
        >= 10f+log2(7/24).

Thus bounded/o(f) scans require native mass at least10; under the
parent's equal-volume full-scan transfer assumptions the same necessary
mass holds for admissible full-bank implementations. The equal-volume
prefix mass is122 and full-output stock128, so this q3 architecture
cannot produce a favorable native moment at that cut. Native rank of a
sum was never inferred from one constituent's tableau.

The theorem covers **every invertible scalar GL2 M at this one q3 cut**,
including f-dependent Gaussian coefficients. The three saved candidates
are independent literal source bindings, not an exhaustive search used
as the theorem. Larger q routing schedules, operator-valued coupled
bridges, other core/delivery choices, changed endpoints and cross-cut
query fusion remain outside it. No stronger kappa or supplier claim is
made.
