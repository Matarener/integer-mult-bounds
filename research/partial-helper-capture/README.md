# Partial capture of two staged544 consumers

The temporary sum capture is exact, but does not reduce the recursive child
profile or either helper width. This answers the concrete partial-capture
question left by [PR4061](https://github.com/CrocSwap/integer-mult-bounds/pull/4061)
on its two frozen PR3945 words. No new supplier or kappa is claimed.

## Construction and cost

Write `x = helper600`, `y = helper601`. At the common frame `(45,)`, the
original block adds `(x+y)/4` to each of targets 175 and 183, and
`(-x+y)/4` to each of targets 123 and 202. All six registers may contain
arbitrary entering values. One exact partial capture is:

1. Keep the four disagreeing reads into 123 and 202.
2. Set `x += y`, add `x/4` to 175 and 183, then set `x -= y`.

The source pair returns literally to `(x,y)` before the next original event.
The eight scalar ADDs replace eight scalar ADDs. Both helpers already enter
at `(45,)`; every original read in this block occurs at that same frame and
the first native warp is later. Each of the four targets climbs from ZERO
to `(45,)` once, contributing four rank-one children. The capture retains all
four target climbs and introduces no helper climb. The disagreeing reads
keep both helper roles.

Literal reverse cleanup contains two additional adjacent inverse shears.
Their product is the identity, so explicit cancellation recovers the original
cleanup exactly. The strongest version of this candidate has zero complete
scalar delta; keeping the unsimplified literal cleanup adds two scalar ADDs.
Both have the same native child profile and widths:

| Invoice | Frozen word | Partial capture |
| --- | ---: | ---: |
| Rank 1 children | 2482 | 2482 |
| Rank 2 children | 712 | 712 |
| Rank 3 children | 218 | 218 |
| Rank 4 children | 109 | 109 |
| Rank 5 children | 20 | 20 |
| Rank 8 children | 8 | 8 |
| Helper widths 5 / 6 / 7 / 8 / 9 | 28 / 18 / 53 / 96 / 213 | unchanged |

Thus the difference of the local moments `sum H_r * r^(1-a)` is exactly zero
for every exponent `a`. Helper identities, invocation endpoints and width
requests are unchanged, so this splice supplies no new owner-residual saving.
No new physical owner fill or complete supplier admission is asserted.

The partial capture reduces target writes by two and adds two helper writes.
Each helper is still read four times in the block; its later paid native climbs
and helper role remain. Those scalar changes are not a new recursive saving.
The `0.03825` allowance discussed for PR4045's different
rank-16 replacement is not an allowance for this splice.

## Evidence and exact scope

The public checkers and their result files document the exact source, local
matrix, whole-word dirty-input, inverse-transpose, literal cleanup, frame and
rejection-control coverage. See [construction/DERIVATION.md](construction/DERIVATION.md)
and the separate [independent review](independent/REVIEW.md).

The matrix identity is a written argument for arbitrary vector-valued fields
with dyadic coefficients, under the common identical frame representative.
The source bindings and whole-word tests concern exactly two finite words.
They are not a formal-kernel proof, an approximate/native phase replay, a new
owner/precision/tape/stock proof, or a new multiplication theorem.

More generally, under the inherited monotone, single-register native contract,
any replacement with these six physical block endpoints must pay the four
targets' ZERO-to-`(45,)` transitions. Each has dimension difference one, so
four rank-one children are a sharp floor; the original block attains it.
This does not exclude a different source boundary, changed surrounding
itinerary, extra storage, a different consumer or a changed joint-child ABI.
The larger-kappa target remains open; this run stops on the zero-saving result.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/partial-helper-capture
```

The registered commands are self-contained within this package and also run
in an official Git-free export. Local replay, hosted CI and mathematical
acceptance are separate evidence gates.

## Sources and credit

Canonical base: `bb4bccbf42844d2801487450727c2f63e10d1d0f`, priority revision 6.
[SOURCE-EXPORT.json](SOURCE-EXPORT.json) maps the retained bytes to their exact
original public heads and paths; [SOURCES.json](SOURCES.json) binds their
source-only publication ancestor. These two provenance roles are distinct.

Riquelme Soares (@hevlyo), PR4061 at
`f977a8a3dcb2983829d066a80420b7ded42d3e09`, supplies the sign-column result and
the open partial-capture question. Dugongue's PR3945 supplies the frozen words,
retained through Chris R / Clear1nsight's PR4045. Tekalign's PR4048 supplies the
same-frame capture idea. Rohan Arun's PR4076 retains the audit core written by
Sagar Thakrar, with its Arham Tahir contract lineage. The original staged-entry,
geometry, compiler, native, owner and outer credit remains in the unchanged
[predecessor note](predecessor4061/README.md) and
[source notice](source4076/NOTICE.md).

New construction, exact checks and scoped comparison: Ross Richardson with
substantial OpenAI GPT-6.1 Sol assistance, including separate mathematical AI
contexts. AI checks are not independent human review. Apache-2.0; retained
source licenses and notices apply. The canonical investigation is
[Discussion4060](https://github.com/CrocSwap/integer-mult-bounds/discussions/4060#discussioncomment-19051443).

## Open next questions

A useful successor must change a source or consumer boundary so that a real
positive-rank visit or helper role disappears, then pay the changed access,
restoration and owner costs. Specify that boundary and a favorable complete
invoice before another construction. This package provides no such successor;
it does not justify a new search over the same scalar block.
