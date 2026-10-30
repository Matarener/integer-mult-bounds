# Constructive gauge transport and a dense paired consumer

Dugongue, with substantial OpenAI Codex assistance. Informal mathematics only. No numerical experiments, executable mathematical checks, Lean runs or external searches were used for this note.

The main construction is an event-by-event Gaussian gauge compiler that can change a row's gauge at an ADD without paying twice. Its multivariate form groups a correction on several independent Gaussian axes into one whole Gaussian request. This supplies explicit additional choices for the actual complementary B/C providers. A second, independent construction consumes a common-frame coded pair through a complete dense XOR-convolution algorithm. Neither construction is asserted to furnish an unproved profitable whole supplier or a larger multiplication κ.

## Predecessors and exact scope

The source contracts are the actual complementary quotient and restriction providers in `research/native-dual-suppliers/HETEROGENEOUS-CONTROLLER.md`, its full endpoint identity in `FREE-ENDPOINT-GAUGES.md`, and the Laurent controller construction in `research/kappa-rebuild/bit/complex_controller_factor.py`. Only the mathematical definitions in that source were read; nothing was executed. The local main interfaces have 112 independent pairs, with 56 ordinary A ports and 56 exceptional B or C ports; helper inputs remain independent at every call. The complete native profiles and notices belong to their retained source authors.

The linked `Mathproof/SymplecticTITOCIBalancedCoevaluation20260901.lean` supplies the reciprocal primal/dual cancellation precedent. The previous `algebra.md` supplies the exact two-state carry tensor and common-gauge algebra. The actual whole-K normalizers have the documented form `L_i = Z_z P_Gi`, with an invertible binary linear map and a real linear character. This is stronger than merely being an arbitrary signed permutation and is the hypothesis needed by the XOR-algebra construction below. The retained central-Q decoder proves a fully paid repair of the actual opposite endpoint; its positive Gaussian cost is not erased by this note.

Credit Cao Yifan, DaysSky, Cinna Davis, Nick Petalas, Ryanson Jonathan, Rohan Arun, Dugongue, zxv, Jacob Alan Sussman, the retained provider/controller authors and the Gaussian/Clifford/source08 lineage. The whole-K discussion also retains THU New Media Research Center and Ali Romman's geometry and the native-interface contributors named in the preceding deliverable. The constructions here do not establish world novelty or an exhaustive historical comparison.

## 1. A precise row-gauge ADD construction

Let Q be an explicitly available invertible Gaussian on a selected coordinate block, with every even power of Q an explicitly available ordinary monomial. A field is an arbitrary vector; a row gauge a means that its physical value is Q^a times its logical value. Integer exponents, rather than only parity bits, are retained in all operator identities. Their parity is used only to count Gaussian calls.

Consider the logical ADD

    x_t ← x_t + ε Q^k x_s,

where s and t are distinct fields and ε is an explicitly available scalar. Suppose the source and target enter in gauges b and a. Keep the source in gauge b, and choose the target's outgoing gauge c. The physical update must be

    z_t ← Q^(c−a) z_t + ε Q^(k+c−b) z_s.             (1)

**Theorem C1 (one-axis ADD with a changing target gauge).** The update (1) has an explicit implementation with at most one Q call, fixed ordinary monomial/scalar operations and at most one owned temporary field. It uses no Q call exactly when both displayed exponents are even in this construction. The source is preserved, and the temporary is cleared.

**Proof.** Put α = c−a and β = k+c−b. If both are even, both factors are ordinary monomials: apply the first to the target, copy the source to owned storage if a nontrivial source monomial is needed, add its scaled image, and clear the temporary. If only α is odd, execute Q on the target, with its remaining even power as an ordinary monomial, and add the ordinary source image. If only β is odd, form the source image in owned storage, apply its single Q and even monomial there, and add it to the ordinary target image. If both are odd, rewrite (1) as

    Q[Q^(α−1) z_t + ε Q^(β−1) z_s].

The two inner powers are even. Form the bracket by ordinary operations and then execute Q once on the target. Each case implements the exact integer-exponent identity and preserves the source. An inverse odd Gaussian can equally be written as one Q followed by an even monomial. ∎

The assertion describes an emitted tariff, not a lower bound against every conceivable algorithm for Q. A literal width-dependent butterfly algorithm remains possible and has its own nonrecursive cost.

**Corollary C2 (redirect an already paid correction).** If k is even and a and b have opposite parity, either of the choices c=a and c=b costs one Gaussian in C1. The former transforms a source copy; the latter transforms the target and aligns its output gauge with the source. The alignment costs no additional Gaussian beyond the correction already paid for that crossed ADD.

**Proof.** For c=a the first exponent is even and the second odd. For c=b the first is odd and the second even. Apply C1. ∎

This is a new scheduling choice relative to pricing every crossed ADD while forcing its target gauge to stay fixed. It can affect later queries and scalar boundaries; it does not automatically make their full costs vanish.

## 2. Several commuting Gaussian axes

Let Q_0,...,Q_(r−1) act on explicitly specified mutually independent coordinate axes. They commute, and each Q_j squared is a known monomial. For an integer vector v write Q^v for their product and let supp₂(v) be its odd-coordinate set. The operator Q^v is an ordinary monomial times a whole Gaussian on |supp₂(v)| axes. An actual Gaussian job on this support is one rank-|supp₂(v)| request, with the usual explicit normalizers; it is not a collection of productive outputs on different input fields.

**Theorem C3 (multivariate one-job redirection).** In (1), replace a,b,c,k by integer vectors. Let

    v = k+a−b.

The outgoing target gauge can be chosen as either c=a or c=b−k. In the first case only the source requires the correction Q^v; in the second only the target requires Q^(−v). Both implementations use one whole Gaussian of the same rank |supp₂(v)|, plus ordinary monomials. All input fields remain independent.

**Proof.** Substitute the two choices in (1). For c=a its target exponent is zero and its source exponent is v. For c=b−k its source exponent is zero and its target exponent is −v. The two odd supports agree. Strip the even powers to ordinary monomials and execute the remaining whole Gaussian. ∎

For arbitrary c in several axes, two Gaussian requests may be needed. C1's one-axis conclusion must not be extended to arbitrary vector output gauges. C3 is the constructive alternative that retains one request and equal cost.

For a rank moment t in (0,1), a correction of rank h≥1 has price h^t, rather than h separately priced rank-one calls. The strict inequality h^t<h for h>1 follows from h^(t−1)<1. Grouping is legal only when those axes act on the same arbitrary field in one actual whole request. Independent fields may not be grouped by this argument.

## 3. Exact multivariate incidences for B and C

Let Q_0 be the logical controller's central Gaussian. Let a local physical provider instead use Q_s, and let D be its seven-axis block Gaussian, commuting with the displayed gauges. Its physical types are

    A_s = diag(D,D) S_y(Q_s^(−1)),
    B_s = diag(D,Q_sD) S_y(Q_s^(−1)),
    C_s = diag(Q_sD,D) S_y(1).

More uniformly, set b,c in {0,1} with (b,c) respectively (0,0),(1,0),(0,1). The type is diag(1,Q_s^b) A_s diag(Q_s^c,1). Write e_j for the jth exponent vector.

**Theorem C4 (typed incidences without a hidden adapter).** The physical type equals the gauge-conjugate of the logical A_0 whenever the following integer equalities hold:

    g_X,out − g_X,in = c e_s,
    g_Y,out − g_Y,in = b e_s,
    g_Y,in − g_X,in = e_0 + (c−1)e_s.                 (2)

Its outgoing row difference is then

    g_Y,out − g_X,out = e_0 + (b−1)e_s.               (3)

**Proof.** Gauge-conjugating logical A_0 gives diagonal entries Q^(g_X,out−g_X,in)D and Q^(g_Y,out−g_Y,in)D, and lower off-diagonal entry Q^(−e_0+g_Y,out−g_X,in)D. The first two equations give the physical diagonal entries. Substituting the third into the off-diagonal exponent yields (b+c−1)e_s, which is exactly the displayed typed provider's off-diagonal entry. Subtracting the first two gauge updates gives (3). ∎

Thus B_s takes row difference e_0−e_s to e_0, while C_s takes e_0 to e_0−e_s. In particular B_s can be followed by C_t at their common intermediate difference e_0; C_t can be followed by B_t. These are operator identities, not free changes of chart. Ordinary A ports, all other incident operations and both global boundaries must satisfy their own equalities. If central coordinates overlap other Gaussian factors, the final rank is the odd support of the full combined exponent vector, not the sum of nominal ranks.

## 4. Complete-program telescoping and scalar boundaries

Fix an actually supplied reference controller whose complete identity is

    L M R = diag(T_i).

The scalar RIGHT program R acts first, then M, then the scalar LEFT program L. Choose a row gauge G_j at every chronological field boundary. Implement each event E_j as G_j E_j G_(j−1)^(−1), using C1–C4 where applicable and actual monomial swaps/scales elsewhere.

**Theorem C5 (constructive whole changed request).** The resulting program acts on arbitrary raw inputs by

    G_out diag(T_i) G_in^(−1).

If every T_i is a monomial in the same commuting Gaussians, the result is diagonal, and its exact exponent vector on channel i is the original exponent plus a_out,i−a_in,i. Its productive rank is the odd support of that full vector. Helpers remain separate independent channels when the admitted local endpoints and physical port permutations preserve their original helper ABI.

**Proof.** Multiplying consecutive implemented events cancels each interior G_j^(−1)G_j. What remains is G_out(LMR)G_in^(−1). The assumed reference diagonal identity gives the result, and commuting endpoint factors gives the exponent formula. No Gaussian is executed merely to reinterpret the input logically as G_in^(−1)x: the implemented physical events act directly on raw x. The exact operator on the admitted original fields is diagonal with invertible factors. The only erasures in C1 affect owned temporary copies, so no original arbitrary field is identified or erased. No input fields are merged by a chart choice. ∎

**Theorem C6 (a complete scalar-boundary tariff).** Let B be any fixed scalar row matrix on n fields. Let its prescribed input and output gauges be integer vectors a_i and b_i in a single central Q direction. For either s=0 or s=1, its gauge-conjugate can be implemented with at most

    number{i : a_i differs from s modulo 2}
      + number{i : b_i differs from s modulo 2}

rank-one Gaussian requests, followed or preceded by the actual scalar program and ordinary even-power monomials. Choosing s optimally bounds the total by n.

**Proof.** First change each input field from its physical input gauge to uniform gauge s. This uses one Q exactly for each odd difference s−a_i, together with the actual even monomial. Execute B. A scalar matrix commutes with the same Q^s on every row, so its outputs remain in uniform gauge s. Finally change row i to b_i. The Gaussian count is the displayed sum. The sums for s=0 and s=1 add to 2n, so their smaller value is at most n. ∎

For the two complete boundaries together, one may choose the SAME common outside gauge Q^s on every input and every output channel. Then this common gauge commutes with the diagonal target and changes no productive target. The actual RIGHT boundary can be executed followed by the needed changes to the prescribed interior entrance gauges; the LEFT boundary can be preceded by changes from its prescribed interior exit gauges. Choosing s by the combined majority gives at most n total rank-one requests across both boundaries, since there are 2n interior gauge bits. This proves an honest finite boundary allowance even when the scalar matrices are dense. It does not price the allowance as zero.

## 5. A fully specified alternating schedule, with its actual tariff

This construction applies to the retained p-pair event pattern, for any fixed p≥2 for which the reference complete Laurent factorization is supplied. There are p+2 thick LOCALs: stage 0, every odd stage, and stage 2p. The even stages 2,...,2p−2 are thin Q^(−1) shear queries. Do not alternate provider types over those thin queries as if they were full provider calls.

Use the same 56 exceptional ports throughout. Choose thick provider types alternately B,C,B,C,..., starting with B at stage 0. At the exceptional ports give pair 0 initial gauges (0,0). Stage 0 B changes them to (0,1), so odd stage 1 C is admissible and leaves (1,1). For pair j≥1 choose its entrance gauges equal to the previous pair's post-odd gauges. Those post-odd states cycle as

    s_0=(1,1), s_1=(1,0), s_2=(0,0), s_3=(0,1), s_(j+4)=s_j.

**Theorem C7 (an emitted typed schedule with complete middle pricing).** This gauge assignment admits every typed thick LOCAL. Every forward bridge is ordinary. Exactly ceil((p−1)/2) of the thin queries use a rank-one Gaussian in C1's fixed-gauge construction. The backward terminal bridges use p rank-one requests. Signed swaps transport their row gauges without further Gaussian work. A complete unchanged-target endpoint can be supplied using C6 with at most 2p additional rank-one requests at the two scalar boundaries.

**Proof.** Stage 0 and stage 1 were checked above. A B input pair has equal gauges and its output Y flips, producing an opposite pair; the following C accepts that pair and returns an equal pair with the opposite common bit. Repeating gives the displayed four-state cycle. Before pair j+1's first LOCAL its entrance gauges equal pair j's post-odd gauges. Both forward bridges connect those same row gauges: the intervening thin query does not change a chosen gauge. Their coefficients therefore remain even powers of Q, so they are ordinary.

The thin query is a forward Q^(−1) ADD. Its physical coefficient is odd exactly when the two current row gauges agree. Those are the C outputs, indexed by even j among 0,...,p−2. There are ceil((p−1)/2) of them. Neighboring states s_j,s_(j+1) differ in exactly one bit, so each usual backward bridge has exactly one crossed ADD. The final pair receives one additional thick LOCAL after its odd stage; its final state is s_p rather than s_(p−1). Since s_p and s_(p−2) differ in both bits, the last backward bridge has two crossed ADDs. Thus the p−2 ordinary adjacent bridges cost one each and the last costs two, totaling p. A signed swap moves the attached gauge with the row and introduces only its known scalar sign. There are n=2p rows in the scalar boundaries; apply the common-outside-gauge consequence of C6 to obtain at most 2p additional calls without changing the diagonal target. ∎

At the 56 ordinary ports use the original zero-gauge A incidences and their unchanged thin-query tariff. Every local helper is fresh and retains its own endpoint. The number of B calls is ceil((p+2)/2), and C calls floor((p+2)/2), so their helper and paid profiles are summed with exactly those multiplicities. Every seven-axis IDLE is charged on its actual selected stage set.

C7 is a complete sufficient construction, not a claim that naive alternation funds a larger exponent. In particular, the middle count p+ceil((p−1)/2) is greater than the old p−1 thin-query count. The additional redirection choices in C2–C3 can alter this schedule and its future boundary cost, but a lower complete moment must be proved for an actual resulting word before it is promoted. C7 prevents a local B→C match from being mistaken for a free entire controller.

## 6. A separate dense consumer from the convolution algebra

Let Γ be a finite abelian group and let A be its complex group algebra, represented as coefficient arrays with convolution *. If α is a group automorphism and χ a character, define

    Lx(g) = χ(g) x(α^(−1)g).

**Theorem C8 (explicit algebraic normalizers).** L is an invertible algebra automorphism of A. If Γ=(Z/2)^f, these are exactly the form of binary-linear index permutations followed by real linear characters used by the documented whole-K normalizers.

**Proof.** Reindexing a convolution by the additive bijection α preserves the equation a+b=g. Character multiplicativity gives χ(a)χ(b)=χ(g) in each summand. Hence (Lx)*(Ly)=L(x*y). Both factors are invertible and preserve the convolution identity. In the binary case a real linear character is (−1) raised to a binary linear form, which is exactly the stated sign multiplier. ∎

The theorem concerns linear coordinate permutations and character signs. An arbitrary affine translation or arbitrary signed permutation does not satisfy the same automorphism identity and is not silently included.

Let L=diag(L_1,...,L_R), let K be a scalar R by R matrix with K^T K=I, and set C=L^(−1)(K⊗I)L. Define the A-valued bilinear output

    Ψ_L(x,y) = sum_(u=1)^R (L_u x_u)*(L_u y_u)
             = sum_u L_u(x_u*y_u).

**Theorem C9 (a complete paired coded consumer).** For all arbitrary dense x,y,

    Ψ_L(Cx,Cy)=Ψ_L(x,y).

The same holds for a product of such codes sharing the same L. If a convolution filter F is invertible, then also

    Ψ_L(F^(−1) Cx, F Cy)=Ψ_L(x,y),                   (4)

where F acts on every owner field by the same convolution. More generally x,y may be replaced by any explicitly supplied operator images D x and E y, without a commutation assumption on C with D or E.

**Proof.** Put a=Lx and b=Ly. Then L(Cx)=Ka and L(Cy)=Kb. Expand the output:

    sum_u (sum_v K_uv a_v)*(sum_w K_uw b_w)
      = sum_(v,w) (sum_u K_uv K_uw) (a_v*b_w)
      = sum_v a_v*b_v.

This uses K^T K=I and bilinearity over the commutative coefficient algebra. Products of orthogonal K matrices remain orthogonal, proving the common-frame assertion. If F is convolution by h, its inverse is convolution by a convolution inverse of h. Associativity and commutativity give (F^(−1)z)*(Fw)=z*w for every pair of fields. Apply this cancellation before applying L_u and summing. Substitution of D x,E y proves the last statement. ∎

A varying normalizer itinerary is NOT automatically a common L. One sufficient case is L_(j,u)=A_j L_u for an owner-independent algebra automorphism A_j: then that A_j commutes with every scalar owner matrix and cancels in each code, leaving exactly L^(−1)(K_j⊗I)L. This gives an actual nontrivial family of admissible changing descriptions while preserving the common-frame theorem.

For binary Γ, the documented central Q_f has one-bit coefficients a=(1+i)/2 and b=(1−i)/2, so it is convolution by the tensor product of the two-point vector (a,b). Its Fourier eigenvalues are products of a+b=1 and a−b=i and are therefore nonzero. It is an invertible convolution filter, and (4) applies with F=Q_f.

However, the actual source positive terminal P E Q is not automatically the companion Q P E required in (4). They agree only under an established commutation relation. Nor does XOR convolution equal cyclic convolution on integer digit indices. Those actual interface conditions are retained explicitly.

## 7. An explicit dense algorithm and its output contract

**Theorem C10 (dense XOR contraction without decoding the codes).** For Γ=(Z/2)^f, N=2^f, and the C9 normalizers, Ψ_L(z,w) is computed on arbitrary dense arrays by 2R forward Walsh transforms, one inverse Walsh transform, and O(RN) ordinary pointwise products, additions and frequency permutations. Using the ordinary butterfly recursion gives O((R+1)Nf) field work. If an actually supplied all-input Walsh procedure has complete cost W(N,f), the same construction has cost at most (2R+1)W(N,f)+O(RN), with its actual coefficient/precision costs included.

**Proof.** Let Hx(ξ)=sum_g (−1)^(ξ·g)x(g), so H^(−1)=H/N. Direct character orthogonality proves H(x*y)=Hx·Hy. Also

    H(L_u x)(ξ) = Hx(α_u^T(ξ+z_u))

when χ_u(g)=(−1)^(z_u·g). Thus compute Hz_u,Hw_u once each, permute their frequency coordinates by the known affine bijection, multiply and sum the R pairs, and apply H^(−1) once. The convolution theorem gives exactly Ψ_L(z,w). Splitting a Walsh transform by its final bit yields two half-size transforms and N scalar additions/subtractions, hence O(Nf) operations by induction. This is an explicit dense algorithm, rather than an inference from tensor bond dimension. ∎

The output here is one A-valued sum of R products, not R independent Gaussian outputs. The theorem therefore gives no license to retain R old productive-target credits. It is a useful changed consumer when the surrounding multiplication formula already requires that sum. Mapping it to a full integer-multiplication caller still requires an exact carry-aware/cyclic interface and a compatible companion producer; no such missing map is assumed in these proofs.

The main actionable positive result for the actual B/C route is C1–C6: full chronological gauge changes, one-job target redirection and a complete finite boundary tariff. The dense consumer C8–C10 is a distinct exact service that can be considered by a multitype assembly theorem only at its true input/output dimensions and its displayed paid cost. No larger κ has been inferred from an unpaid local match or a changed output sum.


