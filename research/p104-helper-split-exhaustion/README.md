# No PR5599-type helper split remains on the PR5907 P104 word

**Scoped negative result; no new κ.** The helper-subspace split of
[PR #5599](https://github.com/CrocSwap/integer-mult-bounds/pull/5599) (Ali Romman) retires a helper early at a
strictly intermediate chart and lets a fresh independent input use the rest of its program, replacing one
U-to-V target by a U-to-F and an F-to-V target at zero paid cost. On the latest conditional P104 word,
[PR #5907](https://github.com/CrocSwap/integer-mult-bounds/pull/5907) (DreamingOfClouds, κ 0.003125282), an exact
exhaustion census over **every helper boundary group (69), every strictly intermediate chart and every cut**,
with the **whole** pure prefix and suffix subspaces and an exact pairing decision, finds **no split cut at all**
under the PR5599 contract. A relaxed necessary condition (input support = every public role starting at U,
output support = every public role ending at V) also finds none.

The reason is structural. In every one of the 1,412 (cut, chart) classes where a pure-prefix direction `a`
(aP supported on the boundary roles) and a pure-suffix direction `b` (Sb supported on the boundary roles) both
exist, the pairing `a·b` is identically zero on A × B: a field whose row is still pure at the cut is read into
main fields later, and a field whose future is clean has already been mixed. A PR5599 split needs one field that is
pure on both sides, and the PR5907 word has none left. (The same census on PR5599's own emitted word finds none
under the group contract either; the authors took what the contract offers.)

Base: canonical main `19fdb086ea96af9a9f87936a2b888e10af4ed810`. Live inputs are pinned in [SOURCES.json](SOURCES.json).

## Why this matters

In the complete PR5907 invoice (66,852 paid calls, 13,444 targets, rank surplus 760) one split H9 → H4+H5 per
local call is worth about +1.4·10⁻⁶ of conditional saving, and about 177 per local call would reach the admitted
BIT cap .0034 (the compiler feasibility of 145 splits was certified in PR #5614). The census shows the supply on
the current word is zero, so further κ from this mechanism needs the PR5718 kind of split (different input and
output bases with a mid-word correction, [PR #5718](https://github.com/CrocSwap/integer-mult-bounds/pull/5718),
flyingviper), not another cut search. PR #5702 (theon199) already shows that splits funded by an added paid call
lose; this package closes the zero-paid-cost side on the PR5907 word.

## What is checked

The criterion is PR5599 PROOF.md section 1: for a group of helpers with boundary charts (U, V), a chart F with
U ⊂ F ⊂ V and a cut after event i, a row `a` over the fields at F and a column `b` over the fields at F with
`aP = c`, `Sb = d`, `c` and `d` supported on the group and `a·b = c·d = 1`. The census
([splitcensus.py](splitcensus.py), standard library, independent of the PR5599 code):

- evaluates every group, every chart F in the strict span nesting, and the cut after **every event that touches
  F** (between two such events the prefix rows and the suffix columns of the fields at F are unchanged, so this is
  the complete set of cut classes); the PR5599 `search.py` screens cuts after MOVE events and one representative
  combination per field;
- computes the whole subspace A of combinations of the rows at F whose image lies in the input support and the
  whole subspace B of combinations of the suffix columns whose image lies in the output support (exact Gaussian
  elimination over Q, zero-image combinations retained);
- decides exactly whether some pair has `a·b = c·d ≠ 0`: either a kernel vector of `F1 − F2` with `F1 ≠ 0`, or a
  2×2 minor form `u_i v_j − u_j v_i` (u = x(F1−F2), v = xF1) that is not identically zero, which is detected on
  the finite probe set {e_k, e_k + e_l}; a found pair is built explicitly and normalised;
- classifies every two-sided class as `witness`, `F1zero` (a·b ≡ 0), `F2zero` (c·d ≡ 0) or `mismatch`.

| Word | Supports (c / d) | Evaluations | Two-sided classes | Witnesses |
|---|---|---:|---:|---:|
| PR5907 | group / group (PR5599 contract) | 8,913 | 3, all `F1zero` (chart 712, helper 468) | **0** |
| PR5907 | boundary / boundary (relaxation) | 8,913 | 1,644 (1,631 `F1zero`, 13 `F2zero`) | **0** |
| PR5565 source, cuts 13,700–13,800 (control) | group / group | 99 | 18 | 18, including the authors' first split at cut 13775, chart 120, ranks (5, 4), pivot 648 |

The boundary relaxation is only a necessary condition: a split whose corrections stay at the two boundaries needs
its supports inside roles that both start at U and end at V, so a witness there would still need a legality check;
none exists.

## Verification

```sh
python3.12 -B research/p104-helper-split-exhaustion/verify.py
```

About six seconds, standard library only. It authenticates the pinned inputs and the PR5907 local paid and helper
profiles; runs the two censuses on the PR5907 word (0 witnesses each, every two-sided class an orthogonality
failure); runs the positive control on the pinned PR5565 source word and passes both the census's own witness and
the authors' first SPLITS.json witness through an independent exact prefix/suffix check; rejects a corrupted
witness and a wrong cut; checks the decision procedure on three synthetic instances; and compares
[RESULT.json](RESULT.json) in full (every negative class is listed there). Marker: `PASS_P104_HELPER_SPLIT_EXHAUSTION`.

## Scope and limits

Scalar legality only, as in the PR5599 screen: native maps, the physical caller, the compiler and the outer checks
are not involved. Zero-cost splits with a mid-word correction (PR5718) are outside this criterion and are not
excluded. The census covers cuts where the helper's intermediate chart is one of the word's existing charts;
splits that first insert new transports are a different (paid) mechanism. The selected record is unchanged. This
is an agent check, not human acceptance.

## Open next questions

- Which of the 1,412 two-sided classes admit a PR5718-type split (unpaired cut column with a later ordinary
  correction)? First step: for each class in `RESULT.json`, list the outside roles reached by `Sb'` and search
  later events at their charts for a field equal to the nuisance functional. Blocked by a new search, not by this
  package; the 26,000-event cap leaves room for about five such splits.
- Is the orthogonality of pure-past and pure-future directions a property of every ladder word after its splits
  are taken? First step: run `splitcensus.py` on PR5718…PR5827 (seconds per word).

## Credit

Ali Romman (PR5599 split criterion and search), flyingviper (PR5718), theon199 (PR5702), DreamingOfClouds
(PR5907 word) and the P104 lineage retain credit; nothing of theirs is modified. Prepared by Matarener with
Claude (Anthropic) via Claude Code. Apache-2.0.
