# Disposition receipt: the Gaussian halo-exponent PR chain

**Claim type:** a source-bound overlap and disposition receipt (the overlap-receipt card). **No new κ.**
It makes no closures and no merge recommendations. It covers 13 open PRs submitted on 2026-10-21 against
base `2a13eb18`. The verifier checks the receipt's internal consistency and its retention claims.
`RECEIPT.json` records exact heads and package-file blobs.

## Disposition

All 13 PRs are single-package additions on base `2a13eb18`. **None is retained on main**: each package
path is absent at the base.

| PR | Author | Head | Role | Depends on | Independent check |
| --- | --- | --- | --- | --- | --- |
| #4437 | jwr404 | `7ca94e97` | ideal column majorant across `g = 2`; ideal gap `> 1/(8p²)` | — | #4468 |
| #4438 | jwr404 | `6157a47b` | within-cell gauge transfer, `1/(1−ε)`; `C = 3` | #4437 | #4469 |
| #4439 | jwr404 | `26af8afb` | within-cell ε exponents 12, 26, 28, 28, 6 | #4438, #4437 | #4471 |
| #4442 | jwr404 | `d079c2b0` | across-cell ε exponents (downward reading) | #4439, #4449 | #4471 |
| #4449 | mihir-s-05 | `1fb77b37` | across-cell rounding `0 ≤ H ≤ n`, `n − H < 4η` | — | #4472 |
| #4451 | jwr404 | `be243a28` | weight error is relative `δ = 2^{2−32760p}` | — | #4460 |
| #4452 | jwr404 | `af68f597` | within-cell δ exponents 11, 24, 26, 26, 6 | #4451, #4437 | #4460 |
| #4462 | pinterbanget | `c8fd7f81` | across-cell δ transfer; "rounded"-reading robustness | #4452, #4449, #4442 | **none yet** |
| #4460 | pinterbanget | `6aaf4810` | check of #4451/#4452 | | |
| #4468 | pinterbanget | `b5f7fbbb` | check of #4437 | | |
| #4469 | pinterbanget | `baf56b16` | check of #4438 | | |
| #4471 | pinterbanget | `0cf8e2b0` | check of #4439/#4442 | | |
| #4472 | pinterbanget | `dcf680a1` | check of #4449 | | |

## Relations

- **The two routes.** The δ route (#4451, #4452, #4462) implies the ε route's weight hypothesis with
  room, since #4451 shows `δ < 1/(16p²)`. It gives smaller exponents: 11, 24, 26, 26, 6, against 12,
  26, 28, 28, 6. The ε results remain valid but are coarser. Neither route is on main.
- **Coverage.** Every author PR in the set has at least one independent check, by separately written
  code. All checks are by one contributor, so a second, different reviewer is still missing.
- **The one gap.** The open transfer #4462 has no independent check yet.
- **Hypotheses common to the whole chain.** The ideal gaps (GAUSSIAN's "eventually" statements, #4402)
  and the page-generator implementation are not discharged by any PR in the set.

## Not covered

- PRs outside the named set, for example #4402 and #4406 already on main, and the downstream report.
- Any judgement of merge priority.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/halo-chain-receipt --check-only
python3.12 -B scripts/research_package.py --package research/halo-chain-receipt
git fetch origin pull/4452/head && git ls-tree -r FETCH_HEAD research/gaussian-delta-exponents   # compare a recorded blob
```

The verifier prints `PASS_HALO_CHAIN_RECEIPT`.

## Open next questions

1. **An independent check of #4462 by a different contributor.**
   - *First step:* replay Lemma A's split with δ, and Lemma B's `10p²` ceiling.

## Credit

- jwr404 (James Reed) and mihir-s-05 (Mihir Srivastava) wrote the author PRs.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
