# Phase defects with a pointwise fixed subspace

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Let V=F_2^n, n>=1, with its ordinary nondegenerate dot product. Fix b in V,
a subspace W of V, and the quadratic refinement

    q_b(x) = wt(x) + 2(b dot x) modulo 4.

The dot product in this expression takes values zero and one. Write

    G_W = {S in O(n,2): Sw=w for every w in W}.

Use the row convention of Gareth Davidson #1255 and Nick Petalas #5225:

    q_b(S^T x) - q_b(x) = 2 d_b(S) dot x modulo 4.

The unrestricted mixed-sign theorem of #5225 is a cited premise. It says
that every defect satisfies q_b(d_b(S))=0, that T_e=I+ee^T has defect e
whenever q_b(e)=0, and that d_b(AB)=d_b(A)+A d_b(B). No predecessor
verification or physical implementation is assumed here.

**Restricted image theorem.** The exact defect image of G_W is

    D_(b,W) = {e in W-perpendicular: q_b(e)=0}.               (1)

Every e in this set has the representative T_e inside G_W. Put

    H_(b,W) = {S in G_W: d_b(S)=0}.

Every S in G_W has the unique factorization

    S = T_e H,     e=d_b(S),     H in H_(b,W).                (2)

Each defect fiber has exactly |H_(b,W)| elements. Consequently

    |H_(b,W)| = |G_W| / |D_(b,W)|.                           (3)

This statement permits degenerate W, including totally isotropic subspaces.
No nondegeneracy assumption or choice of a complement to W is needed.

## Proof of the restriction and its converse

If S fixes W pointwise, its inverse fixes W pointwise too. Orthogonality gives
S^T=S^-1. For w in W the defining defect identity therefore gives

    2 d_b(S) dot w = q_b(w)-q_b(w) = 0 modulo 4.

Thus d_b(S) belongs to W-perpendicular. The cited unrestricted theorem gives
q_b(d_b(S))=0, proving necessity in (1).

Conversely, let e belong to the set in (1). Since q_b(e)=0, e has even
weight, so e dot e=0. The cited transvection identity gives T_e in O(n,2),
T_e^2=I and d_b(T_e)=e. For every w in W,

    T_e w = w + e(e dot w) = w.

Hence T_e belongs to G_W. This proves sufficiency and the promised attaining
representative. It also shows that a nonzero defect requires exactly one
such algebraic rank-one transvection when correcting a chart in G_W.
This is a factor count, not a paid physical cost.

## Factorization and fibers

For S in G_W, put e=d_b(S) and H=T_e S. Both factors fix W, and the cited
cocycle gives

    d_b(H) = e + T_e e = e+e = 0.

Here T_e e=e follows from e dot e=0. Thus H belongs to H_(b,W) and S=T_e H.
The defect e is forced by S, after which H=T_e S is forced, proving
uniqueness. The cocycle also shows that zero-defect maps form a subgroup
and that d_b(T_e H)=e for every H in that subgroup. Left multiplication by
T_e is therefore a bijection onto the e fiber. This proves (2) and (3).

## Literal axes and nested restrictions

Suppose W is spanned by k distinct coordinate vectors. Orthogonality forces
S to be the identity on those axes and an arbitrary orthogonal map on the
remaining m=n-k coordinates. Defects vanish on the fixed coordinates.
Let b_free be b restricted to the free coordinates. Translation
z -> b_free+z in (1) gives the closed count

    N = sum_{0<=j<=m, j == wt(b_free) modulo 4} binomial(m,j),
    |H_(b,W)| = |O(m,2)| / N.                               (4)

Use |O(0,2)|=1. The all-fixed case has N=1. In particular, signs on fixed
axes do not affect this count. This answers the literal-axis question left
open by #5225.

For arbitrary W_1 contained in W_2, equation (1) gives

    D_(b,W_2) = D_(b,W_1) intersect W_2-perpendicular.         (5)

The actual fixed subspace matters, not only its dimension. At n=4, b=0,
fixing e_1 leaves only defect zero. Fixing the isotropic vector e_1+e_2
allows defects zero and (1,1,1,1). Both constraints have dimension one.
The latter nonzero defect is attained by T_(1,1,1,1), which fixes e_1+e_2
but moves each of e_1 and e_2. Replacing a required fixed sum by separately
fixed axes would impose a stronger contract.

## Scope and credit

This is a scoped algebraic proof. The only change from #5225 is the exact
pointwise-fixed-subspace contract and its consequences above. The sign mask
remains attached to the chart's columns. Setwise stabilization, unequal input
and output restrictions and nonorthogonal charts are separate questions.
The finite verifier corroborates the new restricted statement; it does not
supply its all-width quantifiers or audit predecessor results.

Credit Nick Petalas #5225 for the unrestricted mixed-sign image, representatives,
cocycle and explicit literal-axis handoff; Philipp / mightyOil #1300 for the
equal-sign phase model; Gareth Davidson #1255 for the residual C-gate phase
and row conventions; and yssite #1558 following icekylinx #24 for the retained
signed Gauss-normalization context. All existing notices remain unchanged.
No external literature priority is claimed for quadratic refinements,
transvections, subgroup fibers or their elementary restriction argument.

No native producer, chart circuit, physical route, data acquisition, dirty-state
restoration, stock, precision, fixed-tape implementation, compiler or complete
consumer bill is constructed. Those costs remain unknown. No new kappa,
supplier admission, selected-frontier change or complete multiplication theorem
follows. Independent human and formal proof-kernel review are unclaimed.
