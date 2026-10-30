# Complete spectator prefixes for the global Hadamard supplier

Prepared by [zxv](https://github.com/zxv), with substantial OpenAI Codex assistance. Apache-2.0. This is a constructive conditional interface proof. The completed suppliers, fixed-tape primitives, numerical guarantees and analytic framework remain hypotheses.

## 1. The opening in the actual caller

Canonical main `721c03822c421b7f7fcbb2598993b947c4d88419` selects PR6030 at κ=.003125804, priority revision 8. Its outer ledger is the PR4359 `endpoint.py` named in SOURCES.json. The selected five assumptions remain.

The retained `TENSOR-COMPILER.md` §3 states that its Hadamard schedule is identical across axes and coarse-label blocks; only the diagonal tables differ. `SUPPLIER-SUPPORT-AUDIT.md` §§2–3 and `SUPPORT-ADVERSARIAL-AUDIT.md` §3 explicitly authorize a completed H call on the **complete global binary tensor**, followed by restoration of the original coarse-coordinate order before the next diagonal. A fixed coarse-label microbox is outside that contract.

The current reservation takes the row prefix and compact controls from the selected neighborhoods themselves. Those selected bits are deferred, so the active call is repeated on the reserved bits later. Under the conservative new-stock envelope in `OUTER-TRANSFER-AUDIT.md` §5, this needs the reserve to be sublinear in the active width. This is a sufficient allocation policy, not a property of the completed kernel.

The source `notes/compact-control-layout.tex` supplies a stronger endpoint fact than preservation of address labels alone: each completed call is the desired C tensor on active coordinates and **identity on all reserved and spectator coordinates for arbitrary incoming coefficients**. Its row split uses only the leading row region; both front control fields and the back control field remain complete inside every row. This enables a different allocation.

## 2. A sparse gather with an arbitrarily long spectator prefix

Let the globally complete stream have binary address set `{0,1}^N`, arbitrary preceding fibers and arbitrary payloads. Let h disjoint complete K-bit neighborhoods occupy an ordered list S of k=hK positions. The selected bit has the same offset in each neighborhood. The input need not be separable, zero, or independent across coordinates.

Let Q≥1 be the **product** of all simultaneous row divisibility requirements for the complete call, including nested BIT/complex calls. Put

$$R=K\left\lceil\frac{\lceil\log_2 Q\rceil}{K}\right\rceil.$$

Choose front and back capacities

$$G=4\lceil\log_2p\rceil+6,\quad K=128G,\quad H=hG,$$

$$F=K\lceil2H/K\rceil,\qquad B_c=K\lceil H/K\rceil.$$

Assume the following fields, plus the retained protected suffix/router workspace, fit inside N:

$$\underbrace{R}_{\rm row}\ \big|\ \underbrace{F}_{\rm two\ front\ fields}\ \big|\
\underbrace{hK}_{\rm active\ slots}\ \big|\ \underbrace{B_c}_{\rm back\ field}\ \big|\ \rm spectators.$$

Use the exact sparse extension already proved in the retained `SUPPORT-ROUTER.md`; its new application here is the spectator-prefix placement and complete-callee boundary. Let T be the ordered positions of the active slots in this display. Map S to T in order. Complete the coordinate permutation π by sending `T\S` bijectively to `S\T`, in any fixed order, and fixing everything outside `S∪T`.

**Lemma 1.** π is a bijection supported on at most 2hK positions. Every preimage of a physical position outside T lies outside S. In particular the new row prefix, front controls and back controls are genuine spectators of the selected kernel.

**Proof.** The prescribed map S→T is a bijection. The remaining positions in the union are precisely `T\S` in the domain and `S\T` in the image, of equal cardinality. Their matching completes a bijection on the union. The identity completes it on the whole address set. Since all of S maps into T, no position outside T has a preimage in S. ∎

The original S may intersect the proposed physical row prefix. This is allowed: exposure moves those selected neighborhoods to T first. At the moment rows are exposed, the row prefix contains only spectator coordinates. No original selected bit is preprocessed or discarded.

Crucially, this construction does **not** transpose an R-bit field across the address. It changes at most 2hK coordinate positions, even if R≫hK and T starts far from S. The retained support-local router charges by moved support, with arbitrary distance. Therefore exposure and restoration cost

$$O\!\left(V(h+1)^{1-a_{\rm BIT}}\operatorname{polylog}p+\operatorname{poly}p\right).$$

Here a_BIT is the saving of the supplied paid equal-width BIT primitive. It is not free indexed access, and it is not automatically the old .0034 primitive when a stronger target requires a stronger router. The short-record proof reserves its untouched suffix before routing and confines later operations to its complement. The current construction leaves Θ(p) binary coordinates available whenever R+O(h polylog p)=o(p), so the same suffix and reservoir conditions hold.

## 3. Complete rows, dirty data, one padding and return

After π, interpret the first R bits as the row label and pad its count once:

$$2^R\le Z:=Q\left\lceil2^R/Q\right\rceil<2^{R+1}.$$

Each added row contains the **entire** within-row range, including all active slots, both front controls, the back control, remaining spectators and the record suffix. Only the extra rows are zero. Every original row remains arbitrary. Existing row coordinates are being reinterpreted; there is no factor `2^R` increase in volume. The only enlargement is Z/2^R<2.

Call the retained **active core at width h**, with H=hG and its complete stock Q. The spectator blocks are not passed as extra selected axes to the old public preprocessor; that step is replaced by this wrapper. The core proof uses the complete-field capacities, not their origin as selected axes. Run this complete active callee using Q. Its endpoint is

$$I_{\rm ROW}\otimes I_{\rm controls}\otimes C_T\otimes I_{\rm remaining\ spectators}.$$

During this call Z is a possibly nonbinary preceding fiber, with the same binary within-row fields. Exposure routers run only before padding and after restriction, as in the retained source. Q covers the full nested product, so the source splits, chronological child returns and reassemblies require no second exterior padding. Temporary row mixing inside the implementation is permitted; its completed endpoint must be the displayed row-independent operator.

Under the retained exact/common-grid endpoint contract, every padded zero row returns to zero. A rounded replacement must separately supply its completed-error and padding-disposal guarantee; ideal zero rows do not authorize silently erasing approximate residuals. Delete padded rows **before** running π inverse. Then restore the original coordinate layout. As an operator on the original global tensor, the result is exactly

$$P_\pi^{-1}(I\otimes C_T)P_\pi=C_S.$$

This is equality on arbitrary full arrays, including arbitrary correlations with every borrowed spectator. All h selected kernels are completed in this one top-level active-core invocation, which still performs its retained internal recursion. There is no active-axis deferral caused by row or compact-field reservation.

For arbitrary intervening diagonal operators D1,D2, the actual schedule is

$$D_2\,P_\pi^{-1}(I\otimes C_T)P_\pi\,D_1=D_2 C_S D_1.$$

There is no claim that a coarse-dependent diagonal commutes with exposure or with intermediate row mixing. The next diagonal is executed only after padding deletion and inverse exposure. This is exactly the source tensor compiler's global-call boundary.

Three limitations are substantive. A row-preserving but row-dependent endpoint `direct_sum_r C_r` is insufficient. A fixed-label microbox lacks complete spectator ranges. And a native caller needing the sum of simultaneous logarithmic stocks must not replace their product by a maximum. The verifier's controls test each distinction.

## 4. Uniform capacity and cost without an active-width stock cutoff

Let N=Θ(p), h≤C p^x, x<1, and suppose the **total** stock satisfies

$$\log_2Q\le C_0\bigl(1+\log(2h)+h^\nu p^\zeta(\log(2p))^A\bigr),\qquad
0\le\nu<1,\quad\zeta\ge0.$$

Q and the active-core descriptors must be generated within the retained charged polynomial(p) setup budget. A short numeric encoding alone does not prove fast generation. The row prefix is one aggregate field; it does not create R separately parsed descriptors. Here the bound is on binary row bits. A source bound in complete K-bit chunks has the same power exponents because K=Θ(log p). Constants and degrees are fixed and computable before input length varies.

If

$$\boxed{\nu x+\zeta<1,}$$

then `R=O(p^(νx+ζ) polylog p+log p)=o(p)`, and `hK+F+B_c+router_workspace+protected_suffix=o(p)`. Thus the display in §2 fits eventually. The source long-axis condition also holds for d=Θ(p^ε), ε<1: each original axis has Θ(p^(1−ε)) bits and can contain its K-bit neighborhood. No requirement compares R with h or asks a single original axis to hold the row prefix.

With explicit constants, an effective threshold follows from the positive power gaps. Below that fixed global threshold one may use the retained elementary algorithm; this is a finite parameter range absorbed in the asymptotic constant. No p-dependent `h≥p^(ζ/(1−ν))` threshold is needed.

There is also no coefficient-guard charge proportional to R. For any fixed active prefix matrix A and number of rows Z, `||I_Z tensor A||_infinity=||A||_infinity`, and its largest dyadic denominator height is unchanged. The scalar role maps repeat the same bounded blocks at aligned row addresses; address/row permutations have norm one and add no denominators. The retained completed-child guard recurrence therefore has the same per-node constants and selected width h. Unlike the old preprocessor, this wrapper never applies a selected kernel to a prefix/control coordinate. Any prescribed h^rho envelope thus transfers without an extra R term, under the same all-column/primitive precision hypotheses. This is a mathematical coefficient-bound transfer, not an implementation of rounded native children.

The source stopped recursion and complete stock Q are unchanged. Every internal child keeps the same complete within-row fields; its cost uses its current volume. The unused binary suffix still has Θ(p) positions because R+O(h polylog p)=o(p). Consequently the retained polynomial descriptor work, row arithmetic, parking and head-return charges have the same absorption as in the source. R-bit row parameters have O(p)-bit representations, and their setup is charged polynomial(p). The short-record suffix remains fixed by every operation that uses its length for amortization.

If the underlying completed supplier has the retained `O(V h^(1−q) polylog p)` recurrence with q<a_BIT and the strict leaf/internal gaps, the added two exposure routes fit that allowance. Whole-row padding/deletion is O(V) up to the retained logarithms. The retained C-to-H0/raw-H phases and power-of-two normalization remain paid O(V) scans with O(h) additional guard. They can be applied on the named selected bits after inverse exposure. All coefficients and the selected-width guard are unchanged by coordinate permutations; controls and row bits are address fields, not new coefficient values.

**Theorem 2.** Under the retained complete-callee, native, paid router, fixed-tape, numerical and analytic hypotheses, Lemma 1 and §3 construct a global-H interface at the same saving q whenever `νx+ζ<1`. It uses original spectator coordinates, one padding by less than two, completes all selected axes, and restores the full coarse layout before the next diagonal.

This is a constructive replacement for the source active-axis reservation. It does not establish those retained implementation hypotheses, manufacture a finite supplier or raise the selected κ. In the actual selected ζ=0 regime it removes the conservative outer deferral; an exponent improvement still needs stronger suppliers or another substantive analytic change.

## 5. The resulting positive outer admission contract

The original outer nine savings are retained unchanged. Let rational U,B>0 be completed complex-uniform and admitted ordinary BIT budgets and

$$M=\min(U,B,1/32).$$

For a prescribed global/group precision guard `d^ρ polylog(d)`, ρ≥1, retain `ρε<1` and `ρβ<1`. At the full-width call h=d=Θ(p^ε), Theorem 2 needs `νε+ζ<1`; at grouped calls it needs `νβ+ζ<1`. Since β<ε and ν≥0, the global inequality implies the grouped one. Both include the product of simultaneous nested requirements.

In the source ledger, replace its two active-width stock predicates by these two ambient stock tests. Retain all 54 strict checks and the other two functional checks, and append the two precision checks: 60 predicates in total. This is an explicitly changed wrapper, so active-width stock fit is not claimed or silently inferred.

For `0≤ζ<1` put

$$E=\begin{cases}
\min(1,1/\rho,(1-\zeta)/\nu),&\nu>0,\\
\min(1,1/\rho),&\nu=0.
\end{cases}$$

**Theorem 3.** The 60 strict exponent predicates have rational witnesses exactly when

$$\boxed{E>1/2,\qquad \mathrm{OLD}<\kappa<ME.}$$

OLD is the source's historical comparison threshold, not a universal mathematical lower bound. This theorem is the arithmetic admission result for Theorem 2's conditional interface, not a complete multiplier.

**Necessity.** The precision, ambient-stock and source dimension conditions give ε<E. Membership plus β>0 gives ε>1/2. Source ordering gives q<M, and the main row gives `κ<εq<ME`. The baseline row gives κ>OLD.

**Sufficiency.** Choose

$$\epsilon=\frac{\max(\kappa/M,1/2)+E}{2},\quad
q=(\kappa/\epsilon+M)/2,\quad a=(2q+M)/3,\quad b=(q+2M)/3.$$

Then `1/2<ε<E≤1` and `κ<εq<q<a<b<M`. Put

$$\eta=\min((2\epsilon-1)/2,(1-\epsilon)/2),\quad
\beta=2\epsilon-1-\eta,$$

$$h_0=\min((\epsilon-1/2)/2,1/64),\quad
\mathrm{layout}=3/32-\epsilon q-h_0,\quad
r_0=(1-\rho\epsilon)/4,\quad \mathrm{stop}=(b-a)/(2b).$$

Here `0<β<2ε−1<ε`, `ξ=ε−h0`, and all four new precision/ambient-stock checks are positive. For ν=0, both stock checks equal `1−ζ>0`.

All remaining source predicates follow directly. The leaf saving is `(a+b)/2>a`, the internal exponent is `1−a`, and `λ=1−(q+a)/2` gives every λ gap. The positive membership/header gaps follow from β<2ε−1. Both group gauge expressions exceed `4(1−ε)+2h0`, while `0<r0≤(1−ε)/4`. Moreover

$$1-\epsilon+q\beta-\epsilon q\ge(1-\epsilon)(1-3q/2)>0,$$

so the fused Gaussian and group BIT savings exceed the main saving. The boundary saving is at least 5/64; the sparse-union saving is at least 31/64; the group-scan saving is ε−η≥(3ε−1)/2>1/4, and the polynomial and microbox rows have savings greater than 1/2 and 77. They all exceed κ<1/32. The source constants, halo bounds, semantic group guard and explicit metadata predicate stay positive. This checks every family of the 60 predicates. The verifier additionally evaluates their exact source expressions on 1,920 witnesses, including points 10^-24 below ME. ∎

The general unchanged-ledger result `OLD<κ<M` belongs to [Nick Petalas](https://github.com/petalas)'s [PR5984](https://github.com/CrocSwap/integer-mult-bounds/pull/5984). The rational witness shape also follows the preceding [PR6062](https://github.com/CrocSwap/integer-mult-bounds/pull/6062) analysis. The new contribution is the spectator-prefix construction and its ambient-stock condition; no unchanged-ledger theorem is claimed again.

## 6. An explicit advancing interface that active-axis stock cannot fit

Take **hypothetical completed** U=B=.02, precision exponent ρ=3/2 and total stock envelope

$$\log_2Q=O(h^{1/2}p^{3/5}\operatorname{polylog}p).$$

Then E=2/3 and ME=1/75. The new interface admits κ=.011 with

$$\epsilon=73/120,\quad\beta=13/120,\quad
q=139/7300,\quad a=106/5475,\quad b=431/21900.$$

The remaining parameters and every row are in RESULT.json. The main saving is `139/12000≈.01158333`, and all 60 predicates have positive slack. The stock powers are `νε+ζ=217/240<1` globally and `νβ+ζ=157/240<1` in grouped calls. Row prefixes can be much larger than their active widths, while the global tensor still contains enough complete spectator coordinates.

Putting the same envelope into active axes would require `β(1−ν)>ζ`, i.e. β>6/5, which cannot hold. The construction escapes that restriction by changing where rows come from. It does not beat an unchanged invoice or declare a new .011 multiplier; the .02 suppliers remain missing.

Six encoded layout checks at `log2 p=480,960,1920` verify complete prefix/control/active fields, the retained finite K guard, per-axis neighborhoods, router reservoirs and the protected suffix for both widths. They manipulate compressed integer counts; they do not execute astronomical tensors. Small exact reference fixtures separately execute the operator, padding, arbitrary dirty rows and label-dependent diagonal boundaries. The all-size theorem uses the written proof, not extrapolation from either family of checks.
