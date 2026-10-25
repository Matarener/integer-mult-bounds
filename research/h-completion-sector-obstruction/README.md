# One fixed native edge obstructs every completion-only fresh H inverse

**Submission authorized by the user on 2026-10-21.**

The complex H branch in [PR4359](https://github.com/CrocSwap/integer-mult-bounds/pull/4359)
leaves endpoint monodromies that cannot be discarded as free scalar factors.
Its existing fresh-axis probe tests one particular H. This note extends that
obstruction to **every invertible selected-row completion**, including
non-scalar completions and the inverse matrices used by reverse calls.

Only one ordinary matrix entry is needed. In the actual native owner chart,
the fixed entry `G[1,2] = -1/2` sends

```
input:  role 2, address 512   (first fresh block label 512)
output: role 1, address 9235  (first fresh block label 9216)
coefficient: -1/2.
```

Changing any of the eight selected completion rows cannot change this edge.
Neither can using the completed matrix's inverse eliminate the sector
obstruction. Any completed inverse built solely from operators that preserve
this old block is therefore impossible. A replacement must touch that block,
change the ordinary edge, or change its owner geometry.

This is a **scoped negative result**, not a lower bound on all H decoders,
the 672-query direct repair, BIT constructions, or integer multiplication.
There is no new κ. In particular, a geometry-aware decoder that mixes the old
block remains open. The original selected result and every frozen source are
unchanged.

## 1. Actual operators and the fixed edge

Let `V` be the rational vector space with basis `e_(p,y)`, where
`0<=p<112` is a role and `y` is a 73-bit address. This is the exact
permutation/character representation of the native monomial owners; it does
not replace them by free formal symbols.
Extending scalars to complex coefficients leaves the nonzero witness and
commutator argument unchanged, so permitted complex scalar phases are covered.

The stored query rows `R` give the no-COPY response

\[
J=I-\tfrac14R^TR.
\]

The allowed selected rows are

```
S = {0, 7, 20, 27, 36, 46, 57, 111}.
```

Both roles 1 and 2 are ordinary. Independent reconstruction from the pinned
query rows gives `J[1,2]=-1/2`. Consequently every matrix obtained by replacing
only rows in S retains this entry. The theorem below is stronger: every other
entry of G may be arbitrary, subject to invertibility and this one fixed edge.

For the actual first fresh stage let

\[
\Gamma_p e_y=(-1)^{d_p\cdot y}e_{g_p y},\qquad
\Gamma=\operatorname{diag}_p(\Gamma_p).
\]

Here `g_p` is the binary native owner map and `d_p` its required even Gaussian
phase character. The checker reconstructs these directly from
`DATA-PHASES.json`, rather than importing the predecessor's executable.
The maps and characters satisfy `Gamma_p^2=I`.

In particular, for the witness ports:

```
d_1 = 5636, d_2 = 9732,
g_2(512) = 37,
g_1(37) = 9235,
(-1)^(d_2 dot 512 + d_1 dot 37) = +1.
```

For any rational invertible G with `G[1,2]=-1/2`, define

\[
A(G)=\Gamma(G\otimes I)\Gamma^{-1}.
\]

The displayed coefficient of `A(G)` is exactly `-1/2`. There is **no sum over
other entries of G**: the input has only role 2, the diagonal inner owner
preserves that role, G selects its `(1,2)` entry, and the diagonal outer owner
preserves output role 1. This proves independence from all completion choices.

## 2. A universal obstruction that includes inverse calls

Let `B1` be address bits 9 through 16. Write `Pi` for projection onto the
sector where these bits have value 512, on every role. Thus
`Pi e_(2,512)=e_(2,512)`, while `Pi e_(1,9235)=0` because
`9235 & B1 = 9216`.

The witness gives

\[
\left[\Pi,A(G)\right]_{(1,9235),(2,512)}=\tfrac12\ne0,
\qquad [\Pi,A]=\Pi A-A\Pi.
\tag{1}
\]

This holds for **every** admissible G in the class above. Since G and Gamma
are invertible,

\[
[\Pi,A^{-1}]=-A^{-1}[\Pi,A]A^{-1}\ne0.
\tag{2}
\]

This inverse step matters. The inverse of a general selected-row completion
does not itself retain the ordinary rows of J. Applying the fixed-edge witness
directly to that inverse would be unjustified. Equation (2) supplies the
required conclusion without assuming that false row condition.

For any invertible operators L and R commuting with Pi, and either
`sigma=+1` or `sigma=-1`,

\[
[\Pi,L A^\sigma R]=L[\Pi,A^\sigma]R\ne0.
\tag{3}
\]

Thus `L A^sigma R` cannot be the identity, or any other Pi-commuting endpoint.
This is an exact linear-algebra proof, not extrapolation from a finite menu
of completion coefficients.

### Why fresh stages fall inside this scope

Common-frame scalar role mixing commutes with Pi. Stage zero has identity
owners, so every invertible stage-zero completion does as well.

Every later source owner at stages 2 through 8 acts only on the original
nine coordinates and its own disjoint eight-coordinate block. Its binary
map satisfies

```
projection_B1(g*y) = projection_B1(y).
```

Every diagonal coefficient character also preserves address sectors. Hence
these owners, their inverses, arbitrary common-frame scalar matrices, and
their conjugated complete stage factors all commute with Pi. The checker
verifies this on all 73 basis addresses for all **784** later native charts.
Closure under composition and inversion proves it for every word in these
generators, without a bound on word length or scalar coefficients.

For example, a monodromy `A_2(G_2)^eps2 A_1(G_1)^eps1 A_0(G_0)^eps0`
cannot be inverted by a word using only later fresh stages, if the factors
are invertible and G1 retains the fixed ordinary edge. Both orientations and
arbitrary non-scalar selected-row completions are included.

Initialized and erased owned fields do not create an exception if the
induced completed linear map on the active arbitrary fields preserves these
sectors. If such a map were a genuine inverse of A, the endpoint identity
would force it to be invertible; equation (2) would then apply. A projection
can erase the exhibited leakage, but also destroys independent input data
in that sector. It is not an arbitrary-input inverse.

### Every positive column count

At column multiplicity f, use the basis address `(512,0,...,0)` and output
`(9235,0,...,0)`. The owners lift column by column. Extra zero columns remain
zero and contribute character phase +1. The fixed scalar role coefficient
is still `-1/2`; it is not raised to the f-th power. Therefore (1) holds for
every integer `f>=1`. Let Pi now select block label `(512,0,...,0)` across
these columns. Equations (2) and (3) are unchanged.

This uses the source's all-column monomial interpretation. It does not
infer a physical tape implementation or an all-size multiplication theorem
from a small-column numeric check.

## 3. What this closes and what it leaves open

The earlier `joint_boundary_probe.py` exhibits leakage for one fixed H and
then excludes a fresh-axis inverse for that H. This contribution makes the
fixed ordinary edge the only matrix premise. Searching scalar lambda values,
arbitrary dyadic completion matrices, or longer fresh-only inverse words
cannot escape it while that edge and the owner chart remain fixed.

It does **not** exclude a coupled boundary decoder acting on all endpoint
banks, extra operators mixing B1, a changed ordinary local response, changed
owner charts, or a differently priced producer/consumer interface. It gives
no paid-query count. In particular, it does not promote the predecessor's
672-request direct correction into a universal lower bound.

The current complete-bill ledger is therefore:

| Obligation | Status |
| --- | --- |
| Original exact H completion and signed owners | Predecessor evidence, pinned; only the two witness owners' phase identities are rechecked here |
| Fixed-edge leakage for arbitrary invertible completions | Proved above; source-bound exact witness checked |
| Inverse and unbounded fresh-word obstruction | Proved by commutator identities (2) and (3) |
| All 784 later owners preserve B1 | Exact basis checks; their phase characters cannot change address labels |
| A new old-block-mixing decoder and its restoration | Unknown |
| Its full movement, recursive and scalar cost | Unknown; no zero cost assigned |
| A completed improved H supplier or larger κ | Not established |

Decision: narrow the completion-only fresh-inverse route. Continue only
after naming an actual old-block-mixing operator, ordinary-row change or
owner change and pricing its complete endpoint. No further completion grid
or larger fresh-word search is justified by this result.

## 4. Verification and meaningful controls

From the repository root, Python 3.12 or later, standard library only:

```sh
python3 -B research/h-completion-sector-obstruction/verify.py
python3 -B scripts/research_package.py --package research/h-completion-sector-obstruction --check-only
python3 -B scripts/research_package.py --package research/h-completion-sector-obstruction
```

To write a new receipt rather than comparing the stored result:

```sh
python3 -B research/h-completion-sector-obstruction/verify.py --out /absolute/path/to/new-result.json
```

The verifier authenticates five immutable predecessor inputs. It reconstructs
`R R^t=56I`, the selected Gram identity, `J[1,2]`, and a valid default H with
`H=I+BC`, `CB=-2I`, hence `H^2=I`. It checks all 112 first-stage charts for
invertibility and both witness charts on the complete 154-point quadratic
phase basis. The all-column and universal commutator arguments are written
proofs; they are not claimed as machine-formalized theorems.

The controls exercise changed hypotheses:

- Omitting the signed-owner character fails the exact Gaussian phase contract
  at 56 test points for each witness port. The support obstruction alone does
  not detect that omission; the phase checks do.
- Three unrestricted selected-row perturbations leave the witness unchanged.
  This is a finite sanity check accompanying the one-edge symbolic proof;
  those perturbations need not be invertible native programs.
- Reusing the actual old-block H stage twice restores the complete default
  witness vector. This leaves the fresh-only class, as it must.
- Replacing the ordinary body by identity also removes this witness. It
  changes the mandatory edge and does not preserve the old native invoice.
- A noninvertible sector projection removes leakage and annihilates a valid
  independent input vector. Erasure cannot be counted as restoration.

`RESULT.json` records the exact owner maps, phases, witness and coverage.
No frozen artifact is regenerated. No full native word replay, Lean build,
Docker run, historical suite or new multiplication certificate is required
for this scoped lemma.

Local validation on Python 3.12.8/macOS 26.5.1 arm64 passed the registered
replay and metadata/pin validation. A Git-free file copy passed `-I -O -B`
in 0.783 seconds; changed-owner-input and changed-witness-receipt controls
both rejected. The same receipt also passes on Python 3.14.5. Timings depend
on the host. These are author checks; the universal proof awaits review.

## 5. Sources, credit and overlap

Publication base: canonical main
`12fa8c5c844be21bfefb38a19503fbd867a11244`, priority revision 7. Scientific
inputs: zxv's PR4359 head `da637c87c89482bc4c86be36bd0071b3d400dbed`.
The five source files are retained byte-for-byte under `vendor/`; original
paths, Git blobs and SHA256 hashes are in `VENDOR.json`. `SOURCES.json` pins
the base task catalogue and selected record. The copied notes retain their
original paths in their own relative links; consult the pinned source commit
for dependencies outside this focused subset.

The native H construction and earlier fresh-sector witness are zxv's.
The retained source's owner/phase conventions credit ywz65's
`qq16-current-frame-consumer/native_support.py` and the pinned QQ16 lineage.
Original source headers and attribution are preserved. This contribution
adds the fixed-edge universal quantifier, inverse handling and commutant
closure, with source-bound checks.

The final overlap refresh covered 531 open PRs and 3,271 discussions and
comments, with complete reported pagination at 2026-10-21 18:05 UTC, plus
local notes. It did not search every code diff or remote closed PR body.
The closest prior work is PR4359's `joint_boundary_probe.py` and H primitive
audit. Pending PR4412, PR4414 and PR4416 change the identity-response compiler
or controller; PR4416 proposed κ = 0.00268647 at entry. Those pending
claims are not selected results or evidence that this H obstruction has been
reviewed. No Discussion or PR has been posted for this local contribution.

## Open next questions

1. **A costed old-block-mixing decoder.** Identify the actual operator that
   mixes B1 and test the complete arbitrary-input endpoint, including all
   scalar, routing, recursive and restoration costs. This is the main route
   left open; a generic free-word cancellation does not supply it.
2. **Change the fixed ordinary edge or its owner.** Try a native local word
   changing `(1,2)` while preserving its producer and helper contracts. First
   recheck the entire response and invoice; zeroing one witness alone is not
   a new supplier. The present completion-only theorem then no longer applies.
3. **Apply the commutant method at a different interface.** Pin the actual
   owner and retained matrix entry first. A different invariant may constrain
   another boundary, but no such extension or cost lower bound is claimed here.

Prepared by zxv with substantial OpenAI Codex assistance. Apache-2.0.
No subagents or independent human mathematical review were used.
