# QQ16 Gaussian-axis arithmetic on six physical bit tapes

**Scope:** one exactly divisible, nonuniform tensor-axis line primitive, not an F0/B1 producer or an admitted recursive supplier.

The [native reference](../qq16-native-rounded-components/vendor/native.py) defines, for every coordinate `x` and its partner `y=x xor (1<<axis)`, the exact pair
```
r'[x] = (r[x]+r[y]+s*(i[y]-i[x]))/2
i'[x] = (i[x]+i[y]+s*(r[x]-r[y]))/2
```
for `s in {-1,1}`. This package gives a literal sequential bit-tape implementation of that map, including data movement, scratch zeroing, head returns, and a cell-action invoice. It deliberately uses the *pinned source* formula rather than the rotated displayed second output noted by #3652/#3671.

## Result and contract

Given `N=2^n` coordinates, `n>=1`, signed two's-complement little-endian component width `W>=2`, and an axis `0<=axis<n`, the algorithm transforms two **owned, separately based** `NW`-cell data tapes. Four further owned, discardable `NW/2`-cell scratch tapes may contain arbitrary initial bits. All six tape heads start at their individual origins. Each numerator above must be even and within signed W-bit range; this is a **caller precondition**, not a condition checked non-destructively by the tape program.

On successful completion the two data streams contain the exact pair transform, all scratch cells are zero, all six heads return to their origins, and the exterior cells are never accessed. A finite-state carry in `{-1,0,1,2}` and a fixed index/controller schedule suffice for each local step. The implementation has an exact counted cell-action tariff:

| Tape class | READ | WRITE | MOVE | Total |
| --- | ---: | ---: | ---: | ---: |
| Two data tapes combined | `2NW` | `2NW` | `8NW` | `12NW` |
| Four scratch tapes combined | `4NW` | `4NW` | `12NW` | `20NW` |
| **Total** | **`6NW`** | **`6NW`** | **`20NW`** | **`32NW`** |

In addition, the caller must supply `2NW` data bits and `2NW` cleanable owned scratch bits, and pay for obtaining the input layout, encoding, addressing/finite control, neighbouring native recipe monomials, cover maps, producer scalar instructions, restoration, F17 consumption, and recursive/tape transfers. Bit-operation counts and Gaussian rank-one child tariffs are not interchangeable. The 11,076 axis factors per layer in #3303 imply the **conditional axis-only** subtotal `354432 lambda N W` single-cell actions, *only if* every required axis step is supplied in this layout with the stated preconditions. No complete-producer physical bill is inferred.

## Proof idea

The packing pass streams coordinate blocks in order, separating each axis-bit lane into four half-length scratch arrays without touching external cells. For each axis block, low-lane output and high-lane output use the same input bits with opposite sign. A streamed numerator bit has `t = carry + a - s*b + c + s*d` (and the corresponding imaginary expression), `out = t mod 2`, `carry' = floor(t/2)`. The carry range is invariant since the signed sum of four bits lies in `[-1,3]` and the carry lies in `[-1,2]`. Exact divisibility makes the lowest output bit zero. Dropping that bit and sign-extending the highest one performs exact division by two on a signed W-bit numerator. The high-lane pass is the last scratch reader, so it clears every scratch cell without destroying an earlier read. All traversals are closed and contribute the counts above. The argument works for all positive n and W under the explicit range/divisibility premises, not merely the finite fixtures.

## Reproduction

From the repository root with Python 3.12+ and no third-party packages:

```sh
python3 -I -B research/qq16-gaussian-axis-tapes/verify.py
python3 -I -O -B research/qq16-gaussian-axis-tapes/test_verify.py
python3 -B scripts/research_package.py --package research/qq16-gaussian-axis-tapes
```

The first command verifies the complete published `RESULT.json`. The second runs behavioural rejecting controls. The registered command additionally validates metadata/source pins. The primary check loads and hashes the exact native source and all-depth arithmetic receipt. It checks 8,192 signed pair cases, 56 routed axis/sign cases at dimensions 2 through 128, 72 signed boundary cases at widths through 545, 18 comparisons against the actual 512-coordinate pinned native line (both signs on all nine axes), and four consecutive axis/inverse operations sharing scratch. It meters every tape cell operation. Sources are authenticated before execution. No full F0/B1/native/selected cold replay, Lean proof, hosted CI, or human review is asserted.

## Relationship to predecessors

Ali Romman's QQ16 construction and native/geometry lineage supply the operator. Nick Petalas' #3303 and #3270 supply the all-depth producer and factor-count envelope; #3652 (ToikY) independently checks its primitive ledger, and #3671 documents the output-turn convention. Sagar Thakrar's #3241/#3377 address different physical access boundaries, while Dugongue's #3394 prices owner-cover permutations rather than the present Gaussian coordinate primitive. The recorded missing caller and consumer in #3339 remain missing. This is a separate local implementation, not a replacement for these results. New work by Clear1nsight with substantial OpenAI ChatGPT assistance. Apache-2.0.

## Open next questions

1. **Actual caller layout.** Can the literal F0/B1 source establish the six separately based owned windows, the exact signed grid, and available scratch before each axis factor? First bind a specific native event to real owner/frame/tape intervals. Missing caller ownership and entrance protocol block this.
2. **Whole-producer bill.** What physical layout transitions are required between the 11,076 axis factors, monomial permutations, cover maps and scalar steps? First price one adjacent event pair without gifting relocation or addressing. The full source and its consumer remain uncharged.
3. **Dirty helper semantics.** Can each caller borrow helper fields whose endpoint is frame-relative rather than literal common-coordinate restoration (#3293)? First bind one named borrowed caller interface and test arbitrary nonconstant input. No full QQ16 helper restoration follows from this package.

**Decision:** close this bounded local tape primitive and stop. Unknown costs are not zero, and no new `kappa` or selected-frontier change is claimed.
