# Two-neighbour ADD moves do not improve the raw moment

**No new κ.** Selected κ stays 0.001672660197076918.

This is a scoped obstruction for one frame-path change left open by
[PR #3942](https://github.com/CrocSwap/integer-mult-bounds/pull/3942).
It is not a review of that paper's interaction or new-gap reduction, and it
is not the radius-one theorem. The first displacement there is one neighbour.
Here the first ADD crosses at least two scalar neighbours.

## Result

Fix either literal PR #3734 provider word carried by PR #3942. Consider an
existing ADD, a cut in its commuting corridor that passes at least two gates,
and any common frame dimension legal for the removed-gate interval at that
cut. The raw rank-moment delta of that first move is nonnegative for every
real `0 < a < 1`. The certificate is the predecessor curvature test: rank
mass zero and nonnegative partial sums of `C_k = sum_r d_r min(r, k)`.
The first-move price depends only on dimension, by the interval formula in
PR #3942, PROOF.md §4, so this dimension census covers every subspace of
the same dimension.

Each provider has 5,501 ADD gates, 4,979 of them with a long cut, and
1,761,760 dimension cases: 239,103 nonzero and 1,522,657 neutral. The two
providers agree on these counts. None improves.

One changed-frame witness on the base word is gate `A[595] = add 459 510`
with coefficient `-1` and empty frame. Moving it to cut `1214` crosses 618
gates, including both an ADD and a SCALE, and the only legal rank-1 frame
is `span{85}`. The frame bill changes by `+3` rank-1 children and `-1`
rank-3 child. Its caps are `[2, 1, 0, ...]`, so the move is strictly losing.
After the coefficient update and rederived cleanup, the edited word passes
the vendored frame auditor. Every one of the 1,767,681 single-ADD
retimings of that edited word keeps the combined histogram certified
nonnegative. This witness does not unlock a saving inside that single-move
class.

## What this does not show

A second move that itself changes a frame interval of quotient rank greater
than 1, or a second cut that is priced only after another long move, is
outside the continuation census. Native phase, hosting, stock, precision,
tape, all-size transfer and both supplier caps are not repriced. Unknown
costs are not zero. The scalar crossing rule is the sufficient PR #3886
condition, not every algebraic commutation. No 632-input free-operator
replay was repeated. This is not a multiplication theorem.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/staged544-two-neighbour-invoice/verify.py
python3 -B scripts/research_package.py --package research/staged544-two-neighbour-invoice
```

The expected first line starts
`PASS_STAGED544_TWO_NEIGHBOUR_INVOICE` and ends with `improving=0 no_new_kappa`.
The registered timeout is 180 seconds. A local run is well under that.

`vendor/retiming.py` is byte-identical to PR #3942 at
`1416f8cd6bfb2f2eb9aa5cc22f0388a85fdbac91`. `vendor/audit_core.py` and both
`inputs/BORROW-WORD-43*.json.gz` files are the copies carried in that
package. SHA256 values are checked before use.

## Open next questions

1. Does every long first move, not only `A[595]`, keep every single-ADD
   continuation nonnegative? One witness cannot extend the radius-one
   theorem. The first step is the same continuation census on a move whose
   frame interval has quotient rank greater than 1.
2. Can a second ADD that itself crosses two neighbours improve the combined
   raw moment? Freeze one edited word and one such second cut before any
   larger search.

## Credit

PR #3734 / dataisfire for the provider words. PR #3886 and PR #3942 /
Chris R, Clear1nsight, for the retiming rules, curvature test and the open
two-neighbour question. Sagar Thakrar for the frame auditor. The radius-one
interaction reduction remains their argument; this package does not review
it. New census and witness by unpaidmoon, with substantial Cursor Grok
assistance. Apache-2.0.
