# Three-contribution rigidity for two-sided address twists

## Scoped result and inherited model

Use the odd-denominator coefficient ring O=Z_(2), Gamma=M_m(O), m>=2,
and R=F2[Gamma] from PR5003 (`bit-address-twist-second-order/PROOF.md`).
There are exactly three arbitrary dirty registers. Paid calls are
D_N(A)=I+([A]-1)N with rational rank-one A in Gamma, conjugated by an
independent diagonal tuple tau_jr(B)=L_jr B R_jr, L_jr,R_jr in GL_m(O).
The new **eight-call pattern** contains two independent J=uu^T calls,
one P_s=u e_s^T for each s, and one D_s=e_s e_s^T for each s, u=(1,1,1)^T.
All orders and all these twists/frames are allowed. No further mixing or
registers are allowed. Twists are favorably free; this is not a native tariff.

**Theorem.** If this word equals diag([C_0],[C_1],[C_2]) as an operator on
(R/I^3)^3, where I is the augmentation ideal, then every C_s mod2 has matrix
rank at most one. In particular it cannot realize three I_m targets, m>=2.
The same conclusion holds if any listed frame is zero modulo two.

This is a different first-order-feasible pattern from PR5003's one-J seven-call
pattern. It is not a classification of arbitrary eight-call words, a universal
nine-call bound, a supplier, a kappa improvement or independent formal acceptance.

## 1. Rank distance of two-sided transports

Let V=M_m(F2). For distinct linear maps U(B)=LBR and U'(B)=L'BR', with
all four factors invertible, rank(U-U')>=m.

Composing with U^-1 reduces the assertion to F(B)=B-XBY. If X is not scalar,
there exists v such that v and Xv are independent. Indeed, if every nonzero
vector were its own invariant line, over F2 invertibility would give Xv=v
for every v. Choose a linear functional ell with ell(v)=1 and ell(Xv)=0.
On the m-dimensional subspace B=v w^T, ell(F(B))=w^T, so F is injective
there and rank(F)>=m. If X is scalar, it equals I; then F(B)=B(I-Y), whose
rank as a map of matrix spaces is m rank(I-Y). Distinctness gives Y!=I,
so this is at least m. This proof does not assume uniqueness of a factorization.

## 2. Three-term quadratic rigidity

Let a_1,a_2,a_3 in V, and let U_1,U_2,U_3 be two-sided invertible transports.
Suppose

    sum_i a_i=0,    sum_i a_i (U_i z)=0 in Sym^2(V), for all z in V.       (1)

Polynomial squares are retained. Then the nonzero terms have a common U_i.
Consequently, if b_i=U_i^-1 a_i, then sum_i b_i=0.

If all a_i vanish the conclusion is immediate. Exactly one nonzero term is
impossible. If exactly two are nonzero they coincide, and injectivity of
multiplication by their nonzero linear polynomial forces their transports equal.
If all three are nonzero, a_1 and a_2 are distinct, hence linearly independent
over F2, and a_3=a_1+a_2. Equation (1) gives

    a_1 ((U_1-U_3)z) + a_2 ((U_2-U_3)z)=0.                            (2)

In the ordinary polynomial ring, the distinct linear factors a_1,a_2 are
coprime. Thus the degree-one forms (U_1-U_3)z and (U_2-U_3)z are respectively
lambda(z)a_2 and lambda(z)a_1. This holds also when either is zero; over F2
the scalar lambda(z) is unique and linear in z. The two difference maps have
rank at most one. Section1 and m>=2 force both differences to vanish.
Then sum b_i=U_3^-1(sum a_i)=0. We use only homogeneous degree two, so the
argument does not mistake the truncated algebra for an integral domain.

The rank-distance premise matters: arbitrary invertible linear maps of V can
differ by rank one. The verifier supplies an explicit such three-term solution
with distinct maps. Therefore this lemma does not eliminate arbitrary linear
address relabeling or four-or-more-term syzygies.

## 3. Apply the lemma to the actual eight-call pattern

The predecessor establishes R/I^3 = F2[t_1,...,t_(m^2)]/(degree>=3), with
V=I/I^2 and degree2=Sym^2(V). This follows by reducing Gamma modulo4; odd
denominators are invertible there. Its derivation and operator convention are
retained, not replaced by Boolean or square-free polynomial semantics.

For call j define a_jr=tau_jr(A_j) mod2 and let U_jrs be the induced map
of tau_jr tau_js^-1 on V. Source compatibility gives

    a_jr=U_jrs a_js.                                                 (3)

A call increment raises augmentation degree at least one. For an off-diagonal
block (r,s), constants give sum a_jr=0. Dirty degree-one input z gives
sum a_jr(U_jrs z)=0 in degree2. Products of two increments have degree>=3
on that input, so these necessary conditions are independent of chronology.
In products, later calls act on the left. We do not discard cross terms on
constant inputs; we simply do not need them for this necessary obstruction.

Exactly three calls contribute to (r,s): J_1,J_2,P_s. Apply Section2 and (3):

    a_J1,s+a_J2,s+a_Ps,s=0.                                          (4)

The diagonal first-order equation is therefore c_s=a_Ds,s. Reduction mod2
of a rank-one matrix over O has rank<=1, by vanishing of its 2x2 minors;
invertible left/right twists preserve this. Hence rank(c_s)<=1 for each s.
The proof includes all zero reductions and every call order. It does not need
an exhaustive twist enumeration or an endpoint search.

## 4. A genuinely new first-order-feasible fixture

For m=3 take untwisted frames A_J1=E00 and A_J2=E01. For P_s use A=E00;
choose its role-s transport to send E00 to d=(e0+e1)e1^T and its other two
role transports to send E00 to b=e0(e0+e1)^T. Such maps are invertible
left/right maps: at role s use L=I+E10 and R exchanging columns0,1; at
other roles use L=I and R=I+E01. Take A_Ds=E22, untwisted. Then in every
off-diagonal block E00+E01+b=0, while every diagonal increment is
E00+E01+d+E22=I3. Every one of the eight frames is nonzero and rank one.
This passes the constant-input first-order screen, yet the theorem excludes it.
The two J terms have equal transport, while the P_s relative transport is
different. For a basis z with z!=U_Ps,rs z the dirty residue is
b(z+U_Ps,rs z), nonzero by polynomial injectivity. The independent sparse
(Z/4) group-ring oracle checks this residue after the actual complete word.

## Evidence and open boundary

The quantified result is the written proof. The finite verifier checks all
36 two-sided GL2(F2) maps, their pairwise rank distances, all nonzero
three-form/transport solutions in a reduced complete local domain, the above
m3 fixture, independent dirty group-ring calculations, and direct positive
controls. It retains an arbitrary-GL(V) counterexample as a boundary control.
No finite check substitutes for the all-m proof. Arbitrary other projectors,
extra mixing/helpers, even denominators, and native pricing remain open.

Credit PR5003 Krzysztof Wójt and PR4953 JoyboyBrian; Cinna Davis/PR2110
and the Ali Romman, eumemic and huxint lineage. Prepared by JoyboyBrian with
substantial OpenAI Codex assistance. Apache-2.0.
