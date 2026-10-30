# Two 3-cycles need at least ten calls in every address dimension

**Written proof with finite corroboration in a formal model. No new κ.**
The selected conditional exponent stays 62009/20000000.

## Result

In the formal model `M_2(F2[GL_n(F2)])` of #4939/#4950/#4968, a paid call is
`I + ([g]+[e])N` with `g` a coordinate CNOT and `N` a rank-one binary
idempotent. Free scalar maps are allowed and equality is formal. Let `c` be a
coordinate 3-cycle and let every other address coordinate be a spectator that
the target restores.

For **every** `n >= 3`, `diag([c],[c])` has no word of length at most 9. A word
of length 10 or 11 at any `n` would give one at `n = 5` with a narrow profile:

* both spectators written at least twice and read at least twice;
* each target coordinate written and read at least twice;
* (target, spectator) write counts `(6,4)`, `(6,5)` or `(7,4)`;
* at least one call writing a target coordinate from a spectator, and one
  writing a spectator from a target coordinate.

Hence `10 <= cost <= 12` for every `n >= 5`. Before this note, the known lower
bound for `n >= 5` was the single-cycle cost 6 of `research/three-cycle-address-floor`.
Exact cost 12 in every dimension is now equivalent to excluding that one
five-coordinate case.

## Why it works

A coordinate written by exactly one call cannot be restored. Project the word
product onto the group elements that leave that row unchanged. The projection
equals `A (I+N) B`, where `A` and `B` are the products before and after the
call. After augmentation, `I+N` has rank one, while the target is invertible.
The same projection forces each target coordinate to be written at least
twice. Transposition turns writes into reads. Spectators that are never written,
or never read, are removed by an exact restriction or quotient homomorphism.
Counting writes then bounds the number of live spectators by two.
[PROOF.md](PROOF.md) gives the complete argument.

## Evidence

[verify.py](verify.py) uses only the standard library and checks the lemmas on
concrete words:

| Check | Coverage |
|---|---|
| Paid calls are involutions | all 120 calls at `n = 5`, `R = 2` |
| `rank(I+N) = R-1` | all 6 idempotents at `R = 2`, all 28 at `R = 3` |
| Single-write projection identity | 150 random words at `n = 5` |
| Restriction and quotient homomorphisms | 60 random words each |
| Transpose anti-automorphism | 60 random words |
| Single-write rank consequence | all 368,136 reduced words of length ≤ 3 at `n = 4` (629,928 cases) |
| Upper bound | the 12-call word at `n = 5`, spectators untouched |
| Counting step | residual profiles `(10,6,4)`, `(11,6,5)`, `(11,7,4)` |
| Controls | a dropped `I+N` factor is rejected |

The random checks test the written lemmas; they do not replace the proof. The
`n = 3` and `n = 4` exclusions are cited premises, not re-run.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -I -W error -B research/two-three-cycles-every-dimension/verify.py
python3.12 -I -O -W error -B research/two-three-cycles-every-dimension/verify.py
python3.12 -B scripts/research_package.py --package research/two-three-cycles-every-dimension
```

Each run prints `PASS_TWO_THREE_CYCLES_EVERY_DIMENSION` in about five seconds.

## Scope

Card `bit-new-register-model`, scope **changed** (see [TASK.json](TASK.json)).
This answers the reduction part of Open next question 1 of James Reed's
[#5379](https://github.com/CrocSwap/integer-mult-bounds/pull/5379)
(`research/spectator-three-cycle-additivity`): every `n` now reduces to `n = 5`,
and lengths up to 9 are excluded everywhere. It does not search `n = 5`, does
not treat a dirty third register, and supplies no native operation, tariff or
κ change.

## Open next questions

1. **Exclude lengths 10 and 11 at `n = 5`.** This would make the cost 12 in
   every dimension. First restrict a meet-in-the-middle search to the three
   write profiles above. Each spectator must be both written and read twice,
   which removes most of the 120-letter alphabet at each position. The blocker
   is the size of the unrestricted ball.
2. **Dirty third register with spectators.** Lemma 1 and the rank argument hold
   for any register count, so the same reduction applies to
   `diag([c],[c],[e])`. It needs base cases at `R = 3` beyond the `n = 3` bound
   of #5292, whose length-11 case is still open.
3. **Sharper write counts.** A two-write analogue of Lemma 1, controlling when
   two writes to one row cancel, might show that each live spectator costs three
   calls. That would remove the residual case without search.

## Credit

The formal model is Mihir Srivastava's #4939. The `n = 3` and `n = 4` exact
costs, and the question, are James Reed / jwr404's #5005 and #5379. The
single-cycle all-dimension reduction of `research/three-cycle-address-floor`
(JoyboyBrian, #4974) suggested the restriction step. Those results are cited,
not re-run or audited. The whole-word projection lemma, the read/write
counting and this reduction were produced by Nick Petalas.
