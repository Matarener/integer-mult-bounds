# Where rounded native codes keep their history

**Scoped theorem and constructive codec; author-checked evidence. No new κ.**

This package determines the exact recovery information lost by the actual
112-owner rounded inverse as its output grid changes. It also proves that
the worst-case history cost multiplies under repeated same-grid recoding,
even through noncommuting changes of integer coordinates.

The coarse input is `x∈Z^112`; the output is
`y=2^g x−M round_away(2^g Mᵀx/52)`, where the pinned source has
`MᵀM=56I`. The fixed parameter `g` measures output precision **relative to
the actual input lattice**. It is not an absolute working-precision allowance.

| Relative bits `g` | Exact worst-case recovery states | Packed tag bits | Added fractional slots + tag bits¹ |
|---:|---:|---:|---:|
| 0 | 815,730,721 | 30 | 30 |
| 1 | 51,008,161 | 26 | 138 |
| 2 | 362,401 | 19 | 243 |
| 3 | 4,096 | 12 | 348 |
| 4 | 16 | 4 | 452 |
| 5 | 1 | 0 | 560 |

¹One real scalar coordinate across all 112 owners, with uniform fixed-width
fractional fields: `112g+ceil(log₂ F_g)`. This comparison excludes magnitude
bits, scratch, movement, and execution costs. Every `g≥5` is injective.
Increasing input and output precision together preserves the same-grid loss.

The `g=0` result is [Ali Romman](https://github.com/aliromman)'s
[PR #5323](https://github.com/CrocSwap/integer-mult-bounds/pull/5323).
The positive-precision rows and the composition theorem extend that work.

## Significance for researchers

Recovery tags, precision, and repeated recoding can now be compared using an
exact interface theorem. Five relative bits permit a tag-free mathematical
decoder; they add 560 fractional bit positions if all 112 output fields are
uniformly widened. That route is most attractive when the finer output grid
is already needed. On the same grid, integer frame changes cannot keep the
recovery history bounded through indefinitely many recodings on growing input
ranges. A proposal must retain history, introduce relative refinement or other
recoverable information, change the map, or accept irreversible disposal.

## The broader theorem

For full-column-rank integer `M`, positive integer `β`, and inputs in `B Z^n`,
the fibers of `z−M round(Mᵀz/β)` are exactly the integer quotients in a
translated residual parallelotope satisfying the input-lattice congruence.
Uniform finite recovery tags exist exactly when `MᵀM−βI` is nonsingular.
This supplies a reusable test and a finite enumeration method, with no general
efficient synthesis claim.

For this source, `N` real coordinates and `t` same-grid recodings require
exactly `13^(8Nt)` worst-case history states. Fixed known unimodular pre/post
maps may mix all `112N` fields and need not commute. Packed history needs
`ceil(8Nt log₂13)` bits; for `N=1,t=18`, that is **533 bits**.

With total uniform relative refinement `G`, side information of at most `S`
states, and a `b`-bit retained history, the necessary conservation inequality is

```text
b + log₂S + 112NG ≥ 8Nt log₂13.
```

Sharpness is proved for same-grid history with no extra observation. The
refined/side-information inequality is a necessary volume bound; the one-step
table is stronger. These history claims require the unbounded lattice, or a
sufficiently large finite range. Stationary frames have an explicit sufficient
input bound `||x||∞≤2(13^t−1)`. A fixed small range need not attain the bound.

See [PROOF.md](PROOF.md) for all hypotheses, the source binary code's weight
enumerator `a^8+14a^4b^4+b^8`, attaining fibers, and the volume argument.

## Nearest overlapping work and useful seams

| Work | Existing contribution | New use or unresolved seam |
|---|---|---|
| [PR #4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933), [Dillon Amburgey](https://github.com/dillona); [PR #4929](https://github.com/CrocSwap/integer-mult-bounds/pull/4929), [David Ganz](https://github.com/Dugongue) | Physical normalizers and native code geometry | Bind the coarse lattice and actual common-coordinate access before using the table. |
| [PR #5035](https://github.com/CrocSwap/integer-mult-bounds/pull/5035), [Brian](https://github.com/JoyboyBrian) | Finite bitwise rounded kernel and sharp output error | Its byte-exact kernel is calibrated here; destructive zero-writing still needs a separate reversible implementation. |
| [PR #5323](https://github.com/CrocSwap/integer-mult-bounds/pull/5323), [Ali Romman](https://github.com/aliromman) | Sharp same-grid `13^8` states | Direct predecessor; this package adds relative precision, code-coset ranking, and changing-frame composition. |
| [PR #5321](https://github.com/CrocSwap/integer-mult-bounds/pull/5321), [Ali Romman](https://github.com/aliromman) | Cheaper kernel arithmetic | Recovery-codec cost must join its bill; the information theorem supplies no priced implementation. |
| [PR #5333](https://github.com/CrocSwap/integer-mult-bounds/pull/5333), [Ali Romman](https://github.com/aliromman) | All-site physical pair residual budget | Extract actual input/output grids before identifying any relative bits. |
| [PR #5438](https://github.com/CrocSwap/integer-mult-bounds/pull/5438), [Mark](https://github.com/Matarener) | Proposed exact selected-caller grids | Its absolute grid requirement does not by itself establish five relative bits for this inverse map. |

Classical outside input is MacWilliams'
[weight-enumerator theorem](https://doi.org/10.1002/j.1538-7305.1963.tb04003.x)
and Forney's [Fourier/duality treatment](https://arxiv.org/abs/0911.5508).
The new claim is the exact source application and its composition consequences;
general code duality and volume counting retain their classical status.
[OVERLAP.json](OVERLAP.json) records search coverage and its limits.

## Reproduction and interfaces

Python 3.10+ and the standard library suffice. From the repository root:

```sh
python3 -B research/precision-state-frontier/verify.py
python3 -B research/precision-state-frontier/test_package.py
python3 -B research/precision-state-frontier/mutation_check.py
```

The first prints [RESULT.json](RESULT.json); `--source-root .` additionally
checks six exact canonical source hashes and equality of the literal matrix.
The default is self-contained and Git/network-free. The second repeats both
normal and optimized verification from a read-only portable copy with an empty
`PATH`, then exercises the public JSON interfaces and rejection controls.
The third tests five semantic changes in both Python modes on private copies.
[VALIDATION.json](VALIDATION.json) records commands, hashes, environment, and
unrun obligations. This standalone package is not registered in the shared
replay catalogue.

```sh
python3 -B research/precision-state-frontier/frontier.py table
python3 -B research/precision-state-frontier/frontier.py encode input.json > encoded.json
python3 -B research/precision-state-frontier/frontier.py decode encoded.json
python3 -B research/precision-state-frontier/history.py budget.json
```

Encoding input has exactly `{"g":4,"x":[112 exact integer entries]}`.
The output includes the fine integer output, rank tag, source identity, and
fiber/state metadata. `budget.json` may be `{"rounds":18}`; optional fields
are `components`, `total_relative_guard_bits`, and `side_states`.
The codec supports `0≤g≤16`; excessive guard/exponent requests fail with
“no decision” rather than silently truncating the mathematical domain.

Finite checks cover all 64 Gram entries, 2,016 dyadic congruence cases, 1,280
coset counts, 321 scalar intervals, 97 attaining-fiber roundtrips, 36 other
input roundtrips, 24 unchanged source-kernel calls, three source-sized changing
frame chains, and noncommuting toy windows totaling 345,859 inputs.
Large fibers are counted by the proof and factored codec, not enumerated.

## Risks, tradeoffs, and remaining obligations

| Boundary | Consequence |
|---|---|
| Relative versus absolute precision | Widening both grids leaves `g=0`; existing absolute guards cannot be reused as an injectivity proof. |
| Interface versus reversible machine | The injective output/tag map still needs legal computation, storage, routing, and eventual restoration. |
| Uniform precision cost | Eliminating a thirty-bit tag can add 560 fractional positions; output range and scratch may add more. |
| Lattice and observation contract | Nonunimodular maps, extra outputs, rereads, and variable control change the information bill. |
| Input range and repetition | The exact repeated bound is asymptotic in available input range; it does not force 533 bits in every bounded eighteen-step caller. |
| Validation status | Written scoped proof and author calibration; independent mathematical review and caller admission remain open. |

## Open next questions

| Direction | Opportunity and first discriminating step | Main risk / stop rule |
|---|---|---|
| Actual pair/caller lattice | At one named inverse call, derive the input lattice and output grid using the physical and exact-grid work above. | Stop applying this frontier if the matrix or access contract differs. |
| Paid reversible codec | Compile one `g=0` or `g=4` rank/unrank path with explicit scratch and restoration; compare the complete bill to retained-input replay. | The information optimum may cost more to compute than a simpler thirty-two-bit quotient layout. |
| Unequal precision | Optimize per-owner grid additions using the actual congruence lattice, rather than widening all 112 fields. | Determinant volume alone is not an attainable decoder; avoid claiming an optimum from that relaxation. |
| Mixed refined chains | Compute a sharp two-step fiber with one relative bit and a noncommuting integer frame. | One-step maxima need not multiply after refinement; the current conservation inequality may be loose. |
| Wider native-code family | Derive the row lattice and coset enumerator of one other admitted low-rank code, then compare complete recovery cost. | A favorable determinant or binary code does not establish physical access or a useful full invoice. |
| Finite-range frontier | Determine the smallest `H` attaining a chosen row or repeated-frame bound, using exact branch-and-bound. | Fixed-range enumeration grows rapidly; stop after a certified threshold or explicit useful gap. |

Source pin: canonical main `32890bc5de034ab8fc93ac88ead7279a6a416d04`,
priority revision seven. Its selected conditional `κ=0.003027288235` is
unchanged. [zxv](https://github.com/zxv), with substantial OpenAI Codex
assistance. Apache-2.0. The retained source kernel keeps its original notice;
all native, controller, precision, compiler, and recovery predecessors retain
their attribution.
