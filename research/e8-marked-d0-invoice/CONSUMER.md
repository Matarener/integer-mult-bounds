# An explicit actual-decoder consumer

Prepared by conorholds, with substantial OpenAI Codex assistance. Apache-2.0.
This derives a local consumer of the intrinsic marked-d=0 invoice theorem. It does not assert global reduction of
all P112 decoders to this class.

Use norm-two representatives r_s, s in P, C_h(s)=(r_s,h), and
N0(s,t)=(r_s,r_t)/2. All products are ordinary transpose products, over an
arbitrary characteristic-zero field K. Suppose an exact factorization is

    N0 = sum_j p_j q_j^T.

Assume all p_j are nonzero and no two are proportional. Suppose the actual
factor ranks are (rank P,rank Q)=(9,8+t), with 9+t total terms, t in {2,3}.
There is a singleton pivot p_pi=lambda delta_v, lambda!=0, for a P112 root v.
Rescaling that factor and inversely rescaling q_pi preserves all supports,
costs, ranks and word spaces, so assume p_pi=delta_v. Let S be the
span of all q_j and T=S_{<=7}. Assume dim(C intersect T)=0. Then the actual
binary decoder cost is at least64. There is no restriction on the pivot
word q_pi and no assumed losing root row. The proof uses the unmarked
invoice floor and derives the marked witness precisely when a free pivot
could permit a rebate.

## 1. Recover the exact intrinsic data

The column space of N0 is exactly C: its columns are (1/2)C_(r_s), and the
P112 roots span the eight-dimensional normal space. Exact factorization
therefore puts C inside span{p_j}. The singleton delta_v lies outside C,
because every nonzero codeword has at least49 nonzero P coordinates.
The actual rank-nine hypothesis now gives

    span{p_j}=C direct-sum K delta_v.

Consequently each nonpivot factor has a unique decomposition

    p_j=(1/2)C_(a_j)+omega_j delta_v.

This code-plus-unit shape is derived from actual ranks and exactness; it is
not a projected-normalization hypothesis. Project the exact matrix identity
onto C along delta_v. On column s, injectivity of h -> C_h gives

    sum_(j!=pi) a_j q_j(s)=r_s,
    C_h=sum_(j!=pi) (a_j,h) q_j.

The delta_v component of the same exact factorization gives

    q_pi=-sum_(j!=pi) omega_j q_j.

Thus the nonpivot8+t words span S and are a basis, since rank Q=8+t.
If any a_j=0, p_j would be proportional to the pivot or zero, forbidden.
Consequently every intrinsic functional xi_j(h)=phi_j(C_h)=(a_j,h) is
nonzero. The [unmarked theorem](UNMARKED.md) therefore gives I>=64, without
assuming any marked index or support condition on q_pi.

## 2. The one-sided invoice is exact

For a rank-one term define its binary cost by the rank of beta restricted
to the row-label and column-label spans. The root-only lemma with correction
space zero shows that a nonzero codeword has label weight8 or9, and weight8
is possible only in a frame-root direction: a nonframe root has its own
root coloop in addition to the rank8 nonself remainder. A frame word has
span W_i=z_i^perp. Thus the one-sided projected family

    D'={( (1/2)C_(a_j), q_j): j!=pi}

has cost

    I=sum_(j!=pi) w(q_j)-n_c,

where correction means a_j proportional to frame f_i and z_i in the actual
column-label span U_j. This is the elementary rank loss of a nondegenerate
binary pairing restricted to a codimension-one row span: exactly one is
lost iff its orthogonal line lies in U_j. The label pairing beta is
nondegenerate in its 9-dimensional ambient space (E8 is unimodular).

## 3. Bound the actual row edits, without importing a ledger identity

Changing a codeword row only at v can gain, retain or lose its v coordinate.
Gaining does not reduce binary rank; retaining does not change its support.
For a genuine loss, compare C_h with C_h-C_h(v)delta_v.

If the resulting row-label span has dimension<=8, the root-only lemma with
the one-dimensional unit correction space forces h to be a root direction.
For a frame root f_i, deleting at most one coordinate still leaves its
rank8 span W_i, by the frame remainder cut24. For a nonframe root r!=v,
the nonself P remainder remains rank8 after one deletion (restricted cut20, obtained from full cut24 by removing the four nonorthogonal frame roots),
and its own root coloop r is still present, so rank9 persists. Thus the only
loss that can reduce a term's binary cost has h proportional to v itself.

All actual rows of that last type that lose v are proportional to

    (1/2) C_v-delta_v.

There is therefore at most one, by the no-parallel-actual-row hypothesis.
If such a row exists, call its index k. Its projected row span is full9,
while its actual row span is W_v. Its term loses exactly

    epsilon_k=[ell_v in U_k].

If no such row exists, put epsilon=0. Let c_pi be the actual singleton
pivot's binary cost. Since its row-label span has dimension one, c_pi is
zero or one. Consequently

    cost(D) >= I-epsilon+c_pi.                              (C)

If c_pi=1, the unmarked I>=64 and epsilon<=1 give cost(D)>=64. If c_pi=0
and no losing root row exists, (C) gives the same conclusion.

It remains to consider c_pi=0 with the unique losing row k. Pivot cost zero
means beta(ell_v,ell_s)=0 at every support coordinate of q_pi, equivalently
q_pi vanishes on O_v={v} union {s in P:(r_s,v)=0}. Also omega_k=-gamma, so
the exact pivot identity in Section1 gives

    phi_k(q_pi)=gamma!=0.

Thus g=q_pi supplies the actual marked witness, with xi_k=gamma ev_v. The
marked theorem gives I-epsilon>=64, completing the last branch of (C).
If q_pi=0, the pivot identity and nonpivot basis force all omega_j=0, so
there is no losing row; this harmless case is included as well.

## 4. Sharpness: full marked actual cost64 examples

The lower bound is attained for both t=2 and t=3. Here is a coefficient
construction, not just a numerical receipt. Use standard frame roots
f_1=e1+e2, f_2=e3+e4, f_3=e5+e6 and their five companions. Choose

    r_1=e1+e7, r_2=e3+e7, and r_3=e5+e7 if t=3,
    J={1,...,t}, K=the remaining frame indices.

These roots have private J coordinates and (r_1,r_2)=1. More generally any
such private root set with (r_1,r_2)!=0 works. Put c_i=(r_i,f_i)=+/-1 and

    s_i=r_i-c_i f_i,   v_i=sigma_i s_i,   sigma_i=+/-1,
    gamma_i=2/(v_i,r_i)=2 sigma_i.

The reflection s_i is a root, (s_i,r_i)=1, and gamma_i v_i=2s_i. Choose
the sign sigma_i to match the chosen root representative. Set

    b_i=delta_(r_i),       xi_i=gamma_i ev_(v_i),
    A(h)=-sum_i xi_i(h)b_i,
    H=(r_1,...,r_t, f_k for k in K),
    q_h=C_h+A(h),         F=(b_1,...,b_t,q_h for h in H).

Private frame coordinates make H a basis. The code distance bound49 and
the flat cap36 show S=C+span(b_i) has S_{<=7}=span(b_i): a word outside
that unit space has at least49-t>=46 support points. Thus d=0 holds for
the actual defined low space.

For root-high normal r_l, the own coordinate vanishes and every other
selected coordinate changes sign:

    q_(r_l)(r_l)=0,
    q_(r_l)(r_i)=-(r_i,r_l) for i!=l.

For a frame-high normal f_k all selected coordinate values merely change
sign. Other coordinates stay unchanged. Root-high supports are therefore
the nonself nonorthogonal P remainders, with span W_(r_l) and weight8;
frame-high supports remain their original W_k supports, also weight8.
The root-high dual is ev_(f_i)/c_i and is corrected. A frame-high dual is

    mu_k=ev_(f_k)/2-sum_i ((r_i,f_k)/(2c_i))ev_(f_i).

It is a frame functional only when it is its own frame, whose label is
absent from W_k. Thus exactly t highs are corrected, no low unit is,
and I=t+64-t=64.

Take v=v_1, marked low index1, and g=gamma_1 b_1+gamma_2 b_2. Both support
roots lie in N(v), so g vanishes on O_v and phi_1(g)=gamma_1!=0. The unit
label ell_(r_1) differs from ell_v, so epsilon=0. This already proves
sharpness of the intrinsic marked theorem.

Let a_j represent each actual restricted functional xi_j, and eta_j be
the actual coefficients of g in F. Define the full factorization by

    p_pi=delta_v, q_pi=g,
    p_j=(1/2)C_(a_j)-eta_j delta_v, q_j=the member of F.

The code expansion gives the projected N0 factorization; subtracting
delta_v g^T from the nonpivot terms and adding the pivot proves exactness.
There are9+t terms, with ranks(P,Q)=(9,8+t). The first low row loses v.
The second edited low row has v-entry

    sigma_1(r_1,r_2)-2sigma_2 in {+/-1,+/-3},

so retains its support. All other rows are unchanged. The free pivot costs0,
each low term costs1, each root-high term costs7, and each frame-high term
costs8. Hence actual cost is t+7t+8(8-t)=64.

Actual rows and columns are nonzero and nonparallel. Low code normals use
one own J coordinate and three K coordinates; root-high duals use only one
J coordinate; frame-high duals use one own K coordinate and some J
coordinates. These patterns are pairwise nonparallel. Two proportional
actual rows would then give a nonzero codeword supported at the single
pivot, contradicting distance49. Columns in F are a basis, and g has two
nonzero low coordinates, so it is parallel to none of them. The replay
checks both actual families directly as well as every N0 entry.

The two separate implementations independently construct members of this
sharp family, including their actual marked coefficients and binary term costs.
They are sharpness examples for this local theorem and consumer, not a
global lower-bound proof outside the displayed class.

### 4.1 Controls for the expanded consumer

For either sharp family, replace g by one third of its displayed value and
scale its actual basis coefficients accordingly. The pivot remains free,
both edited low rows retain their v coordinates, and the actual cost remains
64. Thus the no-losing-row branch has nonparallel, nonzero actual factors.

For a paid-pivot/no-loss example set eta_j=(a_j,v)/4 for every nonpivot
index. The code expansion gives g=C_v/4. Every nonzero v entry is halved
and no row changes support. The pivot costs1 and the total costs65. These
examples cover both t values.

Finally the existing unmarked I=64,epsilon=1 control extends to a normalized
actual cost64 factorization with a paid pivot. Give its three unit lows
coefficients eta=(1,1,1), its marked high coefficient eta_k=gamma, and all
other highs coefficient zero. The pivot g=sum eta_j q_j is not free; otherwise
it would be the missing marked witness. Its cost1 pays the unique rebate1.
The unit-column terms retain cost1 and every other high is unchanged. Direct
entrywise and binary-cost checks in both coordinate algorithms verify this
construction, including ranks(P,Q)=(9,11) and nonparallel actual factors.
This example shows why one cannot simply discard the paid pivot's cost.

## 5. Scope boundary

No assertion is made that every two-sided decoder below64 admits a singleton
pivot, the rank pair (9,8+t), the tight9+t terms, or d=0. Those are the larger
source reduction's obligations. The code-plus-unit row shape is now derived
from the actual rank-nine and singleton hypotheses. Free-pivot support and
existence of a losing root row are not hypotheses of this local theorem.
The source's masked-to-exact completion may add zero-cost terms; this result
does not assert that the completion preserves the displayed tight term count.
The derivation above validates the local passage from the displayed actual
factorization to the marked data and invoice, rather than treating those
local identities as assumptions. It does not establish C2-C6 or all L120.
