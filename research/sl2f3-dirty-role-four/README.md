# One dirty role does not lower the SL2(F3) conjugate-triple minimum

**Research construction / finite exact minimum; no new kappa.** Answers the
open dirty-role question of
[`research/sl2f3-conjugate-triple-seed592f`](../sl2f3-conjugate-triple-seed592f/README.md):
does one arbitrary restored dirty scalar role lower the five-call minimum for
`diag([i],[w],[w^{-1} i w])` in `F_2[\mathrm{SL}_2(\mathbb F_3)]`?

**No.** In `M_4(F_2[\mathrm{SL}_2(\mathbb F_3)])` with target

```text
diag([i], [w], [c], [e]),    c = w^{-1} i w,
```

the exact paid-call minimum remains **five**:

- Paid labels `{i, i^{-1}, w, w^{-1}}` and all **120** rank-one idempotents of
  `M_4(F_2)` give **480** factors.
- Exact meet-in-the-middle covers every word of length `0..4`
  (`480^4` raw four-call words via `2+2` joins).
- Two-call table: **230400** words, **165261** distinct exact states; every
  pair is cross-checked against full group-algebra convolution.
- The direct five-call conjugate word on roles `0..2` attains the target and
  restores the dirty role to `[e]`.
- No length-`≤4` witness exists, so the minimum is exactly five.

This is a finite formal-algebra theorem, not a physical supplier invoice.
**No new kappa.** Selected κ stays `0.001672660197076918`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/sl2f3-dirty-role-four/verify.py
python3.12 -I -O -Werror -B research/sl2f3-dirty-role-four/verify.py
python3.12 -I -B research/sl2f3-dirty-role-four/independent.py
python3.12 -I -B research/sl2f3-dirty-role-four/test_package.py
python3.12 -B scripts/research_package.py --package research/sl2f3-dirty-role-four
```

Expected:

```text
PASS_SL2F3_DIRTY_ROLE_FOUR group=24 roles=4 calls=480 idempotents=120 target_minimum=5 pair_words=230400 distinct_pair_states=165261 dirty_lowers=false short_witness=none no_new_kappa
PASS_INDEPENDENT_SL2F3_DIRTY_ROLE_FOUR group=24 roles=4 calls=480 target_minimum=5 distinct_pair_states=165261 dirty_lowers=false no_new_kappa
PASS_SL2F3_DIRTY_ROLE_FOUR_PACKAGE_TESTS groups=4
PASS_REGISTERED_RESEARCH_PACKAGE research/sl2f3-dirty-role-four outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` also passes.

## Scope and overlap

Base commit `bb4bccbf42844d2801487450727c2f63e10d1d0f` (CrocSwap/main). Direct
predecessor: `sl2f3-conjugate-triple-seed592f` (three-role minimum 5; dirty-role
OQ answered here). Soft overlap ≈0.35–0.55 vs that package (shared group and
generators; new four-role alphabet, dirty target coordinate, and 480-factor
census). Clear of leave-alone odd-kernel, PR2298/Colkitt, precision-blind,
dihedral-census, UT4, and PR2809 cascades.

## Open next questions

1. Do two or more restored dirty scalar roles lower the five-call minimum for
   this same `SL2(F3)` endpoint?
2. Is there a priced native address-operation realization of this alphabet
   inside an admitted BIT supplier?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit Cinna Davis / `sl2f3-conjugate-triple-seed592f` for the
three-role theorem and dirty-role OQ; PR1822 Q8 lineage; PR468 / PR288
register-model lineage. No independent human review is claimed. No new kappa.
