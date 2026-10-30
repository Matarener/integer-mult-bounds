# Pure mathematics for native transform assembly

Dugongue, with substantial OpenAI Codex assistance. Informal mathematics only. This note contains no experiments, numerical certificates, execution scripts or Lean formalization. The proofs below are mathematical arguments, not claims of kernel verification. Classical circuit transposition, tensor norm identities, recurrence methods, Fourier convolution and carrying retain their classical status. The contribution is their explicit composition into sufficient native cost and recovery contracts.

The intended use is to connect an actually constructed structured transform to an integer-multiplication recurrence. There is no new numerical κ in this note. In particular, the symbolic assembly theorems do not supply a missing fast transform merely by naming its desired cost.

## Source precedents actually inspected

The linked library supplied the following source precedents. No source was executed or compiled.

* `FastPoly/Cost/Circuit.lean` and `FastPoly/Cost/MultiplicationProgram.lean`, thomasahle/fast-polynomials, revision `09a36b0e7a6c153462bd43b91d4a3bb7ac886bef`. The former represents a DAG with a genuine shared `bind`; the latter fixes circuit syntax before quantifying over inputs. Its counts charge nonscalar multiplications and additions, while constants, scalar multiplication and wires are free in that algebraic accounting. Theorems 1–3 below therefore add their native costs explicitly.
* `TCSlib/Programs/WordRAM/Basic.lean` and `TCSlib/Programs/WordRAM/Steps.lean`, Shilun-Allan-Li/tcslib, revision `3a211c0cd7725e077637fff97931909731a3f1f4`. Their retained Anthropic formal-math/AFM26 lineage is acknowledged. The ISA has addition, subtraction, multiplication, indirect loads/stores, negative branches and halting; it does not provide division, shifts, masks or free arbitrary constants. `steps_straight`, `effect_add`, `effect_mul` and the framing definitions motivate the instruction-level hypotheses in Theorem 1. They are precedents, not a proof that an arbitrary real-arithmetic circuit fits those words.
* `Mpfx/Rounding/Ulp.lean`, bksaiki/mpfx-lean, revision `8bd80452927ae9234fc378c07a00f2962e1e5b6f`. `nearest_eq_of_close` and `nearest_eq_of_close'` supply the strict half-step sufficient recovery principle. Theorem 6 spells out the integer-convolution specialization and carrying argument.
* `CatCryptCore/Crypto/Lattice/CyclicConvolutionGeneric.lean` and `CatCryptCore/Crypto/Lattice/NTTFullInversionGeneric.lean`, spitters/CatCrypt-core, revision `dc39071735465240b54b43db9b98335d66660d48`. `dft_cyclicConv` and `idft_dft` are the exact Fourier/convolution precedents used in Theorem 7.

The shared lexical DAG/library query for `MultiplicationProgram` returned no indexed hits, although direct inspection of the linked source succeeded. This is an index-coverage limitation. No completeness or project-wide novelty follows from that query.

## Definitions

All vector norms in Theorems 4–6 are maximum norms, and matrix norms are their induced norms. Thus `||A||∞` is the maximum absolute row sum. A circuit is fixed independently of its data. Preparation can depend on the public dimension, prescribed target precision and fixed operator, but cannot depend on the particular right-hand side unless its cost is charged for that right-hand side.

A native cost counts arithmetic, coefficient construction, loads, stores, initialization, control, output copying and halting. A claim about algebraic operation count alone will be named as such. A Word RAM has signed W-bit cells and must use only the stated instruction set; integer intermediates interpreted as exact integers must fit in the signed range.

## Theorem 1. A uniform integer DAG has a fully charged native realization

Let a fixed straight-line integer DAG have n input cells, m output selections, G arithmetic vertices, and H distinct integer constants. Each arithmetic vertex is an addition, subtraction or multiplication of previous values. Suppose all constants and all integer results, including products, have absolute value below `2^(W−2)`, and all used addresses and loop counters fit in signed W-bit words. Let `U` be the cost of a uniform generator that writes the DAG descriptors and its constants. Then the DAG can be evaluated, its input preserved, its outputs copied to owned output cells, and every owned non-output cell cleared, in

`O(U + G + n + m + H W)`

native instructions, with `O(G + n + m + H)` owned cells. It preserves every exterior cell. If constant synthesis is already included in U, the `H W` term need not be counted twice.

**Proof.** Assign a separate value cell to each vertex, which avoids any assumption about an optimal register allocation. Reserve disjoint scratch, descriptor, coefficient and output regions. A fixed finite interpreter reads each operation tag and its two predecessor addresses, loads the operands into scratch cells, executes the corresponding arithmetic instruction, and stores the result in its assigned cell. Every descriptor occupies a bounded number of words and every interpreter path has bounded length, so each vertex costs O(1) instructions including control. The range hypothesis ensures that modular word addition, subtraction and multiplication agree with the intended signed integer result.

Construct zero by subtracting a scratch cell from itself. Construct one with the literal-one instruction. A constant of at most W−2 magnitude bits can be built from its binary digits by repeated doubling and, for each one bit, addition of one. Negate at the end if necessary. Every intermediate stays no larger than its final nonnegative magnitude, so this uses O(W) instructions per constant without a shift, division or free literal. The generator's own cost and production of the digits are included in U; the theorem does not assume a free uniform circuit family.

Initialization and clearing visit the owned regions and use one zeroing operation plus constant overhead per cell. Copy the m selected values before clearing internal values. Inputs are read but never overwritten. The interpreter only writes its assigned owned regions, which proves exterior preservation. Add the stated costs. ∎

**Use.** This is a sufficient bridge from an actual integer DAG to the native model. FastPoly's uncharged scalar operations must first be expanded into actual multiplications and constant constructions. A real or rational circuit requires a separate finite-word realization; Theorem 1 does not silently provide one.

## Theorem 2. Linear transposition with sharing and an explicit size bound

Let a linear circuit over a commutative ring compute `A x` using G vertices of the form `z = αu + βv`, with n inputs and m outputs, where zero coefficients and repeated predecessors are allowed. Then an explicit reverse circuit computes `Aᵀ y` with O(G + n + m) scalar multiplications and additions, and O(G + n + m) stored ring elements.

If the ring is the integers, all coefficients have absolute value at most B, all output seeds have absolute value at most Y, and `B₀ = max(1,B)`, every intermediate of the reverse construction has absolute value at most

`m max(1,Y) (1 + 2B₀)^(G+1)`.

Consequently it has a native realization by Theorem 1 whenever this conservative bound and all products fit the chosen words. A sharper separate bound can replace it.

**Proof.** Give every forward node an adjoint cell, initially zero. Add each output seed to the cell for the selected forward output. Process the forward vertices in reverse topological order. At a vertex `z = αu + βv`, add `α z*` to `u*` and `β z*` to `v*`. If u and v coincide, do both additions. Each vertex uses at most two scalar multiplications and two additions. Every node is visited once, so shared forward values do not cause the reverse circuit to duplicate a whole upstream subgraph.

For correctness, view the formal bilinear pairing between adjoints and forward values. Replacing `z* z` by `z*(αu+βv)` preserves the pairing exactly and removes the last forward vertex. After all replacements, the pairing is `yᵀ A x = (Aᵀ y)ᵀ x`. Therefore the final input adjoints equal `Aᵀ y`, coefficientwise, over every commutative ring.

For the integer bound, let L be the sum of absolute values of all currently live adjoints. Initially `L ≤ mY`. Processing one vertex removes its value z* and adds at most `2B₀ |z*|` elsewhere, so L increases by at most a factor `1+2B₀`. The individual products are bounded by `B₀ L`; absorbing one extra factor into the displayed bound covers both products and partial sums. This gives the claim. ∎

**Use.** This theorem provides the transpose rather than assuming an inverse or adjoint oracle. Its range bound also explains exactly when an algebraic transpose can be used in the same word width. It does not claim that transposition preserves precision for an ill-conditioned factorization.

## Theorem 3. Input-independent preparation is shared across independent fibers

Suppose an explicitly specified linear map A has preparation cost S, prepared storage K, and a complete application procedure of cost C and working storage V for one right-hand side. Assume preparation depends only on A and public size/precision parameters. Then applying A to R arbitrary, mutually independent right-hand sides costs

`S + R C`,

uses `K + V` working storage when right-hand sides and outputs are streamed, and produces exactly the same outputs as R separately prepared applications. If all outputs must remain simultaneously resident, their storage must be added.

**Proof.** Execute the preparation once and retain its immutable result. Apply the given complete procedure to each right-hand side in order, reusing its private working region after its stated cleanup. By its all-input correctness, the application produces A applied to that right-hand side, irrespective of the other right-hand sides. The same immutable preparation is therefore valid each time. Add the costs and take the maximum simultaneous working storage. ∎

This applies, for example, to a fixed elimination factorization, a fixed convolution kernel or fixed polynomial-evaluation nodes. It does not permit reuse of a data-dependent residual, a rounded quotient of the current input, or an output that later computations have changed. Preparation must include its actual constants and finite-precision requirements.

## Theorem 4. Complete rectangular tensor-axis accounting

Let `A_i` map vectors of length `s_i` to length `t_i`, with `1 ≤ s_i ≤ t_i`, for `i=1,…,D`. Let each fixed map have preparation cost S_i and complete per-fiber application cost C_i, including coefficient access, gather, scatter and cleanup. Put `T = ∏ t_i`. The tensor product `A_D ⊗ ⋯ ⊗ A_1` has an explicit axis-by-axis realization of cost at most

`Σ_i S_i + T Σ_i (C_i/t_i)`.

It uses at most two T-entry data buffers plus the prepared data and one application's scratch. In exact arithmetic the induced maximum norm satisfies

`||A_D ⊗ ⋯ ⊗ A_1||∞ = ∏_i ||A_i||∞`.

**Proof.** Before axis i, earlier axes have lengths t_j and later axes still have lengths s_j. The number of length-s_i fibers is therefore

`R_i = (∏_{j<i} t_j)(∏_{j>i} s_j)`.

Since every `s_j ≤ t_j`, `R_i ≤ T/t_i`. Prepare each map once, and use Theorem 3 on its R_i fibers. Summing gives the cost formula. A source buffer and destination buffer suffice; all intermediate array sizes are at most T. Any implementation that treats gather/scatter as free must add them before using C_i.

For the norm identity, a row of the tensor product is indexed by a tuple of rows. Its absolute row sum is the product of the absolute row sums of those rows, by distributivity of finite sums and `|ab|=|a||b|`. Every factor attains its maximum because there are finitely many rows. Taking the maximum therefore yields exactly the product of the individual maxima. ∎

**Dominant-cost corollary.** Let p be the master logarithmic width, `D=O(p^ε)` and `T=O(n p^(−λ))`. If the complete application bounds satisfy `C_i=O(t_i p^β)` uniformly and total preparation is `O(n p^(−λ+β+ε))`, then the complete tensor application costs

`O(n p^(−λ+β+ε))`.

This is a mathematical conversion of an already proved application bound into an array bound. A reduction of β by a fixed positive amount gives the same fixed-power saving for this assembly, provided every displayed premise still holds. The corollary does not supply a method with a desired β, and it becomes a full integer-multiplication statement only after all other caller and recovery terms satisfy the same bound.

## Theorem 5. A product of nearly contractive stages has additive guard bits

Let exact stages satisfy `x_i = A_i x_(i−1)`, for i from 1 to D. Let their implemented outputs satisfy

`x̃_i = A_i x̃_(i−1) + e_i`, with `||e_i||∞ ≤ ε_i`,

and assume `||A_i||∞ ≤ 1+η_i`, where every η_i is nonnegative. Then

`||x̃_D−x_D||∞ ≤ exp(Σ_i η_i) (||x̃_0−x_0||∞ + Σ_i ε_i)`.

In particular, if `Ση_i ≤ c log p`, initial data are exact, and each local error is at most `2^(−B)`, it is sufficient for target error at most `2^(−P)` to choose

`B ≥ P + ceil(c log₂ p) + ceil(log₂ D)`.

For strict target error, add one further guard bit.

**Proof.** Subtract exact and implemented recurrences. Repeated substitution gives

`x̃_D−x_D = A_D⋯A_1(x̃_0−x_0) + Σ_i A_D⋯A_(i+1)e_i`.

Take norms, apply submultiplicativity, and bound every relevant product of `1+η_j` by `exp(Ση_j)` using `1+u≤exp(u)`. This proves the first inequality. Under the additional assumptions it is at most `p^c D 2^(−B)`, and the stated bit choice gives the second claim. ∎

**Scope.** The local error bounds must include coefficient generation and the internal arithmetic of each stage. A bounded norm of the final composite matrix alone does not establish them. The theorem is useful when a new factorization proves small norm products throughout its actual execution, including both orientations required by recovery.

## Theorem 6. Strict coefficient error gives exact integer multiplication

Let `B≥2` be an integer base and

`a = Σ_{i=0}^{m−1} a_i B^i`, `b = Σ_{j=0}^{r−1} b_j B^j`,

where `0≤a_i,b_j<B`. Let `c_k = Σ_{i+j=k} a_i b_j`, taking missing coefficients as zero. Suppose a mathematical approximate transform produces real numbers c̃_k with `|c̃_k−c_k|<1/2` for every coefficient. Then nearest-integer rounding recovers every c_k uniquely, and ordinary carry propagation reconstructs exactly ab.

Moreover, with `h=min(m,r)`, every c_k is at most `h(B−1)^2`, and the incoming carry is at most `h(B−1)`. Thus every quantity entering a carry division is at most `h B(B−1)`.

**Proof.** Every c_k is an integer. Any different integer is at distance at least 1 from c_k, hence at distance greater than 1/2 from c̃_k by the triangle inequality. Therefore c_k is the unique nearest integer. This is the strict half-lattice-step principle also represented by the inspected Mpfx declarations.

Set carry q_0=0 and let `u_k=c_k+q_k`, `d_k=u_k mod B`, `q_(k+1)=floor(u_k/B)`. Then `u_k=d_k+Bq_(k+1)`. Induction yields

`Σ_{j<k} c_j B^j = Σ_{j<k} d_j B^j + q_k B^k`.

After all ordinary coefficients have been processed, continue with c_k=0 until the carry vanishes. The identity then gives the base-B representation of `Σc_k B^k=ab`.

There are at most h contributing digit products per coefficient, proving its bound. If `q_k≤h(B−1)`, then `u_k≤h(B−1)^2+h(B−1)=hB(B−1)`, so `q_(k+1)≤h(B−1)`. The initial carry satisfies the bound; induction completes the proof. ∎

**Native-model scope.** This theorem proves exact recovery and a magnitude bound. Division by B must be charged in a model without division or shifts, including the inspected minimal tcslib ISA. It is not automatically one instruction there. An implementation with a proved division procedure, or a stated extended ISA, can combine that procedure's cost with this theorem.

## Theorem 7. Zero padding and exact Fourier inversion give a complete coefficient contract

Let a field K contain a primitive L-th root ω, with `L ≠ 0` in K. Let two coefficient sequences have lengths m and r, with `L ≥ m+r−1`, and pad them by zero to length L. Define the forward transform by

`F(x)_k = Σ_j x_j ω^(jk)`

and the inverse by

`F⁻¹(X)_j = L^(−1) Σ_k X_k ω^(−jk)`.

Then inverse-transforming the pointwise product of the two forward transforms returns exactly the ordinary polynomial product coefficients, padded to length L. If K is the prime field of characteristic q and all desired integer coefficients lie in `[0,q)`, taking their standard representatives recovers the integer coefficients exactly.

**Proof.** Expand the transformed cyclic convolution. Reindex its inner sum by the cyclic additive bijection and use `ω^L=1`. The result is the pointwise product of the transforms. For inversion, expand the double sum; the inner sum of powers is L when its two indices agree, and zero otherwise. The primitive-root hypothesis gives this orthogonality and the nonzero-L hypothesis permits normalization by `L^(−1)`. These are the precise source precedents `dft_cyclicConv` and `idft_dft`.

In a padded convolution, every nonzero product has indices with sum between zero and `m+r−2<L`. Consequently no such sum wraps around modulo L. The cyclic convolution equals the ordinary product in every output coordinate. Finally, reduction modulo q is injective on `[0,q)`, so each representative identifies its unique integer coefficient. ∎

This is a sufficient algebraic endpoint. It does not construct a modulus family, primitive roots or a faster native transform, and supplies no asymptotic runtime by itself. Those are separate constructive inputs rather than consequences of source-library correctness.

## Theorem 8. A strict recursive moment yields a uniform saved logarithmic power

Let `0<r_j<1` and `a_j≥0` be fixed, and let F be a nonnegative normalized cost defined for `p≥p_min>0`. Suppose F is bounded on the base interval below some threshold p_0, and above that threshold satisfies

`F(p) ≤ Σ_j a_j F(r_j p) + B p^(−γ)`,

whenever a child enters the base interval it is charged by that base bound. If κ is nonnegative, `γ≥κ`, and

`q = Σ_j a_j r_j^(−κ) < 1`,

then `F(p)=O(p^(−κ))` uniformly for all sufficiently large p.

**Proof.** Choose A so that `F(u)≤A u^(−κ)` on all base arguments encountered and

`A(1−q) ≥ B p_0^(κ−γ)`.

This is possible because the base arguments lie in a fixed interval bounded away from zero: the smallest child ratio is positive. Let ρ be the largest child ratio, which is strictly below one. Induct over multiplicative bands whose upper endpoints are successive powers of `ρ^(−1)`. For any p in the next band, all recursive arguments lie in earlier bands. Thus

`F(p) ≤ A p^(−κ) Σ_j a_j r_j^(−κ) + B p^(−γ)`

`≤ [Aq+Bp_0^(κ−γ)] p^(−κ) ≤ A p^(−κ)`.

The induction covers every finite p and proves the estimate. ∎

The toll B must include all preparation, native memory work, rounding and recovery assigned to that recursive call. The a_j must count actually supplied child services with the correct independent output contracts. A favorable formal expression with unpaid children is not an instance of the theorem.

## Theorem 9. Coupled service types admit a positive matrix-moment assembly

Consider finitely many actual service types, with normalized nonnegative costs F_a. Suppose there are fixed nonnegative coefficients c_abj and shrink ratios `0<r_abj<1` such that every service has an explicit recursive construction satisfying

`F_a(p) ≤ Σ_(b,j) c_abj F_b(r_abj p) + B_a p^(−γ)`.

Base costs have the same boundedness property as in Theorem 8. Define the nonnegative moment matrix

`M(κ)_ab = Σ_j c_abj r_abj^(−κ)`.

If there is a vector v with every entry strictly positive and a number q<1 such that `M(κ)v≤qv`, and `γ≥κ`, then simultaneously

`F_a(p)=O(v_a p^(−κ))`

for every service type a.

**Proof.** Define `G_a=F_a/v_a`. Substitute the recursive inequality and multiply each child by `v_b/v_a`. The sum of weighted κ-moments in row a is at most q. Choose A to dominate all normalized base costs and all row toll requirements

`A(1−q) ≥ max_a (B_a/v_a) p_0^(κ−γ)`.

Use the same multiplicative-band induction as in Theorem 8, taking the largest ratio across all types. Its induction hypothesis holds simultaneously for every G_b. Each recursive row is then at most `Aq p^(−κ)` plus its toll, hence at most `A p^(−κ)`. Multiply back by v_a. ∎

**Constructive two-type corollary.** Suppose `M=[[a,b],[c,d]]`, where `a,d<1`, `b,c>0`, and

`bc<(1−a)(1−d)`.

Choose any positive t strictly between `c/(1−d)` and `(1−a)/b`; the interval is nonempty by the displayed inequality. For `v=(1,t)`, both inequalities `a+bt<1` and `c+dt<t` hold. Their two positive relative margins have a positive minimum, yielding a q<1 and hence Theorem 9.

**Research use.** A genuinely coupled native construction can be analyzed before flattening every service to a common worst standalone price. The vector v gives explicit exchange weights. This is a sufficient theorem for actual recursive constructors with actually retained outputs; it does not grant useful output credit to an interface that has not been decoded. No such new coupled construction is proved in this note, and no numerical κ is inferred from the corollary alone.


For the present research program, possible type labels include normalized geometric evaluation, polynomial coefficient convolution, and consumption of an explicitly coupled Gaussian interface. The algebraic existence of these maps does not itself provide any entry of M. An entry is justified only by a specified recursive constructor with its paid independent outputs. In particular, the finite-bond carry tensor in the companion algebraic note is an exact encoding; it is not already a fast dense contraction service. The matrix theorem can compose a future cheap consumer with a genuinely constructed convolution procedure, but counts neither as constructed here.
## Theorem 10. A chain of normalized geometric reciprocal blocks needs only linear master precision

For each i, let `0<x_(i,0)<⋯<x_(i,g_i−1)=X_i` and suppose consecutive roots satisfy `x_(i,j+1)/x_(i,j)≥exp(h_i)`, with h_i positive. Normalize `r_(i,j)=x_(i,j)/X_i`, define

`E_i(z)=∏_j(1−r_(i,j)z)`,

and let `R_i` be lower-triangular convolution by the first `L_i+1` coefficients of `1/E_i(z)`. Then

`||R_i||∞ ≤ (L_i+1) exp(2/h_i)`.

Consider any compatible sequence of these blocks, with zero-padding or coordinate selections between them; such padding and selection have maximum norm at most one. If every implemented block contributes maximum-norm error at most `2^(−B)`, the input is exact, and there are D blocks, it is sufficient for final error strictly below `2^(−P)` to take

`B ≥ P + ceil(log₂ D) + Σ_i ceil(log₂(L_i+1)) + ceil((2/ln 2)Σ_i h_i^(−1)) + 1`.

If the master parameter p satisfies `P=O(p)`, `Σlog₂(L_i+1)=O(p)`, `D=O(p^ε)` for a fixed `ε<1`, and every `h_i^(−1)=O(log p)`, the required B is O(p). Inputs of magnitude at most `2^(C p)` remain bounded by `2^(C' p)` throughout the exact block chain, for a suitable fixed C'. Thus these particular normalized reciprocal blocks have a sufficient O(p)-bit magnitude and error budget for the entire chain.

**Proof.** Put `q_i=exp(−h_i)`. Relabel the normalized roots from largest to smallest. Their j-th member is at most `q_i^j` for j from zero to `g_i−1`. The coefficient of degree k in the reciprocal is a complete homogeneous sum of nonnegative monomials in these roots. Its value is no greater than the same sum at `1,q_i,…,q_i^(g_i−1)`. Choose multiplicities of the positive-index roots; the multiplicity of the root 1 is then forced whenever their total is at most k. Dropping this restriction only increases the sum, so every reciprocal coefficient is at most

`∏_(j≥1)(1−q_i^j)^(−1)`.

The logarithm of this convergent positive product is

`Σ_(m≥1) 1/[m(exp(h_i m)−1)] ≤ h_i^(−1) Σ_(m≥1) m^(−2) ≤ 2/h_i`.

Here `exp(u)−1≥u`, and `Σ m^(−2)≤2` follows by bounding the tail from m=2 by the integral of x^(−2) from 1 to infinity. A row of R_i contains at most `L_i+1` nonnegative coefficients, proving its norm bound.

Substitute the exact recurrence for the error, as in Theorem 5. Every suffix product is at most the full product of these norm bounds, since each bound is at least one. Therefore final error is at most

`D 2^(−B) ∏_i(L_i+1) exp(2Σ_i h_i^(−1))`.

The stated B gives strict target error. Under the asymptotic hypotheses, `D log p=O(p^ε log p)=O(p)`, so all guard terms are O(p). The same product bound applied to the exact input proves the magnitude statement. ∎

**Exact contribution.** The reciprocal coefficients and truncations are the normalized geometric-annihilator construction developed in the companion algebraic-transform note; the proof above makes the precision consequence self-contained. It establishes neither a fast way to apply the fixed-kernel convolution nor stability of converting a global Gaussian caller into and out of this scaled coefficient convention. Those two costs are not charged as zero. The theorem applies to the normalized blocks actually defined here, rather than to an unproved Gaussian wrapper.
## Theorem 11. The run inverse assembles over the whole tensor with O(p)-bit precision

Consider a family of D square periodic inverse axes on an array of volume `V=∏_(i=1)^D S_i`. For each axis use exactly the periodic kernel N_i, Beatty-run construction, boundary Schur system and two-block-inverse recovery of analysis theorem A11. In particular, write `ρ_i=1+θ_i=T_i/S_i`, `q_(i,j)=floor(ρ_i j+1/2)`, `β_(i,j)=ρ_i j−q_(i,j)`, and

`(N_i)_(u,v)=Σ_(k∈Z) exp(−a_i[(ρ_i(v+kS_i)−q_(i,u))²−β_(i,v+kS_i)²])`.

Assume the constants in the following bounds are uniform across axes:

* `d=Θ(p^(1/4))`, `D=Θ(d)`, `θ_i=Θ(1/d)` and `a_i=Θ(d sqrt(p))`;
* `log(S_i+1)=O(p^(3/4))`, and each T_i and S_i is an integer with `S_i<T_i≤2S_i`;
* the real parameter a_i has a uniform polynomial-in-p procedure for producing every required O(p)-bit approximation; in particular the source choice a_i = π times a prescribed polynomially bounded integer square has this property by the elementary arctangent-series construction in A11;
* the requested final absolute error is `2^(−P)` with `0≤P=O(p)`, and the original array has maximum norm at most `X=exp(O(p))`.

Use the extended arithmetic Word RAM of A11.9: its words contain a sufficiently large constant multiple of p bits, its bounded-word arithmetic includes integer division and specified fixed-point rescaling shifts, and raw products fit before rescaling. Then for all sufficiently large p the tensor inverse

`N_D^(−1) ⊗ ⋯ ⊗ N_1^(−1)`

has a constructive approximation with final maximum-norm error strictly below `2^(−P)`, total application cost

`O(V p^(1/4) log p)`,

and one input-independent preparation of `2^(o(p))` operations and words. Preparation is performed once per distinct axis/policy, and all its coefficient generation and boundary factors are counted. If additionally `log V=Θ(p)`, preparation is `V^(o(1))` and is asymptotically smaller than the displayed application cost. The statement concerns these exact periodic inverse kernels and their tensor product; it does not assert the other Gaussian wrapper maps, a native supplier or a full multiplication recurrence.

**Proof: complete line costs.** Fix the shared input magnitude bound described below and choose the same local error target for every line on an axis. By A11, the truncation width can be chosen with

`w_i²=Θ(p/a_i)=Θ(sqrt(p)/d)`.

The shortest run has length `Θ(1/θ_i)=Θ(d)`, whereas `w_i=Θ(p^(1/8))` and `d=Θ(p^(1/4))`. Thus its boundary neighborhoods are disjoint for all sufficiently large p, as A11 requires. Its physical contraction parameter is

`τ_i=2/[exp(a_i ρ_i θ_i)−1]=O(exp(−c sqrt(p)))`

for a uniform positive c. In particular every τ_i is at most 1/8 eventually. The complete line application bound of A11 is

`O(S_i[log(2+1/θ_i)+θ_i w_i²])`

`=O(S_i[log d+sqrt(p)/d²])`.

This includes both applications of the block inverse, the sparse U z product, the boundary solve, gathering and scattering. It does not replace the second block inverse by a dense stored `B^(−1)U` product.

For a square axis, exactly `V/S_i` arbitrary fibers are transformed. Apply Theorems 3–4: the preparation is shared, while all per-fiber work is paid. Summing the line bound over D axes gives

`O(V[d log d+sqrt(p)/d]) = O(V p^(1/4) log p)`.

**Proof: whole-tensor error and word width.** A11 gives `||N_i^(−1)||∞≤(1−τ_i)^(−1)`. Put

`K=∏_i(1−τ_i)^(−1)`.

For τ_i at most 1/8, `−log(1−τ_i)≤2τ_i`; hence

`log K≤2Σ_i τ_i=O(p^(1/4) exp(−c sqrt(p)))`.

Therefore K is at most e eventually. This uses the actual completed physical maps. The internal run similarities have exponential magnitude, but their cost and precision are already paid inside each completed line procedure. Multiplying their separate condition numbers across all axes would discard the cancellation proved by A11 and give an unnecessary precision bound.

Choose every axis procedure to have uniform absolute local error at most `2^(−P)/(16D)`. The completed line error bounds also bound the full axis error in maximum norm because its fibers are independent. The suffix-error identity from Theorem 5, with the physical inverse norms just bounded, then gives final error at most

`K D · 2^(−P)/(16D) ≤ e·2^(−P)/16 < 2^(−P)`.

The same partial-prefix argument bounds every approximate intermediate array by `e(X+1)`, so this is a public sufficient input-magnitude bound for preparing every axis procedure; preparation does not depend on a particular fiber's values. A local target with `P_i=P+ceil(log₂(16D))` therefore suffices. Its A11 guard requirement is

`P_i + O(a_i/θ_i + log(S_i+1) + log(w_i+1) + log(e(X+1)+1))`.

Here `a_i/θ_i=Θ(d² sqrt(p))=Θ(p)`, and every other term is O(p). Thus the complete line algorithm, including its FFT factors and boundary arithmetic, uses O(p) integral and fractional bits. A fixed sufficiently large multiple of p also contains the raw products before rescaling. Both its rounding errors and its exponent-dependent range are included in this budget.

**Proof: preparation and amortization.** A11 prepares the run convolution kernels, sparse boundary coupling, local boundary responses and boundary factorizations using a uniform polynomial number of operations in `S_i`, p and the other displayed polynomial parameters. Since `S_i≤exp(O(p^(3/4)))`, each such polynomial is `exp(O(p^(3/4)))` times a polynomial in p, which is `2^(o(p))`. There are only `O(p^(1/4))` axes, so their total preparation has the same classification. The prepared storage is no larger than its explicitly written polynomial-sized data. If `log V=Θ(p)`, taking logarithms shows the preparation is `V^(o(1))`; its ratio to `V p^(1/4)log p` tends to zero. This establishes the complete stated bound. ∎

**Fixed-power comparison within the same adapter scope.** The inherited ordinary reused-band construction has inverse-adapter work `O(V[d+p^(1/4)sqrt(d)])`. At `d=Θ(p^(1/4))` its second term is `O(V p^(3/8))`. The construction above gives the smaller bound `O(V p^(1/4)log p)`: the ratio of the displayed growth bounds is `p^(1/8)/log p`, which tends to infinity. This compares sufficient upper bounds for the same periodic inverse family; it is not a lower bound against the earlier algorithm or a new full-multiplication κ. The new mechanisms are the exact whole-run Toeplitz inverse and the boundary-only Schur recovery, both explicitly constructed in A11.
## What these results supply

Theorem 1 turns an explicit, bounded integer DAG into a native execution contract, charging costs omitted by an algebraic circuit measure. Theorems 2–4 preserve sharing, give an explicit transpose and propagate a constructed line algorithm through the whole tensor array. Theorems 5–7 supply sufficient precision and exact coefficient recovery. Theorems 8–9 are uniform sufficient assembly arguments, including a route for genuinely coupled service families. Theorems 10–11 establish linear master precision for the normalized reciprocal chain and the complete tensor assembly of the actual run-based periodic inverse, respectively.

The remaining research task is mathematical: construct a dominant structured transform or coupled consumer satisfying a stronger complete cost contract, with finite-word intermediate bounds and independent outputs. The scalar and matrix moment results make the required composition explicit. They do not replace that construction by an assumed oracle. No lower barrier or failed search is being offered as the result.



