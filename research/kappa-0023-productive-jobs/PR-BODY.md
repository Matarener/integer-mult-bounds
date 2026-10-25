**Conditional candidate with a complete local replay; awaiting external mathematical review.**

The winning uniform templates are finite and specified explicitly by
algorithm, but at astronomically large ranks: `2^276540184361` for complex and
`2^6552928412` for BIT before covering. Their instruction lists and constants
have not been materialized. **This is an asymptotic existence result, not a
practical algorithm.**

## Result

$$
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad \kappa=0.0023.
$$

| Reference point | κ | Gain from this PR |
|---|---:|---:|
| [#1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094), selected frontier (maintainer-reviewed) | 0.001672660197 | +37.51% |
| [#4181](https://github.com/CrocSwap/integer-mult-bounds/pull/4181), highest conditional claim located in public PRs | 0.001730980256 − 10⁻⁴⁶ − 10⁻⁷⁰ | **+32.87%** |
| **This PR** | **0.0023** | |

The increase over [#4181](https://github.com/CrocSwap/integer-mult-bounds/pull/4181) is 5.690 × 10⁻⁴ in the exponent saving. The
percentages compare those endpoints, not measured running times.

Recent conditional gains have been 10⁻⁹ to 10⁻⁷ per step, obtained by
refilling the same staged words. [#4091](https://github.com/CrocSwap/integer-mult-bounds/pull/4091) proved the pooled ceiling for those
words, and [#4181](https://github.com/CrocSwap/integer-mult-bounds/pull/4181) attained it, noting that any further gain needs a changed word
or inventory. This PR changes what the recursion counts as useful output.
Helpers that finish holding a completed transform of their own arbitrary input
keep that work instead of undoing it, so one local unit produces jobs of several
ranks. A finite integer compiler then turns that mixed rule back into an
ordinary uniform supplier, so the inherited outer theorem can use it.

## The key idea: count the work helpers already do

In the uniform-supplier interface every local unit returns its helpers to the
identity. Each helper's arbitrary input is borrowed, transformed in passing and
then restored. Often, though, a helper ends a controller holding a *known,
completed* transform of its own arbitrary input. Restoring that input pays twice
for work that could be delivered as output.

We keep these **productive jobs** at whatever rank they happen to have and
price the controller by its complete mixed balance. With `W_k` independent
productive outputs of rank `k` and `p_r` paid recursive calls of rank `r`, the
mixed saving `C` solves

$$
\sum_r p_r\, r^{1-C}=\sum_k W_k\, k^{1-C}.
$$

For example, a helper that has completed a width-8 transform of its own input
earns nothing under uniform accounting. It must be restored, or forced into a
full rank-57 output, before it counts. Under mixed accounting it is simply a
rank-8 productive job and contributes `8^{1−C}` to the right-hand side. The p3
invoice below books 1,570 such helper jobs of ranks 6–9 beside its 672 main
outputs.

That change of accounting changed which controllers were worth building. A
**pK controller** is a path of `K` call pairs, `2K + 1` local calls in all. An
**idle window** is a stretch of stages in which a bank of 224 fields sits
untouched by the main calls, so helper work can be scheduled there. Even the
first complete p2 cover beats [#4181](https://github.com/CrocSwap/integer-mult-bounds/pull/4181)'s supplier endpoint (0.0017310):

| Controller (complex) | What changed | Mixed saving `C` |
|---|---|---:|
| p2, complete identity cover | Helpers priced at their own ranks | 0.0017730 |
| p2, initial-prefix deletion | Early idle windows removed literally | 0.0020133 |
| **p3, seven calls** | Integral boundary factorization; adapters replace idle paths | **0.0023051** |

The p3 controller keeps four idle windows: two of rank 16 on stages 0/1 and
5/6, and two of rank 8 on stages 2 and 4. An exact, integral factorization of
its boundary operator removes two more. Exact input/output scalar adapters
take the place of those whole idle paths, which did no useful work, and that is
what yields rank-25 and rank-57 main outputs. The emitted word
records every normalizer, absolute phase, source complement, owned center and
helper endpoint.

**How the controllers were found.** Candidates were discovered with
floating-point LP column generation. Each reported construction was then
reconstructed as exact rational patterns, and its inventory, chronology,
target mass and paid ranks were checked again without the optimizer. Larger
menus did not beat p3: paired controllers through p6, 64 p3 single-field masks
and 123,904 commuting stage allocations. These are finite search results, not
optimality claims.

A favorable balance alone proves nothing. Productive jobs have different ranks,
exist at different times and live in different physical frames. The remaining
work converts this local tariff into a κ.

## From a mixed tariff to κ

### 1. Compile mixed jobs into one uniform supplier

The inherited outer theorem needs a *uniform* supplier, in which every output
has the same rank. The obvious fix is to rotate the mixed roles so that each
array takes every role once, and it fails. Averaging replaces `Σ W_k k^τ` by a
smaller concave expression, and the mixed saving disappears. The compiler
instead keeps the hierarchy of sources, complements and exits.

It builds on the mixed-target lockstep flow of [@jacobalansussman](https://github.com/jacobalansussman)'s
Theorem 1G ([#4268](https://github.com/CrocSwap/integer-mult-bounds/pull/4268)). At a fixed top rank `N`, a Pascal-class bijection matches
each paid round's jobs to target roles of a child class at exactly equal integer
ranks. Missing demands become top-level sources of rank `s`, and the deepest
classes emit strictly smaller exit jobs of rank `e`. As in Theorem 1G, each
source array splits as `s + (N − s)`, and its complementary `N − s` axes are
completed recursively. Here the already-compiled smaller uniform program pays
for them, so every array ends with the full rank-`N` transform. With `L(n)` the
paid rank-one leaves per productive array, `w_s` normalized source weights and
`x_e` exit counts normalized by the number of source arrays,

$$
L(n)=\sum_s w_s\,L(n-s)+\sum_e x_e\,L(e),\qquad \sum_s w_s=1 .
$$

At `τ = 1 − C` the source and exit potentials are equal. Strict child/target
separation (`r_max < k_min`) makes exit ranks sublinear in `n`, so the exits
become negligible at any slightly larger exponent `z₀`. Concavity of the
complements then gives `L(n) ≤ A n^{z₀}`. Some explicit finite rank therefore
satisfies

$$
P_N < B_N\,N^{z}\qquad(z_0<z<1),
$$

which for rational `z = a/b` is the integer test `P_N^b < B_N^b N^a`. One
integer multiplier clears every batch denominator, so no fractional piece of a
physical array is ever routed. Copied inputs, owned blank storage and the one
center reused chronologically inside a unit receive no productive credit. The
full derivation is in [`FINITE-PRECOMPILATION.md` §5](https://github.com/zxv/integer-mult-bounds/blob/codex/conditional-kappa-0023/research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md#5-why-some-fixed-n-has-the-required-saving).

### 2. Delay the BIT cover until the whole program is compiled

Under the GL cover, a BIT projector `P` becomes `gPg⁻¹`. Converting each one
immediately to a weighted canonical query creates incompatible role-specific
weights, which is where the original interface failed. The fix is to compile
the *entire* finite BIT circuit first and introduce one ambient cover with one
common external weight afterward. The enabling algebra is the covariance of
complete projector jobs. With `C_N` the reversal,

$$
D_P=\begin{pmatrix}I-P & PC_N\\ C_NP & I-C_NPC_N\end{pmatrix},
\qquad
Q_S\,D_Q\,Q_S^{-1}=D_{SQS^{-1}},
\qquad
Q_S=\operatorname{diag}(S,\,C_NSC_N).
$$

Routing a whole cover fiber by `g ↦ gS` therefore matches equal-rank completed
jobs while the external weight stays independent of the fresh cover coordinate.
Only the final rank-one leaves become weighted ordinary children.

The atom exponent also had to change. The retained stopped recurrence has a
linear adapter term, and with the old atom exponent 1/1000 that term caps the
ordinary BIT saving at 0.001, whatever the supplier achieves. Raising it to
0.003 removes the cap. The compiled program reaches 0.002760, paying the generic
cover fallback leaves 0.002750, and the conversion gives

$$
(1-0.003)(0.002750)+0.003\,(0.0000384599)=0.0027418653797 .
$$

We admit BIT conservatively at 0.0027, so it no longer caps the complex
supplier. The cover prime satisfies `q > 25,600,000 N^5`, and every bad class
pays its full fallback bill.

### 3. Re-derive precision and storage for the new template

A compiled word this large cannot inherit the old supplier's small constants.
[`FINITE-TEMPLATE-CLOSURE.md`](https://github.com/zxv/integer-mult-bounds/blob/codex/conditional-kappa-0023/research/kappa-rebuild/transfer-audit/FINITE-TEMPLATE-CLOSURE.md) derives new ones from the template's
own finite counts. The semantic precision guard stays linear in depth, `C0·d`,
because children return completed values on one fine grid. Their temporaries
are never simultaneously unfinished parent operands. The simultaneous reserve
becomes `q0(h,p) ≤ C(log₂h + h^0.003 (log₂p)^3 + 1)`, with reserved bits
deferred to later shrinking phases.

### 4. Pay the complete outer bill

Every retained outer cost has exponent saving strictly above 0.0023:

| Outer cost | Saving |
|---|---:|
| Main transform | 0.00230197698 |
| Global coordinate routing | 0.0023025 |
| Fused Gaussian work | 0.00231193094 |
| Group BIT routing | 0.002312430925 |
| Boundary matrix work | 0.00230297698 |
| Sparse union movement | 0.40855297698 |
| Group scans | 0.99998 |
| Polynomial products | 0.99999 |
| Microbox face corrections | 77.00004 |

The minimum slack is exactly `98849/50000000000 = 0.00000197698`. A separate
outer auditor recomputes all nine rows and the changed functional inequalities.
Boundary matrix work uses Strassen with the exact comparison `7^16 < 2^45`.

## Complete invoices

The counts below belong to each **local p3 mixed unit**, and their balance gives
the mixed root. BIT figures are before the cover.

| Local mixed unit | Complex | BIT |
|---|---|---|
| Productive jobs `{rank: count}` | `{6:192, 7:56, 8:93, 9:1229, 25:448, 57:224}` | `{8:3073, 22:444, 50:222}` |
| Paid calls `{rank: count}` | `{1:17623, 2:5065, 3:1738, 4:714, 5:254}` | `{1:9261, 2:9394, 3:553, 4:308, 5:714, 6:77, 7:1465}` |
| Independent productive fields | 2,242 | 3,739 |
| Total paid calls | 25,394 | 21,772 |
| Scalar allowance | 1,147,304 real primitives | 174,908 ADDs (swap = 3 ADDs) |
| Mixed root `C` | 0.0023050901948… | 0.0027698302… |

The compiler turns each unit into a uniform supplier with only rank-one paid
leaves. Its own counts are finite but enormous, and they are not the unit counts
above.

| Compiled uniform supplier | Complex | BIT |
|---|---|---|
| Explicit uniform rank | `2^276540184361` | `2^6552928412` |
| Uniform saving at that rank | 0.002304 | 0.002760 (before cover) |
| Saving entering the outer bill | **0.002304** (binding) | 0.0027 (after cover fallback and conversion) |

The exact root enclosures are `[0.002305090194876170622919094755,
0.002305090194876170622919094756]` (complex) and `[0.002769830250,
0.002769830251]` (BIT).

## Verification

Based on canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244` (priority
revision 7). Python standard library only:

```sh
python3 -B research/kappa-0023-productive-jobs/verify.py --check-only
python3 -B research/kappa-0023-productive-jobs/verify.py --out /absolute/path/to/new-replay
```

- A fresh sequential replay outside the checkout passes **23 scientific stages
  and 59 artifact comparisons**. It covers native reconstruction, phases, owners
  and bills, the finite compiler, the delayed BIT cover, the new constants, the
  explicit ranks and the independent outer audit. Logs are in
  [`research/kappa-0023-productive-jobs/evidence/`](https://github.com/zxv/integer-mult-bounds/tree/codex/conditional-kappa-0023/research/kappa-0023-productive-jobs/evidence).
- The review runner fixes a stale-pin ordering defect in the original runner and
  compares receipts across hosts under declared metadata rules. No mathematical
  field is waived, and four mutation controls, such as a changed target κ, are
  rejected.
- The import binds 365 unchanged delivered files plus 16 canonical-main inputs.
  The critical replay does not rerun every historical negative search.

**Where to start reading**

- [`OUTER-TRANSFER-AUDIT.md`](https://github.com/zxv/integer-mult-bounds/blob/codex/conditional-kappa-0023/research/kappa-rebuild/transfer-audit/OUTER-TRANSFER-AUDIT.md): proof entry point and the complete outer bill.
- [`FINITE-PRECOMPILATION.md`](https://github.com/zxv/integer-mult-bounds/blob/codex/conditional-kappa-0023/research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md): the finite integer compiler (step 1).
- [`DELAYED-COVER-BRIDGE.md`](https://github.com/zxv/integer-mult-bounds/blob/codex/conditional-kappa-0023/research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md): the delayed BIT cover and atom conversion (step 2).
- [`EXPLICIT-TEMPLATE-BOUNDS.md`](https://github.com/zxv/integer-mult-bounds/blob/codex/conditional-kappa-0023/research/kappa-rebuild/controller/EXPLICIT-TEMPLATE-BOUNDS.md): the explicit winning ranks.
- [`FINITE-TEMPLATE-CLOSURE.md`](https://github.com/zxv/integer-mult-bounds/blob/codex/conditional-kappa-0023/research/kappa-rebuild/transfer-audit/FINITE-TEMPLATE-CLOSURE.md): new precision and storage constants (step 3).
- [`VALIDATION.md`](https://github.com/zxv/integer-mult-bounds/blob/codex/conditional-kappa-0023/research/kappa-0023-productive-jobs/VALIDATION.md): replay runner, comparison rules and import details.

## Scope

- **Conditional.** The claim keeps the inherited analytic decomposition, exact
  recovery, ordered movement, fixed-tape execution and prime-padding premises.
- **Not yet reviewed.** The new universal arguments are written proofs backed by
  finite checks: the compiler, native adapters, common-weight BIT interface and
  support-local outer transfer. They are neither formally verified nor
  externally accepted.
- **Not materialized.** The winning templates' full words and constants have not
  been generated. The materialized rank-57 complex and rank-50 BIT examples check
  completion, batching and ownership, but neither reaches the limiting saving.
- The selected frontier and shared verification code are unchanged.

## Outstanding research directions

The most direct route past 0.0023 is the **H branch**. The identity `H = I + BC`
with `CB = −2I` gives `H² = I`, which suggests cheap reversible completions over
the legal ring. On the [#589](https://github.com/CrocSwap/integer-mult-bounds/pull/589) BIT word, a minimum three-row invertible completion
cuts the local correction to three rank-one calls, and phase-correct complex
owner maps pass exact checks. What it
lacks is a cheap way to close the controller's endpoints. Three interval
corrections remain, costing 672 rank-one requests in complex arithmetic and 666
in BIT, so even the cheapest BIT version falls 21 short. Generic cancellation,
register sharing and same-cut compression have been ruled out. A
geometry-aware decoder has not been. Details are in
[`LITERATURE-AND-PROBES.md`](https://github.com/zxv/integer-mult-bounds/blob/codex/conditional-kappa-0023/research/kappa-rebuild/LITERATURE-AND-PROBES.md) and the
[architecture overview](https://github.com/zxv/integer-mult-bounds/blob/codex/conditional-kappa-0023/research/kappa-rebuild/architecture/README.md).

## Open next questions

- **Review the chain as one argument.** Start with the integer source/exit
  matching and all-column native adapters, then the common-weight BIT interface
  and the support-local outer transfer.
- **Shrink the templates.** Tighten the paid-leaf superpotential or find smaller
  explicit successful ranks without giving up integer batching or complete
  constants.
- **Build a geometry-aware H decoder.** Start from the actual query subspaces,
  the phase-correct complex owners and the three-row BIT completion. A survivor
  must put preparation, routes, reads, restoration and all endpoints in one
  invoice.
- **Improve the complex tariff.** The complex mixed root now binds, so more BIT
  saving alone cannot advance this point. A changed native word or
  productive-job contract must improve its complete moment.

None of these questions is used to justify the 0.0023 claim.

## Literature

These sources shaped the construction above, grouped by the part they informed.
Each note says what the source suggested and what we actually used; the notes
describe our use, not claims by the cited authors. Sources behind unsuccessful
branches are included because they explain the turns the search took.

### Productive work and mixed accounting

1. **Jacob Alan Sussman** (2026). “Theorem 1G: mixed-target recursion.”
   [PR #4268](https://github.com/CrocSwap/integer-mult-bounds/pull/4268) ·
   [pinned proof](https://github.com/jacobalansussman/wht-power-saving-lean/blob/563b4e6e913625637f36ba7869bf5fcd0dd4975a/research/record-track/proofs/theorem-1g.md)

   The direct algorithmic predecessor. Its integer Pascal-class lockstep flow
   matches unequal target jobs with smaller paid demands under an exact moment
   balance, splitting each source as `s + (n − s)` and paying the remainder
   recursively. It is the core of our compiler. Our contribution is realizing
   that mechanism as a finite integer compiler with native adapters, an explicit
   winning rank and the outer transfer. [#4268](https://github.com/CrocSwap/integer-mult-bounds/pull/4268) claims a DFT improvement and no κ; its Lean results
   do not verify this compiler or the multiplication claim.

2. **Arnold Schönhage** (1981). “Partial and Total Matrix Multiplication.”
   *SIAM Journal on Computing* 10(3), 434–455.
   [doi:10.1137/0210032](https://doi.org/10.1137/0210032)

   The classic precedent for assembling useful partial computations into a
   larger complete one, which is the shape of the productive-job idea. The
   tensor theorem served only as motivation; the native source/exit schedule
   and paid complements carry the actual bridge.

3. **Péter Vrana** (2024). “Partial and weighted matrix multiplication.”
   arXiv:2408.15728. [arXiv](https://arxiv.org/abs/2408.15728v1)

   Reinforced that unequal, weighted useful work deserves its own accounting.
   It encouraged us to keep mixed ranks rather than round them to a uniform
   job. Its support-rank theorem is not applied to transform programs.

4. **Robert Robere and Jeroen Zuiddam** (2021). “Amortized Circuit Complexity,
   Formal Complexity Measures, and Catalytic Algorithms.” ECCC TR21-035.
   [ECCC](https://eccc.weizmann.ac.il/report/2021/035/)

   Motivated one production-and-consumption ledger with an explicit price for
   every resource. Its repeated-output setting reuses a single input, so it
   grants no independent-output credit here.

### Building the controller over the legal coefficient ring

5. **J. J. Koliha** (2001). “Block diagonalization.” *Mathematica Bohemica*
   126(1), 237–246. [EMIS](https://emis.de/ft/45438)

   Resolutions of the identity by idempotents pointed us at the operator
   coefficients of the whole controller rather than its individual calls. That
   view informed the exact coefficient factorizations tested for p3, including
   the integral boundary factorization that removes two idle windows.

6. **Ahmad Abdi, Gérard Cornuéjols, Bertrand Guenin and Levent Tunçel** (2023).
   “Dyadic linear programming and extensions.” arXiv:2309.04601.
   [arXiv](https://arxiv.org/abs/2309.04601)

   Made the denominator restriction a first-class constraint. Power-of-two
   balancing and shear factorizations then avoided an unavailable division
   by 13. Its general LP algorithm was not implemented.

7. **Ahmad Abdi, Gérard Cornuéjols, Bertrand Guenin and Levent Tunçel**
   (2021; rev. 2022). “Total dual dyadicness and dyadic generating sets.”
   arXiv:2111.05749. [arXiv](https://arxiv.org/abs/2111.05749v2)

   Separated a rational feasibility witness from a realization over the
   allowed dyadic ring. This shaped the search's rejection gates.

8. **Ingrid Daubechies and Wim Sweldens** (1998). “Factoring Wavelet Transforms
   into Lifting Steps.” *Journal of Fourier Analysis and Applications* 4(3),
   247–269. [author manuscript](https://9p.io/who/wim/papers/factor/factor.pdf)

   Lifting suggested reversible triangular factors for the six-bank transfer in
   place of generic scalar elimination. Frame contacts, coefficients,
   preparation and restoration were still checked natively.

9. **Christopher M. Brislawn** (2024). “The Causal Complementation Algorithm
   for Lifting Factorization of Perfect Reconstruction Multirate Filter Banks.”
   arXiv:2408.07970. [arXiv](https://arxiv.org/abs/2408.07970v1)

   Suggested factors constrained by *when* boundary data become available, not
   unconstrained matrix elimination. We used exact legal shears and verified
   the actual contact times.

10. **Christopher M. Brislawn** (2019; final rev. 2024). “Factoring Perfect
    Reconstruction Filter Banks into Causal Lifting Matrices: A Diophantine
    Approach.” *Journal of Computational Algebra* 12, 100024.
    [arXiv:1902.09040](https://arxiv.org/abs/1902.09040v5)

    Sharpened the same causal-divisibility question in an earlier handoff. It
    never licensed an unavailable contact or an uncharged inverse.

11. **Hyung-Ju Park** (1995). *A Computational Theory of Laurent Polynomial
    Rings and Multidimensional FIR Systems.* PhD thesis, UC Berkeley,
    UCB/ERL M95/39.
    [report](https://www2.eecs.berkeley.edu/Pubs/TechRpts/1995/ERL-95-39.pdf)

    The factor `I − P + zP` (§7.4) guided exact projector/delay
    representations, checked with rational oblique projectors and their full
    coefficient identities. No orthogonal rotations were imported.

12. **Zinnur Doğanata, P. P. Vaidyanathan and Truong Q. Nguyen** (1988).
    “General synthesis procedures for FIR lossless transfer matrices, for
    perfect-reconstruction multirate filter bank applications.” *IEEE Trans.
    Acoustics, Speech, and Signal Processing* 36(10).
    [doi:10.1109/29.7544](https://doi.org/10.1109/29.7544) ·
    [Caltech copy](https://authors.library.caltech.edu/records/mv71c-vqj75)

    Inspired a transfer-matrix view of the controller with an explicit boundary
    basis. Its lossless lattices do not license irrational rotations or free
    frame changes.

13. **John Urschel** (2023). “Representing the Special Linear Group with Block
    Unitriangular Matrices.” arXiv:2305.00485.
    [arXiv](https://arxiv.org/abs/2305.00485v2)

    Motivated short block-shear controllers in the earlier redesign. Its
    field-level factor counts were leads only; dyadic coefficients, contacts
    and the recursive bill were checked separately.

### Arbitrary dirty state, restoration and causal flow

14. **Jean-Guillaume Dumas and Bruno Grenet** (2024). “In-place accumulation
    of fast multiplication formulae.” ISSAC 2024; arXiv:2307.12712.
    [arXiv](https://arxiv.org/abs/2307.12712v3)

    Suggested borrowing completed output arrays as dirty scratch and restoring
    them exactly. Every native contact and reverse operation stayed priced.

15. **Harry Buhrman, Richard Cleve, Michal Koucký, Bruno Loff and Florian
    Speelman** (2014). “Computing with a full memory: Catalytic space.”
    ECCC TR14-053. [ECCC](https://eccc.weizmann.ac.il/report/2014/053/)

    Supplied the discipline for borrowed scratch: it starts arbitrary and must
    return exactly. Productive jobs meet a different contract, finishing with
    the declared transform of their arbitrary input. Keeping the two
    requirements apart is what lets the construction credit productive work.
    It also motivated all-column dirty-bank tests rather than zero-initialized
    examples.

16. **Antoine Vinciguerra** (2026). “An Operator Approach to Register Programs
    for Catalytic Computing.” arXiv:2609.18692.
    [arXiv](https://arxiv.org/abs/2609.18692v1)

    Motivated stating restoration as a whole-operator identity and checking
    whole arbitrary register columns. Its access counts were not imported. Its
    polynomial-degree and passive-output assumptions differ from our linear
    jobs, and its matrix lifting and coefficient divisions need not stay
    within the permitted dyadic coefficients.

17. **Marten Folkertsma, Ian Mertz, Sergii Strelchuk and Sathyawageeswar
    Subramanian** (2026). “Fast Cliffords When Your Quantum Memory Is Full.”
    arXiv:2609.40144. [arXiv](https://arxiv.org/abs/2609.40144v1)

    Prompted a dirty-workspace cycling probe, which was rejected. Its
    restored-workspace premise fails for our accumulating dirty logger.

18. **Joseph Connelly and Kenneth Zeger** (2016). “Linear Network Coding over
    Rings, Part II: Vector Codes and Non-Commutative Alphabets.”
    arXiv:1608.01737. [arXiv](https://arxiv.org/abs/1608.01737v2)

    Kept coding over the actual coefficient structure separate from a
    convenient field-rank count. Acquisition, transport, scatter and erasure
    therefore stay in the causal interface and the invoice.

19. **Mark Braverman and Zhongtian He** (2026). “The Multiple Unicast
    Conjecture is False.” arXiv:2610.10108.
    [arXiv](https://arxiv.org/abs/2610.10108v1)

    Motivated timed, operator-valued carriers with causal local processing.
    Its characteristic-three code and throughput factors were not transferred.

20. **Vadim Kostrykin and Robert Schrader** (2001). “The Generalized Star
    Product and the Factorization of Scattering Matrices on Graphs.” *Journal
    of Mathematical Physics* 42, 1563–1598.
    [arXiv:math-ph/0008022](https://arxiv.org/abs/math-ph/0008022)

    Suggested composing through retained interface variables in earlier work.
    It remained an analogy; feedback inverses and recursive costs could not be
    omitted.

### BIT synthesis, state bounds and the H branch

21. **Ketan N. Patel, Igor L. Markov and John P. Hayes** (2008). “Efficient
    Synthesis of Linear Reversible Circuits.” *Quantum Information and
    Computation* 8(3–4), 282–294.
    [arXiv:quant-ph/0302002](https://arxiv.org/abs/quant-ph/0302002)

    Motivated explicit binary ADD/SWAP synthesis with shared linear forms. It
    was used for exact F₂ synthesis and never for characteristic-zero complex
    arithmetic. The archived BIT note cites the preprint under another title.

22. **Andrea Visconti, Chiara V. Schiavo and René Peralta** (2018). “Improved
    upper bounds for the expected circuit complexity of dense systems of linear
    equations over GF(2).” *Information Processing Letters* 137.
    [NIST](https://www.nist.gov/publications/improved-upper-bounds-expected-circuit-complexity-dense-systems-linear-equations-over)

    Suggested keeping shared dense sums alive until all consumers finish. The
    resulting deferred reconstruction did not remove the physical frame or the
    dirty baseline.

23. **Alex Parent, Martin Roetteler and Krysta M. Svore** (2015). “Reversible
    circuit compilation with space constraints.” arXiv:1510.00377.
    [arXiv](https://arxiv.org/abs/1510.00377)

    Motivated joint lifetime and cleanup accounting. The helper-pair census
    then rejected all five geometrically eligible coalescings; lifetime overlap
    alone was not enough for native reuse.

24. **Dmitry Chistikov, Szabolcs Iván, Anna Lubiw and Jeffrey Shallit** (2017).
    “Fractional Coverings, Greedy Coverings, and Rectifier Networks.”
    STACS 2017, LIPIcs 66, 23.
    [doi:10.4230/LIPIcs.STACS.2017.23](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.STACS.2017.23)

    Motivated shared consumer maps and source-neighborhood covers. Rectifier
    size does not pay for restoration or native transport.

25. **G. David Forney Jr.** (2009; rev. 2010). “Minimal realizations of linear
    systems: The ‘shortest basis’ approach.” arXiv:0910.4336.
    [arXiv](https://arxiv.org/abs/0910.4336v3)

    Framed the question as the state needed across an actual time cut. The
    nine-center rank checks then ruled out an eight-signal carrier at that cut,
    leaving other cuts open.

26. **Navin Kashyap** (2007). “On Minimal Tree Realizations of Linear Codes.”
    arXiv:0711.1383. [arXiv](https://arxiv.org/abs/0711.1383)

    State requirements depend on the decomposition and consumer interface. This
    scoped the same fixed-cut obstruction rather than a universal lower bound.

27. **Clément Pernet and Arne Storjohann** (2018). “Time and space efficient
    generators for quasiseparable matrices.” *Journal of Symbolic Computation*
    85, 224–246. [arXiv:1701.00396](https://arxiv.org/abs/1701.00396)

    Motivated compact exact state across cuts in earlier observer probes, whose
    measured gaps exposed insufficient state in the tested contract.

28. **Itziar Baragaña and Alicia Roca** (2019). “Fixed rank perturbations of
    regular matrix pencils.” arXiv:1907.10657.
    [arXiv](https://arxiv.org/abs/1907.10657v2)

    Distinguished prescribed-rank completion from a loose rank bound. Its
    field-size hypotheses were not imported into F₂; the BIT completion was
    proved and tested directly.

29. **A. Amparan, I. Baragaña, S. Marcaida and A. Roca** (2023; rev. 2024).
    “Row or column completion of polynomial matrices of given degree.”
    arXiv:2306.06104. [arXiv](https://arxiv.org/abs/2306.06104v2)

    Suggested completing only the designated cheap output rows. Checking
    invertibility instead of requiring an involution produced the three-row BIT
    completion. Endpoint debt still blocks a higher claim.

30. **Christophe Reutenauer** (1994). “A Survey on Noncommutative Rational
    Series.” FPSAC 1994, 393–402.
    [proceedings](https://fpsac-archive.github.io/FPSAC94/ARTICLES/45Reutenauer.pdf)

    Motivated testing the coefficient space of all boundary words jointly. The
    resulting span obstruction rejects the universal two-passage model and
    leaves geometry-aware coding open.

31. **Jean Berstel and Christophe Reutenauer** (2010). “Minimization.” Ch. 2 of
    *Noncommutative Rational Series with Applications*, Cambridge University
    Press, 29–46.
    [chapter](https://www.cambridge.org/core/books/abs/noncommutative-rational-series-with-applications/minimization/ACD53CC08C3CB9451564D3488D24FE22)

    Supplied the minimal-realization viewpoint for the same test. The native
    obstruction has its own direct proof.

### Retained outer inputs

32. **Volker Strassen** (1969). “Gaussian elimination is not optimal.”
    *Numerische Mathematik* 13, 354–356.
    [doi:10.1007/BF02165411](https://doi.org/10.1007/BF02165411)

    The retained boundary-matrix algorithm. The exact comparison
    `7^16 < 2^45` permits the conservative exponent 45/16 in the outer ledger.

33. **Timothy S. Trudgian** (2014). “Updating the error term in the prime
    number theorem.” arXiv:1401.2689.
    [arXiv](https://arxiv.org/abs/1401.2689v2)

    Theorem 2 is a cited input to the inherited fine-prime padding argument.
    The local verifier does not re-prove it.

## Attribution

| PR | Submitter | Used here |
|---|---|---|
| [#23](https://github.com/CrocSwap/integer-mult-bounds/pull/23) | [@jacklightChen](https://github.com/jacklightChen) | Semantic precision and bulk resampling |
| [#555](https://github.com/CrocSwap/integer-mult-bounds/pull/555) | [@eumemic](https://github.com/eumemic) | Punctured BIT supplier predecessor |
| [#589](https://github.com/CrocSwap/integer-mult-bounds/pull/589) | [@DreamingOfClouds](https://github.com/DreamingOfClouds) | Retained BIT word and transport improvements |
| [#1094](https://github.com/CrocSwap/integer-mult-bounds/pull/1094) | [@rohanarun](https://github.com/rohanarun) | Selected conditional result |
| [#1673](https://github.com/CrocSwap/integer-mult-bounds/pull/1673) | [@Vlado-V](https://github.com/Vlado-V) | Capped phase-cell fusion outer wrapper |
| [#1758](https://github.com/CrocSwap/integer-mult-bounds/pull/1758) | [@jeremykothe2](https://github.com/jeremykothe2) | Gauge-free interiors and radix-distributed union schedule |
| [#1786](https://github.com/CrocSwap/integer-mult-bounds/pull/1786) | [@chafreaky](https://github.com/chafreaky) | Fine source-prime padding |
| [#3945](https://github.com/CrocSwap/integer-mult-bounds/pull/3945) | [@Dugongue](https://github.com/Dugongue) | Staged544 owner-fill predecessor |
| [#4076](https://github.com/CrocSwap/integer-mult-bounds/pull/4076) | [@rohanarun](https://github.com/rohanarun) | Three staged helper entries and T360 fill |
| [#4085](https://github.com/CrocSwap/integer-mult-bounds/pull/4085) | [@zxv](https://github.com/zxv) | Receiver sharing on the staged T360 supplier |
| [#4088](https://github.com/CrocSwap/integer-mult-bounds/pull/4088) | [@1337isnot1337](https://github.com/1337isnot1337) | Mixed fourth staged entry |
| [#4091](https://github.com/CrocSwap/integer-mult-bounds/pull/4091) | [@RossRichardson](https://github.com/RossRichardson) | Fixed-inventory pooled ceiling |
| [#4181](https://github.com/CrocSwap/integer-mult-bounds/pull/4181) | [@rohanarun](https://github.com/rohanarun) | Pooled-ceiling fill; comparison point |
| [#4268](https://github.com/CrocSwap/integer-mult-bounds/pull/4268) | [@jacobalansussman](https://github.com/jacobalansussman) | Mixed-target recursion (Theorem 1G), basis of the compiler; claims no κ |

Earlier geometry, native checker, owner, compiler and circuit contributions are
credited in the frozen packages and source notices.

Prepared with substantial AI assistance, including ChatGPT Pro (Astra 6.0),
GPT-6.1 Sol and Opus 5.5. Apache-2.0 for new material; original notices and
third-party licenses are retained.
