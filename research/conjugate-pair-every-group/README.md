# The conjugate-pair target needs four calls in every group

**Scoped written theorem in a formal group-algebra model, with finite
corroboration; no new κ.** This contribution was produced by Nick Petalas.
New work is Apache-2.0.

Let `G` be any group, `F` any field and `x, y ∈ G` with `xy ≠ yx`. In the
rank-one-idempotent register model of
[#4089](https://github.com/CrocSwap/integer-mult-bounds/pull/4089), with paid
factors `I + ([g]-[e])N` for `g ∈ {x, y}`, the target

```text
T = diag([xy], [yx], [e], …, [e])  ∈ M_r(F[G])
```

has exact paid-call minimum **four** at every width `r ≥ 2`. Extra dirty
spectator roles never lower the bill.

This answers Open next question 2 of Wentao Li's
[#4089](https://github.com/CrocSwap/integer-mult-bounds/pull/4089)
(`research/a5-conjugate-any-registers`) for every conjugate-pair alphabet at
once. #4089 proves the A5 case over F2 and Wentao Li's
[#4093](https://github.com/CrocSwap/integer-mult-bounds/pull/4093) proves
PSL(2,7). Both use a support filter specific to their group: they check that
only `xyx` and `yxy` can carry both `xy` and `yx`. In a general group,
coincidences such as `x²y = yx` defeat that filter. The new proof handles them.

## The new step

[PROOF.md](PROOF.md) has the full argument. Each factor is written as
`[g]N + (I-N)`, so a three-call product is `Σ_U [g_U] P_U` with
`P_U = X_1 X_2 X_3` and `X_i ∈ {N_i, I-N_i}`. Multiplying a coefficient on the
left by `N_1` or `I-N_1` and on the right by `N_3` or `I-N_3` isolates one
corner of subsets. This yields three uniform lemmas:

1. the single-call products `P_{1}, P_{2}, P_{3}` vanish;
2. the `(I-N_1, I-N_3)` corner of the `xy` and `yx` coefficients vanishes;
3. `P_{12}` and `P_{23}` are not both nonzero.

The patterns `xyx` and `yxy` then fail by Lemma 3. The patterns `xxy`, `yyx`,
`xyy` and `yxx`, which can survive the support test when `G` has a suitable
coincidence, fail by a rank-one column/row mismatch. Words of length at most
two fail by support alone. The proof uses no generation, perfectness, element
order or field characteristic.

The noncommuting hypothesis is needed: for `y = x⁻¹` the target is `I`.

## Evidence

| Claim | Kind | Evidence |
|---|---|---|
| no word of length ≤ 3, every `G`, `F`, `r` | written proof | [PROOF.md](PROOF.md) |
| four calls suffice | construction | direct word `D_{E00}(x) D_{E00}(y) D_{E11}(y) D_{E11}(x)` |
| finite cross-check | exact finite certificate | `verify.py` |

`verify.py` checks the expansion and corner identities on 200 seeded rational
triples. It collects the 82 distinct length-4 word-coincidence signatures of
noncommuting pairs in S3, S4, S5, Q8 and the free group. The direct word and
its four one-call deletions are checked on each. Their words of length 1..3
reduce to 26 subset-class keys. Every key is excluded exhaustively over F2 at
widths 2 and 3 and over F3 at width 2. The finite check corroborates the proof
and does not replace it: it covers neither all groups nor all widths.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/conjugate-pair-every-group/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/conjugate-pair-every-group/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/conjugate-pair-every-group
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/conjugate-pair-every-group --check-source-history
```

Any CPython 3.12 may replace that interpreter path. The expected marker is
`PASS_CONJUGATE_PAIR_EVERY_GROUP`; each run takes about five seconds locally.

## Limits

This is a theorem in the formal group-algebra model only. It prices no native
address operation, conversion, restoration or recursive caller, and it is not
a multiplication theorem. The selected κ is unchanged. The proof has had no
independent human or proof-kernel review.

## Open next questions

1. Which diagonal pair targets `diag([g],[h])` in an arbitrary group admit
   cross-register sharing below the sum of their positive word lengths? The
   corner-sandwich lemmas may give uniform floors in place of per-group
   censuses such as the S3 and Q8 pair censuses. First step: try
   `diag([xyx],[yxy])` at length five. Longer words have more corners and
   coincidence patterns; no general lemma is supplied here.
2. Is there a priced native nonabelian address alphabet inside an admitted
   BIT supplier? This theorem shows that the conjugate-pair target offers no
   saving in any group, so such a proposal must find its gain elsewhere.

The same questions are structured in [TASK.json](TASK.json).

## Credit

Wentao Li ([#4089](https://github.com/CrocSwap/integer-mult-bounds/pull/4089),
[#4093](https://github.com/CrocSwap/integer-mult-bounds/pull/4093)) supplied
the model, the any-register A5 and PSL(2,7) theorems and the open question.
Cinna Davis ([#2246](https://github.com/CrocSwap/integer-mult-bounds/pull/2246))
supplied the original A5 target and its fixed-width result. Their results are
cited, not re-checked. Source pins are in [SOURCES.json](SOURCES.json).
