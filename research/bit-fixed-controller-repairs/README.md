# Fixed BIT controller repairs and a two-code closed word

This package compares two precise modifications of the inherited bank recipe.
It adds a sharp repair theorem for every bank count and a shorter closed
controller. The two local alphabets are different and their costs are not
interchanged.

* For the fixed recipe with local blocks over
  `F2[N]/(N²−1)`, the exact number of extra scalar-conjugated single-bank `N`
  calls is `2B+1` when `B` is odd and `2B−1` when `B` is even. Here there
  are `2B` public banks, and every input is arbitrary. The proof includes
  explicit attaining repairs and permits any finite number of restored dirty
  spectators in this formal alphabet.
* For the distinct controller using coded stages 0 and 1 and clean remaining
  stages, a terminal correction uses only **two** code applications. The
  historical correction used six. Both close the inherited recipe for every
  `B≥1`; the two-code count is optimal in the stated single-bank generator
  alphabet with the fixed coded prefix.

The second result saves scalar work. Its declared native normalization remains
two 111-port sweeps, and its conditional rank-mass comparison with the all-clean
word is still `2·60−222 = −102`. No positive supplier or kappa is claimed.
Both all-B statements concern the abstract recipe. The historical native
driver requires at least five stages, and its old physical bank tiling is
specified only for nine stages; B=1 is not claimed as a native instance.

## Fixed recipe and exact repair tariff

The local blocks in this section are

```
F(x,y) = (x, x+Ny),       B(x,y) = (Nx+y, y),
```

over characteristic two, with one common nonidentity involution `N`.
Every old bridge and the terminal exchange are retained. With `ε=N+I`,
the evaluated word is `I+εA_B`; its defect relative to the desired common
`N` endpoint is `I+εM_B`, where `M_B=A_B+I`.

The all-parameter calculation gives

```
rank(M_B) = 2B          (B odd),
            2B−1        (B even),       trace(M_B)=1.
```

An allowed added call is `I+εuvᵀ`, where `vᵀu=1`. Thus each call has a
rank-one idempotent coefficient. Products add these coefficients because
`ε²=0`. Rank gives a call floor, while trace forces an odd call count.
Explicit idempotent decompositions attain both floors. The proof and
construction are in [PROOF-RECIPE.md](PROOF-RECIPE.md).

For `B=4`, the exact formal count is seven calls. A particular implementation
charging 111 native rank-one children per `N` call would charge 777. That
conditional conversion does not supply native admission or a complete moment
comparison. Arbitrary scalar mixing is free only in this formal model.
Changing the original local calls or their scalar control can change the defect.

## Closed hybrid with two code applications

This section uses a separate integral free-group algebra with independent
invertible generators `a0,a1`. The coded first pair is

```
F0(x,y) = (a0 x, y+a0 x),
B1(x,y) = (x−y, a1⁻¹ y).
```

The remaining `2B−1` local calls are clean. Keep every inherited bridge.
Unlike the historical word, insert no immediate code pullback after F0 or B1.
Immediately before the terminal exchange the first pair is

```
X0 = −y0,
Y0 = −y0 + a1⁻¹(y0+a0 x0),
```

and every other pair is `(-yj,xj)`. At the declared common FULL cut, apply

```
Y0 -= X0;
Y0 := a1 Y0;
Y0 += X0;
Y0 := a0⁻¹ Y0.
```

This makes the first pair `(-y0,x0)`. The old exchange therefore gives
`(Xout,Yout)=(x,−y)` on every independent input. Literal inverse and
inverse-transpose identities use the actual ordered word. Transpose generators
are not identified with inverses.

Abelianizing the independent code labels gives a determinant requirement of
`a1/a0` for the added correction. At least one occurrence of each label is
needed, proving the two-occurrence floor in this alphabet. Additional coded
local calls, simultaneous multibank code primitives or a changed target are
outside this optimum. See [PROOF-HYBRID.md](PROOF-HYBRID.md).

For the assigned 1,499-ADD code, the correction uses
`2·1499+222 = 3220` scalar ADDs, versus the historical `9216`: a saving of
`5996`. Both words declare the same 222 native normalization children.
Logical endpoint equality alone cannot validate or erase that native bill.
The conditional 60-unit local saving is the separate returned-owner comparison
in [PR4185](https://github.com/CrocSwap/integer-mult-bounds/pull/4185);
mixed clean/coded hosting and all-size precision are not supplied here.

The formal signed coded maps above are not the full integer lift of the R429
factory. Its clean target formula is a binary VALUE statement; its integer
target may contain even helper leakage. Local helper restoration, legal
native frames, source-code access and copied-state cleanup remain separate
implementation premises.

## Early promotion has an actual native obstruction

The retained P012 code has entry `A[3,0]=1`. For the actual inherited E8
routes, the corresponding relative ADDRESS map sends the source root line
into a nonzero fresh coordinate:

```
(0,0,2,0,0,0,0)
```

over the rationals and modulo 101. It therefore fails to preserve the target
promoted root-line frame. This rejects the particular proposal to apply that
future code freely after early target promotion. It does not rule out a new
factory accepting promoted inputs or a different controller.

The independent replay reconstructs the two needed routes and this one
offdiagonal entry. The historical replay retains its original all-pair route
check, without presenting that older work as a new theorem.
With ADDRESS push `T=rho3⁻¹ rho0`, the source VALUE function
`f(w)=1[w10=0]` is constant on the source P0-line fibers. Its forward image
`g(w)=f(T⁻¹w)` has `g(0)=1` and `g(v3)=0` for the target root `v3`,
so it fails target P3-line invariance. This is an admitted source quotient
function, not an assumption that an isolated point delta is admissible.

## Verification and source boundary

Run the registered package from the repository root:

```
python3.12 -B scripts/research_package.py --package research/bit-fixed-controller-repairs
```

[VERIFY.json](VERIFY.json) declares every command. All required scientific
inputs are inside this package. [EVIDENCE-INDEX.md](EVIDENCE-INDEX.md) separates
the three original complete receipts, the two new independent checkers,
written all-parameter proofs and acceptance controls.

The old files remain byte-identical under `frozen/`; original absolute paths
are provenance only. [ADAPTATIONS.md](ADAPTATIONS.md) specifies the authenticated
source reader, function selection and optimized-Python behavior. Full JSON
comparisons preserve types and event order. No broad search is rerun.

Historical receipts retain their original planning allowances and scoped
statements. In particular, their numbers 492 and 309 are not used as a new
matched supplier budget. The current claims are those stated above and in the
two proof notes.

## Open next questions

Can a different native caller reduce the two normalization sweeps or amortize
them while preserving every arbitrary input and helper? First specify legal
current frames and the full mixed owner allocation, then compare complete
rank profiles and source-access costs. The scalar identity does not answer
those questions.

Can a changed original recipe beat the fixed-repair tariff? The first step
must name which original paid local or scalar-control operation changes.
The theorem here fixes that recipe; it does not constrain all callers.

## Sources and credit

The bank recipe retains the DreamingOfClouds, eumemic, Zhihao Chen and
chafreaky lineage and its source notices. Ali Romman supplied the R438
deletion/source-code ancestry; Sagar Thakrar supplied transport and rehosting.
The R429 interface is [PR3645](https://github.com/CrocSwap/integer-mult-bounds/pull/3645);
the FULL-target/seeded caller work is
[PR4039](https://github.com/CrocSwap/integer-mult-bounds/pull/4039) and is not
republished as a new construction here.

The original local findings, new all-parameter derivations, shorter controller,
independent checking contexts and this publication were prepared by Ross
Richardson with substantial OpenAI Codex assistance. Separate AI review is not
human acceptance or a formal-kernel proof. Apache-2.0.
