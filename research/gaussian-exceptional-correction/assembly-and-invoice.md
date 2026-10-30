# Complete native assembly and a sharp precision invoice

The exceptional Gaussian correction now has a finite algorithm for every input. The pruned spectral construction and the integral Smith construction both preserve the full response, with actual coefficient, grid, source-read and cleanup costs. The additional result here is a uniform whole-transform addition-precision invoice and its exact source-recipe assembly. The invoice improves on fixed-modulus arithmetic; it does not establish a higher multiplication κ.

## A1 Exact tensor lifting of the native recipe

Let π=1+i, C=[[i,1],[1,i]], A_n=π^(-n)C^(tensor n). In the pinned native compiler the coordinate C gate is

    ((1+i)/2) I + ((1-i)/2) X = A_1.

Its lower_child recipe is a literal right monomial, a rank-r coordinate product of these gates, then a left monomial. Monomials here are actual signed permutations, translations and coordinate phases in {1,i,-1,-i}; the recipe retains the absolute scalar phase.

**Theorem A1 (all-width matrix assembly).** Suppose a supplied exact one-column recipe has the matrix identity U=M_L(A_r tensor I)M_R, including its global phase. The literal f-column tensor lift has the exact identity

    U^(tensor f)
      =M_L^(tensor f) P^(-1)
          (A_(rf) tensor I) P M_R^(tensor f),

where P is the explicit permutation regrouping active and spectator coordinates. Any global phase i^b in the one-column recipe becomes i^(bf) under this lift. Replacing A_(rf) by either complete circuit in the companion notes preserves the entire lifted matrix.

**Proof.** Tensor the supplied one-column identity f times. The active factor is (A_r)^(tensor f), which is A_(rf) after regrouping its rf two-coordinate axes. The remaining axes are identity factors. A tensor product of monomial matrices is still the explicit corresponding monomial. Scalar phases multiply, yielding i^(bf). Substitution of an equal active matrix preserves the product. QED.

This proves an all-width matrix identity for the literal replicated definition. Identifying a physical caller's layout, phase convention and actual implementation with this lift remains part of its source contract. P is not a free TM movement operation. Its actual scans, permutation and storage must be counted. The supplied source's finite recipe identities are retained facts; no new exact phase replay or kernel audit was run.

An inverse recipe uses the conjugate central matrix, since A_n is symmetric unitary and A_n^(-1)=conjugate(A_n). Conjugating the Smith or spectral word preserves every Gaussian valuation and modulus. Its monomial matching and phase order are the actual inverse recipe's, not an arbitrary reversal of one displayed scalar coefficient.

## A2 A complete replacement for one actual native request

Write n=rf, N=2^n, and let B be the actual number of spectator slices. Let an arbitrary input have declared grid π^(-d)Z[i], with d>=0, and require output modulo π^p. Apply the actual right matcher and coordinate permutation, clear the input denominator, and set p'=p+d. The active integer-input circuit must deliver A_n at precision p'. After its left matcher and spectator routing, restore the source grid π^(-d). Original inputs are read and remain unchanged; all other arrays are initialized owned work. Add to an arbitrary original receiver only after the complete matched output exists, then perform the declared owned cleanup.

For the spectral route use

    G_B=π^R g(W),       G_T=π^n A_n-π^(n-R)G_B,

and the exact assembly

    π^n A_n x = π^(n-R)G_Bx + G_Tx.

The bulk numerator needs modulus π^(p'+R). The explicit exceptional algorithm uses Q=p'+2n-R-1 working digits and delivers G_T modulo π^(p'+n). Its final exact quotient is implemented by at most one π division, an ordinary binary shift and a unit phase. It is not Nm successive full-precision divisions.

For the Smith route use the exact factorization

    C=S diag(1,π²) T,
    S=[[i,0],[1,1]],       T=[[1,-i],[0,1]],

with the propagated moduli in consumer-construction.md. It computes ALL of A_n x. There is no exceptional bank left to assume, no input parity restriction and no omitted helper output.

**Theorem A2 (arbitrary-input native substitution).** Each of these finite routines, with the specified source matchers and grid, gives the same native output modulo π^p on every spectator slice, preserves every arbitrary original input and can accumulate into an arbitrary receiver. Their costs are the sum of their actual ordinary operations and storage, multiplied by B, plus all matching, routing, source/receiver traffic, initialization and cleanup.

**Proof.** The companion spectral identity or Smith identity gives the central response at precision p'. Unit-phase monomials and permutations preserve valuation of errors. Dividing the declared input scale π^d takes an error in π^(p+d) to one in π^p. Addition retains the receiver's old arbitrary value. All temporary changes are confined to the explicitly owned arrays, whose clearing or charged reversal restores their storage. Tensor lifting and untouched spectator factors establish the complete native response. QED.

A compatible cache can be reused only at the same actual input version and sufficient creation precision, as proved in shared-tail-delivery.md. A mode, cache or reused numerator is correlated data and receives no extra productive credit. No favorable cache availability is assumed in A2.

### A2a Public MOVE has an explicit in-place adapter

A source-preserving routine that returns Kx in owned work is not by itself the in-place instruction x ← Kx. The following exact adapter closes that interface. It applies to the actual invertible native matrix K and to finitely represented inputs.

First compute h=Kx exactly in an owned array while retaining x. Swap the complete physical payloads and their declared representation headers, so x now holds Kx and owned h holds the old x. Run the exact inverse source-preserving routine on the new x and subtract K^(-1)x from h. The owned h is now identically zero. Clean up all other owned work under the declared erasure contract. This leaves x at its required new frame and every other original field equal to its old value.

**Proof.** After the swap the pair is (Kx_old,x_old). Invertibility gives K^(-1)(Kx_old)=x_old exactly, so subtraction zeros only the owned old-value array. The original field holds its prescribed image throughout the final cleanup. Swapping means actual payload/header movement, not a free frame relabeling. The inverse uses its own reversed matchers, source grid and phase. QED.

This adapter pays BOTH kernel algorithms, all matching in both directions, the full physical swap, its two owned buffers, grid alignment and cleanup. It does not claim the original nNP comparison for the whole adapter; A3 compares the central forward arithmetic only. A host with a separately proved direct in-place word can use that word with its own full bill.

Exactness here is obtained constructively. If the integral input numerator on grid π^(-d) has coordinate magnitudes below 2^b, the native output has a numerator on grid π^(-d-n) with magnitudes below 2^(b+n), since the raw tensor has N unit-phase terms per row and the monomial matchers preserve coordinate magnitude. Taking a raw recovery modulus π^(2q), for example q>=b+d+n+2, permits unique signed decoding of that numerator. The inverse has the same explicit finite-height calculation on its supplied input grid. Reading the bit heights and performing both decodings are charged. The proven exact numerator circuits therefore supply the required exact forward and inverse routines without an oracle.

If only rounded modular values are computed, K^(-1) of the rounded result need not be the old x. Such a routine cannot use this adapter to assert exact zero cleanup. It must retain the missing information or give a separate permitted approximation/erasure proof. No rounded owned field is silently declared zero here.

## A3 A sharp invoice for both Smith passes

Let P=p+n with n>=1 and p>=0. Precision p=0 still denotes a fractional quotient; it does not say that a normalized child response is absent. Only zero RAW modulus permits branch omission. Define J_m to be a fair binomial variable with m trials. The exact addition-operand precision mass of both Smith passes is

    Q_add=N sum_(m=0)^(n-1) E[(P-2J_m)_+].              (1)

This follows from the literal stage count: each T or S stage at processed depth m contains 2^(n-m-1) pairs with binomially distributed prefix or suffix weights. Adding both passes gives the N factor in (1). No probability is used as an input-distribution assumption; the expectation is just compact notation for a finite binomial sum over ALL coordinate labels.

**Theorem A3 (uniform full-pass precision invoice).** For every n>=1 and p>=0,

    N[np+n(n+1)/2] <= Q_add
      <= N[np+n(n+1)/2+n exp(-p²/(2n))]
      <= N[np+n(n+1)/2+n].                            (2)

If p>=n-2, the first bound is exact: the excess is zero. This is a whole-transform addition bill, not merely the small storage mass of the final diagonal bank.

**Proof.** Set Y_m=m-2J_m and a_m=P-m. The law of Y_m is symmetric with mean zero, and a_m=p+n-m>0. The scalar identity x_+=x+(-x)_+ and symmetry give

    E[(a_m+Y_m)_+]=a_m+E[(Y_m-a_m)_+].

For m>0 its moment generating function satisfies

    E exp(tY_m)=cosh(t)^m<=exp(mt²/2).

Indeed log(cosh t)<=t²/2 follows by integrating tanh t<=t for t>=0; symmetry handles negative t. Markov's inequality optimized at t=u/m therefore gives

    Pr[Y_m>u]<=exp(-u²/(2m))<=exp(-u²/(2n)),  u>=0.

At m=0 the excess is identically zero. By the nonnegative tail integral,

    E[(Y_m-a_m)_+]
      <=integral_(a_m)^infinity exp(-u²/(2n)) du.

Put s=n-m, so the lower endpoints are p+s for s=1,...,n. Swap the finite sum and integral. For a given u>=p, the number of s with p+s<=u is at most u-p. Hence the total excess is at most

    integral_p^infinity (u-p) exp(-u²/(2n)) du
      <=integral_p^infinity u exp(-u²/(2n)) du
      =n exp(-p²/(2n)).

The excess is nonnegative. Finally,

    sum_(m=0)^(n-1) a_m
       =n(p+n)-n(n-1)/2=np+n(n+1)/2,

which proves (2). If p>=n-2, P>=2(n-1)>=2m for every m in the sum. There is then no negative part at all, so the excess is zero. QED.

**Corollary A3a (a strict concrete ordinary improvement).** A literal raw C tensor at common precision P has addition-operand mass nNP. The Smith word's mass is smaller by at least

    N n(n-3)/2

for n>3. At p=n its exact ratio to that fixed-modulus mass is

    (3n+1)/(4n).

At fixed p and growing n the ratio tends to one half.

**Proof.** Subtract the last upper bound in (2) from nN(p+n). At p=n the excess vanishes and direct substitution gives the ratio. For fixed p, both the lower and upper ratios in (2) tend to one half. QED.

This is a proved precision-work saving for an exact arbitrary-input source primitive. It is not a measured runtime ratio. Signed exchanges, shifts, phase application, copies, permutation/routing, grid representation and clearing remain actual operations. A complete bit upper bound is

    O(Q_add+NP+Nn)

for the declared indexed arithmetic implementation, plus its actual layout traffic. On a fixed-tape machine include the real axis-routing implementation; on a word RAM include operand-word and index-word costs. The theorem supplies no model change by renaming one primitive operation a unit step.

## A4 A constructive choice between the correction circuits

For a spectral interval [a,a+R] with 0<=R<n, let t be the number of exceptional Walsh labels, A(T) its explicit prefix-tree incidence and B_e the stated scalar coefficient bit bound. Let

    B_c=2+ceil(log2(R+1))+R+R ceil(log2(a+R+1)).

A complete arithmetic upper bound for bulk plus spectral correction is

    O( N(nR+R B_c+1)(p'+R+1)
       +(p'+2n-R)[A(T)+N+t B_e]
       +N(p'+n)+coefficient_preparation ).             (3)

The first term is the actual ordinary bulk numerator word. The second is the complete pruned analysis, multiplier and transpose word, including its normalization precision. The third includes assembly and numerator quotient/traffic; every coefficient-preparation and routing cost remains explicit. The coefficient-valuation-aware subtree profile can reduce the second term, but only with proved valuations.

The Smith alternative has bound (2) with p', its own copies and phases, and its complete route bill. A literal raw tensor at uniform precision remains a third algorithm. All three are finite exact circuits. Choosing the least of their SUPPLIED structural upper bounds gives a uniform upper bound equal to their minimum, plus a charged selector and preparation; it does not require looking at the unknown input values or assuming an unavailable summary.

The pruned spectral construction replaces a previous Nt dense measurement/scatter incidence by O(N log(t+1)), or by its sharper low/high-weight prefix bound. The Smith alternative removes the Walsh-projector denominator entirely. These are distinct positive corrections of the old construction, not two savings that may be blindly added together.

## A5 Whole-word precision and exact recovery

Local modular outputs must meet the demands of their ACTUAL continuation. For a finite word of linear updates, include all public endpoints, every productive helper, each required COPY/source observation and dirty restoration in the demanded observation list. Propagate precision backwards as in shared-tail-delivery.md. An ordinary dyadic denominator 2^d costs 2d Gaussian units. A normalized n-axis native factor has entry valuation at least -n; unit-phase monomials add no valuation debt.

A simple sufficient, conservative schedule for an output precision p_out is to add the sum of all later denominator debts along every relevant path before truncating a local result. The exact DAG maximum can be smaller; the conservative total is finite and explicit. The same source value must retain a consistent creation precision and grid at all its later reads.

**Theorem A5 (finite whole-word endpoint compilation).** Use A2 for source-preserving update requests and the fully charged exact A2a adapter for in-place native MOVEs, at its sufficient finite-height recovery precision. Substitute any named finite set of such occurrences, using the backwards schedule for every remaining modular operation. The resulting ordinary word agrees with the original execution on every listed observation modulo its demanded precision, satisfies every original-field obligation, and pays each new array, scalar word, source version, inverse installation and cleanup. If the final bounded Gaussian-integer numerators are demanded modulo π^(2q), with 2^q larger than twice their coordinate bound, centered decoding gives the exact original numerators and hence the exact declared fractional outputs.

**Proof.** Every replacement's local error lies in the stated π-power. Each later edge multiplies it by a coefficient whose valuation debt was already subtracted backwards. Its contribution to any observation is therefore in the required output ideal. Finite sums preserve divisibility, giving all observations simultaneously. The source-preserving owned-word construction leaves its original inputs intact. At a MOVE, A2a gives the exact specified original-field image and zeros its owned old-value array by the exact inverse identity. All other original fields retain their required original-execution values. The equality of ideals (π^(2q))=(2^q) gives the ordinary coordinate residues; two possible coordinates within the declared interval cannot differ by a nonzero multiple of 2^q. Divide only the final declared output grid. QED.

This theorem gives an actual whole-word modular and exact endpoint constructor. It does not establish that its cost fits the stronger time allowance of a particular multiplication recurrence.

## A6 The precise κ test and the result obtained

At candidate saving C, use the ACTUAL full paid histogram P_r, independent productive histogram T_r and all additional charges E(C). The signed first moment is

    F(C)=sum_r T_r r^(1-C)-sum_r P_r r^(1-C)-E(C).

Every new recursive request belongs in P; every removed independent helper output is debited from T. Ordinary work is charged to the relevant full compiler allowance rather than counted as zero because a transform has no Gaussian subquery. The higher moment, completion, stock, precision/tape, BIT and outer tests stay required at the SAME candidate saving.

For the actual replacement in this package there is no missing exceptional algebraic operation: A2-A5 emit it and its exact output. The unresolved gain is the complete ALL-SIZE time invoice. With n=rf and p'=Theta(f), the Smith literal addition mass in (2) is Theta(2^(rf) f²), before spectators. An indexed input field contains Theta(2^(rf) f) bits. Thus this particular ordinary implementation has an N_bits log N_bits arithmetic scale, with a strictly improved leading addition-precision coefficient. That does not supply the required N_bits (log N_bits)^(1-C) saving for positive C. This is a comparison of the emitted implementation, not a lower bound against another algorithm.

The spectral implementation (3) may be attractive for a shared or small exceptional response, but its nR bulk, full source reads, true Q precision and complete scatter are present. A small diagonal bank or residual rank cannot replace those terms. The current pending PR 5811 κ=.00312418633064 is not beaten by a proved whole invoice here.

## Open next questions

1. **Amortize an actual repeated bank.** Find several source-equal responses with a shared immutable input version in the current word, then use one pruned or triangular analysis and charge every version update and full delivery. First step: exact events and a complete new word, beyond the four already released accumulated updates.
2. **A compatible commuting patch.** The exact common-gauge compiler charges every actual entry, exit, source import and recipient export. Find a real connected patch whose complete paid and ordinary bills win. Generic canonical charts do not have one common diagonalizer; their chirps and independent endpoints must be retained.
3. **A faster active-axis representation.** The exact whole-pass invoice shows where the growing-width work remains. Seek a concrete structured input/output representation that reduces the NUMBER of ordinary passes while still delivering every independent target, rather than only pruning diagonal channels. Its encoder and decoder must be emitted and charged.

The mathematical advances established here are complete arbitrary-input exceptional delivery, exact current native matching, a uniform sharp whole-transform precision invoice and source-preserving whole-word recovery. A new numerical κ would require an additional funded construction, and none is asserted.

New text is Apache-2.0 with substantial OpenAI Codex assistance. The source Gaussian/native/caller, spectral-transport and preprint attributions are retained in SOURCES.md and NOTICES.md. Smith form, Walsh transposition, binomial concentration and finite error propagation are classical; the present contribution is their explicit source-bound construction and complete invoice.

