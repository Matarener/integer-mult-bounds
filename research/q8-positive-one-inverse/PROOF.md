# Positive Q8 calls with one inverse target

Let G=Q8={1,z,i,zi,j,zj,k,zk}, with z=i²=j², z²=1, ij=k,
ji=zk. The central group element z is distinct from the scalar 1 in F2[G].
There are R finite roles, all with independent arbitrary dirty input.
The required endpoint is exactly diag([g_1],...,[g_R]) in the full formal
group algebra. Identity roles are restored dirty spectators.

A paid call is D_N(g)=I+([g]+1)N, with g in {i,j}, N=u v^T over F2,
u,v nonzero and v^T u=1. Thus N is a rank-one idempotent. Scalar GL_R(F2)
mixing is free. There is no clean allocation, erasure, free address map or
higher-rank call. An i call costs alpha and a j call costs beta, for any
nonnegative real prices. The order of group multiplication is retained.
Every such idempotent is a scalar conjugate of a coordinate projector:
choose u as the first basis vector and complete it with a basis of ker v^T.

Let every target lie in {1,i,zi,j,zj}. Write s_i for the number in {i,zi},
s_j for the number in {j,zj}, W=s_i+s_j, and q for the number in {zi,zj}.

**Theorem.** If q is zero or one, the exact minimum bill is

    alpha*s_i + beta*s_j + 2*q*min(alpha,beta).

If q is any positive integer, every legal word still satisfies this lower
bound with q replaced by 1. Attainment for q>=2 is not asserted. The theorem
allows arbitrarily many restored dirty spectators and arbitrary free mixing.

## Normalize and retain formal coefficient support

Move each scalar basis change through adjacent paid calls by conjugation.
This preserves binary rank and idempotence. Augmentation [g]->1 sends every
paid factor and the endpoint to I, so the residual scalar matrix is I.
Every word therefore has a normalized product of n paid factors, with the
original noncommuting group order preserved. This normalization follows the
credited register-model predecessors.

Let X have the n columns u_l and Y the n rows v_l^T. In the expansion of
T-I, every term has its image in im X and its row space in row Y, since
its scalar part is u_a(v_a^T u_b)...v_c^T. This holds for each of the eight
formal group coefficient matrices separately. At the diagonal endpoint,
the coefficient at each nonidentity g is the coordinate projector onto
that target class. Together these span every active coordinate axis,
both as columns and as rows. Consequently rank X>=W and rank Y>=W,
so n>=W. This is the full-coefficient support argument of ywz65/PR2587.

## Equality would force orthogonal projectors

The character chi:G->F2 that is 1 on {i,zi,j,zj} and 0 on {1,z,k,zk}
induces a ring map [g]->1+chi(g)*epsilon to F2[epsilon]/epsilon².
Every paid factor has image I+epsilon*N_l. The complete endpoint forces

    XY = sum_l N_l = P,

where P is the projector onto the W active coordinate axes. This combined
character is credited to Nick Petalas/PR3450. It erases all signs and cannot
by itself validate a formal endpoint.

Suppose n=W. The two support containments imply that im X is exactly the
active coordinate space and row Y is exactly its dual. Delete the zero
spectator rows of X and zero spectator columns of Y. The resulting square
matrices X_A,Y_A satisfy X_A Y_A=I_W. Hence Y_A X_A=I_W, and also YX=I_n.
It follows that v_l^T u_m=delta_lm and

    N_l N_m = 0 for l!=m.

Every product term of degree at least two vanishes. The full word is then

    T = I + sum_l ([g_l]+1)N_l.

Its only possible group coefficients are 1,i,j. A requested zi or zj
coefficient cannot occur. Thus q>0 forbids n=W. This equality analysis is
the new sign-sensitive step. It uses the full endpoint after applying the
sign-blind quotient.

## Trace parity and label floors

Taking the binary trace of XY=P gives n=W mod 2, since
trace(N_l)=v_l^T u_l=1 for every allowed paid call. Combining parity with
the preceding exclusion proves n>=W+2 whenever q>0.

The separate characters chi_i=1 on {i,zi,k,zk} and chi_j=1 on
{j,zj,k,zk} give

    sum_(i calls) N_l=P_i,   sum_(j calls) N_l=P_j.

The target class projectors have ranks s_i,s_j, so n_i>=s_i and n_j>=s_j.
Put a=n_i-s_i and b=n_j-s_j. They are nonnegative and satisfy a+b>=2
when q>0. Thus alpha*n_i+beta*n_j is at least the stated baseline plus
2*min(alpha,beta). For q=0 the baseline itself is a lower bound.

For q=0, apply each requested generator to its own coordinate. For q=1,
do the same, using i at the zi coordinate or j at the zj coordinate,
and apply the cheaper generator twice on that same coordinate. Its square
is z, which is central, so the result is the required negative generator.
This adds exactly 2*min(alpha,beta), leaves all other roles unchanged and
uses no extra role. The construction includes zero prices and empty active
lists. This proves the exact nonnegative-real-price tariff for q<=1.

## Boundaries and credit

Aaron Wang/PR2318 already exhausts both positive and inverse alphabets for
all two-role target pairs. The values in that finite domain are credited.
This theorem removes the role bound for the one-inverse family and gives
its weighted tariff. PR2587 supplies full coefficient support and the
restricted positive target tariff. PR3450 supplies the inverse-label
all-target tariff and combined character; its signs have unit inverse
prices and do not settle the positive-only claim here. Sylvester's
inequality is not needed for the new equality argument.

Idempotence is essential to the trace step. Allowing nilpotent factors,
clean-only inputs, target k/z classes or projector-dependent prices changes
the statement. Multiple negative targets require a stronger invariant or
sharing construction. No physical caller, native supplier, multiplication
exponent or selected-frontier change follows from this formal theorem.
Independent human and formal proof-kernel review are unclaimed.
