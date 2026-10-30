# Typed actual-width physical H

**A one-round rounded return for the matched twiddle layout. No new κ.**

PR #3623 proves a matched chunk width `K = floor((d-1)^(1/500))` and joins
PR #3617's fixed diagonal to arithmetic-oracle butterflies. Its first open
question is a typed physical `H` and toward-zero `Q_p` on that same array.
This package supplies that call: MSB packet words in, physical-order rounded
tensor out, with an exact read/write/gate bill and a data-independent head
itinerary. It does not build the inter-round stock contract.

## Result

For each round of the ten small layouts used by PR #3623's cube checker, and
for both original and physical source orders, the tape program equals PR
#3623's explicit tensor followed by toward-zero division by `2^g`. The
borrowed source is unchanged, scratch and per-bit auxiliary tapes are
blanked, heads return to cell 0, and a second call is rejected. The old
descriptor `(0, 1, 2)` is rejected on the matched round whose bits are
`(3, 4, 5)`. A numerator `17` at `p = 4` is rejected before the butterfly.

The bill depends only on the record count, coefficient count, selected-bit
count and precision. On the two-record witness it is 768 reads, 1200 writes
and 620 gates. Across the 50 calls the totals are 18,871,808 reads,
27,630,304 writes, 94,213,460 moves and 9,636,792 gates. [PROOF.md](PROOF.md)
derives the closed form. The cube comparisons are wiring controls for that
schedule, not a production-width execution.

Arithmetic right shift is a different return: `-1` shifted by one bit stays
`-1`, while this `Q_p` returns `0`. Skipping the LSB-to-MSB bridge changes
the integer `1`.

## Evidence

The frozen tensor is byte-identical to `check_join.py` at PR #3623 head
`c5ab698bba8b35323e40ae3b132e78f26179d393` and at the handoff head
`328c40966b650f60b1d62cfb0b1d67b2b755eb62` (git blob
`421ae05f081ec37e4c5fa0b1b7e200a1578ab16d`). The current PR head only adds a
workflow commit after that scientific file. `Q_p` was also checked on every
integer in `[-2^{p+g}, 2^{p+g}]` for `p = 4` and `g = 0..6`.

From the repository root, with Python 3.12 and the standard library:

```sh
python3 -B research/typed-actual-width-physical-h/verify.py
python3 -B -O research/typed-actual-width-physical-h/verify.py
python3 -B scripts/research_package.py --package research/typed-actual-width-physical-h --check-only
python3 -B scripts/research_package.py --package research/typed-actual-width-physical-h
```

Both direct runs print `PASS_TYPED_ACTUAL_WIDTH_PHYSICAL_H` and match
[RECEIPT.json](RECEIPT.json). On this host each direct run took about 10
seconds. The registered launcher was also run, as recorded in the PR.

Not run: the selected cold replay, Lean, Docker, a production `ell`, the
PR #3617 diagonal, and any all-round tape reuse.

## Open next questions

1. Can one fixed collection of full-cube tapes carry every round, with
   previous-output reset and a proved simultaneous-stock bound? The diagonal
   pass is one-shot and this `H` allocates its auxiliary tapes per selected
   bit. A useful first step is one two-round schedule on the `ell = 2`
   witness with an explicit buffer list. The blocker is that no such shared
   inventory is constructed here.
2. Can this return be placed under PR #3617's framed diagonal on one complete
   cube without a fresh stage object per round? That would discharge the
   fixed-`h` join, not the inter-round stock question. The blocker is the
   one-shot full pass and the still-unpriced initial framing.
3. Does any of this change the retained outer movement bottleneck? No faster
   exponent is claimed. Reopen that only with a paid movement change. The
   blocker is the unchanged `169711/2000000000000` ordinary term.

## Credit

The matched layout, tensor and toward-zero truncation are Clear1nsight's PR
#3623, incorporating Sagar Thakrar's PR #3617 diagonal contract and the
PR #3493 / #3593 / #3599 / #3611 sources credited there. The handoff is
discussion #1166 comment 19016699. New tape schedule, bill and checks by
unpaidmoon, with substantial assistance from Grok 4.7 in Cursor. No
independent human or formal-kernel acceptance is claimed. Apache-2.0.

## Relation to the parallel arithmetic invoice

While this package was being checked, the same account posted a different
one-round answer to comment 19016699: discussion comment 19056745 and
upstream PR #4123 (`research/typed-actual-width-h`, head
`499427578245cbd3d2b07680945a94f6e927d020`). That invoice counts normalized
`H0` add/sub operations, truncations and bit touches, and proves a Euclidean
error below `sqrt(2) 2^{-p}`. This package does not repeat that count. It
prices the unnormalized butterfly as a one-shot tape program: sequential
split, interleave, adjacent butterfly, deinterleave and merge, then
toward-zero division by `2^g`, with a closed read/write/gate form and a
data-independent head itinerary. The two artifacts can be reviewed
separately. Neither prices inter-round stock or the PR #3617 diagonal.
