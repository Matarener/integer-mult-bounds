# Group B's native residual widths through the shipped T74 fill

**Finite native/interface audit; no new kappa or supplier admission.**

Both literal PR2979 providers pass the mixed-entrance check for group B.
Helpers 448, 449, 484 and 485 enter at `[51]` and end at
`W = [256,128,64,34,17,11,4]`. Their emitted residual width is **six**, not
the terminal dimension seven. Helper 299 enters at zero and uses width
**seven**. Exact native identities include global phase and both orientations.
These widths bind to all 3,330 group-B placements in the shipped T74
allocation. Adapter and `LOCAL-CHECKS` hashes match the retained
`FULL-NATIVE-RECEIPT.json`.

This package deliberately does **not** headline the already-registered guide
margins `+42541` / single-299 `-58943`. Those facts reprint `#2979`
`STAGE-PRICES.json` and match the deferred soft-overlap tip `f795116d`
(`research/rank7-group-b-single-control-audit/`). The contribution here is the
native residual / wrapper binding that tip left open.

### Existing coverage and the added check

`research/rank7-group-a-entrance-audit/` already binds group A's native
residuals for helpers 331/450/451/508/509 under a different shared word
`W_A = [256,128,64,38,20,10,1]`. Group B is outside that package.

The deferred group-B single-control audit already checked joint versus
single-299 guide margins and placement counts. It recorded an open question
asking whether emitted mixed-entrance wrappers and native residual recipes
match widths `7/6/6/6/6` in both orientations. This package answers that
question with an independent source-bound native replay.

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
| 299 | zero | 8 | 8 | 7 |
| 448, 449, 484, 485 | span(51) | 8 | 7 | 6 |

Here `51 = 34 xor 17` lies in the span of `W`. Treating the entering helpers
as cold would select the wrong native operator even if a rank field were
edited to six. The cold right wrapper and the entering right wrapper are not
interchangeable: the all-column check rejects that substitution. A different
contained line, `[4]`, has the same dimension but also fails with the actual
`[51]` recipe.

The verifier regenerates both complete emitted programs with the unchanged
transport/emitter and reconstructs the full serialized adapter file using
the original generation convention. The uncompressed `LOCAL-CHECKS.json`
and `RESIDUAL-ADAPTERS.json` hashes match PR2979's retained native receipt.
Both regenerated event streams also match the counts and canonical event
digests inside that pinned receipt.

## Reproduction

```sh
python3 -I -B research/rank7-group-b-native-widths-audit/verify.py
python3 -I -O -B research/rank7-group-b-native-widths-audit/verify.py
python3 -I -B research/rank7-group-b-native-widths-audit/test_verify.py -v
python3 -I -B scripts/research_package.py --package research/rank7-group-b-native-widths-audit --check-only
python3 -I -B scripts/research_package.py --package research/rank7-group-b-native-widths-audit
```

Expected verify line:

```text
PASS_GROUP_B_NATIVE_WIDTHS providers=2 helpers=5 residual_widths=7,6,6,6,6 pairs=299:0:260,448:114:260,449:114:260,484:114:260,485:114:260 placements=3330 adapter_pinned both_orientations no_new_kappa
```

## Open next questions

1. Can the checked group-B direct paths and endpoints be joined to the
   complete native dependency closure of their private cleanup?
2. Do the complete physical, precision/tape and outer obligations admit the
   unchanged PR2979 source after independent review?

## Credit

Builds on #2979 (Dugongue / mdumitrean), the DreamingOfClouds / PR458 emitter
lineage, Sagar Thakrar's exact kernel, Nick Petalas's group-A entrance native
audit, and the deferred group-B single-control tip `f795116d` (which this
package does not reprint). New check by Wentao Li. Apache-2.0.

Prepared by Wentao Li with substantial AI assistance.

[2979]: https://github.com/CrocSwap/integer-mult-bounds/pull/2979
