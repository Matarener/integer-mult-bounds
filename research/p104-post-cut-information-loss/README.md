# PR5718-shape leak corrections: third-engine check of the PR6030 exclusion, and a PR5907 witness

**Scoped exact result; no new κ.** Base: canonical main `721c03822c421b7f7fcbb2598993b947c4d88419`, where
[PR #6030](https://github.com/CrocSwap/integer-mult-bounds/pull/6030) (DreamingOfClouds) is the selected word. The
selected record is unchanged by this package.

**Priority.** [PR #6045](https://github.com/CrocSwap/integer-mult-bounds/pull/6045) (JosieElliston) left open
*combination carriers* and *rewritten events* for the PR5718-shape leak classes of Nick Petalas's
[PR #6040](https://github.com/CrocSwap/integer-mult-bounds/pull/6040) census. On the selected PR6030 word, both
questions were answered first by apoursh's [PR #6067](https://github.com/CrocSwap/integer-mult-bounds/pull/6067)
(head `4d629cf0`) and independently by jon314159's
[PR #6069](https://github.com/CrocSwap/integer-mult-bounds/pull/6069) (head `b3f5aabd`). Both report 4,009
information-lost classes, 22 with no chart-local combination carrier, and 2 (cuts 13637/13639, helper 572) where
clearing the leak erases `z`. This package was built without knowledge of them; their overlap surfaced only at
submission. Lemma 1 below is the same information-collision argument as theirs, and the credit for it is theirs.

What this package adds:

1. **A third, independent engine for the PR6030 numbers.** It uses an exact left-kernel tracker (29 vectors, about
   20 ms per word), rather than PR6067's `R M⁻¹ S e_p` collision test or PR6069's global dependency filter. It
   reproduces 4,009 / 22 / 2. Its 24 residual classes equal PR6069's `global_screen.survivors` class for class
   (local comparison against PR6069's committed `EXPECTED.json`; not part of the verifier).
2. **The PR5907 word, where the exclusion fails.** Class (cut after 13776, chart 1031, helper 699, leak to role 149)
   is legalized at the scalar level by an orig-zero chart-local combination program. So the PR6030 exclusion
   depends on the word: it is not a property of the PR5718 split shape or of the correction model, and the
   combination-carrier test is not vacuous on real data.

## Result

| Word | Leak classes | Information lost at the cut | Residual | Residual, by chart-local combination closure |
|---|---:|---:|---:|---|
| PR6030 (selected) | 4,033 | 4,009 | 24 | 22 no usable combination, 2 clearable only by erasing `z` (as PR6067/PR6069) |
| PR5907 | 4,206 | **4,180** | 26 | 23 no usable combination, 2 erased, **1 witness** |

**The PR5907 witness.** Directly after the cut, the seven fields `696 − 698 + 699 − 700 − 702 − 767 + 792` at chart
1031 sum to zero in the original word, and to `z − ℓ` in the split word. Reading this combination into targets 697
(`μ = 1`), 698 (`μ = 2`) and 700 (`μ = −1`) adds `μ (z − ℓ)` to each. The program lowers to 18 ADDs, 1 SCALE and 1
COPY, all chart-local. The COPY cannot be avoided with this combination: each read into a field of its own support
lowers its pairing with `z`, which reaches 0 at the last read (an overwrite). The words contain 23 COPY events of
their own, but native legality is not checked here. A plain simulator (`check.py`) shows that every O output equals
the original output exactly. `z` then reaches V-final roles 698, 700 and 702 (not 699), and PR6040's pairing test
passes. Three perturbed programs are rejected. This is **not** a split proposal: native maps, cost, owned lifetimes
and the caller are unchecked, and PR5907 is not the selected word.

## Lemma 1 (information loss)

Setting as in PR6040/PR6045. The word acts linearly on `N = n + m` fields (`n = 770` public, `m = 29` owned). After
event `t`, field `f` holds the linear form `row_f(t)` in the inputs; `W(t)` is the `N × n` matrix of these rows.
For a class with cut after event `i` and helper `p`, the split word replaces `p`'s content by a fresh input `z`, so
its state at the cut is `W(i) + e_p ⊗ (z − ℓ)`. Let `P` be the original post-cut map, so `d = P e_p`, and let
`O` be the public roles whose final chart is not `V = final[p]`. The class leaks when `d_o ≠ 0` for some `o ∈ O`.

> If a leak class can be legalized by some post-cut linear map `G` (that is, `G` gives every O output its original
> value identically in `x` and `z`), then `row_p(i)` lies in the span of `{row_f(i) : f ≠ p}`.

*Proof.* Take `o ∈ O` with `d_o ≠ 0` and compare `G_o (W(i) + e_p (z − ℓ)) = P_o W(i)`. The coefficient of `z`
gives `(G_o)_p = 0`. What remains is `(G_o − P_o) W(i) = 0`. So `c = G_o − P_o` is in the left kernel of `W(i)`,
with `c_p = −(P_o)_p = −d_o ≠ 0`. ∎

Fresh scratch fields only add zero rows, so they do not change the conclusion. The lemma uses neither charts nor
costs, so it holds for every edit made after the cut. Edits *before* the cut are not covered; for example, saving a
copy of `ℓ` before the cut makes `p` redundant.

## Lemma 2 (tracking the left kernel)

`K(t) = {c : c W(t) = 0}`. Field `p` is *redundant* at `t` when some `c ∈ K(t)` has `c_p ≠ 0`. `kernel.py` updates
a basis of `K` exactly at each event: ADD `r += q f` maps `c ↦ c A⁻¹` (`c_f −= q c_r`), SCALE `r *= s` maps
`c_r ↦ c_r / s`, INIT/CLEAR `r` gives `(K ∩ {c_r = 0}) + span{e_r}`, COPY `r := q f` gives
`{k + c (e_r − q e_f) : k ∈ K, k_r = 0}`, and MOVE changes nothing. Each rule follows from `W(t+1) = A W(t)`.

`verify.py` does not rely on these rules. On both words the final field matrix has exact rank 770. Rank never
increases along a word, so every intermediate state has rank 770 and `dim K = 29`. At every leak-class cut it checks that
the tracker holds 29 linearly independent vectors that annihilate the exact `W(i)`; together these show that the
vectors span `K(i)`. A seeded brute-force comparison then runs 300 random small words, comparing the tracker's
redundant set with exact rank deletions after every event.

## Residual classes: chart-local combination closure

For a redundant class, `kernel.closure_intervals` decides which insertion points are usable by programs of
*batches*. A batch at time `t` reads `c · state` for some `c ∈ K(t)` supported on the fields of one chart `X`; in the
split word this equals `κ (z − ℓ)`. It then adds multiples of that value to targets at `X`. Such programs never
change an original row. A batch is usable only if `c` pairs nonzero with the z-column, either the original column
`β(t)` or `D(t)`, the forward image of every earlier usable target. That gives a sound upper bound on the reachable
z-columns. PR6045's `correction_spans` and `decide` (pinned, unmodified) then test whether `d_O` can be cleared
without erasing `z`, and apply PR6040's pairing test. The PR5907 witness is then rebuilt as an explicit program and
checked by the plain simulator in `check.py`. That check is independent of the kernel and suffix algebra. The
verifier also confirms that three perturbed programs are rejected.

## Reproduce

Python 3.12, standard library, from the repository root (about 20 s):

```sh
python3.12 -B research/p104-post-cut-information-loss/verify.py
python3.12 -B scripts/research_package.py --package research/p104-post-cut-information-loss
```

Marker: `PASS_P104_POST_CUT_INFORMATION_LOSS`. `--write` regenerates `RESULT.json`. Normal replay is read-only and
compares the receipt byte for byte.

## Scope and limits

- This is the scalar O-defect condition of PR6040/PR6045 only: the O outputs must equal the original outputs, and
  `z` must reach a V-final output. Native maps, owned lifetimes, restoration, caller, compiler, precision, cost and
  outer checks are not modelled.
- Lemma 1 covers every linear edit after the cut, for the PR5718 unit injection `b = e_p` at a PR6040 class. It does
  not cover edits before the cut, other injections, or a changed class definition. The census inherits PR6040's
  input rule ('empty').
- The residual-class closure covers batch programs whose every read is an orig-zero chart-local combination. It
  does not cover programs whose individual reads have nonzero original value and cancel only across several
  times. That gap concerns only the 24 PR6030 residual classes, because Lemma 1 already covers the other 4,009.
- The PR5907 witness is a scalar-level existence check, not a priced or native split.

## Open next questions

- **Pre-cut edits.** Lemma 1 says that any PR5718-shape split on the PR6030 word must keep `ℓ` somewhere else at
  the cut, for example in a copy saved into an owned field before the cut, and that copy must be uncomputed later.
  Is there a class where such a save, with its extra owned lifetime, plus a post-cut correction is legal? First
  step: for each leak class, add one pre-cut `INIT s; s += p` at the latest chart that `p` shares with a free owned
  field, then rerun the closure.
- **Why PR5907 and not PR6030?** On PR6030, the residual helper-700 classes (cuts 13399 to 13441) have their
  redundancy relation spread over charts 1031 and 1043, so no chart-local combination exists (observed in a local
  run; not a causal claim). First step: compare the chart-1031 field relations of the two words around the
  corresponding cuts.
- **Price the PR5907 witness.** Its 20 inserted events and the change of the z-column (it now reaches roles 698,
  700 and 702 instead of 699) need the PR5599 complete signed bill. This matters only if a similar redundant class
  appears on the selected word.
- **Cross-time cancellation** on the 24 residual PR6030 classes (see Scope). JoyboyBrian's
  [PR #6088](https://github.com/CrocSwap/integer-mult-bounds/pull/6088) excludes one concrete two-ADD seam family for
  helper 572.

## Credit

Nick Petalas (PR6040 census and class definition), Matarener (PR5994 census and pure-subspace decision),
flyingviper (PR5718 split shape), Ali Romman (PR5599 split criterion), DreamingOfClouds (PR5907 and PR6030 words)
PR6045 (JosieElliston, session 33: `leakfix.py`, pinned unmodified), and apoursh (PR6067) and jon314159
(PR6069), who published the PR6030 exclusion and Lemma 1's argument first, retain credit; nothing of theirs is
modified. Prepared for JosieElliston by Claude Opus 5.5 (Anthropic) via Claude Code, as one session of an unattended
overnight run; no human review. Apache-2.0.
