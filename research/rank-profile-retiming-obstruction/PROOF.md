# Finite retiming obstruction and its scope

## 1. Scalar correctness does not license arbitrary rank exchanges

For a scalar addition `g = I + c E_ds`, an addition `h = I + b E_uv`
commutes under the sufficient condition `d != v` and `u != s`. This is obtained
by multiplying the two elementary matrices. A diagonal scale by q at d changes
c to qc when g is moved right across the scale; a scale at s changes c to c/q.
Moving left reverses those factors. These identities hold on arbitrary inputs,
including dirty helpers. All source scales in the retained words are nonzero
powers of two. The transformed addition remains dyadic. No new gate is inserted.

The class fixes every other instruction, frame, native warp cut, entrance,
centre/target boundary, and helper exit. It is deliberately narrower than all
semantics-preserving circuit rewrites. In particular, the scalar identities do
not make arbitrary pairs of recursive children exchangeable.

## 2. Complete local frame-price enumeration

On one of the moved ADD's registers let its old preceding, gate, and following
frames have dimensions p, u, q. Removing this occurrence changes its price by

    f(q-p) - f(u-p) - f(q-u),       f(r) = r^(1-a), f(0) = 0.

The first following fixed constraint may be a true charged climb or a zero-cost
boundary check. For pricing only, the latter is relaxed to a virtual climb to
its required frame. Its charge is zero in the original word and in every legal
candidate, so this is a sound over-approximation. Native maps are preceded by
explicit entrance checks in the trace, and no moved gate crosses such a cut.
The temporary centre descents are billed separately; they do not overwrite the
main forward register's frame. This distinction is checked against the retained
full invoice.

After removing the ADD, let P1,P2 be the frames immediately before its proposed
position, and Q1,Q2 the first subsequent constraints. The new common frame F
must satisfy

    L = P1 + P2 <= F <= H = Q1 intersect Q2.

If L is not contained in H, the position is impossible in the relaxation. If
L is contained in H, a basis of L can be extended to a basis of H. Taking each
prefix gives a frame of every dimension from dim L through dim H. Its added
price on register j is

    f(dim F - dim Pj) + f(dim Qj - dim F) - f(dim Qj - dim Pj).

There are no other changing costs in this relaxed frame invoice. The cost
depends only on dim F. Consequently checking every integer in that interval is
complete over all binary subspaces, not just the chosen basis representatives.
Every legal candidate has exactly one of the enumerated signed histograms.

The implementation scans every permissible insertion cut in each maximal
scalar corridor, including unchanged placement with a changed frame. Corridors
end at noncommuting ADDs, phase boundaries, the A prelude, or native B warp cuts.
A different corridor is not inferred from an earlier neutral move. Per-register
entry and exit constraints are taken at the actual segment boundaries, so a
pre-warp frame cannot be mistaken for its post-warp image.

## 3. Exact all-exponent certificate for all 19 deltas

For a signed new-minus-old histogram d of equal rank mass, put

    C_k = sum_r d_r min(r,k).

The retained discrete-curvature expansion gives

    sum_r d_r f(r) = sum_{k=1}^{T-1} C_k theta_k,
    theta_k = 2 f(k) - f(k-1) - f(k+1).

For `f(x)=x^(1-a)` and `0<a<1`, each theta_k is positive and theta_k strictly
decreases with k. One direct proof is the triangular integral

    theta_k = a(1-a) integral_{-1}^{1}
              (1-|t|) (k+t)^(-1-a) dt.

For k=1 the integral is improper at t=-1. It converges because the triangular
weight cancels one power of k+t and a<1. The identity follows by integration by
parts, or the finite second-difference formula followed by the endpoint limit.
Increasing k strictly decreases the integrand on the interior, establishing the
strict order. This is an elementary curvature fact, not a new circuit theorem.

Let `S_j = C_1 + ... + C_j`. Summation by parts, with theta_T=0 solely for this
finite identity, yields

    sum_{k=1}^{T-1} C_k theta_k
      = sum_{j=1}^{T-1} S_j (theta_j - theta_{j+1}).

Therefore `S_j >= 0` for all j suffices for non-improvement for every a in (0,1).
If d is nonzero and has zero rank mass, at least one S_j is positive, so the
inequality is strict. The zero histogram has equal price.

All 19 independently regenerated histogram types have zero rank mass and
nonnegative S_j. Eighteen have the simpler nonnegative caps already. The one
mixed-cap type is

    d = {1:1, 2:2, 3:-3, 4:1},  C = (1,1,-1,0,...),

so its difference is theta_1 + theta_2 - theta_3 > 0. This illustrates why
checking only signs of the individual caps would leave a genuine gap. The
verifier does not infer the all-exponent result from floating-point samples.

In particular, the proposed `2+2 -> 1+3` change has C_2=-1 and cannot occur among
these candidates. Added nonnegative charges cannot repair a lack of savings
when all normalisers and common costs are held fixed. A simultaneous multi-gate
change, a new frame at another instruction, or a changed boundary escapes the
class and is not excluded.

## 4. A literal improving control and conditional overhead reserve

The counterfactual rollback and recovery of the credited PR2957 swap have exact
new-minus-old profile `{1:1,2:-1,3:-1,4:1}`, with C_2=C_3=-1. They pass the
retained arbitrary-dirty free-operator semantics in both orientations after
literal inverse cleanup is rederived. The recovered word is the pinned PR3734
word, not a newly discovered current improvement.

PR3863's uniform lower bound at l=17/10000, u=18/10000 gives the raw credit

    L = l(1-u)/(3(1+2u)) + l(1-u)/(4(1+3u))
      = 1491695107/1513529160000.

For 3240 copies, 3240L-3 = 2437538889/12612743000 > 0. Thus three added rank-1
children are affordable in this conditional comparison of otherwise unchanged
invoices. This calculation neither supplies those three physical operations nor
admits the counterfactual full supplier. Its purpose is to attach the inherited
pricing theorem to an actual source-level rewrite with checked local boundaries.

The proof is informal mathematics supported by finite exact Python replay. It
is not a kernel proof of the continuum inequalities or of integer multiplication.
