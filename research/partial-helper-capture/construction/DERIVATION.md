# Partial capture of helpers 600 and 601

The explicit partial sum capture is exact on both frozen words, including all
dirty inputs. Its best certified cleanup has **zero change in the paid recursive
profile, ordered helper widths, and scalar primitive count**. This concrete
capture therefore supplies no exponent-saving mechanism. This is a scoped
construction and cost test, not a lower bound for captures with changed boundary
frames or a changed child interface.

## Pins and exact covered model

The immutable source-only freeze is
`f0631e4329ef4124c498fe3d1c500aab34ce6490`. The two compressed PR3945 words are
the bytes exported by PR4061 head
`f977a8a3dcb2983829d066a80420b7ded42d3e09`:

| File under `predecessor4061/frozen/` | SHA-256 |
| --- | --- |
| `WORD-base.json.gz` | `08e6c96fbe3dfec96cb8451b3867ef8c1a214109ecd1e5af7fcc28e0f05728d0` |
| `WORD-extra.json.gz` | `d83c2ec9cecc0ad092d34ea4080b28a4fd7199579356b6d5a8fc6cd53ff93299` |

The exact semantics, chronological binary frames, and literal cleanup generator
are imported from the retained `source4076/vendor/audit_core.py`, SHA-256
`888679ca8502cdcb100420fe5382a052529a494bf76cb332928b86e62612b951`, at source
PR4076 head `9744f9df268590295a9872b1952c695a678192b9`. The verifier checks all
three hashes before importing or evaluating them. It does not change the source
words or the source checker.

There are 632 live independent inputs: sources 0 through 111, targets 112 through
223, and 408 live helpers among 224 through 703. The 72 removed helpers are
absent. Each of the 91 declared private buffers, at its retained helper number
plus 704, is also an independent arbitrary input. The exact checks therefore
cover 723 independent coordinates, not just clean helpers or zero buffers.
Coefficients are dyadic rationals. The 72 native operators are independent
invertible noncommuting symbols; cancellation uses only adjacent inverse pairs.

## Reconstructible edit

Every index below is zero-based. In each frozen word replace exactly `B[77:85]`
by the following eight ADD records, all on common frame `[45]`:

```text
202 -= 600/4                 # retained exception read, originally B78
123 -= 600/4                 # retained exception read, originally B80
202 += 601/4                 # retained exception read, originally B82
123 += 601/4                 # retained exception read, originally B84
600 += 601                   # capture
183 += 600/4                 # agreeing consumer
175 += 600/4                 # agreeing consumer
600 -= 601                   # undo
```

The four exception ADD records are byte-identical to their predecessor records.
The two removed records are the agreeing reads of 601 into 183 and 175. The B
list still has 1870 records, so every native warp position is unchanged. All
other forward word fields, including A, wrappers, compensation, cut, restore,
entrance/terminal frames, removed helpers, and initial operator corrections,
remain unchanged. The cleanup is derived separately below.

## Current pullbacks and arbitrary-input identity

Write `a` and `b` for the values in helpers 600 and 601 on entry to B77. Neither
helper is touched in A or in B before this block. The wrappers and cut do not
write these helpers. Consequently their current pullbacks are exactly their
original independent dirt `a = x_600`, `b = x_601`. Neither has zero input merely
because a frame is declared. No native operator occurs within this block; the
first native B warp is at position 250.

The predecessor's eight reads add `(b-a)/4` to each exception consumer 123 and
202, and `(a+b)/4` to each agreeing consumer 175 and 183. The new block first
performs the four exception reads. It then changes `(a,b)` to `(a+b,b)`, uses the
captured sum twice, and applies the exact inverse shear. Its endpoint map is

```text
123 -> 123 + (-a+b)/4
175 -> 175 + ( a+b)/4
183 -> 183 + ( a+b)/4
202 -> 202 + (-a+b)/4
600 -> a
601 -> b
```

Target values on block entry are arbitrary. They are never read by the changed
block, so reordering its target additions introduces no cross term. If T is the
four-target vector in the order 123, 175, 183, 202, and H is `(a,b)`, the complete
local matrix is

```text
M = [[I_4, C], [0, I_2]],
C = (1/4) * [[-1,1], [1,1], [1,1], [-1,1]].
```

Its inverse transpose is `[[I_4,0],[-C^T,I_2]]`. Equivalently, chronological dual
propagation replaces each `dst += q src` by `src -= q dst`. Thus the partial
capture is a local equality on all six independent values, including both
dirty helpers, and in both orientations. This is not a permanent raw-dirt
change `A_new = A_old S`: the intermediate capture and its undo have joint
source map I at the block endpoint. The target-dirt compensation remains
exactly the predecessor's map because the entire local block map is equal,
rather than because any compensation direction was guessed.

The rational six-coordinate identity in `verify.py` is separate from the
imported whole-word evaluator. Full evaluation then checks both frozen words,
both cleanup choices below, and both orientations over the free group algebra.
Every one of the 723 output rows and 723 input columns is covered. A separate
reverse traversal checks the forward matrix by pulling back every input column.
Both words have exactly the declared complete forward map
`target_i += source_i`, with all other live and private-buffer coordinates
unchanged; their inverse transposes have `source_i -= target_i`. This includes
arbitrary private-buffer inputs: they have identity self-map and no leak.
The entire 723-coordinate state at the cleanup boundary also matches the
predecessor, including its restored-helper isolation contract.

## Cut/frame legality and helper identities

Both helpers enter the word at frame `span(45)`. Their old four reads and all
six new uses remain at this same frame. The added shears therefore require no
positive frame climb. Each of the four targets still needs its first climb
from the zero frame to `span(45)`; reducing two repeated reads removes none of
these target climbs. All following source productions and target reads occur
after the helpers have been restored to their original current values.

There is also a small fixed-contract floor: a monotone scalar rewrite on these
six registers with the same block entrance and exit frames must take each of
the four targets from dimension 0 to dimension 1. Under the inherited rule
that native charges are counted per register, each requires one rank-1 climb,
so the block costs at least `4 H_1`. Native frame warps preserve dimension and
cannot supply these climbs. The predecessor and this capture both attain the
floor. This statement fixes the six-register boundary and monotone native
contract; it is not a barrier against changing that boundary or using a
different joint native interface.

The checker walks every gate in chronological order, including native frame
warps, and rechecks the lifted binary-frame action. It checks dyadic/access
hygiene, the unchanged target cut, and each declared endpoint. The old and new
positive frame transitions agree register by register, including their exact
subspace masks. Ordered helper identities and their entrance/terminal masks
also agree, not merely their multiset of widths. Helpers 600 and 601 each keep
entrance dimension 1, terminal dimension 9, and width 8, with positive climbs
`4,1,1,1,1`. Neither helper is removed or mapped to a private restoration buffer.

This binary-frame verification is not a native Clifford-phase certificate or
an owner-allocation proof.

## Literal reverse-inverse cleanup and certified cancellation

Cleanup is first regenerated by reversing the **complete changed** invertible
non-target word and inverting every gate under the inherited target/prelude
exclusions. The two added forward source shears are not silently omitted.
Their inverses are adjacent in cleanup because the intervening forward gates
write only targets and are excluded by the inherited cleanup contract.

On both words the literal cleanup has 5227 records. At zero-based cleanup
indices 1225 and 1226 it contains

```text
600 += 601       # inverse of the forward undo
600 -= 601       # inverse of the forward capture
```

Both are at the full nine-dimensional frame. The private-buffer remapping is
the identity for these two helpers. This adjacent pair is exactly I on
arbitrary values. Removing **that explicit pair only** reproduces the frozen
5225-record cleanup byte for byte. This is a certified adjacent cancellation,
not an assertion that a newly added source gate is absent from the literal
inverse. Both the 5227-record literal cleanup and the canceled cleanup pass
the full arbitrary-input forward and inverse-transpose checks.

The frozen cleanup is consequently semantically valid for this changed word.
Calling it the unmodified literal reverse-inverse list is a representation
error; calling it the result of the exhibited cancellation is correct.

## Complete paid deltas

The complete recomputed paid profile on each word is

```text
2482 H_1 + 712 H_2 + 218 H_3 + 109 H_4 + 20 H_5 + 8 H_8.
```

The helper width inventory is `28 W_5 + 18 W_6 + 53 W_7 + 96 W_8 + 213 W_9`,
with all 408 helper identities and endpoint masks retained. For both cleanup
choices the profile and every ordered helper width are unchanged. Hence the
rank moment `sum_r c_r r^p` changes by exactly zero for every exponent p.

| Executed records | Predecessor | Literal cleanup | Canceled cleanup |
| --- | ---: | ---: | ---: |
| Prefix ADD | 11597 | 11597 | 11597 |
| Cleanup ADD | 4633 | 4635 | 4633 |
| Complete ADD | 16230 | 16232 | 16230 |
| Complete SCALE | 1164 | 1164 | 1164 |
| Complete WARP | 168 | 168 | 168 |
| Initial operator-correction records | 36 | 36 | 36 |
| Complete records | 17598 | 17600 | 17598 |

The 168 WARP count includes the implicit native B warps. The 36 initial
operator-correction records are high-level records; this table does not
relabel them as scalar gates. Their source accesses, operator words and any
expanded wrappers are unchanged, so their expanded delta is zero. In the
changed local block two target ADDs are exchanged for two helper ADDs. The
literal cleanup adds two ADDs; the explicit cancellation removes those two.
No paid source visit, recursive child, helper width, correction, or restoration
charge is eliminated. Even the strongest verified cleanup therefore has no
positive recursive saving to transfer to a larger kappa.

## Defect-sensitive controls and reproduction

On each word the verifier actually changes the relevant gates and rejects:

- Missing the forward capture undo, with downstream warp positions retimed
  and cleanup regenerated: the exact map acquires coefficient `-1/2` from
  entering helper 601 to target 123.
- Capturing a difference instead of a sum, with the matching inverse undo:
  the same dirty-input coefficient is wrong by `-1/2`.
- Deleting just one member of the literal inverse pair: the final map
  acquires coefficient `1` from entering helper 601 to helper 600.
- Giving the capture shear incomparable frame `[51]`: chronological frame
  containment fails at B81 on helper 600.
- Describing the canceled/frozen cleanup as the literal reverse-inverse list:
  literal-list equality rejects it, while the checker explicitly confirms
  that its semantic map passes with the cancellation certificate.

From the repository root:

```sh
python3 -B research/partial-helper-capture/construction/verify.py
python3 -O -B research/partial-helper-capture/construction/verify.py
```

Both commands compare fresh exact results to `RESULT.json`; neither changes
the frozen inputs or the committed result. The verifier uses explicit checks,
not Python assertions. An external checkpoint stage may write a separate
fresh result using

```sh
python3 -B research/partial-helper-capture/construction/verify.py --output /ABSOLUTE/PATH/result.json
```

The marker is `PASS_PARTIAL_HELPER_CAPTURE`; the deterministic result includes
the verifier hash, source hashes, both derived word hashes, exact matrix
hashes, the cleanup cancellation location, and rejecting witnesses.

## Scope, stop rule, and remaining obligations

The local written identity applies over any additive module with central
dyadic scalars. The global certificate is a complete symbolic linear-map and
frame check for these two fixed words; it is not a search over all possible
captures, a formal-kernel proof, or an all-size multiplication theorem.

The decisive stop rule fires because this partial capture removes no paid
child or helper width even after the best explicit cleanup cancellation.
No new kappa, selected-frontier change, or improved owner fill is claimed.
Physical native phases, compiler/common-label realization, the full owner's
chronological allocation, precision/source-access implementation, and an
all-size recursive/outer transfer remain inherited or unverified obligations.
Equal ordered widths alone would not certify a changed owner schedule. This
package does not charge an optimistic owner reuse as an additional gain.

**Open next questions:** any successful use of this pair must change a further
paid boundary, child rank, restoration path, or helper requirement. This
package provides no such change and undertakes no broader optimization.

## Sources and credit

- Dugongue / PR3945 supplies the two complete supplier words and their
  inherited staged/terminal, restoration, owner and native framework.
- Riquelme Soares (@hevlyo) / PR4061 supplies the exact frozen inputs and
  signed-consumer test. Its explicit open question is partial capture of
  agreeing consumers 175/183 while retaining exceptions 123/202.
- Chris R / Clear1nsight / PR4045 identifies this helper group and its
  support-restricted interface; no result from its allowance screen is
  strengthened here.
- PR4061 credits Tekalign / PR4048 for the same-frame signed-capture idea.
  Its global-sign mechanism does not directly apply to the disagreeing
  columns. The new contribution here is the displayed partial capture,
  its literal inverse/cancellation, complete dirty-input comparison, and
  the exact zero-profile result.
- Rohan Arun / PR4076 retains the imported audit core. That core is Sagar
  Thakrar's PR3687 code and credits Arham Tahir's coupled-carrier audit for
  its frame/word contract. It is reused source code, not a newly independent
  implementation. The separate rational six-cell calculation and reverse
  column traversal are identified above without claiming independent human
  review.

Retain the package Apache-2.0 license and all predecessor notices. The new
construction, verifier and write-up were prepared with substantial OpenAI
Codex assistance. No independent human review is claimed.
