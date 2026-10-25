# Any-register four-call floor for the PSL(2,7) conjugate 7-cycle pair

**Research construction / algebraic any-register bound; no new kappa.** Answers
open question 2 of open
[#4089](https://github.com/CrocSwap/integer-mult-bounds/pull/4089)
(`research/a5-conjugate-any-registers`): does the same support-plus-middle-projector
pattern give any-register floors for other perfect-group conjugate-pair
alphabets?

**Yes, for `PSL(2,7) ≅ GL(3,F2)`.** In `M_r(F2[PSL(2,7)])` with paid labels
`{x,y}` (`x` order 2, `y` order 3, `xy` and `yx` distinct order-7 elements) and
every binary rank-one idempotent, the target

```text
diag([xy], [yx], [e], …, [e])
```

has exact paid-call minimum **four** for every finite register width `r >= 2`:

- The direct word `D_{E00}(x) D_{E00}(y) D_{E11}(y) D_{E11}(x)` attains the
  target for every `r >= 2`.
- Support filter: among all words of length `≤ 3` over `{x,y}`, only `xyx` and
  `yxy` have subsequence-support containing both 7-cycles.
- Each of those patterns forces the middle projector `B = E00+E11`, which has
  **rank 2** and is therefore outside the rank-one paid alphabet.

This is a written support-plus-coefficient proof on a **different** perfect-group
alphabet from #4089 / #2246. It does not reprint the A5 5-cycle census and does
not reopen the deferred A5 width-4 BFS.

**No new kappa.** Selected κ stays `0.001672660197076918`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/psl27-conjugate-any-registers/verify.py
python3.12 -I -O -Werror -B research/psl27-conjugate-any-registers/verify.py
python3.12 -I -B research/psl27-conjugate-any-registers/independent.py
python3.12 -I -B research/psl27-conjugate-any-registers/test_package.py
python3.12 -B scripts/research_package.py --package research/psl27-conjugate-any-registers
```

Expected:

```text
PASS_PSL27_CONJUGATE_ANY_REGISTERS minimum=4 roles=all_finite_r>=2 group_order=168 support_patterns=['xyx','yxy'] forced_B_rank=2 ... no_new_kappa
PASS_INDEPENDENT_PSL27_CONJUGATE_ANY_REGISTERS gl3_order=168 support_patterns=['xyx','yxy'] forced_B_outside_rank_one ... no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/psl27-conjugate-any-registers outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O -Werror` also passes.
Duplicate JSON keys and on-disk certificate corruption (temp copy) are rejected.

## Scope and overlap

Base commit `bb4bccbf42844d2801487450727c2f63e10d1d0f` (CrocSwap/main). Direct
predecessor ask: #4089 OQ2 (other-alphabet support lemma). Methodological
credit: #2246 / `a5-conjugate-5cycle-seedd316f8` for the A5 floor that #4089
lifted; Q8 any-register coefficient style. Preferred #2687 admitted BIT-supplier
and #2888 non-toy fitted-`k`/GL64 Incoming were not grounded within budget
without repeating deferred thin obstructions.

Soft-overlap versus #4089 is intentional successor semantics on harness shape
(support filter + coefficient chase), with **new** group order `168`,
`(2,3,7)` generators, independent full-`GL(3,F2)` rebuild, and a distinct
7-cycle endpoint. Clear of leave-alone dirty-role-minimum cascade
(#4083/#4084 + deferred A5 width-4), dicyclic depth layers, dihedral
nine-prime, precision-blind Norm, PR2298, odd-kernel thin retargets, UT4
unfinished, and PR2809 cascades. Does not reprint the A5 `xyx`/`yxy` rank-2
argument as an A5 claim.

## Open next questions

1. Is there a priced native address-operation realization of this PSL(2,7)
   `(2,3,7)` alphabet inside an admitted BIT supplier?
2. Does a uniform lemma cover every perfect group admitting a `(2,3,p)`
   conjugate-pair presentation with the same length-3 support filter?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit #4089 for the other-alphabet OQ; #2246 /
`a5-conjugate-5cycle-seedd316f8` for the A5 conjugate floor; PR840 construction
pattern; Q8 any-register coefficient style as methodological credit only. No
independent human review is claimed. No new kappa.
