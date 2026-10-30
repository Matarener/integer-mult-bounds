# Standard product entrance from the encoded P104 exit

**Negative result. No new κ.** Selected κ stays `0.001672660197076918`.

Discussion #1166 comment 19032700 asks for one downstream consumer that keeps the PR #3943 encoded endpoint and avoids the unaffordable source return. This package prices the standard product entrance `Y_i = w_i` in `H_i`. In the adapter alphabet that entrance already costs the whole 192-transport floor. The extra scalar work that restores `X` does not add a further transport. The paired-chain rank gap is the legacy-return gap `352 s + 104`.

## Result

The encoded exit stores `w_J` on `Y_J`, `w_N` on `X_N`, `q` on `X_J`, and `v_N` on `Y_N`. The defect `v_N - w_N` has rank 96 as a form in `(x, y)`, so none of the 96 N products is already on `Y`.

Any program in the published FULL-only alphabet that reaches `Y_i = w_i` in `H_i` on every realizable encoded exit, and restores helpers, uses at least 192 rank-one transports. One explicit program attains 192. It performs 576 unit additions. It leaves `X_J = q` and replaces `X_N = w_N` by `X_N = x_N`. The legacy return adapter adds 384 unit additions and 192 scales on top of those same 192 transports, and only then restores every `X_i = x_i`.

Both exits have frame-dimension total 2416. With the PR #3943 credit of 2312, the rank masses 2576 and 2768 produce nine-stage gaps 1544 and 3272. The standard-Y consumer pays the larger one. Leaving the banks in place avoids the transports and does not present this entrance.

The argument is an alphabet lower bound plus an exact invoice. It is not a native-phase replay, a physical owner embedding, or a multiplication theorem.

## Verification

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/p104-encoded-exit-consumer
```

The direct checker also passes under `python3 -O -B`. It rebuilds the Gram block from `research/p104-native-channel/inputs/P104-FIXTURE.json`, checks the rank-96 defect, realises all 96 one-bank witnesses, runs the product program and the legacy adapter, and checks the integer screen. Skipping one required lift is rejected. Skipping one descent leaves that Y bank in FULL.

Not run: the PR #3943 native prefix, Lean, Docker, and the selected cold replay.

## Credit

Chris R / Clear1nsight, PR #3943, for the encoded exit, the inverse, the adapter alphabet, and the paired-chain screen. PR #3956 matched the 960-add and 1152-add return adapters and is not redone. PR #4006 fuses a different late-delivery cleanup; it does not price this Y entrance. Rohan Arun / PR #1972, Chafik Boukhalfa / PR #1991, and Adam Gall / PR #1940 supply the channel and schedule retained by that geometry. The fixture hash is the PR #1071 lineage carried on main.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent human or formal-kernel review is claimed. New work is Apache-2.0.

## Open next questions

1. A cross-chart add, or one clean scratch bank, might move `w_n` onto `Y_n` without a separate lift and descent. The 192-transport bound uses the FULL-only alphabet above and does not forbid that change. The blocker is a priced alphabet that is actually legal for the native word.
2. The split read, `w_N` from `X_N` and `w_J` from `Y_J`, has no transport in this model and is not a standard Y entrance. Naming a real next-stage caller that accepts those banks, with `q` and `v_N` either consumed or restored, is a different contract. No such caller is pinned here.
