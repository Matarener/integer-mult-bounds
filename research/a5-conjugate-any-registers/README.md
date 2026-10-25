# Any-register four-call floor for the A5 conjugate 5-cycle pair

**Research construction / algebraic any-register bound; no new kappa.** Answers
the open algebraic-invariant question of
[`research/a5-conjugate-5cycle-seedd316f8`](../a5-conjugate-5cycle-seedd316f8/README.md)
(merged as [#2246](https://github.com/CrocSwap/integer-mult-bounds/pull/2246)):
for every finite register width `r >= 2`, the dirty-register target

```text
diag([xy], [yx], [e], …, [e])
```

in `M_r(F2[A5])` with paid labels `{x,y}` generating `A5` and every binary
rank-one idempotent has exact paid-call minimum **four**. Extra dirty spectator
roles cannot lower the bill. This is a written support-plus-coefficient proof,
not another fixed-width BFS census.

The direct four-call word on roles `0` and `1` attains the target for every
`r`. Every word of length at most three is excluded: only the label patterns
`xyx` and `yxy` can even place both 5-cycles in the group-algebra support, and
each of those patterns forces the middle projector to equal the rank-two matrix
`E00+E11`, which is not a paid rank-one idempotent.

**No new kappa.** Selected κ stays `0.001672660197076918`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/a5-conjugate-any-registers/verify.py
python3.12 -I -O -Werror -B research/a5-conjugate-any-registers/verify.py
python3.12 -I -B research/a5-conjugate-any-registers/independent.py
python3.12 -I -B research/a5-conjugate-any-registers/test_package.py
python3.12 -B scripts/research_package.py --package research/a5-conjugate-any-registers
```

Expected:

```text
PASS_A5_CONJUGATE_ANY_REGISTERS minimum=4 roles=all_finite_r>=2 support_patterns=['xyx','yxy'] forced_B_rank=2 ... no_new_kappa
PASS_INDEPENDENT_A5_CONJUGATE_ANY_REGISTERS even_permutations=60 support_patterns=['xyx','yxy'] forced_B_outside_rank_one ... no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/a5-conjugate-any-registers outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O -Werror` also passes.
Duplicate JSON keys and on-disk certificate corruption (temp copy) are rejected.

## Scope and overlap

Base commit `bb4bccbf42844d2801487450727c2f63e10d1d0f` (CrocSwap/main). Direct
predecessor: `a5-conjugate-5cycle-seedd316f8` / #2246 (two- and three-role
minimum 4; asks for an algebraic all-roles invariant). Preferred #2687
admitted BIT-supplier and #2888 non-toy fitted-`k`/GL64 Incoming were not
grounded within budget without repeating deferred thin obstructions. This
package takes the disjoint #840-style branch requested by the #2246 deferral
note (prefer the invariant lemma over further role-count BFS). Clear of
leave-alone dirty-role-minimum cascade (#4083/#4084 + deferred A5 width-4
census), dicyclic depth layers, dihedral nine-prime, precision-blind Norm,
PR2298, odd-kernel thin retargets, UT4 unfinished, and PR2809 cascades.

Soft-overlap versus #2246 is intentional successor semantics (same alphabet and
endpoint; new all-`r` proof replaces finite search). Soft-overlap versus the
deferred width-4 BFS package is low on method (no BFS layers; coefficient chase)
while answering the same invariant ask.

## Open next questions

1. Is there a priced native address-operation realization of this A5 `(2,3,5)`
   alphabet inside an admitted BIT supplier?
2. Does the same support-plus-middle-projector pattern give any-register floors
   for other perfect-group conjugate-pair alphabets (e.g. other `(2,3,5)`
   presentations)?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit #2246 / `a5-conjugate-5cycle-seedd316f8` for the two-/three-role
theorem and the invariant OQ; PR840 construction pattern; Q8
any-register coefficient style as methodological credit only. No independent
human review is claimed. No new kappa.
