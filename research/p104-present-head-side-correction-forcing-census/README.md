# Present-head side-correction forcing census

**Bounded claim.** On the published native-channel word, every checked
present-head strict `I−G/2` side-correction entry among flags `{1, 9, 43}`
needs non-private rank floor `+2`. The census covers each flag's primary
entry plus five additional off-diagonal nonzero Gram sources on that
target row (18 entries). No counterexample was found. No new κ.

## Why this package

Open [#3601](https://github.com/CrocSwap/integer-mult-bounds/pull/3601)
prices flag 43's entry `(59,21)` at the co-hosted cut with strict min `+2`
and co-host discount 0. Open
[#3610](https://github.com/CrocSwap/integer-mult-bounds/pull/3610) prices
flag 1's entry `(7,0)` with R1 free-ride / R0 `+2`. Both leave the same
OQ: does every present-head target row need `+2` for its strict
side-correction entry?

This package answers that OQ by a **cross-entry obstruction census** on
the published word. It is not a reprint of those correction words or
bills. Flag 9 uses the published chronology
([#3443](https://github.com/CrocSwap/integer-mult-bounds/pull/3443))
only; the deferred flag-9 head-step repair is not reopened.

## Method

For each checked entry `(target, source)`:

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

## Primary feeders (leave-alone citations)

| Flag | Entry | Classes obstructed | Source leaves final | Selected feeder | Gram |
|---:|---|---:|---:|---|---:|
| 1 | `(7,0)` coef `+1/2` | 19/19 | 1074 | `X7` head 387 | 2 |
| 9 | `(23,4)` coef `+1/2` | 25/25 | 745 | `X58` head 333 | 0 |
| 43 | `(59,21)` coef `−1/2` | 28/28 | 884 | `X12` head 131 | 0 |

Flag 1 and flag 43 feeders match the known samples cited by #3610 and
#3601 (bills not re-derived). Flag 9's feeder `X58:333` via `G7`/`G16`
is new relative to those open bills.

## Theorem

All 18 checked present-head strict entries need `+2`. No counterexample
entry appears in this census. Selected κ
`0.001672660197076918` is unchanged.

## Exact replay

```sh
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-forcing-census/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-forcing-census/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-side-correction-forcing-census/test_package.py
```

## Limits

- Published word only; co-hosted repair charts are out of scope.
- Sample of 18 entries, not the full ~48 nonzero off-diagonal sources
  per present-head target row.
- Non-private floor only; private-copy `+1` paths are not priced here.
- Does not admit a corrected supplier or change κ.

## Open next questions

Does the same `+2` floor hold for every off-diagonal nonzero Gram entry on
the three present-head target rows, beyond this 18-entry sample? Separately,
can a private-copy or end-cut bill for flag 9 on the published word discount
the non-private floor the way #3610's R1 free-ride does for flag 1, without
reopening the deferred flag-9 head-step repair?
