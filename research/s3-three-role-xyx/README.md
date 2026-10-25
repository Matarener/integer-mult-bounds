# One dirty role does not lower the S3 longest Coxeter double minimum

**Research construction / finite exact minimum; no new kappa.** Answers the
three-register open question of
[`research/bit-s3-two-target-census-seed36501`](../bit-s3-two-target-census-seed36501/README.md)
for the fixed target `diag([xyx],[xyx],1)`: does one arbitrary restored dirty
scalar role permit a shared-call saving below the two-register six-call bill?

**No.** In `M₃(F₂[S₃])` with target

```text
diag([xyx], [xyx], [e]),
```

the exact paid-call minimum remains **six**:

- Paid labels `{x,y}` and all **28** rank-one idempotents of `M₃(F₂)` give
  **56** factors.
- Exact involution meet-in-the-middle covers every word of length `0..5`
  via `ball(I,2) ∩ ball(T,3)` and the symmetric split (both empty).
- Identity and target balls through radius three have layer sizes
  `[1, 56, 1750, 45396]`.
- The direct six-call word on roles `0..1` attains the target and restores the
  dirty role to `[e]`.
- No length-`≤5` witness exists, so the minimum is exactly six.

This is a finite formal-algebra theorem, not a physical supplier invoice.
**No new kappa.** Selected κ stays `0.001672660197076918`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/s3-three-role-xyx/verify.py
python3.12 -I -O -Werror -B research/s3-three-role-xyx/verify.py
python3.12 -I -B research/s3-three-role-xyx/independent.py
python3.12 -I -B research/s3-three-role-xyx/test_package.py
python3.12 -B scripts/research_package.py --package research/s3-three-role-xyx
```

Expected:

```text
PASS_S3_THREE_ROLE_XYX roles=3 calls=56 idempotents=28 target_minimum=6 ... dirty_lowers=false short_witness=none no_new_kappa
PASS_INDEPENDENT_S3_THREE_ROLE_XYX roles=3 calls=56 target_minimum=6 ... hits=0 dirty_lowers=false no_new_kappa
PASS_S3_THREE_ROLE_XYX_PACKAGE_TESTS groups=7
PASS_REGISTERED_RESEARCH_PACKAGE research/s3-three-role-xyx outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` also passes.

## Scope and overlap

Base commit `bb4bccbf42844d2801487450727c2f63e10d1d0f` (CrocSwap/main). Direct
predecessor: `bit-s3-two-target-census-seed36501` (two-register no-sharing;
three-role OQ answered here for this fixed target). Soft overlap ≈0.30–0.50 vs
that package (shared S3 transposition alphabet; new three-role projectors,
dirty target coordinate, and 56-factor MITM). Clear of leave-alone #4083
SL2(F3) dirty-role, #4078 dihedral nine-prime census, odd-kernel / #2687 thin
tariff retargets, #2888 F_I GL2(F3) toys, precision-blind Norm, PR2298 §3,
UT4 unfinished, and PR2809 cascades.

Preferred #2687 admitted BIT-supplier and #2888 non-toy fitted-`k`/GL64
Incoming were not grounded within budget without repeating deferred thin
obstructions; this package takes the disjoint #840-style construction branch.

## Open next questions

1. Does a fourth restored dirty scalar role lower the six-call minimum for
   this same S3 longest Coxeter double target?
2. Is there a priced native address-operation realization of this alphabet
   inside an admitted BIT supplier?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit Cinna Davis / `bit-s3-two-target-census-seed36501` for the
two-register theorem and three-role OQ; PR840 construction pattern; PR288
register-model lineage. No independent human review is claimed. No new kappa.
