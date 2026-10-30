# Changed complex interfaces: exact objects and their complete child prices

This scope contains three constructive interface experiments and one finite
producer screen. **None supplies an additional admitted κ increase.** The most
substantial new object replaces two rank-four transforms by two rank-two
transforms and an exact, nonmonomial two-bank correction. The correction works
on arbitrary dirty data and has an exact tensor identity. Paying it as an
ordinary native child changes the bill from `2 H4` to `4 H2`, which loses.
Implementing it with the explicit scalar/translation circuit instead requires
a number of bulk passes growing with tensor multiplicity. This identifies a
specific surviving resource question after changing the interface, rather than
assuming the disputed moved-axis overlay is correct.

All earlier scopes and public sources remain unchanged. These experiments use
the legitimate adaptive `BORROW-WORD-43base.json.gz`; the paired-phase price
uses the newer, separately admitted composed T360 invoice. The two word
variants are distinguished in the receipts. All source paths are relative to
the repository root and are bound by SHA-256.

## 1. A literal partial capture of the agreeing consumers

The retained helpers 600 and 601 have the same entrance frame `span(45)`. In
consumer order `(123, 175, 183, 202)`, their early columns, after removing a
common factor `1/4`, are

| Helper | 123 | 175 | 183 | 202 |
|---|---:|---:|---:|---:|
| 600 | −1 | +1 | +1 | −1 |
| 601 | +1 | +1 | +1 | +1 |

`partial_capture.py` constructs the interface explicitly. At their common
entrance it sets `600 += 601`. Consumers 175 and 183 now read only helper 600.
Consumers 123 and 202 read `−600/4 + 601/2`. After these early observations it
executes `600 -= 601`, before either helper's later production. The exact
inverse cleanup is regenerated.

The resulting full word is retained at `partial-capture/WORD.json.gz`.
All 632 independent signed input columns and all 91 private zero buffers
satisfy the original free-operator identity, before and after joint frame
optimization. The optimizer examines its full containment graph and changes
no frame. The profile is exactly

```json
{"1":2439,"2":724,"3":225,"4":102,"5":20,"8":8}
```

The two saved TARGET reads are offset by four encoding/rollback/cleanup ADDs:
the literal scalar bill increases by two ADDs. Both helpers and every paid
child remain. This is a legal, exact partial capture with a neutral exponent
profile. It settles this particular rollback implementation of the partial
capture suggested by PR4061; it does not exclude a changed later production
or a different observation interface. A fresh physical caller build was not
run for this profile tie.

## 2. Keeping a changed quartet basis through production

`matched_basis.py` changes the assumption that each original helper column
must remain individually visible. It applies a dyadic matrix `M` at the common
entrance of helpers `(600,601,602,604)`, then conjugates every later producer
and consumer by `M` and `M⁻¹`, including restore and inverse cleanup. Adjacent
updates are combined only when they commute at the same frame.

The finite family contains 86 distinct interfaces: the identity, 72 elementary
shears with coefficients `±1, ±1/2, ±2`, 12 two-helper Hadamards, and one
four-helper Walsh basis after removing signed row-permutation duplicates.
Every interface passes the exact arbitrary-dirty operator check. The identity
has the original profile; all 85 nonidentity interfaces fail the native frame
containment constraints. The receipt records an explicit infeasible node and
its incompatible lower and upper frames for each failure.

This failure happens after preserving the actual operator. For example, a
mixed helper can inherit producer directions whose span is the full space,
while its later TARGET observation still requires a proper hyperplane. The
native frame solver then has no admissible frame for that node. This is a
finite-family result with fixed original TARGET endpoints and the stated
basis placements. It is not a theorem against arbitrary coupled encoders or
changed endpoints. The complete cases are in `quartet-base/RESULT.json`.

The auxiliary `warm_producer.py` screen changes later B production after its
early dirty observations. It protects SOURCE, TARGET, wrapped inputs and all
nonzero-entrance dirty inputs, and permits only the previous exact correction
interface for zero-entrance, full-exit helpers. Of 104 warm helpers, 52 do not
have a multi-write producer in the selected interval. For the other 52, the
fixed ordered rational elimination does not return an accepted dyadic witness
from compatible donors at the selected last-write frame. No candidate reaches
the favorable-price gate. The `no_dyadic_protected_span` label in its receipt
means this exact solver outcome; alternate free-variable choices and broader
interfaces have not been excluded. See `warm-producer-base/RESULT.json`.

## 3. An exact two-bank rank reduction

Use the native convention

\[
C_v=\frac{(1+i)I+(1-i)X_v}{2},\qquad
\widehat C_v(\chi)=i^{\chi\cdot v\bmod2}.
\]

In the canonical rank-four interior of a native child, write the four
character coordinates as `x,y,z,w`. The desired multiplier is
`i^(x+y+z+w)`. The two orthonormal axes `1110` and `0001` give the rank-two
multiplier `i^((x⊕y⊕z)+w)`. Their ratio is

\[
(-1)^{xy+xz+yz}
=(-1)^{(x\oplus y)(y\oplus z)+y}.
\]

Let `a=x⊕y`, `b=y⊕z`. Use the two existing data banks as a two-dimensional
label; no bank is assumed clean. Define

\[
H=\begin{pmatrix}1&1\\1&-1\end{pmatrix},\quad
Z_b=\begin{pmatrix}1&0\\0&(-1)^b\end{pmatrix},\quad
X_a=HZ_aH^{-1}.
\]

`Z_b` is a coefficient translation of the second bank. The dyadic `H` and
`H⁻¹` are two ADDs and one scale each. On a character, `X_a` is identity for
`a=0` and swaps the two banks for `a=1`. Therefore

\[
X_aZ_bX_aZ_b=(-1)^{ab}I_2.
\]

Translate both banks by the second axis to supply `(-1)^y`. Composing this
correction with the two rank-two transforms gives exactly two rank-four
transforms, with the correct global phase and arbitrary values in both banks.
This genuinely changes the interface: the intermediate operator mixes the
two banks nonmonomially.

`paired_phase.py` independently executes the literal Gaussian-dyadic bulk
gates on all 32 coefficient basis inputs at tensor multiplicity one. It also
checks all characters at multiplicities one, two and three: 16, 256 and 4,096
characters, respectively. Omitting the final common translation fails every
coefficient column at multiplicity one and half of the characters at every
tested multiplicity.

The experiment binds this canonical identity to the actual quartet
transition from `span(45)` to `span(409,80,40,5,2)`. It derives the retained
left and right monomial wrappers with the pinned exact native compiler and
compares all 512 native columns, including global phase. The entrance vector
45 is not presumed orthonormal: the paired construction operates inside the
compiler's canonical rank-four interior. Applying the same exact replacement
inside the unchanged wrappers proves the corresponding paired residual
identity. No full supplier is nominated from this local identity.

## 4. Tensor correctness and the bill that defeats the saving

For tensor multiplicity `f`, the exact missing multiplier is

\[
\widehat K_f(\chi)
=(-1)^{\sum_{t=1}^f[
(\chi_{1,t}\oplus\chi_{2,t})
(\chi_{2,t}\oplus\chi_{3,t})+\chi_{2,t}]}.
\]

One commutator per tensor factor supplies this multiplier on both banks. The
identity for each factor is symbolic, so the all-size operator statement is
not inferred solely from the finite checks. The literal fixed-two-bank bill
is `8f` bulk ADDs, `4f` scales and `4f+2` one-bank translations. The last two
translations combine the separate linear phases into one translation vector
on each bank. All scalar coefficients are dyadic.

Here the sign is **diagonal in Fourier coordinates**. In coefficient
coordinates it is a convolution. Exact integer inverse Walsh transforms show
four nonzero coefficients of magnitude `1/2` per row at `f=1`; tensoring gives
`4^f` nonzero coefficients of magnitude `2^(−f)` per row. Consequently it is
not a coefficient-wise streamed sign, a permutation, or a monomial operator
`D P D†`. Gray-code evaluation of a coefficient-index sign does not implement
this Fourier-index sign.

This support argument is not a general arithmetic-circuit lower bound. In the
restricted model of whole-bank binary ADDs and monomial routing, a row support
can at most double per ADD depth, so the correction requires at least `2f`
mixing levels. The displayed implementation has a growing number of full
bank passes. Its runtime and prefix precision must be charged; it cannot be
assigned the constant linear overhead used by the retained recursion merely
because `f=1` is cheap. An implementation outside that bulk model remains a
separate question.

There is a complete uniform native implementation: the exact Clifford
compiler gives `K₁` native rank two, and its tensor rank is `2f`. Paying that
correction on each bank turns the child bill into

\[
2H_4 \longrightarrow 4H_2.
\]

For `H_r=r^(1−a)` and any positive `a`, its increase is
`4·2^(1−a)−2·4^(1−a)>0`. The rank mass returns to the original value; splitting
the rank among additional children loses the concavity saving.

The exact price in `paired-phase/RESULT.json` uses the equivalent normalized
units `H_m(r)=r·(m/r)^a`, with `m=73`, `a=349/200000`, 3,240 local calls and
322,560 productive families. The composed baseline exceeds the target by
`946.54819491625849` normalized units globally, or
`0.29214450460378349` per call. These numbers equal the raw `r^(1−a)` excess
times `73^a`; the corresponding raw global excess is approximately
`939.48799125824555`.

If the essential correction were omitted, the optimistic `2H4→2H2` arithmetic
would cross the target, with global excess about `−12063.53`. This is explicitly
not an operator-correct supplier. Paying the normal rank-two correction gives
global excess `978.07786804447206`, an additional cost of
`0.0097313805951276433` normalized units per call. The favorable screen keeps
all owner and stock costs fixed. Additional routing, child-count fallback and
precision costs cannot reverse this losing sign. No κ is promoted from either
version.

## 5. The surviving construction question

The exact paired identity isolates a changed premise with enough arithmetic
scale: a coupled adapter would need to realize the Fourier-quadratic correction
with a uniform favorable bill, or interleave the native queries and the
production/observation interface so that a separately paid rank-two correction
is unnecessary. The explicit two-bank commutator does not provide that bill.
The finite basis and rollback experiments explain why simply mixing these
four existing helpers, while retaining their present later endpoints, has not
produced it. They do not exclude a new coupled native macro, new slots, changed
TARGET interfaces or a different production graph.

## Replay and attribution

From the repository root, use fresh absolute output directories:

```sh
python -B research/kappa-operator-repair/complex-architecture/partial_capture.py --output /tmp/complex-partial-fresh
python -B research/kappa-operator-repair/complex-architecture/paired_phase.py --output /tmp/complex-paired-fresh
python -B research/kappa-operator-repair/complex-architecture/matched_basis.py --output /tmp/complex-basis-fresh
python -B research/kappa-operator-repair/complex-architecture/warm_producer.py --output /tmp/complex-producer-fresh
```

The quartet search records elapsed seconds; compare its scientific fields and
source bindings rather than expecting byte-identical timing. Other receipts
are deterministic for their pinned sources. The scripts require only Python's
standard library and the files listed in `REPLAY-DEPENDENCIES.json`.

The adaptive supplier and its native lineage retain the credited work of
Rohan Arun, Jeremy Diviney and their predecessor authors. PR4061 by Riquelme
Soares supplied the exact signed consumer comparison and partial-capture
question. PR4045 by Chris R supplied the paid joint-interface analysis and the
pinned exact residual/compiler lineage, including PR2226 and the native
Clifford compiler credited there. The operator and dyadic tensor-cost
distinction also builds on the explicit warning in PR3989. This scope's
matched-basis experiment, warm-producer screen, literal partial rollback and
paired commutator were developed with substantial OpenAI assistance. These
are exact executable experiments and mathematical arguments, not independently
human-reviewed or proof-kernel-certified results. New material is Apache-2.0.
