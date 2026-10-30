# Prime-exponent group labels cost one rank unit per target

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with exact finite corroboration; no new κ.** This uses Ali
Romman's relaxed group-gate model ([PR #5394](https://github.com/CrocSwap/integer-mult-bounds/pull/5394),
`research/group-subproduct-cover`), unchanged. Let G be a group of prime
exponent and K any field. Any diagonal target with d nonidentity entries,
repetitions allowed, needs total projector rank at least d. Arbitrary
finite clean or dirty scalar workspace and singular or rectangular free
maps do not change this. The rank-one count is therefore exactly d whenever
every target label is allowed.

This answers that package's Open next question for these groups. The
rank-one count exceeds the relaxed subproduct-cover cost exactly when the
cover is shorter than d. The gap can be exponential: in (C2)^n, the
2^n − 1 nonidentity labels have cover cost n and rank-one count 2^n − 1.

## Method

[PROOF.md](PROOF.md) proves a representation rank cut. For any
representation ρ over an extension field,

    Σ_i rank(ρ(t_i) − I)  ≤  Σ_j rank(N_j) · rank(ρ(g_j) − I).

The left regular permutation representation over K itself has
rank(ρ(g) − I) = |G|(1 − 1/ord g) in every characteristic. In a group of
prime exponent every nonidentity label gives the same value, and the
bound becomes d.

## Evidence

[verify.py](verify.py) uses only the standard library. It is read-only and
uses no network or Git. It checks:

- the regular defect rank formula for all 405 element/field pairs in
  (C2)^2, (C2)^3, (C2)^4, (C3)^2, C5, the order-27 Heisenberg group, C4 and
  Q8, over Q, F2, F3, F5 and F7;
- 206 seeded random circuits with rectangular and singular free maps,
  projectors of every rank, and any labels. Each circuit checks the
  augmentation identity and multiplicativity of the entrywise regular image,
  and that the cut holds;
- exact cover costs 2, 3 and 4 for all nonidentity targets of (C2)^2, (C2)^3
  and (C3)^2. For those groups, over Q, F2 and F3, it checks the attaining
  cover word and the direct d-gate word, both with an untouched dirty role.
  It also checks the length-4 basis cover of all 15 labels in (C2)^4 over F2;
- five controls: a dropped cover letter, the C4 case where the regular cut
  alone is weaker, Q8 with mixed orders, a zero identity defect, and a
  rank-two projector.

The finite checks corroborate the written proof. They do not replace its
all-group, all-field argument.

## Reproduce

From the repository root, with CPython 3.12 (here
`/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12`; any CPython 3.12
works):

```sh
python3.12 -I -B -W error research/prime-exponent-rank-cut/verify.py
python3.12 -I -O -B -W error research/prime-exponent-rank-cut/verify.py
python3.12 -B scripts/research_package.py --package research/prime-exponent-rank-cut
python3.12 -B scripts/check_research_commit.py --package research/prime-exponent-rank-cut --check-source-history
```

The verifier ends with
`PASS_PRIME_EXPONENT_RANK_CUT regular_checks=405 random_circuits=206 separations=4 controls=5 no_new_kappa`.
It runs in under a second locally. No receipt file is written. The printed
JSON summary is the run record.

## Limits

This is an abstract count in an optimistic relaxed model. It does not price
physical group gates, scalar maps, source reads, precision, recursive
children, hosting or cleanup. The selected frontier and κ are unchanged.
Groups without prime exponent are not settled. For three copies of a² in C4
the regular cut alone gives 2, not 3. PROOF.md section 6 notes that
faithful characters give the same d bound for cyclic groups when the
characteristic does not divide the order; that remark has no separate
finite check here. No independent human or formal proof-kernel review is
claimed.

## Credit and overlap

- Ali Romman, [PR #5394](https://github.com/CrocSwap/integer-mult-bounds/pull/5394)
  (`research/group-subproduct-cover`): model, cover theorem, the question,
  and the all-group three-label rank-one floor. It is cited, not re-verified.
- Wentao Li, `research/elementary-abelian-diagonal-minimum`: the rank-one
  minimum t in F2[(C2)^k]. Corollary 3 contains that statement and extends
  it to every field, every prime, nonabelian prime-exponent groups,
  projectors of any rank and singular free maps.
- Rank telescoping through a representation: this account's
  [PR #5202](https://github.com/CrocSwap/integer-mult-bounds/pull/5202)
  (`research/order21-normal-tariff`) and the character twist in
  `research/cut58-separable-query-floor`.

## Open next questions

1. For groups without prime exponent, is the rank-one count always at least
   the number of nonidentity entries? The first case is three copies of a²
   in C4. The regular cut gives 2, and a top-coefficient argument may give 3.
2. Which positive combination of permutation representations gives the
   best cut for a fixed group and target, for example in D8 or Q8 over F2?
   This is a finite linear program over transitive G-sets, and it is valid
   in every characteristic.
3. Does any physically realizable label family have prime exponent and a
   priced native implementation? Without one, these counts do not move a
   supplier bill.
