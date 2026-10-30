# Moment ceiling of the pooled R437 carrier profile

**Finite exact certificate for a fixed profile. No new κ, supplier admission
or frontier change.** This contribution is produced by Nick Petalas.

ToikY's [PR #5810](https://github.com/CrocSwap/integer-mult-bounds/pull/5810)
(`research/r437-unpooled-budget-obstruction`) shows that the unpooled #4067
host fails the retained moment test at the admitted BIT target `17/5000`. It
leaves other invoices open: "a different invoice, productive normalization,
target allocation ... needs its own bound". Chris R / Clear1nsight's
[PR #4176](https://github.com/CrocSwap/integer-mult-bounds/pull/4176)
(`research/r437-carrier-integration`) fixes the pooled profiles C (original
R437 with the 63 pooled owner moves) and D (the #4067 carrier with the same
moves). Its BILL.md says "No new decimal root is needed". This package computes
that root as a certified ceiling.

## Result

Use #5810's moment with every added charge omitted:

    M(c) = Σ_r n_r · r/(64·28416) · (64/r)^c.

Every rank in C and D is below 64, so each term increases with `c`. A
nonnegative surcharge `S(c)` only raises the left side of `M(c)+S(c) <= 1`.
The certificate proves `M(lo) < 1 < M(hi)` exactly. Therefore **every
`c >= hi` fails for every nonnegative surcharge**, and the fixed contract cannot
pass above the ceiling `hi`.

| Profile | Source | Certified crossing bracket of M |
|---|---|---|
| U, unpooled #4067 host | #5810 README | (0.0017366903544672, 0.0017366903544673) |
| C, pooled original | #4176 `PROFILE_C` | (0.0017367386530996, 0.0017367386530997) |
| **D, pooled carrier** | #4176 `PROFILE_D` | **(0.0017367829682417, 0.0017367829682418)** |

- **The carrier keeps its gain under pooling.** The D ceiling exceeds C by
  4.4315142e-8 (exact interval in RESULT.json). The C ceiling exceeds U by
  4.83e-8.
- **The admitted BIT target is out of reach at this normalization.** For D,
  `M(17/5000)` lies in an interval around `1.005440413297699` and exceeds 1.
- **The required width is 28571.** With D's paid profile unchanged, `M(17/5000) <= 1`
  holds exactly when the productive normalization is at least
  `Σ n_r r (64/r)^{17/5000} / 64`. The certificate places that number strictly
  between 28570 and 28571. The smallest integer width is **28571**, 155 more
  than 28416. C and U give the same integer.

All three profiles have 903456 paid calls, rank mass 1808352 and
`M(0) = 18837/18944`. That matches #5810's constant `A`.

**Consistency with reported values.** Two reported values should lie below
these ceilings, since their invoices include surcharges that this package
omits. Both do. #4067's passing grid point 0.001736690352456612377607 lies
2.0e-12 below the U bracket. Rohan Arun's closed #3959 pooled crossing
0.001736738651088946052684 lies 2.0e-12 below the C bracket. Neither
predecessor was replayed.

## Method

`verify.py` uses only the standard library and exact `Fraction` intervals.
Every endpoint is rounded outward to the grid `2^-256`.

- `log 2, log 3, log 5, log 7, log 13` come from `atanh(1/q)` series for
  `q = 3, 5, 9, 15, 25`, each with an explicit geometric tail bound.
  `log(64/r)` is assembled by factoring `r`.
- `exp(t)` on `0 <= t <= 1/2` uses the Taylor partial sum. The Lagrange tail is
  bounded by twice the next term.
- The profiles are read from #4176's `numerical.py` with `ast` and from #5810's
  README text. No predecessor code is executed. Both files are pinned by
  SHA256 in the verifier and in SOURCES.json. The verifier also checks the
  call count, rank mass, the #4176 normalization `W = 28416` and `M = 64`.

Controls must reject:
- D's bracket applied to C;
- the physical width 28425 in place of the productive width 28416;
- one D rank-42 call moved to rank 1;
- the carrier delta `{1:+288, 2:-576, 3:+288}` reversed on D.

The log intervals are also checked against floating-point `log` and must be
narrower than `10^-60`. The normal run requires byte equality with the
committed [RESULT.json](RESULT.json); `--emit` prints the recomputation.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -B research/r437-pooled-moment-ceiling/verify.py
python3.12 -O -B research/r437-pooled-moment-ceiling/verify.py
python3.12 -B scripts/research_package.py --package research/r437-pooled-moment-ceiling
```

Each direct run prints `PASS_R437_POOLED_MOMENT_CEILING` and takes under one
second.

## Scope and limits

- This is a **ceiling for one fixed moment test**. It assumes #5810's contract:
  productive normalization `64·28416` and the retained gate `M + S <= 1`. It is
  not a runtime lower bound, and it does not price D's complete invoice. It is
  not admission of the pooled compiler, physical caller, precision or stock
  boundaries, which #4176 and the family status keep open.
- The width threshold is a statement about normalization only. Adding productive
  columns would change the word, the caller and the paid profile. No such
  construction is proposed.
- The R437 line is not the selected supplier. The selected conditional κ stays
  `0.00310045` (#5599). The BIT budget there is admitted at `.0034` from a
  different supplier.

## Open next questions

1. **What is D's complete pooled crossing?** It matters because the ceiling
   omits the 864 added ADDs, the finite invoice term and the pooled-routing
   premise that #4176 retains. First step: add #4176's complete D invoice
   charges to `M(c)` and bisect with the same interval arithmetic. Blocked by
   #4176's retained absolute 77-factor routing premise, which has no
   source-bound proof.
2. **Which change of paid profile could close the gap to `17/5000`?** It
   matters because one carrier exchange per call moves the ceiling by only
   about 4.4e-8, while D still needs `M(17/5000)` lowered by about 0.544%.
   First step: compute the exact per-call moment change of each available
   local exchange at `c = 17/5000`, then compare the needed total with the
   903456 paid calls. Blocked by: no inventory of further exchange-eligible
   calls beyond #4067's 288.

Structured versions are in [TASK.json](TASK.json).

## Credit

ToikY (#5810) supplied the fixed moment contract, the unpooled profile and the
open pooled question. Chris R / Clear1nsight supplied the #4067 carrier, the
#4176 pooled C/D profiles and normalization, and the earlier pooled-allocation
audit. Rohan Arun supplied the #3959 pooled crossing. The retained R437 lineage
credited in those packages is unchanged: ai-nanachi/#3647, Ali Romman/#1043,
Sagar Thakrar/#3700, unpaidmoon/#4147, zxv/#3690 and others. The new work is
the certified pooled ceilings, the carrier gain under pooling and the
width threshold. Apache-2.0.
