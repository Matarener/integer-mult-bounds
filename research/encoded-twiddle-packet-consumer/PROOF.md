# Consuming one encoded synthetic-twiddle header

Copyright 2026 Sagar Thakrar. Apache-2.0. Prepared with substantial OpenAI
Codex assistance, including separate implementation and review agents.

## Statement and inherited producer contract

This is a source-relative join of one output of Nick Petalas's PR3593
`Controller` to one complete coefficient packet. The retained producer commit
is `46c04613a19a5b7bd50d98e50bbc8ea8dc6275b0` (exact bytes are recorded
in SOURCES.json).
Its exponent theorem is an explicit inherited premise, not reproved here.
No address enumeration, complete round, physical butterfly or outer caller
is supplied by this join.

Let `ell >= 2`, `r = 2^ell`, and let `w >= 2` be a signed component width.
The producer returns a raw, most-significant-bit-first header of `ell+1`
bits, its head at zero, representing `E` modulo `2r`. Its borrowed
descriptor starts with `^ 1^ell #` and is returned unchanged at its left
delimiter. The consumer reads those actual tapes. A separate borrowed
descriptor `^ 1^w $` supplies component width by a unary scan.

The coefficient source is one framed packet `^ bits $`, containing exactly
`r` Gaussian coefficients in increasing coefficient order. Each consists
of a signed MSB-first `w`-bit real component followed by its imaginary
component. These are complete coefficient words, not address bits. The
output uses the same framing and ordering convention.

Write `E = epsilon*r + s`, where `epsilon` is the first header bit and
`0 <= s < r` is its remaining binary word. The endpoint is multiplication
by `y^E` in `Z[i][y]/(y^r+1)`, on precisely this packet. Signed minimum
`-2^(w-1)` is forbidden in every component which this particular exponent
requires to negate; copying that minimum without negation is allowed.
In particular the stronger no-minimum input contract of the predecessor
packet implementation is sufficient. For unit-disk grid components the
source format `w=p+2` is sufficient as well.

The original producer executable restricts `ell` to 2..32 and its axis
count to 1..16. This package does not remove those admission caps or claim
execution of all mathematical shapes. The mathematical implication from
a valid encoded header is separate from finite simulator admission,
preallocation and the retained producer's general-family argument.

## Exact split and sign identity

For `f(y)=sum_(j=0)^(r-1) z_j y^j`, split the coefficient sequence into
its first `r-s` coefficients and last `s` coefficients. Since `y^r=-1`,

```
y^E f = (-1)^(epsilon+1) sum_(j=r-s)^(r-1) z_j y^(j+s-r)
      + (-1)^epsilon     sum_(j=0)^(r-s-1) z_j y^(j+s).
```

Consequently output the suffix before the prefix, negating the suffix
exactly when `epsilon=0` and the prefix exactly when `epsilon=1`.
When `s=0` the suffix is empty; this includes the identity header and
the all-coefficient sign change at `E=r`. Reducing a negative exponent
modulo `2r` preserves this rule because `y^(2r)=1`.

Both components of each coefficient receive the same sign. No Gaussian
component exchange, coefficient truncation or frequency permutation is
part of this operation. In particular it preserves every coefficient norm
and introduces no numerical error. Its inverse uses the residue of `-E`.

For a component to be negated, complementing its bits and adding one
computes its additive inverse modulo `2^w`. Except at signed minimum,
this is its exact integer negative in the signed `w`-bit range. The
minimum pattern is a leading one followed only by zeros. Detecting this
pattern while copying a word therefore suffices for the advertised guard;
no decoded component value is needed. Copying a word requires no such
restriction. The full consumer implementation and paid-control argument
below determine how these elementary identities are executed.

## Relation to the supplied exponent

The retained PR3593 output contract is

```
E = sign * 2^(ell-h) * sum_(i in I) x_(i,h) sum_(v<h) 2^v x_(i,v)
    modulo 2^(ell+1),
```

where `I` is the source's participating-axis set and `sign` is selected
by its direction symbol. The producer recovers that value from the actual
named-slot address and unary/flag descriptor. The consumer neither
reconstructs the exponent from a host integer nor decodes a host address
to choose its coefficient split. Thus, conditional on that exact producer
contract, the joined endpoint is the source's one-record synthetic
monomial. Named-slot interpretation, participation and exponent production
remain attributed to the predecessor.

This theorem supplies no record enumerator and no assertion that a caller
places headers beside the correct records. The join uses the actual
producer output and descriptor for one address explicitly supplied to it.

## The actual header and countdown control

`counts_from_header` reads the first header bit into the finite flag
`epsilon`. It then scans precisely the first unary descriptor field.
For every unary `1` it advances the raw header once and stages the next
bit on tape `a`. The first `#` ends this scan. Scanning the same unary
field backwards returns the header and descriptor heads to their entries;
neither borrowed tape receives a write. This uses no host-decoded `ell`
or exponent. Only this first descriptor field is needed by the consumer.

The staged MSB word is traversed backwards into the little-endian counter
`b`, followed by one high zero and an end delimiter. It therefore represents
`s` in `ell+1` bits. A complement-and-carry pass computes `-s modulo 2r`
into `a`; toggling its highest bit gives `r-s`. If `s=0`, that toggle
turns zero into `r`. Otherwise it turns `2r-s` into `r-s`. The prefix
counter is consequently always positive and the suffix counter may be zero.

`mark_top` replaces the highest nonzero digit by the special digit `2`,
which means a one bit marked as most significant. A finite flag represents
the zero case. Counter heads return to their `^` delimiters. `decrement`
starts at the low bit, turns each trailing zero into a one, then turns the
first one into zero. If that one was the marked top, either the counter is
now zero or the next lower digit is marked as its new top. It returns to
the left delimiter immediately. It does not scan the whole counter after
every coefficient. This proves both the numerical decrement and the local
zero-detection invariant.

For a positive current value `n`, the scan visits `nu_2(n)` trailing
zeros and one terminating one. A complete countdown from `N` has

```
sum_(n=1)^N nu_2(n) = sum_(k>=1) floor(N/2^k) < N.
```

Thus both countdowns together take `O(r)` primitive operations, after
their `O(ell)` initialization, because their initial values add to `r`.
Return scans are over just the digits visited by that decrement; they
do not introduce an `ell` factor per coefficient.

## Packet traversal, signs and successful restoration

`split` consumes its counter by one decrement per coefficient. Its finite
control calls `copy_word` exactly twice per coefficient, real then imaginary.
Each call scans the actual unary width descriptor, copying one current-cell
source bit per unary `1`, and then returns the width head by its delimiter.
It follows that the prefix receives exactly the first `r-s` coefficients
and the suffix exactly the remaining `s`. The source must then be at its
end delimiter. Both buffers receive their own end delimiter and their
heads return to the left delimiter.

`emit` traverses the suffix first, then the prefix, ending each at its
buffer delimiter. `emit_word` copies exactly one unary-width component to
the word tape while recording its sign and whether any lower bit is nonzero.
For a negation it rejects precisely the minimum pattern and performs the
right-to-left complement-and-carry pass proved above. It then copies the
word forwards into the output. A following word overwrites the same word
extent, so the previous contents are never treated as new input.

The signs passed by `run` are `not epsilon` for suffix negation and
`bool(epsilon)` for prefix negation. These are exactly the signs in the
algebraic identity. Every input coefficient is copied once, emitted once,
and retains real/imaginary component order. An empty suffix ends at its
delimiter without emitting any component. The output receives its final
delimiter and its head returns to zero.

The borrowed source and unary width descriptor are never written and
return to their left delimiters. Header and producer descriptor were
already restored before coefficient processing. On successful return,
`clear` scans each of the five private scratch tapes to its capacity guard,
clears that guard, returns by the still-present left delimiter while
clearing the interior, then clears the left delimiter. All their cells
are zero and their heads are zero. The output remains framed with its
capacity guard; that guard is storage metadata beyond the output delimiter,
not an extra coefficient bit.

On a signed-minimum rejection in an otherwise valid admitted packet, the
same `finally` block clears all five scratch tapes and also the partial
output. The borrowed heads are restored. This is a one-shot consumer,
including after rejection. Malformed framing, mismatched host capacities,
interruption and external tape mutation are outside this restoration
contract; an exception path for arbitrary malformed tapes is not claimed.

## Encoded initialization and the physical inventory

The constructor admits and allocates blank simulator storage using `ell`
and `w`; it executes no consumer tape operation. Matching allocated extents
are a valid-input precondition. It does not supply an exponent or a schedule
to `run`. Host allocation, list management and validation costs are not
asserted to be physical tape operations.

The actual `initialize` operation frames the three packet tapes by scanning
the borrowed source from `^` to `$`, initializing one cell on each of the
three roles per actual input bit. It adds an endpoint cell and a capacity
guard, then returns all heads by their left delimiters. The word tape is
initialized analogously from the actual unary width descriptor. Both counter
tapes are initialized from the producer descriptor's actual unary `ell`
field, with one extra binary digit, endpoint cell and capacity guard.
These reads, writes, unit moves and tests are charged. Thus the initialization
schedule itself is encoded-input-driven; it is not justified merely by
charging host loops over decoded capacities.

After allocation, `run` and its helpers inspect a tape only through its
current-cell `read`, `write` and unit `move` methods. Their loops terminate
on actual delimiters, unary symbols, or the marked-counter zero flags.
The role tuples have fixed size, and copying the real and imaginary words
is a fixed two-call control sequence. `epsilon`, carry, zero, sign and
minimum-detection state have finite ranges. `capacities`, Python head indices
and stored cell arrays are allocation/diagnostic data, not inputs to the
executed control. The dictionaries describing named roles have fixed size.
No trace or decoded exponent table is retained.

Put `L=2rw`. The six owned tape capacities, including framing/guards, are

```
prefix, suffix, output: each L+3
word:                   w+3
a, b:                   each ell+4
owned total:            3L+w+2ell+20.
```

Let `C_source` be the borrowed source's actual allocated capacity, at least
`L+2`; its active framed packet ends at `$`. Extra capacity after that
delimiter is not consumed. In particular a prior consumer output has
capacity `L+3`, including its trailing guard, and is a valid source without
copying or removing that guard. The width descriptor uses `w+2` cells.
The header and producer descriptor are shared existing tapes, not copies.
Therefore joining this consumer to the retained producer increases the
allocated finite-alphabet capacity by exactly

```
3L+2w+2ell+22+C_source.
```

For a minimally framed source this is `4L+2w+2ell+24`; for a prior guarded
output it is `4L+2w+2ell+25`. With the retained producer's 26 tapes the
join has 34 fixed tape roles. If `C_prod` is its stated capacity, add the
displayed increment to it, counting its output header and descriptor once.
If the source is retained from an earlier operation in a larger caller,
deduplicate that actual tape too when forming the larger caller's inventory.
This is tape capacity, not Python object memory or a bit-encoding count.
The alphabets and finite-control state are fixed independently of the shape.

## Paid consumer bound and joined invoice

The consumer tariff counts every current-cell read, write and unit move,
plus each explicit fixed finite-control gate recorded by `gate`. A named
Boolean gate such as complement-and-carry is one fixed macro in this tariff,
not a claim that its implementation uses only one Boolean primitive.
The remaining dispatch/control transitions require a constant factor per
recorded action or fixed macro entry. Thus a tariff bound also gives the
stated asymptotic full-transition bound, without asserting an exact numeric
count for every machine-state transition.

The following conservative phase bounds follow directly from the loops.
They include the head-return scans; their deliberately loose constants do
not use finite timing measurements.

| Phase | Upper bound in recorded actions |
| --- | ---: |
| Encoded initialization | `23L+11w+16ell+120` |
| Header staging, counter construction and top marking | `100ell+100` |
| All `copy_word` calls | `11L+20r` |
| All `emit_word` calls | `27L+60r` |
| Both complete countdowns | `23r` |
| Remaining split/emit guards, packet returns and fixed control | `12L+8r+100` |
| Five successful scratch clears | `16L+8w+16ell+106` |

For example, a `copy_word` costs at most `11w+10`, and there are `2r`
such calls. An `emit_word`, including its negation branch and word return,
costs at most `27w+30`, again for `2r` calls. A decrement costs at most
`7nu_2(n)+16`; the valuation identity gives the countdown row. For a scratch
tape of capacity `C` initially at its left delimiter, `clear` costs exactly
`8C-6` in this tariff. The capacities above give the last row. Empty
segments still incur their delimiter/return overhead, included in the
fixed-control row.

Summing the displayed bounds gives at most
`89L+111r+19w+132ell+426`. Since `w>=2`, `r<=L/4`, so this is bounded by
`120L+24w+144ell+512`, and hence, for `ell>=2`,

```
T_consumer <= 256*(L+ell+w+1) = O(rw+ell).
```

The verifier's exact tariff is the sum of the actual per-role action
counters and finite-gate counters, not this upper bound substituted for a
measurement. Consumer actions on borrowed producer tapes are measured as
increments during the consumer call. If `T_prod` denotes the producer's
recorded action/gate invoice at the end of its call, the joined invoice is
`T_prod+T_consumer`. Summing producer counters again after consumption would
double-count the header/descriptor increments and is not this formula.

Under the predecessor's source band `D*ell=O(p)`, its established allowance
is `O(p^3)` producer transitions. Consequently this one-header/one-packet
join has `O(p^3+rw+ell)` transitions. With `w=O(p)`, `ell=O(p)` and the
retained long-record hypothesis that `r` eventually dominates every fixed
power of `p`, this is `O(rp)` per supplied record. This is an asymptotic
conditional implication, with no explicit cutoff, complete layer invoice,
address-enumeration cost or caller/stock/dirty-restoration admission.

## Attribution, evidence and remaining boundary

Nick Petalas's PR3593 supplies the encoded header producer, unary shape
protocol, exponent proof and full polynomial producer invoice; PR3582 is
its retained direct-operation predecessor. His `synthetic-monomial-packets`
supplies the earlier signed packet endpoint and data-only invoice, whose
host-provided integer headers left this encoded join open. The source
transform and their retained predecessor notices remain credited. The
split/sign algebra and linear packet cost were already stated there; they
are not new transform identities.

This package's contribution is the actual paid connection through the raw
header and unary descriptor, including carry-stopping encoded coefficient
countdowns and encoded scratch initialization. Finite execution checks
corroborate the endpoint, counters, guard and restoration claims on their
listed cases; they do not prove unbounded quantifiers. The written argument
is not independent human acceptance or a proof-assistant certificate.
The producer theorem is inherited and its full source chain is identified
in the manifest. No complete synthetic round, T74 refinement, production
native object, numerical error chain, supplier admission, new multiplication
exponent or selected-frontier change is claimed.
