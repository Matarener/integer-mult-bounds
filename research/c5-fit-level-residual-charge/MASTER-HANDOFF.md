# Handoff: fit-level residual C5 local-opt charging fails on diagonal I

## Result

The natural coefficient-sensitive completed-fit inequality
`sum_C Cost_opt(K|_C) <= Cost_opt(K)` **fails** on `K = I_112`: granting all
23 physical C5 floors of 20 gives LHS ≥ 460, while the explicit diagonal
decomposition `I = sum_i e_i e_i^T` has complete-plane tariff exactly 224.
Dual scanners agree. Selected κ unchanged at `0.001672660197076918`.

Pinned CrocSwap main tip (branch base): `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
Scientific geometry base (SOURCES): `463113d675af7410ac91d53a4fed51ec6494eb9a`.
Branch: `cursor/c5-fit-level-residual-charge-fe94`.
Scientific package tip: `c8a6fa90dde7a2d0ac5dedd601d7122802fa4815` (Wentao-only; no `Co-authored-by: Victor Li`).
Branch tip: this commit (`git rev-parse HEAD` on `cursor/c5-fit-level-residual-charge-fe94`).
Package: `research/c5-fit-level-residual-charge/`.

## Switch

Preferred next47 commoncut35 OQ from `research/p112-mixed566-cut34` is already
answered on main by `research/p112-mixed566-cut35` (and cut36 has a literal
counterexample). Did not reprint that bill. Primary fallback
`c5-four-residual-floors` direct global-charging OQ is already answered by
`c5-global-charging-obstruction` / `c5-global-charging-ceiling` (termwise
ceiling `180/7`). Took the **successor** coefficient-sensitive completed-fit
OQ from those packages, scoped to the residual/local-opt candidate.

Avoided: P104 side-correction leave-alones; stock-leaf class-only `S_leaf=1`
DEFERs; centre-path soft-overlap with open `#3120`/`#3548`/`#3147`.

## Exact commands (expected PASS)

```sh
python3.12 -I -W error -B research/c5-fit-level-residual-charge/verify.py
# PASS_C5_FIT_LEVEL_RESIDUAL_CHARGE cycles=23 local_floor_sum=460 diagonal_cost=224 inequality_holds=false

python3.12 -I -O -W error -B research/c5-fit-level-residual-charge/verify.py
# same marker

python3.12 -I -W error -B research/c5-fit-level-residual-charge/independent.py
# PASS_C5_FIT_LEVEL_RESIDUAL_CHARGE_INDEPENDENT cycles=23 local_floor_sum=460 diagonal_cost=224 inequality_holds=false

python3.12 -I -O -W error -B research/c5-fit-level-residual-charge/test_verify.py
# 9 tests OK

python3.12 -W error -B scripts/research_package.py --package research/c5-fit-level-residual-charge
# PASS_REGISTERED_RESEARCH_PACKAGE research/c5-fit-level-residual-charge outcome=completed
```

## Closest priors

- `research/c5-global-charging-obstruction` — termwise fixed-weight ceiling `180/7`; leaves coefficient-sensitive completed-fit OQ.
- `research/c5-global-charging-ceiling` — same method audit; same successor OQs.
- `research/c5-four-residual-floors` — local floors and original global-charging handoff wording.

## Soft-overlap risks

- Do not read this as reprinting the termwise `180/7` bill or the four residual local proofs.
- Do not read `460 > 224` as a new global decoder floor; it falsifies one charging candidate.
- J-bearing identity extensions do **not** discriminate the candidate (they are too expensive); the diagonal fit does.
- Preferred mixed566 commoncut35 / cut34 bills are leave-alone priors, not dependencies.

## What remains open

Does an explicit cancellation identity (beyond residual local-opt costs) give
a valid fit-level charge that beats the termwise `180/7` ceiling?

## Credit

Nick Petalas (termwise charging obstruction/ceiling), Krzysztof Wójt
(four-residual floors handoff), Tekalign/PR2782, Cinna Davis/PR1825, Adam
Gall/PR1889, thakrarsagar/PR3256, retained matching lineage.

Prepared by Wentao Li `<wentaol4@illinois.edu>` with substantial AI assistance.
No CrocSwap PR opened (donor instruction).
Python 3.12.3
Linux x86_64
