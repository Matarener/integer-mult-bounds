# Integral swap localisation and filtered Gaussian response packets

Dugongue, with substantial OpenAI Codex assistance. This note extracts two explicit finite constructions from the pinned OpenAI preprint: an integer implementation of its low-degree partial-swap operator, and a precision-and-jet filtered mode compiler. It also proves an exact first-jet property of six real P104 updates. These results do not assume that the preprint's complete ETH conclusion has been accepted, and they do not supply an unpriced SAT or tensor-contraction oracle.

The source is `openai/math` at `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a`, especially the partial-swap construction in `main_full_version.tex` and the Cauchy mode expansion in `quantitative-contraction.tex`. The ramified Gaussian precision conversion is supplied separately in this package. Source reading is not a new Lean or computational verification.

## 1 The paper's partial-swap polynomial needs no odd scalar division

Let Pi_1,...,Pi_q be commuting ordinary involutions. Each has an explicit finite signed-permutation word on the actual payload. Work in characteristic zero, put

    E_i=(I-Pi_i)/2, W=sum_i E_i, V=product_i Pi_i.

For integers a>=0 and R>=1 define the interpolant

    f(X)=(-1)^a sum_(h=0..R-1) (-2)^h binom(X-a,h).

It satisfies f(j)=(-1)^j at every integer j in [a,a+R-1]. This is the explicit Newton form of the alternating-value polynomial used in the paper.

**Lemma 1.** The operator f(W), despite the factorial denominators in its scalar polynomial notation, is an INTEGER linear combination of products of the ordinary Pi_i.

**Proof.** The E_i are commuting idempotents. On a joint eigenspace their sum W has eigenvalue j, the number of negative Pi eigenvalues. Consequently

    binom(W,j)=sum_(|S|=j) product_(i in S) E_i.

This equality can also be checked with the explicit dyadic joint-sector projectors, whose sum is I. The polynomial identity

    binom(X-a,h)=sum_(j=0..h) binom(-a,h-j)binom(X,j)

then gives

    f(W)=sum_(j=0..R-1) c_j B_j,
    B_j=sum_(|S|=j) product_(i in S)(I-Pi_i),
    c_j=(-1)^a sum_(h=j..R-1)
                   (-1)^h 2^(h-j) binom(-a,h-j).

Every c_j is an integer, because generalized binomial coefficients at an integer are integers. Every B_j is an integer permutation polynomial. QED.

In particular there is no hidden division by an odd factor of h!, no unsupported inverse scalar, and no extra two-adic denominator debt in THIS operator implementation. The scalar polynomial f itself may have rational monomial coefficients; the cancellation occurs after evaluating it on the stated commuting involutions.

**Lemma 2.** The response y += V f(W)x has an explicit ordinary word using at most R-1 persistent elementary-sum fields and a constant number of evaluation work fields. Its dynamic programme uses at most q(R-1) updates of the form

    F_j += (I-Pi_i)F_(j-1).

**Proof.** Use F_0=x, keep x unchanged, and initialize F_j=0 for positive j<R. For each i update j in descending order. The elementary-symmetric recurrence gives the required B_j x. An update d += (I-Pi)z needs no third field: execute d+=z, apply Pi to d, execute d-=z, then apply Pi to d again. It returns d_old+z-Pi z while preserving z. Form sum c_j F_j in an owned accumulator by integer doubling-and-ADD routines, apply V, add the result to y, and clear every owned field. All scrubs, additions, permutation passes and coefficient words have positive ordinary cost. QED.

The explicit coefficient and norm bound

    Gamma=sum_(j<R) |c_j| 2^j binom(q,j)

bounds the payload operator norm when each Pi_i has norm one. Prefix bounds follow from the same recurrence, or from products of the emitted instruction norms. Gamma can be large; an actual native installation must include its bit heights, routing, guards and suspended storage. A query-free ordinary implementation does not make its work free in a multiplication model.

**Lemma 3.** M=V f(W) fixes every joint eigenspace whose negative-sign count lies in [a,a+R-1]. Thus I-M factors through the direct sum of the remaining eigenspaces.

**Proof.** On the count-j eigenspace, V acts by (-1)^j and f(W) by f(j). Their product is one on the stated interval. Use the explicit joint-sector projectors to collect the other components. This is an explicit factorization, not an unknown low-rank measurement oracle. QED.

This is a producer/consumer-localisation tool. It is not itself a cheaper implementation of an unrestricted Gaussian Q: replacing an identity wire by an ordinary low-defect operator still requires accounting for its exceptional response and the actual later consumer.

## 2 Precision and Taylor degree jointly filter modes

Let O be a discrete valuation ring with uniformizer pi. In the Gaussian adaptation use pi=1+i and O=Z[i] localized at the prime (pi). Then v_pi(n)=2v_2(n) for nonzero rational integers n. This ramified ring is not the paper's unramified extension O with i silently inserted.

Fix precision P and Taylor order J. Work in

    A=(O/(pi^P))[z]/(z^J).

Suppose a finite grouped multilinear contraction has row forms consisting of local terms plus modes. Each mode Z has one source group and one target group, and has the explicit form

    z a_Z(z) L_Z(X),
    v_pi(a_Z)>=w_Z>0,

where L_Z depends only on source-group variables, while its coefficient belongs to the target-group row form. All coefficients and local factors are integral. The same statement permits an additional fixed truncated coefficient variable, with its storage and arithmetic charged.

**Theorem 4.** The contraction modulo (pi^P,z^J) is exactly a sum over mode exponent tuples beta satisfying BOTH

    sum_Z w_Z beta_Z<P,
    sum_Z beta_Z<J.

For each such beta its coefficient factors into the product of the source/target group contractions obtained by coefficient extraction and by substituting the actual L_Z powers.

**Proof.** Expand the finite product of affine row factors. Every occurrence of mode Z contributes a factor z and pi-adic weight at least w_Z. The coefficient of Z^beta is therefore divisible by pi^(sum w_Z beta_Z) and by z^(sum beta_Z). A term outside either strict bound is zero in A. For every remaining monomial, each mode's coefficient lies in one target group and its L_Z power depends only on one source group. Collecting these factors by group and summing each group's disjoint Boolean variables proves the exact product formula. QED.

This is a one-step finite identity. It neither assumes the preprint's full recursive running time nor treats a child contraction as a free native query. To claim a whole recursive speedup one must sum every child's actual cost, every retained mode, jet arithmetic, interpolation and description cost, including any growth of coefficient-algebra dimension along recursion.

**Corollary 5.** For J=2 only the zero-mode case and one occurrence of a single mode survive. If there are K eligible modes, at most K+1 group-response cases are required. For J=1 only the local case remains.

**Proof.** The second strict bound permits total mode multiplicity zero or one. The first bound can remove further modes. QED.

The work saving is exact for a first jet; it is not a claim that all needed Hermite data have order at most two. The preprint's higher-order recovery and its precision losses must be supplied separately for each actual output.

## 3 The Cauchy tile gives actual integral modes

Use the paper's L=2^a packet grid S={-L,...,L-1}, alpha=2^(a+1) and

    C(T)=product_(t in S)(T-t),
    W_xy(T)=C(T)/[C'(0)(T-(y-x))].

This is a polynomial, since its displayed denominator factor cancels one numerator factor. At T=0 it is the identity wire map. In local coordinates T=t+alpha z, the paper's elementary valuation factor cancellation gives integral coefficients.

For a tile y=y_0+2^(i+1)j, let u_x=T-y_0+x and assume the crossing condition v_2(u_x)<=i, where i=v_2(t). Geometric expansion gives terms

    [C(T)/(C'(0)u_x)] [2^(i+1)/u_x]^b j^b.

The source linear form is the explicit integer sum sum_j j^b X_j. Its coefficient has rational-integer two-adic valuation at least b+1, hence Gaussian pi-adic valuation at least 2(b+1). For a crossing tile the factor C(t+alpha z) also has z as a factor, while the relevant omitted denominator has nonzero constant term; thus each crossing mode has at least one Taylor factor z. Theorem 4 therefore applies with Gaussian weights 2(b+1), AFTER any coefficient normalizations have been debited.

The literal coefficient recipe first removes the known powers of two from each scalar factor and then inverts its odd part. Odd denominators are units in O. A division by 2^d costs 2d powers of pi precision and is not a unit operation. The endpoint-lowering theorem in this package gives the required increased modulus and net mode weights when normalizers introduce those denominators.

### A concrete local factorisation with fewer assignment cases

Take L=2, a=1, t=1 and z=1, so T=5. Direct integer multiplication in the displayed polynomial gives

    C(T)/C'(0)=-420,
    W(5)=[[-84,-105],[-70,-84]].

Modulo pi^4, which is the ideal (4), the two crossing diagonal entries vanish. The two off-diagonal local entries become 3 and 2. For arbitrary unary factors A_0(Y_0),A_1(Y_1),B_0(X_0),B_1(X_1), put l_0(u)=1-u and l_1(u)=u. The four-bit contraction is exactly

    [sum_(Y0,X1) A_0(Y0)B_1(X1)l_Y0(3X1)]
    *[sum_(Y1,X0) A_1(Y1)B_0(X0)l_Y1(2X0)]

modulo pi^4. Each bracket has four assignments, replacing the original sixteen-assignment joint sum by eight local assignment cases and a multiplication. The two inputs and all factor values are arbitrary elements of the stated coefficient ring.

This is an explicit finite algebraic saving for an actual kernel from the preprint. It is not a Gaussian provider or a complete Hermite reconstruction at precision four. A larger requested output precision may retain the crossing modes again, and a global reconstruction must pay the taper and normalization precision. None of those costs is suppressed by this example.

## 4 An actual P104 packet has only first-order interaction

The common PR 5786 word at `6b936acd68a7e0f9062037900f0fe9bc4b6fdd25` contains the following six additions, which PR 5802 later groups into three sum acquisitions. The indices below are in that COMMON word:

| Index | Destination | Source | Coefficient | Frame |
|---:|---:|---:|---:|---:|
| 13104 | 146 | 640 | -1/2 | 531 |
| 13110 | 146 | 641 | -1/2 | 531 |
| 13287 | 151 | 630 | -2 | 543 |
| 13293 | 151 | 628 | -2 | 543 |
| 13475 | 173 | 613 | 1 | 559 |
| 13481 | 173 | 611 | 1 | 559 |

Give these six coefficients independent formal multipliers t_1,...,t_6. All other instructions remain fixed.

**Theorem 6.** The full source endpoint is affine in these six parameters, with no mixed products or second-order terms.

**Proof.** Use the FULL event predicate: an event touches receiver r if its destination is r, or if it is ADD/COPY with source r. From the first selected event for r through event 13481, the literal records satisfying this predicate are exactly that receiver's two selected additions. Thus there is no intervening MOVE, SCALE, INIT, CLEAR, COPY or other ADD on an already affected receiver, and no cross-field read of it. In the larger whole interval, the only other source reads of these labels are 13278 on role 151 and 13468 on role 173, both before that receiver's first selected addition and hence parameter-free. ADD/COPY are the only cross-field value-reading instructions in this fixed alphabet; MOVE is a one-field fixed linear coframe change. All selected source rows therefore stay parameter-independent. Each parameter is added once to its unread receiver, so the window endpoint is M_0+sum_i t_i M_i. Its fixed linear prefix and suffix preserve this degree bound. This applies to all original columns without inverting a singular prefix. QED.

The first-jet interpretation is exact: modulo the ideal of parameter degree two there is no loss at all for this packet. A symbolic mode method needs only the constant response and six linear responses, rather than 64 formal subset cases. This is an actual source-bound construction/verification saving, not an extra paid Gaussian saving on top of PR 5802's already credited three acquisitions.

A future coefficient or summary proposal can use the linear equations

    sum_i (t_i-1)M_i=0

to preserve the complete endpoint, with source matching, chronology and productive targets checked independently. This is a concrete use of the paper's coefficient/jet viewpoint and the linked library's linear invariant-synthesis precedent. No uncomputed dependence between the M_i is assumed. If they are independent, the displayed ansatz has no nontrivial coefficient edit.

## 5 The exact recursive bill for a transported mode algorithm

A complete candidate must provide every deformed local tensor, coefficient word, mode weight, actual Hermite jet order and increased precision. At a node t let B_t be its allowed mode tuples, and let P_(t,beta,g) be the paid Gaussian child list for group g's ACTUAL response routine. Let P_interpolation contain all other Gaussian requests needed by coefficient conversion, endpoint matching or reconstruction. Then the complete replacement paid list is

    P_new=P_interpolation
          +sum_t sum_(beta in B_t) sum_g P_(t,beta,g).

Only original independent final Gaussian jobs retain productive credit. Modes, polynomial coefficients, duplicated tensor factors and owned measurement banks are correlated computations, so they create no new productive targets by themselves.

For a fixed tested C, a sufficient first-moment improvement over a specified old complete program is

    sum_(r in P_old) r^(1-C)
      >sum_(r in P_new) r^(1-C),

with all target changes separately included if the endpoint contract changes. Both higher-moment and completion guards, ordinary word cost, precision, source frames, target autonomy and all original-field endpoints remain part of the same whole witness. The ring/jet method gives an exact construction rule; it does not turn a local contraction into a funded multiplication algorithm automatically.

Our present pure-mathematical results are Lemmas 1–3, Theorem 4 and its low-jet corollary, the explicit Cauchy example, and Theorem 6 on the real six-update packet. No additional Gaussian query has been removed from the current whole caller by this note. In particular it does not evade PR 5808's immutable-channel repair bound by relabelling a lower-rank call: this transport changes precision and multi-query contracts and must pay their full costs.

## Precedents and credit

The pinned OpenAI preprint supplies the partial-swap spectral construction, Cauchy deformation, valuation-weighted modes and tapered Hermite strategy. Its full contraction/ETH claim is a separate audit question. The integral Newton-permutation implementation, joint valuation/Taylor-degree filtering, explicit local kernel factorisation and source-bound P104 first-jet observation are the additional constructions proved here.

Inspected linked-tree precedents are `Mathproof.Abstraction.LinearInvariantSynthesis`, `Mathproof.SymplecticTI`, `Mathproof.LibraryBridges.Claude.TIModuleIso20260905`, `Mathproof.LinearAlgebra.SchurBlockElimination`, `Mathproof.Meta.Problem18P36ClockedRAMSemantics20261004`, and `Mathproof.Meta.Problem18Lax13BitCost20261007`. They motivate explicit coefficient constraints, support-aware transport, complete bounded semantics and real word costs. Their presence is not a new kernel audit or a claimed all-size RAM improvement.

Retain Ali Romman's PR 5786/5774/5802, Joel Pulikkan/GamingPuzzled's released block work, flyingviper, Cinna Davis, Cao Yifan, DaysSky, Nick Petalas, Ryanson Jonathan, Jacob Alan Sussman, zxv and every source matching, ownership, precision, BIT and analytic notice. The earlier noncommuting matrix-unit atlas supplies a different algebraic query interface; a fixed single-Q faithful-algebra lower bound is not defeated by interpolation inside that same interface. New text is Apache-2.0 with substantial OpenAI Codex assistance. No mathematical programme, solver, replay or Lean check was run for this note.
