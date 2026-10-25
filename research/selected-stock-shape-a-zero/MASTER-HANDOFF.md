# Handoff: selected stock shape A = 0 (m=73 complex)

## Result

Under the finite-stock-as-C reading already named by
`research/selected-coarse-depth-stock/PROOF.md`, the selected m=73 complex
producer's per-level divisor candidate is independent of atom width `w`, so
the shape bound `log_2 C(w) <= A*w + B` holds with **A = 0** and **B = 2642**.
Leaf reserve `rho` remains unbound. Selected κ is unchanged at
`0.001672660197076918`.

Pinned main: `6f100d4bb5083f8c35d96fd95a539811c62f245c`.
Branch: `cursor/selected-stock-a-zero-60b9`.
Scientific package tip: `9b257d8e75bf205d150b4d2a6a8280f5e1d8f76a` (Co-authored-by Victor Li stripped from branch).
Branch tip: this commit (git rev-parse HEAD on the branch).
Package: `research/selected-stock-shape-a-zero`.

## Switch

Did not switch cards. Preferred obligation 1 (selected-stock-envelope OQ1:
bind A or prove A=0) was still open after #3113. Avoided recomputing B=2642 /
halving. Did not take P104 coefficient work (soft overlap with open
#3363/#3365/#3371/#3372) or scatter-export schema (would need identical-receipt
tooling bar).

## Exact commands (expected PASS)

```sh
python3.12 -I -B research/selected-stock-shape-a-zero/verify.py
# PASS_SELECTED_STOCK_SHAPE_A_ZERO A=0 B_bits=2642 rho=unbound no_digit_tower_lift no_new_kappa

python3.12 -I -O -B research/selected-stock-shape-a-zero/verify.py
# same marker

python3.12 -I -B research/selected-stock-shape-a-zero/independent.py
# PASS_SELECTED_STOCK_SHAPE_A_ZERO A=0 B_bits=2642 rho=unbound no_digit_tower_lift no_new_kappa_INDEPENDENT

python3.12 -I -B research/selected-stock-shape-a-zero/test_package.py
# PASS_SELECTED_STOCK_SHAPE_A_ZERO_TESTS groups=6

python3.12 -B scripts/research_package.py --package research/selected-stock-shape-a-zero
# PASS_REGISTERED_RESEARCH_PACKAGE research/selected-stock-shape-a-zero outcome=completed
```

## Closest priors

- [#3113](https://github.com/CrocSwap/integer-mult-bounds/pull/3113)
  `research/selected-stock-envelope-m73` — bound B_bits=2642, left A,B,rho unbound.
- [#2105](https://github.com/CrocSwap/integer-mult-bounds/pull/2105)
  `research/selected-coarse-depth-stock` — 43/26 depth and shape composition.
- [#2084](https://github.com/CrocSwap/integer-mult-bounds/pull/2084)
  `research/selected-bit-parent-reserve` — ordinary BIT A≥4096 contrast.

## Soft-overlap risks

- Do not read this as recomputing #3113's B_bits or halving.
- Do not read A=0 as a closed sigma envelope (rho and finite-stock-as-C
  admission remain).
- Ordinary BIT packages that bind positive A are contrast only.

## What remains open

Bind `rho` (or prove `rho=0`); maintainer adoption of finite stock as uniform
`C(w)`.

## Credit

Aaron Wang (#3113), Sricharan Vagvala (#2105), Adam Gall (#2084), retained
cover notes. Notices untouched.

Prepared by Wentao Li with substantial AI assistance.
