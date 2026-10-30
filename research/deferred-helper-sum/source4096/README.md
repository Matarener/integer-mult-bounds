# Shared staged-helper boundary: an exact obstruction

The common rewrite defect of helpers 608 and 609 does not yield a cheaper
single dirty channel under the tested boundary. Exact columns exclude
pair-only extraction. The natural six-register terminal cone also has no
nonzero scalar reader of the original helper pair. This tests a proposed
change to the helper interface; it is a scoped negative result.

Let H={608,609} and R={608,609,417,419,421,610}. On the actual non-target
operator M before literal cleanup, both PR4076 providers satisfy

```
M e608 = e608 + e417/2 - e421/2 - e610,
M e609 = e609 + e417/2 - e419/2 - e610.
```

Rows 421 and 419 give a nonsingular diagonal minor. Inverse rows give a
stronger statement: alpha supported on R and alpha M supported on H imply
alpha=0. Thus no invertible scalar entrance change confined to H and terminal
change confined to R can isolate a restored helper direction. The common
417/610 defect is only part of each complete column.

The proof and checkers distinguish the complete prefix from the suffix at
the actual shared staging cut. The 608 source OLD event10535 maps to NEW10523. The later609 record
reuses numerical10535 after the608 edit, mapping instead to NEW10527.
Literal NEW10535 is checked separately. Both providers and these declared boundaries have the same
obstruction. Inverse-cone equality is computed explicitly.

A separate check tests the genuine common sum in the two releases into 610.
Its literal sum/restore implementation has the same local recursive profile
and ordered helper widths. A changed scalar gate count does not establish
recursive savings. Complete-invoice equality is conditional on unchanged
admitted owner inputs; no new owner, native, phase, precision, storage or
outer admission follows.

## Reproduction and evidence

```
python3.12 -B scripts/research_package.py --package research/shared-staged-helper-interface
python3.12 -B scripts/check_research_commit.py --package research/shared-staged-helper-interface --check-source-history
```

RESULT.json and the proofs specify the actual passed coverage. The arithmetic
is exact for the named words; the written implication covers every scalar
basis in the stated model. It is not a formal-kernel proof or a new supplier,
kappa, multiplication theorem, or selected-frontier improvement. Local and
hosted evidence are recorded separately.

## Sources and credit

Rohan Arun/PR4076 is pinned at
`9744f9df268590295a9872b1952c695a678192b9`; canonical base is
`bb4bccbf42844d2801487450727c2f63e10d1d0f`, priority revision 6.
SOURCE-EXPORT.json binds exact bytes to original Git blobs. The local freeze
in SOURCES.json is publication ancestry; pending PR4076 is not thereby an
ancestor of canonical main.

Tekalign/PR4087 supplies the prior rank-two rewrite-defect observation. This
package tests its shared 608/609 component against full maps and source
boundaries. PR4085's receiver rewrite and PR4088's mixed fourth entry remain
separate. Preserve the credit of Ross Richardson/3605, dataisfire/3734,
ChaloupeMusic and Erwan Secousses/3949 and 3815, Dugongue and David Ganz/3945,
Marius-Paul Dumitrean, Sagar Thakrar/3687, Arham Tahir, roger-sato/3693, and
the complete lineage in [the retained notice](source4076/NOTICE.md).

Prepared for Ross Richardson with substantial OpenAI GPT-6.1 Sol assistance
and two separate mathematical AI checks. These are not independent human or
formal-kernel acceptance. Apache-2.0; the standalone export includes LICENSE.

## Open next questions

An enlarged recovery boundary must price extra current source cells, target
compensation, terminal changes and all inverse cleanup. The inverse pivots
require at least two cells outside R for any nonzero scalar reader of H;
a reader using both helper coordinates needs all four displayed pivot cells.
This is a necessary access condition, not a construction or a cost saving.
TASK.json records the next bounded step and unresolved costs.
