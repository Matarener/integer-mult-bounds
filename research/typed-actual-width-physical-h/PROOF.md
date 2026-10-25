# Typed actual-width H and toward-zero return

This note prices one matched-layout normalized butterfly and its rounded
return. It does not apply the diagonal, reuse tapes across rounds, or change
a multiplication exponent.

## Typed object

Fix a layout parameter `K >= 1`, axis flags, length `ell >= 2`, and precision
`p >= 1`. Let the original and physical named-slot orders be the two orders in
PR #3623's `slots_for`. Write `M` for the number of records and `r = 2^ell`
for the coefficients in each record. A round `h` in that layout's round list
has selected address bits `beta_1, ..., beta_g` from the matched-extent rule:

- on a common round, `g` equals the axis count and the bits are
  `right + rho + t K`;
- on a prefix round, the bits are exactly the physical slots of height `h`.

The packet width is `w = p + 2`. The work width is `W = p + g + 2`. Every
borrowed numerator is an integer in `[-2^p, 2^p]`, encoded as an MSB-first
two's-complement word of width `w`. The call reads those words in either the
original or the physical slot order and writes the rounded tensor in the
physical order. The root copy is LSB-first. The consumer copy is MSB-first.
Both copies, and the blanked work tape, finish with their heads at cell 0.
The borrowed source bytes are unchanged. The object rejects a second call.

An old descriptor is not coerced. On the three short axes with `ell = 3` and
`K = 1`, round `h = 1` has selected bits `(3, 4, 5)`. The concealed bits
`(0, 1, 2)` raise `selected-bit descriptor`.

## Butterfly and rounding

Sign-extend each admitted word into width `W`. For each selected bit `beta`,
split the work image by that address bit, interleave the two halves so that
partners are adjacent, replace each adjacent pair `(a, b)` by `(a+b, a-b)`,
and merge the sum back onto the clear bit and the difference onto the set bit.
Component additions and subtractions are ripple circuits on width `W`.
Subtraction is invert-and-add-one. A final carry that leaves the signed
`W`-bit range aborts; the bound below says a successful admitted call does
not hit that abort.

After `t` selected bits, every work numerator is a sum of `2^t` input
numerators with coefficients in `{±1}`. Its absolute value is therefore at
most `2^{p+t}`. At `t = g` this is at most `2^{p+g}`. Width `W = p+g+2`
represents every integer from `-2^{p+g+1}` through `2^{p+g+1}-1`, so the
whole work vector fits.

`Q_p` then acts componentwise. Let `s` be the sign bit. Form the magnitude by
xoring every bit with `s` and adding `s`, drop the `g` low bits by keeping the
high `w` bits, then xor with `s` and add `s` again. For a nonnegative
magnitude this wiring is division by `2^g` rounded down. Restoring the sign
makes the result truncating division: nonnegative inputs use `floor(n/2^g)`,
and negative inputs use `-floor(|n|/2^g)`. That is not an arithmetic right
shift. In particular `-1` divided by `2` is `0` here and `-1` under an
arithmetic shift. The same witness appears in the two-record call below:
records `(0, 0)` and `(1, 0)` on the single selected bit become `(0, 0)` and
`(0, 0)` after rounding, whereas an arithmetic shift of the difference `-1`
would have left `-1`.

The consumer word is that signed `w`-bit vector, MSB first. The root word is
its reversal. Decoding the reversal as an MSB word changes the integer `1`.
Reversing again recovers it. After rounding, every returned numerator still
lies in `[-2^p, 2^p]`, which fits in a `w = p+2` two's-complement word
because `2^p <= 2^{p+1}-1` and `-2^p >= -2^{p+1}`.

The integer shadow of this schedule is exactly the unnormalized Hadamard on
the selected bits, followed by truncating division by `2^g`. Hadamard factors
on distinct bits commute, so the selected-bit order does not change the
integer result. PR #3623's explicit tensor `h_direct`, followed by its
toward-zero `truncate`, is the same map. The finite cubes compare those two
executables; they are controls for the wiring, not the only inputs covered
by the schedule.

## Exact bill

Write `C = 2 M r` for the number of real and imaginary components, and
`L = C W` for the work-tape length. A successful call performs exactly

```text
reads  = C w + 5 g L + L
writes = 2 L + 7 g L + 2 C w
gates  = C (W - w) + C + 2 g M + (3/2) g C W + C (2 W + 2 w)
```

The summands are the layout read and sign-extended write, five sequential
work-length passes per selected bit (split, interleave, adjacent butterfly,
deinterleave, merge), the final `Q_p` read, the root and consumer writes, and
the final work-tape blank. The two extra writes per selected bit blank the
half tapes and the paired tape. Gates are one disk test and `W-w` sign-fanout
gates per component, two address tests per record per selected bit, `3W`
adder/inverter gates per butterfly component pair, and `2W+2w` magnitude and
resign gates per component. Head travel is data-independent and equals the
itinerary in `itinerary_moves`: every scan starts and ends at cell 0, and the
adjacent butterfly is the only pass that seeks backward inside a pair.

For two records of one bit each, that adjacent pair costs 4 moves: step from
cell 0 to cell 1, return to cell 0, step to cell 1, and home. The whole
linear level on that shape costs 14 moves, because each of the five length-2
scans costs 2 and the adjacent pair costs 4, while every one-cell half tape
costs 0. Both integers are checked.

The two-record witness with `ell = 2`, one short axis, `K = 1`, `p = 4` and
one selected bit has `M = 2`, `r = 4`, `g = 1`, `W = 7`, `w = 6`, `C = 16`
and `L = 112`. The formulas give 768 reads, 1200 writes and 620 gates, and
the executed ledger matches those three integers. Its head travel is the
separate itinerary value 3890.

## What this does not prove

The diagonal factors `J_h` stay with PR #3617. This return is `Q_p H` in
physical slot order, not `J Q_p H` and not `Q_p H J`. Auxiliary tapes are
allocated per selected bit and blanked before the next bit; that is not a
fixed all-round stock. The initial framing of a production cube, descriptor
updates, previous-output reset, and a simultaneous buffer bound are still
open. No call uses the production band `ell >= 45812984491`. No selected
exponent changes.

The checked `Q_p` range is every integer from `-2^{p+g}` through `2^{p+g}`
for `p = 4` and `0 <= g <= 6`, which covers every selected-bit width in the
cube suite. The wiring argument is not limited to those widths; the exhaustive
loop is.
