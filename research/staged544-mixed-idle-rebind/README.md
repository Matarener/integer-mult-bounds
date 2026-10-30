# The ordinary rebind cannot charge PR #4088's mixed idle

**Finite profile reproduced. Ordinary admission blocked by the shipped idle remainder. No selected-frontier change.**

The highest pending conditional endpoint on canonical main `bb4bccbf42844d2801487450727c2f63e10d1d0f` is the mixed staged544 profile of [PR #4088](https://github.com/CrocSwap/integer-mult-bounds/pull/4088) at head `72d7efc181edb21806a878f174847c96dd410ab0`:

`κ = 0.001730979115670792472760 − 10^-46 − 10^-70`.

[PR #4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100) quotes a numerically sharper unconditional reading of that same profile and states that the historical outer-admission CLI was not run. Selected κ remains `0.001672660197076918` (#1094).

## What blocks admission

The inherited ordinary rebind, pinned here as `vendor/rebind.py` (SHA-256 `faf283eb4edd2e6a1ccb40b3cb3ba30ae54338eaf5ea0a10d84d11d7939502af`, from the PR #3815 replay archive used by the #3945/#4076/#4085 release), does two things this fill cannot survive:

1. It has only the provider ids `gauge44` and `extra`, and it writes one width vector onto every call of a provider.
2. It rebuilds the global profile as `n_pid * (one integer local profile) + idle`, where `idle` is the shipped `CONSTRUCTION.json` remainder and is not recomputed.

An independent scan of the vendored #4088 rows finds that helper 601, origin index 367, has width 8 on 2,150 three-entry calls and width 7 on 1,090 four-entry calls. Both orientations mix those widths (`gauge44`: 1,040 eights and 528 sevens; `extra`: 1,110 eights and 562 sevens). The two extra rank-1 cells on each fourth-entry call are not divisible by the orientation's call count, so no single integer local profile per orientation reproduces the mixed local histogram.

The scanned idle remainder is `{3: 22783, 5: 1625, 48: 138492}`. Relative to the #4085 two-provider idle `{3: 22842, 5: 1890, 48: 138438}` the change is

`-59 H3 − 265 H5 + 54 H48`,

rank mass `+1090`. That exactly balances the local rank-mass drop of one unit on each of the 1,090 fourth-entry calls. Keeping the #4085 idle while accepting the mixed local histogram drops those 1,090 rank units. The moment of that illegal profile changes sign near `0.00174722463155`, more than `1.62455 × 10^-5` above the scanned root. The `+54` rank-48 cells are the charge the ordinary engine would omit.

The scanned complete profile is

`{1: 8060060, 2: 2310120, 3: 751813, 4: 327210, 5: 66425, 8: 25920, 48: 138492}`.

Its moment is negative at `0.001730979115670792472760` and positive at the next 24th digit. That reproduces the finite #4088 bracket. It is a positive control for the scan, not a new root and not an admission.

## Existing checks and what is still open

#4088's own verifier walks this fill and prices the moment. #4085 completed the two-provider ordinary release for the three-entry words. No open PR extends that rebind to four width vectors and a recomputed idle. This package does not rerun native stages or the outer-release CLI, and it does not discharge #4100's unconditional argument. The selected record is unchanged.

## Reproduce

From the repository root, standard-library CPython 3.12:

```sh
python3 scripts/research_package.py --package research/staged544-mixed-idle-rebind --check-only
python3.12 scripts/research_package.py --package research/staged544-mixed-idle-rebind
```

The direct command is `python3 -B research/staged544-mixed-idle-rebind/verify.py`. It checks the vendored bytes, scans all 1,321,920 rows, certifies both moments, and rejects five mutations: a 108-of-324 selector, a three-entry width on the first fourth-entry call, the frozen-idle profile at the claimed bracket, one extra rank-1 cell, and the #4085 profile at the claimed bracket.

## Open next questions

1. Extend the pinned rebind to four provider ids, recompute idle from the per-call widths, keep every admission predicate and mutation control, and rerun the ordinary/outer release. That is the integration step still required before a maintainer can consider this endpoint.
2. A different literal fill might place helper 601's freed unit without creating 54 rank-48 idle cells. Any such fill needs its own row scan and moment certificate; the fractional screen is not a substitute.

## Credit

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

The mixed words, dispatch and owner rows are unmodified exports of Cinna Davis's PR #4088. The three-entry gzip hashes `df31495c…` and `9a28f7ef…` are the candidate pins of zxv's PR #4085 release. The two-provider rebind is the unmodified PR #3815 archive file used by Dugongue's PR #3945 and Rohan Arun's PR #4076. `NOTICE.md` records the export.
