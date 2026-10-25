# One shared radix traversal in the source-pinned directory producer

ToikY, with substantial OpenAI Codex assistance. Apache-2.0.

## Result and predecessor boundary

PR2590 (ywz65), `research/source-directory-setup-cost`, already proves the
unchanged producer's cubic radix reconstruction and complete volume-linear
asymptotic. Its explicit next question asks whether one encoded exponent
traversal can be shared across the fixed matrix coordinates. This package
answers that question for the producer component: replace its repeated
`high_power` traversal by one shared traversal, preserve its exact result and
complete record-tape behavior, and save a specified number of Word reads,
writes and unit moves. No new asymptotic order is claimed.

The source closure is six byte-authenticated files retained at canonical main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, under
`research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor/`.
The `directory.py` SHA256 is
`4270e370b2bfe38ef73aadcd97d1b3496b56bd582115d74331eb9e5ceb90bec7`;
the six original executable files remain unchanged. The experiment rebinds only the
producer module's `high_power` callback after constructing an already valid
Context. Context construction, including its separate `high_count`, and
Context close are outside the measured component and remain unchanged.

The new claim is the shared traversal, its exact complete producer-action
delta and a separately derived complete read/write/move invoice. The earlier
division write law, output-volume theorem and directory/reserve lifetime
results retain their original credit. This is no full selected caller,
source-stock construction, physical tape compiler, recursive tariff or kappa
result.

## Valid input contract and replacement

Write `d` for the fixed vocabulary dimension, `M=d^2`, `modulus=q^w`,
`c=q^(w-1)`, `H=c^M`, with `q>=2`, `w>=1`. A valid source Ring uses
`L=bit_length(modulus)+1` numerical bits. `B>=1` is the number of physical old
prefix positions; `h>=0` is the number of fields in each prefix. The supplied
old-field count is an `I`-bit Word, while the old-prefix count is a canonical
variable-length Count. The supplied old-directory/count/field and used Context
heads enter at 1; unrelated protected spectators retain their own heads.

Every old field has one valid finite `Q`-bit source code, followed by `M`
valid `L`-bit words with values strictly below `c`, then its record delimiter.
There are no extra or missing input symbols. One serialized field therefore
has

```
F = Q + 2 + M(L+1)
```

symbols. Equal old prefixes remain distinct physical positions. Successful
production emits, in source order, every old prefix followed by every
lexicographically ordered high field. Its output extent and count are

```
U = B H (h+1) F,              returned_count = B H.
```

The source `counts.high_power` performs `M` complete `radix_power` traversals.
Each traversal yields `w` times; `digit_suffix` skips the first yield and
multiplies its Count by `q` on every other yield. The replacement is:

```
first = True
for _ in radix_power(ring,q):
    if first:
        first = False
    else:
        for _ in range(d*d):
            value.multiply_small(q)
```

Both programs apply the same ordered sequence of exactly `M(w-1)`
multiplications by the same fixed `q`. Thus they have exactly the same Count
intermediate values, bit widths, symbol operations and final value `BH`.
The replacement decodes no runtime exponent: the existing encoded traversal
controls the outer loop and the inner `d*d` bound is fixed finite vocabulary
data. At `w=1` it still performs one full validating traversal; skipping every
traversal would omit source validation.

The radix generator and Count multiplication operate on disjoint Word and
record-Tape objects. Retaining its divisor/power across multiple Count
multiplications requires no additional Word. On success it frees those Word
roles and restores the same protected heads. Consequently every later
instruction of `produce`, its supplied arguments and its old-prefix/output
state is identical. No change to `old_prefix`, Odometer, cleanup, count
comparison, code validation or source serialization is needed.

This theorem concerns successful valid inputs. It does not add a new
exception-path rollback contract to the inherited source, or establish that
every arbitrary malformed numerical record is leak-free on rejection.

## Exact radix invoice

All vectors below have order `(reads,writes,unit_moves)` and use the source's
fixed-alphabet Word/Tape meters. They include zero initialization and erasure
where stated. Python allocation, instrumentation, audit-only integer decoding
and a physical fixed-tape implementation are outside this meter.

For a full-width division with quotient popcount `s`, the exact Word invoice is

```
D_L(s) = (15L^2+44L+33 + (12L+15)s,
           3L^2+ 8L+ 4 + ( 3L+ 2)s,
          14L^2+50L+44 + (12L+20)s).
```

PR2590 owns the middle, write-count identity. The other lanes are derived from
the same frozen methods. Each of the `L` division iterations performs a shift,
erases its former remainder, compares full words, writes one quotient bit and
moves both scan heads. A subtraction occurs exactly for the `s` one bits of
the quotient. Every `shift_add_bit` includes its `L+1` loop-condition reads;
finite literal loading also includes its extent-check reads. Counting these
reads is necessary for the complete invoice.

Useful exact vectors, for words starting at head 1, are

| Operation | `(reads,writes,unit_moves)` |
|---|---|
| Arena zero | `(4L+5,L+1,4L+6)` |
| Arena free | `(2L+3,L+1,2L+4)` |
| Arena copy | `(8L+9,2L+1,8L+12)` |
| Nonaliased comparison | `(5L+6,0,4L+8)` |
| Word zero test | `(2L+3,0,2L+4)` |
| Literal `q`, `b=bit_length(q)` | zero-vector plus `(2b+1,b,2b+2)` |

Let `A_L`, `E_L`, `C_L`, `P_L`, `Z_L` respectively denote the last table's
literal, free, copy, comparison and zero-test vectors. One full radix
traversal has exact cost

```
R(q,w,L) = A_L + C_L + (w+2)P_L
           + sum_(j=0..w-1) D_L(popcount(q^j))
           + 2w Z_L + (2w+2)E_L.
```

The two extra comparisons validate the final one; the final two erasures
dispose of divisor and power. The unchanged source performs `M` such
traversals, and the replacement performs one. All other Word operations and
every record/index operation agree. The exact complete producer saving is
therefore

```
Delta_record = Delta_index = (0,0,0),
Delta_residue = (M-1) R(q,w,L).
```

It is zero for `d=1` and strictly positive in all three lanes for `d>1`.
This saving is independent of `B`, `h`, old field values and the Count size;
those affect identical retained work. The asymptotic cubic dependence on
`w` remains when `d` is fixed, as already proved in PR2590.

## Complete retained work, rather than only output writes

`independent.py` derives the entire original and replacement invoices, not
only their delta. It imports no primary or predecessor executable and binds
the six source byte strings before comparing the measured receipt. Its
separate lanes include all supplied Tape and Word meter changes as well as
source-created scratch objects.

The exact Odometer counts per old prefix are

```
I_c = sum_(j=1..M) c^j,       A_c = sum_(j=0..M-1) c^j,
T_c = A_c (c-popcount(c)).
```

Here `I_c` counts digit increments, `A_c` counts carry/reset paths and `T_c`
counts one-bit ripple visits. At `c=1`, both sums equal `M`, rather than using
a singular geometric-quotient expression. Each reset scans the entire `L`
bits. The last advance, which marks the Odometer finished, is included.

For `K>=1`, put `t=K-popcount(K)` and `e=bit_length(K)-1`. All emission Count
increments from 0 to K cost

```
(2t+5K, t+K+e, 2t+4K+2e).
```

The complete Counter countdown from K to 0 costs

```
(2t+5K+1, t+K+2e+3, 2t+4K+2e+4).
```

The different final-zero and growing-right-delimiter paths explain the
different constants. Constructors, old padded-field-count input scans,
normalization, Count equality and final erasure are additional explicit
terms; they are not folded into a zero-cost loop bound. Count multiplication
from bit width `k` to `k'` costs `(2k+k'+2,k'+1,2k'+2)`.

For completeness, a saved old prefix has `n=hF` symbols. Its construction,
return rewind, all H copies and final clear cost

```
(4n+4+H(3n+3), 2n, 4n+6+H(2n+4))
```

on its own record Tape. The output Tape, including its final rewind, costs
`(2U+1,U,2U+2)`. Its borrowed old-input Tape costs
`(2BhF+BhML+3,0,2BhF+4)`. This includes all validation reads, initial and
final rewinds. One old numerical word's allocation, decoding, range check,
saved serialization and erasure costs `(16L+19,3L+2,14L+24)`.
These terms, all Odometer Word operations, all count operations and the
unchanged `high_power` or replacement term are summed in the checker.

The source creates exactly `5+2B` record Tape objects during production.
No physical Tape-object reuse is inferred merely because a logical role is
dead. The already known additional numerical live-word peak is
`max(M,6)`: Odometer owns M, exponent reconstruction needs at most six and
old-prefix decoding owns one at a time. Those phases are disjoint. The shared
version does not change this peak. This is reuse/confirmation of the existing
directory lifetime analysis, not a new reserve theorem or proof that the
physical caller can host all objects simultaneously.

## Finite evidence and limits

The measured component starts with a valid Context. Both variants run against
the same source fixtures, with runtime `Word.inspect` forbidden. The primary
observer includes all preexisting borrowed record tapes, all new record tapes,
residue-arena/template actions and the index-word arena. The independent
checker reproduces every action lane from formulas and independently creates
the complete expected output bytes by base-c address expansion.

Seven paired fixtures include three distinct empty-prefix positions,
nonempty histories of lengths one and two, radices 2/3/5, a binary long-carry
case, a nine-digit binary Odometer, a nontrivial `d=2,c=3` high cube and the
actual `d=64,c=1` boundary. The latter runs the unchanged dimension-64 producer code, but is
not a full nontrivial high-cube or selected source-stock execution. Bounded
small Odometers independently corroborate unique ordered enumeration, full
carry/reset counts and ripple sums. These checks do not replace the symbolic
loop argument above.

At `d=64,q=3,w=1,L=3`, one radix traversal costs `(523,95,556)`.
The replacement saves exactly `(2141685,389025,2276820)` residue Word actions.
In the recorded `B=1,h=1,Q=6507,I=4` fixture, its residue Word invoice changes
from `(2793472,483328,2916352)` to `(651787,94303,639532)`.
Record Tape `(310027,91612,274870)` and index Word `(15,0,12)` costs agree.
The complete output bytes/count, protected words, heads and scratch erasure
also agree. No elapsed-time or bit-machine saving is inferred from these
source-meter numbers.

Credit Jose Manuel/PR2569 for the producer, ywz65/PR2590 and PR2566 for setup
and primitive cost analysis, and the retained stream/cardinality/selected
caller and storage-reserve lineage. Original source notices and all frozen
bytes remain intact. Adoption into a shared producer, a complete caller
invoice, physical Tape layout/allocation, full Pi/source-stock admission,
recursive/supplier/outer obligations and frontier changes are outside this
package. No independent human or formal-kernel acceptance is claimed.
