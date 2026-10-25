# Exact arithmetic adaptations

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
I retain the word, FFT, phase and Gaussian sources through the authenticated
archives in `inputs/`. I describe the arithmetic refinements below;
PROOF.md gives the conditional tensor join and EVIDENCE.md separates the
completed checks from later publication runs.

## Fixed-digit products

In `tensor_word.py` I use 32 fixed shift/add phases to multiply two 32-bit
controls. After checking both control ranges, I return zero when either
digit is zero. Set `W=2^32`. During a schoolbook digit update,

```
old_digit + first_digit * second_digit + carry
    <= (W-1) + (W-1)^2 + (W-1) = W^2-1 = 2^64-1.
```

I write the low 32 bits and retain a carry at most `W-1`. In the 32 product
phases, the partial sum never exceeds the final digit product and the shifted
multiplicand never exceeds `W(W-1)`. I therefore keep data controls within 64
bits. These widths are compile-time constants. I keep arbitrary-width
operands, accumulated digits and loop extents on physical tapes; I never
decode an unbounded operand into a host integer. I zero-extend the final
partial operand digit and normalize the result after the final row.

I add each product and incoming carry into its accumulator digit during one
forward scan. Put `t_0=a*b+c` and let `z` be the old digit. After `i` bits,
I maintain `t_0+(z mod 2^i)=r_i+2^i*t_i`, where `r_i` contains the emitted
bits. For old bit `z_i`, I compute `s=(t_i & 1)+z_i`, write `s & 1`, and
set `t_(i+1)=(t_i >> 1)+(s >> 1)`. Induction proves that after32 steps I
have emitted `(t_0+z) mod W` and retained `floor((t_0+z)/W)`.
I bound `t_0<=W²-W`, `s<=2`, the final carry by `W-1` and the complete
sum by `W²-1`. I accumulate the old digit before overwriting its bits,
so I preserve the original maximum-control telemetry. For an extension I
use zero old bits and retain the blank-cell check before writing the next
right marker. I use this operation only on owned scratch: a late malformed
digit can fail after partial output, and the enclosing helper closes that
unfinished result and restores borrowed operands.

After processing the first `i` digits of the first operand, I retain its exact
partial product with the complete second operand. For the next row I shift
the starting position by one digit. The existing highest occupied digit lies
within this row's second-operand span. After those updates I therefore reach
the right marker and append one carry digit. I walk back 32 times
the encoded second-operand digit count, reaching the next row's start. I
retain complete accumulator digits, including a zero high carry, until the
final normalization; that preserves the right-marker invariant across rows.

In `DigitWordProduct` I fix the leaf cutoff at 1024 bits. Above that cutoff I call
the retained recursive entry, continuation and output serializer. I check
both operand widths before taking the zero shortcut. The fixed leaf change
preserves that recursion's asymptotic bound.

After proving a positive declared width at most1024, I probe its eleven-bit
encoding and scan each operand with a counter that saturates at that width
plus an overflow flag. I keep scanning after overflow, preserving the original
priority of a late nonbinary digit over the final width error. I restore
the borrowed origin on either outcome. Unsupported encodings retain the
original `fits` path. I check both operands before the zero-capable leaf.
I cover the1024/1025 probe boundary, a130-bit encoded width,4097-bit
oversized operands and a malformed digit after overflow.

Inside that leaf I probe at most 32 second-operand digits, execute at most
32 rows and move back at most 1024 cells per row. I check the right markers
at each complete extent. I keep these loop states in bounded finite control;
I keep operand and result data on tapes. The inherited caller copies its
operands into distinct read roles before entering the leaf. I retain its
complete double-width output serializer and continuation.

In `tensor_counts.py` I use the same digit calculation for arbitrary-width
setup products. I copy both operands, so an aliased square still has two
independent read cursors. For this unbounded setup helper I retain encoded
digit counts. Alongside the complete second-operand scan I maintain a
saturating state in `0..32`, then an overflow state. For a complete operand
of at most 32 digits I retreat by at most 1024 unit steps per row. After
overflow I retain the encoded amortized ripple countdown. Both branches
retreat by the same digit extent; the first operand can have arbitrary
length. For operand bit lengths
`a,b`, I spend `O((a+1)(b+1))` time and `O(a+b+1)` space, including input
copies, normalization and cleanup. I need a fixed number of tapes.
I specialize `Count.product` only for the duration
of `TensorPreparation.run` and restore the exact original class method on
exit, including exceptions. I retain the coefficient formulas and exact
rational operations. I do not decode a complete operand into a host integer.

## Streamed exact division during coefficient setup

In `tensor_division.py` I keep the quotient on a tape as I scan the numerator
from its most significant bit. After processing a prefix, I maintain
`N_k=q_k*d+r_k` with `0<=r_k<d`. For the next bit `x`, I compute

```
t = 2*r_k+x
outgoing = int(t >= d)
r_(k+1) = t-outgoing*d.
```

Since `t<2*d`, I need at most one subtraction. I append `outgoing` to an
MSB-first scratch stream, representing `q_(k+1)=2*q_k+outgoing`. I reverse
that stream once into the canonical quotient and normalize it. I avoid
rescanning the growing quotient at each numerator bit.

I inspect at most 32 denominator bits and then require the right marker
before admitting a divisor into fixed control. For `1<=d<=2^32-1`, I keep
`r_k<=d-1`, so `t<=2^33-3`. I serialize the final remainder through 32 bit
writes and normalize it; I do not pass a runtime value to `Count.literal`.
For a larger divisor I retain the original encoded remainder recurrence
and a separate divisor copy, including when the caller aliases the operands.

Before that recurrence, I copy up to `m-1` leading numerator bits into a
prefix scratch, using the copied divisor's remaining digit positions as
the extent. Here `m` is the canonical divisor's bit length. I emit one zero
quotient bit for each copied bit, since the prefix is less than
`2^(m-1)<=d`. I reverse the prefix once into the encoded remainder, then
reuse the scratch for the final quotient. I keep a short numerator at its
left marker until the recurrence finishes; otherwise I would process it
again. I repair the scratch and divisor heads before clearing or rewinding.
If the divisor's highest symbol is not one, I retain the original recurrence
without prefill. I never decode either operand or its length.

This prefill costs `O(n+m)` and leaves at most `max(0,n-m+1)` recurrence
steps. For canonical encoded lengths `n,m>=1`, I therefore spend
`O(n+m+max(0,n-m+1)*m)`, within the original general allowance. I reuse the
same five owned tapes. If `n<m`, I return quotient zero and the complete
numerator as remainder without running the encoded remainder recurrence.

For numerator and denominator bit lengths `n,m`, I charge `O(n+1)` time
in the bounded-divisor branch and `O(n*m+n)` in the general branch. I include
the probe, copies, reverse scan, normalization and cleanup. I use a fixed
number of tapes and `O(n+m)` cells. I restore both borrowed heads and return
two distinct owned Counts. I step back from a left marker before invoking
the retained rewind or cleanup operation.

Within `exact_setup_arithmetic`, I replace the direct division bindings in
`encoded`, `gaussian_rationals`, `gaussian_window` and `twiddle_setup`. I load
those modules before entering the scope, reject an existing adaptation and
restore their original bindings on normal and exceptional exit. I apply
this scope only during coefficient preparation. I preserve the exact
quotient and remainder, coefficient formulas and directed-rounding rules.

## Binary digit-pair square roots

In `tensor_twiddles.py` I scan the operand from its most significant end in
pairs, with a single initial bit for odd lengths. Suppose I have processed
the prefix `x` and retained `q=floor(sqrt(x))`, `r=x-q*q`. Then
`0<=r<2q+1`. Appending a digit `d` in `0..3` gives

```
4x+d = (2q)^2 + (4r+d).
```

The next root is either `2q` or `2q+1`: `4x+d < (2q+2)^2`. I select the
second case exactly when `4r+d >= 4q+1`, subtracting `4q+1` from the remainder.
That proves the invariant by induction and the exact integer square root at
the final digit. I keep `q` and `r` on encoded tapes; only the two-bit digit
and the parity of the operand length enter finite control.

For an `n`-bit input I make `O(n)` iterations, each with `O(n)` scans. I spend
`O(n²)` time and `O(n)` space on a fixed tape inventory. I restore the borrowed
input head after stepping back from its left marker.

## Inward roots of unity at fixed small orders

For any admitted precision `P>=16`, set

```
B = 2^P
U = 2^(2P-1)
m = floor(sqrt(2^(4P-3)))
h = floor(sqrt(U))
c = floor(sqrt(U+m))
s = floor(sqrt(U-m-1)).
```

Write `z=sqrt(2^(4P-3))`. Irrationality gives `m<z<m+1`. The exact squared
numerators of `cos(pi/8)` and `sin(pi/8)` on the `B` grid are `U+z` and `U-z`.
Each lies between consecutive integers. Since no integer square lies strictly
between consecutive integers, I obtain

```
c = floor(B*cos(pi/8))
s = floor(B*sin(pi/8))
h = floor(B/sqrt(2)).
```

I need the minus one in the sine radicand: the upper endpoint `U-m` could
itself be an integer square. I apply signs after flooring nonnegative
magnitudes, preserve exact axis values and select orders2,4,8 from order16.
Each component has no larger magnitude than its exact counterpart and an
error below `2^-P`. Each complex value therefore has norm at most one and
error below `sqrt(2)*2^-P < 2*2^-P`.

These estimates meet the retained Twiddles and positive PhaseBasis contracts.
I install the same small-order producer in the FFT-word product owner and
rebuild its canonical port inventory with that actual child's output.
I retain the original run methods, including signed emission, norm checks,
protected returns and cleanup. I bind their `TwiddlePlan` constructor to the
authored `SmallOrderPlan`. For orders above16 that plan delegates to the
original setup and value methods. I retain no table across calls.

The small-order setup uses a fixed number of encoded square roots and scans,
so I charge `O(P²)` time and `O(P)` space. I make no change to the general-order
setup allowance. The new producer need not reproduce a Taylor enclosure's
bytes, though the checked complete p48 chirp did reproduce them on this
fixture.

## Exact products with their effective operand width

In `tensor_arithmetic.py` I scan each canonical magnitude once, count its
bits and enforce the declared positive word width. I retain the original
digit and width-limit checks and register the first owned length before
measuring the second operand. I complete both fit checks before a zero
shortcut or child execution. At effective widths at most256 I use the
fixed physical digit leaf within the scalar owner, preserving the word owner's
protected-return guard. Above256 I call the same physical word owner at
the larger operand length and consume its complete double-width return.
I preserve the exact signed integer product, including zero and aliased
operands. I introduce no numerical rounding.

Within the scalar leaf I borrow distinct physical operand tapes. I identify
aliases after unwrapping their leases and copy the second operand only for
that case. I execute at most eight digit rows, each with at most eight
updates and a retreat of at most 256 cells. I use fixed controls for these
extents, check their right markers, and keep the result on its owned tape.
I restore borrowed heads and close the optional copy on success or failure.
The same row invariant and 64-bit multiply-add bound prove exactness. I keep
the declared-width and protected-return checks before zero shortcuts.

This interface lets the Gaussian consumers avoid repeated serialization of
unused high zero digits in their conservative work-width guards. I retain
the guards: a wide operand with a zero partner still fails before the word
call. For effective width `m<=n`, I pay `O(n)` for the entrance scans and
`O(m log²(m+2))` above the fixed leaf cutoff. Below that cutoff the digit
calculation has a uniform constant bound. This fits the original
`O(n log²(n+2))` allowance and fixed-tape space bound. I change neither
coefficient-page widths nor the producer's arithmetic.

I check 37 complete signed physical products and eight rejection cases,
including both wide-operand/zero-partner orders, the 256/257-bit branch
boundary, shared-tape views, a protected child return and positive reuse.
I inject a forbidden allocation after partial output in both the distinct
and aliased scalar paths and check restoration before reuse.
I register each measured width for cleanup before constructing the next
temporary. I also check failure during cutoff allocation after both widths
exist.

## Exact numerical-record serialization

In `tensor_records.py` I inspect at most 13 bits of the encoded record width,
then require the right marker and a value at most 4096 before using a bounded
loop. I restore the width's origin before reading or writing payload. For
wider widths I call the saved original codec. I keep payload bits on tapes.

For an admitted width `n`, I execute the retained per-bit operation exactly
`n` times. On read I require a binary symbol, append it to an owned Count,
advance the source, append the right marker and normalize. On write I emit
the next value bit or a zero after its right marker, then enforce the
original fit condition and restore the value's origin. I retain width zero:
reading returns zero; writing accepts zero and rejects a nonzero value.

Induction on the loop index gives the same first `i` output bits and cursor
positions after `i` iterations. At `i=n` I obtain the original complete
record and final cursor. I do not rewind the width after the payload loop:
if the caller aliases width and source, that would undo the consumed source
position. I close an unfinished read result on failure and retain its owning
lease on success. The bounded branch costs `O(n+1)` time; the constant width
probe preserves the original larger-width time and space bounds.

For the duration of `Tensor.run`, I replace five explicit bindings: both
codecs in `ring_words` and `gaussian_convolution`, and `write_fixed` in
`word_product`. The retained signed fallbacks, packed Gaussian slots and
complete double-width word returns reach those bindings through their
function globals. I preserve their positive-width, signed headroom,
coefficient separation and output extent checks, other imported codec
aliases, and the original fallbacks. I reject a nested adaptation and
restore those bindings on success or exception.

I also replace the `ring_words.power_two` and `ring_words.bit_at` support
bindings within that scope. For exponents at most 4096 I construct `2^n`
by writing `n` zero bits, a one and the right marker on an owned tape. The
final one proves canonicality, including the zero-exponent result one.
For positions at most 4096 I select a bit through unit tape movements and
return zero upon reaching the right marker. I preserve both skipped-bit
and selected-bit checks, and rewind the borrowed operand on success or
failure. I finish the position probe before scanning the value, so physical
value/index aliases retain the same result and origin. The original bit
window also holds at its right marker and fills later positions with zero.

I use `O(n+1)` time and space to construct the bounded power, and
`O(min(n,length)+1)` time with no auxiliary Count to select the bit. I keep
the power and operand data on physical tapes and preserve the original
larger-parameter fallbacks. I check 10 powers, 50 bit selections, malformed
selected/skipped bits, alias views and cleanup after partial power output.
I restore the complete seven-binding scope after success or exception.

I checked 36 unsigned records at widths from zero through 4097, with complete
zero padding and a trailing sentinel. I checked 20 signed boundary cases,
three calls to each larger-width fallback, truncated and late-invalid reads,
oversized writes, aliased width/source views and interrupted scope restoration.
I also checked that a 130-bit encoded width cannot enter bounded control.
I run the complete recursive-word/FFT group under the same scope; its
2049-bit case requires 4098 output bits and reaches the original fallback.

Before installing those replacements, I load the Tile, Core, Chirp and
small-twiddle modules. The cold word checker previously imported them inside
the scope and retained some temporary `power_two` references. I now capture
the eleven direct aliases and two copied function namespaces after preloading,
and check that I preserve their entry values on success and exception.
The word check also requires the original thirteen references before entry
and after the complete group. I include a separate interrupted-scope control.

## Direct bounded signed records

In `tensor_signed.py` I retain the existing `Signed` class, positive-width
admission and4096 cutoff. For a bounded read I collect the complete record
and retain its last bit as the sign. For a negative record I replace each
owned bit with complement plus carry, starting at carry1. The temporary
sum is at most2 and carry at most1. The complete result is `2^n-raw`, with
final carry0 because the sign bit proves `raw>=2^(n-1)>0`. I normalize and
transfer that same owning Count into `Signed`. I close partial results on
failure and keep the source's consumed cursor.

Before writing, I reproduce the original comparison with `2^(n-1)` in at
most `n` magnitude steps. Early right marker means less; another encoded
digit after `n` steps means greater. At exact width, high bit0 means less,
high bit1 with all lower bits zero means equal, and any lower one means
greater. I retain the `binary comparison digits` error and avoid validating
an oversized tail that the original comparison did not inspect. I admit
positive magnitude strictly below the limit and negative magnitude at most
the limit, completing this guard before writing any output.

I emit positive bits directly. For a negative magnitude I stream the same
complement-plus-one recurrence, supplying zero bits after its right marker.
I write exactly `n` bits and restore the borrowed magnitude. Both branches
cost `O(n+1)` with fixed controls and tape inventory. I delegate larger
widths to the original functions. I also delegate a source/width physical
alias, preserving the original reader's rewind behavior, and destination
aliases with the magnitude or width. Shared magnitude/width parameters
remain supported by completing the width probe before scanning data.

I preload the complete Tensor module graph before the record scope. I
replace thirteen reader bindings, fourteen module writer bindings and the
two writer entries in the copied small-twiddle namespaces. I preserve the
saved fallback functions and restore all29 bindings on success or exception.
The existing seven unsigned/binary bindings share that scope.

I check64 signed boundary cases through4097 bits, compare the complete wire
bits with separately computed two's-complement encodings, and decode each
accepted return. I check wider-function dispatch, physical alias handling,
zero-width admission, partial in-place conversion, partial negative output
and malformed-input error order. These checks supplement the unsigned
record, power and bit-selection controls.

## Local evidence and limits

I checked all 65536 eight-bit operand pairs through the 32-phase control,
100 full-width boundary pairs and four control-width rejections. I also
checked 52 physical word products through 2049 bits, recursive parents and an
actual FFT-word call. The complete word-fixture bytes retained their prior
hash after the fixed-digit refinement. I also checked 324 setup
products, including aliasing and class-method restoration after an exception.
These include 2049-bit first operands with second operands of 1023, 1024
and 1025 bits, crossing the bounded retreat threshold.
For digit-pair roots I checked 540 cases through 1024-bit square boundaries
against host integer square roots. I checked 32 complete signed phase tables
and four positive phase bases at precisions 16,48,54,113 against separate
rational radical enclosures.

For streamed division I checked 2082 quotient/remainder pairs against host
`divmod`, with numerators through 4097 bits, divisors across the 32-bit branch
boundary, zero numerators and aliased operands. I checked zero-divisor
rejection, borrowed head restoration, the four actual setup bindings and
their restoration after an interrupted adaptation.
I also reject failures while allocating the quotient scratch and general
remainder, checking that I return the earlier allocations and borrowed heads.
The prefix refinement adds thirty cases across33/65/129/513/4097-bit
divisors, including shorter numerators, the exact prefix boundary, equal
operands and short positive quotients. I checked2112 pairs in total, with
numerators through4101 bits. I also interrupt the prefix reversal after
partial output for both an exhausted and an unexhausted numerator, then
check the complete borrowed-head and owned-tape restoration.

The full64-coordinate p48 chirp passed its separate dense Fourier enclosure
and reproduced hash
`0d77ae678a513059c5e6153b4ba85fc273dabcbfbf58155ca69e514c609f5297`.
Before the32-bit refinement, I measured52.461 seconds on this host with the
small-order producer and eight-bit leaf,475.041 seconds with only that leaf,
and519.754 seconds with the earlier fixed1024-bit leaf. I used the disclosed
exact p48 metadata specialization and retained
finite q2 children. These timings do not establish production-scale behavior
or a new multiplication exponent. I have not obtained independent human
review or formal verification.
