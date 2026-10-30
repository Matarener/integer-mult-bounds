# Actual P104 Newton producer and downstream interfaces

This package answers the three explicitly assigned open questions of
[PR #3382](https://github.com/CrocSwap/integer-mult-bounds/pull/3382), frozen
head `2834523b1cd4ea83ba7a043e2e2f5f3332cf9909`. It binds the Gaussian Newton
representation to the actual producer and downstream operations of the first
P104 collector, proves the restored internal endpoint, retains every outgoing
read, and gives the complete direct logical bill and its physical obligations.
The selected frontier is unchanged.

The presubmission overlap check found Nick Petalas's complementary
[PR #3406](https://github.com/CrocSwap/integer-mult-bounds/pull/3406), exact
head `18a054fd585ab4b2010770ec83cba0c9f28184e3`. It classifies the whole-word
independent-product entrance, with 104 Y inputs in `4B9` and 78 N inputs in
`2B9`, while retaining the native change-of-chart identities as a premise.
It explicitly links our active local-interface claim. The new evidence here
is the independently certified finite frame paths, actual producer and
consumer join with every outgoing port, reachable exact counterexample, and
complete direct bill. PR #3406 is credited pending context; its broader suite
is not rerun or claimed as this package's result.

| Assigned question | Answer on this scope | Evidence |
| --- | --- | --- |
| Can the actual producer supply the collector's `B9` entrance? | Yes when all 52 named initial Y banks are in `4B9` and the six dirty D/Q entrances are in `B9`. This condition is necessary and sufficient for the specified prefix invariant. Initial `B9` alone fails on an explicit reachable input. | [PRODUCER.md](PRODUCER.md) |
| Can the actual downstream consumer preserve the representation and requested map? | Yes for the 63-bank open program through event 4516, with five additional dirty G inputs in `B9`, exact native frame paths and explicit coefficient intertwiners. External recipient histories remain separate. | [CONSUMER.md](CONSUMER.md) |
| Does this establish an improved complete physical bill? | The direct logical bill and conservative internal widths are now explicit. Physical caller admission and tariffs remain open. The inherited unchanged five-forward/four-dual consumer still fails its favourable screen at `599/584`. | [COMPARISON.md](COMPARISON.md) |

## Source and exact boundary

The scientific base is canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`. The actual word and native recipes
come from ywz65's [PR #2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586),
head `7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`, retained in
`research/p104-rounded-collector/inputs/WORD.json` and `NATIVE.json.gz`.
[SOURCES.json](SOURCES.json) pins these bytes, the copied PR #3382 model/proof,
the budget source and the contextual predecessors.

Every bank has 512 Gaussian entries indexed by nine bits. The source chart is
`Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)`. All event numbers below are
zero-based. Put

\[
 \mathcal Y=\{22,\ldots,32\}\cup\{63,\ldots,103\},\qquad
 \pi=1+i,
 \qquad E=\begin{pmatrix}1&0\\1&\pi\end{pmatrix}^{\otimes9}.
\]

PR #3382's module is
\(\mathcal B_9=E\mathbb Z[i]^{512}\), equivalently the arrays whose Newton
coefficient at subset \(S\) is divisible by \(\pi^{|S|}\). The actual
butterfly and affine/quadratic Gaussian wrapper alphabet preserve it. We use
one common grid `2^-f`; the formulas below use its Gaussian integer numerators.

The admitted persistent state is:

| Initial banks, all at frame `[]` | Count | Numerical domain |
| --- | ---: | --- |
| `Y22`–`Y32`, `Y63`–`Y103` | 52 | `4B9` |
| `D27`–`D31`, `Q7` | 6 | Arbitrary dirty `B9` |
| `G27`–`G31` | 5 | Arbitrary dirty `B9` |

Private `C` is owned zero at event 2025 and literally zero before erasure at
2039. The 63 persistent banks undergo **576 actual internal events** through
4516. Every outgoing read is retained as one of **675 ADD ports**, giving
**1,251 retained events and ports**. The omitted external histories are not
numerically executed by this open program. No physical ownership or aliasing
permission follows merely from these distinct numerical bank names.

## 1. The producer theorem and a reachable failure

Backward dataflow from the five D entrances and Q7 at event 2025 gives a
**257-event dependency cone**, with 58 initial dependencies, 200 native
transports of total rank 354, 52 quarter ADDs and five initial-D subtractions
from Q7. Each named Y bank is read once into exactly one of the five D banks;
the D31/D30/D29/D28/D27 source group sizes are **3, 7, 7, 11 and 24**.

The actual Y paths are invertible on both `B9` and `4B9`. Their quarter
contributions therefore lie in `B9` exactly when the corresponding initial
Y belongs to `4B9`. With initially admitted D/Q banks, all 52 stronger Y
conditions are necessary and sufficient for membership after every tracked
event and completed native layer. This is a prefix-invariant characterisation;
it does not classify additional final-cut admissions obtained by cancellation.

The weaker initial contract is false even when arithmetic remains exactly on
the grid. Set **`Y27[0]=64`** and every other initial component of all 358
persistent source banks to zero. Every initial bank lies in `B9`, while Y27
fails `4B9`. The actual full prefix through event 2024 remains arithmetically
exact. At the collector entrance,

\[
 D31[8]-D31[0]=-1,
\]

so its degree-one Newton coefficient is not divisible by `1+i`. This supplies
an actual producer failure, rather than an arbitrary value invented at a later
quarter site. The separately implemented full-prefix replay agrees with the
producer's valuation certificate: **20 active native calls and six active
quarter reads**. Amplitude 256 supplies the positive control.
[PRODUCER.md](PRODUCER.md) gives the quantified theorem, precise source paths,
counterexample and controls.

## 2. The downstream endpoint, outgoing reads and actual intertwiners

The consumer authenticates the operator paths for all **392 retained native
occurrences**, covering **163 frames and 230 redundant path equalities**.
It compares the exact action on all 18 Pauli generators and a nonzero dyadic
anchor vector. The generator images fix an operator up to scalar; the anchor
fixes its global phase. A changed return phase that preserves every Pauli image
is explicitly rejected. Both literal archived U and V are covered.

Let \(A_H\) denote the resulting source-bound operator from the empty frame
to frame \(H\), and set

\[
 O=[256,136,64,40,16,4,2,1],\quad Q=[364],\quad
 F=[256,128,64,32,16,8,4,2,1],\quad
 s=\frac14\sum_{j\in\mathcal Y}Y_j^0.
\]

The literal collector produces \(Q_7=A_Q(Q_7^0+s)\) and restores `C` to
zero. The real D cleanup quarters, G reads and later unit subtractions, and
Q7 cleanup quarters give, at the last relevant event 4516,

\[
 b^{\rm final}=A_F b^0
 \quad\text{for every one of the 63 persistent banks}.
\]

Thus the initial values are restored in the authenticated final-frame
coordinates. Physical arrays at two different frames are not claimed equal.
The finite path certificate also proves

\[
 A_F=(C^{-1})^{\otimes9},\qquad
 E^{-1}A_FE=
 \begin{pmatrix}1&i\\0&-i\end{pmatrix}^{\otimes9}.
\]

Every outgoing side effect remains in the interface and the bill:

| Source read | Outgoing ports |
| --- | ---: |
| Y to other D banks | 348 |
| Y to other Q banks | 171 |
| G to X | 104 |
| Initial Q7 to X, events 492–543 | 52 |
| **Total** | **675** |

For each port at frame \(H_e\), its literal increment \(\delta_e\) is
retained. Normalising each X-port increment by its own authenticated frame
map gives

\[
 \sum_{e\to X_t} A_{H_e}^{-1}\delta_e
 =\frac{\epsilon_t}{2}\sum_{j\in\mathcal Y}Y_j^0,
 \qquad\epsilon_t\in\{+1,-1\}.
\]

There are 39 positive and 13 negative target signs; all dirty D/Q/G
coefficients cancel. The resulting **52-by-52 bank-coefficient matrix has
rank one**; expanding the 512 entries of each array gives rank 512 over
\(\mathbb Q(i)\). This is a frame-normalised outgoing-port operator.
A final physical X-bank claim also needs its omitted updates and transports.
The other 519 Y ports remain separately retained.

Each port increment belongs to `B9`. Its ADD is exact for any current Gaussian
recipient, and preserves `B9` when that recipient is currently in `B9`.
An external recipient's initial admission and future native operations require
their own proof.

The coefficient-coordinate map is explicitly \(E^{-1}AE\). The checker
derives all 512 columns for the actual empty-to-Q and empty-to-F maps, with
12,288 and 19,683 nonzero entries respectively. Their distinction from the
unconjugated numerical map is visible on one input: the first coordinate of
\(E^{-1}A_QE e_0\) is 1, while that of \(A_Qe_0\) is \((1-i)/2\).
Persistent coordinates remove intermediate codec pairs only under this
compatible logical contract. Arbitrary-input preparation and exposed port
adapters still need to be supplied and charged.
[CONSUMER.md](CONSUMER.md) proves these statements and records the complete
source/frame conventions.

## 3. Complete known costs and the inherited stop

[COMPARISON.md](COMPARISON.md) reconstructs every retained operation and port
from the frozen word. The minimal 257-event producer is already included in
the 576 internal events and is not counted again.

| Work for the complete open program | Direct logical count |
| --- | ---: |
| Native signed-floor pair applications | 148,736 |
| Actual wrapper executions | 784 |
| Wrapper cycles / Gaussian scratch swaps | 23,822 / 425,230 |
| Wrapper unit-phase applications | 401,408 |
| Field ADDs, including all ports | 857 |
| Real additions/subtractions, before doublings | 2,067,456 |
| Additional real doublings | 159,744 |
| Native real floor halvings | 594,944 |
| Exact real halvings for the quarter ADDs | 1,382,400 |

Component traffic, private initialization/zero inspections, wrapper setup and
the numerical storage inventory are also retained. If every initial component
is bounded by integer `H`, a conservative unitary-norm/triangle proof bounds
internal payload by **1568H**, literal pair work by **7840H**, and each outgoing
increment by **1600H**. A current target bound `H_target` still requires capacity
for `H_target+1600H`; the increment bound does not price or bound the recipient's
omitted history.

These are direct logical counts and constructive width bounds. The complete
physical caller still owes the 52 strengthened Y admissions; actual incoming
heights, external targets and representation adapters; ownership, record layout,
routing, control and scratch cleanup; and all recursive/outer-completion costs.
The logical array inventory is not a physical allocation theorem. Unknown
charges are not assigned zero, and PR #3382's six-bank codec is not the cost of
this 63-bank interface.

For the unchanged consumer, an existing favourable screen already stops
expansion. Retain width 73, 832 original live families, the exact five PR #2458
forward and four PR #2712 or PR #2725 dual profiles, the 3,014-unit persistent
credit per call and remaining coverage mass 32,778. For `0 <= a < 1`, every
finite number `B` of fully paid auxiliary banks obeys

\[
 M_B(a)\ge
 \frac{5\cdot3070+4\cdot3542+32778+73B}{73(832+B)}
 =1+\frac{1560}{73(832+B)}>1.
\]

At `B=0` this is **599/584**. This inherited result is credited to Jose
Manuel's [original finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/2619#discussioncomment-18955566)
and Vasek's [PR #2744 audit](https://github.com/CrocSwap/integer-mult-bounds/pull/2744).
It is conditional on those exact profiles and coverage hypotheses. The local
representation theorem does not change them or establish a universal P104
obstruction.

The family decision is to retain this source/consumer result and stop supplier
expansion aimed at a new selected saving with that unchanged consumer. A
concrete changed profile, coverage law or caller must first supply and pass its
own compatible, fully charged favourable screen.

## Evidence and reproduction

The package combines written admission/restoration proofs, exhaustive finite
operator certificates, separately written exact interpreters and bounded dense
fixtures. [RECEIPT.json](RECEIPT.json) binds their implementation/source bytes
and outcomes. In particular:

- The producer verifies its actual dependency order, reachable counterexample
  and strengthened-domain positive controls using the authenticated PR #3382
  model.
- The consumer imports no producer or predecessor numerical model. It proves
  the actual frame-path equalities, reconstructs the two coefficient maps, and
  checks 148,736 literal/ideal pairs and all 675 source increments on a dense
  signed 63-bank fixture.
- `independent.py` separately replays the full-prefix counterexample and the
  Fraction-valued scalar port rows. The cost audit independently reconstructs
  the complete event/port inventory, actual wrapper counts and rational bounds.
- Controls reject source drift, swapped or omitted producer reads, a changed
  quarter coefficient/sign, and a globally phased return invisible to Pauli
  actions. Separate exact controls distinguish the conjugated and unconjugated
  maps and expose the false favourable screen caused by unpaid auxiliary-bank
  denominator credit.

Independent here means separately written automated checks and cross-review;
substantial AI assistance is disclosed. The source-bound finite operator proof
and quantified module argument are distinguished from the dense fixture, which
does not establish arbitrary-input or all-size physical execution.

From the repository root, run:

```sh
python3 -B research/p104-newton-interfaces/verify.py
python3 -B -O research/p104-newton-interfaces/verify.py
```

The same commands apply at the root of the source-complete export. Runtime
requires standard-library Python and the files pinned in
[SOURCES.json](SOURCES.json), preserving repository-relative paths; replay needs
no Git, network or native compilation. [VERIFY.json](VERIFY.json) records the
replay contract, and [TASK.json](TASK.json) preserves the explicit assignment,
overlap coverage, checkpoint evidence and stopping decision. Context-only
sources are identified separately in `SOURCES.json.context_sources` and are
not runtime dependencies.

The two package-local PR #3382 files are retained byte for byte and checked
against fixed SHA256 values before execution. Their original commit and blob
identities are recorded in `SOURCES.json.retained_sources`. They deliberately
do not require an unmerged predecessor commit in the new branch's ancestry:
the generic provenance gate checks the canonical-base source pins, and the
direct verifier checks these retained bytes. The unchanged predecessor suite
is not rerun, and byte identity does not establish external mathematical review.

## Open next questions

1. **Can the 675 ports be joined to an actual external consumer?** Bind the
   external target updates, frames, reads and widths, then prove the composed
   terminal map. The retained port operator gives exact inputs to that task;
   its frame-normalised X sum does not replace those histories.
2. **Can a changed caller or profile pass a complete cost screen?** Produce a
   compatible input/adaptor contract paying the 52 `4B9` admissions, all exposed
   conversions and physical/recursive charges, and name the exact old-profile
   or coverage premise it changes. Stop if even its favourable relaxation fails;
   a passing relaxation would justify the next admission test, not certify a
   supplier.

## Credit and license

Prepared by **Clear1nsight**, with substantial OpenAI assistance in mathematics,
implementation, verification, source review and prose, including concurrent
analysis agents. Apache-2.0; copied inputs retain their source notices.

Credit remains with **ywz65 / PR #2586** for the corrected dual word and native
recipes; **Arham Tahir / PR #2665** for the retained collector binding;
**Tekalign (`tekuuu`) / PR #3025** for the literal signed-floor pair, wrapper
convention, cycle schedule and logical ledger; **Ross Richardson / PR #3068**
for the period-domain contract and larger-exactness question; and **PR #3382**
for the phase-complete Gaussian Newton theorem and model. Its classical
Clifford/Barnes–Wall coding context is inherited, not claimed as a new lattice
family here.

The `599/584` finding and audit retain **Jose Manuel (`jmbarrancoml`)** and
**Vasek (`flyingviper`) / PR #2744** credit, with the exact PR #2458, #2712 and
#2725 profiles preserved. Jose Manuel's physical monomial, dense paired
collector and selected-controller work in **PRs #3087, #3131 and #3385** is
inspected context with its own retained assumptions; it is not imported as an
admission of this changed caller. Exact predecessor heads and context-source
hashes are recorded in [SOURCES.json](SOURCES.json) and
[COMPARISON.md](COMPARISON.md).
