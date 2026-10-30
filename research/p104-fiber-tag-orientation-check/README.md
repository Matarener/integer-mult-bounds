# #4154's P104 fiber-tag seam, checked in its sources' orientation

**Claim type: an independent finite check with a correction. No new κ.** The
selected conditional κ stays `0.001672660197076918`.

## Object

[PR #4154](https://github.com/CrocSwap/integer-mult-bounds/pull/4154)
(unpaidmoon, merged, `research/p104-fiber-tag-seam`) compares #3966's row tag
`z ⊗ q_j` with its column tag `r_i ⊗ z` on the 104 P104 labels, and pins
#3954's witness. The `p104-side-correction` card lists it as still needing
independent validation.

**The orientation question.** The sources fix which tag is which:

- **#3966** (`p104-phase-uniform-gauge/PROOF.md` §4) defines the row
  correction as `z ⊗ q_j` and the column correction as `r_i ⊗ z`, with
  `q_j = O p_j` for the row label and `r_i = O p_i` for the column label.
- **#3954**'s witness lines are `386 ⊗ 386` (row port) and `405 ⊗ 386`
  (donor port), decoded from its `RESULT.json`. Both lie in the row fiber
  `q = 386`, so the pair is row 386, column 405, on the shared line
  `r_i ⊗ q_j = 49 ⊗ 386`.

#4154's README states that convention. Its code does not: `tags(row_image,
column_image)` returns `z ⊗ column_image` as the row tag and
`row_image ⊗ z` as the column tag. Those are the transposes.

## Results

**Confirmed: everything that does not depend on orientation.**

| Claim | Result |
| --- | --- |
| Labels | `labels.json` equals `physical_labels` in #3966's source `RESULT.json` |
| Gauge | `O` is an orthogonal involution with the weight law, on all of `F₂⁹` |
| Label classes | 56 of class 1 and 48 of class 3; every image is class 3 |
| Full address | no agreement in any of the 10,816 ordered pairs |
| Shared line | 5,440 pairs agree and 5,376 disagree |
| Uniform tag `a` | never a row tag or a column tag |
| Minimum Hamming distance | 6, only at labels 4 and 32 |
| Witness Hamming distance | 20 |

**Corrected: the witness and one census sentence.** These are in #3966's
orientation, at row 386 and column 405.

| | #4154 | Source orientation |
| --- | --- | --- |
| Shared-line flips (row, column) | `(0, 1)` | `(1, 0)` |
| Does `a` match the row tag on the shared line? | no | **yes** |
| Separating cell | bit 11 = `(1, 2)` | bit 11 does not separate; bit 19 = `(2, 1)` does |
| Helper matches the row tag on the shared line exactly when | the column label is class 3 | **the row label** is class 3 |

The count is `104 · 48` ordered pairs either way.

- **The full-address obstruction stands.** `a` is never a row tag, so a
  helper carrying `a` still fails to match a row owner on the full 81-bit
  address.
- **The shared-line conclusion does not.** #4154 says that on the witness's
  shared line "a helper carrying `a` does not match this row owner". In the
  source orientation it does match there. That conclusion is the premise of
  #4154's open question 2.

**Control.** Evaluating #4154's transposed objects reproduces its numbers
exactly: flips `0/1`, the helper mismatch and bit 11. The census is
unchanged. The difference is therefore exactly the transpose. The verifier
also checks the line in #4154's code that builds the row tag from the column
image.

**Provenance note.** #4154 says #3966's `RESULT.json` "is not a Git object on
this base". It is on main, as
`research/p104-phase-uniform-gauge/source/RESULT.json`, with the pinned SHA256
`ce05a27e…`.

## Method and independence

The verifier imports nothing from #4154. It represents tensors as sets of
`(α, β)` cells rather than packed integers. It reads the labels from #3966's
file, not #4154's copy, and it reads the orientation from #3966's text and
#3954's witness vectors.

## Not covered

- Native routing, owners, dirty return, precision and the inherited
  44,096 excess, all of which #4154 also leaves open.
- Which orientation a future P104 caller should use. This package only
  matches the sources' definitions.

## Reproduce

```sh
python3.12 -B research/p104-fiber-tag-orientation-check/verify.py
```

It prints `PASS_P104_FIBER_TAG_ORIENTATION_CHECK` in about 2 seconds, using
only the standard library.

## Open next questions

1. **Revisit #4154's open question 2 in the source orientation.** At the
   witness, the uniform tag already agrees with the row tag on the shared
   line. The remaining question is only full-address agreement, which `a`
   can never give.
   - *First step:* restate the question for the full address alone.
   - *Blocked by:* nothing.

## Credit

The seam comparison is unpaidmoon's (#4154). The labels, the gauge and the
corrections are #3966's (ToikY); the witness is #3954's (Clear1nsight).
Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5)
assistance. Apache-2.0.
