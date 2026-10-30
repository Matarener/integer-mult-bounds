# Causal mixed-precision delivery for the explicit Gaussian correction

Dugongue, with substantial OpenAI Codex assistance. This note gives a constructive temporal interface for the exact correction circuits in this package. Its contributions are source-version sampling, tagged precision, backward demand propagation, transposed delivery, and installation at actual P104 sites. All storage, coefficient, routing, restoration and ordinary-operation costs remain charged. No mathematical programme, numerical experiment, solver, source replay or Lean process was run.

## 1 The actual correction, with its physical width

Write π=1+i, N=2^n and A_n=([[i,1],[1,i]]/π) tensor-powered n times. The preceding Gaussian bridge in PR 5813 fixes integers 0≤R≤n and 0≤a≤n−R, the Newton interpolant

    g(j)=i^a Σ_(h=0..R) (i−1)^h binom(j−a,h),

and E={s:|s| outside [a,a+R]}. With H_E the literal unnormalized Walsh rows indexed by E, the exact identity is

    A_n x = g(W)x + 2^(−n) H_E^T diag(i^|s|−g(|s|)) H_E x.       (1)

The companion [correction-algorithm.md](correction-algorithm.md), C1–C4, supplies an explicit integral ordinary word for the second term, with a shared pruned Walsh tree, its literal transpose, coefficient words, modewise valuation and complete coordinate-incidence/precision account. The companion [consumer-construction.md](consumer-construction.md) gives an alternative exact integral triangular factorization. These are actual circuits; neither is an assumed cheap low-rank oracle.

The relevant n is the physical number of tensor positions. A rank-r child at lifted width m can have n=rm. It is not legitimate to replace this by the fixed nine-bit dimension describing P104 charts. Classical full Walsh processing and the ordinary Gaussian tensor algorithm remain competing exact routines. A finite-coordinate calculation is not an all-size exponent improvement.

## 2 Deferred delivery uses actual source versions

### D1 Exact causal acquisition and delivery

Suppose a response is y+=K Σ_j c_j x_j, with all sampled x_j at the same actual input chart. Its source occurrences are taken at prescribed chronological events. Assume y is not read or otherwise modified between its first deferred addition and delivery, except for the additions being replaced. Initialize an owned sum h at that input chart, execute h+=c_j x_j at the old event of each sample, then run the explicit bulk and exceptional correction on this one snapshot. Apply the exact native input/output matchers and global phase in their declared order, deliver to y before its first subsequent observation, and clear every owned work array. This produces the same whole-caller endpoint while preserving every arbitrary original donor and receiver.

**Proof.** Until delivery the changed execution differs only in y. Since nobody observes y, each sampled donor has its old current value even if that donor changed since a previous sample. After the last sample h is the prescribed sum of those actual versions. Equation (1) gives its exact native response. Matching, delivery and restoration make all state equal before the next observation. Owned cleanup never erases an arbitrary original input. Induct over the old prefix, sample events and suffix. ∎

The bank name of a donor is not its old value. Holding an immutable snapshot or sampling at the actual old event is essential. A COPY, source read in an ADD, frame-changing instruction, or restoration observation of y is an actual barrier. A net endpoint identity alone does not prove this causal premise.

### D2 Creation precision is part of a cached value's identity

Represent one physical cached coordinate by π^(−e)z, where e is a declared integer tag and z is an integral numerator stored modulo π^Q. It serves a read modulo π^p exactly when Q≥max(0,p+e), provided z denotes this same creation-time version. To serve a declared finite family of future reads, create the cache at

    Q=max_(future reads j) max(0,p_j+e),

or recompute explicitly when a later larger demand arrives. A later request does not upgrade a residue by choosing a higher-precision representative. Every recomputation, fresh rounding and live backing version is charged.

**Proof.** Two valid numerator representatives differ by π^Q times an integer. Their physical values differ by π^(Q−e), which is zero modulo π^p when Q−e≥p. If Q is smaller, adding π^Q gives a possible indistinguishable numerator whose physical outputs differ at the requested modulus. Taking the maximum gives simultaneous sufficiency. The assertion concerns the same stored version, so subsequent source mutation cannot silently replace its creation value. ∎

All full-output observations, productive-helper outputs and dirty restoration participate in this maximum. If exact integer recovery needs a larger final modulus than an intermediate display, substitute that full modulus first. Independent source values remain independent even if they share a frame and precision tag.

## 3 Backward valuation demand gives a complete ordinary compiler

### D3 Precision propagation through an explicit integral circuit

Let an explicit acyclic numerator circuit have Gaussian-integer edge coefficients and equations

    z_v = Σ_(u→v) b_(vu) z_u.

The list of all scalar words, outputs and numerator tags is supplied. Give each required output v a demand P_v=max(0,p_v+e_v). Process the circuit backwards, assigning each input of a node the demand

    P_u=max_(u→v) max(0,P_v−v_π(b_(vu))),                 (2)

and combine this with any independent observation of u by taking the maximum. Zero coefficients are omitted. Evaluate each node at its declared modulus using the actual integer scalar word. This computes every required physical output to its demanded modulus, with no runtime inverse of an odd scalar or of π.

**Proof.** If an input error is divisible by π^P_u, multiplication by b_(vu) makes it divisible by π^(P_u+v_π(b_(vu))) and hence by π^P_v. A finite sum of such errors still has this divisibility. Backward induction establishes the needed demands; forward induction establishes output correctness. Each node is evaluated using its supplied Gaussian-integer coefficients, so divisibility is used to discard unavailable low-significance information, never to invent digits. ∎

For several future consumers, include every consumer edge before computing these maxima. Fractional grids belong in the declared tags or in an explicitly increased common numerator; (2) is not applied as if a fractional coefficient were integral.

**Complete cost.** Charge the supplied Gaussian-integer word for every edge at the necessary operand precision, each actual input/output incidence, the actual memory movement, every initialized or cleared work cell, and the maximum simultaneous cached numerators and suspended caller state. If integer arithmetic at P digits costs M(P), substitute M at every emitted operation rather than replacing the whole circuit by its smallest output precision. The transpose can make formerly low-precision nodes high-precision; its demand propagation is recomputed.

### D4 Transposed delivery has a literal circuit and its own precision profile

An explicit gather circuit with L scalar additions/subtractions has an explicit transpose scatter with at most 2L adjoint additions, preserving arbitrary y by accumulation into a zero-owned output followed by y+=output. Multiplication by a supplied scalar transposes to multiplication by that SAME scalar, without complex conjugation. Apply D3 to this new circuit and to every receiver observation to determine its precision. Extra phases and signed-permutation matchers use their actual adjoints or inverses only when the desired matrix identity requires them.

**Proof.** Reverse a gather instruction z=u+v by accumulating the z-adjoint into both u and v. Reverse z=u−v by adding into u and subtracting from v. This is the matrix transpose identity on the nose. Reversing composition gives the complete transpose; all adjoints start at zero except the supplied leaf coefficients. The old y is untouched until its owned result is added. D3 now proves precision for this explicit new word. No Hermitian conjugation is introduced by a formal linear transpose. ∎

For the tail in (1), this delivers H_E^T diag(δ) H_E x, not an uncomputed abstract decoder. The entire joint required output is used; cancellation in one recipient cannot justify dropping a dirty/helper output elsewhere.

## 4 A mixed-precision triangular bank has an explicit temporal contract

The companion triangular construction factors

    C=[[i,1],[1,i]]=S diag(1,π²) T,
    S=[[i,0],[1,1]],    T=[[1,−i],[0,1]],
    A_n=π^(−n) S^(tensor n) diag(π^(2|u|)) T^(tensor n).    (3)

These identities follow by direct matrix multiplication and tensoring. No unknown change-of-basis map is assumed.

### D5 Coordinate tags implement (3) with unequal precision

Suppose integral x is required through A_n modulo π^p, and put P=p+n. After a T stage with processed index prefix u, the required integral numerator precision is max(0,P−2|u|). The final diagonal bank coordinate u has tag e_u=n−2|u| and numerator precision max(0,p+e_u). To merge one S pair whose tags are e and e−2, compute

    b_new=a+π² b,       a_new=i a,

and give both outputs tag e. The higher-tag numerator precision is max(0,p+e); the lower input is needed only to max(0,p+e−2). All these are explicit Gaussian-integer operations.

**Proof.** The T update is a←a−ib, with b unchanged. Its future coefficient for a processed one bit acquires π² from the diagonal, so (2) lowers that branch's required numerator precision by two. Iterate across bits. For the S merge, the represented physical values are π^(−e)a and π^(−e+2)b. Multiplication by S gives top π^(−e)ia and bottom π^(−e)(a+π²b), exactly the stated update. D3 gives the input precision requirements. Repeat to the final uniform tag n and divide only by this declared output grid, not by an unavailable integral numerator digit. ∎

The tag can be negative: that coordinate's value is already divisible by a positive power of π. If p+e≤0, its contribution vanishes at the requested modulus. It still has an actual declared grid; no negative-size bit string is allocated.

### D6 Persistent triangular measurements obey the same source-version rule

A bank h=T^(tensor n)x can be cached with the coordinate tags of D5. For a window of actual scalar operations at the SAME compatible physical presentation, update h by h+=c k when x+=c z and k=T^(tensor n)z, by h*=c when x*=c, and by owned zeroing when x is initialized to zero. All needed coordinate precisions are assigned from the complete future window using D2–D3. At an actual read, finish (3) by its explicit diagonal and S word; preserve the bank or pay to reconstruct it according to later liveness. This supplies a real cached-response construction, including every bank update and delivery.

**Proof.** T^(tensor n) is linear. The asserted bank updates therefore preserve the invariant at each event. D2 fixes each version and prevents unsupported precision upgrades. D3 assigns sufficient numerator demands. Equation (3) proves the delivered response. Induct over the chronological window. Owned banks and caller values remain live until their actual last reads, then their actual cleanup is executed. ∎

Dyadic scalar updates such as c=1/2 need explicit grid alignment: multiplying by 1/2 lowers Gaussian valuation by two. Put the bank and source on a declared common numerator grid and raise the source creation demand by this debt before using D3. A previously cached lower-precision numerator cannot be upgraded for free. After such edits D5 is used on the integral numerator, with the common source tag added to all output demands.

A changed coframe needs its actual map on this bank. Unless an explicit cheap word for that map is given, compute a new bank from the actual source or charge the actual change-of-frame word. The whole P104 word is not asserted to have one shared triangular basis. A nested native rank alone is not a compatibility proof. Independent source fields need independent initial bank gathers unless a supplied source equality combines them.

## 5 The actual native normalization is the Gaussian tensor

### D7 Exact source-kernel installation, including its phase

In the source Clifford compiler, the positive C gate along a coordinate swap X is

    C_native=((1+i)/2)I+((1−i)/2)X.

Since i/π=(1+i)/2 and 1/π=(1−i)/2, this is exactly [[i,1],[1,i]]/π=A_1. Its inverse is the coefficient conjugate, so it has the same Gaussian-valuation precision rules. The source fourier routine composes these coordinate C gates. Its lower_child routine emits right monomial, then the rank-r coordinate fourier, then left monomial, with the absolute global phase retained. Thus replacing that central primitive by (1) or (3), tensor-lifted at the actual width and retaining every spectator, is an exact source-equal replacement of the native recipe. Every monomial, phase, spectator route and output normalization remains part of the executed word.

**Proof.** The displayed coefficient identities identify the source's actual two-coordinate action, without a rank analogy. Tensoring the coordinate identities gives its central axis product. Substitution inside the supplied two-sided recipe therefore preserves that recipe's exact action on every input column and its global phase. Conjugating all coefficients gives the inverse case. The source's all-positive-width extension is a retained source premise, not a new kernel audit performed here. ∎

D7 is a matrix substitution. An actual in-place MOVE also needs an explicit charged installation adapter, as specified in [assembly-and-invoice.md](assembly-and-invoice.md). A source-preserving routine producing an owned output is not by itself the in-place instruction. Include its actual swap/routing, source and output tags, any inverse cleanup, owned-erasure contract and full precision before applying whole-word substitution.

The literal source inspected is the canonical main vendor clifford_exact.py and its separately implemented native_verify.py. In particular, this identification does not claim that all canonical frames have one common Walsh eigenbasis: canonical_frame conjugates a partial axis product by a permutation followed by a quadratic diagonal chirp. Its actual chirps are retained.

### D8 A common Fourier gauge has a complete boundary invoice

Suppose a named temporal patch has an explicit common physical Walsh transform F=H_n such that EACH internal native instruction U has the supplied exact diagonal form FUF^(−1), and all internal scalar operations act on its actual compatible presentations. Keep every inside field as h=Fx. At each entry create this bank; scalar ADD/COPY/SCALE acts on the banks; internal U becomes its explicit diagonal phase. For each mixed outside-to-inside sample, import F applied to that actual outside source version. For each inside-to-outside delivery, export F^(−1) of that actual increment. Decode every surviving inside field at its final exit, including every independent helper and arbitrary dirty field. Owned zero initialization and zero retirement need no Gaussian transform, but their actual scrub/clear and storage are charged.

This is a whole-caller equal construction. If there are b actual charged transform boundaries of width d and the removed native grades are r_1,...,r_k, its exact paid-moment change, before any OTHER changed recursive calls, is

    ΔP_t=b d^t−Σ_j r_j^t,

and its productive inventory is unchanged when every original autonomous physical endpoint is restored. If both ΔP_(1−C)<0 and ΔP_(1−C+u)≤0, its first and higher normalized paid moments improve or stay within their old bounds at the same test parameters; with unchanged targets the completion ratio stays fixed. This is sufficient only together with the full new ordinary, precision, routing, lifetime and compiler budgets.

**Proof.** h=Fx is preserved by scalar linearity, and the supplied conjugation identity proves each internal phase instruction. The mixed import/export formulas are ordinary substitutions through F and F^(−1), with actual source snapshots and recipients preserved as in D1. At every required exit the decoded state equals the original, including arbitrary dirty values, so the same independent targets retain their old credit. Charge every actual boundary and subtract only the native instructions truly replaced. The moment statements now follow directly with the unchanged productive denominators. ∎

A boundary is an actual version read, not merely a distinct role label. Several consumers can share a decoded or encoded cache only while its creation version and adequate precision remain unchanged under D2–D3. If a source mutates, either update its exact cache or perform a new paid conversion. A full patch counts the actual lifetimes of these versions, every COPY and each relevant restoration read.

The transform boundaries themselves are paid Gaussian queries, not free Walsh changes of coordinates. Put D=diag(i^|x|). Direct multiplication gives

    H_n=(1−i)^n D A_n D,       H_n^(−1)=2^(−n)H_n.

Thus each such full-width transform has one central Gaussian query with explicit phase/scalar words, actual movement and output-grid normalization. Charge the extra denominator debt of the inverse and the coefficient/height growth of both sides; propagate all future demands using D3. The formula does not bypass the source matching cost.

This gauge theorem is a positive exact compiler for a supplied common-diagonal patch. No claim is made that the entire current P104 frame collection satisfies its premise or that a particular favorable boundary invoice has been found. Enlarging a patch adds actual crossing sources, receivers and targets, which must be counted before claiming a gain.

## 6 The actual P104 sites, productive credit and the whole bill

The retained PR 5802 source has three owned accumulated-sum conversions, on destinations 146, 173 and 151. Their input/output chart pairs are 531→529, 559→549 and 543→541. Each pair has dimensions eight and seven. The phase-aware source compiler provides each native query's actual central Gaussian primitive, ordinary matching words, exact global phase and every-positive-tensor-width contract. D7 identifies its central C-axis with the actual normalized Gaussian tensor; installation retains the exact matching, spectator and normalization identities, not a rank analogy.

For the first site, the PR 5786 common word samples donor 640 at event 13104 and donor 641 at event 13110, each with coefficient −1/2 in chart 531. Destination 146 is retargeted to chart 529. The released source checks its literal no-read/no-write barrier. Its owned sum therefore satisfies D1, and both circuit families give a source-equal implementation of its remaining Gaussian kernel after the actual recipe's matchers. An inverse-direction Gaussian kernel uses the conjugate coefficients in (1) and (3), with the same valuation rules; all phases and normalization-grid changes stay explicit.

The other two existing sums use their own released source events and coefficients. Their fixed sum acquisition and one-query delivery are already credited in PR 5802 and retained by PR 5806. Nothing here subtracts that saving a second time. These are literal locations for the new explicit kernel implementation, not a new proof that the original two deliveries fuse.

Every original public input, independent helper target, dirty endpoint and outer caller obligation stays required. Replacing an owned query produces no new productive target. If an altered caller changes a public helper endpoint, debit its old target and prove its actual new autonomous endpoint before crediting any new target. A scalar cache is correlated data, not another independent Gaussian job.

For each actual replacement occurrence at physical width n, the complete new ordinary bill contains:

- the old causal samples, the sum buffer and all native input/output matching words;
- either the complete bulk plus exceptional-tail circuit, or the entire triangular circuit;
- all scalar synthesis, coordinate incidences, scans or RAM accesses at their actual precision and bit-height;
- every live cached version, deferred recipient, caller field, interpreter descriptor and work array;
- all initialization, numerator alignment, delivery, input preservation, owned cleanup and restoration.

The old owned-field cap is not automatically preserved. Simultaneous arrays are charged by their actual size and lifetime, and the caller's idle, thin-query and normalizer charges remain. A global proposal sums over all 18 local invocations and every affected occurrence. Ordinary work must fit the actual recursive allowance; zero Gaussian subqueries does not make an N log N ordinary transform a free primitive.

The positive result is a complete causal, mixed-precision implementation interface for explicit correction and triangular words, together with actual caller sites where the source version and no-read hypotheses hold. No new whole-caller paid/productive histogram, admissible ordinary budget or κ is established by this note. The current construction can still have substantial ordinary work even when few exceptional modes survive.

## Credit

Credit OpenAI's pinned October 25, 2026 preprint for spectral localisation, valuation-weighted modes and immutable descriptions; PR 5813 for the Gaussian source specialization; Ali Romman for PR 5786/5802 and the retained native matcher, chronology and ownership framework; PR 5806 and its predecessor chain for the combined caller. Walsh transposition, Gaussian elimination and valuation propagation are classical techniques. The new contribution here is their explicit temporal, precision and source-caller assembly, not a claim of worldwide novelty for those component facts. All original source attribution and Apache-2.0 notices remain in force.
