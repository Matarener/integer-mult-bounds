# All-target Q8 inverse-label tariff

This is a written theorem in the full formal group algebra. Finite replays
corroborate the argument; they do not quantify over every word or role count.

## Model and statement

Let G=Q8={1,z,i,zi,j,zj,k,zk}, where z is the central group element -1,
i^2=j^2=k^2=z, ij=k and ji=zk. In F2[G], [z] and the scalar 1 are distinct.
Fix any finite R roles. Every initial role is arbitrary independent dirty data.
The required endpoint is exactly diag([g_1],...,[g_R]), with g_a in G.
An identity target is a restored dirty spectator.

The paid labels are {i,zi,j,zj}. A paid call is

    D_N(g)=I+([g]+1)N,   N=u v^T,   u,v in F2^R nonzero.

The original alphabet requires v^T u=1, so N is idempotent. The theorem also
holds if rank-one nilpotent couplings, v^T u=0, are admitted for the same price.
In the latter case the factor is its own inverse. An idempotent factor's
inverse uses g^-1, which is an allowed label of the same price.
Scalar GL_R(F2) maps are free. No address map, erasure, clean allocation or
higher-rank call is free. All preparation and restoration calls are counted.

The two i labels each cost alpha and the two j labels each cost beta, for
arbitrary nonnegative real alpha,beta. Let s_i,s_j,s_k count targets in
{i,zi}, {j,zj}, {k,zk}, respectively, and t count z targets. Identity targets
are not included in these counts.

**Theorem.** For every finite R, every target list and every word length,

    minimum = alpha*(s_i+s_k) + beta*(s_j+s_k)
              + 2*t*min(alpha,beta).

At unit prices this is s_i+s_j+2*s_k+2*t, exactly the separate direct bill.
The conclusion includes arbitrary restored dirty workspace and arbitrary
interleaved scalar mixing. It makes no assertion about physical supplier costs.

## Normalize scalar mixing

Moving a scalar basis change through a paid factor conjugates N and preserves
its binary rank and idempotent or nilpotent type. The augmentation [g]->1 maps
each paid factor and the target endpoint to I. Hence the residual scalar
matrix must be I. It suffices to consider a product of n paid factors, in
its original noncommuting group order. This is the normalization credited to
the register-model predecessors, including PR2318 and PR2587.

## Full coefficients force both support ranks

For the normalized word let X have columns u_l, and Y have rows v_l^T.
The expansion of T-I over nonempty ordered subsets has terms

    ([g_a]+1)...([g_b]+1) * u_a * (scalar products) * v_b^T.

Every binary coefficient matrix therefore has image contained in im X and
row space contained in row Y. At the formal diagonal endpoint, the
coefficients at the seven nonidentity group elements are coordinate
projectors onto the corresponding target classes. Their images together,
and their row spaces together, span all W=s_i+s_j+s_k+t active axes. Thus

    rank X >= W,   rank Y >= W.                         (1)

This is the full-coefficient support argument of ywz65/PR2587. It works for
nilpotent couplings as well. A nonfaithful quotient alone cannot supply (1).

## The combined parity quotient supplies the missing joint charge

Let chi:G->F2 be the homomorphism that is 1 on {i,zi,j,zj} and 0 on
{1,z,k,zk}. There is a ring homomorphism to the dual numbers

    F2[G] -> F2[epsilon]/(epsilon^2),
    [g] -> 1+chi(g)*epsilon.

For every paid factor its image is I+epsilon*N_l, since every paid label has
chi=1. Products of two increments vanish. Consequently the complete
endpoint forces

    XY = sum_l N_l = P_i + P_j,                         (2)

where P_i,P_j project onto the two signed target classes. The k and z
classes vanish in this single quotient. The right side has rank s_i+s_j.
Sylvester's inequality applied to the ACTUAL paired X,Y gives

    rank X + rank Y <= n + rank(XY) = n+s_i+s_j.

Together with (1) this proves

    n >= 2W-s_i-s_j = s_i+s_j+2*s_k+2*t.                (3)

Equation (2) is the new step relative to the restricted-target proof. Using
the two separate first-order ranks and summing them loses the overlap at k.
Their sum in a single quotient cancels that overlap before applying
Sylvester, preserving its full two-call charge alongside z's charge.

For completeness, Sylvester follows because rank(XY) is at least
rank Y minus dim ker X, which is rank Y-(n-rank X). It holds for n=0 too.
No trace, commutativity of Q8, projector orthogonality or role bound is used.

## Separate label floors and weighted attainment

Use the two other binary characters, chi_i=1 on {i,zi,k,zk} and
chi_j=1 on {j,zj,k,zk}. Their dual-number quotients give

    sum_(i-label calls) N_l = P_i+P_k,
    sum_(j-label calls) N_l = P_j+P_k.

Each summand has binary rank one, so the class call counts obey

    n_i >= s_i+s_k,   n_j >= s_j+s_k.                   (4)

Let a=n_i-s_i-s_k and b=n_j-s_j-s_k. By (3)-(4), a,b>=0 and a+b>=2t.
It follows for every nonnegative real alpha,beta that

    alpha*n_i+beta*n_j
      >= alpha*(s_i+s_k)+beta*(s_j+s_k)+2t*min(alpha,beta).

Coordinate-projector words attain this bound in the full group algebra:
use the designated single label for every signed i or j target, use ij for
k and ji for zk, and use ii or jj for each z target, choosing the cheaper
class. Identity roles are untouched. Each k recipe costs one of each class;
each z recipe costs two calls from the cheaper class. The construction
restores every spectator and needs no extra role or scalar mixing. Both
idempotent-only and enlarged nilpotent alphabets therefore have the same
sharp tariff. Empty active lists and zero prices are included.

## Scope and credit

Aaron Wang/PR2318 checked all 64 two-role pair minima for this inverse-label
alphabet, but claimed no structural lower bound or arbitrary-role extension.
ywz65/PR2587 proved a support-rank tariff for {1,i,j,z} under positive labels
and left k and signed noncentral classes open. Cinna Davis/PR1925 supplies
related arbitrary-role first-order bounds for mixed k triples. This proof
reconciles those scopes and adds the combined parity quotient, the complete
all-target class-symmetric tariff and the rank-one nilpotent extension.
Sylvester's inequality and the general support method are credited, not
claimed as new linear algebra.

Positive-only signed-target tariffs and four independently priced signed
labels are outside the sharpness statement. One cannot reprice -i as a
single positive i call. The two first-order characters identify 1 with z,
so represented equality alone never accepts a formal endpoint. Clean-only
ancillas and projector-dependent prices change the proof's hypotheses.
Arham Tahir/PR3137 supplies a separate finite-array compiler and physical
caller handoff; the abstract class prices here do not discharge that handoff.
No selected supplier, kappa, all-size multiplication theorem, formal-kernel
proof or independent human review follows.
