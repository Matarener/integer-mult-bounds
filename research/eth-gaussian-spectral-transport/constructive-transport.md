# Constructive communication summaries and uniform descriptor transport

Dugongue, with substantial OpenAI Codex assistance. This note transports explicit mechanisms from OpenAI's preprint [The Exponential Time Hypothesis is False](https://github.com/openai/math/blob/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf), revised October 25, 2026. Its main ETH claim is not assumed as an accepted theorem here. The positive constructions below are proved directly and do not require calling its SAT algorithm.

The source mechanisms are small communication summaries, bounded coefficients rather than rank alone, valuation-weighted mode descriptions, and immutable creation-time semantics. Their use for a changed Gaussian provider requires its exact physical response and complete query/ordinary bill. This note does not turn a faster search for one fixed word into a κ improvement.

## 1 Exact communication summaries become an actual query program

Work in the source's declared scalar ring R, ordinarily R=Z[1/2] when only dyadic scalar words are admitted. Let K:A→B be one supplied native query between actual whole-field presentations A and B. Its positive Gaussian grade is q and its phase-aware input/output matching words are part of the supplied primitive. All source versions x_i live at A; all receiving fields y_j live at B. Original x_i and y_j are arbitrary independent inputs.

The prescribed response is

    x stays x,    y += M K x,

where K acts on every source payload and M is a matrix of scalar owner coefficients. A scalar matrix at a common chart commutes with the payload query. Suppose an explicit factorization M=L C through r rows has actual admitted scalar words for C and L.

### Theorem 1 A factored communication response has an r-query implementation

Initialize r owned buffers at A. Compute h=Cx while preserving every x_i. Apply K to each h row exactly once, using its actual owned-query and normalizer contract. At B add L times the queried bank into y, then clear all owned buffers and scratch at their actual exit charts. This emits the exact response with r grade-q query calls and no productive credit on a summary or its copy.

**Proof.** Linearity gives K(Cx)=C(Kx). The final addition is L C Kx=M Kx. Its source bank was only read. Each y retains its old arbitrary value plus its prescribed increment. All auxiliary fields are owned and return zero under their charged source contract. No independent input is identified with another, and no original y is erased. ∎

**Complete charge.** Add C's and L's scalar words, every buffer INIT/COPY/CLEAR, all K matchers, routing, descriptors and suspended-instance reserves. If the scalar synthesis from the companion paper-filter construction costs S_C(N), S_L(N) and scratch R_C,R_L on a payload of size N, the new ordinary charge includes both costs and the actual maximum simultaneously live scratch. These costs are not declared constant when their defining parameter grows.

The theorem applies to observational responses or shears. It does not silently replace an in-place MOVE by an overwritten independent field. If an in-place interface is required, its actual output installation and restoration must be separately implemented and counted.

### Theorem 2 Temporal summaries preserve actual source versions

In Theorem 1, each source occurrence may be sampled at its actual time into the corresponding C buffer entries. All buffers keep chart A until delivery. Suppose no receiving y field is read or otherwise modified between its first deferred update and the common delivery cut, apart from the updates being replaced. Then one late batch of K calls and L additions preserves the entire surrounding word.

**Proof.** Until delivery, only the y fields differ from the old execution. The unread-destination condition prevents that difference from affecting any future donor or control value. Hence each buffer samples precisely the old current source version at the old event. After the final sample, the buffer holds exactly its required row combination. Theorem 1 restores every y to its old complete value before its next read. All other state was unchanged. Induct over the prefix, sample events and suffix. ∎

The condition is a literal chronological contract, not a static information-rank statement. If a donor changes, its old occurrence is still sampled at its real time. Holding only a donor's bank name does not preserve its old version.

## 2 Obtain a dyadic delivery factor without a forbidden inverse

The preprint's layout condition says that an external response is invariant under the kernel of a measurement matrix. Over Q, this means its row lies in the measurement row space. The physical scalar alphabet may instead require a factorization over R=Z[1/2]. The following positive certificate handles that difference constructively.

### Theorem 3 A unit-section certificate constructs the delivery matrix

Suppose C has a supplied ordinary right section E, so C E=I_r. If M kills ker C over the ambient field, set L=M E. Then L C=M. If C,E,M have admitted R-valued scalar words, Theorem 1 is an actual R-valued program with this explicit L.

**Proof.** For every x, C(x−ECx)=0. Kernel annihilation gives Mx=MECx. Thus M=MEC=L C. Every executed map is one of the supplied finite words or their explicit composition; no source-prefix inverse is taken. ∎

### Theorem 4 A Smith certificate removes unnecessary field division

Let U and V be explicitly invertible matrices over R with

    U C V = D=diag(d1,...,ds,0,...),

in rectangular diagonal form with nonzero d_j. Suppose the first s columns of M V have entries d_j z_ij with z_ij in R, and all later columns are zero. Put Z_ij=z_ij for j<=s and zero for the other r columns, and put L=Z U. Then L C=M over R, even when the d_j are not units.

**Proof.** The stated divisibility witness says M V=Z D=Z U C V. Cancel the supplied invertible V on the right, obtaining M=Z U C. The runtime L contains the already supplied R-valued coefficients z_ij; it does not execute division by a nonunit d_j. ∎

This is a constructive module certificate, not just a field-rank certificate. In the source's dyadic ring an odd reciprocal need not be an admitted scalar primitive. The preprint often works in Z_(2), where odd denominators are invertible; these are different rings. Its modular inversion routine cannot simply be renamed an exact dyadic native instruction.

For the companion ordinary synthesis of f(W), include the literal integer dynamic-program word and its real field/movement bill. Integer coefficients of that word may be used in C or L without an odd runtime division. The matrix factorization or Smith data must still refer to the exact desired physical response, not only the filter's rank.

### Lemma 5 Coefficient size controls the real summary budget

If |x_i|<=B pointwise and the absolute row sums of C and L are at most D_C and D_L, then |Cx|<=D_C B pointwise. If K has actual maximum-norm bound N_K(N), its queried summaries have magnitude at most N_K(N)D_C B, and the increment to any receiver is at most D_L N_K(N)D_C B.

**Proof.** Apply the triangle inequality to each explicit row and then the actual K norm inequality. ∎

The fixed source bounds must cover every intermediate scalar synthesis value too. A one-row measurement with exponentially growing coefficients can require many bits even though its row count is one. This is why the preprint controls measurement coefficients as well as the number of measurements.

## 3 A positive two-query fusion under the current source model

Take two actual values u and v at chart A and a destination y at chart B. Let F be any explicitly synthesized ordinary linear map on an owned A-presented payload, with its actual finite scalar/permutation word, scratch and norm bounds. The desired two responses are

    y += K F(u),    y += K F(v).

Assume y is unread and unchanged between them except for these two responses.

### Theorem 6 One query computes the two-response sum

Initialize owned h at A, sample u at the first event and v at the second event by h+=u and h+=v, evaluate the supplied F on that owned sum, query K once, add the result to y at B, and clear h and F's work storage. This preserves all original source values and gives exactly y_old+K F(u)+K F(v). It uses one K call instead of two.

**Proof.** Before delivery h holds the actual sampled sum u+v. Linearity gives K F(u+v)=K F(u)+K F(v). The unread barrier proves that each sampled source is the same version as in the old word and that delayed delivery cannot affect any intervening state. All cleanup acts only on owned buffers. ∎

The ordinary filter F may be the companion f(W) primitive, but its dynamic program, coefficients, moves and scratch are paid. The old comparison must include two actual separately evaluated F responses; the new one includes one F evaluation plus its real acquisition and delivery operations. This is an exact new response primitive, not an assertion that every caller asks for that response.

**Concrete inherited instance.** In the PR5786 base of the accumulated-sum construction, the actual selected events are

    13104: ADD 146 <- 640, coefficient −1/2, chart 531;
    13110: ADD 146 <- 641, coefficient −1/2, chart 531.

The PR5802 changed presentation places destination 146 at chart 529 while the two donor versions remain at 531. The admitted owned conversion K=C_529 C_531^(-1) has rank one because the actual nested chart dimensions are eight and seven. With F=I and the common coefficient −1/2, Theorem 6 is the concrete two-update native-sum primitive at this site. Two separate rank-one delivery queries for that same response are replaced by one rank-one query on their owned sum, with all three arbitrary original values preserved.

The published PR5802 already includes that construction, its surrounding coframe changes and its full changed helper credits. It is a correctness and price example, not an extra saving to subtract again from PR5806. Any f(W)-enhanced use or different simultaneous response needs its own actual consumer identity and full changed bill.

## 4 Immutable descriptions make the construction uniform

The preprint's recursive tensors are represented by their creation data and creation precision. A retained description is reused at that original meaning, rather than repeatedly substituting old entry evaluators into new ones. The following are constructive compiler statements, independent of its ETH conclusion.

### Theorem 7 Creation-time representatives have consistent read semantics

For each created object record its precision p_c, fixed description D and immutable source-version references. Define its value at index x to be the canonical representative of Eval(D,x) at p_c. Every later higher-precision read returns that same representative embedded at the requested precision. Then every read of that stored version returns one and the same value, regardless of the number or precision of later reads.

**Proof.** The description, index, original references and p_c are unchanged. Their canonical evaluation is therefore the same finite value. A later read embeds that value instead of recomputing the old expression at a different precision. Induction over reads preserves the invariant. ∎

For modular objects this is the fixed residue representative in [0,2^p_c). For dyadic complex coordinates it is the fixed value returned by the declared rounding rule. Canonical lifting need not preserve addition or multiplication, so a compiler cannot replace this rule by a higher-precision re-evaluation and assume equality. The resulting approximation defect must be paid in the actual precision analysis.

### Theorem 8 A shared stored defect has one combined suffix image

Suppose one creation-time error e is read through exact linear maps S1,...,Sk into the SAME joint required output space, including every dirty-restoration and productive-helper obligation. For independent outputs compose each map with its direct-sum output embedding. Its total output effect is (sum_j S_j)e, bounded by ||sum_j S_j||*||e||. It need not be charged as k independent errors. A separately recomputed or rerounded value introduces a different error and requires its own term.

**Proof.** Every read carries the same e by Theorem 7. Distribute each exact linear output map and sum before applying the norm inequality. ∎

This permits a precise lifetime-aware error budget for shared query summaries. It neither treats errors as random nor removes any output obligation, including productive helpers.

### Theorem 9 Flat local descriptions avoid recursive evaluator multiplication

Suppose each created descriptor contains one kernel tag, its finite local parameters, its creation precision and immutable references. Assume each kernel's entry routine directly evaluates its own local formula with at most a declared number of original-data reads; it does not recursively evaluate a chain of older created entry routines. If the program makes Q_j entry requests to descriptor j, its total entry work is at most

    sum_j Q_j [E_j(N,p_c,j)+A_j(N)],

plus the explicit descriptor creation, interpreter navigation and routing work. E_j is the local kernel's real evaluation bound and A_j bounds its data/descriptor access. Owned working space is the maximum simultaneous local workspace plus all live descriptors, caller values and interpreter stack.

**Proof.** Execute each request through its kernel tag with the recorded local parameters. Charge the complete local evaluation and each declared read. The no-recursive-callback premise prevents multiplying that evaluation cost by an older entry evaluator. Keep immutable backing data until its last read. Allocate local temporary space for one request at a time and restore its owned slots. Add all live persistent values and the actual navigation stack. ∎

This is the useful closure property exhibited by the preprint's packet tensor descriptions. Merely storing an arbitrary recursive expression DAG does not establish it: many distinct ancestral entries may otherwise be evaluated. In a TM implementation A_j includes actual scans; on a word RAM it includes word/address fit and table construction. Neither memory model is given free random access by this theorem.

### Theorem 10 A streamed finite-word interpreter need not materialize the word

Let an explicit acyclic template grammar expand to L primitive events. Suppose a next-event iterator uses stack depth d, emits the exact next opcode/operands in P(d,log M) operations, and has no hidden old-source recomputation; M bounds its finite metadata. Then executing the expanded word costs its literal data-operation costs plus O(L P(d,log M)) interpreter work and O(d log M) iterator space, with all live caller data and descriptions counted separately.

**Proof.** Traverse the grammar depth first, retaining the current template and child index at each active level. Invoke the supplied next-event routine for each of the L events and immediately execute it. No event is omitted or executed twice. Sum iterator work; only the d active levels occupy iterator space. ∎

For fixed local words this is a constructive uniformity mechanism, not a new κ by itself. If a growing-family application claims an asymptotic gain, substitute its actual d,M,P and source scale into the final runtime. An unspecified polynomial overhead or an enormous fixed SAT search is not a logarithmic-saving theorem.

## 5 What this contributes to the source construction

The concrete output is an explicit shared-summary query compiler over the actual scalar ring, a temporal read/version rule, a fully priced two-query fusion, coefficient/magnitude bounds, and uniform creation-time/iterator constructions. The paper-inspired f(W) filters can plug into these interfaces only through their literal ordinary words and exact requested responses.

A complete κ consequence requires a changed word whose actual P,T,W invoice improves at the tested exponent and survives the same physical caller, independent-target, completion, compiler and precision conditions. The current PR5806 hybrid conditional κ=0.0031234 is a predecessor checkpoint. No additional paid query or productive credit is inferred here without an actual new response contract.

## Predecessor credit

Credit OpenAI's October 25, 2026 preprint and its stated measurement-separation, packet-mode and immutable-description methods, together with its cited algebraic/interpolation antecedents. The kernel factorization, Smith divisibility, linearity and streaming-interpreter arguments above are classical mathematics assembled for this physical source interface, not claimed as new general facts.

Retain Ali Romman's PR5802/5786/5774/5751, the PR5795/5796 and Joel Pulikkan/GamingPuzzled block lineage, flyingviper PR5718, Cinna Davis's SOURCE/controller work, Jacob Alan Sussman, zxv, Cao Yifan and all source native, phase, ownership, compiler, precision and BIT notices. This text uses literal source readings and informal proofs only. New prose is Apache-2.0.
