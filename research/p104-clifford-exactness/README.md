# A phase-compatible exact domain for one complete P104 collector

This package gives an explicit Gaussian Newton lattice on which the original
fifteen-event P104 collector executes **exactly on its retained grid**, including
both separately archived native transports and all four actual phase wrappers.
Its five borrowed sources remain unchanged, its dirty query receives the exact
native update, and its owned private array returns to literal zero.

The new result is the phase-compatible entrance contract, its all-rank
maximality theorem, and its application to this complete local collector.
The construction uses classical Clifford and Barnes–Wall/coding ideas, with a
self-contained proof for the source's Gaussian normalization. It does not
claim a new classical lattice family or a new scalar precision threshold.

The entrance is a substantive restriction. A full P104 producer has not been
shown to supply it. The package also specifies and charges an optional codec
schedule for arbitrary coefficient inputs; that schedule realizes the conjugate
logical map `E^-1 U E`. Input conversion, later divisions, physical hosting and
recursive consumption still have to meet the larger caller's contract. There
is no supplier or kappa improvement in this contribution.

## Mathematical result

Put `R = Z[i]` and `pi = 1+i`. An array on an `r`-bit address cube has unique
multilinear Newton coefficients `a_S`. Define

\[
 \mathcal B_r=\{f(x)=\sum_S a_Sx^S:\ \pi^{|S|}\mid a_S\},
 \qquad
 E_r=\begin{pmatrix}1&0\\1&1+i\end{pmatrix}^{\otimes r}.
\]

The encoder maps arbitrary Gaussian coefficients bijectively onto `B_r`.
For the source's Gaussian butterfly

\[
 C(a,b)=\bigl((a+b+i(a-b))/2,\ (a+b-i(a-b))/2\bigr),
\]

its coefficient action becomes the integral update

\[
 E_1^{-1}CE_1:(c_0,c_1)\longmapsto(c_0+c_1,ic_1).
\]

[PROOF.md](PROOF.md) establishes four linked statements.

1. **Exact maximality.** `B_r` is exactly the Gaussian-integral entrance on
   which every partial coordinate product `C_T` remains Gaussian integral.
   It is consequently the largest integral module invariant under every
   coordinate `C_j`. The proof is Boolean Möbius inversion of
   `(C_T f)(0) = sum_(S subset T) a_S/pi^|S|`.
2. **Literal signed-floor exactness.** The credited lifting pair agrees with
   the ideal butterfly exactly when `pi` divides the input difference.
   The domain invariant supplies this condition at every prefix, including
   negative integers. This all-input argument is separate from basis testing.
3. **Phase and address closure.** The module is preserved by invertible
   binary affine address maps and input-address phases
   `i^(p + sum l_j x_j + 2 sum q_jk x_j x_k)`. Explicit integral coefficient
   formulas cover address XOR, SWAP, CNOT, S and CZ, with their inverses.
   All four actual source wrappers have precisely this alphabet.
4. **One complete collector.** For five source arrays and an initial query
   in `2^-f B_9`, the literal endpoint is
   `(D,Q,C=0) -> (D,Q + U sum(D),C=0)`, on the same grid. The archived return
   `V` satisfies `VU=I`; no paired-inverse substitution is made.

The maximality quantifier matters. For `f=pi*x0*x1`, each of `C_0 f` and
`C_1 f` is integral, but the composed transform has constant coefficient
`1/pi`. The proof therefore concerns every partial product, rather than
individual entrance tests or arbitrary completed-word cancellations.

This domain also has a precise relationship to the preceding work. Ross
Richardson's PR3068 structured phase witness `(1,i)` belongs to `B_1` and
executes exactly here. That changes the phase-closure premise. It does not
establish a global containment of the earlier Gamma/Lambda period lattices.

## Exact source and collector boundary

Scientific base: `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6.
[SOURCES.json](SOURCES.json) contains Git blobs, SHA256 digests, predecessor
heads and attribution. The twelve declared inputs include all executed or
authenticated source files and the retained source notices. The selected
record and originating task catalogue are historical provenance.

| Source | Exact role |
|---|---|
| ywz65 / PR2586, `7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1` | The literal 5,398-event word and native recipes, preserved by the rounded-collector archive |
| Tekalign / PR3025, `a544ef068a46f4de3bc47d1d02149cbdc3ba547f` | Signed-floor pair, source phase convention, in-place wrapper algorithm and earlier scalar invoice |
| Ross Richardson / PR3068, `7d2c519a1fdcc6bf66f6f08757eed7c48762d3f2` | Period-domain contract and the phase/exactness handoff motivating this changed scope |

The consumed interval is **zero-based events 2025–2039**. The verifier binds
both unique native occurrences, at 2031 and 2033, and checks the word's frame
and private-lifetime syntax through event 2039. That structural prefix check
does not execute the preceding arithmetic or establish its numerical domain.

| Item | Contract |
|---|---|
| Address space | 512 complex entries, nine binary address bits |
| Borrowed sources | D31, D30, D29, D28, D27; arbitrary within `2^-f B_9`, unchanged locally |
| Source frame | `[256,136,64,40,16,4,2,1]` |
| Mutable query | Arbitrarily dirty Q7 in `2^-f B_9`, frame `[364]` |
| Private C | Owned zero array, allocated at 2025 and checked zero before erasure at 2039 |
| Numerical word | Five gathers, rank-seven U, one query ADD, separately archived rank-seven V, five ungathers |
| Distinct roles | Source, query and private ownership remain separate; physical delivery is an external premise |

## Evidence and reproducibility

The retained [RECEIPT.json](RECEIPT.json) is reproduced in full, including
implementation hashes. The verifier compiles the captured source bytes
directly and rejects implementation changes during replay. It authenticates
external bytes before executing the predecessor differential oracle.

The primary implementation checks 2,450 signed pair cases, 1,234 generator
intertwiners at ranks one through four, four dense signed collector entrances
with every event/native prefix checked, and a complete optional cold codec
call. It compares the actual source's ideal and literal kernels on all array
entries. Its frame, source, ownership, cleanup, domain and invoice controls
fail explicitly under Python optimization.

[independent.py](independent.py) was initially implemented before its author
read the primary model or proof. It imports no predecessor executable and
uses a Newton/Möbius encoder plus a separate rational numerator oracle.
[INDEPENDENT.md](INDEPENDENT.md) documents its derivation and limits. It checks:

- All **512 complex columns** of the actual ideal U followed by V.
- All **1,024 signed real/imaginary encoder columns** through literal U and V,
  with **3,670,016** pair-level exact comparisons.
- Every address and phase of all four wrappers, their inverse permutations,
  and their actual cycle counts.
- Three further dense signed collectors, with source preservation, query
  equality and literal private erasure; wrong return and wrong phase controls
  preserve the lattice but fail the endpoint.

The combined checks retain controls for individual-gate versus partial-product
integrality, the admitted old phase witness, encoder intertwiners,
out-of-alphabet cubic phase, quarter division and unjustified codec commutation.
This is separate automated derivation and checking within one assisted
contribution. Independent human review and formal proof-kernel checking remain
unperformed.

From a checkout containing the declared sources, using standard-library Python:

```sh
python3.12 -B scripts/research_package.py --package research/p104-clifford-exactness --check-only
python3.12 -B scripts/research_package.py --package research/p104-clifford-exactness
```

The registered manifest runs the complete replay normally and under `-O`,
with a 300-second cap per command. A source-complete export needs neither Git
nor network for the mathematical replay:

```sh
python3 -I -B research/p104-clifford-exactness/verify.py
python3 -I -O -B research/p104-clifford-exactness/verify.py
```

The standalone checker accepts `--repo /path/to/source-root`. The generic
metadata checker separately needs Git provenance and the original catalogue;
a Git-free mathematical PASS does not claim that metadata operation ran.
Native compiler, full selected-baseline, whole-word arithmetic and recursive
supplier replays are outside this local result.

## Complete local accounting and remaining prices

The direct invoice prices the specified in-place numeric schedule. Functional
Python copies, membership checks and verification snapshots are instrumentation.
A production caller must either establish the entrance precondition or pay
for its validation. Address plans, control/tape work and physical routes need
their actual implementation tariff.

| Direct collector item | Exact count |
|---|---:|
| Unit whole-array ADDs | 11 |
| Signed-floor pair applications | 3,584 |
| Real additions/subtractions, including the eleven ADDs | 39,936 |
| Floor halvings | 14,336 |
| Pair quarter turns | 3,584 |
| Actual wrapper unit phases | 2,048 |
| Actual wrapper cycles | 416 |
| Actual wrapper Gaussian swaps | 2,464 |

The four cycle counts are `[64,128,160,64]`. PR3025's different paired-inverse
schedule would give 384 cycles and 2,432 swaps. A rejecting invoice control
prevents those counts from being used for the actual archived V. The proof
and receipt retain component reads/writes, zero initialization/checks, source
access subtotals, one owned C bank, one Gaussian wrapper scratch and pair work.

One nine-bit encoder or decoder has **2,304 pair steps**. The optional cold
coefficient call preserves five borrowed inputs by creating five owned copies,
encoding those copies and the mutable query, executing the collector, decoding
all six fields, and uncopying the five source banks to zero. In addition to
the direct collector it needs:

- Six encodes and six decodes: 110,592 real additions/subtractions and
  27,648 exact real halvings.
- Five copy ADDs and five cleanup ADDs: 10,240 more real additions/subtractions.
- Five additional owned banks: 2,560 complex words, with explicit initialization,
  zero checks and the component traversal counts in the receipt.

The endpoint is `q + E^-1 U E sum(D)`. The package does not identify this with
an existing caller requesting U. The conversion is constructive and fully
counted in the direct numeric currency; its logical compatibility and physical
price still have to be established by a consumer.

Finite headroom is explicit. For entrance component bound H, encoding has
conservative component bound `3363 H`, a direct admitted collector has native
prefix bound `160 H` and query bound `161 H`, and decoding has factor 32.
Composing the optional cold schedule gives query bound `17326176 H` and
conservative scratch bound `69304704 H`. These are sufficient range bounds,
with signed storage and primitive bit costs still to be charged.

| Family-level obligation | Status in this contribution |
|---|---|
| Fixed local word, source bytes, frames and clean private endpoint | Supplied under the stated entrance contract |
| Every literal phase/native prefix is exact | Proved on `2^-f B_9` |
| Codec identity, borrowed-source strategy and direct numeric bill | Supplied for the explicit conjugate logical map |
| Earlier producer supplies B_9 at this cut | Unproved |
| Later quarter ADDs preserve the required domain | Require source in `4 B_r`; not automatic |
| Native backend, physical owners, routing, control tape and precision admission | Unpriced or inherited; no admission claimed |
| Favorable complete consumer or supplier moment | Unknown |

The stopping decision is to retain this theorem and one complete collector
contract. An expansion needs an actual compatible producer/consumer and its
whole bill. No claimed saving is available for that consumer to inherit for
free.

## Task selection and coordination

This is a handoff-first, changed-scope continuation of the `p104-side-correction`
card, using PR3068's state-exactness question. The original card, seed, scope
key, source checkpoint and overlap limits are retained in [TASK.json](TASK.json).
The advance claim is
[Discussion2750 comment19008062](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19008062).

At entry the check covered all 276 open PR records and 332 visible Discussion
records across twelve relevant threads, plus targeted P104/lattice/coding terms.
Discussion pagination and sparse local-package coverage were incomplete;
unpublished work was not inspected. Existing grid thresholds, period-index
studies and generic min-cut/frame optimizers were identified and left outside
this result. The card's baseline orientation command could not complete in
the sparse checkout because its selected assembly input was omitted; no
baseline PASS or selected-construction failure is inferred.

## Open next questions

1. **Can a real preceding producer supply this entrance?** This matters because
   local exactness has value only when the required states reach the cut. The
   first step is to trace one actual source producer's Newton divisibility,
   including every coefficient division, and price any required preparation.
   Arbitrary prior arithmetic and physical source availability are the blockers.
2. **Can an actual next consumer retain the representation?** Bind one real
   downstream operation, its frames and requested map. For a quarter source,
   prove membership in `4 B_r` before dividing; for coefficient coordinates,
   prove the required intertwiner. Full caller compatibility is currently open.
3. **Can a complete physical implementation improve the bill?** Combine a
   proven producer/consumer with the paid Gaussian-monomial and arithmetic
   backend, retained storage, control tape, precision and cleanup costs. Until
   those contracts are bound, there is no favorable recursive or supplier
   moment to compare with the selected construction.

## Credit and license

Prepared by Clear1nsight with substantial OpenAI assistance, including three
concurrent agents for algebra, independent reconstruction and source/cost
review. Apache-2.0. Original headers, LICENSE, NOTICE, upstream/LICENSE and
source-specific READMEs are retained in the declared export closure.

Credit ywz65/PR2586 and the native P104 lineage; Arham Tahir/PR2665/2999 and
numerical-boundary work; Tekalign/PR3025/3033; Ross Richardson/PR3068 and the
sharp Clifford-grid method; Nick Petalas/PR2754/2771/3035/3037; Arham Tahir's
PR3046; Alejandro Zarzuelo Urdiales's Gaussian parity work; and the retained
geometry/compiler lineage, including Chafik Boukhalfa/PR628. Jose Manuel's
PR3087 physical Gaussian monomial implementation is related context, with
its separate physical assumptions and costs retained.

Classical inspiration: Nebe, Rains and Sloane,
[The invariants of the Clifford groups](https://arxiv.org/abs/math/0001038) and
[A Simple Construction for the Barnes-Wall Lattices](https://arxiv.org/abs/math/0207186).
The application, exact source contract and executable checks here are the
claimed contribution; those classical constructions retain their authorship.
