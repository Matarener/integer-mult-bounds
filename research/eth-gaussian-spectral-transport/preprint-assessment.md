# Exact counting and Gaussian valued tapered recovery

Dugongue, with substantial OpenAI Codex assistance. The positive mathematical extraction is an explicit Gaussian-valued Hermite recovery constructor with a complete precision bill. Its proof is supplied below. This is an informal theorem, not a fresh formalization, an independently accepted proof of the preprint's full ETH claim, or a new multiplication κ by itself.

## 1 What the pinned preprint actually states

The source is OpenAI, *The Exponential Time Hypothesis is False*, revised October 25, 2026, pinned to repository commit `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a`. The main theorem states a deterministic exact counting algorithm for every fixed k>=2. For n declared variables and m clauses its bit-operation bound is

    (n+m)^(O_k(1)) 2^(O_k(n log log n/sqrt(log n))),

with polynomial space. When m<=D n for fixed D, the exponential factor improves to 2^(O_(k,D)(n/sqrt(log n))). The fixed-k qualification matters: the displayed constants can depend on k. The source uses exact residue and rational arithmetic, not a unit-cost arithmetic oracle.

The body also proves a weaker interpolation bound with n(log log n)^2/sqrt(log n) in the exponent; the sharper main bound comes from its final tensor-contraction appendix. These should not be conflated. The original manuscript date is October 17 and its displayed revision date is October 25.

The tensor-contraction interface is particularly relevant. With s a size parameter, the source allows a bipartite Boolean tensor network with O(s) wires, polynomially many vertices, maximum degree at most ceil(s^(9/10)), and entries in

    (Z/2^P Z)[V]/(V^ell),  P,ell=O(s).

A tensor entry must have an explicit uniform evaluator costing a fixed polynomial in s plus description length, times 2^(A s^(9/10)); it must use polynomial space. The claimed contraction cost is a fixed polynomial in the same description length times 2^(O(s/sqrt(log s))). Both entry-description size and entry-evaluation work are part of the theorem.

**Primary sources.** [Pinned manuscript](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/main_full_version.tex), [quantitative contraction proof](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/quantitative-contraction.tex), and [quantitative reduction](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/quantitative-reduction.tex).

## 2 Pivotal steps inspected and their evidence level

The assessment read the main counting construction, its measurement separation and Boolean-difference identities, replacement-row and coefficient bounds, sparse parity checks and greedy derandomization, and the full quantitative contraction proof. The final circuit-lower-bound appendix was also read. This is substantial proof inspection, not exhaustive independent verification of the whole manuscript or its cited prerequisites.

The following distinctions affect any attempted transfer.

- **Shared summaries.** At an interpolation node, each factor's dependence on other variable groups factors through explicitly supplied integer measurement rows. Bounds on their row sums control the number of measurement values. Rank alone is insufficient: one binary-weight row can distinguish every Boolean vector. The separation identity is exact distributivity after grouping assignments by their actual summaries.
- **Restoration at the origin.** Polynomial replacement forms restore each original variable at zero. Values and sufficiently many Taylor coefficients at other nodes recover that origin. The node routines are not assumed to preserve a source factor's interpretation as a Boolean indicator away from zero.
- **No uncomputed high-precision lift.** Each implicit tensor stores a creation precision. Subsequent recursive calls use the SAME canonical representatives chosen at that creation precision. Canonical lifting is not a ring homomorphism, so this convention is a necessary part of the actual deformation.
- **Precision drives branching.** Tapered node multiplicities reduce the needed local precision from an untapered order MD to order MD/u. Cross-group modes have divisibility proportional to their weights, so only weighted monomials below that precision survive.
- **Explicit child contraction.** Each mode monomial factors into actual child networks with at most M/8 wires. Vertex labeling, packet construction and child entry descriptions are included; an unimplemented low-rank observation does not supply those networks.
- **No SAT-counting circularity in the stated reduction.** Greedy parity tests compare counts from an independently constructed sparse-polynomial counter. The unknown satisfying count is a common additive term for all candidate tests, so minimizing the total also minimizes remaining bad assignments. The procedure need not know that common term. Accepting the resulting headline algorithm still requires the independently specified counter and all its complexity bounds.

The manuscript advertises an ordinary deterministic fixed-k algorithm. Its E^NP oracle appears in a separate circuit-lower-bound consequence, not as an oracle supplied to its counting algorithm. The informal Gaussian extraction below depends only on elementary polynomial interpolation and valuation calculations; the headline complexity claim is not a premise of that extraction.

## 3 Gaussian residue arithmetic with an exact unit convention

Put π=1+i and let R=Z[i]_(π), the localization of the Gaussian integers at the prime generated by π. Let K=Q(i). The valuation v_π is normalized by v_π(π)=1. Since π²=2i,

    v_π(n)=2 v_2(n) for every nonzero rational integer n.

A unit of R has valuation zero. In particular an odd rational integer, such as 13, is a unit; division by 2 or π is not a unit operation.

For a finite coefficient algebra K[V]/(V^ell), use coefficientwise valuation: its value is the minimum of the valuations of its coefficients, with v(0)=infinity. Then v(A+B)>=min(v(A),v(B)) and v(AB)>=v(A)+v(B). The latter may be strict because the coefficient algebra has nilpotents, which causes no problem below. All scalar interpolation coefficients are central.

**Lemma G1  Exact Gaussian unit arithmetic.** A supplied Gaussian integer u not divisible by π is invertible modulo π^P. One constructive recipe uses u^(-1)=conjugate(u)/Norm(u), where Norm(u) is odd, followed by ordinary odd-integer modular inversion. Gaussian division by π, when divisibility is proved, is the exact map

    (a+bi)/(1+i)=((a+b)/2)+((b−a)/2)i.

**Proof.** π divides a+bi exactly when a and b have the same parity. In the opposite-parity unit case a²+b² is odd, so its inverse exists modulo every power of two and hence modulo every power of π. Multiplying by conjugate(u) gives the inverse. In the divisible case both displayed numerators are even and multiplication by 1+i verifies the quotient. QED.

These are actual integer operations. Their bit cost, copies, scans and owned buffers remain ordinary work. A fixed coefficient can have a fixed literal word; a coefficient whose bit length grows with a construction parameter must be charged at that growing length.

## 4 Weighted truncation and its finite mode count

**Lemma G2  Valuation weighted truncation.** Let

    H(Z)=sum_beta c_beta product_j Z_j^(beta_j)

be a finite polynomial, with v_π(c_beta)>=sum_j w_j beta_j and positive integer w_j. On π-integral arguments, every term of weighted degree at least P vanishes modulo π^P. More generally, if v_π(Z_j)>=−d_j, the valid effective weight is w_j−d_j, rather than w_j.

**Proof.** Valuations of a product are at least the sum of the displayed coefficient and argument valuations. Every discarded term has valuation at least P. Their finite sum also has valuation at least P. QED.

The argument bound is part of the contract. Clearing a dyadic denominator consumes precision; it cannot be relabeled as an odd unit.

**Lemma G3  A small number of modes per weight gives a short enumeration.** Suppose a finite variable set has at most K variables of each positive integer weight, with K>0. The number of nonnegative exponent tuples of weighted degree below P>0 is at most

    exp(2 sqrt(2 K P)).

If all weights are twice their positive base weights, with at most K variables per base weight, the bound becomes exp(2 sqrt(K P)).

**Proof.** For θ>0, the count is at most

    exp(θP) product_j (1−exp(−θw_j))^(−1).

Its logarithm is at most θP+K sum_(w>=1)−log(1−exp(−θw)). Expanding the logarithm and summing the geometric series bounds this sum by

    sum_(h>=1) 1/[h(exp(θh)−1)]
      <=(1/θ)sum_(h>=1)1/h² <=2/θ.

Use θ=sqrt(2K/P). For doubled weights apply the first assertion with effective budget P/2. Finite bounded-budget tuples can be enumerated by choosing exponents successively, and every partial feasible tuple has its all-zero continuation. QED.

This proof is independent of the preprint's global complexity theorem. It explains exactly which valuation and multiplicity witnesses a proposed Gaussian deformation must provide.

## 5 A Gaussian valued tapered Hermite constructor

The following is the directly usable local theorem. It gives an explicit recovery algorithm and its precision bill.

Choose integers a>=u>=1 and M>=u. Define

    L=2^a,
    S={−L,−L+1,...,L−1},
    alpha=2^(a+1),
    h=ceil(3M/u).

For every NONZERO t in S put i=v_2(t), D_t=L/2^i and

    q_t=h max(0,u−i).

Only nodes with q_t>0 are queried. The origin is omitted, so its desired value is never an input to the recovery procedure. Set q_t=0 on inactive nonzero nodes in products below.

**Theorem G4  Gaussian tapered Hermite recovery.** Let F(T) lie in (K[V]/(V^ell))[T], have degree at most M(2L−1), satisfy F(0) in R[V]/(V^ell), and satisfy

    F(t+alpha z) in (R[V]/(V^ell))[z] for every t in S.

For any P>=1, F(0) modulo π^P is constructively recoverable from the first q_t coefficients of F(t+alpha z), each supplied modulo

    π^(P_t),
    P_t=P+16hD_t+16M(a+1),

at every active nonzero node t. All data and arithmetic are finite and exact. The scalar recovery costs polynomially many bit operations in M,L,a,ell,P and the supplied coefficient-description lengths.

### Proof part 1  Enough jets and an explicit identity

There are L odd nodes in S. At each of them q_t=hu, so

    sum_(t!=0) q_t >=Lhu>=3ML>M(2L−1).

Also h<=4M/u and q_t<=4M. Define the scalar polynomial

    E_t(T)=product_(s in S, s!=0,t) ((T−s)/(t−s))^(q_s).

It equals one at its own node and vanishes to order q_s at every other active node. Put

    B_t(z)=[ F(t+alpha z)/E_t(t+alpha z) ]_(degree<q_t).

Ordinary Hermite interpolation gives the exact formula

    F(0)=sum_(t:q_t>0) E_t(0) B_t(−t/alpha).

For completeness, replace zero by an indeterminate T. The right side has degree less than Q=sum q_t. At each active node its Taylor coefficients through order q_t−1 equal those of F. Its difference from F is divisible by product_(t!=0)(T−t)^(q_t) and has degree below Q. It is therefore zero. This is applied coordinatewise in the basis 1,V,...,V^(ell−1), so no field property is incorrectly assumed for the nilpotent coefficient algebra.

### Proof part 2  Forming the local quotient loses no precision

For distinct s,t in S, v_2(t−s)<=a. Thus

    E_t(t+alpha z)
      =product_(s!=0,t) (1+alpha z/(t−s))^(q_s)

has π-integral coefficients and constant coefficient one. Its reciprocal modulo z^(q_t) is also π-integral, by formal inversion of a series with constant term one. Consequently input jet errors divisible by π^(P_t) still have that divisibility after multiplication by this reciprocal and truncation.

### Proof part 3  The tapered prefactor loses at most 12hD_t powers of π

Fix t with i=v_2(t) and write D=D_t. Since E_t(0) is a nonzero rational scalar,

    v_2(E_t(0))
       =sum_(s!=0,t) q_s[v_2(s)−v_2(t−s)]
       =D sum_(j=1)^(a−i) (j/2^j)[q(i+j)−q(i)],

where q(j)=h max(0,u−j). Here is the count behind the second equality. Nodes s of valuation below i contribute zero. For each j>=1 there are D/2^j nodes of valuation i+j, and D/2^j nodes whose difference from t has valuation i+j. The latter have valuation i. These follow from the complete residue grid of length 2^(a+1); the excluded zero and t do not contribute to these sets.

The taper is h-Lipschitz, so q(i+j)−q(i)>=−hj. Therefore

    v_2(E_t(0))>=−Dh sum_(j>=1) j²/2^j=−6Dh.

The geometric-series identity gives the final sum. Integer rational valuations double in the Gaussian ring, hence

    v_π(E_t(0))>=−12Dh.

### Proof part 4  Evaluation and summation complete the precision proof

The Gaussian valuation of −t/alpha is 2i−2(a+1), at least −2(a+1). Since B_t has degree below q_t<=4M, evaluating any coefficient error at that point loses at most 8M(a+1) powers of π. Multiplying by E_t(0) loses at most another 12hD_t. Thus the error in that node's contribution has valuation at least

    P_t−12hD_t−8M(a+1)>=P.

The sum of all node errors has valuation at least P as well. There is no extra logarithm of the number of nodes in this nonarchimedean sum bound. Since the exact answer F(0) is π-integral, the reconstructed sum has the same residue modulo π^P. QED.

### Proof part 5  Actual finite residue arithmetic

Every coefficient in the Hermite formula is an explicitly specified rational scalar. Products contain polynomially many factors and their integer numerator/denominator lengths are polynomial in M,L,a. The input jets have finite Gaussian residue representatives. Arithmetic can therefore be performed on exact rational Gaussian coordinates, cancelling the powers of π only when divisibility has been established and inverting the remaining units by G1. An explicit alternative avoids rational array states: choose one common Gaussian denominator D for all recovery coefficients; let d=v_π(D). Accumulate the cleared linear combination modulo π^(P+d), then divide by π^d and invert D/π^d. The per-node precision bounds already prove that its unknown higher digits cannot affect this numerator modulo π^(P+d).

A canonical representative modulo π^P may be chosen by successive division: subtract the unique digit in {0,1} giving divisibility by π, divide, and repeat P times. Any implicit operand must retain the SAME creation-time representative when subsequently used at higher precision. A later arbitrary lift is not a replacement for information that was never computed.

The construction uses ordinary finite Gaussian-integer arithmetic, initialization, copies and cleanup. If it is applied entrywise to a matrix or payload bank, multiply its arithmetic and movement costs by the actual number of entries processed. Those operations do not become free because the formula has a short mathematical description.

## 6 An explicit deformation satisfies the integrality hypotheses

The Hermite assumptions are achievable by a literal construction, rather than being a request for an unknown integral family.

**Theorem G5  A Gaussian-integral Cauchy deformation.** Let

    C(T)=product_(s in S)(T−s),
    W_xy(T)=C(T)/[C'(0)(T−(y−x))],  0<=x,y<L.

The denominator's linear factor cancels, so every W_xy is a rational polynomial of degree 2L−1. Its exact values satisfy W(0)=I, and W_xy(t+alpha z) has coefficients in R for every t in S. The same holds for a block-diagonal collection of packets, restricted to their actual occupied ports.

**Proof.** On the diagonal y=x the cancellation at zero gives C'(0)/C'(0)=1. Off the diagonal a zero numerator factor remains at zero. For the local integrality, the nonzero differences t−s on the complete residue grid have a valuation multiset independent of t. Thus v_2(C'(t))=v_2(C'(0)). In C(t+alpha z), its distinguished t factor is alpha z and every other factor is coefficientwise divisible by 2^(v_2(t−s)). Divide by C'(0). If the omitted y−x factor is the t factor, all powers of two cancel integrally. Otherwise its valuation is at most a and the alpha z factor retains a surplus of at least one power of two. Odd denominators are units. Hence every coefficient is 2-adically integral and therefore π-integral. QED.

For a concrete finite Boolean tensor contraction, write A(Y) and B(X) for the products of its two sides' lifted π-integral entries. Replace its wire equality by the literal polynomial

    F(T)=sum_(X,Y in {0,1}^M) A(Y)B(X)
           product_(row ports x) l_(Y_x)((W(T)X)_x),
    l_0(z)=1−z, l_1(z)=z.

At T=0 the product is exactly the equality indicator X=Y, so F(0) is the original Gaussian-valued contraction. The degree is at most M(2L−1), and G5 makes every local Taylor polynomial π-integral. Thus G4 applies to this explicitly defined F. It has a finite brute-force evaluation even before any structural shortcut is discovered. A faster jet evaluator, with its physical cost, is a separate construction to supply.

The coefficients A,B can also lie in R[V]/(V^ell). Their commutativity supplies the displayed product; all valuation estimates remain coefficientwise. A different phase coefficient field requires its actual extension and ramification, as in G7 below.

## 7 The taper produces a proved precision reduction

**Corollary G6  Quantified taper dividend.** Suppose the input precision and evaluation-loss term obey

    P+M(a+1)<=B M D_t/u

for a specified constant B at an active node. The Gaussian precision of G4 then satisfies

    P_t<=(64+16B) M D_t/u.

For comparison, in the SAME Hermite prefactor construction give every valuation level below u one uniform multiplicity q*=Θ(M), with all higher multiplicities zero. At the last active level i=u−1 that explicit prefactor loses Θ(M D_t) powers of π. This comparison concerns the stated termwise Hermite recipe, not a universal lower bound on every possible interpolation algorithm.

**Proof.** Since h<=4M/u,

    P_t=P+16hD_t+16M(a+1)
         <=64MD_t/u+16[P+M(a+1)].

For the uniform multiplicity, the valuation identity in G4 instead gives

    v_π(E_t(0))=−2D_t q* sum_(j=1)^(a−u+1) j/2^j.

Here a>=u, so the finite sum is at least 1/2 and below 2. The loss is therefore between D_t q* and 4D_t q*, proving the asserted order. QED.

This is the positive feature to import: spread the required total jet multiplicity across valuation levels with a bounded slope, so a local denominator sees the slope rather than the largest multiplicity. The inherited precision condition is explicit. In the preprint's recursive construction it is obtained by cumulative packet scales: D_t contains an extra exponential factor absorbing earlier precisions. It must be proved again for a proposed multiplication schedule, rather than assumed from its name.

Combined with G3, a family with at most K=O(M/D_t) modes per base weight and doubled π weights needs at most

    exp(O(sqrt(K P_t)))=exp(O(M/sqrt(u)))

weighted monomials when G6's hypotheses hold. This is an exact arithmetic/precision mechanism; it becomes a runtime gain only when all those monomials admit the claimed cheap entry and delivery algorithms.

## 8 Other fixed phase extensions have a counted ramification cost

**Corollary G7  A discrete valuation version.** Let a declared characteristic-zero phase field have a discrete valuation v with v(2)=e>0, odd integers units, and an integral local ring. Under G4's local integrality and origin assumptions, the SAME integer grid and taper recover F(0) modulo the Pth power of its uniformizer from node precision

    P_t=P+8e hD_t+8e M(a+1).

**Proof.** All nonzero rational scalar valuations equal e times their ordinary 2-adic valuations. The prefactor loss is at most 6e hD_t and local evaluation loses at most 4e M(a+1). The reciprocal of the local E_t series remains integral with constant term one. The stated precision exceeds the sum of these losses plus P. The interpolation identity itself is characteristic-zero polynomial algebra and is unchanged. QED.

The Gaussian case has e=2. A source with additional roots of unity must specify its actual coefficient field, a suitable local ring, residue arithmetic and e. The preprint's unramified auxiliary field does not automatically contain i or every source phase; no phase extension is being treated as free.

## 9 A hand-worked recovery example

Take a=u=M=1. Then L=2, S={−2,−1,0,1}, alpha=4 and h=3. Only the two odd nodes are active, with q_(-1)=q_1=3. Their six Taylor coefficients determine every polynomial of degree at most three. G4 supplies a conservative local precision P+128.

For a cubic F(T)=A+BT+CT²+DT³ with Gaussian-integer coefficients, a shorter exact formula uses only the constant and linear local Taylor coefficients. Write

    c_+=coefficient of z in F(1+4z),
    c_-=coefficient of z in F(−1+4z).

Direct expansion gives

    F(0)=[F(1)+F(−1)]/2−(c_+−c_-)/16.

Indeed the first term is A+C and c_+−c_-=16C. Precision P+8 at these four coefficients suffices modulo π^P, because 16 has π valuation eight and 2 has valuation two. This illustrates both the literal arithmetic and the conservative nature of the general bound. It does not claim that the supplied evaluations are Gaussian-query free or that the recovered outputs are independent new jobs.

## 10 Exact operator recovery is a real constructor

**Corollary G8  Entrywise operator or payload recovery.** Let a finite operator-valued polynomial F(T) have entries satisfying G4 in one fixed basis. Given actual source-preserving routines for the required jets F(t+alpha z)x on the SAME arbitrary π-integral input x, G4 recovers F(0)x modulo π^P by an explicit ordinary linear recombination, provided all declared coefficient denominators are accounted for. No new Gaussian request is needed by the recombination itself.

**Proof.** The π-integral input makes the local vector jets and origin value π-integral. Apply the scalar Hermite identity to every matrix entry, or directly to the resulting vector over the coefficient field. All interpolation coefficients are central scalar values. Use the cleared-denominator algorithm in proof part 5 on separately owned buffers. It leaves x untouched, forms the exact residue of the requested output, then clears every owned query and recovery buffer after its last use. QED.

For a source input in π^(−d)R^n with a known d>=0, first clear that common denominator. Apply G4 to π^d F(T)x at target precision P+d and restore its declared π^(−d) output header. The recovered error after that restoration is divisible by π^P. This raises the requested node precisions and does not treat a nonintegral input as though it were integral.

The ordinary cost includes scalar multiplications, exact divisions, unit inversions, masks/codecs if used, input copies, output additions, array scans, routes and suspended-instance reserves. If F(0)x is promised to have Gaussian-integer coordinates A+Bi with |A|,|B|<=H, choosing P=2p and 2^p>2H gives exact signed coordinate recovery: π^(2p) and 2^p generate the same Gaussian ideal, so each ordinary coordinate is known modulo 2^p and has a unique representative in the stated interval. The height promise must come from the actual source; it is not inferred from the modular calculation.

Productive targets belong only to their actual original independent inputs. Several recovered functions of one x are not automatically several independent Gaussian jobs. Absolute phase, input/output ABI and all-column identities remain part of each proposed source implementation.

## 11 What can be transported to integer multiplication now

There are two constructive uses, with distinct outputs.

**Fixed-word discovery.** Encode a bounded source family of legal frames, exact common-target requests, ownership rules and coefficient choices. A correct finite SAT or counting encoding can nominate a witness, and the preprint's claimed SAT algorithm is one possible future search engine. The useful released result would be the explicit new word and independent endpoint/invoice proof. A faster search engine does not itself improve an already fixed multiplier's κ. A bounded source family must be encoded with all its physical and phase conditions, not only an optimistic rank objective.

**Gaussian deformation and tapered recovery.** Build a literal operator family with an exact origin map, π-integral local jets and source-realized low-cost node routines. G4–G8 give a complete recovery/precision constructor; G6 and G3 quantify the taper and weighted-mode advantages. The algebraic-application companion develops concrete ordinary polynomial/partial-swap evaluators. The next mathematical task is a source-bound jet routine whose complete paid list plus recovery bill is smaller than the old Gaussian work, while preserving every required original helper endpoint.

For an actual proposed replacement, carry its full changed paid and productive profiles into the current caller and certify all three compiler guards at one common tested saving. The prior conditional κ = 0.0031234 hand-budget package is a separate complete source composition; this extraction alone supplies no additional numerical κ.

A black-box use of the SAT or scalar contraction bound is not a near-linear integer-multiplication algorithm. It remains a subexponential bound in Boolean variable/wire count, multiplied by a polynomial in input-description length, and the scalar contraction theorem returns a scalar ring value. A multiplier needs explicit encoding, all required outputs, operand bits, phase/precision and decode costs. The positive theorems above avoid making that unproved complexity transfer.

## 12 Assessment status and attribution

The source headline, complete algorithm and global runtime remain an author preprint claim. The examined local valuation/Hermite and weighted-count arguments have been re-proved here in their stated Gaussian form. The whole #SAT algorithm, every tensor-entry constructor, all degree/height inequalities, cited results and complexity simulations have not received a new independent end-to-end audit in this work. No computational test or Lean proof is claimed.

Preserve OpenAI's preprint attribution and its cited classical predecessors: polynomial and Hermite interpolation, Beigel–Tarui modular amplification, conditional expectation, Tanner/expander codes, finite-field arithmetic, weighted partition generating functions and the cited counting constructions. The Gaussian-valued presentation also builds on the project's existing Gaussian lattice and precision bookkeeping, exact phase/Clifford matching, scalar/source/caller work, and all inherited compiler and analytic notices. The contribution here is the explicit ramified Gaussian recovery theorem, its positive taper bill, exact unit/division implementation and precise transport contract. New explanatory text and proofs are Apache-2.0 with substantial OpenAI Codex assistance.
