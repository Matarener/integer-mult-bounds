# Exact PR2298 §3 operation counts on mixed adjacent widths

**Research construction / recursive interface; no new kappa.** Answers open
question 2 of
[`pr2298-format-recovery-audit`](../pr2298-format-recovery-audit/README.md)
(merged [#2413](https://github.com/CrocSwap/integer-mult-bounds/pull/2413)):
are the section-3 exchange counts right?

**Yes**, on every mixed adjacent bit-width pattern at `d≤8`:

| Invoice | Exact count |
|---|---|
| Axis-order reversal | `⌊d/2⌋` exchanges |
| Tensor expose/restore map | `2(d−1)` exchanges |
| One-extra-bit pair | 1 interchange + 1 bit move |
| Equal-width pair | 1 interchange |

Census size: `∑_{d=1}^{8} 2^d = 510` patterns with widths in `{3,4}` (the
mixed `r/2`/`r` domain). Sharp at `d=8`: reversal `4`, tensor `14`. Physical
spot-checks replay the low-level `(swap|move)` stream through the pinned
`physical.move_address` oracle.

This is an exact schedule invoice, not a reprint of the prose bounds alone and
not a retarget of `selected-conservative-outer/checks.py`'s algebraic CRT
fixture (different domain, separate interchange/bit-move tallies, bound
assertions).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/pr2298-section3-opcounts/verify.py
python3.12 -I -O -Werror -B research/pr2298-section3-opcounts/verify.py
python3.12 -I -B research/pr2298-section3-opcounts/independent.py
python3.12 -I -B research/pr2298-section3-opcounts/test_package.py
python3.12 -B scripts/research_package.py --package research/pr2298-section3-opcounts
```

Expected:

```text
PASS_PR2298_SECTION3_OPCOUNTS patterns=510 max_d=8 rev_bound=floor(d/2) tensor_bound=2(d-1) one_extra_bit=1+1 sharp_d8_rev=4 sharp_d8_tensor=14 no_new_kappa
PASS_INDEPENDENT_PR2298_SECTION3_OPCOUNTS patterns=510 max_d=8 rev_bound=floor(d/2) tensor_bound=2(d-1) no_new_kappa
PASS_PR2298_SECTION3_OPCOUNTS_PACKAGE_TESTS groups=5
PASS_REGISTERED_RESEARCH_PACKAGE research/pr2298-section3-opcounts outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()`; `-O` also passes.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap/main). Closest
priors: PR2298 §3; #2413 OQ2; Colkitt nonadjacent-axis audit. Soft-overlap with
`checks.py` CRT algebra is moderate (shared elementary schedule, distinct
exhaustive mixed-width census and bound ledger). Leave-alone precision-blind /
odd-kernel / PR2809 / route-cube / UT4 clusters were not reopened.

## Open next questions

1. Do the same closed forms hold for non-adjacent width gaps larger than one
   bit?
2. Can section 7's exposure exponent be expanded from these counts into a
   fully numerical chunk-swap ledger at fixed `(d,ell,tau)`?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit Jose Manuel / PR2298, #2413, Douglas Colkitt's nonadjacent
audit, and the synthetic-layout physical oracle. No independent human review is
claimed. No new kappa.
