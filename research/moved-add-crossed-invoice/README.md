# Moved-ADD crossed frames have a zero local invoice

**No new κ.** Selected conditional κ stays `0.001672660197076918`.

On three scalar registers, swapping two commuting additions and retargeting both
frames from one line to the other crossed line is a legal final word. Each
one-move intermediate is frame-illegal. The scalar map is the identity
`y := y + x + z`, including arbitrary initial values, and the inverse cleanup
restores those values. The charged rank histogram is six rank-1 children on
both words, so the delta is zero.

## Scope and evidence

Catalogue card `scalar-to-moment`, scope **refined**. The card asks whether one
scalar simplification changes a paid histogram. This package answers that for
the moved-ADD pair requested by
[discussion #1166 comment 19034220](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19034220),
not for an R439 helper-star word.

The predecessor stationary census (open PR #3964) proves that no such pair
exists while both ADD addresses stay fixed on the pinned PR #3734 providers.
Its synthetic control, old frames `span(e1)` and new frames `span(e2)` between
`{0}` and `span(e1,e2)`, is not a gate move. The witness here is that same
frame pattern realized by a move that the predecessor reorder test allows.

### Identity

Let `A` be `y += x` and `B` be `y += z`, with coefficient 1. Each gate's target
is not the other gate's source, so the predecessor reorder test lets either
gate pass the other and does not change the coefficient. Over any ring,

```text
A then B  =  B then A  =  (x, y + x + z, z)
```

from an arbitrary initial triple. The cleanup `y -= z` then `y -= x`, also at
coefficient 1, restores the initial triple after either order. Replacing either
coefficient by 2, or swapping the noncommuting pair `y += x` then `z += y`,
breaks the equality. Both of those controls are checked.

### Frames and invoice

Frames are subspaces of `F_2^9`, stored as bit masks. A visit is legal only
when the current frame is contained in the gate frame. The charged child has
rank equal to the dimension gap. Every register starts at `{0}` and must finish
at `V = span(e1, e2)`.

| Word | Order and frames | `y` chain | Histogram |
|---|---|---|---|
| Original | `A` at `L`, `B` at `L`, then cleanup at `V` | `{0} ⊆ L ⊆ L ⊆ V` | six `H1` |
| Moved pair | `B` at `M`, `A` at `M`, then the same cleanup | `{0} ⊆ M ⊆ M ⊆ V` | six `H1` |
| Only `A` moved | `B` at `L`, `A` at `M` | `{0} ⊆ L ⊆ M` | illegal |
| Only `B` moved | `B` at `M`, `A` at `L` | `{0} ⊆ M ⊆ L` | illegal |

`L = span(e1)` and `M = span(e2)` are distinct lines, so neither contains the
other. The `x` and `z` chains are one line visit plus the climb into `V` on
both legal words. Cleanup uses frame `V` and adds the three remaining rank-1
climbs. Rank mass is 6 on both words. The histogram delta is the zero vector,
so `sum_r delta_r r^a = 0` for every real `a`. An unchanged histogram is not a
κ gain.

The same-line swap, both frames `L`, is legal. Illegality comes from the
crossed lines, not from the reorder itself.

### What this does not separate from a saving

Widening both moved frames to `V` has delta `-6 H1 + 3 H2` against the original
word. For every integer fraction `0 < p/q < 1`, `2^p < 2^q`, so
`3 (2^a - 2) < 0` throughout `0 < a < 1`. That local moment decreases. The
one-move intermediate that widens only `A` and leaves `B` on `L` is legal, so
this saving sits in the sequential contract. It is a control, not a provider
occurrence and not a supplier admission.

No PR #3734 word was searched. Native warps, centre cuts, stock, precision,
tape, all-size transfer and both supplier caps are absent. They are not priced
as zero.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/moved-add-crossed-invoice/verify.py
python3 scripts/research_package.py --package research/moved-add-crossed-invoice
```

Expected marker:

```text
PASS_MOVED_ADD_CROSSED_INVOICE registers=3 adds=2 cleanup=2 histogram_H1=6 delta=0 rank_mass_delta=0 both_intermediates=illegal scalar=commuting_identity favorable_sequential=-6H1+3H2 one_intermediate=legal no_new_kappa
```

The checker raises on a failed containment, a broken identity, or a histogram
mismatch. It does not sample the providers.

## Open next questions

Does any moved-ADD pair on the two pinned PR #3734 providers have a legal final
frame assignment, two illegal one-move intermediates, and a strictly negative
moment for every real `a` in `(0,1)`? The three-register witness only shows that
a move can create the crossed-line pattern, and that this pattern can have
invoice zero. The first step is one scalar segment and the crossed-line
assignment on pairs the reorder test already allows to cross. The provider trace
lives in open PR #3964 rather than on this main checkout, and a full pair census
is a separate budget.

## Credit

The stationary census, the synthetic crossed-line control and the reorder test
are Chris R / Clear1nsight, PR #3964, head `8a8bfb8d36cf5c9f7681b9e7f5d7876a4ba0f5a0`.
The open question is discussion #1166 comment 19034220. The legal-sequential
predecessor is PR #3942. The paid exchange that motivates a histogram change is
Dugongue's PR #3863; this witness does not realize that `H1 - 2 H2 + H3`
exchange. The pinned providers are dataisfire's PR #3734 and are not replayed
here.

Prepared by unpaidmoon with substantial Cursor Grok assistance. No independent
human review is claimed. Apache-2.0.
