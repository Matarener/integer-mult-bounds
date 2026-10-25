# Present-head side-correction full-row forcing census

**Bounded claim.** On the published native-channel word, every off-diagonal
nonzero Gram strict `I−G/2` side-correction entry on present-head target
rows `Y7` / `Y23` / `Y59` (flags `{1, 9, 43}`; 48 sources per row; 144
entries) needs non-private rank floor `+2`. No counterexample. No new κ.

## Why this package

Open [#3614](https://github.com/CrocSwap/integer-mult-bounds/pull/3614)
proved the `+2` floor for an 18-entry sample (primary plus five extras per
present-head row) and left OQ1: full-row extension on `Y7`/`Y23`/`Y59`.
This package answers that OQ by completing every off-diagonal nonzero
Gram source on those three rows. It extends #3614's method; it is not a
file clone and does not reprint open
[#3618](https://github.com/CrocSwap/integer-mult-bounds/pull/3618) /
[#3610](https://github.com/CrocSwap/integer-mult-bounds/pull/3610) /
[#3601](https://github.com/CrocSwap/integer-mult-bounds/pull/3601)
correction bills. The deferred flag-9 head-step repair is not reopened.

## Method

For each entry `(target, source)` among the 144:

1. Enumerate insertion classes after every `add`/`copy` that touches the
   source or target register on the published program.
2. At each class, inject a least-frame merge of the two registers and
   sweep forward under common-chart ADD closure (class-Z style). Record
   the first register whose forced frame exits its endpoint.
3. Separately, track when the source first exits the target final
   hyperplane and which initial X-heads are present outside that final.
4. Conclude zero-mass blocked. Endpoint-restoring non-private nested
   transports contribute even rank mass, so the strict non-private floor
   is `+2`.

## Primary feeders (leave-alone citations from #3614)

| Flag | Entry | Classes obstructed | Source leaves final | Selected feeder | Gram |
|---:|---|---:|---:|---|---:|
| 1 | `(7,0)` coef `+1/2` | 19/19 | 1074 | `X7` head 387 | 2 |
| 9 | `(23,4)` coef `+1/2` | 25/25 | 745 | `X58` head 333 | 0 |
| 43 | `(59,21)` coef `−1/2` | 28/28 | 884 | `X12` head 131 | 0 |

The #3614 18-entry sample is covered as a named subset of this census
(`in_pr3614_sample`). Bills for those primaries remain leave-alone.

## Theorem

All 144 present-head strict entries on `Y7`/`Y23`/`Y59` need `+2`. No
counterexample entry appears. Selected κ `0.001672660197076918` is
unchanged.

## Exact replay

```sh
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-full-row-census/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-full-row-census/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-full-row-census/test_package.py
```

## Limits

- Published word only; co-hosted repair charts are out of scope.
- Non-private floor only; private-copy `+1` paths are not priced here.
- Flag 0 and absent-head targets are out of scope.
- Does not admit a corrected supplier or change κ.

## Open next questions

Can a private-copy or co-hosted chart discount any of the 126 non-primary
full-row entries? Separately, does the same row-complete floor hold for
present-head flag 0 once the coefficient cascade commits a cut?
