# Phase-sharp pre-wrapper uniqueness

**One interface lemma. No new κ, no supplier, no selected-frontier change.**

`HyperplaneEnd/Labels.lean` proves `factor_iff_pre` only for scale `1`: if `(N)`
holds and `C` is invertible, then

```text
L^{-1} T_U T_E^{-1} R'^{-1} = C ⊗ id    iff    R' = R.
```

The post-wrapper package `research/hpe-post-wrapper-lemma` states the matching
phase-sharp fact for `L'` and explicitly does not claim the pre-side extension.
This package states that extension and checks it.

## Lemma

Assume `(N)`, `T_U T_E^{-1} = L (C ⊗ id) R`, with `L`, `R'` and `C` invertible
and `λ` a scalar. Then

```text
L^{-1} T_U T_E^{-1} R'^{-1} = λ (C ⊗ id)    iff    R' = λ^{-1} R.
```

In particular `λ = 1` is `factor_iff_pre`. For monomial wrappers the only scales
are `λ ∈ {1, i, -1, -i}`, so the pre-wrapper phase field is the whole freedom:
`R' = i^t R` satisfies the identity at `λ = i^{-t}` and at no other fourth root
of unity.

**Proof.** Substitute `(N)`. The left side is `(C ⊗ id) R R'^{-1}`. Invertibility
of `C ⊗ id` forces `R R'^{-1} = λ I`, hence `R' = λ^{-1} R`. The converse is
substitution. Equality is of linear maps, global phase included. ∎

Invertibility of `C` is necessary. A rank-1 residual can satisfy the scaled
equation for an `R'` that is not `λ^{-1} R`.

## What was checked

Equational replay over `Q(i)`, sizes 2 and 3, five scalars
(`1, i, -1, -i, 2+i`): ten forward-and-converse replays, each with an
invertible one-entry shift that must fail, plus one singular-`C` control.

Exact `Z[i]` circuits, standard library only, on the three certified pairs in
`HyperplaneEnd/Exact.lean`. Ports reproduce `lhsLit` / `rhsLit` and the
monomial gate lists. For each pair the pre-wrapper is varied and the post
wrapper stays the shipped `L`:

| mutant | result |
|---|---|
| shipped `R`, and a dead low-triangle quadratic bit | holds only at `λ = 1` |
| phase `+1`, `-1`, `+2` | holds only at `i^{-t}` |
| offset xor, linear `Z/4` flip, live quadratic bit, `L` used as `R'` | fails all four roots of unity, with an exact `(row, column)` witness |
| residual `C8 ⊗ id` | rejected for the shipped pre-wrapper |

`--self-test` shifts the shipped pre-wrapper phase by one, keeps the port
literals consistent with that shift, and requires the `λ = 1` clause to reject
it. It holds at `i^3` instead.

## Not claimed

No Lean kernel proof. `Labels.lean` still has neither `factor_iff_post` nor a
scalar on `factor_iff_pre`. No cold `(E = 0)` pair, no multi-gate tail, no
`hrec` climb, unit row, footprint or whole-invocation discharge. No
multiplication theorem and no κ. Selected κ stays `0.001672660197076918`.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/hpe-pre-wrapper-phase
```

Expected first lines include `PASS_HPE_PRE_WRAPPER_PHASE` and
`PASS_SELF_TEST`. Direct checks:

```sh
python3 -B research/hpe-pre-wrapper-phase/verify.py
python3 -B research/hpe-pre-wrapper-phase/verify.py --self-test
```

## Open next questions

Kernel-check the scalar pre-wrapper statement beside `factor_iff_pre`. That
would put the phase freedom at the same trust level as the `λ = 1` theorem.
First step: add the `λ` hypothesis to a successor of `Labels.lean` without
editing the frozen file, and extend `PrintAxioms`. Blocked here by the absence
of a Lean/Mathlib 4.21.0 toolchain.

The same scalar statement for a cold `(E = 0)` literal is open. The three
certified pairs are non-cold. First step: bind one cold `(N)` circuit with
this verifier's gate semantics. Blocked because no cold literal pair is in
`Exact.lean`.

## Credit

Jeremy Kothe (`jeremykothe2`) proved `factor_iff_pre` in
[PR 593](https://github.com/CrocSwap/integer-mult-bounds/pull/593). The
post-side phase-sharp lemma and its exact arithmetic are
`research/hpe-post-wrapper-lemma` (Aaron Wang). The pre-side audit that left
the arithmetic unrun is `research/hpe-prewrapper-binding`
([PR 2706](https://github.com/CrocSwap/integer-mult-bounds/pull/2706), Riquelme
Soares). Gate semantics follow the five kinds documented in
`HyperplaneEnd/Clifford.lean`. This package adds the pre-side scalar extension
and its checks.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel review.
