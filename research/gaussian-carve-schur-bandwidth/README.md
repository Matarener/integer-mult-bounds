# Boundary-order bandwidth of the separated Gaussian carve

**Scoped audit, no new κ.** One precision/conditioning step of the proposed
#4100 construction holds at the retained dyadic carve. Selected κ stays
**0.001672660197076918**.

## Result

Let a matrix have bandwidth `b` when it vanishes for `|i-j| > b`. Eliminate
disjoint contiguous interiors, and write the Schur complement in survivor
order (the order GAUSSIAN.md calls boundary order: original order with each
eliminated gap closed).

**Theorem.** If at least `b` survivors lie between successive interiors, and
each eliminated block is invertible, that Schur complement has bandwidth at
most `2b-1`. One middle interval already attains `2b-1`, and so does a pair
of intervals separated by exactly `b` survivors. The constant cannot be
replaced by `b`.

**Application.** #4100's carve, as specified by the retained capped-interior
loop, puts exactly `W` boundary vertices between successive interiors and
reserves `W` vertices at each end of a phase cell. GAUSSIAN.md truncates at
physical half-bandwidth `W`, so `b = W`, and calls the same separation
"interior neighbors are separated by `W`". The Schur matrix in boundary order
therefore has bandwidth at most `2W-1`. That is `O(W)`, which is the claim in
GAUSSIAN.md, and it is the same cap PR #4285 proved for one middle interval.
Separated interiors do not force a wider band. The written boundary costs
`O(V d W^(τ-1) / B polylog(p))` and `O(V d W / B polylog(p))`, with
`τ = 45/16`, stay valid: replacing `W` by `2W-1` multiplies a pure power
`W^(29/16)` by less than 4.

**The separation hypothesis is necessary.** For bandwidth 2, singleton
interiors separated by only one survivor have Schur bandwidth equal to the
interior count on every chain of length 1 through 8. From four interiors
onward that exceeds `2b-1 = 3`, and the band keeps growing through the
checked range. An entry at distance `b+2`, with nothing eliminated between
its endpoints, also escapes the cap. GAUSSIAN.md's `O(W)` sentence is not
claimed for that shorter gap.

## Proof

Number coordinates by integers. Interiors are `B_k = {L_k, ..., R_k}` with
`R_k < L_{k+1}` and `S_k = L_{k+1} - R_k - 1 ≥ b`.

The closest indices of `B_k` and `B_{k+1}` differ by `S_k + 1 ≥ b + 1 > b`,
so the pivot block has no entry between distinct interiors. It is their
direct sum, and the Schur update is the sum of the individual updates.

A survivor meets `B_k` only from the original-index rim `[L_k - b, L_k)` or
`(R_k, R_k + b]`. Because the neighbouring separator contains at least `b`
survivors, that rim lies entirely in the separator and contains no other
interior. Two survivors on the same rim are at most `b - 1` apart in both
original and boundary order. A left-rim survivor `u` and a right-rim survivor
`v` satisfy `v - u ≤ R_k - L_k + 2b`, and the only eliminated indices between
them are the `R_k - L_k + 1` points of `B_k`. Closing that gap leaves
boundary distance at most `2b - 1`.

An original entry has `|u - v| ≤ b`. Eliminated indices between its endpoints
only shorten boundary distance, so the entry stays within distance `b`.
Entries with neither an original coupling nor a common rim are zero. The
bandwidth is therefore at most `2b - 1`.

A prefix pivot has an empty rim on one side, so it has no cross term and the
bandwidth is at most `b`. The retained loop reserves `W` endpoints before the
first interior, so every carved interior is two-sided and the sharp cap is
`2W - 1`, not `W`.

PR #4285's 7×7 witness (off-diagonal `-1/8`, eliminate `{2,3,4}`) attains
bandwidth 3 with far entry `-1/432`. The two-interval host in the verifier,
separator exactly `b = 2`, also attains bandwidth 3. Both are inside the
support count above; neither is an exception to it.

PR #4298 and PR #4299 certify one interior on one equal-weight path, of
bandwidth 2 and 3, for a few lengths. They do not bound a second interior,
and both say they do not measure the truncated Gaussian row. The counting
argument above is what lets the retained loop delete every interior at once.

## What was not proved

This does not price inverse norms, Gaussian tails, halo rectangles, or a
circular phase cell. PR #4286 already shows that a circular band can follow
arc length; the linear theorem uses the retained period cuts and endpoint
strips as boundary. No Strassen leading constant is recomputed, and no
#4100 executable window is replayed. Finite samples are certificates for the
sharp and failing hosts. The all-size support bound is the counting argument
above, not an extrapolation from those hosts.

The RHS batch "between `W` and `2W`" is a count of right-hand sides. It is
wide enough to hold one row of a `2W-1` band. This audit does not decide
whether some narrow solver instead builds triangular factors of width exactly
`W`. GAUSSIAN.md states `O(W)`, not `≤ W`.

## Reproduce

CPython 3.12, standard library only, from the repository root:

```sh
python3 -B research/gaussian-carve-schur-bandwidth/verify.py
python3 scripts/research_package.py --package research/gaussian-carve-schur-bandwidth
```

The verifier recomputes the #4285 witness, the separated-cap layouts for
bandwidth 1, 2 and 3, the growing under-separated chain, an out-of-band
failure control, and a singular-pivot rejection. It also checks the pinned
GAUSSIAN.md and CAPPED-GAUGE-AUDIT.md sentences and `7^16 < 2^45`.

## Open next questions

1. Does any narrow boundary solve on this Schur complement use triangular
   windows of width exactly `W`? That would miss the `2W-1` fill even though
   the `O(W)` cost sentence survives. The first step is to bind one narrow
   solve in the retained shallow-Toeplitz schedule to a concrete window width.
   Blocker: GAUSSIAN.md does not name that width; it names `O(W)` and an RHS
   batch of width at most `2W`.

2. Does every #4100 phase cell retain a period cut through elimination? A
   circular cell with no retained cut is the setting where PR #4286 lets
   bandwidth follow arc length. The first step is one full-period cell in the
   caller, with its cut marked boundary before the carve. Blocker: this
   package audits the linear loop and does not replay the tensor caller.

## Credit

The carve sentence and the `O(W)` claim are Cinna Davis's #4100
`GAUSSIAN.md`. The loop that retains the next `W` vertices as boundary is the
capped-interior audit in `research/capped-phase-fusion/CAPPED-GAUGE-AUDIT.md`.
The one-interval cap `2b-1`, the witness ratios, and the far entry `-1/432`
are jwr's PR #4285; they are recomputed here and not imported. PR #4298 and
PR #4299 are the one-interior boundary-order checks on equal-weight paths.
PR #4283 and PR #4286 are the neighbouring bandwidth audits. PR #4311's
coverage map is the checklist that still listed the carve comparison as open.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human or formal-kernel review is claimed.
