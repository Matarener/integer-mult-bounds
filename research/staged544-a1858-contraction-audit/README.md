# Independent cleanup certificate for the A1858 contraction

**Partial. No new κ.** Selected κ stays `0.001672660197076918`.

## Scope and evidence

Original card: `independent-moment`, scope **refined**. This is not the #2979
rank-7 group audit and not the separated seven-block contraction in PR #4019
(upstream #4112). Discussion #1166 comment 19035159 asks for an independent
challenge of the consecutive A1858 contraction and its cleanup in
[PR #3998](https://github.com/CrocSwap/integer-mult-bounds/pull/3998), head
`389268a6b5e0373a3125d5c6fcd6995f4ea324f5`.

On all four frozen words vendored from that head, zero-based `A[1858:1861]` is

```
457 <- 457 - 475
456 <- 456 + 457
456 <- 456 + 475
```

with common frame `span(82,42)`. The two-ADD image

```
456 <- 456 + 457
457 <- 457 - 475
```

has the same exact rational matrix on `{456,457,475}`. An independent cleanup
derivation, which does not import PR #3998, reproduces each stored cleanup
section. Replacing the triple by the pair changes cleanup only by substituting
the three inverse ADDs

```
456 <- 456 - 475
456 <- 456 - 457
457 <- 457 + 475
```

with the two inverse ADDs

```
457 <- 457 + 475
456 <- 456 - 457
```

at one index (`3447` on both PR3734 words, `3448` on both PR3945 words). The
forward ADD count and the cleanup ADD count each fall by one. The deleted gate
is the inverse of the central ADD. The two surviving inverses also exchange
order; a pure deletion would not be the inverse of the contracted pair.

The same scan of every consecutive ADD triple in `A` after `prelude_events`,
in all of `B`, and in all of `restore` finds this one inverse site before the
edit and none after it. That domain is wider than PR #3998's warp-cut segments.
A wrong central sign, a reversed cleanup order, a helper destination omitted
from cleanup, and a target destination inserted into cleanup are rejected.
The general coefficient identity `[g,h] = [h,(i,k,-ab),g]` is checked for one
non-unit pair at the middle central position.

## What this does not establish

The recursive profile `{1:2440,2:725,3:224,4:102,5:20,8:8}` is not recomputed.
No frame climb, native operator, owner schedule, precision, stock, tape, or
supplier bill is replayed. The scalar saving is not integrated into a new
PR3945 producer. No selected-frontier change.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -B research/staged544-a1858-contraction-audit/verify.py
python3 scripts/research_package.py --package research/staged544-a1858-contraction-audit
```

Expected first line: `PASS_A1858_CLEANUP_CONTRACTION words=4 sites_before=1 sites_after=0 forward_add_delta=-1 cleanup_add_delta=-1 pr3734_cleanup_index=3447 pr3945_cleanup_index=3448`.

The four gzip inputs are byte copies of PR #3998 `inputs/`, pinned by the
SHA256 values in `verify.py`. Base commit `bb4bccbf42844d2801487450727c2f63e10d1d0f`.
Catalogue and selected-record provenance are in [SOURCES.json](SOURCES.json).

## Open next questions

- Recompute the frame bill of the contracted word, including the successor
  climb of registers 456, 457 and 475. The cleanup identity does not decide
  whether the published histogram is unchanged.
- The handoff's second half, carrying this scalar saving into the PR3945
  producer with native, owner and precision obligations, is still open. Stop
  if that bill repays the two removed ADDs.

## Credit

Dataisfire's PR3734 words and Dugongue's PR3945 words are the frozen inputs.
Chris R / Clear1nsight wrote the PR #3998 contraction and asked for this
check in discussion comment 19035159. The separated A2 audit in #4112 is a
different block. unpaidmoon, with substantial Cursor
Grok assistance. Apache-2.0. No independent human or formal-kernel review.
