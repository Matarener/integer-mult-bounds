# Gauge44 A-block exact resynthesis

This package is a reproducible finite-circuit contribution against the X4 word from [CrocSwap/integer-mult-bounds PR #799](https://github.com/CrocSwap/integer-mult-bounds/pull/799).

It replaces the 14 consecutive dimension-four blocks in the A prefix by exact rationally equivalent elementary words. A fixed-seed search (`seed=20261013`, 4,096 pivot orders per block) uses only dyadic row operations, checks the exact block map, and preserves each block's stored frame.

| quantity | #799 X4 | resynthesized |
|---|---:|---:|
| A gates | 4,283 | 3,528 |
| A-gate reduction | — | 755 (17.6% of A; 6.1% of A+B+cleanup) |
| B gates | 1,918 | 1,918 |
| cleanup gates | 6,260 | 6,260 |
| local paid profile | `{1:2548, 2:338, 3:430, 4:194, 5:56, 8:8}` | identical |
| conditional κ | `0.001661634653669567` | identical |

The output word has canonical content SHA-256 `9094660307632862c3b09027a736fe93d397e88fa74806755a2e83198c060844`; the input X4 word is `1e1d99ba7aab877d6b573c41f7030ee73de9a52fee51d0a822ddaae71251999`.

## Verification

`search/reproduce.py` regenerates the exact output word from the pinned input and checks the complete A+B scalar map. The saved receipts then record the independent checks:

- 728 arbitrary columns in both orientations and all native frame chains pass.
- 25 scalar/frame/wrapper negative controls pass; wrapper exactness passes.
- All 2,949 directed phase edges and 224 endpoint adapters pass.
- The complete owner, invoice, two exact moment engines, 47 outer inequalities, admission controls, and PR589 bit controls pass.
- The global assembly remains `κ = 0.001661634653669567`; the gain is a lower finite scalar invoice, not a new exponent claim.

To reproduce the word:

```sh
python3.11 search/reproduce.py \
  --input /path/to/PR799-X4/FULL-WORD.json.gz \
  --out /tmp/gauge44-a-resynth/FULL-WORD.json.gz
```

The full resynthesis receipt is in `artifacts/RECIPE.json`; global and local receipts are in `artifacts/`.

This is conditional on the repository's inherited compiler, hosting, precision/tape, analytic-transfer, and bit interfaces. It does not claim an unconditional multiplication theorem or a new κ.

## Upstream follow-up replay

This package is a follow-up to the merged [PR #799](https://github.com/CrocSwap/integer-mult-bounds/pull/799). It was cold-replayed against the current main checkout used for this submission (main `12fa8c5c`):

```sh
python3 -B research/gauge44-a-resynthesis/verify.py --work /tmp/gauge44-a-resynthesis
```

The command replays the package-local global verifier against the repository's pinned dependencies and checks the frozen candidate hash. The exact A-block search can be rerun with `search/reproduce.py` when the PR #799 X4 input word is available.

The live execution receipt is frozen in `artifacts/CURRENT-MAIN-LIVE-REPLAY.json`. It records a fresh run of the package verifier from package logic commit `e83aaa13` against the full repository checkout at main `12fa8c5c844be21bfefb38a19503fbd867a11244`; every restore, bind, emit, audit, invoice, assembly, admission-control, and bit-supplier-control stage exited zero, with the same `κ = 0.001661634653669567` and candidate SHA.
