# Signed columns of staged544 helpers 600 and 601

**Negative result. No new kappa.** The selected record is unchanged.

## Scope

The drawn catalogue card was `p104-side-correction`. Its named experiment, one
collection from #2981 with acquisition times, coefficients and dirty
restoration, is already open for flag 0 in #3915, #3669 and #3683. The same
present-head scan covers flags 1, 9 and 43, so another flag pass is the
card's pending-follow-up trigger.

The next catalogue suggestion is `complex-rank-shape-decoder`. Its ideal
rank-16 screen already clears 5% in `levers.py`, and repacking the selected
word's idle remainder is a scope-change trigger of that card. The live handoff
in discussion 1166, comment 19038903, names a smaller unclaimed test on the
same alphabet that #4045 just bound: whether the complete consumer columns of
actual helpers 600 and 601 are signed-proportional under one common native
frame. This package runs that test. It does not emit a capture.

## What is established

Both frozen PR3945 words used by #4045 (`91afbb643f7f4ccf6f34b685ecd959eb790a0f94`)
carry the same consumer adds for helpers 600, 601, 602 and 604. Each helper is
read by exactly seven `add` events. The only frame common to the 600 and 601
reads is `(45,)`, and on that frame the consumers are exactly 123, 175, 183
and 202, each with coefficient ±1.

In that consumer order the columns are

| helper | 123 | 175 | 183 | 202 |
| --- | ---: | ---: | ---: | ---: |
| 600 | -1 | +1 | +1 | -1 |
| 601 | +1 | +1 | +1 | +1 |
| 602 | -1 | +1 | +1 | +1 |
| 604 | -1 | -1 | +1 | -1 |

On both frozen PR3945 words, the frame-(45,) consumer columns of helpers 600 and 601 are neither equal nor opposite.

The same split holds for every pair among the four helpers: each pair agrees
on some of these consumers and disagrees on others. A capture that needs one
global sign, as in the H6 same-frame sum/difference of #4048, therefore does
not apply to this group. Flipping the two disagreeing entries of column 601
makes it equal to column 600, so the checker is not rejecting every pattern.

The two word files are not identical. Their SHA-256 values are
`08e6c96fbe3dfec96cb8451b3867ef8c1a214109ecd1e5af7fcc28e0f05728d0` and
`d83c2ec9cecc0ad092d34ea4080b28a4fd7199579356b6d5a8fc6cd53ff93299`, matching
git blobs `806784bf99d9d15004d2d227d06268556a0726c8` and
`c531be7383ad3ba941600c7ced14e5e10d6d1c67` at the #4045 head. Only the named
consumer columns were compared.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/staged544-helper600-sign-columns
```

The direct check also works without Git:

```sh
python3.12 -B research/staged544-helper600-sign-columns/verify.py
```

Expected marker: `PASS_STAGED544_HELPER600_SIGN_COLUMNS`.

## Limits

This does not rerun the #4045 support obstruction, the #4031 rank-4 screen, or
the #4048 H6 lattice. It does not price a partial capture, a nonmonomial
encoder, or any other helper pair. Adds where these helpers are destinations
are productions, not consumer columns, and are not part of the sign test.
No supplier, hosting bill, or selected-frontier change is claimed. The selected
baseline replay was not run: this checkout does not contain the assembly roots
that `research_baseline.py` imports.

## Open next questions

Can a capture that keeps the disagreeing consumers 123 and 202, and merges
only the agreeing consumers 175 and 183, reduce the complete child and
restoration bill? Those two consumers already share a sign, but the other two
do not, so both helpers stay necessary. A first step is to price one explicit
partial capture of consumers 175 and 183, including cleanup, against the
0.03825 allowance in #4045. No such map is exhibited here.

## Credit

Dugongue / #3945 supplies the two words. Chris R / Clear1nsight / #4045
identifies helpers 600, 601, 602 and 604 and the rank-16 support obstruction.
Tekalign / #4048 supplies the same-frame signed-capture idea that this test
refuses to transfer. Gonzalo Mier / #4031 supplies the zero-charge screen
#4045 already separated from this interface. Riquelme Soares (@hevlyo), with
substantial AI assistance in the extraction, checker and write-up. Apache-2.0.
No independent human review is claimed.
