# One-role compilation of the cap-two schedule loses to the direct swap recipe

**Scoped negative bill; no new κ.** The open handoff at
[discussion 1166, comment 19142691](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19142691)
asks for one eligible chronological caller and a complete
`F,Q,B,wNew,wDirect` bill for the cap-two ABI, then the strict test

```text
B < (2F + 6Q - Delta)/4,    Delta = wNew - wDirect.
```

This package names the caller the selected one-role BIT service can
actually run: the five-call schedule of
[#5083](https://github.com/CrocSwap/integer-mult-bounds/pull/5083),
compiled call-by-call into unweighted reversed calls. That bill fails the
test on the accounting screen already used by
[#5099](https://github.com/CrocSwap/integer-mult-bounds/pull/5099).
The selected conditional result stays
`κ = 605457647/200000000000`.

## Caller and bill

The formal schedule applies `a` on owners `{0,1}`, `b` on `{0,2}`, `a` on
`{2}`, `b` on `{1,2}`, and `a` on `{0,1}`. Under the reversed reading in
`notes/three-stage-cover-bit.tex`, `aba` is the ordinary swap `J13`. The
direct competitor for three such targets is the note's recipe
`J_A = R_tail F_A R_tail`, at most one width-`f` reversed call and two
width-`floor(f/2)` reversed calls on the same volume. Three targets
therefore cost at most `3F+6Q`, with `wDirect = 0` inside that count.

The selected integer-width contract
(`notes/batched-bit-rows.tex`, general moment paragraph) gives each child
exactly `1/W` of the parent volume, and repetitions are separate calls.
[#5099](https://github.com/CrocSwap/integer-mult-bounds/pull/5099) records
the matching volume reading: two owners placed in one call raise the volume
to `2V/W` and do not create a cap-two discount. Each selected owner must
change, and a reversed generator on one owner is one unweighted width-`f`
call of price `F`. Spectator preservation is inside that call. The
optimistic one-role compilation is therefore

```text
B = 2F,  wNew = 0,  Delta = 0.
```

Any extra restoration or positive outside cost only increases `B` or
`Delta`. The five-call word then costs `F+4B = 9F`.

## Strict test

With `B = 2F` and `Delta = 0`,

```text
2F < (2F+6Q)/4  iff  Q > F.
```

Equality `Q = F` is break-even and fails the strict test. The difference
from the direct upper recipe, divided by `F`, is

```text
6(1 - Q/F).
```

The #5099 screen is the hypothetical same-volume model
`F = K f^(1-C)`, `Q = K floor(f/2)^(1-C)`, `K>0`, `0 ≤ C ≤ 17/5000`,
not a new physical law. It gives

```text
Q/F ≤ 2^(C-1) < 200/399 < 1,
```

because `2^(1-C) > 399/200` is the exact integer inequality
`399^5000 < 2^4983 * 200^5000`. Hence `Q < F` at every integer width, and

```text
(9F - (3F+6Q))/F > 398/133.
```

At `C = 0` the model is exact rather than a ratio cap: even widths lose by
`3F`, width one (where `Q = 0`) loses by `6F`, and odd widths lose by more
than `3F`. A positive `Delta` widens the loss. A negative `Delta` of size
greater than the gap could change the decision; none is proved.

A price `B = F` with `Q = F/2` does satisfy the strict inequality
(threshold `5/4`). That control is outside the one-role service. The
failure is the price of two separate calls, not an algebra error.

## What this does not show

This stops the one-role compilation. It does not forbid a different
multi-owner primitive whose complete price is below `2F`, and it does not
rerun the #5083 formal-word proof or the #5099 package replay. The power
screen is the predecessor's accounting model; actual half-width prices
above the full-width price would be a different hypothesis and are not
supplied by the pinned notes. No physical fixture, emitter, changed
histogram, or selected-frontier edit is included.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3 -I -W error -B research/cap2-one-role-direct-bill/verify.py
python3 scripts/research_package.py --package research/cap2-one-role-direct-bill
```

The direct command prints `PASS_CAP2_ONE_ROLE_DIRECT_BILL`. The registered
command also prints `PASS_REGISTERED_RESEARCH_PACKAGE`. Both finish in a
few seconds. The checker authenticates the pinned source bytes, the
one-role and direct-recipe sentences, the selected κ string, the integer
power bound, 128 widths, the break-even case, a below-threshold control,
and the sign of an unproved negative `Delta`.

## Open next questions

1. Can a changed multi-owner primitive meet `B < (2F+6Q-Delta)/4` with the
   same volume, orientation, spectators and a fully charged outside bill?
   That is the only remaining way through this gate. Start with one explicit
   layout and its summed call list. The selected one-role service does not
   supply a price below `2F`.
2. If that bill passes, does the changed inventory improve the selected
   #5413 complex moment after finite work, both tails, compiler reserve and
   outer transfer? A local BIT comparison is not a new κ. This question
   stays blocked until a passing bill exists.

## Credit

Nick Petalas supplied the #5083 formal five-call word. Chris R / Clear1nsight
supplied the #5099 physical ceiling, the direct-recipe threshold and the
two-owner volume reading. The BIT notes retain their source authors. The
selected record is #5413. Prepared by unpaidmoon with substantial Cursor
Grok assistance. Apache-2.0.
