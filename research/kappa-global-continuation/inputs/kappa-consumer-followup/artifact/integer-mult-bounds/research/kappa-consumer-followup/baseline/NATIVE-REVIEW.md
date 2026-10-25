# Independent review of the modern involution component

## Finding and scope

The reviewed finite local component passes the checks below. I found no error in its eight serial source updates, physical placement of dirty compensation, pivot endpoint gauges, signs, or newly supplied native phase bindings. This closes the old missing native-line binding at the level of a compositional finite component proof. It does not admit a complete supplier, the routed nine-stage consumer, or a kappa increase.

The reviewed file is `recovered-involutory/modern_native_component.py`, SHA256 `f6769f1ecd6b2e582748805b3afcf4c65824ba108ce7f23a4d011c45f8b724de`. Fresh independent-output replay is retained in `native-review-replay/`. The separate review executable is `review_native.py`, with machine receipt `NATIVE-CRITICAL-REVIEW.json`.

The two providers are the actual PR3734 words from commit `fa041037a3374eaa08feeca0b26a5d6893194147`. The cached canonical words are byte-identical to the live package's `inputs/NATIVE-{base,extra}.json.gz`; the borrowed-word hashes match the live `words/BORROW-WORD-43{base,extra}.json.gz`. The native receipt is authenticated by the live `REPLAY-INPUTS.json` manifest, with SHA256 `7ddf3f80b2fa61d1ab12035da9ef1c95d43f76077df819d7683144d7862a3f93`.

## What was checked independently

The component's sparse interpreter propagates 632 independent logical input columns: 112 source inputs, 112 target inputs, and 408 arbitrary persistent helper inputs. It treats climbs and native adapters as changes of physical gauge. That is legitimate only when a separate native argument establishes the physical maps and phases. Merely omitting those events from the scalar interpreter would not suffice.

I checked the crucial new implication using the actual modern endpoint recipes and the exact Gaussian/Pauli native interpreter. For each selected pivot `(0,7,20,27,36,46,57,111)`, and for each provider, the positive rank-one `C_q` line followed by the actual source entry adapter agrees with that source's canonical entrance frame. The actual target frame followed by its actual exit adapter agrees with `C_q^{-1} FULL`, including global phase. Composition in the forward order `FULL C_q^{-1}` agrees as well. These 32 exact composition assertions per provider rule out a line that has the right hyperplane but the wrong phase or direction.

The component separately executes 16 new native recipes, eight in each sign/direction, on all 512 address basis vectors, for 8192 exact Gaussian basis checks per provider. Its phase and direction mutation controls reject. This count concerns the 16 new lines; it is not a claim that the entire 632-register by 512-address circuit was expanded as one basis calculation. Retained core recipes and their authenticated modern source proof are reused compositionally.

The component derives `R K = 14 I`, `R P = I`, and `A = 12 P - K`. Therefore `R A = -2 I`. I independently multiplied the eight rank-one updates in their actual serial order and checked that every future query remains equal to its original `R_k x`. The resulting matrix equals `I + A R`. This addresses the concern that an in-place source update might silently change the next query. It also avoids relying solely on the component's `source_code` builder for this claim.

All scalar entries of `R`, `K`, `P`, `A`, `G`, and `J` have denominators that are powers of two. The coefficients belong to the central dyadic scalar ring; the native recipes are exact Gaussian dyadic operators. There is no floating-point phase or coefficient approximation in these checks.

## Dirty compensation and ownership

Removing the complete centre slice gives the exact target defect `J x - K H h`, with `J = I - K R`. The forward precompensation adds `K H h` to the target at the physical entrance. Its 815 additions read only helpers whose literal entrance frame is I. The backward precompensation is the corresponding inverse-transpose helper update, also in the I gauge. The full logical replay checks arbitrary values of all 408 helpers; their restoration is not established by setting them to zero.

The 91 internal buffers are a different resource: they are owned zero buffers with explicit allocation and erasure. They are not 91 additional arbitrary input columns in this new component replay. The private query scratch is allocated/cleared by the component and does not overwrite an arbitrary borrowed helper. Resetting the gauge of an erased zero register is harmless; resetting an arbitrary live helper in the same way would be invalid.

The literal persistent frame chronology, wrapper pre/post positions, climb ranks, zero-buffer lifetimes, and boundary scalar gauge compatibility are separately checked by the component. The new `intrinsic_line` event is resolved through a named native recipe. It has not yet been integrated into a fresh production whole-supplier compiler invocation or physical allocation proof.

## Resulting local contract and bill

The verified forward endpoint is `(G x, y + G x, h)`. The verified backward endpoint is `(x - y, G y, h)`. These are changed source/target contracts, with `G^2 = I`; they are not ordinary addition or subtraction endpoints.

Both providers have the recursive profile `{1:2448,2:725,3:224,4:102,5:20}`, with rank mass 5078. The original modern local profile has mass 5134. The difference is exactly eight removed rank-eight centre operations and eight new rank-one corrections. The new finite scalar bill is 179900 real scalar primitives per orientation under the component's accounting.

To use this result for kappa, a complete routed consumer must still discharge its changed encoding, preserve or correctly consume any dirty retained records, and pay its full recursive, physical-stock, scalar, precision, and recovery costs. The present review supplies no zero-price assumption for those remaining tasks.

## Reproduction

From the repository root, with the actual live source and reconstructed cache present at their recorded workspace paths:

```sh
python3 -B ../recovered-involutory/modern_native_component.py --out research/kappa-consumer-followup/baseline/native-review-replay
python3 -B research/kappa-consumer-followup/baseline/review_native.py
```

Both commands passed. The first is a fresh replay of the component into a separate output directory. The second is the independent exact endpoint and serial-product review described above; it uses the component only to extract its `R,K,P,J` data, and does not claim an independently implemented full scalar interpreter.

SPDX-License-Identifier: Apache-2.0. Substantial OpenAI Codex assistance under user direction.
