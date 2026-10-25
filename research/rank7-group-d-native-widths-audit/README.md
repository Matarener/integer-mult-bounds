# Group D's native residual widths through the shipped T74 fill

**Finite native/interface audit; no new kappa or supplier admission.**

Both literal PR2979 providers pass the entering-residual check for group D.
Helpers 454, 455, 556 and 557 enter at `[51]` and end at
`W = [256,128,64,37,21,8,3]`. Their emitted residual width is **six**, not
the terminal dimension seven. Exact native identities include global phase and
both orientations. These widths bind to all 2,664 group-D placements in the
shipped T74 allocation. Adapter and `LOCAL-CHECKS` hashes match the retained
`FULL-NATIVE-RECEIPT.json`. The four helpers share one residual pair
`114:263`.

This package deliberately does **not** headline the already-registered guide
margins `+17170` / single-helper negatives from `#2979`
`STAGE-PRICES.json`. The contribution here is the native residual / wrapper
binding for group D, in the style of leave-alone #3411 (group B) and the
in-flight group-C native-widths audit.

### Existing coverage and the added check

`research/rank7-group-a-entrance-audit/` binds group A
(`331/450/451/508/509`, `W_A`). Leave-alone #3411
`research/rank7-group-b-native-widths-audit/` binds group B
(`299/448/449/484/485`, `W_B`). In-flight
`research/rank7-group-c-native-widths-audit/` @ `ad6350cbb` binds group C
(`452/453/532/533`, `W_C`) and left group D as its open next question.
Group D is outside those packages.

## Exact native statement and source binding

The source is [PR2979][2979] at
`be191346391661f4d35fc0d1508d0a6029572576`; the base is canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6
(κ = `0.001672660197076918`). [SOURCES.json](SOURCES.json) records exact Git
blobs and SHA256 hashes. The native producer, exact kernel and retained
emitter are authenticated before execution. No frozen predecessor is modified.

For entrance `E` and terminal `U`, write the native residual as
`S(E,U) = T_U T_E^-1`. The source compiler produces `S = L F_w R`, where
`F_w` is the retained coordinate Fourier primitive on the first `w` address
axes. A separate exact Gaussian-integer kernel checks all 512 columns of
that identity, and the emitted inverse wrappers satisfy

```text
L^-1 S(E,U) R^-1 = F_w,
w = dim(U) - dim(E).
```

| Helper(s) | Entrance | Parent terminal dimension | Parent width | Joint/final width |
|---|---|---:|---:|---:|
| 454, 455, 556, 557 | span(51) | 8 | 7 | 6 |

Here `51 = 37 xor 21 xor 3` lies in the span of `W`. Treating an entering
helper as cold would select width seven and break the shipped packing. The
parent right wrapper (width seven) is not interchangeable with the joint
width-six recipe: the all-column check rejects that substitution. A different
contained line, `[3]`, has the same dimension but also fails with the actual
`[51]` recipe. The same-width group-C terminal span
`⟨256,128,64,32,19,11,6⟩` likewise fails against the group-D recipe.

The verifier regenerates both complete emitted programs with the unchanged
transport/emitter and reconstructs the full serialized adapter file using
the original generation convention. The uncompressed `LOCAL-CHECKS.json`
and `RESIDUAL-ADAPTERS.json` hashes match PR2979's retained native receipt.
Both regenerated event streams also match the counts and canonical event
digests inside that pinned receipt.

## Reproduction

```sh
python3 -I -B research/rank7-group-d-native-widths-audit/verify.py
python3 -I -O -B research/rank7-group-d-native-widths-audit/verify.py
python3 -I -B research/rank7-group-d-native-widths-audit/test_verify.py -v
python3 -I -B scripts/research_package.py --package research/rank7-group-d-native-widths-audit --check-only
python3 -I -B scripts/research_package.py --package research/rank7-group-d-native-widths-audit
```

Expected verify line:

```text
PASS_GROUP_D_NATIVE_WIDTHS providers=2 helpers=4 residual_widths=6,6,6,6 pairs=454:114:263,455:114:263,556:114:263,557:114:263 placements=2664 adapter_pinned both_orientations no_new_kappa
```

## Open next questions

1. Can the checked group-D direct paths and endpoints be joined to the
   complete native dependency closure of their private cleanup?
2. Do the complete physical, precision/tape and outer obligations admit the
   unchanged PR2979 source after independent review?

## Credit

Builds on #2979 (Dugongue / mdumitrean), the DreamingOfClouds / PR458 emitter
lineage, Sagar Thakrar's exact kernel, Nick Petalas's group-A entrance native
audit, leave-alone #3411 group-B native widths, and the in-flight group-C
native-widths tip `ad6350cbb`. New check by Wentao Li. Apache-2.0.

Prepared by Wentao Li with substantial AI assistance.

[2979]: https://github.com/CrocSwap/integer-mult-bounds/pull/2979
