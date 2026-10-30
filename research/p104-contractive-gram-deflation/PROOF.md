# A sharp error floor for contractive P104 Gram deflation

## Contract and theorem

Let P consist of the 56 unoriented D8 root lines e_i +/- e_j in R^8,
and any proper subset of the 64 half-spin root lines of one fixed parity.
Choose one root r_i of squared length 2 on every retained line. Let R
have these roots as rows and let K=RR^T/2.

A contractive rank-seven approximation means

    K_D = R D R^T/2,
    D real symmetric, 0 <= D <= I in positive-semidefinite order,
    rank D <= 7.

Then the exact minimum of max_{i,j}|K_ij-(K_D)_ij| is 1/4. Any omitted
half-spin root q gives an attaining matrix D=I-qq^T/2. It is an orthogonal
rank-seven projector. If the half-spin subset is empty the same witness
works; only one omitted half-spin root is required.

This is a scoped proof about coefficient error. It does not give a lower
bound for unrestricted rank-seven matrices, nonsymmetric approximants,
noncontractive approximants, nonlinear processing, or masked exactness.

## The D8 direction bound

For every unit vector u in R^8,

    max_{r in D8} |r dot u|^2 >= 1/2.

To prove it, arrange the absolute coordinates as x_1>=x_2>=...>=x_8>=0
and put s=x_1+x_2. The largest absolute D8 inner product is s. Since
the remaining coordinates are at most x_2,

    1 = sum x_i^2 <= (s-x_2)^2 + 7*x_2^2 <= 2*s^2.

The last bound follows because this convex quadratic on 0<=x_2<=s/2
is bounded by the larger endpoint value, max{s^2,2*s^2}. This proves
the direction bound. It is an elementary root-geometry inequality, not a
new general rank-approximation theorem.

## Lower bound for every admissible D

The rank cap gives a unit vector u in ker D. Symmetry and 0<=D<=I imply

    I-D >= u u^T.

For example, use an orthonormal eigenbasis with u as a zero-eigenvalue
vector of D. In that basis I-D-u*u^T has only nonnegative eigenvalues.
Consequently the coefficient error E=K-K_D is positive semidefinite and

    E_ii = r_i^T (I-D) r_i /2 >= (r_i dot u)^2/2.

The retained D8 subsystem supplies an i with E_ii>=1/4. A diagonal entry
already gives the required lower bound on maximum absolute entry. This
argument covers all real admissible D, not just rational or sampled D.

## Exact attaining deflation

Choose a half-spin root q whose line is omitted. It has squared norm 2,
so D=I-qq^T/2 is symmetric, idempotent, positive semidefinite and rank 7.
It lies between zero and I. Its error is

    E_ij = (r_i dot q)(r_j dot q)/4.

For a D8 root the inner product with q is in {-1,0,1}. For another
half-spin root of the same parity, the sign patterns differ in an even
number of coordinates. Unless their lines agree, the inner product is
also in {-1,0,1}. The line of q is absent, so every retained root has
inner product at most one in absolute value. Thus every error entry is
at most 1/4. Some D8 root has inner product of absolute value one, so
the maximum is exactly 1/4. This proves sharpness constructively.

## P104 binding and meaning for precision

Matarener's PR6166 at 096938513138868f0ed27639061f1a5054900f96 identifies
the selected P104 ports with all 56 D8 lines and 48 half-spin lines in
orthonormal coordinates. Its e8/ports-d8.md lists the sixteen omitted
lines. That coordinate identification is a cited predecessor premise,
not a result independently checked here. MISSING.json retains just those
factual signs so the new deflation witnesses replay without the pending PR.
No predecessor certificate, code uniqueness, single-word weight, generalized
support weight, native operator or supplier replay is run.

The coefficient convention K=RR^T/2 is the retained P104 Gram-channel
convention from Rohan Arun's PR1972 and Chafik Boukhalfa's PR1991 native
channel, with its credited root/frame lineage. This theorem introduces
contractive approximation of that channel as a changed mechanism.

For every admissible D there is an input x=B e_i such that the i-th output
bias is at least |B|/4. Thus the approximation error is not o(|B|), uniformly
over arbitrary inputs. Increasing the arithmetic precision cannot remove
this mathematical bias. The attaining matrices even have dyadic rational
entries. Any supplier using this deletion must explicitly correct the
residual or justify a different consumer/error contract. No correction
cost is declared free and no complete signed-moment gain is claimed.

The full scalar word may have other routes and cancellations. The theorem
only concerns replacing this Gram block by K_D while retaining the other
terms and demanding entrywise accuracy. It does not exclude changing the
side correction, targets, source encoding, masking or complete circuit.

## Evidence

The standard-library verifier constructs this root set from the retained
sign list, checks all sixteen rank-seven projectors by integer arithmetic,
and enumerates every coefficient of each new error matrix. It checks the
D8 inequality on the 6,560 nonzero vectors in {-1,0,1}^8. Those are finite
corroborations of the written proof, not extrapolations to arbitrary D.
The verifier also rejects wrong parity, duplicate missing lines and a
retained-root deflation falsely claimed to attain error 1/4. Normal and
optimized runs retain explicit exception checks. Source hashes bind the
generated receipt. Independent human and formal proof-kernel review remain
unclaimed.
